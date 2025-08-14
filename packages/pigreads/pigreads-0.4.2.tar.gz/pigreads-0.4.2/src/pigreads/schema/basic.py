"""
Schema for some basic data types
--------------------------------
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Vector3D(BaseModel):
    """
    Vector in three dimensions in space.
    """

    x: float = 0
    "Value in x direction."
    y: float = 0
    "Value in y direction."
    z: float = 0
    "Value in z direction."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."


class Slice(BaseModel):
    """
    Slice of an array.

    :see: :py:class:`slice`
    """

    axis: int = -1
    "Axis of the slice."
    start: int | None = None
    "Start of the slice."
    end: int | None = None
    "End of the slice."
    step: int | None = None
    "Step of the slice."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(self) -> slice:
        """
        Return a slice object.

        :return: Slice object.
        :see: :py:class:`slice`
        """
        return slice(self.start, self.end, self.step)
