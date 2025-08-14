# Pigreads: Python-integrated GPU-enabled reaction diffusion solver
# Copyright (c) 2024 Desmond Kabus. All rights reserved.

"""
Pigreads Python module
----------------------

This Python module is the main interface to set up and run Pigreads simulations
solving the reaction-diffusion equations with OpenCL and NumPy:

.. math::

    \\partial_t \\underline{u}
    =
    \\underline{P} \\nabla \\cdot \\mathbf D \\nabla \\underline{u}
    +
    \\underline{r}(\\underline{u})

for :math:`\\underline{u}(t, \\mathbf x)`, :math:`t\\in[0, T]`, and
:math:`\\mathbf x\\in\\Omega\\subset\\mathbb R^3`, with initial conditions and
no-flux boundary conditions.

The following equations define a simpler example with only two variables,
:math:`\\underline{u} = (u, v)`, with no diffusion in :math:`v`, and
homogeneous and isotropic diffusion:

.. math::

    \\begin{aligned}
    \\partial_t u
    &=
    D \\nabla^2 u
    +
    r_u(u, v)
    \\\\
    \\partial_t v
    &=
    r_v(u, v)
    \\end{aligned}

Pigreads performs the most expensive calculations on graphics cards
using OpenCL, see :py:func:`Models.run` and :py:func:`Models.weights`.
Input and output as well as setting up and interacting with the simulation
should be done in Python, with the exception of adding source terms, so-called
stimulus currents. Pigreads uses the simplistic finite-differences method and
forward-Euler time stepping.

A Pigreads simulation is usually defined in the following steps:
First, define the geometry of the medium. In this example, we use a 2D plane
with 200 points in both x and y::

    import pigreads as pig
    import numpy as np

    R = 10.
    z, y, x = np.mgrid[0:1, -R:R:200j, -R:R:200j]
    dz, dy, dx = pig.deltas(z, y, x)
    r = np.linalg.norm((x, y, z), axis=0)

Pigreads is optimised for three-dimensional space. For
lower-dimensional simulations, set the number of points in additional
dimensions to one, as done above for the z-dimension.

Calculations are performed at all points with periodic boundary conditions.
The integer field ``inhom`` defines which points are inside (1) the medium and outside (0)::

    inhom = np.ones_like(x, dtype=int)
    inhom[r >= R] = 0

Values of inhom larger than zero can be used to select one of multiple models,
i.e., reaction terms :math:`\\underline{r}`. For an ``inhom`` value of 1,
``models[0]`` is used; and ``models[1]`` for a value of 2, etc. One or more of the
available models can be selected using an instance of the :py:class:`Models`
class::

    models = pig.Models()
    models.add("marcotte2017dynamical", beta=1.389)

This class also has a function to create an array of the same shape as ``inhom``
in space but for a given number of frames in time. The first frame is filled
with the appropriate resting values for each model. Initial conditions can then
be set in the 0th frame::

    states = models.resting_states(inhom, Nframes=100)
    states[0, x < -8, 0] = 1
    states[0, y < 0, 1] = 2

Note that states has five indices, in this order: time, z, y, x, state variable.
This indexing is consistently used in Pigreads and NumPy.

The calculation of the diffusion term :math:`\\underline{P} \\nabla \\cdot
\\mathbf D \\nabla \\underline{u}` is implemented as a weighted sum of neighbouring points.
The weights can be calculated using the function :py:func:`weights`, which also requires the
diffusivity_matrix :math:`D` as input, which is set using :py:func:`diffusivity_matrix`::

    diffusivity = pig.diffusivity_matrix(Df=0.03)
    weights = pig.weights(dz, dy, dx, inhom, diffusivity)

Finally, the simulation can be started using :py:func:`run`, which does ``Nt``
forward-Euler steps and only returns the final states after those steps::

    Nt = 200
    dt = 0.025
    for it in range(states.shape[0] - 1):
        states[it + 1] = pig.run(models, inhom, weights, states[it], Nt=Nt, dt=dt)

The 5D array states can now be analysed and visualised, for instance with Matplotlib:

    import matplotlib.pyplot as plt
    plt.imshow(states[-1, 0, :, :, 0])
    plt.show()

Full examples with more sophisticated plotting outputting an MP4 movie, a
progress bar, and stability checks can be found in the ``examples`` folder in
the Git repository of this project.
"""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from datetime import datetime
from pathlib import Path
from textwrap import dedent, indent
from typing import Any, ClassVar

import numpy as np

import pigreads.models
from pigreads import core as _core
from pigreads import core1 as _core1
from pigreads import core2 as _core2
from pigreads._version import version as __version__
from pigreads.schema.model import ModelDefinition, ModelEntry

