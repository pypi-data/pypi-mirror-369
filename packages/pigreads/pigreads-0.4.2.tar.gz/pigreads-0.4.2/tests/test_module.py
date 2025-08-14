from __future__ import annotations

import importlib.metadata
from typing import Any

import numpy as np

import pigreads as pig


def test_version():
    assert importlib.metadata.version("pigreads") == pig.__version__


def test_deltas():
    z, y, x = np.meshgrid(
        [0], np.arange(0, 4, 0.2), np.linspace(0, 1, 5), indexing="ij"
    )
    dz, dy, dx = pig.deltas(z, y, x)
    assert dz == 1
    assert dy == 0.2
    assert dx == 0.25
    assert pig.delta(y, ax=-2) == dy


def test_ithildin():
    z, y, x = np.mgrid[0:1, 0:3, 0:3]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    models = pig.Models()
    models.add("marcotte2017dynamical")
    models.add("aliev1996simple", k=8)
    assert models.available[models[0].key].variables == {"u": 0.0, "v": 0.0}
    states: np.ndarray[Any, Any] = models.resting_states(inhom, Nframes=2).astype(
        np.float32
    )
    weights = pig.weights(dz, dy, dx, inhom, diffusivity=0)
    Nt, dt = 3, 0.01
    states[1] = pig.run(models, inhom, weights, states[0], Nt=Nt, dt=dt)
    log, variables = pig.to_ithildin(Nt * dt, dt, dz, dy, dx, models, states, inhom)
    del log["Start date"]
    del log["Simulation parameters"]["Ithildin library version"]
    del log["Simulation parameters"]["Serial number"]
    assert (
        str(log)
        == r"{'Ithildin log version': 2, 'Simulation parameters': {'Timestep dt': 0.01, 'Frame duration': 0.03, 'Number of frames to take': 2, 'Name of simulation series': 'pigreads'}, 'Geometry parameters': {'Number of dimensions': 3, 'Voxel size': [1.0, 1.0, 1.0], 'Domain size': [3, 3, 1]}, 'Model parameters': {'Model type': 'Marcotte & Grigoriev 2017', 'Class': 'marcotte2017dynamical', 'Citation': 'https://doi.org/10.1063/1.5003259\nhttps://doi.org/10.1063/1.4915143\nhttps://doi.org/10.1103/PhysRevLett.71.1103\nhttps://doi.org/10.1063/1.166024', 'Parameters': {'diffusivity_u': 1.0, 'diffusivity_v': 0.05000000074505806, 'beta': 1.3890000581741333, 'eps': 0.009999999776482582, 'ustar': 1.5414999723434448}, 'Initial values': {'u': 0.0, 'v': 0.0}, 'Variable names': ['u', 'v'], 'Number of vars': 2}, 'Model parameters 1': {'Model type': 'Aliev & Panfilov 1996', 'Class': 'aliev1996simple', 'Citation': 'https://doi.org/10.1016/0960-0779(95)00089-5', 'Parameters': {'diffusivity_u': 1.0, 'eps0': 0.0020000000949949026, 'mu1': 0.20000000298023224, 'mu2': 0.30000001192092896, 'a': 0.15000000596046448, 'k': 8.0}, 'Initial values': {'u': 0.0, 'v': 0.0}, 'Variable names': ['u', 'v'], 'Number of vars': 2}}"
    )
    assert " ".join(variables.keys()) == "u v inhom"
    assert variables["u"].shape == (2, 1, 3, 3)
    assert variables["v"].shape == (2, 1, 3, 3)
