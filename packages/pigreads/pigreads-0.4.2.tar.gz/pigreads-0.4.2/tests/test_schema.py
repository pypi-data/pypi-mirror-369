from __future__ import annotations

from copy import deepcopy
from tempfile import NamedTemporaryFile
from typing import Any

import numpy as np
import pydantic
import pytest
import yaml

from pigreads.schema import Simulation
from pigreads.schema.model import ModelDefinition

data_minimal = yaml.safe_load("""
pigreads: 1
Nfr: 1
Nt: 1
Nz: 1
Ny: 1
Nx: 1
dt: 0.1
dz: 0.1
dy: 0.1
dx: 0.1
diffusivity: 0.1
models: aliev1996simple
""")


def modify_sim(key: str, option: Any) -> Simulation:
    data = deepcopy(data_minimal)
    data[key] = option
    return Simulation(**data)


def check_all_sims(key: str, options: list[Any]) -> list[Simulation]:
    sims = [modify_sim(key, o) for o in options]
    for sim in sims[1:]:
        assert sims[0].model_dump_json() == sim.model_dump_json()
    return sims


class Test_Misc:
    def test_minimal(self):
        Simulation(**data_minimal)

    def test_double(self):
        modify_sim("double_precision", True)

    def test_states(self):
        sim = Simulation(**data_minimal)
        inhom = sim.prepare_inhom()
        models = sim.prepare_models()
        varidx = sim.varidx(models)
        sim.prepare_states(models, varidx, inhom)

    def test_run(self):
        sim = modify_sim("init", {"u": 0.3})
        sim.Nfr = 2
        sim.Nt = 1
        states = sim.run()
        assert np.allclose(states[-1].squeeze(), [0.32519996, 0.000408])

    def test_run_memmap(self):
        with NamedTemporaryFile(suffix=".npy") as f:
            np.save(f, np.ones(shape=(0,)))
            f.seek(0)
            Simulation(**data_minimal).run(path=f.name)

    def test_space(self):
        sim = Simulation(**data_minimal)
        sim.Nz, sim.Ny, sim.Nx = 2, 3, 4
        sim.dz, sim.dy, sim.dx = 0.1, 0.2, 0.3
        z, y, x = sim.prepare_space()
        assert x.shape == (sim.Nz, sim.Ny, sim.Nx)
        assert y.shape == (sim.Nz, sim.Ny, sim.Nx)
        assert z.shape == (sim.Nz, sim.Ny, sim.Nx)
        assert sim.dz * 0.9 < z[1, 0, 0] - z[0, 0, 0] < sim.dz * 1.1
        assert sim.dy * 0.9 < y[0, 1, 0] - y[0, 0, 0] < sim.dy * 1.1
        assert sim.dx * 0.9 < x[0, 0, 1] - x[0, 0, 0] < sim.dx * 1.1


class Test_ModelEntry:
    def test_string(self):
        modify_sim("models", "aliev1996simple").prepare_models()

    def test_dict_none(self):
        modify_sim("models", {"aliev1996simple": None}).prepare_models()

    def test_dict_empty(self):
        modify_sim("models", {"aliev1996simple": {}}).prepare_models()

    def test_dict_values(self):
        modify_sim("models", {"aliev1996simple": {"k": 3}}).prepare_models()

    def test_dicts(self):
        modify_sim(
            "models",
            yaml.safe_load("""
            aliev1996simple:
                k: 3
            marcotte2017dynamical:
        """),
        ).prepare_models()

    def test_list(self):
        modify_sim(
            "models",
            yaml.safe_load("""
          - aliev1996simple:
          - aliev1996simple:
                k: 3
        """),
        ).prepare_models()

    def test_list_key(self):
        modify_sim(
            "models",
            yaml.safe_load("""
          -
            key: aliev1996simple
          -
            key: aliev1996simple
            k: 3
        """),
        ).prepare_models()

    def test_duplicate(self):
        modify_sim(
            "models",
            yaml.safe_load("""
          - aliev1996simple:
              k: 3
            aliev1996simple:
              k: 4
        """),
        ).prepare_models()

    def test_none(self):
        with pytest.raises(pydantic.ValidationError):
            modify_sim("models", None)

    def test_float(self):
        with pytest.raises(pydantic.ValidationError):
            modify_sim("models", 1.0)

    def test_check_empty(self):
        options: list[Any] = [
            "aliev1996simple",
            {"aliev1996simple": None},
            {"aliev1996simple": {}},
            {"key": "aliev1996simple"},
            {"key": "aliev1996simple", "parameters": {}},
        ]
        options = [*options, *([o] for o in options)]
        for sim in check_all_sims("models", options):
            sim.prepare_models()

    def test_check_one(self):
        options: list[Any] = [
            {"aliev1996simple": {"k": 3}},
            {"key": "aliev1996simple", "k": 3},
            {"key": "aliev1996simple", "parameters": {"k": 3}},
        ]
        options = [*options, *([o] for o in options)]
        for sim in check_all_sims("models", options):
            sim.prepare_models()

    def test_check_two(self):
        options: list[Any] = [
            {"marcotte2017dynamical": None, "aliev1996simple": {"k": 3}},
            [{"marcotte2017dynamical": None}, {"aliev1996simple": {"k": 3}}],
            [{"key": "marcotte2017dynamical"}, {"key": "aliev1996simple", "k": 3}],
            [
                {"key": "marcotte2017dynamical"},
                {"key": "aliev1996simple", "parameters": {"k": 3}},
            ],
        ]
        for sim in check_all_sims("models", options):
            sim.prepare_models()


