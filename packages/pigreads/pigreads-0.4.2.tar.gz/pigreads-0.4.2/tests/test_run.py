from __future__ import annotations

from typing import Any

import numpy as np
import pytest

import pigreads as pig


def test_inhom():
    z, y, x = np.mgrid[0:1, 0:1, 0:3]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.arange(3).reshape((1, 1, 3))
    models = pig.Models()
    models.add("aliev1996simple")
    models.add("gray1983autocatalytic")
    states = models.resting_states(inhom, Nframes=2)
    states[0, 0, 0, 0, :] = 1.0  # outside
    states[0, 0, 0, 1, 0] = 0.4  # aliev1996simple u
    states[0, 0, 0, 2, 1] = 0.5  # gray1983autocatalytic v
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    states[1] = models.run(inhom, weights, states[0], Nt=1, dt=0.1)
    assert np.allclose(states[0, 0, 0, 0, :], 1), "starting at given outside value"
    assert np.all(np.isnan(states[1, 0, 0, 0, :])), "outside value must be set to nan"
    assert states[0, 0, 0, 1, 0] < states[1, 0, 0, 1, 0], (
        "aliev1996simple u must increase"
    )
    assert states[0, 0, 0, 1, 1] < states[1, 0, 0, 1, 1], (
        "aliev1996simple v must increase"
    )
    assert states[0, 0, 0, 2, 0] > states[1, 0, 0, 2, 0], (
        "gray1983autocatalytic u must decrease"
    )
    assert states[0, 0, 0, 2, 1] < states[1, 0, 0, 2, 1], (
        "gray1983autocatalytic v must increase"
    )


def test_stim():
    z, y, x = np.mgrid[0:1, 0:1, 0:5]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    inhom[:, :, -1] = 2
    models = pig.Models()
    models.add("trivial")
    models.add("aliev1996simple", k=0, eps0=0, mu1=0)
    states = models.resting_states(inhom, Nframes=2)
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    stim_signal = np.array([(0, 0), (-1, 2), (4, 1), (np.nan, np.nan)])
    stim_shape = np.array([0, 1, 0.5, -1, 1]).reshape(inhom.shape)
    dt = 1.0
    states[1] = pig.run(
        models,
        inhom,
        weights,
        states[0],
        stim_signal=stim_signal,
        stim_shape=stim_shape,
        Nt=3,
        dt=dt,
    )
    assert states.shape == (2, 1, 1, 5, 2)
    sum_u, sum_v = np.sum(stim_signal[:3], axis=0)
    for i in range(4):
        assert states[1, 0, 0, i, 0] == dt * stim_shape[0, 0, i] * sum_u, f"i={i}"
    assert states[1, 0, 0, 4, 1] == dt * stim_shape[0, 0, 4] * sum_v


def test_stims():
    z, y, x = np.mgrid[0:1, 0:1, 0:5]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    inhom[:, :, -1] = 2
    models = pig.Models()
    models.add("trivial")
    models.add("aliev1996simple", k=0, eps0=0, mu1=0)
    states = models.resting_states(inhom, Nframes=2)
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    stim_signal = np.array(
        [[[6, 2], [0, 0]], [[8, 9], [6, 7]], [[5, 9], [8, 0]], [[8, 0], [7, 1]]]
    )
    stim_shape = np.array([[[[8, 5, 2, 4, 0]]], [[[1, 6, 6, 6, 3]]]])
    dt = 1.0
    states[1] = pig.run(
        models,
        inhom,
        weights,
        states[0],
        stim_signal=stim_signal,
        stim_shape=stim_shape,
        Nt=3,
        dt=dt,
    )
    assert states.shape == (2, 1, 1, 5, 2)
    assert np.all(np.isnan(states[1, 0, 0, :-1, 1]))
    assert np.allclose(
        states[1, 0, 0, :-1, 0],
        np.array([166, 179, 122, 160]),
    )
    assert np.allclose(
        states[1, 0, 0, -1, :],
        np.array([-336, 21]),
    )


