#include <Python.h>

// Example: int add(int a, int b)
static PyObject* cpp_add(PyObject*, PyObject* args) {
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b))
        return nullptr;
    return PyLong_FromLong(a + b);
}

static PyMethodDef ModuleMethods[] = {
    {"add", cpp_add, METH_VARARGS, "Add two integers."},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "reason.cpp",
    nullptr,
    -1,
    ModuleMethods
};

PyMODINIT_FUNC PyInit_cpp(void) {
    return PyModule_Create(&moduledef);
}