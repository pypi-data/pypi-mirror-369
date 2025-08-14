from __future__ import annotations

import numpy as np
import pytest

import pigreads as pig


def test_small():
    with pytest.raises(AssertionError):
        pig.normalise_vector(np.array([]))


def test_large():
    with pytest.raises(AssertionError):
        pig.normalise_vector(np.ones((1, 1, 1, 1, 1)))


def test_2():
    with pytest.raises(AssertionError):
        pig.normalise_vector(np.ones((2, 2, 2)))


def test_034():
    nvec = pig.normalise_vector([0, 3, 4])
    assert nvec.shape == (1, 1, 1, 3, 1), "5 dimensions: z, y, x, row, col"
    assert np.allclose(nvec.flatten(), [0, 0.6, 0.8])


def test_000():
    assert np.allclose(pig.normalise_vector([0, 0, 0]), [0, 0, 0])


def test_random():
    random = np.random.default_rng(seed=0)
    vec = random.uniform(size=(2, 4, 2, 3))
    nvec = pig.normalise_vector(vec)
    assert nvec.shape == (2, 4, 2, 3, 1), "5 dimensions: z, y, x, row, col"
    length = np.linalg.norm(nvec, axis=(-2))
    assert np.allclose(length, 1)