def test_stim_dt():
    z, y, x = np.mgrid[0:1, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    models = pig.Models("trivial")
    states = models.resting_states(inhom, Nframes=3)
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    stim_signal = np.arange(5).reshape((-1, 1))
    stim_shape = inhom
    dt = 0.1
    states[1] = dt * pig.run(
        models,
        inhom,
        weights,
        states[0],
        stim_signal=stim_signal,
        stim_shape=stim_shape,
        Nt=10,
        dt=1,
    )
    states[2] = pig.run(
        models,
        inhom,
        weights,
        states[0],
        stim_signal=stim_signal,
        stim_shape=stim_shape,
        Nt=10,
        dt=dt,
    )
    assert np.allclose(states[1], states[2])


def test_cell():
    z, y, x = np.mgrid[0:1, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    models = pig.Models("aliev1996simple")
    states = models.resting_states(inhom, Nframes=3)
    states[0, ..., 0] = 0.4
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    for i in range(states.shape[0] - 1):
        states[i + 1] = models.run(inhom, weights, states[i], Nt=199, dt=0.1)
    assert states.shape == (3, 1, 1, 1, 2)
    states = states.squeeze()
    assert np.allclose(
        states,
        [
            [4.00000006e-01, 0.00000000e00],
            [9.06229615e-01, 5.90469241e-01],
            [4.87683921e-11, 1.08949475e-01],
        ],
    )


def test_cable():
    z, y, x = np.mgrid[0:1, 0:1, 0:50]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    inhom[..., -1] = 0
    models = pig.Models("aliev1996simple")
    states = models.resting_states(inhom, Nframes=3)
    states[0, x < 5, 0] = 0.4
    weights = models.weights(dz, dy, dx, inhom, diffusivity=1)
    Nt, dt = 399, 0.05
    for i in range(states.shape[0] - 1):
        states[i + 1] = models.run(inhom, weights, states[i], Nt=Nt, dt=dt)
    assert states.shape == (3, 1, 1, 50, 2)
    assert np.allclose(
        states[:, 0, 0, (0, 25, 48), 0],
        [
            [4.0000001e-01, 0.0000000e00, 0.0000000e00],
            [9.0334904e-01, 9.9558353e-01, 1.0182223e-14],
            [1.0085634e-08, 5.3530955e-01, 9.9503601e-01],
        ],
    )


def test_spiral():
    z, y, x = np.mgrid[0:1, -25:25, -25:25]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    inhom[:, -1, :] = 0
    inhom[:, :, -1] = 0
    models = pig.Models("aliev1996simple")
    states = models.resting_states(inhom, Nframes=3)
    states[0, x > 0, 0] = 1
    states[0, y > 0, 1] = 1
    weights = models.weights(dz, dy, dx, inhom, diffusivity=1)
    Nt, dt = 399, 0.05
    for i in range(states.shape[0] - 1):
        states[i + 1] = models.run(inhom, weights, states[i], Nt=Nt, dt=dt)
    indices = 0, 10, 40, 48
    assert states[0, 0, 49, 49, 0] == 1.0
    assert np.all(np.isnan(states[1:, 0, 49, 49, :])), (
        "outside value must be set to nan"
    )
    assert np.allclose(
        states[:, 0, indices, indices, 0],
        [
            [0.0000000e00, 0.0000000e00, 1.0000000e00, 1.0000000e00],
            [2.1328260e-01, 9.8938406e-01, 6.8952787e-08, 1.8248732e-11],
            [8.7120086e-01, 5.8410158e-03, 2.0007190e-05, 4.3070755e-12],
        ],
    )


def test_aniso():
    z, y, x = np.mgrid[0:1, -25:25, -25:25]
    r = np.linalg.norm((x, y), axis=0)
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    models = pig.Models("aliev1996simple")
    states = models.resting_states(inhom, Nframes=3)
    states[0, r < 3, 0] = 1
    diffusivity = pig.diffusivity_matrix(Df=1.0, Ds=0.2, f=[1, 2, 3])
    weights = models.weights(dz, dy, dx, inhom, diffusivity=diffusivity)
    Nt, dt = 399, 0.05
    for i in range(states.shape[0] - 1):
        states[i + 1] = models.run(inhom, weights, states[i], Nt=Nt, dt=dt)
    assert np.allclose(states[1, 0, 10, 15, 0], 0.15971428)
    assert np.allclose(states[1, 0, 15, 34, 0], 0.3017956)
    assert np.allclose(states[2, 0, 37, 33, 0], 0.1480847)
    assert np.allclose(states[2, 0, 25, 19, 0], 0.00012683906)


def test_double():
    z, y, x = np.mgrid[0:1, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    models1 = pig.Models("aliev1996simple")
    models2 = pig.Models("aliev1996simple", double_precision=True)
    states: np.ndarray[Any, Any] = models2.resting_states(inhom).astype(np.float64)
    states[0, ..., 0] = 0.4
    weights = models2.weights(dz, dy, dx, inhom, diffusivity=0)
    assert states[0].ndim == 4
    states_single = models1.run(inhom, weights, states[0], Nt=199, dt=0.1)
    states_double = models2.run(inhom, weights, states[0], Nt=199, dt=0.1)
    assert states_single.ndim == 4
    assert states_double.ndim == 4
    assert states_single.dtype == np.float32
    assert states_double.dtype == np.float64
    assert np.allclose(states_single, states_double)


def test_precision_conflict():
    z, y, x = np.mgrid[0:1, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    models = pig.Models("aliev1996simple", double_precision=True)
    states = models.resting_states(inhom, Nframes=2)
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    with pytest.raises(AssertionError):
        states = pig.run(
            models, inhom, weights, states[0], Nt=100, dt=0.1, double_precision=False
        )


def test_dt():
    z, y, x = np.mgrid[0:1, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x)
    models = pig.Models("aliev1996simple")
    states = models.resting_states(inhom, Nframes=3)
    states[0, ..., 0] = 0.4
    weights = models.weights(dz, dy, dx, inhom, diffusivity=0)
    dt = 0.0001
    states[1] = models.run(inhom, weights, states[0], Nt=100, dt=dt)
    states[2] = models.run(inhom, weights, states[0], Nt=10, dt=dt * 10)
    assert np.allclose(states[1], states[2], rtol=1e-3, atol=1e-5)
    assert np.allclose(
        states.squeeze(),
        [
            [4.0000001e-01, 0.0000000e00],
            [4.0485540e-01, 4.8295802e-05],
            [4.0485030e-01, 4.8268699e-05],
        ],
    )
