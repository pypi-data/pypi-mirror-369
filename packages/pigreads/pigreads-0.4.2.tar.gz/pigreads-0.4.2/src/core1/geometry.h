__kernel void calculate_weights(const Real dz, const Real dy, const Real dx,
                                __global void *mask_data,
                                struct StatesIdx mask_idx,
                                __global void *diffusivity_data,
                                struct StatesIdx diffusivity_idx,
                                __global void *weights_data,
                                struct StatesIdx weights_idx) {

  struct States mask = {mask_data, STATES_UNPACK(mask_idx)};
  struct States diffusivity = {diffusivity_data,
                               STATES_UNPACK(diffusivity_idx)};
  struct States weights = {weights_data, STATES_UNPACK(weights_idx)};

  const Size iz = get_global_id(0);
  const Size iy = get_global_id(1);
  const Size ix = get_global_id(2);

  const Real idxx = 1.0 / (dx * dx);
  const Real idyy = 1.0 / (dy * dy);
  const Real idzz = 1.0 / (dz * dz);
  const Real idxy = 0.25 / (dx * dy);
  const Real idxz = 0.25 / (dx * dz);
  const Real idyz = 0.25 / (dy * dz);

  // easier for notation, local copies of diffusion coefficients
  Real Dxx, Dyy, Dzz, Dxy, Dyz, Dxz;

  // mask:
  // v index: 1

  // diffusivity:
  // v index: xx, yy, zz, yz, xz, xy

  // weights:
  // v index: 19-point Laplacian
  // 0: central point
  // 1-6: main axes +x, -x +y, -y, z+,-z
  // 7-10: yz plane ++,+-,-+,--
  // 11-14: xz plane ++,+-,-+,--
  // 15-18: xy plane ++,+-,-+,--

  if (ix < weights.Nx && iy < weights.Ny && iz < weights.Nz) {
    struct States m = States_offset(mask, 0, iz, iy, ix, 0);
    struct States w = States_offset(weights, 0, iz, iy, ix, 0);
    struct States D = States_offset(diffusivity, 0, iz, iy, ix, 0);

    for (Size iv = 0; iv < weights.Nv; iv++) {
      *_pr(_v(iv, w)) = 0.;
    }

    if (_b(m)) {

      // 1. current Jx at ix+1/2
      if (_b(_x(+1, m))) {
        Dxx = 0.5 * (_r(_v(0, _x(+1, D))) + _r(_v(0, D))) * idxx;
        Dxy = 0.5 * (_r(_v(5, _x(+1, D))) + _r(_v(5, D))) * idxy;
        Dxz = 0.5 * (_r(_v(4, _x(+1, D))) + _r(_v(4, D))) * idxz;

        // terms Dxx
        *_pr(_v(0, w)) -= Dxx;
        *_pr(_v(1, w)) += Dxx;

        // terms Dxy
        *_pr(_v(0, w)) += Dxy * (_b(_y(-1, m)) - _b(_y(+1, m)));
        *_pr(_v(1, w)) += Dxy * (_b(_y(-1, _x(+1, m))) - _b(_y(+1, _x(+1, m))));
        if (_b(_y(+1, _x(+1, m)))) {
          *_pr(_v(15, w)) += Dxy;
        }
        if (_b(_y(-1, _x(+1, m)))) {
          *_pr(_v(16, w)) -= Dxy;
        }
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dxy;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dxy;
        }

        // terms Dxz
        *_pr(_v(0, w)) += Dxz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        *_pr(_v(1, w)) += Dxz * (_b(_z(-1, _x(+1, m))) - _b(_z(+1, _x(+1, m))));
        if (_b(_z(+1, _x(+1, m)))) {
          *_pr(_v(11, w)) += Dxz;
        }
        if (_b(_z(-1, _x(+1, m)))) {
          *_pr(_v(12, w)) -= Dxz;
        }
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dxz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dxz;
        }
      }

      // 2. current Jx at ix-1/2
      if (_b(_x(-1, m))) {
        Dxx = -0.5 * (_r(_v(0, _x(-1, D))) + _r(_v(0, D))) * idxx;
        Dxy = -0.5 * (_r(_v(5, _x(-1, D))) + _r(_v(5, D))) * idxy;
        Dxz = -0.5 * (_r(_v(4, _x(-1, D))) + _r(_v(4, D))) * idxz;

        // terms Dxx
        *_pr(_v(2, w)) -= Dxx;
        *_pr(_v(0, w)) += Dxx;

        // terms Dxy
        *_pr(_v(2, w)) += Dxy * (_b(_y(-1, _x(-1, m))) - _b(_y(+1, _x(-1, m))));
        *_pr(_v(0, w)) += Dxy * (_b(_y(-1, m)) - _b(_y(+1, m)));
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dxy;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dxy;
        }
        if (_b(_y(+1, _x(-1, m)))) {
          *_pr(_v(17, w)) += Dxy;
        }
        if (_b(_y(-1, _x(-1, m)))) {
          *_pr(_v(18, w)) -= Dxy;
        }

        // terms Dxz
        *_pr(_v(2, w)) += Dxz * (_b(_z(-1, _x(-1, m))) - _b(_z(+1, _x(-1, m))));
        *_pr(_v(0, w)) += Dxz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dxz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dxz;
        }
        if (_b(_z(+1, _x(-1, m)))) {
          *_pr(_v(13, w)) += Dxz;
        }
        if (_b(_z(-1, _x(-1, m)))) {
          *_pr(_v(14, w)) -= Dxz;
        }
      }

      // 3. current Jy at iy+1/2
      if (_b(_y(+1, m))) {
        Dyy = 0.5 * (_r(_v(1, _y(+1, D))) + _r(_v(1, D))) * idyy;
        Dxy = 0.5 * (_r(_v(5, _y(+1, D))) + _r(_v(5, D))) * idxy;
        Dyz = 0.5 * (_r(_v(3, _y(+1, D))) + _r(_v(3, D))) * idyz;

        // terms Dyy
        *_pr(_v(0, w)) -= Dyy;
        *_pr(_v(3, w)) += Dyy;

        // terms Dyx
        *_pr(_v(0, w)) += Dxy * (_b(_x(-1, m)) - _b(_x(+1, m)));
        *_pr(_v(3, w)) += Dxy * (_b(_y(+1, _x(-1, m))) - _b(_y(+1, _x(+1, m))));
        if (_b(_y(+1, _x(+1, m)))) {
          *_pr(_v(15, w)) += Dxy;
        }
        if (_b(_y(+1, _x(-1, m)))) {
          *_pr(_v(17, w)) -= Dxy;
        }
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxy;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxy;
        }

        // terms Dyz
        *_pr(_v(0, w)) += Dyz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        *_pr(_v(3, w)) += Dyz * (_b(_z(-1, _y(+1, m))) - _b(_z(+1, _y(+1, m))));
        if (_b(_z(+1, _y(+1, m)))) {
          *_pr(_v(7, w)) += Dyz;
        }
        if (_b(_z(-1, _y(+1, m)))) {
          *_pr(_v(8, w)) -= Dyz;
        }
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dyz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dyz;
        }
      }

      // 4. current Jy at iy-1/2
      if (_b(_y(-1, m))) {
        Dyy = -0.5 * (_r(_v(1, _y(-1, D))) + _r(_v(1, D))) * idyy;
        Dxy = -0.5 * (_r(_v(5, _y(-1, D))) + _r(_v(5, D))) * idxy;
        Dyz = -0.5 * (_r(_v(3, _y(-1, D))) + _r(_v(3, D))) * idyz;

        // terms Dyy
        *_pr(_v(4, w)) -= Dyy;
        *_pr(_v(0, w)) += Dyy;

        // terms Dyx
        *_pr(_v(4, w)) += Dxy * (_b(_y(-1, _x(-1, m))) - _b(_y(-1, _x(+1, m))));
        *_pr(_v(0, w)) += Dxy * (_b(_x(-1, m)) - _b(_x(+1, m)));
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxy;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxy;
        }
        if (_b(_y(-1, _x(+1, m)))) {
          *_pr(_v(16, w)) += Dxy;
        }
        if (_b(_y(-1, _x(-1, m)))) {
          *_pr(_v(18, w)) -= Dxy;
        }

        // terms Dyz
        *_pr(_v(4, w)) += Dyz * (_b(_z(-1, _y(-1, m))) - _b(_z(+1, _y(-1, m))));
        *_pr(_v(0, w)) += Dyz * (_b(_z(-1, m)) - _b(_z(+1, m)));
        if (_b(_z(+1, m))) {
          *_pr(_v(5, w)) += Dyz;
        }
        if (_b(_z(-1, m))) {
          *_pr(_v(6, w)) -= Dyz;
        }
        if (_b(_z(+1, _y(-1, m)))) {
          *_pr(_v(9, w)) += Dyz;
        }
        if (_b(_z(-1, _y(-1, m)))) {
          *_pr(_v(10, w)) -= Dyz;
        }
      }

      // 5. current Jz at iz+1/2
      if (_b(_z(+1, m))) {
        Dzz = 0.5 * (_r(_v(2, _z(+1, D))) + _r(_v(2, D))) * idzz;
        Dxz = 0.5 * (_r(_v(4, _z(+1, D))) + _r(_v(4, D))) * idxz;
        Dyz = 0.5 * (_r(_v(3, _z(+1, D))) + _r(_v(3, D))) * idyz;

        // terms Dzz
        *_pr(_v(0, w)) -= Dzz;
        *_pr(_v(5, w)) += Dzz;

        // terms Dzy
        *_pr(_v(0, w)) += Dyz * (_b(_y(-1, m)) - _b(_y(+1, m)));
        *_pr(_v(5, w)) += Dyz * (_b(_z(+1, _y(-1, m))) - _b(_z(+1, _y(+1, m))));
        if (_b(_z(+1, _y(+1, m)))) {
          *_pr(_v(7, w)) += Dyz;
        }
        if (_b(_z(+1, _y(-1, m)))) {
          *_pr(_v(9, w)) -= Dyz;
        }
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dyz;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dyz;
        }

        // terms Dzx
        *_pr(_v(0, w)) += Dxz * (_b(_x(-1, m)) - _b(_x(+1, m)));
        *_pr(_v(5, w)) += Dxz * (_b(_z(+1, _x(-1, m))) - _b(_z(+1, _x(+1, m))));
        if (_b(_z(+1, _x(+1, m)))) {
          *_pr(_v(11, w)) += Dxz;
        }
        if (_b(_z(+1, _x(-1, m)))) {
          *_pr(_v(13, w)) -= Dxz;
        }
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxz;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxz;
        }
      }

      // 6. current Jz at iz-1/2
      if (_b(_z(-1, m))) {
        Dzz = -0.5 * (_r(_v(2, _z(-1, D))) + _r(_v(2, D))) * idzz;
        Dxz = -0.5 * (_r(_v(4, _z(-1, D))) + _r(_v(4, D))) * idxz;
        Dyz = -0.5 * (_r(_v(3, _z(-1, D))) + _r(_v(3, D))) * idyz;

        // terms Dzz
        *_pr(_v(6, w)) -= Dzz;
        *_pr(_v(0, w)) += Dzz;

        // terms Dzy
        *_pr(_v(6, w)) += Dyz * (_b(_z(-1, _y(-1, m))) - _b(_z(-1, _y(+1, m))));
        *_pr(_v(0, w)) += Dyz * (_b(_y(-1, m)) - _b(_y(+1, m)));
        if (_b(_y(+1, m))) {
          *_pr(_v(3, w)) += Dyz;
        }
        if (_b(_y(-1, m))) {
          *_pr(_v(4, w)) -= Dyz;
        }
        if (_b(_z(-1, _y(+1, m)))) {
          *_pr(_v(8, w)) += Dyz;
        }
        if (_b(_z(-1, _y(-1, m)))) {
          *_pr(_v(10, w)) -= Dyz;
        }

        // terms Dzx
        *_pr(_v(6, w)) += Dxz * (_b(_z(-1, _x(-1, m))) - _b(_z(-1, _x(+1, m))));
        *_pr(_v(0, w)) += Dxz * (_b(_x(-1, m)) - _b(_x(+1, m)));
        if (_b(_x(+1, m))) {
          *_pr(_v(1, w)) += Dxz;
        }
        if (_b(_x(-1, m))) {
          *_pr(_v(2, w)) -= Dxz;
        }
        if (_b(_z(-1, _x(+1, m)))) {
          *_pr(_v(12, w)) += Dxz;
        }
        if (_b(_z(-1, _x(-1, m)))) {
          *_pr(_v(14, w)) -= Dxz;
        }
      }
    }
  }
}

