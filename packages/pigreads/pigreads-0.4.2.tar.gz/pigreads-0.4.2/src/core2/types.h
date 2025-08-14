#ifdef __OPENCL_VERSION__
#define Size ulong
#define Int int
#else
#define Size uint64_t
#define Int int32_t
#include <cfloat>
#endif

#define Real double
#define Models1 Models2
#define MODULE core2
#define VERY_SMALL_NUMBER 1e-20

#define MODULE_DOC                                                             \
  "Double-precision implementation\n-------------------------------\n.. "      \
  "currentmodule:: pigreads\n"