class Test_ModelDefinition:
    def test_normalise(self):
        model = ModelDefinition(
            **yaml.safe_load("""
                name: Name
                description: Description
                dois: []
                variables: {u: 1.0}
                diffusivity: {u: 1.0}
                parameters: {}
                code: "*_new_u = u + dt * _diffuse_u;"
                test: 123
        """)
        )
        assert model.meta["test"] == 123

    def test_code_all(self):
        model = ModelDefinition(
            name="Name",
            description="Description",
            dois=[],
            variables={"u": 1.0},
            diffusivity={"u": 1.0},
            parameters={},
            code="fallback",
            code_float="float",
            code_double="double",
        )
        assert model.code == "fallback"
        assert model.code_float == "float"
        assert model.code_double == "double"
        assert model.get_code() == "float"
        assert model.get_code(True) == "double"

    def test_code_float(self):
        model = ModelDefinition(
            name="Name",
            description="Description",
            dois=[],
            variables={"u": 1.0},
            diffusivity={"u": 1.0},
            parameters={},
            code="fallback",
            code_float="float",
        )
        assert model.code == "fallback"
        assert model.code_float == "float"
        assert model.code_double is None
        assert model.get_code() == "float"
        assert model.get_code(True) == "fallback"

    def test_code_double(self):
        model = ModelDefinition(
            name="Name",
            description="Description",
            dois=[],
            variables={"u": 1.0},
            diffusivity={"u": 1.0},
            parameters={},
            code="fallback",
            code_double="double",
        )
        assert model.code == "fallback"
        assert model.code_float is None
        assert model.code_double == "double"
        assert model.get_code() == "fallback"
        assert model.get_code(True) == "double"


class Test_Diffusivity:
    def test_float(self):
        options: list[Any] = [
            0.03,
            {"Df": 0.03},
        ]
        for sim in check_all_sims("diffusivity", options):
            sim.diffusivity()

    def test_file(self):
        with NamedTemporaryFile(suffix=".npy") as f:
            np.save(f, np.ones(shape=(1, 1, 1, 6)))
            f.seek(0)
            options: list[Any] = [
                f.name,
                {"file": f.name},
            ]
            for sim in check_all_sims("diffusivity", options):
                sim.diffusivity()

    def test_params(self):
        modify_sim(
            "diffusivity",
            {"f": [1, 2, 3], "n": [4, 5, 6], "Df": 1, "Ds": 0.1, "Dn": 0.01},
        ).diffusivity()

    def test_both(self):
        with pytest.raises(pydantic.ValidationError):
            modify_sim("diffusivity", {"Df": 1, "file": "diffusivity.npy"})

    def test_f_int(self):
        with pytest.raises(pydantic.ValidationError):
            modify_sim("diffusivity", {"Df": 1, "f": 2})

    def test_g(self):
        with pytest.raises(pydantic.ValidationError):
            modify_sim("diffusivity", {"Df": 1, "g": [1, 1, 1]})


