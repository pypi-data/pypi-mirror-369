#!/bin/env python3
"""
Run a simulation
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import pigreads as pig
from pigreads.plot import movie


def main():
    random = np.random.default_rng(seed=0)

    R = 11.05
    z, y, x = np.mgrid[0:1, -R:R:200j, -R:R:200j]
    dz, dy, dx = pig.deltas(z, y, x)
    r = np.linalg.norm((x, y, z), axis=0)

    inhom = np.ones_like(x, dtype=int)
    inhom[r > R] = 0
    inhom *= random.uniform(0, 1, size=x.shape) > 0.1

    models = pig.Models()
    models.add("marcotte2017dynamical")

    states = models.resting_states(inhom, Nframes=100)
    states[0, np.linalg.norm(((x + 8), y, z), axis=0) < 2, 0] = 1
    states[0, y < 0, 1] = 2

    diffusivity = pig.diffusivity_matrix(Df=0.03)

    weights = models.weights(dz, dy, dx, inhom, diffusivity)

    Nt = 200
    dt = 0.025
    for ifr in tqdm(range(states.shape[0] - 1)):
        states[ifr + 1] = models.run(inhom, weights, states[ifr], Nt=Nt, dt=dt)

        if ifr > 0 and not np.all(
            np.isfinite(states[ifr + 1][np.isfinite(states[ifr])])
        ):
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                warnings.warn("New NaN values found!", stacklevel=2)

    # plot data with Matplotlib
    plt.imshow(
        states[-1, 0, :, :, 0],
        extent=(x[0, 0, 0], x[0, 0, -1], y[0, 0, 0], y[0, -1, 0]),
    )
    plt.show()

    # create a movie using FFmpeg
    movie(
        "example_api.mp4",
        states[:, 0, :, :, 0],
        progress="bar",
        tlables=[f"frame {ifr}" for ifr in range(states.shape[0])],
        extent=(x[0, 0, 0], x[0, 0, -1], y[0, 0, 0], y[0, -1, 0]),
    )


if __name__ == "__main__":
    main()
