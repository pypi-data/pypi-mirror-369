from __future__ import annotations

import numpy as np
import pytest

import pigreads as pig


def test_ndim():
    with pytest.raises(AssertionError):
        pig.get_upper_triangle(np.array([]))


def test_22():
    with pytest.raises(AssertionError):
        pig.get_upper_triangle(np.ones((2, 2)))


def test_32():
    with pytest.raises(AssertionError):
        pig.get_upper_triangle(np.ones((3, 2)))


def test_23():
    with pytest.raises(AssertionError):
        pig.get_upper_triangle(np.ones((2, 3)))


def test_symmetry():
    M = np.arange(9).reshape((3, 3))
    with pytest.raises(AssertionError):
        pig.get_upper_triangle(M)


def test_33():
    M = np.arange(9).reshape((3, 3))
    M[1, 0] = M[0, 1]
    M[2, 0] = M[0, 2]
    M[2, 1] = M[1, 2]
    T = pig.get_upper_triangle(M)
    assert T.ndim == 1
    assert T.shape == (6,)
    assert np.allclose(T, [0, 4, 8, 5, 2, 1])


def test_9933():
    shape = (9, 9, 3, 3)
    M = np.arange(np.prod(shape)).reshape(shape)
    M[..., 1, 0] = M[..., 0, 1]
    M[..., 2, 0] = M[..., 0, 2]
    M[..., 2, 1] = M[..., 1, 2]
    T = pig.get_upper_triangle(M)
    assert T.ndim == 3
    assert T.shape == (*shape[:2], 6)
