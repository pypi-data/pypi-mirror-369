from __future__ import annotations

import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest
import yaml
from click.testing import CliRunner

from pigreads import __version__
from pigreads.cli import main as cli
from pigreads.progress import PROGRESS_ITERS, BaseProgressIterator
from pigreads.schema import Simulation

yaml_data = """
pigreads: 1
Nfr: 3
Nt: 2
Nz: 1
Ny: 1
Nx: 1
dt: 0.1
dz: 0.1
dy: 0.1
dx: 0.1
diffusivity: 0.1
models: aliev1996simple
init:
    u: 0.3
"""
sim = Simulation(**yaml.safe_load(yaml_data))


def test_usage():
    runner = CliRunner()
    result = runner.invoke(cli)
    print(result.output)
    assert result.exit_code in [0, 2]
    assert result.output.startswith("Usage")


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    print(result.output)
    assert result.exit_code == 0
    assert result.stdout.strip() == f"Pigreads {__version__}"


def test_yaml2json():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.yaml"
        path_output = path / "output.json"

        with path_input.open("w") as f:
            f.write(yaml_data)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["convert", "-f", "json", str(path_input), str(path_output)],
        )
        assert result.exit_code == 0

        with path_output.open() as f:
            assert Simulation(**json.loads(f.read())) == sim


def test_json2yaml():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.json"
        path_output = path / "output.yaml"

        with path_input.open("w") as f:
            f.write(sim.model_dump_json())

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["convert", str(path_input), str(path_output)],
        )
        assert result.exit_code == 0

        with path_output.open() as f:
            assert Simulation(**yaml.safe_load(f.read())) == sim


def test_invalid_conversion():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.json"
        path_output = path / "output.yaml"

        with path_input.open("w") as f:
            f.write(sim.model_dump_json())

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "convert",
                "-f",
                "invalid",
                str(path_input),
                str(path_output),
            ],
        )
        assert result.exit_code == 2
        assert "Invalid value" in result.output


def test_run():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.yaml"
        path_output = path / "output.npy"

        with path_input.open("w") as f:
            f.write(yaml_data)

        runner = CliRunner()
        result = runner.invoke(cli, ["run", str(path_input), str(path_output)])
        assert result.exit_code == 0

        states = np.load(path_output)
        assert np.allclose(states[-1].squeeze(), [0.4401616, 0.00194737])


def test_live():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.yaml"
        path_output = path / "output.npy"
        path_live = path / "live.png"

        with path_input.open("w") as f:
            f.write(yaml_data)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "run",
                str(path_input),
                str(path_output),
                "--live",
                "u",
                "--live-path",
                str(path_live),
                "--live-kwargs={style: dark_background}",
            ],
        )
        assert result.exit_code == 0

        states = np.load(path_output)
        assert np.allclose(states[-1].squeeze(), [0.4401616, 0.00194737])


def test_progress():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.yaml"
        path_output = path / "output.npy"

        with path_input.open("w") as f:
            f.write(yaml_data)

        for progress in PROGRESS_ITERS:
            runner = CliRunner()
            result = runner.invoke(
                cli, ["run", "-p", progress, str(path_input), str(path_output)]
            )
            assert result.exit_code == 0


def test_progress_base():
    for _ in BaseProgressIterator(range(3)):
        pass


def test_movie():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.yaml"
        path_output = path / "output.npy"
        path_movie = path / "movie.mp4"

        with path_input.open("w") as f:
            f.write(yaml_data)

        runner = CliRunner()
        result = runner.invoke(cli, ["run", str(path_input), str(path_output)])
        assert result.exit_code == 0

        result = runner.invoke(
            cli, ["movie", str(path_input), str(path_output), str(path_movie)]
        )
        assert result.exit_code == 0


def test_unstable():
    with TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        path_input = path / "input.yaml"
        path_output = path / "output.npy"

        with path_input.open("w") as f:
            f.write(re.sub(r"dt:.*", "dt: 1e10", yaml_data))

        runner = CliRunner()
        with pytest.warns(RuntimeWarning, match="New non-finite values found"):
            result = runner.invoke(cli, ["run", str(path_input), str(path_output)])
        assert result.exit_code == 0
