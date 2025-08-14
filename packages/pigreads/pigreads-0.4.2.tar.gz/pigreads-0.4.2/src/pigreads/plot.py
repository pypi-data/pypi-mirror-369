"""
Plots and movies
----------------
"""

from __future__ import annotations

import multiprocessing
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.image import AxesImage

from pigreads import Models
from pigreads.progress import PROGRESS_ITERS
from pigreads.schema import Simulation


def get_iz_iv(
    sim: Simulation,
    models: Models,
    variable: str | int | None,
    index_z: int | None,
) -> tuple[int, int]:
    """
    Interpret z index and variable index from command line arguments.

    :param sim: Simulation object.
    :param models: Models object.
    :param variable: Variable name or index.
    :param index_z: Index in z direction.
    :return: Tuple of z index and variable index.
    """

    iz: int = sim.Nz // 2 if index_z is None else index_z
    iv: int

    try:
        iv = int(variable or 0)
        assert iv >= 0, "Invalid variable index"
        assert iv < models.Nv, "Invalid variable index"

    except ValueError:
        iv = 0 if variable is None else sim.varidx(models)[str(variable)]

    assert iz >= 0, "Invalid z index"
    assert iz < sim.Nz, "Invalid z index"

    return iz, iv


def imshow_defaults(
    array: np.ndarray[Any, Any] | None = None,
    sim: Simulation | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Set default imshow arguments.

    :param array: Array to display.
    :param sim: Simulation object.
    :param kwargs: Additional arguments.
    :return: Dictionary of arguments for
             :py:func:`matplotlib.pyplot.imshow`.
    """

    if "origin" not in kwargs:
        kwargs["origin"] = "lower"

    if "interpolation" not in kwargs:
        kwargs["interpolation"] = "none"

    if array is not None:
        if "vmin" not in kwargs:
            kwargs["vmin"] = np.nanmin(array)

        if "vmax" not in kwargs:
            kwargs["vmax"] = np.nanmax(array)

    if sim is not None and "extent" not in kwargs:
        kwargs["extent"] = (
            -0.5 * sim.dx,
            (sim.Nx + 0.5) * sim.dx,
            -0.5 * sim.dy,
            (sim.Ny + 0.5) * sim.dy,
        )

    return kwargs


def plot_frame(
    ax: Axes,
    frame: np.ndarray[Any, Any],
    xlabel: str = "x",
    ylabel: str = "y",
    vlabel: str = "",
    title: str = "",
    **kwargs: Any,
) -> tuple[AxesImage, Colorbar]:
    """
    Display a frame as an image.

    :param ax: Axes object.
    :param xlabel: Label for the x-axis.
    :param ylabel: Label for the y-axis.
    :param vlabel: Colorbar label.
    :param title: Title of the plot.
    :param frame: Frame to display.
    :param kwargs: Passed to :py:func:`matplotlib.pyplot.imshow`.

    :return: Image and colorbar objects.
    """
    assert frame.ndim == 2
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    im = ax.imshow(frame, **imshow_defaults(array=frame, **kwargs))
    cbar = plt.colorbar(im)
    cbar.set_label(vlabel)
    return im, cbar


def movie(
    path: str,
    frames: np.ndarray[Any, Any],
    dpi: int = 180,
    fps: int = 15,
    tlables: list[str] | None = None,
    progress: str = "none",
    progress_dict: dict[str, int] | None = None,
    parallel: int = 1,
    **kwargs: Any,
) -> None:
    """
    Render a chunk of frames to a movie file, with optional parallelization.

    :param path: Path to write the movie file to.
    :param frames: Array of frames.
    :param dpi: Dots per inch.
    :param fps: Frames per second.
    :param tlables: List of time labels.
    :param progress: Progress bar type.
    :param progress_dict: Dictionary to store progress.
    :param parallel: Number of processes (default 1, 0 to use all CPUs).
    :param kwargs: Passed to :py:func:`plot_frame`.
    """
    assert frames.ndim == 3

    if parallel == 1:
        fig, ax = plt.subplots(dpi=dpi)
        writer = FFMpegWriter(fps=fps)
        tlables = [f"{i}" for i, _ in enumerate(frames)] if tlables is None else tlables
        im, _ = plot_frame(ax, frames[0], **imshow_defaults(array=frames, **kwargs))

        prog = PROGRESS_ITERS[progress]
        with writer.saving(fig, path, fig.dpi):
            for (i, frame), tlabel in zip(enumerate(prog(frames)), tlables):
                ax.set_title(tlabel)
                im.set_data(frame)
                writer.grab_frame()
                if progress_dict is not None:
                    progress_dict[path] = i + 1
        return

    Np = multiprocessing.cpu_count() if parallel == 0 else parallel  # pylint: disable=invalid-name
    Nfr = len(frames)  # pylint: disable=invalid-name
    Nfrp = (Nfr + Np - 1) // Np  # pylint: disable=invalid-name
    chunks = [slice(i, min(i + Nfrp, Nfr)) for i in range(0, Nfr, Nfrp)]

    with TemporaryDirectory() as temp:
        paths = [str(Path(temp) / f"{i}.mp4") for i, _ in enumerate(chunks)]

        with multiprocessing.Manager() as manager:
            assert progress_dict is None
            progress_dict_ = manager.dict(dict.fromkeys(paths, 0))
            tasks = [
                [
                    {
                        "path": path,
                        "frames": frames[chunk],
                        "tlables": tlables[chunk] if tlables else None,
                        "progress_dict": progress_dict_,
                        "parallel": 1,
                        "dpi": dpi,
                        "fps": fps,
                        **kwargs,
                    }
                ]
                for path, chunk in zip(paths, chunks)
                if chunk.start < chunk.stop
            ]

            progress_proc = multiprocessing.Process(
                target=movie_progress_updater,
                args=(progress, Nfr, progress_dict_),
            )
            progress_proc.start()

            with multiprocessing.Pool(processes=Np) as pool:
                pool.starmap_async(movie_wrapper, tasks).get()

            progress_proc.join()

        pathlist = Path(temp) / "files.txt"
        with pathlist.open("w") as f:
            for p in paths:
                f.write(f"file '{p}'\n")

        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                pathlist,
                "-c",
                "copy",
                str(path),
            ],
            stderr=subprocess.PIPE,
        )

        _, stderr = proc.communicate()
        assert proc.returncode == 0, stderr.decode()


def movie_wrapper(kwargs: dict[str, Any]) -> None:
    """
    Wrapper for movie to allow for multiprocessing.

    :param kwargs: Keyword arguments for :py:func:`movie`.
    """
    return movie(**kwargs)


def movie_progress_updater(
    progress: str, total: int, progress_dict: dict[str, int]
) -> None:
    """
    Update the progress bar for a movie.

    :param progress: Progress bar type.
    :param total: Total number of frames.
    :param progress_dict: Dictionary to store progress.
    """
    prog = PROGRESS_ITERS[progress]
    for i in prog(range(total)):
        while sum(progress_dict.values()) < i:
            time.sleep(0.1)


class LiveView:
    """
    Live view for a simulation.

    Plot a single variable at a fixed z index in an interactive window or save
    it to a file.

    :param sim: Simulation object.
    :param variable: Variable name or index.
    :param index_z: Index in z direction.
    :param dpi: Dots per inch.
    :param path: File path.
    :param click_radius: Radius of click region.
    :param click_value: Value to add continuously while clicking.
    :param style: Style sheet,
                  passed to :py:func:`matplotlib.style.use`,
                  for example ``dark_background``.
    :param kwargs: Additional arguments to pass to :py:func:`plot_frame` and
                   :py:func:`matplotlib.pyplot.imshow`.

    :ivar sim: Simulation object.
    :ivar fig: Figure object.
    :ivar ax: Axes object.
    :ivar models: Models object.
    :ivar iz: Index in z direction.
    :ivar iv: Index of variable.
    :ivar click_radius: Radius of click region.
    :ivar click_value: Value to add continuously while clicking.
    :ivar click_location: Location of the current click.
    :ivar click_location_prev: Location of the previous click.
    :ivar mouse_pressed: Flag indicating whether the mouse is pressed.
    :ivar kwargs: Additional arguments.
    :ivar path: File path.
    :ivar im: Image object.
    :ivar cbar: Colorbar object.
    """

    def __init__(
        self,
        sim: Simulation,
        variable: str | int | None = None,
        index_z: int | None = None,
        dpi: int | None = None,
        path: Path | str | None = None,
        click_radius: float | None = None,
        click_value: float | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        if style is not None:
            plt.style.use(style)

        self.sim = sim
        self.kwargs = kwargs
        self.fig, self.ax = plt.subplots(dpi=dpi)
        plt.tight_layout()
        self.models = sim.prepare_models()
        self.iz, self.iv = get_iz_iv(sim, self.models, variable, index_z)
        self.kwargs = {
            "vlabel": list(self.models.available[self.models[0].key].variables)[
                self.iv
            ],
            **imshow_defaults(sim=sim, **kwargs),
        }
        self.path = path
        self.im: AxesImage | None = None
        self.cbar: Colorbar | None = None

        if self.path is None:
            self.fig.show()

        self.click_radius = click_radius
        self.click_value = click_value
        self.click_location: tuple[float, float] | None = None
        self.click_location_prev: tuple[float, float] | None = None
        self.mouse_pressed = False

        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)

    def on_press(self, event: Any) -> None:
        """
        Handle mouse button press: store click location and set press flag.
        """
        if (
            self.click_radius is None
            or self.click_value is None
            or event.inaxes != self.ax
            or event.xdata is None
            or event.ydata is None
        ):
            return
        self.click_location = (event.ydata, event.xdata)
        self.mouse_pressed = True

    def on_motion(self, event: Any) -> None:
        """
        Handle mouse motion: draw a thick line between previous and current locations.
        """
        if (
            self.click_radius is None
            or self.click_value is None
            or not self.mouse_pressed
            or event.inaxes != self.ax
            or event.xdata is None
            or event.ydata is None
        ):
            return
        self.click_location = (event.ydata, event.xdata)

    def on_release(self, _: Any) -> None:
        """
        Handle mouse button release: clear press flag.
        """
        if self.click_radius is None or self.click_value is None:
            return
        self.mouse_pressed = False
        self.click_location = None
        self.click_location_prev = None

    def draw_thick_line(self, frame: np.ndarray[Any, Any]) -> None:
        """
        Draw a thick line between the previous and new locations with the given radius.
        """
        if (
            self.click_radius is None
            or self.click_value is None
            or self.click_location is None
        ):
            return

        y1, x1 = self.click_location
        y2, x2 = self.click_location

        if self.click_location_prev is not None:
            y2, x2 = self.click_location_prev

        dx, dy = x2 - x1, y2 - y1

        y, x = np.meshgrid(
            self.sim.dy * np.arange(self.sim.Ny),
            self.sim.dx * np.arange(self.sim.Nx),
            indexing="ij",
        )

        distance = np.abs(+dy * x - dx * y + x2 * y1 - y2 * x1) / np.linalg.norm(
            (dy, dx), axis=0
        )

        t = ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2)

        mask = (distance <= self.click_radius) & (t >= 0) & (t <= 1)

        for y_, x_ in [(y1, x1), (y2, x2)]:
            mask[np.linalg.norm([y - y_, x - x_], axis=0) <= self.click_radius] = True

        frame[mask] += self.click_value
        self.click_location_prev = self.click_location

    def update(self, states: np.ndarray[Any, Any], ifr: int) -> None:
        """
        Update the live view.

        :param states: Array of states with shape (Nfr, Nz, Ny, Nx, Nv).
        :param ifr: Index of frame.
        """

        frame = states[ifr, self.iz, :, :, self.iv]

        self.draw_thick_line(frame)

        if self.im is None:
            self.im, self.cbar = plot_frame(
                self.ax, frame, **imshow_defaults(array=frame, **self.kwargs)
            )

        else:
            assert self.cbar is not None
            vmin, vmax = self.im.get_clim()
            vmin = self.kwargs.get("vmin", np.nanmin([vmin, np.nanmin(frame)]))
            vmax = self.kwargs.get("vmax", np.nanmax([vmax, np.nanmax(frame)]))
            self.im.set_data(frame)
            self.im.set_clim(vmin, vmax)
            self.cbar.mappable.set_clim(vmin, vmax)
            self.cbar.update_normal(self.im)

        self.ax.set_title(
            f"frame {ifr}/{self.sim.Nfr}, t = {ifr * self.sim.Nt * self.sim.dt:.2f}"
        )
        if self.path is None:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        else:
            self.fig.savefig(str(self.path))

    def close(self) -> None:
        """
        Close the opened figure.
        """
        plt.close(self.fig)
