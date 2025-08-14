"""
Models
------
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelEntry(BaseModel):
    """
    A model entry chooses a model by its key and which parameters to use.

    :see: :py:class:`pigreads.Models` and :py:class:`ModelDefinition`
    """

    key: str
    "The key of the model."
    parameters: MutableMapping[str, float] = Field(default_factory=dict)
    "The parameters of the model."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."

    @model_validator(mode="before")
    @classmethod
    def normalise(cls, values: Any) -> Any:
        """
        Normalise the model entry.

        If the entry is a string, it is converted to a dictionary with an empty
        parameter set. If the entry is a dictionary with a single key, the key
        is used as the model key.

        :param values: Any data to try to interpret.
        :return: Normalised data.
        """

        assert isinstance(values, dict)

        key = values.get("key")
        if "key" in values:
            del values["key"]

        parameters = values.get("parameters", {})
        if "parameters" in values:
            del values["parameters"]

        if key is None:
            assert len(values) == 1

            key, parameters = next(iter(values.items()))
            return {"key": key, "parameters": parameters or {}}

        parameters = {**parameters, **values}

        return {"key": key, "parameters": parameters or {}}


class ModelDefinition(BaseModel):
    """
    Definition of a so-called model, i.e., the reaction-term.

    Note: Additional fields are allowed stored in :py:attr:`meta`.

    :see: :py:class:`pigreads.Models` and :py:class:`ModelEntry`
    """

    name: str
    "Human readable name of the model, usually the authors and the year."
    description: str
    "A simple description of the model, what it was designed for, and its unique features."
    dois: list[str] = Field(default_factory=list)
    "List of digital object identifiers in URL form, i.e., starting with ``https://doi.org/10``."
    variables: dict[str, float]
    "Model variable names and their resting/initial values."
    diffusivity: dict[str, float]
    "Dictionary that maps the names of variables to diffuse to their diffusivity."
    parameters: dict[str, float]
    "Model parameter names and their default values."
    code: str
    "Source code of the forward Euler step in OpenCL."
    code_float: str | None = None
    "Source code for single precision floating point numbers, if none, use the generic source code."
    code_double: str | None = None
    "Source code for double precision floating point numbers, if none, use the generic source code."
    model_config = ConfigDict(extra="forbid")
    "Configuration for :py:class:`pydantic.BaseModel`."
    meta: dict[str, Any] = Field(default_factory=dict)
    "Additional fields as a dictionary."

    @model_validator(mode="before")
    @classmethod
    def normalise(cls, values: Any) -> dict[str, Any]:
        """
        Store additional fields as metadata.

        :see: :py:attr:`meta`
        """
        known_fields = set(cls.model_fields.keys())
        known = {k: v for k, v in values.items() if k in known_fields}
        unknown = {k: v for k, v in values.items() if k not in known_fields}
        known["meta"] = {**known.get("meta", {}), **unknown}
        return known

    @property
    def all_parameters(self) -> dict[str, float]:
        "Dictionary of parameters including the diffusivities."
        return {
            **{
                "diffusivity_" + varname: value
                for varname, value in self.diffusivity.items()
            },
            **self.parameters,
        }

    def __call__(self, **parameters: float) -> dict[str, float]:
        """
        Merge diffusivities, default parameters, and given parameters.

        :param parameters: Additional parameters.
        :return: Merged parameter dictionary.
        """
        return {**self.all_parameters, **parameters}

    def get_code(self, double_precision: bool = False) -> str:
        """
        Get the correct source code for a given floating point precision.

        :param double_precision: If ``True``, use double precision for calculations.
        :return: Source code of the forward Euler step in OpenCL.
        """
        if double_precision:
            if self.code_double is None:
                return self.code
            return self.code_double
        if self.code_float is None:
            return self.code
        return self.code_float