# pylint: disable=too-many-lines


def weights(
    dz: float = 1.0,
    dy: float = 1.0,
    dx: float = 1.0,
    inhom: np.ndarray[Any, Any] | None = None,
    diffusivity: np.ndarray[Any, Any] | float = 1.0,
    double_precision: bool = False,
) -> np.ndarray[Any, Any]:
    """
    Calculate the weights for the diffusion term in the reaction-diffusion
    equation.

    The implementation of this function is defined in :py:meth:`Models.weights`.

    :param dz: The distance between points in the z-dimension, see :py:func:`deltas`.
    :param dy: The distance between points in the y-dimension.
    :param dx: The distance between points in the x-dimension.
    :param inhom: A 3D array with integer values, encoding which model to use at each point. \
            Its value is zero for points outside the medium and one or more for points inside. \
            If ``None``, all points are considered inside the medium.
    :param diffusivity: The diffusivity matrix, see :py:func:`diffusivity_matrix`. \
            If a scalar is given, the matrix is isotropic with the same value in all directions.
    :param double_precision: If ``True``, use double precision for calculations.
    :return: Weight matrix for the diffusion term, A 5D array of shape (1, Nz, Ny, Nx, 19).
    """
    models = Models(double_precision=double_precision)
    return models.weights(dz, dy, dx, inhom=inhom, diffusivity=diffusivity)


def run(
    models: Models,
    inhom: np.ndarray[Any, Any],
    weights: np.ndarray[Any, Any],  # pylint: disable=redefined-outer-name
    states: np.ndarray[Any, Any],
    stim_signal: np.ndarray[Any, Any] | None = None,
    stim_shape: np.ndarray[Any, Any] | None = None,
    Nt: int = 1,  # pylint: disable=invalid-name
    dt: float = 0.001,
    double_precision: bool | None = None,
) -> np.ndarray[Any, Any]:
    """
    Run a Pigreads simulation.

    The implementation of this function is defined in :py:meth:`Models.run`.

    :param models: The models to be used in the simulation, see :py:class:`Models`.
    :param inhom: A 3D array with integer values, encoding which model to use at each point. \
            Its value is zero for points outside the medium and one or more for points inside. \
            Values larger than zero are used to select one of multiple models: \
            1 for ``models[0]``, 2 for ``models[1]``, etc.
    :param weights: The weights for the diffusion term, see :py:func:`weights`.
    :param states: The initial states of the simulation, a 4D array of shape \
            (Nz, Ny, Nx, Nv), see :py:func:`Models.resting_states`.
    :param stim_signal: A 3D array with the stimulus signal at each time point \
            for all variables, with shape (Nt, Ns, Nv). If ``None``, no stimulus is applied.
    :param stim_shape: A 4D array specifying the shape of the stimulus, \
            with shape (Ns, Nz, Ny, Nx). If ``None``, no stimulus is applied
    :param Nt: The number of time steps to run the simulation for.
    :param dt: The time step size.
    :param double_precision: If ``True``, use double precision for calculations.
    :return: The final states of the simulation, a 4D array of shape (Nz, Ny, Nx, Nv).
    """
    if double_precision is not None:
        assert models.double_precision == double_precision, (
            "Chosen precision must match with instance of Models."
        )
    return models.run(
        inhom=inhom,
        weights=weights,
        states=states,
        stim_signal=stim_signal,
        stim_shape=stim_shape,
        Nt=Nt,
        dt=dt,
    )


