from __future__ import annotations

import numpy as np

import pigreads as pig


def test_trivial():
    weights = pig.weights()
    assert weights.shape == (1, 1, 1, 1, 19)
    weights = weights.flatten()
    assert weights[0] == -6
    for i in range(1, 7):
        assert weights[i] == 1
    for i in range(7, 19):
        assert weights[i] == 0


def test_scaling():
    assert np.allclose(pig.weights(diffusivity=2), 2 * pig.weights())


def test_matrix():
    diffusivity = pig.diffusivity_matrix(Df=1, Ds=0.5, Dn=0.1, f=[1, 2, 3], n=[4, 5, 6])
    weights = pig.weights(diffusivity=diffusivity)
    assert np.allclose(
        weights.flatten(),
        [
            -3.2,
            0.45259738,
            0.45259738,
            0.512987,
            0.512987,
            0.63441557,
            0.63441557,
            0.02922077,
            -0.02922077,
            -0.02922077,
            0.02922077,
            -0.00876624,
            0.00876624,
            0.00876624,
            -0.00876624,
            -0.01623377,
            0.01623377,
            0.01623377,
            -0.01623377,
        ],
    )


def test_dot():
    z, y, x = np.mgrid[0:5, 0:5, 0:5]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.zeros_like(x, dtype=int)
    inhom[2, 2, 2] = 1
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 5, 5, 5, 19)
    assert np.allclose(weights, 0)


def test_cable_x():
    z, y, x = np.mgrid[0:5, 0:5, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.zeros_like(x, dtype=int)
    inhom[2, 2, :] = 1
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 5, 5, 1, 19)
    weights = weights[0, 2, 2, 0]
    assert weights[0] == -2
    assert weights[1] == 1
    assert weights[2] == 1
    for i in range(3, 19):
        assert weights[i] == 0


def test_cable_y():
    z, y, x = np.mgrid[0:5, 0:1, 0:5]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.zeros_like(x, dtype=int)
    inhom[2, :, 2] = 1
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 5, 1, 5, 19)
    weights = weights[0, 2, 0, 2]
    assert weights[0] == -2
    assert weights[3] == 1
    assert weights[4] == 1
    for i in range(1, 3):
        assert weights[i] == 0
    for i in range(5, 19):
        assert weights[i] == 0


def test_cable_z():
    z, y, x = np.mgrid[0:1, 0:5, 0:5]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.zeros_like(x, dtype=int)
    inhom[:, 2, 2] = 1
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 1, 5, 5, 19)
    weights = weights[0, 0, 2, 2]
    assert weights[0] == -2
    assert weights[5] == 1
    assert weights[6] == 1
    for i in range(1, 5):
        assert weights[i] == 0
    for i in range(7, 19):
        assert weights[i] == 0


def test_edge_x():
    z, y, x = np.mgrid[0:1, 0:1, 0:4]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[:, :, 0] = 0
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 1, 1, 4, 19)
    weights = weights[0, 0, 0, :, :]
    assert np.allclose(np.sum(weights, axis=-1), 0)
    assert np.allclose(weights[0], 0)
    assert np.allclose(weights[2], pig.weights().flatten())
    weights[3, 1], weights[3, 2] = weights[3, 2], weights[3, 1]
    assert np.allclose(weights[1], weights[3])
    assert weights[1, 0] == -5
    assert np.allclose(weights[1][8:], 0)


def test_edge_y():
    z, y, x = np.mgrid[0:1, 0:4, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[:, 0, :] = 0
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 1, 4, 1, 19)
    weights = weights[0, 0, :, 0, :]
    assert np.allclose(np.sum(weights, axis=-1), 0)
    assert np.allclose(weights[0], 0)
    assert np.allclose(weights[2], pig.weights().flatten())
    weights[3, 3], weights[3, 4] = weights[3, 4], weights[3, 3]
    assert np.allclose(weights[1], weights[3])
    assert weights[1, 0] == -5
    assert np.allclose(weights[1][8:], 0)


def test_edge_z():
    z, y, x = np.mgrid[0:4, 0:1, 0:1]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[0, :, :] = 0
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 4, 1, 1, 19)
    weights = weights[0, :, 0, 0, :]
    assert np.allclose(np.sum(weights, axis=-1), 0)
    assert np.allclose(weights[0], 0)
    assert np.allclose(weights[2], pig.weights().flatten())
    weights[3, 5], weights[3, 6] = weights[3, 6], weights[3, 5]
    assert np.allclose(weights[1], weights[3])
    assert weights[1, 0] == -5
    assert np.allclose(weights[1][8:], 0)


