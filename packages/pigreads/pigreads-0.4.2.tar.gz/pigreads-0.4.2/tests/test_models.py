from __future__ import annotations

from typing import Any

import numpy as np
import pytest

import pigreads as pig
from pigreads.schema.model import ModelDefinition


def test_str():
    pig.Models("marcotte2017dynamical")


def test_add():
    key = "marcotte2017dynamical"
    models = pig.Models(
        [
            (key, {}),
            (key, {"eps": 1}),
        ]
    )
    models.add(key)
    models.add(key, eps=2)
    assert models[0] == models[2]
    assert models[1].parameters["eps"] == 1
    assert models[3].parameters["eps"] == 2


def test_len():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    models.add(key)
    models.add(key)
    assert len(models) == 3


def test_Nv():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    assert models.Nv == 2


def test_Np():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    assert len(models[0].parameters) == 5


def test_set_param():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    models[0].parameters["eps"] *= 2


def test_del_param():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    with pytest.raises(NotImplementedError):
        del models[0].parameters["eps"]


def test_repr_params():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    repr(models[0].parameters)


def test_str_params():
    key = "marcotte2017dynamical"
    models = pig.Models()
    models.add(key)
    str(models[0].parameters)


def test_resting_states():
    models = pig.Models()
    models.add("gray1983autocatalytic")
    models.add("courtemanche1998ionic")
    inhom = np.array([[[0, 1], [2, 3]]], dtype=int)
    states = models.resting_states(inhom, Nframes=2)
    assert states.shape == (2, *inhom.shape, models.Nv)
    assert np.all(np.isnan(states[0, 0, 0, 0, :]))
    assert np.all(np.isnan(states[:, inhom == 0, :]))
    assert states[0, 0, 0, 1, 0] == 1
    assert states[0, 0, 0, 1, 1] == 0
    assert abs(-81.18 - states[0, 0, 1, 0, 0]) < 1e-6
    assert abs(11.17 - states[0, 0, 1, 0, 1]) < 1e-6
    assert states[0, 0, 1, 1, 0] == 1
    assert states[0, 0, 1, 1, 1] == 0
    assert np.all(np.isnan(states[1, inhom != 0, :]))


def test_sim0d():
    z, y, x = np.mgrid[0:1, 0:3, 0:3]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)

    for double_precision in [False, True]:
        for modelname in pig.Models().available:
            models = pig.Models(modelname, double_precision=double_precision)
            states: np.ndarray[Any, Any] = models.resting_states(
                inhom, Nframes=2
            ).astype(np.float32)
            weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
            states[1] = models.run(inhom, weights, states[0], Nt=2, dt=1e-10)


def test_define():
    pig.Models.available["fitzhugh1961impulses"] = ModelDefinition(
        name="FitzHugh 1961 & Nagumo 1962",
        description="A 2D simplification of the Hodgkin-Huxley model.",
        dois=[
            "https://doi.org/10.1016/S0006-3495(61)86902-6",
            "https://doi.org/10.1109/JRPROC.1962.288235",
        ],
        variables={"u": 1.2, "v": -0.625},
        diffusivity={"u": 1.0},
        parameters={"a": 0.7, "b": 0.8, "c": 3.0, "z": 0.0},
        code="""
            *_new_u = u + dt * (v + u - u*u*u/3 + z + _diffuse_u);
            *_new_v = v + dt * (-(u - a + b*v)/c);
        """,
    )

    z, y, x = np.mgrid[0:1, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)

    models = pig.Models("fitzhugh1961impulses")

    states: np.ndarray[Any, Any] = models.resting_states(inhom, Nframes=2)
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    states[1] = models.run(inhom, weights, states[0], Nt=100, dt=0.004)
    assert np.allclose(states[1], [1.1996392, -0.6249765])


def test_block_size():
    models = pig.Models()
    assert models.block_size == [1, 8, 8]
    models.block_size = [8, 8, 8]
    assert models.block_size == [8, 8, 8]
