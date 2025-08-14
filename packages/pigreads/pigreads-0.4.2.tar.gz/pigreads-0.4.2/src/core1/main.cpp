#include <cmath>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <set>
#include <stdint.h>
#include <string>

#define ASSERT(code)                                                           \
  if (not(code))                                                               \
    throw std::runtime_error(std::string(__FILE__) + ":" +                     \
                             std::to_string(__LINE__) + ":ASSERT(" +           \
                             std::string(#code) + ")");
namespace py = pybind11;

// 1. type definitions
#include "types.h"

// 2. interface to OpenCL
#include "opencl.hpp"

// 3. matrix data structure
#include "states.h"

// 4. kernel source code
#include "kernels.h"

// 5. model management
#include "models.hpp"

void Models1::add(std::string key, std::string code, Size Nv_,
                  py::array_t<Real> py_params) {
  const Size Np = py_params.size();
  const Real *params = (Real *)py_params.request().ptr;

  const auto it = std::find(model_keys.begin(), model_keys.end(), key);
  Size id;
  if (it == model_keys.end()) {
    compile(code);
    model_keys.push_back(key);
    id = model_keys.size() - 1;
  } else {
    id = std::distance(model_keys.begin(), it);
  }
  model_ids.push_back(id);

  model_offsets.push_back(model_offsets.back() + Np);
  for (Size ip = 0; ip < Np; ip++) {
    model_params.push_back(params[ip]);
  }
  if (Nv_ > Nv) {
    Nv = Nv_;
  }
}

py::array_t<Real> Models1::weights(const Real dz, const Real dy, const Real dx,
                                   const py::array_t<Int> py_mask,
                                   const py::array_t<Real> py_diffusivity) {

  ASSERT(cl);

  struct States mask = STATES_FROM_NPY(Int, py_mask);
  ASSERT(mask.Nt == 1);
  ASSERT(mask.Nv == 1);
  mask.data = py_mask.request().ptr;
  mask.buffer = cl->bufferR(STATES_DATA_SIZE(mask), mask.data);

  struct States diffusivity = STATES_FROM_NPY(Real, py_diffusivity);
  ASSERT(diffusivity.Nt == 1);
  ASSERT(diffusivity.Nv == 6);
  diffusivity.data = py_diffusivity.request().ptr;
  diffusivity.buffer =
      cl->bufferR(STATES_DATA_SIZE(diffusivity), diffusivity.data);

  struct States weights{NULL, sizeof(Real), 1, mask.Nz, mask.Ny, mask.Nx, 19};
  std::vector<Real> weights_vec(STATES_DATA_SIZE(weights), 0);
  weights.data = weights_vec.data();
  weights.buffer = cl->bufferW(STATES_DATA_SIZE(weights));

  cl->execute("calculate_weights", {weights.Nz, weights.Ny, weights.Nx}, dz, dy,
              dx, mask.buffer, StatesIdx{STATES_UNPACK(mask)},
              diffusivity.buffer, StatesIdx{STATES_UNPACK(diffusivity)},
              weights.buffer, StatesIdx{STATES_UNPACK(weights)});

  cl->copyBufferData(STATES_DATA_SIZE(weights), weights.buffer, weights.data);

  cl->free(mask.buffer);
  cl->free(diffusivity.buffer);
  cl->free(weights.buffer);

  return py::array_t<Real>(STATES_SHAPE(weights), (Real *)weights.data);
}

py::array_t<Real> Models1::run(const py::array_t<Int> py_inhom,
                               const py::array_t<Real> py_weights,
                               const py::array_t<Real> py_states,
                               const py::array_t<Real> py_stim_signal,
                               const py::array_t<Real> py_stim_shape,
                               const Size Nt, const Real dt) {

  ASSERT(this);
  ASSERT(cl);
  ASSERT(dt > 0);
  ASSERT(Nt > 0);
  buffer();

  struct States s = STATES_FROM_NPY(Real, py_states);
  s.data = py_states.request().ptr;
  ASSERT(s.Nt == 1);
  ASSERT(s.Nv == Nv);

  struct States states{NULL, s.Ns, 2, s.Nz, s.Ny, s.Nx, s.Nv};
  std::vector<Real> states_vec(STATES_DATA_SIZE(states), 0);
  states.data = states_vec.data();
  for (Size i = 0; i < STATES_SIZE(states); i++) {
    ((Real *)states.data)[i] = 0;
  }
  memcpy(states.data, s.data, STATES_DATA_SIZE(states) / s.Nt);
  states.buffer = cl->buffer(STATES_DATA_SIZE(states), states.data,
                             CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR);

  struct States weights = STATES_FROM_NPY(Real, py_weights);
  ASSERT(weights.Nt == 1);
  ASSERT(weights.Nv == 19);
  weights.data = py_weights.request().ptr;
  weights.buffer = cl->bufferR(STATES_DATA_SIZE(weights), weights.data);

  struct States inhom = STATES_FROM_NPY(Int, py_inhom);
  ASSERT(inhom.Nt == 1);
  ASSERT(inhom.Nv == 1);
  inhom.data = py_inhom.request().ptr;
  inhom.buffer = cl->bufferR(STATES_DATA_SIZE(inhom), inhom.data);

  struct States stim_signal = STATES_FROM_NPY(Real, py_stim_signal);
  struct States stim_shape = STATES_FROM_NPY(Real, py_stim_shape);

  if (STATES_SIZE(stim_signal) > 0 && STATES_SIZE(stim_shape) > 0) {
    ASSERT(stim_signal.Ny == 1);
    ASSERT(stim_signal.Nx == 1);

    ASSERT(stim_shape.Nt == stim_signal.Nz);
    ASSERT(stim_shape.Nv == 1);
  }

  stim_signal.data = py_stim_signal.request().ptr;
  stim_shape.data = py_stim_shape.request().ptr;

  size_t size_stim_shape = STATES_DATA_SIZE(stim_shape);
  if (size_stim_shape == 0) {
    size_stim_shape = 1;
  }
  stim_shape.buffer = cl->bufferR(size_stim_shape, stim_shape.data);

  const std::vector<Size> work_size = {states.Nz, states.Ny, states.Nx};
  const std::set<Size> set_of_model_ids = get_set_of_model_ids();

  cl->execute("set_outside", work_size, Real(0.0), inhom.buffer,
              StatesIdx{STATES_UNPACK(inhom)}, states.buffer,
              StatesIdx{STATES_UNPACK(states)});

  for (Size it = 0; it < Nt; it++) {
    for (Size mid : set_of_model_ids) {
      step(mid, inhom, weights, _t(it, states), _t(it + 1, states), dt);
    }

    if (STATES_SIZE(stim_signal) > 0 && STATES_SIZE(stim_shape) > 0) {
      for (Size is = 0; is < stim_signal.Nz; is++) {
        struct States is_amplitude = _z(is, _t(it, stim_signal));
        struct States is_shape = _t(is, stim_shape);
        for (Size iv = 0; iv < Nv; iv++) {
          const Real stim_amplitude = _r(_v(iv, is_amplitude));
          if (fabs(stim_amplitude) > VERY_SMALL_NUMBER) {
            struct States stim_states = _v(iv, _t(it + 1, states));
            cl->execute("add_stimulus", work_size, dt * stim_amplitude,
                        is_shape.buffer, StatesIdx{STATES_UNPACK(is_shape)},
                        stim_states.buffer,
                        StatesIdx{STATES_UNPACK(stim_states)});
          }
        }
      }
    }
  }

  for (Size it = 0; it < states.Nt; it++) {
    cl->execute("set_outside", work_size, Real(NAN), inhom.buffer,
                StatesIdx{STATES_UNPACK(inhom)}, states.buffer,
                StatesIdx{STATES_UNPACK(_t(it, states))});
  }

  cl->copyBufferData(STATES_DATA_SIZE(states), states.buffer, states.data);

  cl->free(weights.buffer);
  cl->free(inhom.buffer);
  cl->free(stim_shape.buffer);
  cl->free(states.buffer);
  free();

  return py::array_t<Real>(py_states.request().shape, _pr(_t(Nt, states)));
}

#define _BIND_CLASS(module, class) py::class_<class>(m, #class)
#define BIND_CLASS(module, class) _BIND_CLASS(module, class)

PYBIND11_MODULE(MODULE, m) {
  m.doc() = MODULE_DOC;
  BIND_CLASS(m, Models1)
      .def(py::init<>())
      .def_readonly("Nv", &Models1::Nv,
                    "Maximum number of state variables in the models.")
      .def("__len__", &Models1::size, "Number of model entries.")
      .def("get_number_definitions", &Models1::get_number_definitions,
           "Get the number of model definitions.")
      .def("get_key", &Models1::get_key,
           "Get the key of the model with the given index.")
      .def("get_parameter", &Models1::get_parameter,
           "Get the parameter with the given indices.")
      .def("set_parameter", &Models1::set_parameter,
           "Set the parameter with the given indices.")
      .def("get_block_size", &Models1::get_block_size,
           "Get the local work size for running OpenCL kernels.")
      .def("set_block_size", &Models1::set_block_size,
           "Set the local work size for running OpenCL kernels.")
      .def("add", &Models1::add,
           "Add a model by compiling it and storing its parameters.")
      .def("weights", &Models1::weights, "Calculate the weights for diffusion.")
      .def("run", &Models1::run, "Run a simulation.");
}
