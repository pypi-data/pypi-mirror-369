#include <Python.h>

#if defined(__cplusplus)
extern "C" {
#endif

#if PY_MAJOR_VERSION > 2
#  if PY_MINOR_VERSION < 11
#   include <floatobject.h>
    int PyFloat_Pack4(double x, unsigned char *p, int le) {
        return _PyFloat_Pack4(x, p, le);
    };
    int PyFloat_Pack8(double x, unsigned char *p, int le) {
        return _PyFloat_Pack8(x, p, le);
    };
    double PyFloat_Unpack4(const unsigned char *p, int le) {
        return _PyFloat_Unpack4(p, le);
    };
    double PyFloat_Unpack8(const unsigned char *p, int le) {
        return _PyFloat_Unpack8(p, le);
    };
    static PyObject * FP4(PyObject *self, PyObject *args) {
        double x;
        unsigned char p;
        int le;
        if (!PyArg_ParseTuple(args, "dyi", &x, &p, &le))
            return NULL;
        return PyLong_FromLong(PyFloat_Pack4(x, (unsigned char)p, le));
    };
    static PyObject * FP8(PyObject *self, PyObject *args) {
        double x;
        unsigned char p;
        int le;
        if (!PyArg_ParseTuple(args, "dyi", &x, &p, &le))
            return NULL;
        return PyLong_FromLong(PyFloat_Pack8(x, (unsigned char)p, le));
    };
    static PyObject * FU4(PyObject *self, PyObject *args) {
        unsigned char p;
        int le;
        if (!PyArg_ParseTuple(args, "yi", &p, &le))
            return NULL;
        return PyFloat_FromDouble(PyFloat_Unpack4((const unsigned char)p, le));
    };
    static PyObject * FU8(PyObject *self, PyObject *args) {
        unsigned char p;
        int le;
        if (!PyArg_ParseTuple(args, "yi", &p, &le))
            return NULL;
        return PyFloat_FromDouble(PyFloat_Unpack8((const unsigned char)p, le));
    };
    static PyMethodDef PyFloatImportsMethods[] = {
        {"PyFloat_Pack4", FP4, METH_VARARGS, ""},
        {"PyFloat_Pack8", FP8, METH_VARARGS, ""},
        {"PyFloat_Unpack4", FU4, METH_VARARGS, ""},
        {"PyFloat_Unpack8", FU8, METH_VARARGS, ""},
        {NULL, NULL, 0, NULL}
    };

    static struct PyModuleDef PyFloatImports = {
        PyModuleDef_HEAD_INIT,
        "PyFloatImports",
        NULL,
        -1,
        PyFloatImportsMethods
    };

    PyMODINIT_FUNC PyInit_PyFloatImports(void) {
        return PyModule_Create(&PyFloatImports);
    }
#  endif
#endif
#if defined(__cplusplus)
}
#endif
