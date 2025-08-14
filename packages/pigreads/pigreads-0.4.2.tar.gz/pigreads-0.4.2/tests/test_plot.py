from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
import yaml

from pigreads.plot import LiveView, movie, movie_progress_updater, movie_wrapper
from pigreads.schema import Simulation

yaml_data = """
pigreads: 1
Nfr: 3
Nt: 2
Nz: 1
Ny: 50
Nx: 100
dt: 0.1
dz: 1.0
dy: 0.02
dx: 0.02
diffusivity: 0.1
models: aliev1996simple
init:
    u: 0.3
"""
sim = Simulation(**yaml.safe_load(yaml_data))
states = sim.run()


@dataclass
class MockClickEvent:
    inaxes: Any = None
    xdata: Any = None
    ydata: Any = None


def test_movie():
    with TemporaryDirectory() as tempdir:
        path = str(Path(tempdir) / "movie.mp4")
        movie(path, states[:, 0, :, :, 0])
        assert Path(path).exists()


def test_movie_wrapper():
    with TemporaryDirectory() as tempdir:
        path = str(Path(tempdir) / "movie.mp4")
        movie_wrapper({"path": path, "frames": states[:, 0, :, :, 0]})


def test_movie_progress_dict():
    with TemporaryDirectory() as tempdir:
        path = str(Path(tempdir) / "movie.mp4")
        progress = {path: 0}
        movie(path, states[:, 0, :, :, 0], progress_dict=progress)
        assert progress[path] == sim.Nfr


def test_movie_parallel():
    # Can not test the actual parallelism in this test.
    # Just check if the function runs without error.

    with (
        TemporaryDirectory() as tempdir,
        mock.patch("multiprocessing.Manager") as MockManager,
        mock.patch("multiprocessing.Pool") as MockPool,
        mock.patch("multiprocessing.Process") as MockProcess,
        mock.patch("subprocess.Popen") as MockPopen,
    ):
        mock_manager_instance = mock.MagicMock()
        mock_manager_instance.dict.side_effect = lambda d: d
        MockManager.return_value.__enter__.return_value = mock_manager_instance

        mock_pool_instance = mock.MagicMock()
        mock_async_result = mock.MagicMock()
        mock_async_result.get.return_value = None
        mock_pool_instance.starmap_async.return_value = mock_async_result
        MockPool.return_value.__enter__.return_value = mock_pool_instance

        mock_process_instance = mock.MagicMock()
        MockProcess.return_value = mock_process_instance

        mock_popen_instance = mock.MagicMock()
        mock_popen_instance.communicate.return_value = (b"", b"")
        mock_popen_instance.returncode = 0
        MockPopen.return_value = mock_popen_instance

        path = str(Path(tempdir) / "movie.mp4")
        movie(path, states[:, 0, :, :, 0], parallel=2)

        mock_process_instance.start.assert_called_once()
        mock_process_instance.join.assert_called_once()
        mock_pool_instance.starmap_async.assert_called_once()
        MockPopen.assert_called_once()


def test_movie_progress_updater():
    # pylint: disable=all

    class TestProgressDict(dict[str, int]):
        def __init__(self) -> None:
            super().__init__()
            self.counter: int = 0

        def values(self) -> Any:
            self.counter += 1
            return [self.counter // 3]

    progress_dict: TestProgressDict = TestProgressDict()

    with mock.patch("time.sleep", return_value=None):
        movie_progress_updater("none", 3, progress_dict)

    assert progress_dict.counter == 6


def test_liveview_show():
    fig, ax = plt.subplots()
    with (
        mock.patch.object(fig, "show"),
        mock.patch("matplotlib.pyplot.subplots") as mock_subplots,
    ):
        mock_subplots.return_value = (fig, ax)
        liveview = LiveView(sim)
        liveview.update(states, 0)
        liveview.close()


def test_liveview_clicks():
    with TemporaryDirectory() as tempdir:
        liveview = LiveView(
            sim=sim,
            path=str(Path(tempdir) / "live.png"),
            click_radius=0.2,
            click_value=123,
        )

        liveview.on_press(MockClickEvent(inaxes=liveview.ax, xdata=2, ydata=3))
        assert liveview.click_location == (3, 2)
        assert liveview.click_location_prev is None

        liveview.on_motion(MockClickEvent(inaxes=liveview.ax, xdata=4, ydata=1))
        assert liveview.click_location == (1, 4)
        assert liveview.click_location_prev is None

        liveview.on_release(MockClickEvent(inaxes=liveview.ax, xdata=None, ydata=None))
        assert liveview.click_location is None
        assert liveview.click_location_prev is None  # type: ignore[unreachable]

        liveview.close()


def test_liveview_clicks_none():
    with TemporaryDirectory() as tempdir:
        liveview = LiveView(
            sim=sim,
            path=str(Path(tempdir) / "live.png"),
        )

        liveview.on_press(MockClickEvent(inaxes=liveview.ax, xdata=2, ydata=3))
        assert liveview.click_location is None
        assert liveview.click_location_prev is None

        liveview.on_motion(MockClickEvent(inaxes=liveview.ax, xdata=4, ydata=1))
        assert liveview.click_location is None
        assert liveview.click_location_prev is None

        liveview.on_release(MockClickEvent(inaxes=liveview.ax, xdata=None, ydata=None))
        assert liveview.click_location is None
        assert liveview.click_location_prev is None

        liveview.close()


def test_liveview_draw():
    with TemporaryDirectory() as tempdir:
        liveview = LiveView(
            sim=sim,
            path=str(Path(tempdir) / "live.png"),
            click_radius=0.2,
            click_value=123,
        )
        liveview.click_location = (0.3, 0.8)
        liveview.click_location_prev = (0.7, 1.2)
        frame = np.copy(states[-1, 0, :, :, 0])
        liveview.draw_thick_line(frame)
        assert np.allclose(np.sum(frame), 111793.836)
        assert liveview.click_location_prev == (0.3, 0.8)
