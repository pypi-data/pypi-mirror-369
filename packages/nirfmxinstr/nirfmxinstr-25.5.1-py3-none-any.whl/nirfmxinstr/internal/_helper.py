"""Contains utility functions."""

import threading
from abc import ABC
from collections import defaultdict
from typing import Any, DefaultDict

import numpy
from fasteners import ReaderWriterLock

signal_name_prefix = "signal::"
result_name_prefix = "result::"
all_number_string = "::all"
LO_number_prefix = "LO"
instr_number_prefix = "instr"
module_name_prefix = "module::"


def prepend_signal_string(signal_name: str, selector_string: str) -> str:
    """Prepends the signal name to the selector string with 'signal::' prefix."""
    updated_selector_string = []

    if signal_name and selector_string:
        updated_selector_string.append(f"{signal_name_prefix}{signal_name}/{selector_string}")
    else:
        if signal_name:
            updated_selector_string.append(f"{signal_name_prefix}{signal_name}")
        else:
            updated_selector_string.append(selector_string)

    return "".join(updated_selector_string)


def build_result_string(result_name: str) -> str:
    """Builds a result string with the result name prefixed by 'result::'."""
    selector = []
    if result_name:
        if result_name.lower().startswith(result_name_prefix.lower()):
            selector.append(result_name)
        else:
            selector.append(f"{result_name_prefix}{result_name}")
    return "".join(selector)


def append_number(prefix: str, number: int, selector: str) -> str:
    """Appends a number to a prefix and selector string."""
    selector_string = []
    if number == -1:
        number_string = all_number_string
    else:
        number_string = str(number)

    if not selector:
        selector_string.append(f"{prefix}{number_string}")
    else:
        selector_string.append(f"{selector}/{prefix}{number_string}")

    return "".join(selector_string)


def split_string_by_comma(comma_separated_string: str) -> Any:
    """Splits a comma-separated string into a list."""
    return comma_separated_string.split(",") if comma_separated_string else []


def create_comma_separated_string(string_list: Any) -> str:
    """Helper function to join string list with commas."""
    validate_not_none(string_list, "string_list")

    if len(string_list) > 1:
        return ",".join(string_list)

    return ""  # Return empty string if string_list is empty


def validate_not_none(parameter: Any, parameter_name: str) -> None:
    """Validates that the parameter is not None."""
    if parameter is None:
        raise ValueError(f"{parameter_name} cannot be None.")


def validate_numpy_array(parameter: Any, parameter_name: Any, expected_data_type: Any) -> None:
    """Validates that the parameter is a numpy array with the expected data type."""
    if parameter is None:
        raise ValueError(f"{parameter_name} cannot be None.")
    if type(parameter) is not numpy.ndarray:
        raise TypeError(f"{parameter_name} must be numpy.ndarray, is {type(parameter)}")
    if numpy.isfortran(parameter) is True:
        raise TypeError(f"{parameter_name} must be in C-order")
    if parameter.dtype is not numpy.dtype(f"{expected_data_type}"):
        raise TypeError(
            f"{parameter_name} must be numpy.ndarray of dtype={expected_data_type}, is "
            + str(parameter.dtype)
        )


def validate_signal_not_empty(value: str, parameter_name: str) -> None:
    """Validates that the signal name is not empty."""
    if len(value) == 0:
        raise ValueError(f"{parameter_name} cannot be empty.")


def validate_and_update_selector_string(selector_string: str, obj: Any) -> str:
    """Validates and updates the selector string based on the signal configuration mode."""
    param_name = "selector_string"

    if obj._signal_configuration_mode == "Signal":
        if selector_string.lower().startswith(signal_name_prefix.lower()):
            raise ValueError(f"Invalid {param_name}.")
        return prepend_signal_string(obj.signal_configuration_name, selector_string)

    return ""


def validate_and_remove_signal_qualifier(signal_name: str, parameter_name: Any) -> str:
    r"""This function checks if the "signal_name" contains the qualified name.
    If so, removes the qualifier "signal::" and returns just the name.
    """
    validate_not_none(signal_name, parameter_name)
    signal_prefix = signal_name_prefix
    if signal_name.lower().startswith(signal_prefix.lower()):
        return signal_name[len(signal_prefix) :]
    return signal_name


def validate_array_parameter_sizes_are_equal(
    array_parameter_names: Any, *array_parameters: Any
) -> int:
    """Validates that all array parameters have the same size."""
    array_size = 0
    length = -1

    for parameter in array_parameters:
        if parameter is not None and len(parameter) != 0:
            if length == -1:
                # Get the first non-none item's length if not already obtained
                length = len(parameter)
                array_size = length
            else:
                # Compare consecutive array lengths
                if len(parameter) != length:
                    raise ValueError(
                        f"Array size mismatch: {get_non_none_array_parameter_names(array_parameter_names, array_parameters)}"
                    )

    return array_size


