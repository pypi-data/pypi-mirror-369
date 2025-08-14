struct Models1 {
  Size Nv = 0;
  std::vector<std::string> model_keys;
  std::vector<Size> model_ids;
  std::vector<Size> model_offsets;
  std::vector<Real> model_params;
  std::unique_ptr<OpenCLWrapper> cl;

  Models1() {
    cl = std::make_unique<OpenCLWrapper>();
    compile(CORE_KERNELS);
    model_offsets.push_back(0);
  }

  Size size() const { return model_ids.size(); }
  Size get_number_definitions() const { return model_keys.size(); }

  std::string get_key(Size imodel) const {
    return model_keys.at(model_ids.at(imodel));
  }

  Size get_parameter_offset(Size imodel, Size iparam) const {
    Size offset = model_offsets.at(imodel) + iparam;
    ASSERT(offset < model_offsets.at(imodel + 1));
    return offset;
  }

  Real get_parameter(Size imodel, Size iparam) const {
    return model_params.at(get_parameter_offset(imodel, iparam));
  }

  void set_parameter(Size imodel, Size iparam, Real value) {
    model_params.at(get_parameter_offset(imodel, iparam)) = value;
  }

  void buffer() {
    const Size model_count = size();
    model_ids_buffer =
        cl->bufferR(sizeof(Size) * model_count, model_ids.data());
    model_offsets_buffer =
        cl->bufferR(sizeof(Size) * model_count, model_offsets.data());
    model_params_buffer =
        cl->bufferR(sizeof(Real) * model_params.size(), model_params.data());
  }

  void free() {
    if (model_ids_buffer) {
      cl->free(model_ids_buffer);
    }
    if (model_offsets_buffer) {
      cl->free(model_offsets_buffer);
    }
    if (model_params_buffer) {
      cl->free(model_params_buffer);
    }
  }

  std::set<Size> get_set_of_model_ids() const {
    return {model_ids.data(), model_ids.data() + size()};
  }

  std::vector<Size> get_block_size() const { return cl->getBlockSize(); }

  void set_block_size(const std::vector<Size> &blockSize) {
    cl->setBlockSize(blockSize);
  }

  void compile(std::string code) {
    std::stringstream stream;
    stream << KERNEL_HEADER << "\n\n" << code;
    cl->compile(stream.str().c_str());
  }

  void step(Size model_id, struct States inhom, struct States weights,
            struct States states_old, struct States states_new,
            const Real dt) const {
    const std::vector<Size> work_size = {states_old.Nz, states_old.Ny,
                                         states_old.Nx};
    std::ostringstream kernel_name;
    kernel_name << "Model_" << model_keys[model_id] << "_kernel";
    cl->execute(kernel_name.str().c_str(), work_size, size(), model_ids_buffer,
                model_offsets_buffer, model_params_buffer, inhom.buffer,
                StatesIdx{STATES_UNPACK(inhom)}, weights.buffer,
                StatesIdx{STATES_UNPACK(weights)}, states_old.buffer,
                StatesIdx{STATES_UNPACK(states_old)}, states_new.buffer,
                StatesIdx{STATES_UNPACK(states_new)}, dt);
  }

  void add(std::string key, std::string code, Size Nv,
           py::array_t<Real> params);

  py::array_t<Real> weights(const Real dz, const Real dy, const Real dx,
                            const py::array_t<Int> py_mask,
                            const py::array_t<Real> py_diffusivity);

  py::array_t<Real>
  run(const py::array_t<Int> py_inhom, const py::array_t<Real> py_weights,
      const py::array_t<Real> py_states, const py::array_t<Real> py_stim_signal,
      const py::array_t<Real> py_stim_shape, const Size Nt, const Real dt);

private:
  cl_mem model_ids_buffer = NULL;
  cl_mem model_offsets_buffer = NULL;
  cl_mem model_params_buffer = NULL;
};
