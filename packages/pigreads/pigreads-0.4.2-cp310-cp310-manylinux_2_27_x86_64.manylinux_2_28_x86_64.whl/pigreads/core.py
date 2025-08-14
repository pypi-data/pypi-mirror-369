"""
Base classes for low-level implementation
-----------------------------------------
"""

from __future__ import annotations

from typing import Any

import numpy as np

ERROR_MSG = "Base class should not be called directly."


class Models:
    """
    Base class for the core implementation of the ``Models`` class.

    :see: :py:class:`pigreads.Models` for the main interface to the models.

    The single- and double-precision core C++ implementations inherit from this
    base class.
    """

    Nv: int
    "Maximum number of state variables in the models."

    def __init__(self) -> None:
        raise NotImplementedError(ERROR_MSG)

    def __len__(self) -> int:
        """
        Get the number of models.

        :return: Number of models.
        """
        raise NotImplementedError(ERROR_MSG)

    def get_number_definitions(self) -> int:
        """
        Get the number of model definitions.

        :return: Number of model definitions
        """
        raise NotImplementedError(ERROR_MSG)

    def get_key(self, imodel: int) -> str:
        """
        Get the key of the model with the given index.

        :param imodel: Index of the model.
        :return: Key of the model with the given index.
        """
        raise NotImplementedError(ERROR_MSG)

    def get_parameter(self, imodel: int, iparam: int) -> float:
        """
        Get the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :return: Parameter value.
        """
        raise NotImplementedError(ERROR_MSG)

    def set_parameter(self, imodel: int, iparam: int, value: float) -> None:
        """
        Set the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :param value: New parameter value.
        """
        raise NotImplementedError(ERROR_MSG)

    def get_block_size(self) -> list[int]:
        """
        Get the local work size for running OpenCL kernels.

        :return: Local work size.
        """
        raise NotImplementedError(ERROR_MSG)

    def set_block_size(self, block_size: list[int]) -> None:
        """
        Set the local work size for running OpenCL kernels.

        :param block_size: Local work size.
        """
        raise NotImplementedError(ERROR_MSG)

    def add(self, key: str, code: str, Nv: int, params: np.ndarray[Any, Any]) -> None:  # pylint: disable=invalid-name
        """
        Select and enable a model with given parameters.

        :param key: The key of the model to be added.
        :param code: OpenCL code for the model.
        :param Nv: Number of variables.
        :param params: Parameter values.
        """
        raise NotImplementedError(ERROR_MSG)

    def weights(
        self,
        dz: Any,
        dy: Any,
        dx: Any,
        mask: np.ndarray[Any, Any],
        diffusivity: np.ndarray[Any, Any],
    ) -> np.ndarray[Any, Any]:
        """
        Calculate the weights for the diffusion term in the reaction-diffusion
        equation.

        :param dz: The distance between points in the z-dimension.
        :param dy: The distance between points in the y-dimension.
        :param dx: The distance between points in the x-dimension.
        :param mask: 3D boolean array encoding which points are inside the medium.
        :param diffusivity: The diffusivity matrix.
        :return: Weight matrix for the diffusion term, A 5D array of shape (1, Nz, Ny, Nx, 19).
        """
        raise NotImplementedError(ERROR_MSG)

    def run(
        self,
        inhom: np.ndarray[Any, Any],
        weights: np.ndarray[Any, Any],
        states: np.ndarray[Any, Any],
        stim_signal: np.ndarray[Any, Any],
        stim_shape: np.ndarray[Any, Any],
        Nt: Any,  # pylint: disable=invalid-name
        dt: Any,
    ) -> np.ndarray[Any, Any]:
        """
        Run a Pigreads simulation.

        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                Values larger than zero are used to select one of multiple models: \
                1 for ``models[0]``, 2 for ``models[1]``, etc.
        :param weights: The weights for the diffusion term, see :py:func:`weights`.
        :param states: The initial states of the simulation, a 4D array of shape \
                (Nz, Ny, Nx, Nv).
        :param stim_signal: A 3D array with the stimulus signal at each time point \
                for all variables, with shape (Nt, Ns, Nv).
        :param stim_shape: A 4D array specifying the shape of the stimulus, \
                with shape (Ns, Nz, Ny, Nx).
        :param Nt: The number of time steps to run the simulation for.
        :param dt: The time step size.
        :return: The final states of the simulation, a 4D array of shape (Nz, Ny, Nx, Nv).
        """
        raise NotImplementedError(ERROR_MSG)


__all__ = ["Models"]
