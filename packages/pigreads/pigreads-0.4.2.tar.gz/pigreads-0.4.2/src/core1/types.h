#ifdef __OPENCL_VERSION__
#define Size ulong
#define Int int
#else
#define Size uint64_t
#define Int int32_t
#include <cfloat>
#endif

#define Real float
#define MODULE core1
#define VERY_SMALL_NUMBER 1e-10f

#ifdef __OPENCL_VERSION__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wmacro-redefined"
#define exp(x) native_exp((Real)(x))
#define log(x) native_log((Real)(x))
#define sqrt(x) native_sqrt((Real)(x))
inline Real pow_(Real base, Real exp) { return pow(base, exp); }
#define pow(x, y) pow_((Real)(x), (Real)(y))
#pragma clang diagnostic pop
#endif

#define MODULE_DOC                                                             \
  "Single-precision implementation\n-------------------------------\n.. "      \
  "currentmodule:: pigreads\n"