def get_non_none_array_parameter_names(array_parameter_names: Any, array_parameters: Any) -> Any:
    """Returns a comma-separated string of non-None array parameter names."""
    parameter_name_list = []
    comma_separator = ","

    for i in range(len(array_parameters)):
        if array_parameters[i] is not None:
            parameter_name_list.append(array_parameter_names[i])

    # Join the parameter names using the comma separator
    return comma_separator.join(parameter_name_list)


def contains(source: str, to_check: str, comparison: str = "case_insensitive") -> bool:
    """Checks if 'to_check' is contained in 'source' based on the specified comparison type."""
    if comparison == "case_insensitive":
        return to_check.lower() in source.lower()
    elif comparison == "case_sensitive":
        return to_check in source
    else:
        raise ValueError("Invalid comparison type. Use 'case_insensitive' or 'case_sensitive'.")


def build_lo_string(selector_string, lo_index):
    """Builds a lo string."""
    LO_number_string = append_number(LO_number_prefix, lo_index, selector_string)
    return LO_number_string


def build_instrument_string(selector_string, instrument_number):
    """Builds a instrument string."""
    instr_number_string = append_number(instr_number_prefix, instrument_number, selector_string)
    return instr_number_string


def build_module_string(selector_string, module_name):
    """Builds a module string."""
    selector = []

    if selector_string:
        selector.append(selector_string)

    if module_name:
        if selector_string:
            selector.append("/")
        if module_name.lower().startswith(module_name_prefix.lower()):
            selector.append(module_name)
        else:
            selector.append(f"{module_name_prefix}{module_name}")

    return "".join(selector)


calibration_plane_name_prefix = "calplane::"
port_name_prefix = "port::"


def build_calibration_plane_string(calibration_plane_name):
    """Builds a calibration plane string."""
    if not calibration_plane_name:
        return ""
    if calibration_plane_name.lower().startswith(calibration_plane_name_prefix.lower()):
        return calibration_plane_name
    else:
        return f"{calibration_plane_name_prefix}{calibration_plane_name}"


def build_port_string(selector_string, port_name, device_name, channel_number):
    """Builds a port string."""
    selector = []

    if selector_string:
        selector.append(selector_string)

    if port_name or device_name:
        if device_name:
            if selector_string:
                selector.append("/")

            selector.append(port_name_prefix)
            selector.append(device_name)
            selector.append(f"/{channel_number}")

            stripped_port_name = port_name.replace(port_name_prefix, "") if port_name else ""
            if stripped_port_name:
                selector.append(f"/{stripped_port_name}")

        else:
            stripped_port_name = port_name.replace(port_name_prefix, "") if port_name else ""
            if stripped_port_name:
                if selector_string:
                    selector.append("/")

                selector.append(port_name_prefix)
                selector.append(stripped_port_name)

    return "".join(selector)


class SessionFunctionLock:
    """A class to manage read/write locks for session functions."""

    _lock = ReaderWriterLock()

    @classmethod
    def enter_read_lock(cls) -> Any:
        """Acquires a read lock for session functions."""
        cls._lock.acquire_read_lock()

    @classmethod
    def exit_read_lock(cls) -> Any:
        """Releases the read lock for session functions."""
        cls._lock.release_read_lock()

    @classmethod
    def enter_write_lock(cls) -> Any:
        """Acquires a write lock for session functions."""
        cls._lock.acquire_write_lock()

    @classmethod
    def exit_write_lock(cls) -> Any:
        """Releases the write lock for session functions."""
        cls._lock.release_write_lock()


class ConcurrentDictionary:
    """A thread-safe dictionary that allows concurrent access."""

    def __init__(self):
        """Initializes the ConcurrentDictionary with a thread lock and a default dictionary."""
        self._lock = threading.RLock()
        self._data: DefaultDict[str, Any] = defaultdict(lambda: None)

    def __getitem__(self, key: str) -> Any:
        """Retrieves an item from the dictionary in a thread-safe manner."""
        with self._lock:
            return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets an item in the dictionary in a thread-safe manner."""
        with self._lock:
            self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """Deletes an item from the dictionary in a thread-safe manner."""
        with self._lock:
            del self._data[key]


def validate_mimo_resource_name(device_names: Any, parameter_name: Any) -> None:
    """Validates the MIMO resource names."""
    if parameter_name is None:
        raise ValueError(f"{parameter_name} cannot be None.")

    if isinstance(device_names, list) and len(device_names) > 1:
        for device in device_names:
            if not device:  # Checks for None or empty string
                raise ValueError("Empty resource name is not valid for MIMO.")


class SignalConfiguration(ABC):
    """Represents a signal configuration. Implement this interface to expose measurement functionality."""

    """Type of the current signal configuration object."""
    signal_configuration_type = None

    """Name assigned to the current signal configuration object."""
    signal_configuration_name = ""