def test_corner_xy():
    z, y, x = np.mgrid[0:1, 0:4, 0:4]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[:, :, 0] = 0
    inhom[:, 0, :] = 0
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 1, 4, 4, 19)
    weights = weights[0, 0, :, :, :]
    assert np.allclose(np.sum(weights, axis=-1), 0)
    assert np.allclose(weights[0, :], 0)
    assert np.allclose(weights[:, 0], 0)
    assert np.allclose(weights[2, 2], pig.weights().flatten())
    assert weights[+1, +1, 0] == -4
    assert weights[-1, -1, 0] == -4
    assert weights[+1, -1, 0] == -4
    assert weights[-1, -1, 0] == -4
    assert weights[2, -1, 0] == -5
    assert weights[2, +1, 0] == -5
    assert weights[-1, 2, 0] == -5
    assert weights[+1, 2, 0] == -5


def test_corner_xz():
    z, y, x = np.mgrid[0:4, 0:1, 0:4]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[:, :, 0] = 0
    inhom[0, :, :] = 0
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 4, 1, 4, 19)
    weights = weights[0, :, 0, :, :]
    assert np.allclose(np.sum(weights, axis=-1), 0)
    assert np.allclose(weights[0, :], 0)
    assert np.allclose(weights[:, 0], 0)
    assert np.allclose(weights[2, 2], pig.weights().flatten())
    assert weights[+1, +1, 0] == -4
    assert weights[-1, -1, 0] == -4
    assert weights[+1, -1, 0] == -4
    assert weights[-1, -1, 0] == -4
    assert weights[2, -1, 0] == -5
    assert weights[2, +1, 0] == -5
    assert weights[-1, 2, 0] == -5
    assert weights[+1, 2, 0] == -5


def test_cube():
    z, y, x = np.mgrid[0:4, 0:4, 0:4]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[:, :, 0] = 0
    inhom[:, 0, :] = 0
    inhom[0, :, :] = 0
    weights = pig.weights(dz, dy, dx, inhom)
    assert weights.shape == (1, 4, 4, 4, 19)
    weights = weights[0, :, :, :, :]
    assert np.allclose(np.sum(weights, axis=-1), 0)
    assert np.allclose(weights[0, :, :], 0)
    assert np.allclose(weights[:, 0, :], 0)
    assert np.allclose(weights[:, :, 0], 0)
    assert np.allclose(weights[2, 2, 2], pig.weights().flatten())
    assert weights[+1, +1, +1, 0] == -3
    assert weights[+1, +1, -1, 0] == -3
    assert weights[+1, -1, +1, 0] == -3
    assert weights[+1, -1, -1, 0] == -3
    assert weights[-1, +1, +1, 0] == -3
    assert weights[-1, +1, -1, 0] == -3
    assert weights[-1, -1, +1, 0] == -3
    assert weights[-1, -1, -1, 0] == -3
    assert weights[2, +1, +1, 0] == -4
    assert weights[2, -1, -1, 0] == -4
    assert weights[2, +1, -1, 0] == -4
    assert weights[2, -1, -1, 0] == -4
    assert weights[+1, 2, +1, 0] == -4
    assert weights[-1, 2, -1, 0] == -4
    assert weights[+1, 2, -1, 0] == -4
    assert weights[-1, 2, -1, 0] == -4
    assert weights[+1, +1, 2, 0] == -4
    assert weights[-1, -1, 2, 0] == -4
    assert weights[+1, -1, 2, 0] == -4
    assert weights[-1, -1, 2, 0] == -4
    assert weights[2, 2, -1, 0] == -5
    assert weights[2, 2, +1, 0] == -5
    assert weights[2, -1, 2, 0] == -5
    assert weights[2, +1, 2, 0] == -5
    assert weights[-1, 2, 2, 0] == -5
    assert weights[+1, 2, 2, 0] == -5


def test_double():
    z, y, x = np.mgrid[0:4, 0:4, 0:4]
    dz, dy, dx = pig.deltas(z, y, x)
    inhom = np.ones_like(x, dtype=int)
    inhom[:, :, 0] = 0
    inhom[:, 0, :] = 0
    inhom[0, :, :] = 0
    single = pig.weights(dz, dy, dx, inhom, double_precision=False)
    double = pig.weights(dz, dy, dx, inhom, double_precision=True)
    assert np.allclose(single, double)