__kernel void add_stimulus(const Real amplitude, __global void *shape_data,
                           struct StatesIdx shape_idx,
                           __global void *states_data,
                           struct StatesIdx states_idx) {

  struct States shape = {shape_data, STATES_UNPACK(shape_idx)};
  struct States states = {states_data, STATES_UNPACK(states_idx)};

  const Size iz = get_global_id(0);
  const Size iy = get_global_id(1);
  const Size ix = get_global_id(2);

  if (ix < states.Nx && iy < states.Ny && iz < states.Nz) {
    const Real current = amplitude * _r(States_offset(shape, 0, iz, iy, ix, 0));
    if (fabs(current) > VERY_SMALL_NUMBER) {
      *_pr(States_offset(states, 0, iz, iy, ix, 0)) += current;
    }
  }
}

__kernel void set_outside(const Real value, __global void *mask_data,
                          struct StatesIdx mask_idx, __global void *states_data,
                          struct StatesIdx states_idx) {

  struct States mask = {mask_data, STATES_UNPACK(mask_idx)};
  struct States states = {states_data, STATES_UNPACK(states_idx)};

  const Size iz = get_global_id(0);
  const Size iy = get_global_id(1);
  const Size ix = get_global_id(2);

  if (ix < states.Nx && iy < states.Ny && iz < states.Nz) {
    if (!_b(States_offset(mask, 0, iz, iy, ix, 0))) {
      Real *u = _pr(States_offset(states, 0, iz, iy, ix, 0));
      for (Size iv = 0; iv < states.Nv; iv++) {
        u[iv] = value;
      }
    }
  }
}
