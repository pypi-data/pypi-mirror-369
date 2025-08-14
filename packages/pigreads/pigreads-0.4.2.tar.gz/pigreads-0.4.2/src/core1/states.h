#define GET_NPY_SHAPE(arr, i)                                                  \
  (i <= Int(arr.ndim()) ? Int(arr.shape(Int(arr.ndim()) - i)) : 1)
#define STATES_ADDRESS(s)                                                      \
  ((((s.it * s.Nz + s.iz) * s.Ny + s.iy) * s.Nx + s.ix) * s.Nv + s.iv) * s.Ns
#define STATES_FROM_NPY(type, x)                                               \
  States_from_shape(sizeof(type), GET_NPY_SHAPE(x, 5), GET_NPY_SHAPE(x, 4),    \
                    GET_NPY_SHAPE(x, 3), GET_NPY_SHAPE(x, 2),                  \
                    GET_NPY_SHAPE(x, 1));
#define STATES_DATA_SIZE(s) s.Ns *STATES_SIZE(s)
#define STATES_SHAPE(s) {s.Nt, s.Nz, s.Ny, s.Nx, s.Nv}
#define STATES_SIZE(s) s.Nt *s.Nz *s.Ny *s.Nx *s.Nv
#define STATES_UNPACK(s)                                                       \
  s.Ns, s.Nt, s.Nz, s.Ny, s.Nx, s.Nv, s.it, s.iz, s.iy, s.ix, s.iv

struct States {
  void *data;
  Size Ns;                 // byte size of one element
  Size Nt, Nz, Ny, Nx, Nv; // points per dimension
  Size it, iz, iy, ix, iv; // indices per dimension
#ifndef __OPENCL_VERSION__
  cl_mem buffer;
#endif
};

struct StatesIdx {
  Size Ns;                 // byte size of one element
  Size Nt, Nz, Ny, Nx, Nv; // points per dimension
  Size it, iz, iy, ix, iv; // indices per dimension
};

Size offset(Size i, Int o, Size N) {
  if (o == 0) {
    return i;
  }
  return (((i + N) + o) % N + N) % N;
}

struct States States_from_shape(Size Ns, Size Nt, Size Nz, Size Ny, Size Nx,
                                Size Nv) {
  struct States s = {NULL, Ns, Nt, Nz, Ny, Nx, Nv, 0, 0, 0, 0, 0};
  return s;
}

struct States States_offset(struct States s, Int ot, // codespell:ignore ot
                            Int oz, Int oy, Int ox, Int ov) {
  s.it = offset(s.it, ot, s.Nt); // codespell:ignore ot
  s.iz = offset(s.iz, oz, s.Nz);
  s.iy = offset(s.iy, oy, s.Ny);
  s.ix = offset(s.ix, ox, s.Nx);
  s.iv = offset(s.iv, ov, s.Nv);
  return s;
}

struct States States_offset_t(Int o, struct States s) {
  s.it = offset(s.it, o, s.Nt);
  return s;
}
struct States States_offset_z(Int o, struct States s) {
  s.iz = offset(s.iz, o, s.Nz);
  return s;
}
struct States States_offset_y(Int o, struct States s) {
  s.iy = offset(s.iy, o, s.Ny);
  return s;
}
struct States States_offset_x(Int o, struct States s) {
  s.ix = offset(s.ix, o, s.Nx);
  return s;
}
struct States States_offset_v(Int o, struct States s) {
  s.iv = offset(s.iv, o, s.Nv);
  return s;
}

void *States_get_pointer(struct States s) {
  return (char *)(s.data) + STATES_ADDRESS(s);
}
Int *States_get_pointer_int(struct States s) {
  return (Int *)States_get_pointer(s);
}
Real *States_get_pointer_real(struct States s) {
  return (Real *)States_get_pointer(s);
}
Int States_get_int(struct States s) { return *States_get_pointer_int(s); }
Real States_get_real(struct States s) { return *States_get_pointer_real(s); }
Int States_get_bool(struct States s) { return States_get_int(s) != 0; }

#define _t States_offset_t
#define _z States_offset_z
#define _y States_offset_y
#define _x States_offset_x
#define _v States_offset_v
#define _p States_get_pointer
#define _pi States_get_pointer_int
#define _pr States_get_pointer_real
#define _i States_get_int
#define _r States_get_real
#define _b States_get_bool

Real safe_mult(Real w, Real x) {
  // safe multiplication that checks if w is zero,
  // such that safe_mult(0., nan) returns 0.
  return (w == 0.0) ? 0.0 : w * x;
}

Real safe_divide(Real a, Real b) {
  // safe division that avoids division by zero,
  // i.e., if the denominator b is too close to zero,
  // it instead divides by a VERY_SMALL_NUMBER.
  if (fabs(b) < VERY_SMALL_NUMBER) {
    b = b < 0 ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER;
  }
  return a / b;
}

Real diffuse(struct States w, struct States u) {
  return safe_mult(_r(_v(0, w)), _r(u)) +
         safe_mult(_r(_v(1, w)), _r(_x(+1, u))) +
         safe_mult(_r(_v(2, w)), _r(_x(-1, u))) +
         safe_mult(_r(_v(3, w)), _r(_y(+1, u))) +
         safe_mult(_r(_v(4, w)), _r(_y(-1, u))) +
         safe_mult(_r(_v(5, w)), _r(_z(+1, u))) +
         safe_mult(_r(_v(6, w)), _r(_z(-1, u))) +
         safe_mult(_r(_v(7, w)), _r(_y(+1, _z(+1, u)))) +
         safe_mult(_r(_v(8, w)), _r(_y(+1, _z(-1, u)))) +
         safe_mult(_r(_v(9, w)), _r(_y(-1, _z(+1, u)))) +
         safe_mult(_r(_v(10, w)), _r(_y(-1, _z(-1, u)))) +
         safe_mult(_r(_v(11, w)), _r(_x(+1, _z(+1, u)))) +
         safe_mult(_r(_v(12, w)), _r(_x(+1, _z(-1, u)))) +
         safe_mult(_r(_v(13, w)), _r(_x(-1, _z(+1, u)))) +
         safe_mult(_r(_v(14, w)), _r(_x(-1, _z(-1, u)))) +
         safe_mult(_r(_v(15, w)), _r(_x(+1, _y(+1, u)))) +
         safe_mult(_r(_v(16, w)), _r(_x(+1, _y(-1, u)))) +
         safe_mult(_r(_v(17, w)), _r(_x(-1, _y(+1, u)))) +
         safe_mult(_r(_v(18, w)), _r(_x(-1, _y(-1, u))));
}
