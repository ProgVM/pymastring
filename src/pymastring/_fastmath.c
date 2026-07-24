#define PY_SSIZE_T_CLEAN
#include <Python.h>

static inline Py_UCS4 wrap_code(long code) {
    long m = code % 1114112;
    if (m < 0) {
        m += 1114112;
    }
    return (Py_UCS4)m;
}

static inline Py_UCS4 fast_pow_c(Py_UCS4 base, long exp) {
    if (exp < 0) return 0;
    unsigned long long res = 1;
    unsigned long long b = base % 1114112;
    while (exp > 0) {
        if (exp % 2 == 1) {
            res = (res * b) % 1114112;
        }
        b = (b * b) % 1114112;
        exp /= 2;
    }
    return (Py_UCS4)res;
}

/* 1. Fast C-level XOR between two strings */
static PyObject* fast_xor(PyObject* self, PyObject* args) {
    PyObject *str1, *str2;
    if (!PyArg_ParseTuple(args, "OO", &str1, &str2)) return NULL;
    if (!PyUnicode_Check(str1) || !PyUnicode_Check(str2)) {
        PyErr_SetString(PyExc_TypeError, "Expected string arguments");
        return NULL;
    }

    Py_ssize_t len1 = PyUnicode_GET_LENGTH(str1);
    Py_ssize_t len2 = PyUnicode_GET_LENGTH(str2);
    Py_ssize_t max_len = len1 > len2 ? len1 : len2;

    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(max_len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < max_len; i++) {
        Py_UCS4 c1 = (i < len1) ? PyUnicode_READ_CHAR(str1, i) : 0;
        Py_UCS4 c2 = (i < len2) ? PyUnicode_READ_CHAR(str2, i) : 0;
        buf[i] = wrap_code((long)(c1 ^ c2));
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, max_len);
    PyMem_Free(buf);
    return result;
}

/* 2. Fast C-level Bitwise AND between two strings */
static PyObject* fast_and(PyObject* self, PyObject* args) {
    PyObject *str1, *str2;
    if (!PyArg_ParseTuple(args, "OO", &str1, &str2)) return NULL;
    if (!PyUnicode_Check(str1) || !PyUnicode_Check(str2)) {
        PyErr_SetString(PyExc_TypeError, "Expected string arguments");
        return NULL;
    }

    Py_ssize_t len1 = PyUnicode_GET_LENGTH(str1);
    Py_ssize_t len2 = PyUnicode_GET_LENGTH(str2);
    Py_ssize_t max_len = len1 > len2 ? len1 : len2;

    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(max_len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < max_len; i++) {
        Py_UCS4 c1 = (i < len1) ? PyUnicode_READ_CHAR(str1, i) : 0;
        Py_UCS4 c2 = (i < len2) ? PyUnicode_READ_CHAR(str2, i) : 0;
        buf[i] = wrap_code((long)(c1 & c2));
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, max_len);
    PyMem_Free(buf);
    return result;
}

/* 3. Fast C-level Bitwise OR between two strings */
static PyObject* fast_or(PyObject* self, PyObject* args) {
    PyObject *str1, *str2;
    if (!PyArg_ParseTuple(args, "OO", &str1, &str2)) return NULL;
    if (!PyUnicode_Check(str1) || !PyUnicode_Check(str2)) {
        PyErr_SetString(PyExc_TypeError, "Expected string arguments");
        return NULL;
    }

    Py_ssize_t len1 = PyUnicode_GET_LENGTH(str1);
    Py_ssize_t len2 = PyUnicode_GET_LENGTH(str2);
    Py_ssize_t max_len = len1 > len2 ? len1 : len2;

    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(max_len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < max_len; i++) {
        Py_UCS4 c1 = (i < len1) ? PyUnicode_READ_CHAR(str1, i) : 0;
        Py_UCS4 c2 = (i < len2) ? PyUnicode_READ_CHAR(str2, i) : 0;
        buf[i] = wrap_code((long)(c1 | c2));
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, max_len);
    PyMem_Free(buf);
    return result;
}

/* 4. Fast C-level Bitwise NOT (invert) */
static PyObject* fast_invert(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    if (!PyArg_ParseTuple(args, "O", &str_obj)) return NULL;
    if (!PyUnicode_Check(str_obj)) {
        PyErr_SetString(PyExc_TypeError, "Expected string argument");
        return NULL;
    }

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)(~c));
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 5. Fast C-level Scalar Addition */
static PyObject* fast_add_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    long shift;
    if (!PyArg_ParseTuple(args, "Ol", &str_obj, &shift)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)c + shift);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 6. Fast C-level Scalar Subtraction */
static PyObject* fast_sub_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    long shift;
    if (!PyArg_ParseTuple(args, "Ol", &str_obj, &shift)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)c - shift);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 7. Fast C-level Reflected Subtraction (value - char) */
