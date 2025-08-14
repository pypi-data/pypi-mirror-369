"""
Setters for arrays
------------------
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from pigreads.schema import basic

if TYPE_CHECKING:
    import pigreads
    import pigreads.schema


class SetterFile(BaseModel):
    """
    Set an array to the contents of a file.

    The file should contain a numpy array with the same shape as the array to be set.

    :see: :py:func:`numpy.load`
    """

    cmd: Literal["file"] = "file"
    "Identifier for this setter."
    file: Path
    "Path to the file containing the array."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(
        self, array: np.ndarray[Any, Any], _: pigreads.schema.Simulation
    ) -> np.ndarray[Any, Any]:
        """
        Set the array to the contents of the file.

        :param array: Array to set.
        :return: Array set to the contents of the file.
        """
        array[:] = np.load(self.file)
        return array


class SetterSlices(BaseModel):
    """
    Set slices of an array to a value.

    The slices are defined by a list of :py:class:`pigreads.schema.basic.Slice` objects.
    Only where all slices are true, the value is set.
    """

    cmd: Literal["slice"] | Literal["slices"] = "slices"
    "Identifier for this setter."
    value: float
    "Value to set in the slices."
    slices: list[basic.Slice] = Field(default_factory=list)
    "List of slices."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(self, array: np.ndarray[Any, Any], _: Any) -> np.ndarray[Any, Any]:
        """
        Set the slices of the array to the value.

        :param array: Array to set.
        :return: Array with the slices set to the value.
        """
        array = np.array(array)
        selection: list[int | slice] = [slice(None)] * array.ndim
        for i, _ in enumerate(selection):
            for s in self.slices:
                j = s.axis
                if j < 0:
                    j += array.ndim
                if i == j:
                    selection[i] = s()
        array[*selection] = self.value
        return array

    @model_validator(mode="before")
    @classmethod
    def normalise(cls, values: Any) -> Any:
        """
        Normalise the setter.

        If there is only one slice, it is converted to a list of slices.

        :param values: Any data to try to interpret.
        :return: Normalised data.
        """

        if isinstance(values, dict):
            axis = values.get("axis")
            start = values.get("start")
            end = values.get("end")
            step = values.get("step")
            if axis is not None:
                values["slices"] = values.get("slices", [])
                values["slices"].append(
                    {
                        "axis": axis,
                        "start": start,
                        "end": end,
                        "step": step,
                    }
                )
                for key in ["axis", "start", "end", "step"]:
                    if key in values:
                        del values[key]

        return values


class SetterSpherical(BaseModel):
    """
    Set an array to a value inside or outside a sphere or ellipsoid.

    The ellipsoid is defined by a center and a radii in each dimension. If not
    none, the inside and outside values are set to given values.

    If not given, the radius is set to half the size of the array in each dimension,
    and the center is set to the center of the array.
    """

    cmd: Literal["spherical"] = "spherical"
    "Identifier for this setter."
    outside: float | None = None
    "Value to set outside the ellipsoid, ``None`` for no change."
    inside: float | None = None
    "Value to set inside the ellipsoid, ``None`` for no change."
    radius: basic.Vector3D | float | None = None
    "Radius of the sphere or radii of the ellipsoid, ``None`` for half the size of the array."
    center: basic.Vector3D | None = None
    "Center of the ellipsoid, ``None`` for the center of the array."
    exponent: basic.Vector3D | float = 2
    "Exponent for the norm, usually 2 for a sphere or ellipsoid."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(
        self, array: np.ndarray[Any, Any], sim: pigreads.schema.Simulation
    ) -> np.ndarray[Any, Any]:
        """
        Modify the array to set values inside or outside a sphere or ellipsoid.

        The array is modified in place to set the values inside or outside the
        sphere or ellipsoid to the given values.

        :param array: Array to modify.
        :param sim: Simulation object with the grid information,
                    see :py:class:`pigreads.schema.Simulation`.
        :return: Modified array.
        """

        assert array.ndim == 3

        deltas: list[float] = [sim.dz, sim.dy, sim.dx]
        shape: list[float] = list(array.shape)

        radius: list[float]
        if isinstance(self.radius, basic.Vector3D):
            radius = [self.radius.z, self.radius.y, self.radius.x]
            radius = [np.inf if r <= 0 else r for r in radius]
        elif self.radius is None:
            radius = [
                dx * Nx / 2 if Nx > 1 else np.inf for dx, Nx in zip(deltas, shape)
            ]
        else:
            radius = [self.radius, self.radius, self.radius]

        center: list[float]
        if isinstance(self.center, basic.Vector3D):
            center = [self.center.z, self.center.y, self.center.x]
        else:
            assert self.center is None
            center = [dx * Nx / 2 for dx, Nx in zip(deltas, shape)]

        exponent: list[float]
        if isinstance(self.exponent, basic.Vector3D):
            exponent = [self.exponent.z, self.exponent.y, self.exponent.x]
        else:
            exponent = [self.exponent, self.exponent, self.exponent]

        mask = (
            np.sum(
                np.meshgrid(
                    *(
                        np.abs(
                            (np.array([x0]) if Nx <= 1 else dx * np.arange(Nx) - x0)
                            / Rx
                        )
                        ** ex
                        for dx, Nx, x0, Rx, ex in zip(
                            deltas, shape, center, radius, exponent
                        )
                    ),
                    indexing="ij",
                ),
                axis=0,
            )
            < 1
        )

        if self.inside is not None:
            array[mask] = self.inside

        if self.outside is not None:
            array[~mask] = self.outside

        return array


Setter = Union[SetterFile, SetterSlices, SetterSpherical]
"""
A setter is a command to set an array to a given value or to modify the array
in a specific way.

One of:

- :py:class:`SetterFile`
- :py:class:`SetterSlices`
- :py:class:`SetterSpherical`
"""


def normalise_list_of_setters(values: Any) -> Any:
    """
    Normalise a list of setters.

    Instead of the full representation::

        setters:
        - cmd: spherical
          outside: 0

    The command string can also be given as the only key of a dictionary::

        setters:
        - spherical:
            outside: 0

    Also instead of a list, a dictionary can be given with the command as key::

        setters:
          spherical:
            outside: 0

    If there is a single string given, it is interpreted as a file setter::

        setters: "file.npy"

    If a setter is given as a string::

        setters:
          file: "file.npy"

    It is converted to a dictionary::

        setters:
          file:
            file: "file.npy"

    This function is used in the schema to normalise the input
    and to allow more flexible input formats.

    :param values: Any data to try to interpret.
    :return: Normalised data.
    """

    adapter: TypeAdapter[Setter] = TypeAdapter(Setter)

    if isinstance(values, dict):
        values = [
            {"cmd": k, **({} if v is None else ({k: v} if isinstance(v, str) else v))}
            for k, v in values.items()
        ]
    elif isinstance(values, str) or isinstance(values, Path):  # noqa: SIM101  # pylint: disable=consider-merging-isinstance
        values = [SetterFile(file=Path(values))]
    elif isinstance(values, list):
        values_: list[Any] = []
        for i, _ in enumerate(values):
            obj = values[i]
            if isinstance(obj, dict):
                cmd = obj.get("cmd")
                if "cmd" in obj:
                    del obj["cmd"]
                if cmd is None and len(obj) == 1:
                    cmd, obj = next(iter(obj.items()))
                if isinstance(obj, str):
                    obj = {cmd: obj}
                obj = {"cmd": cmd, **(obj or {})}
            values_.append(obj)
        values = [adapter.validate_python(cmd) for cmd in values_]
    return values
