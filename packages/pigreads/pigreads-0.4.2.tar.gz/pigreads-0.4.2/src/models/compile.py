#!/bin/env python3
"""
Export Myokit MMT files to Pigreads code
----------------------------------------
"""

from __future__ import annotations

import sys
import warnings
from copy import deepcopy
from textwrap import dedent, indent
from typing import Any

import myokit as mk  # type: ignore[import-not-found]
import yaml
from myokit.formats.cellml import (  # type: ignore[import-not-found]
    CellMLImporter,
)
from myokit.formats.opencl import (  # type: ignore[import-not-found]
    OpenCLExpressionWriter,
)

INDENT: str = "    "


def str_presenter(dumper, data):
    """
    A YAML string presenter that uses block style for multiline strings.
    """
    data = data.strip()
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


class PigreadsMyokitWriter:
    """
    This class implements the conversion of a Myokit model to Pigreads
    compatible code.

    :param model: The Myokit model to convert.
    :param meta: A dictionary with metadata to include in the generated code.

    :var model: The Myokit model to convert.
    :vartype model: myokit.Model
    :var exwr1: The expression writer for single floating point precision
    :vartype exwr1: myokit.formats.opencl.OpenCLExpressionWriter
    :var exwr2: The expression writer for double floating point precision
    :vartype exwr2: myokit.formats.opencl.OpenCLExpressionWriter
    :var states: The list of states in the model.
    :vartype states: list[mk.State]
    :var meta: A dictionary with metadata to include in the generated code.
    :vartype meta: dict[str, Any]
    :var double_precision: If ``True``, use double precision for calculations.
    :vartype double_precision: bool
    """

    def __init__(self, model: mk.Model, meta: dict[str, Any]):
        self.model = model
        self.exwr1 = OpenCLExpressionWriter(
            precision=mk.SINGLE_PRECISION, native_math=True
        )
        self.exwr2 = OpenCLExpressionWriter(
            precision=mk.DOUBLE_PRECISION, native_math=False
        )
        self.exwr1.set_lhs_function(self.lhs_format)
        self.exwr2.set_lhs_function(self.lhs_format)
        self.states = list(model.states())
        self.meta = meta
        self.generate_variable_abbreviations()

    @property
    def diffusivities(self) -> dict[str, float]:
        """
        The diffusivities of the model as defined in the metadata.
        """
        d = self.meta.get("diffusivity", {})
        assert isinstance(d, dict)
        return d

    def get_ivar(self, varname: str) -> int:
        """
        Get the index of a state variable by its name.

        :param varname: The name of the state variable.
        :return: The index of the state variable.
        """
        return next(
            i
            for i, state in enumerate(self.states)
            if str(self.lhs_format(state)) == varname
        )

    @staticmethod
    def nodots(s: Any) -> str:
        """
        Convert an object to string and replace dots by underscores.

        :param s: any object to represent as a string.
        """
        return str(s).replace(".", "_")

    def lhs_format(self, x: mk.LhsExpression):
        """
        Format a left-hand side expression.

        :param x: The left-hand side expression to format.
        :return: The formatted left-hand side expression.
        """
        assert not isinstance(x, mk.Derivative), "Can not handle derivatives here."
        if isinstance(x, mk.Name):
            return self.lhs_format(x.var())
        s = self.nodots(x)
        return self.variable_abbreviations.get(s, s)

    @staticmethod
    def rush_larsen(
        v: mk.Variable,
        tau: mk.Variable,
        inf: mk.Variable,
        dt: str = "dt",
    ) -> mk.Expression:
        """
        The Rush-Larsen update for a state variable v.

        :param v: The state variable to update.
        :param tau: The time constant.
        :param inf: The steady state value.
        :param dt: Name of the time step.
        :return: The Rush-Larsen update for the state variable.
        """
        return mk.Plus(
            inf,
            mk.Multiply(
                mk.Minus(v, inf),
                mk.Exp(mk.PrefixMinus(mk.Divide(mk.Name(dt), tau))),
            ),
        )

    @staticmethod
    def safe_divide(a: mk.Expression, b: mk.Expression) -> mk.Expression:
        """
        Division that avoids division by a value close to zero.

        :param a: Enumerator.
        :param b: Denominator.
        :return: Expression of the safe division.
        """
        eps = mk.Name("VERY_SMALL_NUMBER")
        return mk.Divide(
            a,
            mk.If(
                i=mk.Less(mk.Abs(b), eps),
                t=mk.If(
                    i=mk.Less(b, mk.Number(0)),
                    t=mk.PrefixMinus(eps),
                    e=eps,
                ),
                e=b,
            ),
        )

    @classmethod
    def offset_in_division(cls, ex: mk.Expression) -> mk.Expression:
        """
        Avoid division by zero by adding a small offset in specific cases.

        :param ex: An expression to find and replace quotients in.
        :return: The updated expression.
        """

        subst: dict[Any, Any] = {}
        for quotient in ex.walk([mk.Divide]):
            numerator, denominator = quotient
            if not denominator.is_constant():
                subst[quotient] = cls.safe_divide(
                    cls.offset_in_division(numerator),
                    cls.offset_in_division(denominator),
                )
        return ex.clone(subst)

    def state_equation(self, q: mk.Equation, exwr: OpenCLExpressionWriter):
        """
        Format a state equation.

        :param q: The state equation to format.
        :return: The formatted state equation.
        """
        w = q.lhs.walk()
        next(w)
        v = next(w)
        vin = str(self.lhs_format(v))

        # if possible, use Rush-Larsen step
        if isinstance(q.rhs, mk.Divide):
            difference, tau = q.rhs
            if isinstance(difference, mk.Minus):
                left, right = difference
                if left == v:
                    return f"*_new_{vin} = -({exwr.ex(self.rush_larsen(v=v, tau=tau, inf=right))});"
                if right == v:
                    return f"*_new_{vin} = {exwr.ex(self.rush_larsen(v=v, tau=tau, inf=left))};"

        # else use forward Euler
        rhs: mk.Expression = q.rhs.clone()
        rhs = self.offset_in_division(rhs)
        update: str = str(exwr.ex(rhs))
        if vin in self.diffusivities:
            update += f" + _diffuse_{vin}"
        return f"*_new_{vin} = {vin} + dt*({update});"

    def generate_variable_abbreviations(self) -> None:
        """
        Create a dictionary abbreviating long variable names if this
        is possible unambiguously. Short variable names are the last part of the
        long variable name after a dot.
        """
        variables = dict(
            zip(self.model.states(), self.model.initial_values(as_floats=True))
        )
        variables_long = {self.nodots(v): f for v, f in variables.items()}
        variables_short = {}
        for variable, value in variables.items():
            short_varname = str(variable).rsplit(".", maxsplit=1)[-1]
            if short_varname not in variables_short:
                variables_short[short_varname] = value
            else:
                variables_short = variables_long
                break
        self.variables = variables_short
        self.variable_abbreviations = dict(
            zip(variables_long.keys(), variables_short.keys())
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model to a dictionary. This is the main entry point for the
        conversion.

        :return: The model as a dictionary.
        """
        parameters = {
            self.lhs_format(q.lhs): float(q.rhs)
            for block in self.model.solvable_order().values()
            for q in block
            if q.rhs.is_constant()
        }

        d: dict[str, Any] = {
            "name": rf"{self.model.name()} (exported from Myokit)",
            "description": str(self.model.meta.get("desc", "")),
            "dois": [],
            "variables": self.variables,
            "parameters": parameters,
            **self.meta,
        }

        keys = ["code", "code_double"]
        for key, exwr in zip(keys, [self.exwr1, self.exwr2]):
            step = []
            for blockname, block in self.model.solvable_order().items():
                block_ = [eq for eq in block if not eq.rhs.is_constant()]
                if len(block_) < 1:
                    continue
                step.append("")
                step.append(f"// {blockname}")
                for q in block_:
                    if q.lhs.is_derivative():
                        step.append(self.state_equation(q, exwr))
                    else:
                        step.append(
                            "const Real "
                            + exwr.eq(
                                mk.Equation(q.lhs, self.offset_in_division(q.rhs))
                            )
                            + ";"
                        )
            d[key] = "\n".join(step).strip()

        if d[keys[0]] == d[keys[1]]:
            del d[keys[1]]

        return d

    def __str__(self) -> str:
        """
        Convert the model to a string. This is the another main entry point for the
        conversion.

        :return: The model as a string.
        """
        return yaml.safe_dump(
            self.to_dict(), sort_keys=False, indent=2, allow_unicode=True
        )


def main() -> None:
    from pathlib import Path

    cellml = CellMLImporter()

    path_models = Path(sys.argv[1])
    path_docs = Path(sys.argv[2])
    path_module = Path(sys.argv[3])

    paths_by_stem: dict[str, dict[str, str]] = {}
    for file in sorted(path_models.iterdir()):
        suffix = file.suffix[1:].lower()

        if suffix not in ["yaml", "mmt", "cellml"]:
            continue

        if file.stem not in paths_by_stem:
            paths_by_stem[file.stem] = {}

        paths_by_stem[file.stem][suffix] = str(file)

    models = {}
    for key, paths in paths_by_stem.items():
        model = {}
        meta = {}

        assert "yaml" in paths, "Must have yaml file."
        with Path(paths["yaml"]).open() as f:
            meta = yaml.safe_load(f.read())

        if "cellml" in paths:
            assert "mmt" not in paths, "Can only have mmt or cellml, not both."
            try:
                model = PigreadsMyokitWriter(
                    cellml.model(paths["cellml"]), meta
                ).to_dict()
            except Exception as e:
                warnings.warn(f"{paths['cellml']}: {e}", stacklevel=2)
                continue

        elif "mmt" in paths:
            try:
                model = PigreadsMyokitWriter(
                    mk.load_model(paths["mmt"]), meta
                ).to_dict()
            except Exception as e:
                warnings.warn(f"{paths['mmt']}: {e}", stacklevel=2)
                continue

        model.update(meta)
        models[key] = model

    path_docs.mkdir(exist_ok=True)
    for file in path_docs.iterdir():
        if file.is_file():
            file.unlink()

    warning: str = dedent("""
        AUTOMATICALLY GENERATED FILE!
        Edit ``src/models/compile.py`` or the model definitions in
        ``src/models/`` instead, run ``make`` in the main directory to compile.
    """).strip()

    with (path_docs / "index.rst").open("w") as f:

        def p(*args: Any) -> None:
            return print(*args, file=f)

        for line in warning.splitlines():
            p(f".. {line}")
        p()

        p(
            dedent(r'''
            Models
            ======

            A so-called model defines the reaction term of the reaction
            diffusion equation. While Pigreads comes with a variety of
            pre-defined models, it is also easily possible to define a
            model.

            Defining a model
            ----------------


            A model can be defined by adding it to the dictionary of available
            models::

                import pigreads as pig
                from pigreads.schema.model import ModelDefinition

                pig.Models.available["fitzhugh1961impulses"] = ModelDefinition(
                    name="FitzHugh 1961 & Nagumo 1962",
                    description="A 2D simplification of the Hodgkin-Huxley model.",
                    dois=[
                        "https://doi.org/10.1016/S0006-3495(61)86902-6",
                        "https://doi.org/10.1109/JRPROC.1962.288235",
                    ],
                    variables={"u": 1.2, "v": -0.625},
                    diffusivity={"u": 1.0},
                    parameters={"a": 0.7, "b": 0.8, "c": 3.0, "z": 0.0},
                    code="""
                        *_new_u = u + dt * (v + u - u*u*u/3 + z + _diffuse_u);
                        *_new_v = v + dt * (-(u - a + b*v)/c);
                    """,
                )


            The definition must adhere to the schema in :py:class:`pigreads.schema.model.ModelDefinition`.

            Pre-defined models
            ------------------

            .. toctree::
                :maxdepth: 1
                :hidden:
            ''').strip()
        )
        p()
        for key in models:
            p(f"    {key}")
        p()
        p(
            dedent(r"""
            .. csv-table::
                :header: Name, Key, Variables, Parameters
            """).strip()
        )
        p()
        for key, model in models.items():
            p(
                f'    ":doc:`{model["name"]} <{key}>`", "``{key}``", {len(model["variables"])}, {len(model["parameters"])}'
            )

    for key, model in deepcopy(models).items():
        with (path_docs / f"{key}.rst").open("w") as f:

            def p(*args: Any) -> None:
                return print(*args, file=f)

            def code(s: str, summary: str) -> None:
                p(".. raw:: html")
                p()
                p("    <details>")
                p(f"    <summary>{summary}</summary>")
                p()
                p(".. code-block:: c")
                p()
                p(indent(s.strip(), INDENT))
                p()
                p(".. raw:: html")
                p()
                p("    </details>")

            for line in warning.splitlines():
                p(f".. {line}")
            p()

            name: str = model.pop("name")
            p(name)
            p("=" * len(name))
            p()
            p(f"**Key:** ``{key}``")
            p()
            p(model.pop("description").strip())
            p()
            dois: list[str] = model.pop("dois")
            if len(dois) > 0:
                p("References")
                p("----------")
                p()
                for i, doi in enumerate(dois):
                    p(f"{i}. {doi}")
                p()
            p("Variables")
            p("---------")
            p()
            for i, (name, value) in enumerate(model.pop("variables").items()):
                p(f"{i}. ``{name} = {value}``")
            p()
            p("Parameters")
            p("----------")
            p()
            for name, value in model.pop("diffusivity").items():
                p(f"- ``diffusivity_{name} = {value}``")
            for name, value in model.pop("parameters").items():
                p(f"- ``{name} = {value}``")
            p()
            p("Source code")
            p("-----------")
            p()
            code(model.pop("code"), "General code")
            if model.get("code_float", None) is not None:
                p()
                code(model.pop("code_float"), "Code for single precision")
            if model.get("code_double", None) is not None:
                p()
                code(model.pop("code_double"), "Code for double precision")
            if len(model) > 0:
                p()
                p("Additional metadata")
                p("-------------------")
                p()
                p(".. code-block:: yaml")
                p()
                p(
                    indent(
                        yaml.safe_dump(
                            model, sort_keys=False, indent=2, allow_unicode=True
                        ),
                        INDENT,
                    )
                )

    with path_module.open("w") as f:

        def p(*args: Any) -> None:
            return print(*args, file=f)

        for line in warning.splitlines():
            p(f"# {line}")
        p()
        p(
            dedent(f'''
            """
            Pre-defined models
            ------------------
            """

            from typing import Any

            available: dict[str, dict[str, Any]] = {models!r}
        ''').strip()
        )


if __name__ == "__main__":
    main()
