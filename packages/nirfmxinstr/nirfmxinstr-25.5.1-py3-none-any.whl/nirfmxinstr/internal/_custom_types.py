"""Contains custom structures."""

import ctypes


class ComplexDouble(ctypes.Structure):
    "Internal ctypes implementation detail that corresponds to NIComplexDouble in C API." ""
    _fields_ = [("real", ctypes.c_double), ("imag", ctypes.c_double)]


class ComplexSingle(ctypes.Structure):
    "Internal ctypes implementation detail that corresponds to NIComplexSingle in C API." ""
    _fields_ = [("real", ctypes.c_float), ("imag", ctypes.c_float)]
