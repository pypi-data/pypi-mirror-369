#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif
#if PY_MAJOR_VERSION > 2
#  if PY_MINOR_VERSION < 11
    int PyFloat_Pack4(double x, unsigned char *p, int le);
    int PyFloat_Pack8(double x, unsigned char *p, int le);
    double PyFloat_Unpack4(const unsigned char *p, int le);
    double PyFloat_Unpack8(const unsigned char *p, int le);
#  endif
#endif
#if defined(__cplusplus)
}
#endif