class Test_Inhom:
    def test_file(self):
        with NamedTemporaryFile(suffix=".npy") as f:
            np.save(f, np.ones(shape=(1, 1, 1)))
            f.seek(0)
            options: list[Any] = [
                f.name,
                {"file": f.name},
                [{"file": f.name}],
                [{"cmd": "file", "file": f.name}],
            ]
            for sim in check_all_sims("inhom", options):
                sim.prepare_inhom()

    def test_spherical(self):
        center = {"x": 1, "y": 2, "z": 3}
        options: list[Any] = [
            {"spherical": {"outside": 0, "radius": 1, "center": center}},
            [
                {
                    "cmd": "spherical",
                    "outside": 0,
                    "radius": 1,
                    "center": center,
                    "exponent": 2,
                }
            ],
            [
                {
                    "cmd": "spherical",
                    "outside": 0,
                    "inside": None,
                    "radius": 1,
                    "center": center,
                    "exponent": 2,
                }
            ],
        ]
        for sim in check_all_sims("inhom", options):
            sim.prepare_inhom()

    def test_ellipse(self):
        modify_sim(
            "inhom",
            {
                "spherical": {
                    "inside": 1,
                    "radius": {"x": 1, "y": 2, "z": 3},
                    "center": {"x": 4, "y": 5, "z": 6},
                    "exponent": {"x": 7, "y": 8, "z": 9},
                }
            },
        ).prepare_inhom()

    def test_slice(self):
        for literal in ["slice", "slices"]:
            options: list[Any] = [
                {literal: {"axis": -1, "value": 0}},
                [{literal: {"axis": -1, "value": 0}}],
                [{"cmd": literal, "axis": -1, "value": 0}],
            ]
            for sim in check_all_sims("inhom", options):
                sim.prepare_inhom()

    def test_slices(self):
        options: list[Any] = [
            {"slices": {"axis": -1, "value": 0}},
            [{"slices": {"axis": -1, "value": 0}}],
            [{"cmd": "slices", "axis": -1, "value": 0}],
        ]
        for sim in check_all_sims("inhom", options):
            sim.prepare_inhom()

    def test_multiple(self):
        with NamedTemporaryFile(suffix=".npy") as f:
            np.save(f, np.ones(shape=(1, 1, 1)))
            f.seek(0)
            options: list[Any] = [
                {
                    "file": f.name,
                    "spherical": {"outside": 0},
                    "slice": {"axis": -1, "value": 0, "start": 50},
                    "slices": {"axis": -2, "value": 0, "start": 20},
                },
                [
                    {"file": f.name},
                    {"spherical": {"outside": 0}},
                    {"slice": {"axis": -1, "value": 0, "start": 50}},
                    {"slices": {"axis": -2, "value": 0, "start": 20}},
                ],
                [
                    {"cmd": "file", "file": f.name},
                    {"cmd": "spherical", "outside": 0},
                    {"cmd": "slice", "axis": -1, "value": 0, "start": 50},
                    {"cmd": "slices", "axis": -2, "value": 0, "start": 20},
                ],
            ]
            for sim in check_all_sims("inhom", options):
                sim.prepare_inhom()


class Test_Init:
    def test_main(self):
        options: list[Any] = [
            {
                "u": {"file": "u.npy"},
                "v": {
                    "spherical": {"inside": 1},
                    "slice": {"axis": -1, "value": 0, "start": 50},
                },
            },
            {
                "u": [{"cmd": "file", "file": "u.npy"}],
                "v": [
                    {"cmd": "spherical", "inside": 1},
                    {"cmd": "slice", "axis": -1, "value": 0, "start": 50},
                ],
            },
        ]
        check_all_sims("init", options)

    def test_float(self):
        modify_sim("init", {"u": 2, "v": 3}).run()

    def test_file_var(self):
        with NamedTemporaryFile(suffix=".npy") as f:
            np.save(f, np.ones(shape=(1, 1, 1)))
            f.seek(0)
            modify_sim("init", {"u": f.name}).run()

    def test_file(self):
        with NamedTemporaryFile(suffix=".npy") as f:
            np.save(f, np.ones(shape=(1, 1, 1, 2)))
            f.seek(0)
            modify_sim("init", f.name).run()


class Test_Stimulus:
    def test_main(self):
        sim = modify_sim(
            "stim",
            yaml.safe_load("""
            -
                shape:
                    spherical:
                        inside: 1
                        center:
                            x: 5
                            y: 7
                        radius: 1
                signal:
                -
                    start: 0 # ms
                    duration: 50 # ms
                    variables:
                        u: 1
            -
                shape:
                    spherical:
                        inside: 1
                        radius: 2
                        center:
                            x: 2
                            y: 12
                signal:
                -
                    start: 170 # ms
                    duration: 50 # ms
                    variables:
                        u: 1
        """),
        )
        sim.prepare_stim(sim.varidx(sim.prepare_models()))
