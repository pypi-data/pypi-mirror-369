"""Wrapper around driver library.
   Class will setup the correct ctypes information for every function on first call.
"""

import ctypes
import threading
from typing import Any

import nirfmxinstr.errors as errors
import nirfmxinstr.internal._custom_types as _custom_types


class Library(object):
    """Library

    Wrapper around driver library.
    Class will setup the correct ctypes information for every function on first call.
    """

    def __init__(self, ctypes_library):
        """Initialize the Library object."""
        self._func_lock = threading.Lock()
        self._library = ctypes_library
        # We cache the cfunc object from the ctypes.CDLL object
        self.RFmxInstr_GetError_cfunc = None
        self.RFmxInstr_GetErrorString_cfunc = None
        self.RFmxInstr_GetAttributeI8_cfunc = None
        self.RFmxInstr_SetAttributeI8_cfunc = None
        self.RFmxInstr_GetAttributeI8Array_cfunc = None
        self.RFmxInstr_SetAttributeI8Array_cfunc = None
        self.RFmxInstr_GetAttributeI16_cfunc = None
        self.RFmxInstr_SetAttributeI16_cfunc = None
        self.RFmxInstr_GetAttributeI32_cfunc = None
        self.RFmxInstr_SetAttributeI32_cfunc = None
        self.RFmxInstr_GetAttributeI32Array_cfunc = None
        self.RFmxInstr_SetAttributeI32Array_cfunc = None
        self.RFmxInstr_GetAttributeI64_cfunc = None
        self.RFmxInstr_SetAttributeI64_cfunc = None
        self.RFmxInstr_GetAttributeI64Array_cfunc = None
        self.RFmxInstr_SetAttributeI64Array_cfunc = None
        self.RFmxInstr_GetAttributeU8_cfunc = None
        self.RFmxInstr_SetAttributeU8_cfunc = None
        self.RFmxInstr_GetAttributeU8Array_cfunc = None
        self.RFmxInstr_SetAttributeU8Array_cfunc = None
        self.RFmxInstr_GetAttributeU16_cfunc = None
        self.RFmxInstr_SetAttributeU16_cfunc = None
        self.RFmxInstr_GetAttributeU32_cfunc = None
        self.RFmxInstr_SetAttributeU32_cfunc = None
        self.RFmxInstr_GetAttributeU32Array_cfunc = None
        self.RFmxInstr_SetAttributeU32Array_cfunc = None
        self.RFmxInstr_GetAttributeU64Array_cfunc = None
        self.RFmxInstr_SetAttributeU64Array_cfunc = None
        self.RFmxInstr_GetAttributeF32_cfunc = None
        self.RFmxInstr_SetAttributeF32_cfunc = None
        self.RFmxInstr_GetAttributeF32Array_cfunc = None
        self.RFmxInstr_SetAttributeF32Array_cfunc = None
        self.RFmxInstr_GetAttributeF64_cfunc = None
        self.RFmxInstr_SetAttributeF64_cfunc = None
        self.RFmxInstr_GetAttributeF64Array_cfunc = None
        self.RFmxInstr_SetAttributeF64Array_cfunc = None
        self.RFmxInstr_GetAttributeNIComplexSingleArray_cfunc = None
        self.RFmxInstr_SetAttributeNIComplexSingleArray_cfunc = None
        self.RFmxInstr_GetAttributeNIComplexDoubleArray_cfunc = None
        self.RFmxInstr_SetAttributeNIComplexDoubleArray_cfunc = None
        self.RFmxInstr_GetAttributeString_cfunc = None
        self.RFmxInstr_SetAttributeString_cfunc = None
        self.RFmxInstr_Initialize_cfunc = None
        self.RFmxInstr_CheckAcquisitionStatus_cfunc = None
        self.RFmxInstr_CfgExternalAttenuationTable_cfunc = None
        self.RFmxInstr_SelectActiveExternalAttenuationTable_cfunc = None
        self.RFmxInstr_DeleteExternalAttenuationTable_cfunc = None
        self.RFmxInstr_DeleteAllExternalAttenuationTables_cfunc = None
        self.RFmxInstr_EnableCalibrationPlane_cfunc = None
        self.RFmxInstr_DisableCalibrationPlane_cfunc = None
        self.RFmxInstr_CheckIfSignalConfigurationExists_cfunc = None
        self.RFmxInstr_CfgSParameterExternalAttenuationTable_cfunc = None
        self.RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile_cfunc = None
        self.RFmxInstr_CfgExternalAttenuationInterpolationNearest_cfunc = None
        self.RFmxInstr_CfgExternalAttenuationInterpolationLinear_cfunc = None
        self.RFmxInstr_CfgExternalAttenuationInterpolationSpline_cfunc = None
        self.RFmxInstr_CfgSParameterExternalAttenuationType_cfunc = None
        self.RFmxInstr_SendSoftwareEdgeStartTrigger_cfunc = None
        self.RFmxInstr_SendSoftwareEdgeAdvanceTrigger_cfunc = None
        self.RFmxInstr_CheckIfListExists_cfunc = None
        self.RFmxInstr_Close_cfunc = None
        self.RFmxInstr_CfgFrequencyReference_cfunc = None
        self.RFmxInstr_CfgMechanicalAttenuation_cfunc = None
        self.RFmxInstr_CfgRFAttenuation_cfunc = None
        self.RFmxInstr_WaitForAcquisitionComplete_cfunc = None
        self.RFmxInstr_ResetToDefault_cfunc = None
        self.RFmxInstr_ResetDriver_cfunc = None
        self.RFmxInstr_SaveAllConfigurations_cfunc = None
        self.RFmxInstr_ResetEntireSession_cfunc = None
        self.RFmxInstr_ExportSignal_cfunc = None
        self.RFmxInstr_SelfCalibrate_cfunc = None
        self.RFmxInstr_SelfCalibrateRange_cfunc = None
        self.RFmxInstr_LoadConfigurations_cfunc = None
        self.RFmxInstr_ReleaseLicense_cfunc = None
        self.RFmxInstr_IsSelfCalibrateValid_cfunc = None
        self.RFmxInstr_GetError_cfunc = None
        self.RFmxInstr_GetErrorString_cfunc = None
        self.RFmxInstr_ResetAttribute_cfunc = None
        self.RFmxInstr_CreateDefaultSignalConfiguration_cfunc = None
        self.RFmxInstr_GetSessionUniqueIdentifier_cfunc = None
        self.RFmxInstr_GetSParameterExternalAttenuationType_cfunc = None
        self.RFmxInstr_GetExternalAttenuationTableActualValue_cfunc = None
        self.RFmxInstr_GetSelfCalibrateLastTemperature_cfunc = None
        self.RFmxInstr_GetSelfCalibrateLastDateAndTime_cfunc = None
        self.RFmxInstr_GetSignalConfigurationNames_cfunc = None
        self.RFmxInstr_GetListNames_cfunc = None
        self.RFmxInstr_FetchRawIQData_cfunc = None
        self.RFmxInstr_GetAvailablePorts_cfunc = None
        self.RFmxInstr_GetAvailablePaths_cfunc = None

    def _get_library_function(self, name: str) -> Any:
        try:
            function = getattr(self._library, name)
        except AttributeError as e:
            raise errors.DriverTooOldError() from e  # type: ignore
        return function

    def RFmxInstr_GetError(self, vi, error_code, error_description_buffer_size, error_description):
        """RFmxInstr_GetError."""
        with self._func_lock:
            if self.RFmxInstr_GetError_cfunc is None:
                self.RFmxInstr_GetError_cfunc = self._get_library_function("RFmxInstr_GetError")
                self.RFmxInstr_GetError_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_GetError_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetError_cfunc(
            vi, error_code, error_description_buffer_size, error_description
        )

    def RFmxInstr_GetErrorString(
        self, vi, error_code, error_description_buffer_size, error_description
    ):
        """RFmxInstr_GetErrorString."""
        with self._func_lock:
            if self.RFmxInstr_GetErrorString_cfunc is None:
                self.RFmxInstr_GetErrorString_cfunc = self._get_library_function(
                    "RFmxInstr_GetErrorString"
                )
                self.RFmxInstr_GetErrorString_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_GetErrorString_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetErrorString_cfunc(
            vi, error_code, error_description_buffer_size, error_description
        )

    def RFmxInstr_GetAttributeI8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeI8."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI8_cfunc is None:
                self.RFmxInstr_GetAttributeI8_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI8"
                )
                self.RFmxInstr_GetAttributeI8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int8),
                ]
                self.RFmxInstr_GetAttributeI8_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeI8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeI8."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI8_cfunc is None:
                self.RFmxInstr_SetAttributeI8_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI8"
                )
                self.RFmxInstr_SetAttributeI8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int8,
                ]
                self.RFmxInstr_SetAttributeI8_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeI16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeI16."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI16_cfunc is None:
                self.RFmxInstr_GetAttributeI16_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI16"
                )
                self.RFmxInstr_GetAttributeI16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int16),
                ]
                self.RFmxInstr_GetAttributeI16_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeI16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeI16."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI16_cfunc is None:
                self.RFmxInstr_SetAttributeI16_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI16"
                )
                self.RFmxInstr_SetAttributeI16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int16,
                ]
                self.RFmxInstr_SetAttributeI16_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeI32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeI32."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI32_cfunc is None:
                self.RFmxInstr_GetAttributeI32_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI32"
                )
                self.RFmxInstr_GetAttributeI32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeI32_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeI32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeI32."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI32_cfunc is None:
                self.RFmxInstr_SetAttributeI32_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI32"
                )
                self.RFmxInstr_SetAttributeI32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int32,
                ]
                self.RFmxInstr_SetAttributeI32_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeI64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeI64."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI64_cfunc is None:
                self.RFmxInstr_GetAttributeI64_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI64"
                )
                self.RFmxInstr_GetAttributeI64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int64),
                ]
                self.RFmxInstr_GetAttributeI64_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeI64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeI64."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI64_cfunc is None:
                self.RFmxInstr_SetAttributeI64_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI64"
                )
                self.RFmxInstr_SetAttributeI64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int64,
                ]
                self.RFmxInstr_SetAttributeI64_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeU8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeU8."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeU8_cfunc is None:
                self.RFmxInstr_GetAttributeU8_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeU8"
                )
                self.RFmxInstr_GetAttributeU8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint8),
                ]
                self.RFmxInstr_GetAttributeU8_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeU8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeU8(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeU8."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeU8_cfunc is None:
                self.RFmxInstr_SetAttributeU8_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeU8"
                )
                self.RFmxInstr_SetAttributeU8_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_uint8,
                ]
                self.RFmxInstr_SetAttributeU8_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeU8_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeU16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeU16."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeU16_cfunc is None:
                self.RFmxInstr_GetAttributeU16_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeU16"
                )
                self.RFmxInstr_GetAttributeU16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint16),
                ]
                self.RFmxInstr_GetAttributeU16_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeU16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeU16(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeU16."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeU16_cfunc is None:
                self.RFmxInstr_SetAttributeU16_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeU16"
                )
                self.RFmxInstr_SetAttributeU16_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_uint16,
                ]
                self.RFmxInstr_SetAttributeU16_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeU16_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeU32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeU32."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeU32_cfunc is None:
                self.RFmxInstr_GetAttributeU32_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeU32"
                )
                self.RFmxInstr_GetAttributeU32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32),
                ]
                self.RFmxInstr_GetAttributeU32_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeU32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeU32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeU32."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeU32_cfunc is None:
                self.RFmxInstr_SetAttributeU32_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeU32"
                )
                self.RFmxInstr_SetAttributeU32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeU32_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeU32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeF32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeF32."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeF32_cfunc is None:
                self.RFmxInstr_GetAttributeF32_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeF32"
                )
                self.RFmxInstr_GetAttributeF32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                ]
                self.RFmxInstr_GetAttributeF32_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeF32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeF32(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeF32."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeF32_cfunc is None:
                self.RFmxInstr_SetAttributeF32_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeF32"
                )
                self.RFmxInstr_SetAttributeF32_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_float,
                ]
                self.RFmxInstr_SetAttributeF32_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeF32_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeF64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_GetAttributeF64."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeF64_cfunc is None:
                self.RFmxInstr_GetAttributeF64_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeF64"
                )
                self.RFmxInstr_GetAttributeF64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxInstr_GetAttributeF64_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeF64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_SetAttributeF64(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeF64."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeF64_cfunc is None:
                self.RFmxInstr_SetAttributeF64_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeF64"
                )
                self.RFmxInstr_SetAttributeF64_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_double,
                ]
                self.RFmxInstr_SetAttributeF64_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeF64_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_GetAttributeI8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeI8Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI8Array_cfunc is None:
                self.RFmxInstr_GetAttributeI8Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI8Array"
                )
                self.RFmxInstr_GetAttributeI8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int8),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeI8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeI8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeI8Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI8Array_cfunc is None:
                self.RFmxInstr_SetAttributeI8Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI8Array"
                )
                self.RFmxInstr_SetAttributeI8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int8),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeI8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeI32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeI32Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI32Array_cfunc is None:
                self.RFmxInstr_GetAttributeI32Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI32Array"
                )
                self.RFmxInstr_GetAttributeI32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeI32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeI32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeI32Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI32Array_cfunc is None:
                self.RFmxInstr_SetAttributeI32Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI32Array"
                )
                self.RFmxInstr_SetAttributeI32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeI32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeI64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeI64Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeI64Array_cfunc is None:
                self.RFmxInstr_GetAttributeI64Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeI64Array"
                )
                self.RFmxInstr_GetAttributeI64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int64),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeI64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeI64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeI64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeI64Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeI64Array_cfunc is None:
                self.RFmxInstr_SetAttributeI64Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeI64Array"
                )
                self.RFmxInstr_SetAttributeI64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int64),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeI64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeI64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeU8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeU8Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeU8Array_cfunc is None:
                self.RFmxInstr_GetAttributeU8Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeU8Array"
                )
                self.RFmxInstr_GetAttributeU8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeU8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeU8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeU8Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeU8Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeU8Array_cfunc is None:
                self.RFmxInstr_SetAttributeU8Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeU8Array"
                )
                self.RFmxInstr_SetAttributeU8Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeU8Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeU8Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeU32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeU32Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeU32Array_cfunc is None:
                self.RFmxInstr_GetAttributeU32Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeU32Array"
                )
                self.RFmxInstr_GetAttributeU32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeU32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeU32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeU32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeU32Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeU32Array_cfunc is None:
                self.RFmxInstr_SetAttributeU32Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeU32Array"
                )
                self.RFmxInstr_SetAttributeU32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeU32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeU32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeU64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeU64Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeU64Array_cfunc is None:
                self.RFmxInstr_GetAttributeU64Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeU64Array"
                )
                self.RFmxInstr_GetAttributeU64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeU64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeU64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeU64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeU64Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeU64Array_cfunc is None:
                self.RFmxInstr_SetAttributeU64Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeU64Array"
                )
                self.RFmxInstr_SetAttributeU64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeU64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeU64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeF32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeF32Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeF32Array_cfunc is None:
                self.RFmxInstr_GetAttributeF32Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeF32Array"
                )
                self.RFmxInstr_GetAttributeF32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeF32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeF32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeF32Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeF32Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeF32Array_cfunc is None:
                self.RFmxInstr_SetAttributeF32Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeF32Array"
                )
                self.RFmxInstr_SetAttributeF32Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeF32Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeF32Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeF64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeF64Array."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeF64Array_cfunc is None:
                self.RFmxInstr_GetAttributeF64Array_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeF64Array"
                )
                self.RFmxInstr_GetAttributeF64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeF64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeF64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeF64Array(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeF64Array."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeF64Array_cfunc is None:
                self.RFmxInstr_SetAttributeF64Array_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeF64Array"
                )
                self.RFmxInstr_SetAttributeF64Array_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeF64Array_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeF64Array_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeNIComplexSingleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeNIComplexSingleArray."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeNIComplexSingleArray_cfunc is None:
                self.RFmxInstr_GetAttributeNIComplexSingleArray_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeNIComplexSingleArray"
                )
                self.RFmxInstr_GetAttributeNIComplexSingleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeNIComplexSingleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeNIComplexSingleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeNIComplexSingleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeNIComplexSingleArray."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeNIComplexSingleArray_cfunc is None:
                self.RFmxInstr_SetAttributeNIComplexSingleArray_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeNIComplexSingleArray"
                )
                self.RFmxInstr_SetAttributeNIComplexSingleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_float),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeNIComplexSingleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeNIComplexSingleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeNIComplexDoubleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
    ):
        """RFmxInstr_GetAttributeNIComplexDoubleArray."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeNIComplexDoubleArray_cfunc is None:
                self.RFmxInstr_GetAttributeNIComplexDoubleArray_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeNIComplexDoubleArray"
                )
                self.RFmxInstr_GetAttributeNIComplexDoubleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetAttributeNIComplexDoubleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeNIComplexDoubleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size, actual_array_size
        )

    def RFmxInstr_SetAttributeNIComplexDoubleArray(
        self, vi, selector_string, attribute_id, attr_val, array_size
    ):
        """RFmxInstr_SetAttributeNIComplexDoubleArray."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeNIComplexDoubleArray_cfunc is None:
                self.RFmxInstr_SetAttributeNIComplexDoubleArray_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeNIComplexDoubleArray"
                )
                self.RFmxInstr_SetAttributeNIComplexDoubleArray_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_uint32,
                ]
                self.RFmxInstr_SetAttributeNIComplexDoubleArray_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeNIComplexDoubleArray_cfunc(
            vi, selector_string, attribute_id, attr_val, array_size
        )

    def RFmxInstr_GetAttributeString(self, vi, selector_string, attribute_id, array_size, attr_val):
        """RFmxInstr_GetAttributeString."""
        with self._func_lock:
            if self.RFmxInstr_GetAttributeString_cfunc is None:
                self.RFmxInstr_GetAttributeString_cfunc = self._get_library_function(
                    "RFmxInstr_GetAttributeString"
                )
                self.RFmxInstr_GetAttributeString_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_GetAttributeString_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAttributeString_cfunc(
            vi, selector_string, attribute_id, array_size, attr_val
        )

    def RFmxInstr_SetAttributeString(self, vi, selector_string, attribute_id, attr_val):
        """RFmxInstr_SetAttributeString."""
        with self._func_lock:
            if self.RFmxInstr_SetAttributeString_cfunc is None:
                self.RFmxInstr_SetAttributeString_cfunc = self._get_library_function(
                    "RFmxInstr_SetAttributeString"
                )
                self.RFmxInstr_SetAttributeString_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_SetAttributeString_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SetAttributeString_cfunc(vi, selector_string, attribute_id, attr_val)

    def RFmxInstr_CheckAcquisitionStatus(self, vi, acquisition_done):
        """RFmxInstr_CheckAcquisitionStatus."""
        with self._func_lock:
            if self.RFmxInstr_CheckAcquisitionStatus_cfunc is None:
                self.RFmxInstr_CheckAcquisitionStatus_cfunc = self._get_library_function(
                    "RFmxInstr_CheckAcquisitionStatus"
                )
                self.RFmxInstr_CheckAcquisitionStatus_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_CheckAcquisitionStatus_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CheckAcquisitionStatus_cfunc(vi, acquisition_done)

    def RFmxInstr_CfgExternalAttenuationTable(
        self, vi, selector_string, table_name, frequency, external_attenuation, array_size
    ):
        """RFmxInstr_CfgExternalAttenuationTable."""
        with self._func_lock:
            if self.RFmxInstr_CfgExternalAttenuationTable_cfunc is None:
                self.RFmxInstr_CfgExternalAttenuationTable_cfunc = self._get_library_function(
                    "RFmxInstr_CfgExternalAttenuationTable"
                )
                self.RFmxInstr_CfgExternalAttenuationTable_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_CfgExternalAttenuationTable_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CfgExternalAttenuationTable_cfunc(
            vi, selector_string, table_name, frequency, external_attenuation, array_size
        )

    def RFmxInstr_SelectActiveExternalAttenuationTable(self, vi, selector_string, table_name):
        """RFmxInstr_SelectActiveExternalAttenuationTable."""
        with self._func_lock:
            if self.RFmxInstr_SelectActiveExternalAttenuationTable_cfunc is None:
                self.RFmxInstr_SelectActiveExternalAttenuationTable_cfunc = (
                    self._get_library_function("RFmxInstr_SelectActiveExternalAttenuationTable")
                )
                self.RFmxInstr_SelectActiveExternalAttenuationTable_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_SelectActiveExternalAttenuationTable_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SelectActiveExternalAttenuationTable_cfunc(
            vi, selector_string, table_name
        )

    def RFmxInstr_DeleteExternalAttenuationTable(self, vi, selector_string, table_name):
        """RFmxInstr_DeleteExternalAttenuationTable."""
        with self._func_lock:
            if self.RFmxInstr_DeleteExternalAttenuationTable_cfunc is None:
                self.RFmxInstr_DeleteExternalAttenuationTable_cfunc = self._get_library_function(
                    "RFmxInstr_DeleteExternalAttenuationTable"
                )
                self.RFmxInstr_DeleteExternalAttenuationTable_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_DeleteExternalAttenuationTable_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_DeleteExternalAttenuationTable_cfunc(vi, selector_string, table_name)

    def RFmxInstr_DeleteAllExternalAttenuationTables(self, vi, selector_string):
        """RFmxInstr_DeleteAllExternalAttenuationTables."""
        with self._func_lock:
            if self.RFmxInstr_DeleteAllExternalAttenuationTables_cfunc is None:
                self.RFmxInstr_DeleteAllExternalAttenuationTables_cfunc = (
                    self._get_library_function("RFmxInstr_DeleteAllExternalAttenuationTables")
                )
                self.RFmxInstr_DeleteAllExternalAttenuationTables_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_DeleteAllExternalAttenuationTables_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_DeleteAllExternalAttenuationTables_cfunc(vi, selector_string)

    def RFmxInstr_EnableCalibrationPlane(self, vi, selector_string):
        """RFmxInstr_EnableCalibrationPlane."""
        with self._func_lock:
            if self.RFmxInstr_EnableCalibrationPlane_cfunc is None:
                self.RFmxInstr_EnableCalibrationPlane_cfunc = self._get_library_function(
                    "RFmxInstr_EnableCalibrationPlane"
                )
                self.RFmxInstr_EnableCalibrationPlane_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_EnableCalibrationPlane_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_EnableCalibrationPlane_cfunc(vi, selector_string)

    def RFmxInstr_DisableCalibrationPlane(self, vi, selector_string):
        """RFmxInstr_DisableCalibrationPlane."""
        with self._func_lock:
            if self.RFmxInstr_DisableCalibrationPlane_cfunc is None:
                self.RFmxInstr_DisableCalibrationPlane_cfunc = self._get_library_function(
                    "RFmxInstr_DisableCalibrationPlane"
                )
                self.RFmxInstr_DisableCalibrationPlane_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_DisableCalibrationPlane_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_DisableCalibrationPlane_cfunc(vi, selector_string)

    def RFmxInstr_CheckIfSignalConfigurationExists(
        self, vi, signal_name, signal_configuration_exists, personality
    ):
        """RFmxInstr_CheckIfSignalConfigurationExists."""
        with self._func_lock:
            if self.RFmxInstr_CheckIfSignalConfigurationExists_cfunc is None:
                self.RFmxInstr_CheckIfSignalConfigurationExists_cfunc = self._get_library_function(
                    "RFmxInstr_CheckIfSignalConfigurationExists"
                )
                self.RFmxInstr_CheckIfSignalConfigurationExists_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_CheckIfSignalConfigurationExists_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CheckIfSignalConfigurationExists_cfunc(
            vi, signal_name, signal_configuration_exists, personality
        )

    def RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile(
        self, vi, selector_string, table_name, s2p_file_path, s_parameter_orientation
    ):
        """RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile."""
        with self._func_lock:
            if self.RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile_cfunc is None:
                self.RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile_cfunc = (
                    self._get_library_function(
                        "RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile"
                    )
                )
                self.RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxInstr_LoadSParameterExternalAttenuationTableFromS2PFile_cfunc(
            vi, selector_string, table_name, s2p_file_path, s_parameter_orientation
        )

    def RFmxInstr_CfgExternalAttenuationInterpolationNearest(self, vi, selector_string, table_name):
        """RFmxInstr_CfgExternalAttenuationInterpolationNearest."""
        with self._func_lock:
            if self.RFmxInstr_CfgExternalAttenuationInterpolationNearest_cfunc is None:
                self.RFmxInstr_CfgExternalAttenuationInterpolationNearest_cfunc = (
                    self._get_library_function(
                        "RFmxInstr_CfgExternalAttenuationInterpolationNearest"
                    )
                )
                self.RFmxInstr_CfgExternalAttenuationInterpolationNearest_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_CfgExternalAttenuationInterpolationNearest_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxInstr_CfgExternalAttenuationInterpolationNearest_cfunc(
            vi, selector_string, table_name
        )

    def RFmxInstr_CfgExternalAttenuationInterpolationLinear(
        self, vi, selector_string, table_name, format
    ):
        """RFmxInstr_CfgExternalAttenuationInterpolationLinear."""
        with self._func_lock:
            if self.RFmxInstr_CfgExternalAttenuationInterpolationLinear_cfunc is None:
                self.RFmxInstr_CfgExternalAttenuationInterpolationLinear_cfunc = (
                    self._get_library_function(
                        "RFmxInstr_CfgExternalAttenuationInterpolationLinear"
                    )
                )
                self.RFmxInstr_CfgExternalAttenuationInterpolationLinear_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_CfgExternalAttenuationInterpolationLinear_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxInstr_CfgExternalAttenuationInterpolationLinear_cfunc(
            vi, selector_string, table_name, format
        )

    def RFmxInstr_CfgExternalAttenuationInterpolationSpline(self, vi, selector_string, table_name):
        """RFmxInstr_CfgExternalAttenuationInterpolationSpline."""
        with self._func_lock:
            if self.RFmxInstr_CfgExternalAttenuationInterpolationSpline_cfunc is None:
                self.RFmxInstr_CfgExternalAttenuationInterpolationSpline_cfunc = (
                    self._get_library_function(
                        "RFmxInstr_CfgExternalAttenuationInterpolationSpline"
                    )
                )
                self.RFmxInstr_CfgExternalAttenuationInterpolationSpline_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_CfgExternalAttenuationInterpolationSpline_cfunc.restype = (
                    ctypes.c_int32
                )
        return self.RFmxInstr_CfgExternalAttenuationInterpolationSpline_cfunc(
            vi, selector_string, table_name
        )

    def RFmxInstr_CfgSParameterExternalAttenuationType(self, vi, selector_string, s_parameter_type):
        """RFmxInstr_CfgSParameterExternalAttenuationType."""
        with self._func_lock:
            if self.RFmxInstr_CfgSParameterExternalAttenuationType_cfunc is None:
                self.RFmxInstr_CfgSParameterExternalAttenuationType_cfunc = (
                    self._get_library_function("RFmxInstr_CfgSParameterExternalAttenuationType")
                )
                self.RFmxInstr_CfgSParameterExternalAttenuationType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_CfgSParameterExternalAttenuationType_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CfgSParameterExternalAttenuationType_cfunc(
            vi, selector_string, s_parameter_type
        )

    def RFmxInstr_SendSoftwareEdgeStartTrigger(self, vi):
        """RFmxInstr_SendSoftwareEdgeStartTrigger."""
        with self._func_lock:
            if self.RFmxInstr_SendSoftwareEdgeStartTrigger_cfunc is None:
                self.RFmxInstr_SendSoftwareEdgeStartTrigger_cfunc = self._get_library_function(
                    "RFmxInstr_SendSoftwareEdgeStartTrigger"
                )
                self.RFmxInstr_SendSoftwareEdgeStartTrigger_cfunc.argtypes = [ctypes.c_uint32]
                self.RFmxInstr_SendSoftwareEdgeStartTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SendSoftwareEdgeStartTrigger_cfunc(vi)

    def RFmxInstr_SendSoftwareEdgeAdvanceTrigger(self, vi):
        """RFmxInstr_SendSoftwareEdgeAdvanceTrigger."""
        with self._func_lock:
            if self.RFmxInstr_SendSoftwareEdgeAdvanceTrigger_cfunc is None:
                self.RFmxInstr_SendSoftwareEdgeAdvanceTrigger_cfunc = self._get_library_function(
                    "RFmxInstr_SendSoftwareEdgeAdvanceTrigger"
                )
                self.RFmxInstr_SendSoftwareEdgeAdvanceTrigger_cfunc.argtypes = [ctypes.c_uint32]
                self.RFmxInstr_SendSoftwareEdgeAdvanceTrigger_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SendSoftwareEdgeAdvanceTrigger_cfunc(vi)

    def RFmxInstr_CfgFrequencyReference(
        self, vi, selector_string, frequency_reference_source, frequency_reference_frequency
    ):
        """RFmxInstr_CfgFrequencyReference."""
        with self._func_lock:
            if self.RFmxInstr_CfgFrequencyReference_cfunc is None:
                self.RFmxInstr_CfgFrequencyReference_cfunc = self._get_library_function(
                    "RFmxInstr_CfgFrequencyReference"
                )
                self.RFmxInstr_CfgFrequencyReference_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                ]
                self.RFmxInstr_CfgFrequencyReference_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CfgFrequencyReference_cfunc(
            vi, selector_string, frequency_reference_source, frequency_reference_frequency
        )

    def RFmxInstr_CfgMechanicalAttenuation(
        self, vi, selector_string, mechanical_attenuation_auto, mechanical_attenuation_value
    ):
        """RFmxInstr_CfgMechanicalAttenuation."""
        with self._func_lock:
            if self.RFmxInstr_CfgMechanicalAttenuation_cfunc is None:
                self.RFmxInstr_CfgMechanicalAttenuation_cfunc = self._get_library_function(
                    "RFmxInstr_CfgMechanicalAttenuation"
                )
                self.RFmxInstr_CfgMechanicalAttenuation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxInstr_CfgMechanicalAttenuation_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CfgMechanicalAttenuation_cfunc(
            vi, selector_string, mechanical_attenuation_auto, mechanical_attenuation_value
        )

    def RFmxInstr_CfgRFAttenuation(
        self, vi, selector_string, rf_attenuation_auto, rf_attenuation_value
    ):
        """RFmxInstr_CfgRFAttenuation."""
        with self._func_lock:
            if self.RFmxInstr_CfgRFAttenuation_cfunc is None:
                self.RFmxInstr_CfgRFAttenuation_cfunc = self._get_library_function(
                    "RFmxInstr_CfgRFAttenuation"
                )
                self.RFmxInstr_CfgRFAttenuation_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                ]
                self.RFmxInstr_CfgRFAttenuation_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CfgRFAttenuation_cfunc(
            vi, selector_string, rf_attenuation_auto, rf_attenuation_value
        )

    def RFmxInstr_WaitForAcquisitionComplete(self, vi, timeout):
        """RFmxInstr_WaitForAcquisitionComplete."""
        with self._func_lock:
            if self.RFmxInstr_WaitForAcquisitionComplete_cfunc is None:
                self.RFmxInstr_WaitForAcquisitionComplete_cfunc = self._get_library_function(
                    "RFmxInstr_WaitForAcquisitionComplete"
                )
                self.RFmxInstr_WaitForAcquisitionComplete_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.c_double,
                ]
                self.RFmxInstr_WaitForAcquisitionComplete_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_WaitForAcquisitionComplete_cfunc(vi, timeout)

    def RFmxInstr_ResetToDefault(self, vi):
        """RFmxInstr_ResetToDefault."""
        with self._func_lock:
            if self.RFmxInstr_ResetToDefault_cfunc is None:
                self.RFmxInstr_ResetToDefault_cfunc = self._get_library_function(
                    "RFmxInstr_ResetToDefault"
                )
                self.RFmxInstr_ResetToDefault_cfunc.argtypes = [ctypes.c_uint32]
                self.RFmxInstr_ResetToDefault_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_ResetToDefault_cfunc(vi)

    def RFmxInstr_ResetDriver(self, vi):
        """RFmxInstr_ResetDriver."""
        with self._func_lock:
            if self.RFmxInstr_ResetDriver_cfunc is None:
                self.RFmxInstr_ResetDriver_cfunc = self._get_library_function(
                    "RFmxInstr_ResetDriver"
                )
                self.RFmxInstr_ResetDriver_cfunc.argtypes = [ctypes.c_uint32]
                self.RFmxInstr_ResetDriver_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_ResetDriver_cfunc(vi)

    def RFmxInstr_SaveAllConfigurations(self, vi, file_path):
        """RFmxInstr_SaveAllConfigurations."""
        with self._func_lock:
            if self.RFmxInstr_SaveAllConfigurations_cfunc is None:
                self.RFmxInstr_SaveAllConfigurations_cfunc = self._get_library_function(
                    "RFmxInstr_SaveAllConfigurations"
                )
                self.RFmxInstr_SaveAllConfigurations_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_SaveAllConfigurations_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SaveAllConfigurations_cfunc(vi, file_path)

    def RFmxInstr_ResetEntireSession(self, vi):
        """RFmxInstr_ResetEntireSession."""
        with self._func_lock:
            if self.RFmxInstr_ResetEntireSession_cfunc is None:
                self.RFmxInstr_ResetEntireSession_cfunc = self._get_library_function(
                    "RFmxInstr_ResetEntireSession"
                )
                self.RFmxInstr_ResetEntireSession_cfunc.argtypes = [ctypes.c_uint32]
                self.RFmxInstr_ResetEntireSession_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_ResetEntireSession_cfunc(vi)

    def RFmxInstr_ExportSignal(self, vi, export_signal_source, export_signal_output_terminal):
        """RFmxInstr_ExportSignal."""
        with self._func_lock:
            if self.RFmxInstr_ExportSignal_cfunc is None:
                self.RFmxInstr_ExportSignal_cfunc = self._get_library_function(
                    "RFmxInstr_ExportSignal"
                )
                self.RFmxInstr_ExportSignal_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_ExportSignal_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_ExportSignal_cfunc(
            vi, export_signal_source, export_signal_output_terminal
        )

    def RFmxInstr_SelfCalibrate(self, vi, selector_string, steps_to_omit):
        """RFmxInstr_SelfCalibrate."""
        with self._func_lock:
            if self.RFmxInstr_SelfCalibrate_cfunc is None:
                self.RFmxInstr_SelfCalibrate_cfunc = self._get_library_function(
                    "RFmxInstr_SelfCalibrate"
                )
                self.RFmxInstr_SelfCalibrate_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_SelfCalibrate_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SelfCalibrate_cfunc(vi, selector_string, steps_to_omit)

    def RFmxInstr_SelfCalibrateRange(
        self,
        vi,
        selector_string,
        steps_to_omit,
        minimum_frequency,
        maximum_frequency,
        minimum_reference_level,
        maximum_reference_level,
    ):
        """RFmxInstr_SelfCalibrateRange."""
        with self._func_lock:
            if self.RFmxInstr_SelfCalibrateRange_cfunc is None:
                self.RFmxInstr_SelfCalibrateRange_cfunc = self._get_library_function(
                    "RFmxInstr_SelfCalibrateRange"
                )
                self.RFmxInstr_SelfCalibrateRange_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double,
                ]
                self.RFmxInstr_SelfCalibrateRange_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_SelfCalibrateRange_cfunc(
            vi,
            selector_string,
            steps_to_omit,
            minimum_frequency,
            maximum_frequency,
            minimum_reference_level,
            maximum_reference_level,
        )

    def RFmxInstr_LoadConfigurations(self, vi, file_path):
        """RFmxInstr_LoadConfigurations."""
        with self._func_lock:
            if self.RFmxInstr_LoadConfigurations_cfunc is None:
                self.RFmxInstr_LoadConfigurations_cfunc = self._get_library_function(
                    "RFmxInstr_LoadConfigurations"
                )
                self.RFmxInstr_LoadConfigurations_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_LoadConfigurations_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_LoadConfigurations_cfunc(vi, file_path)

    def RFmxInstr_IsSelfCalibrateValid(
        self, vi, selector_string, self_calibrate_valid, valid_steps
    ):
        """RFmxInstr_IsSelfCalibrateValid."""
        with self._func_lock:
            if self.RFmxInstr_IsSelfCalibrateValid_cfunc is None:
                self.RFmxInstr_IsSelfCalibrateValid_cfunc = self._get_library_function(
                    "RFmxInstr_IsSelfCalibrateValid"
                )
                self.RFmxInstr_IsSelfCalibrateValid_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_IsSelfCalibrateValid_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_IsSelfCalibrateValid_cfunc(
            vi, selector_string, self_calibrate_valid, valid_steps
        )

    def RFmxInstr_ResetAttribute(self, vi, selector_string, attribute_id):
        """RFmxInstr_ResetAttribute."""
        with self._func_lock:
            if self.RFmxInstr_ResetAttribute_cfunc is None:
                self.RFmxInstr_ResetAttribute_cfunc = self._get_library_function(
                    "RFmxInstr_ResetAttribute"
                )
                self.RFmxInstr_ResetAttribute_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_ResetAttribute_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_ResetAttribute_cfunc(vi, selector_string, attribute_id)

    def RFmxInstr_CreateDefaultSignalConfiguration(self, vi, signal_name, personality_id):
        """RFmxInstr_CreateDefaultSignalConfiguration."""
        with self._func_lock:
            if self.RFmxInstr_CreateDefaultSignalConfiguration_cfunc is None:
                self.RFmxInstr_CreateDefaultSignalConfiguration_cfunc = self._get_library_function(
                    "RFmxInstr_CreateDefaultSignalConfiguration"
                )
                self.RFmxInstr_CreateDefaultSignalConfiguration_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                ]
                self.RFmxInstr_CreateDefaultSignalConfiguration_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CreateDefaultSignalConfiguration_cfunc(
            vi, signal_name, personality_id
        )

    def RFmxInstr_GetSParameterExternalAttenuationType(self, vi, selector_string, s_parameter_type):
        """RFmxInstr_GetSParameterExternalAttenuationType."""
        with self._func_lock:
            if self.RFmxInstr_GetSParameterExternalAttenuationType_cfunc is None:
                self.RFmxInstr_GetSParameterExternalAttenuationType_cfunc = (
                    self._get_library_function("RFmxInstr_GetSParameterExternalAttenuationType")
                )
                self.RFmxInstr_GetSParameterExternalAttenuationType_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetSParameterExternalAttenuationType_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetSParameterExternalAttenuationType_cfunc(
            vi, selector_string, s_parameter_type
        )

    def RFmxInstr_GetExternalAttenuationTableActualValue(
        self, vi, selector_string, external_attenuation
    ):
        """RFmxInstr_GetExternalAttenuationTableActualValue."""
        with self._func_lock:
            if self.RFmxInstr_GetExternalAttenuationTableActualValue_cfunc is None:
                self.RFmxInstr_GetExternalAttenuationTableActualValue_cfunc = (
                    self._get_library_function("RFmxInstr_GetExternalAttenuationTableActualValue")
                )
                self.RFmxInstr_GetExternalAttenuationTableActualValue_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                ]
                self.RFmxInstr_GetExternalAttenuationTableActualValue_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetExternalAttenuationTableActualValue_cfunc(
            vi, selector_string, external_attenuation
        )

    def RFmxInstr_GetSelfCalibrateLastTemperature(
        self, vi, selector_string, temperature, self_calibrate_step
    ):
        """RFmxInstr_GetSelfCalibrateLastTemperature."""
        with self._func_lock:
            if self.RFmxInstr_GetSelfCalibrateLastTemperature_cfunc is None:
                self.RFmxInstr_GetSelfCalibrateLastTemperature_cfunc = self._get_library_function(
                    "RFmxInstr_GetSelfCalibrateLastTemperature"
                )
                self.RFmxInstr_GetSelfCalibrateLastTemperature_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int64,
                ]
                self.RFmxInstr_GetSelfCalibrateLastTemperature_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetSelfCalibrateLastTemperature_cfunc(
            vi, selector_string, temperature, self_calibrate_step
        )

    def RFmxInstr_GetAvailablePorts(self, vi, selector_string, array_size, available_ports):
        """RFmxInstr_GetAvailablePorts."""
        with self._func_lock:
            if self.RFmxInstr_GetAvailablePorts_cfunc is None:
                self.RFmxInstr_GetAvailablePorts_cfunc = self._get_library_function(
                    "RFmxInstr_GetAvailablePorts"
                )
                self.RFmxInstr_GetAvailablePorts_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_GetAvailablePorts_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAvailablePorts_cfunc(
            vi, selector_string, array_size, available_ports
        )

    def RFmxInstr_GetAvailablePaths(self, vi, selector_string, array_size, available_paths):
        """RFmxInstr_GetAvailablePaths."""
        with self._func_lock:
            if self.RFmxInstr_GetAvailablePaths_cfunc is None:
                self.RFmxInstr_GetAvailablePaths_cfunc = self._get_library_function(
                    "RFmxInstr_GetAvailablePaths"
                )
                self.RFmxInstr_GetAvailablePaths_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_GetAvailablePaths_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetAvailablePaths_cfunc(
            vi, selector_string, array_size, available_paths
        )

    def RFmxInstr_GetSessionUniqueIdentifier(
        self, resource_name, option_string, array_size, session_unique_identifier
    ):
        """RFmxInstr_GetSessionUniqueIdentifier."""
        with self._func_lock:
            if self.RFmxInstr_GetSessionUniqueIdentifier_cfunc is None:
                self.RFmxInstr_GetSessionUniqueIdentifier_cfunc = self._get_library_function(
                    "RFmxInstr_GetSessionUniqueIdentifier"
                )
                self.RFmxInstr_GetSessionUniqueIdentifier_cfunc.argtypes = [
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                ]
                self.RFmxInstr_GetSessionUniqueIdentifier_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetSessionUniqueIdentifier_cfunc(
            resource_name, option_string, array_size, session_unique_identifier
        )

    def RFmxInstr_Initialize(self, resource_name, option_string, handle_out, is_new_session):
        """RFmxInstr_Initialize."""
        with self._func_lock:
            if self.RFmxInstr_Initialize_cfunc is None:
                self.RFmxInstr_Initialize_cfunc = self._get_library_function("RFmxInstr_Initialize")
                self.RFmxInstr_Initialize_cfunc.argtypes = [
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_void_p),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_Initialize_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_Initialize_cfunc(
            resource_name, option_string, handle_out, is_new_session
        )

    def RFmxInstr_Close(self, vi, force_destroy):
        """RFmxInstr_Close."""
        with self._func_lock:
            if self.RFmxInstr_Close_cfunc is None:
                self.RFmxInstr_Close_cfunc = self._get_library_function("RFmxInstr_Close")
                self.RFmxInstr_Close_cfunc.argtypes = [ctypes.c_uint32, ctypes.c_int32]
                self.RFmxInstr_Close_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_Close_cfunc(vi, force_destroy)

    def RFmxInstr_CfgSParameterExternalAttenuationTable(
        self,
        vi,
        selector_string,
        table_name,
        frequency,
        frequency_array_size,
        s_parameters,
        s_parameter_table_size,
        number_of_ports,
        s_parameter_orientation,
    ):
        """RFmxInstr_CfgSParameterExternalAttenuationTable."""
        with self._func_lock:
            if self.RFmxInstr_CfgSParameterExternalAttenuationTable_cfunc is None:
                self.RFmxInstr_CfgSParameterExternalAttenuationTable_cfunc = (
                    self._get_library_function("RFmxInstr_CfgSParameterExternalAttenuationTable")
                )
                self.RFmxInstr_CfgSParameterExternalAttenuationTable_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int32,
                    ctypes.POINTER(_custom_types.ComplexDouble),
                    ctypes.c_int32,
                    ctypes.c_int32,
                    ctypes.c_int32,
                ]
                self.RFmxInstr_CfgSParameterExternalAttenuationTable_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_CfgSParameterExternalAttenuationTable_cfunc(
            vi,
            selector_string,
            table_name,
            frequency,
            frequency_array_size,
            s_parameters,
            s_parameter_table_size,
            number_of_ports,
            s_parameter_orientation,
        )

    def RFmxInstr_GetSignalConfigurationNames(
        self,
        vi,
        selector_string,
        personality_filter,
        signal_names,
        signal_names_size,
        actual_signal_names_size,
        personality,
        personality_array_size,
        actual_personality_array_size,
    ):
        """RFmxInstr_GetSignalConfigurationNames."""
        with self._func_lock:
            if self.RFmxInstr_GetSignalConfigurationNames_cfunc is None:
                self.RFmxInstr_GetSignalConfigurationNames_cfunc = self._get_library_function(
                    "RFmxInstr_GetSignalConfigurationNames"
                )
                self.RFmxInstr_GetSignalConfigurationNames_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetSignalConfigurationNames_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetSignalConfigurationNames_cfunc(
            vi,
            selector_string,
            personality_filter,
            signal_names,
            signal_names_size,
            actual_signal_names_size,
            personality,
            personality_array_size,
            actual_personality_array_size,
        )

    def RFmxInstr_FetchRawIQData(
        self,
        vi,
        selector_string,
        timeout,
        records_to_fetch,
        samples_to_read,
        x0,
        dx,
        data,
        array_size,
        actual_array_size,
        reserved,
    ):
        """RFmxInstr_FetchRawIQData."""
        with self._func_lock:
            if self.RFmxInstr_FetchRawIQData_cfunc is None:
                self.RFmxInstr_FetchRawIQData_cfunc = self._get_library_function(
                    "RFmxInstr_FetchRawIQData"
                )
                self.RFmxInstr_FetchRawIQData_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_double,
                    ctypes.c_int32,
                    ctypes.c_int64,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(_custom_types.ComplexSingle),
                    ctypes.c_int32,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.c_void_p,
                ]
                self.RFmxInstr_FetchRawIQData_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_FetchRawIQData_cfunc(
            vi,
            selector_string,
            timeout,
            records_to_fetch,
            samples_to_read,
            x0,
            dx,
            data,
            array_size,
            actual_array_size,
            reserved,
        )

    def RFmxInstr_GetSelfCalibrateLastDateAndTime(
        self, vi, selector_string, self_calibrate_step, year, month, day, hour, minute
    ):
        """RFmxInstr_GetSelfCalibrateLastDateAndTime."""
        with self._func_lock:
            if self.RFmxInstr_GetSelfCalibrateLastDateAndTime_cfunc is None:
                self.RFmxInstr_GetSelfCalibrateLastDateAndTime_cfunc = self._get_library_function(
                    "RFmxInstr_GetSelfCalibrateLastDateAndTime_Split"
                )
                self.RFmxInstr_GetSelfCalibrateLastDateAndTime_cfunc.argtypes = [
                    ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_char),
                    ctypes.c_int64,
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                    ctypes.POINTER(ctypes.c_int32),
                ]
                self.RFmxInstr_GetSelfCalibrateLastDateAndTime_cfunc.restype = ctypes.c_int32
        return self.RFmxInstr_GetSelfCalibrateLastDateAndTime_cfunc(
            vi, selector_string, self_calibrate_step, year, month, day, hour, minute
        )