static PyObject* fast_rsub_scalar(PyObject* self, PyObject* args) {
    long val;
    PyObject *str_obj;
    if (!PyArg_ParseTuple(args, "lO", &val, &str_obj)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code(val - (long)c);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 8. Fast C-level Scalar Float Multiplication */
static PyObject* fast_mul_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    double factor;
    if (!PyArg_ParseTuple(args, "Od", &str_obj, &factor)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)((double)c * factor));
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 9. Fast C-level Scalar True Division */
static PyObject* fast_truediv_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    double divisor;
    if (!PyArg_ParseTuple(args, "Od", &str_obj, &divisor)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;
    if (divisor == 0.0) {
        PyErr_SetString(PyExc_ZeroDivisionError, "string division by zero");
        return NULL;
    }

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)((double)c / divisor));
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 10. Fast C-level Scalar Floor Division */
static PyObject* fast_floordiv_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    long divisor;
    if (!PyArg_ParseTuple(args, "Ol", &str_obj, &divisor)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;
    if (divisor == 0) {
        PyErr_SetString(PyExc_ZeroDivisionError, "string integer division by zero");
        return NULL;
    }

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)c / divisor);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 11. Fast C-level Modulo */
static PyObject* fast_mod_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    long mod_val;
    if (!PyArg_ParseTuple(args, "Ol", &str_obj, &mod_val)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;
    if (mod_val == 0) {
        PyErr_SetString(PyExc_ZeroDivisionError, "string modulo by zero");
        return NULL;
    }

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = wrap_code((long)c % mod_val);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 12. Fast C-level Power Exponentiation */
static PyObject* fast_pow_scalar(PyObject* self, PyObject* args) {
    PyObject *str_obj;
    long power;
    if (!PyArg_ParseTuple(args, "Ol", &str_obj, &power)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = fast_pow_c(c, power);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 13. Fast C-level Reflected Power Exponentiation */
static PyObject* fast_rpow_scalar(PyObject* self, PyObject* args) {
    long base;
    PyObject *str_obj;
    if (!PyArg_ParseTuple(args, "lO", &base, &str_obj)) return NULL;
    if (!PyUnicode_Check(str_obj)) return NULL;

    Py_ssize_t len = PyUnicode_GET_LENGTH(str_obj);
    Py_UCS4 *buf = (Py_UCS4 *)PyMem_Malloc(len * sizeof(Py_UCS4));
    if (!buf) return PyErr_NoMemory();

    for (Py_ssize_t i = 0; i < len; i++) {
        Py_UCS4 c = PyUnicode_READ_CHAR(str_obj, i);
        buf[i] = fast_pow_c((Py_UCS4)base, (long)c);
    }

    PyObject *result = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, buf, len);
    PyMem_Free(buf);
    return result;
}

/* 14. Fast C-level Matrix Multiplication Dot Product (@) */
static PyObject* fast_matmul(PyObject* self, PyObject* args) {
    PyObject *str1, *str2;
    if (!PyArg_ParseTuple(args, "OO", &str1, &str2)) return NULL;
    if (!PyUnicode_Check(str1) || !PyUnicode_Check(str2)) return NULL;

    Py_ssize_t len1 = PyUnicode_GET_LENGTH(str1);
    Py_ssize_t len2 = PyUnicode_GET_LENGTH(str2);
    Py_ssize_t max_len = len1 > len2 ? len1 : len2;

    unsigned long long total = 0;
    for (Py_ssize_t i = 0; i < max_len; i++) {
        Py_UCS4 c1 = (i < len1) ? PyUnicode_READ_CHAR(str1, i) : 0;
        Py_UCS4 c2 = (i < len2) ? PyUnicode_READ_CHAR(str2, i) : 0;
        total += (unsigned long long)c1 * (unsigned long long)c2;
    }

    return PyLong_FromUnsignedLongLong(total);
}

/* Method registrations */
static PyMethodDef FastMathMethods[] = {
    {"fast_xor", fast_xor, METH_VARARGS, "Fast C-level string XOR"},
    {"fast_and", fast_and, METH_VARARGS, "Fast C-level string AND"},
    {"fast_or", fast_or, METH_VARARGS, "Fast C-level string OR"},
    {"fast_invert", fast_invert, METH_VARARGS, "Fast C-level string bitwise NOT"},
    {"fast_add_scalar", fast_add_scalar, METH_VARARGS, "Fast C-level scalar addition"},
    {"fast_sub_scalar", fast_sub_scalar, METH_VARARGS, "Fast C-level scalar subtraction"},
    {"fast_rsub_scalar", fast_rsub_scalar, METH_VARARGS, "Fast C-level reflected scalar subtraction"},
    {"fast_mul_scalar", fast_mul_scalar, METH_VARARGS, "Fast C-level scalar multiplication"},
    {"fast_truediv_scalar", fast_truediv_scalar, METH_VARARGS, "Fast C-level scalar division"},
    {"fast_floordiv_scalar", fast_floordiv_scalar, METH_VARARGS, "Fast C-level scalar floor division"},
    {"fast_mod_scalar", fast_mod_scalar, METH_VARARGS, "Fast C-level scalar modulo"},
    {"fast_pow_scalar", fast_pow_scalar, METH_VARARGS, "Fast C-level scalar power"},
    {"fast_rpow_scalar", fast_rpow_scalar, METH_VARARGS, "Fast C-level reflected scalar power"},
    {"fast_matmul", fast_matmul, METH_VARARGS, "Fast C-level matrix dot product"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastmathmodule = {
    PyModuleDef_HEAD_INIT,
    "_fastmath",
    "Comprehensive C acceleration module for pymastring",
    -1,
    FastMathMethods
};

PyMODINIT_FUNC PyInit__fastmath(void) {
    return PyModule_Create(&fastmathmodule);
}
