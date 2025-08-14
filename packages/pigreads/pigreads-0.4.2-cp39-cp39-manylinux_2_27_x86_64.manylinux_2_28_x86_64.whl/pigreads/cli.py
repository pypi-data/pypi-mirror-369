"""
Implementation of the CLI
-------------------------
"""

from __future__ import annotations

import json
from typing import Any, TextIO

import click
import numpy as np
import yaml

import pigreads.plot as pp
from pigreads import __version__
from pigreads.progress import PROGRESS_ITERS
from pigreads.schema import Simulation


@click.group()
def main() -> None:
    "Run and visualise Pigreads simulations."


@main.command()
def version() -> None:
    "Show installed version."
    click.echo(f"Pigreads {__version__}")


@main.command()
@click.argument("config", type=click.File("r"))
@click.argument("result", type=click.Path())
@click.option(
    "-p",
    "--progress",
    type=click.Choice(list(PROGRESS_ITERS.keys())),
    default="bar",
    help="Progress bar type.",
)
@click.option(
    "-s", "--start-frame", type=int, default=0, help="Index of frame to start with."
)
@click.option(
    "--live",
    type=str,
    default=None,
    help="Enable live view for a specific variable, given as variable name or index.",
)
@click.option("--live-dpi", type=int, default=None, help="Dots per inch for live view.")
@click.option(
    "--live-path",
    type=str,
    default=None,
    help="File path for live view, if not given, live view is shown in a window.",
)
@click.option(
    "--live-index-z", type=int, default=None, help="Index in z direction for live view."
)
@click.option(
    "--live-kwargs",
    type=yaml.safe_load,
    default="{}",
    help="Additional arguments as YAML or JSON to pass to plot_frame, imshow, and LiveView.",
)
def run(
    config: TextIO,
    result: click.Path,
    progress: str,
    start_frame: int,
    live: str | None,
    live_dpi: int,
    live_path: str | None,
    live_index_z: int | None,
    live_kwargs: dict[str, Any],
) -> None:
    """
    Run a simulation.

    CONFIG is a YAML or JSON file defining the simulation,
    and RESULT is a path to write the results to.
    """

    sim = Simulation(**yaml.safe_load(config))

    liveview = (
        pp.LiveView(
            sim=sim,
            variable=live,
            dpi=live_dpi,
            index_z=live_index_z,
            path=live_path,
            **live_kwargs,
        )
        if live
        else None
    )

    def callback(states: np.ndarray[Any, Any], ifr: int) -> None:
        if liveview:
            liveview.update(states, ifr)

    sim.run(
        path=str(result),
        progress=PROGRESS_ITERS[progress],
        start_frame=start_frame,
        callback=callback,
    )

    if liveview:
        liveview.close()


@main.command()
@click.argument("input", type=click.File("r"), default="-")
@click.argument("output", type=click.File("w"), default="-")
@click.option(
    "-f",
    "--format",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format.",
)
def convert(
    input: TextIO,  # pylint: disable=redefined-builtin
    output: TextIO,
    format: str,  # pylint: disable=redefined-builtin
) -> None:
    """
    Convert a configuration file to canonical format.

    INPUT is a YAML or JSON file defining the simulation,
    and OUTPUT is a path to write the converted file to.
    """
    sim = Simulation(**yaml.safe_load(input))
    data = sim.model_dump()

    if format == "yaml":
        yaml.safe_dump(data, output, allow_unicode=True)
    else:
        assert format == "json"
        json.dump(data, output, indent=2)


@main.command()
@click.argument("config", type=click.File("r"))
@click.argument("result", type=click.Path(exists=True))
@click.argument("movie", type=click.Path())
@click.option("-d", "--dpi", type=int, default=180, help="Dots per inch.")
@click.option("-r", "--fps", type=int, default=15, help="Frames per second.")
@click.option(
    "-p",
    "--progress",
    type=click.Choice(list(PROGRESS_ITERS.keys())),
    default="bar",
    help="Progress bar type.",
)
@click.option("-z", "--index-z", type=int, default=None, help="Index in z direction.")
@click.option(
    "-v", "--variable", type=str, default=None, help="Variable name or index."
)
@click.option(
    "--kwargs",
    type=yaml.safe_load,
    default="{}",
    help="Additional arguments as YAML or JSON to pass to movie, "
    "plot_frame, and imshow, for example "
    '\'{"cmap": "inferno", "vmin": -0.25, "vmax": 1.25}\'.',
)
@click.option(
    "-n",
    "--parallel",
    type=int,
    default=1,
    help="Number of processes (default 1, 0 to use all CPUs).",
)
def movie(
    config: TextIO,
    result: click.Path,
    movie: click.Path,  # pylint: disable=redefined-outer-name
    dpi: int,
    fps: int,
    progress: str,
    variable: str | None,
    index_z: int | None,
    parallel: int,
    kwargs: dict[str, Any],
) -> None:
    """
    Generate a movie from a result file using FFmpeg and Matplotlib.

    CONFIG is a YAML or JSON file defining the simulation,
    RESULT is a NPY file containing the simulation results,
    and MOVIE is a path to write an MP4 video to.
    """

    sim = Simulation(**yaml.safe_load(config))
    models = sim.prepare_models()

    array: np.ndarray[Any, Any] = np.lib.format.open_memmap(  # type: ignore[no-untyped-call]
        result,
        mode="r",
    )
    assert array.shape == (sim.Nfr, sim.Nz, sim.Ny, sim.Nx, models.Nv)
    iz, iv = pp.get_iz_iv(sim, models, variable, index_z)
    array = array[:, iz, :, :, iv]

    zlabel = f" z = {sim.dz * iz:.2f}" if sim.Nz > 1 else ""
    tlables = [
        f"t = {time}" + zlabel for time in (sim.dt * sim.Nt * np.arange(sim.Nfr))
    ]

    pp.movie(
        path=str(movie),
        frames=array,
        tlables=tlables,
        progress=progress,
        parallel=parallel,
        **pp.imshow_defaults(
            sim=sim,
            array=array,
            dpi=dpi,
            fps=fps,
            vlabel=list(models.available[models[0].key].variables)[iv],
            **kwargs,
        ),
    )
