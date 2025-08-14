from __future__ import annotations

import numpy as np
import pytest

import pigreads as pig


def test_no_Ds():
    assert np.allclose(pig.diffusivity_matrix(Df=2), pig.diffusivity_matrix(Df=2, Ds=2))


def test_no_Df():
    assert np.allclose(
        pig.diffusivity_matrix(Df=2, Ds=2), pig.diffusivity_matrix(Df=2, Ds=2, Dn=2)
    )


def test_no_f():
    with pytest.raises(AssertionError):
        pig.diffusivity_matrix(Df=1, Ds=0.1)


def test_f():
    D = pig.diffusivity_matrix(Df=1, Ds=0.5, f=[1, 0, 0])
    assert D.shape == (1, 1, 1, 6)
    assert np.allclose([1, 0.5, 0.5, 0, 0, 0], D)


def test_no_n():
    with pytest.raises(AssertionError):
        pig.diffusivity_matrix(Df=1, Ds=0.5, Dn=0.1, f=[1, 0, 0])


def test_xyz():
    D = pig.diffusivity_matrix(Df=1, Ds=0.5, Dn=0.1, f=[1, 0, 0], n=[0, 1, 0])
    assert D.shape == (1, 1, 1, 6)
    assert np.allclose(D, [1, 0.1, 0.5, 0, 0, 0])


def test_123():
    D = pig.diffusivity_matrix(Df=1, Ds=0.5, Dn=0.1, f=[1, 2, 3], n=[0, 1, 2])
    assert D.shape == (1, 1, 1, 6)
    assert np.allclose(
        D, [0.53571427, 0.56285715, 0.5014285, 0.05428569, 0.10714285, 0.07142857]
    )


def test_multiple():
    random = np.random.default_rng(seed=0)
    a = random.uniform(size=(3,))
    f = np.array([a, a])
    n = np.array([a, a])
    D = pig.diffusivity_matrix(Df=1, Ds=0.5, Dn=0.1, f=f, n=n)
    assert D.shape == (1, 1, 2, 6)
    assert np.allclose(D[0, 0, 0], D[0, 0, 1])