def get_upper_triangle(
    matrix: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """
    Convert a 3x3 matrix to a 6D vector, with the diagonal and upper triangle
    of the matrix as elements in the order xx, yy, zz, yz, xz, xy. Additional
    dimensions are supported, but the last two dimensions must each have size
    3.

    :param matrix: A 3x3 matrix.
    :return: A 6D vector.
    """

    matrix = np.array(matrix)
    assert matrix.ndim >= 2, "matrix must have at least two dimensions"
    assert matrix.shape[-1] == 3, "matrix must be a 3x3 matrix (in the last two axes)"
    assert matrix.shape[-2] == 3, "matrix must be a 3x3 matrix (in the last two axes)"
    assert np.allclose(matrix[..., 1, 2], matrix[..., 2, 1]), (
        "The yz and zy components of matrix need to be the same"
    )
    assert np.allclose(matrix[..., 0, 2], matrix[..., 2, 0]), (
        "The xz and zx components of matrix need to be the same"
    )
    assert np.allclose(matrix[..., 0, 1], matrix[..., 1, 0]), (
        "The xy and yx components of matrix need to be the same"
    )
    triag: np.ndarray[Any, Any] = np.stack(
        (
            matrix[..., 0, 0],  # xx
            matrix[..., 1, 1],  # yy
            matrix[..., 2, 2],  # zz
            matrix[..., 1, 2],  # yz
            matrix[..., 0, 2],  # xz
            matrix[..., 0, 1],  # xy
        ),
        axis=-1,
    )
    return triag


def normalise_vector(
    f: np.ndarray[Any, Any] | list[int] | tuple[int, int, int],
    dtype: type = np.single,
) -> np.ndarray[Any, Any]:
    """
    Normalise a 3D vector to unit length.

    :param f: A 3D vector over space with shape (Nz, Ny, Nx, 3).
    :param dtype: Data type of the arrays, i.e., single or double precision floating point numbers.
    :return: A 5D vector with shape (Nz, Ny, Nx, 3, 1).
    """

    f = np.array(f, dtype=dtype)
    assert isinstance(f, np.ndarray)
    assert f.ndim >= 1, "f must be a 3D vector"
    assert f.ndim <= 4, "too many dimensions for f"
    assert f.shape[-1] == 3, "f must be a 3D vector (in the last axis)"
    while f.ndim < 4:
        f.shape = (1, *f.shape)
    norm = np.linalg.norm(f, axis=-1)
    nonzero = norm > 0
    norm.shape = (*norm.shape, 1)
    f[nonzero] /= norm[nonzero]
    f.shape = (*f.shape, 1)
    assert f.ndim == 5, "f must have 5 dimensions: z, y, x, row, col"
    assert f.shape[-1] == 1, "f must be a 3D column vector"
    assert f.shape[-2] == 3, "f must be a 3D column vector"
    return f


def diffusivity_matrix(
    f: np.ndarray[Any, Any] | list[int] | tuple[int, int, int] | None = None,
    n: np.ndarray[Any, Any] | list[int] | tuple[int, int, int] | None = None,
    Df: np.ndarray[Any, Any] | float = 1.0,  # pylint: disable=invalid-name
    Ds: np.ndarray[Any, Any] | float | None = None,  # pylint: disable=invalid-name
    Dn: np.ndarray[Any, Any] | float | None = None,  # pylint: disable=invalid-name
    dtype: type = np.single,
) -> np.ndarray[Any, Any]:
    """
    Define a diffusivity matrix :math:`\\textbf D` for the reaction-diffusion equation.

    If ``f`` and ``n`` are given, the matrix is defined as:

    .. math::

        \\textbf D = \\textbf D_s \\textbf I + (\\textbf D_f - \\textbf D_s)
        \\textbf f \\textbf f^\\mathrm{T} + (\\textbf D_n - \\textbf D_s)
        \\textbf n \\textbf n^\\mathrm{T}

    :param f: The main direction of diffusion, i.e., the fibre direction. \
            3D vector over space with shape (Nz, Ny, Nx, 3). The last index \
            contains three elements: the x, y, and z component of the vector. \
            Optional if :math:`D_f=D_s=D_n`.
    :param n: The direction of weakest diffusion, i.e., the direction normal to \
            the fibre sheets. A 3D vector over space with shape (Nz, Ny, Nx, 3). The \
            last index contains three elements: the x, y, and z component of the \
            vector. Optional if :math:`D_s=D_n`.
    :param Df: The diffusivity in the direction of the fibres, :math:`\\mathbf{f}`.
    :param Ds: The diffusivity in the fibre sheets, but normal to :math:`\\mathbf{f}`. \
            If ``None``, :math:`D_s` is set to :math:`D_f`.
    :param Dn: The diffusivity in the direction normal to the fibre sheets, \
            i.e., along :math:`\\mathbf{n}`. \
            If ``None``, :math:`D_n` is set to :math:`D_s`.
    :param dtype: Data type of the arrays, i.e., single or double precision floating point numbers.
    :return: A 4D array with shape (Nz, Ny, Nx, 6).

    See also :py:func:`get_upper_triangle` for the convention used for the
    last axis of the output array.
    """

    if Ds is None:
        Ds = Df

    if Dn is None:
        Dn = Ds

    if f is None:
        assert np.allclose(Df, Ds), "If Df!=Ds, f must be given"
        f = [0, 0, 0]

    if n is None:
        assert np.allclose(Ds, Dn), "If Ds!=Dn, n must be given"
        n = [0, 0, 0]

    f = normalise_vector(f, dtype=dtype)
    n = normalise_vector(n, dtype=dtype)
    eye = np.eye(3, dtype=dtype)
    eye.shape = (1, 1, 1, 3, 3)

    D = get_upper_triangle(  # pylint: disable=invalid-name
        Ds * eye
        + np.einsum("...,...ij,...ji->...ij", Df - Ds, f, f)
        + np.einsum("...,...ij,...ji->...ij", Dn - Ds, n, n)
    )
    assert D.ndim == 4
    assert D.shape[-1] == 6
    return D


class ModelParameters(MutableMapping[str, float]):
    """
    A view into the core implementation of the models
    allowing reading and modifying the parameters of a model.

    :param models: Instance of the models class to link to the core.
    :var models: Instance of the models class to link to the core.
    :vartype models: Models
    :param imodel: Index of the model.
    :var imodel: Index of the model.
    :vartype imodel: int
    """

    def __init__(self, models: Models, imodel: int) -> None:
        self._models: Models = models
        self._imodel: int = imodel
        self._keys: list[str] = list(
            models.get_definition(imodel).all_parameters.keys()
        )

    def _key_to_index(self, key: str) -> int:
        """
        Get the index of the parameter with the given key.

        :param key: Key of the parameter.
        :return: Index of the parameter.
        """
        return next(i for i, k in enumerate(self._keys) if k == key)

    def __getitem__(self, key: str) -> float:
        """
        Get the parameter with the given key.

        :param key: Key of the parameter.
        :return: Parameter value.
        """
        return self._models.get_parameter(self._imodel, self._key_to_index(key))

    def __setitem__(self, key: str, value: float) -> None:
        """
        Set the parameter with the given key.

        :param key: Key of the parameter.
        :param value: New value of the parameter.
        """
        self._models.set_parameter(self._imodel, self._key_to_index(key), value)

    def __delitem__(self, key: str) -> None:
        """
        Delete the parameter with the given key.

        Note: This operation is not supported in this class.

        :param key: Key of the parameter.
        """
        message = "Deleting items is not supported in this class."
        raise NotImplementedError(message)

    def __iter__(self) -> Iterator[str]:
        """
        Get an iterator of the keys of the parameters.

        :return: Iterator of the keys of the parameters.
        """
        return iter(self._keys)

    def __len__(self) -> int:
        """
        Get the number of parameters.

        :return: Number of parameters.
        """
        return len(self._keys)

    def to_dict(self) -> dict[str, float]:
        """
        Convert the parameters to a dictionary.

        :return: Dictionary of the parameters.
        """
        return {k: self[k] for k in self._keys}

    def __repr__(self) -> str:
        """
        Get the string representation of the parameters.

        :return: String representation of the parameters.
        """
        return repr(self.to_dict())

    def __str__(self) -> str:
        """
        Get the string representation of the parameters.

        :return: String representation of the parameters.
        """
        return str(self.to_dict())


class Models:
    """
    This class stores the models to be used in a Pigreads simulation. The
    models are defined by OpenCL code. The class variable :py:attr:`available`
    is a dictionary of all available models.

    Models are added to an instance of this class using the :py:meth:`add`
    method, or as a list of tuples in the constructor. The order of the models
    is the order in which they are used in the simulation. ``models[0]`` is used
    at ``inhom`` values of 1, ``models[1]`` at 2, etc.

    :param tuples_key_kwargs: A list of tuples with the model key and keyword \
    arguments encoding parameter names and values to be passed to the \
    :py:meth:`add` method. If a string is given, it is treated the name of the \
    first model to be added with no keyword arguments. If ``None``, no \
    models are added.

    :param double_precision: If ``True``, use double precision for calculations.
    :var double_precision: If ``True``, use double precision for calculations.
    :vartype double_precision: bool
    """

    available: ClassVar[dict[str, ModelDefinition]] = {
        k: ModelDefinition(**v) for k, v in pigreads.models.available.items()
    }
    """
    Dictionary of all available models.
    """

    def __init__(
        self,
        tuples_key_kwargs: list[tuple[str, dict[str, float]]] | str | None = None,
        double_precision: bool = False,
    ):
        self.double_precision: bool = double_precision
        self._core: _core.Models | None = None

        if tuples_key_kwargs is None:
            tuples_key_kwargs = []
        elif isinstance(tuples_key_kwargs, str):
            tuples_key_kwargs = [(tuples_key_kwargs, {})]
        for key, kwargs in tuples_key_kwargs:
            self.add(key, **kwargs)

    @property
    def core(self) -> _core.Models:
        """
        Get the link to the core implementation of this class.
        """
        if self.double_precision:
            if not isinstance(self._core, _core2.Models2):
                self._core = _core2.Models2()
        elif not isinstance(self._core, _core1.Models1):
            self._core = _core1.Models1()
        return self._core

    def __len__(self) -> int:
        """
        The number of models added to the list of models.
        """
        return len(self.core)

    def get_key(self, imodel: int) -> str:
        """
        Get the key of the model with the given index.

        :param imodel: Index of the model.
        """
        return self.core.get_key(imodel)

    def get_definition(self, imodel: int) -> ModelDefinition:
        """
        Get the definition of the model with the given index.

        :param imodel: Index of the model.
        """
        return self.available[self.get_key(imodel)]

    def get_parameter(self, imodel: int, iparam: int) -> float:
        """
        Get the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :return: Parameter value.
        """
        return self.core.get_parameter(imodel, iparam)

    def set_parameter(self, imodel: int, iparam: int, value: float) -> None:
        """
        Set the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :param value: New parameter value.
        """
        self.core.set_parameter(imodel, iparam, value)

    def get_entry(self, imodel: int) -> ModelEntry:
        """
        Get the model entry with the given index linked to the core
        implementation to read and change model parameters.

        :param imodel: Index of the model.
        :return: Model entry with a :py:class:`ModelParameters` view.
        """
        model = ModelEntry(key=self.get_key(imodel))
        model.parameters = ModelParameters(models=self, imodel=imodel)
        return model

    def __getitem__(self, imodel: int) -> ModelEntry:
        """
        Get the model entry with the given index linked to the core
        implementation to read and change model parameters.

        :param imodel: Index of the model.
        :return: Model entry with a :py:class:`ModelParameters` view.
        """
        return self.get_entry(imodel)

    def __iter__(self) -> Iterator[ModelEntry]:
        """
        Get an iterator of model entries linked to the core
        implementation to read and change model parameters.

        :return: Iterator of model entries.
        """
        for imodel in range(len(self)):
            yield self.get_entry(imodel)

    @property
    def block_size(self) -> list[int]:
        """
        Local work size for running OpenCL kernels.

        The ``block_size`` parameter corresponds to OpenCL's ``localWorkSize`` and
        defines the size of a small block of the domain that is processed together by
        the OpenCL platform (typically the GPU).

        If chosen too small, the performance will be suboptimal. If chosen too
        large, the OpenCL kernel will not run. The default value is ``(1, 8, 8)``,
        i.e., a block of unit width in z, and ``8x8`` in the y and x
        dimensions. This is a good compromise for most applications.

        Tweaking this value can lead to significant performance improvements.
        """
        return self.core.get_block_size()

    @block_size.setter
    def block_size(self, block_size: list[int]) -> None:
        """
        Set the local work size for running OpenCL kernels.

        :param block_size: Local work size.
        """
        self.core.set_block_size(block_size)

    def add(self, key: str, **parameters: Any) -> None:
        """
        Select and enable a model with given parameters.

        :param key: The key of the model to be added.
        :param parameters: Parameter names and their values to be passed to the model.
        """
        model_id = self.core.get_number_definitions()
        model_def = self.available[key]
        self.core.add(
            key,
            self.code(key, model_id),
            len(model_def.variables),
            np.array(list(model_def(**parameters).values())),
        )

    def code(self, key: str, model_id: int) -> str:
        """
        OpenCL kernel source code defining a model.

        :param key: The key of the model.
        :param model_id: An integer identifying the model.
        """
        model_def: ModelDefinition = self.available[key]
        code: str = ""
        code += dedent(rf"""
            void Model_{key}_step(
                    Real* const params,
                    struct States weights,
                    struct States states_old,
                    struct States states_new,
                    const Real dt
            ) {{
        """).strip()

        code += "\n"

        for ip, param in enumerate(model_def.all_parameters):
            code += f"  const Real {param} = params[{ip}];\n"

        for ivar, varname in enumerate(model_def.variables):
            code += f"  const Real {varname} = _r(_v({ivar}, states_old));\n"
            code += f"  Real* const _new_{varname} = _pr(_v({ivar}, states_new));\n"
            if varname in model_def.diffusivity:
                code += (
                    f"  const Real _diffuse_{varname} = diffusivity_{varname} "
                    + f"* diffuse(weights, _v({ivar}, states_old));\n"
                )

        code += (
            "\n"
            + indent(model_def.get_code(self.double_precision).strip(), "  ")
            + "\n"
        )
        code += dedent(rf"""
            }}

            __kernel void Model_{key}_kernel(
                    Size model_count,
                    __global Size* model_ids,
                    __global Size* model_offsets,
                    __global Real* model_params,
                    __global void* inhom_data,      struct StatesIdx inhom_idx,
                    __global void* weights_data,    struct StatesIdx weights_idx,
                    __global void* states_old_data, struct StatesIdx states_old_idx,
                    __global void* states_new_data, struct StatesIdx states_new_idx,
                    const Real dt
            ) {{

              struct States inhom      = {{inhom_data,      STATES_UNPACK(inhom_idx)}};
              struct States weights    = {{weights_data,    STATES_UNPACK(weights_idx)}};
              struct States states_old = {{states_old_data, STATES_UNPACK(states_old_idx)}};
              struct States states_new = {{states_new_data, STATES_UNPACK(states_new_idx)}};

              const Size iz = get_global_id(0);
              const Size iy = get_global_id(1);
              const Size ix = get_global_id(2);

              if (ix < states_old.Nx && iy < states_old.Ny && iz < states_old.Nz) {{
                const Int inhom_zyx = _i(States_offset(inhom, 0, iz, iy, ix, 0));
                if (inhom_zyx > 0) {{
                  const Size imodel = (inhom_zyx - 1) % model_count;
                  const Size model_id = model_ids[imodel];
                  if (model_id == {model_id}) {{
                    Real* params = model_params + model_offsets[imodel];
                    struct States w = States_offset(weights, 0, iz, iy, ix, 0);
                    struct States u = States_offset(states_old, 0, iz, iy, ix, 0);
                    struct States u_ = States_offset(states_new, 0, iz, iy, ix, 0);
                    Model_{key}_step(params, w, u, u_, dt);
                  }}
                }}
              }}
            }}
        """).strip()

        return code

    @property
    def Nv(self) -> int:  # pylint: disable=invalid-name
        """
        Maximum number of state variables in the models.
        """
        return self.core.Nv

    @property
    def dtype(self) -> type:
        """
        Data type to use for calculations,
        i.e., single or double precision floating point numbers.
        """
        dtype: type = np.double if self.double_precision else np.single
        return dtype

    def resting_states(
        self,
        inhom: np.ndarray[Any, Any],
        Nframes: int = 1,  # pylint: disable=invalid-name
        dtype: type | None = None,
    ) -> np.ndarray[Any, Any]:
        """
        Create an array of states and fill the first frame with the resting
        values of the models depending on the ``inhom`` values.

        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                Values larger than zero are used to select one of multiple models: \
                1 for ``models[0]``, 2 for ``models[1]``, etc.
        :param Nframes: The number of frames in time.
        :param dtype: Data type of the arrays, \
                i.e., single or double precision floating point numbers.
        :return: A 5D array of shape (Nframes, Nz, Ny, Nx, Nv).
        """

        if dtype is None:
            dtype = self.dtype

        model_count = len(self)
        assert model_count > 0, "must add at least one model"
        assert inhom.ndim == 3
        inhom = inhom.astype(int)
        mask = inhom > 0
        states: np.ndarray[Any, Any] = np.full(
            (Nframes, *inhom.shape, self.Nv), np.nan, dtype=dtype
        )
        for imodel in range(len(self)):
            model_def = self.get_definition(imodel)
            for iv, resting in enumerate(model_def.variables.values()):
                states[0, mask * ((inhom - 1) % model_count == imodel), iv] = resting
        states[:, ~mask, :] = np.nan
        return states

    def weights(
        self,
        dz: float = 1.0,
        dy: float = 1.0,
        dx: float = 1.0,
        inhom: np.ndarray[Any, Any] | None = None,
        diffusivity: np.ndarray[Any, Any] | float = 1.0,
    ) -> np.ndarray[Any, Any]:
        """
        Calculate the weights for the diffusion term in the reaction-diffusion
        equation.

        :param dz: The distance between points in the z-dimension, see :py:func:`deltas`.
        :param dy: The distance between points in the y-dimension.
        :param dx: The distance between points in the x-dimension.
        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                If ``None``, all points are considered inside the medium.
        :param diffusivity: The diffusivity matrix, see :py:func:`diffusivity_matrix`. \
                If a scalar is given, the matrix is isotropic with the same value in all directions.
        :return: Weight matrix for the diffusion term, A 5D array of shape (1, Nz, Ny, Nx, 19).
        """

        assert dz > 0
        assert dy > 0
        assert dx > 0

        if inhom is None:
            inhom = np.ones(shape=(1, 1, 1), dtype=self.dtype)
        assert inhom.ndim == 3

        mask = inhom > 0
        mask.shape = (1, *mask.shape, 1)

        diffusivity = np.array(diffusivity, dtype=self.dtype)
        assert isinstance(diffusivity, np.ndarray)
        if diffusivity.ndim == 0:
            diffusivity = diffusivity_matrix(
                Df=float(diffusivity.item()), dtype=self.dtype
            )
        assert diffusivity.ndim == 4
        assert diffusivity.shape[-1] == 6

        return self.core.weights(dz, dy, dx, mask, diffusivity)

    def run(
        self,
        inhom: np.ndarray[Any, Any],
        weights: np.ndarray[Any, Any],  # pylint: disable=redefined-outer-name
        states: np.ndarray[Any, Any],
        stim_signal: np.ndarray[Any, Any] | None = None,
        stim_shape: np.ndarray[Any, Any] | None = None,
        Nt: int = 1,  # pylint: disable=invalid-name
        dt: float = 0.001,
    ) -> np.ndarray[Any, Any]:
        """
        Run a Pigreads simulation.

        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                Values larger than zero are used to select one of multiple models: \
                1 for ``models[0]``, 2 for ``models[1]``, etc.
        :param weights: The weights for the diffusion term, see :py:func:`weights`.
        :param states: The initial states of the simulation, a 4D array of shape \
                (Nz, Ny, Nx, Nv), see :py:func:`Models.resting_states`.
        :param stim_signal: A 3D array with the stimulus signal at each time point \
                for all variables, with shape (Nt, Ns, Nv). If ``None``, no stimulus is applied.
        :param stim_shape: A 4D array specifying the shape of the stimulus, \
                with shape (Ns, Nz, Ny, Nx). If ``None``, no stimulus is applied
        :param Nt: The number of time steps to run the simulation for.
        :param dt: The time step size.
        :return: The final states of the simulation, a 4D array of shape (Nz, Ny, Nx, Nv).
        """
        assert Nt > 0
        assert dt > 0
        assert len(self) > 0, "must add at least one model"
        assert inhom.ndim == 3

        if stim_signal is None or getattr(stim_signal, "size", 0) == 0:
            stim_signal = np.zeros((0, 0, 0, 0, 0), dtype=self.dtype)
        else:  # np.ndarray
            assert stim_signal.ndim in [2, 3]
            stim_signal = np.reshape(
                stim_signal, (stim_signal.shape[0], -1, 1, 1, self.Nv)
            )

        assert isinstance(stim_signal, np.ndarray)
        Ns = stim_signal.shape[1]  # pylint: disable=invalid-name

        if stim_shape is None or getattr(stim_shape, "size", 0) == 0:
            stim_shape = np.zeros((0, 0, 0, 0, 0), dtype=self.dtype)
        else:  # np.ndarray
            assert stim_shape.ndim in [3, 4]
            stim_shape = np.where(inhom > 0, stim_shape, 0)
            stim_shape.shape = (Ns, *stim_shape.shape[-3:], 1)  # type: ignore[union-attr]

        assert isinstance(stim_shape, np.ndarray)
        assert stim_shape.shape[0] == stim_signal.shape[1]

        return self.core.run(
            np.reshape(inhom, (*inhom.shape, 1)),
            weights,
            states,
            stim_signal,
            stim_shape,
            Nt,
            dt,
        )


def to_ithildin(
    framedur: float,
    dt: float,
    dz: float,
    dy: float,
    dx: float,
    models: Models,
    states: np.ndarray[Any, Any],
    inhom: np.ndarray[Any, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, np.ndarray[Any, Any]]]:
    """
    Convert the output of a Pigreads simulation to an Ithildin SimData object.

    While originally designed for a different reaction-diffusion solver,
    the Python module for Ithildin is useful to analyse Pigreads simulations.

    :param framedur: The duration between subsequent frames, usually in milliseconds.
    :param dt: The time step size used in :py:func:`run`, usually in milliseconds.
    :param dz: The distance between points in the z-dimension, see :py:func:`deltas`.
    :param dy: The distance between points in the y-dimension.
    :param dx: The distance between points in the x-dimension.
    :param models: The models used in the simulation, see :py:class:`Models`.
    :param states: The states of the simulation, a 5D array of shape \
            (Nt, Nz, Ny, Nx, Nv), see :py:func:`Models.resting_states` and :py:func:`run`.
    :param inhom: A 3D array with integer values, encoding which model to use at each point. \
            Its value is zero for points outside the medium and one or more for points inside. \
            If ``None``, all points are considered inside the medium.
    :return: Tuple of an Ithildin log file as a string \
            and a dictionary of the variables by variable name.

    Usage::

        import ithildin as ith
        log, variables = pig.to_ithildin(Nt * dt, dt, dz, dy, dx, models, states, inhom)
        sd = ith.SimData(log=ith.Log(data=log))
        sd.vars = variables
    """

    Nt, Nz, Ny, Nx, _ = states.shape  # pylint: disable=invalid-name

    timestamp = datetime.now()

    log = {
        "Ithildin log version": 2,
        "Simulation parameters": {
            "Ithildin library version": f"pigreads {__version__}",
            "Timestep dt": dt,
            "Frame duration": framedur,
            "Number of frames to take": Nt,
            "Serial number": int(timestamp.strftime(r"%Y%m%d%H%M%S")),
            "Name of simulation series": "pigreads",
        },
        "Geometry parameters": {
            "Number of dimensions": 3,
            "Voxel size": [dx, dy, dz],
            "Domain size": [Nx, Ny, Nz],
        },
        "Start date": timestamp.isoformat(),
    }

    for i, model in enumerate(models):
        model_def = models.available[model.key]
        key = "Model parameters"
        if i > 0:
            key += f" {i}"
        log[key] = {
            "Model type": model_def.name,
            "Class": model.key,
            "Citation": "\n".join(model_def.dois),
            "Parameters": model_def(**model.parameters),
            "Initial values": model_def.variables,
            "Variable names": list(model_def.variables.keys()),
            "Number of vars": len(model_def.variables),
        }

    shape = (-1, Nz, Ny, Nx)
    variables: dict[str, np.ndarray[Any, Any]] = {
        v: states[..., iv].reshape(shape)
        for iv, v in enumerate(models.available[models[0].key].variables.keys())
    }
    if inhom is not None:
        variables["inhom"] = inhom.reshape(shape)

    return log, variables


def delta(x: np.ndarray[Any, Any], ax: int = -1) -> float:
    """
    Extract grid spacing from a 3D array.

    :param x: A 3D array.
    :param ax: The axis along which to calculate the distance.
    :return: The distance between the first two points.

    For example, consider this code::

        z, y, x = np.mgrid[0, 0:4:0.2, 0:1:5j]
        dx = pig.delta(z, ax=-1)
        dy = pig.delta(z, ax=-2)
        dz = pig.delta(z, ax=-3)
    """
    assert x.ndim == 3
    diff = np.diff(np.moveaxis(x, ax, -1)[0, 0, :2])
    return 1.0 if diff.shape[0] == 0 else float(diff[0])


def deltas(*x: np.ndarray[Any, Any]) -> list[float]:
    """
    Extract grid spacing from a 3D meshgrid.

    For example, consider this code::

        z, y, x = np.mgrid[0, 0:4:0.2, 0:1:5j]
        dz, dy, dx = pig.deltas(z, y, x)

    :param x: A 3D array.
    :return: A list with the distances between the points.
    """
    return [delta(xi, i) for i, xi in enumerate(x)]


def prepare_array(
    shape: tuple[int, ...],
    path: Path | str | None = None,
    dtype: type = np.single,
) -> np.ndarray[Any, Any]:
    """
    Prepare an array in a given shape.

    Either create a new array or load an existing array from the file with
    the given path as a memory map.

    The shape and dtype of the array are given as arguments. If the path is
    ``None``, a new array is created. If the path is a file, the array is
    loaded from the file. If the array is not of the correct shape or dtype
    or the file does not exist, a new array is created.

    The array is returned as a memory map if a path is given, otherwise as a
    normal numpy array.

    :param shape: Shape of the array.
    :param path: Path to the file to load the array from.
    :param dtype: Data type of the arrays, i.e., single or double precision floating point numbers.
    :return: Resulting array.
    :see: :py:func:`numpy.lib.format.open_memmap`
    """

    if path is None:
        return np.zeros(shape=shape, dtype=dtype)

    path = Path(path)
    if path.is_file():
        arr = np.lib.format.open_memmap(path, "r+")  # type: ignore[no-untyped-call]
        if isinstance(arr, np.ndarray) and arr.shape == shape and arr.dtype == dtype:
            return arr

    arr = np.lib.format.open_memmap(  # type: ignore[no-untyped-call]
        path,
        "w+",
        dtype=dtype,
        shape=shape,
    )
    assert isinstance(arr, np.ndarray)
    arr[:] = np.nan
    return arr


__all__ = [
    "ModelParameters",
    "Models",
    "__version__",
    "delta",
    "deltas",
    "diffusivity_matrix",
    "get_upper_triangle",
    "normalise_vector",
    "prepare_array",
    "run",
    "to_ithildin",
    "weights",
]
