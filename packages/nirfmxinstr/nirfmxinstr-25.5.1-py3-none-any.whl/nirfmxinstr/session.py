"""session.py - Defines a root class that identifies and controls the instrument session."""

import functools
import pprint
import threading
from typing import Any

import nirfmxinstr.attributes as attributes
import nirfmxinstr.enums as enums
import nirfmxinstr.errors as errors
import nirfmxinstr.internal._helper as _helper
from nirfmxinstr.internal._library_interpreter import LibraryInterpreter
from nirfmxinstr.internal._signal_configuration_manager import (
    SignalConfigurationManager,
)


def _raise_if_disposed(f):
    """From https://stackoverflow.com/questions/5929107/decorators-with-parameters."""

    @functools.wraps(f)
    def aux(*xs, **kws):
        session = xs[0]  # parameter 0 is 'self' which is the session object
        if session.is_disposed:
            raise Exception("Cannot access a disposed Session object.")
        return f(*xs, **kws)

    return aux


class _SessionBase(object):
    """Defines a base class for Session."""

    _instr_map = _helper.ConcurrentDictionary()  # type: ignore
    _session_function_lock = _helper.SessionFunctionLock()
    _signal_lock = threading.RLock()
    _sync_root = threading.RLock()

    def __init__(self, resource_name, option_string="", instrument_handle=None):
        self.is_disposed = False
        self._reference_count = 0
        self._signal_manager = SignalConfigurationManager()  # type: ignore
        self._interpreter = LibraryInterpreter(encoding="windows-1251")  # type: ignore

        if instrument_handle:
            self._resource_name = None
            self._interpreter.set_session_handle(instrument_handle)
            _, _ = self._interpreter.get_attribute_i32(
                "", attributes.AttributeID.PRESELECTOR_PRESENT.value
            )  # type: ignore
        else:
            _helper.validate_mimo_resource_name(resource_name, "resource_name")
            _helper.validate_not_none(option_string, "option_string")
            session_unique_identifier = Session._get_session_unique_identifier(
                resource_name, option_string
            )

            comma_seperated_resource_name = resource_name
            if isinstance(resource_name, list):
                comma_seperated_resource_name = _helper.create_comma_separated_string(resource_name)

            Session._sync_root.acquire()
            if session_unique_identifier not in Session._instr_map._data:
                self._resource_name = session_unique_identifier
                handle_out, is_new_session, error_code = self._interpreter.initialize(
                    comma_seperated_resource_name, option_string
                )  # type: ignore
                self._interpreter.set_session_handle(handle_out)
                if session_unique_identifier:
                    Session._instr_map._data[session_unique_identifier] = self
                    self._increment_reference_count()
            else:
                raise Exception("Session already exists for the given resource name(s).")
            Session._sync_root.release()

        # Store the parameter list for later printing in __repr__
        pp = pprint.PrettyPrinter(indent=4)
        param_list = []
        param_list.append("resource_name=" + pp.pformat(resource_name))
        param_list.append("option_string=" + pp.pformat(option_string))
        param_list.append("instrument_handle=" + pp.pformat(instrument_handle))
        self._param_list = ", ".join(param_list)

    def __enter__(self):
        """Enables the use of the session object in a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Enables the use of the session object in a context manager."""
        self.close()  # type: ignore

    def _increment_reference_count(self) -> None:
        self._reference_count += 1

    def _decrement_reference_count(self) -> None:
        self._reference_count -= 1

    def dispose(self):
        r"""Closes the RFmx session.

        Call this function a number of times equal to the number of times you
        obtained a reference to the RFmx session for a particular resource name.

        .. note::
            You can call this function safely more than once, even if the session is already closed.

            If you have used an existing instrument handle to create this session; calling the dispose,
            close, or force_close functions will only dispose the Python resources associated with this session.
            The pre-existing instrument handle will NOT be released.
        """
        self.close()  # type: ignore

    def close(self):
        r"""Closes the RFmx session.

        Call this function a number of times equal to the number of times you
        obtained a reference to the RFmx session for a particular resource name.

        .. note::
            If you have used an existing instrument handle to create this session; calling the dispose,
            close, or force_close functions will only dispose the Python resources associated with this session.
            The pre-existing instrument handle will NOT be released.
        """
        self._session_function_lock.enter_write_lock()
        try:
            if not self.is_disposed:
                if not self._resource_name:
                    self._interpreter.close(False)  # type: ignore
                    self._interpreter.set_session_handle()
                else:
                    Session._sync_root.acquire()
                    self._decrement_reference_count()
                    if self._reference_count == 0:
                        self._interpreter.close(False)  # type: ignore
                        del Session._instr_map._data[self._resource_name]
                        self._interpreter.set_session_handle()
                        self.is_disposed = True
                    Session._sync_root.release()

        except errors.RFmxError:
            self._interpreter.set_session_handle()
            raise
        self._session_function_lock.exit_write_lock()

    def force_close(self):
        r"""Closes all RFmx sessions.

        Calling this method once will destroy the session,
        irrespective of the many references obtained for the session for a particular resource name.

        .. note::
            If you have used an existing instrument handle to create this session; calling the dispose,
            close, or force_close functions will only dispose the Python resources associated with this session.
            The pre-existing instrument handle will NOT be released.
        """
        self._session_function_lock.enter_write_lock()
        try:
            if not self.is_disposed:
                if not self._resource_name:
                    self._interpreter.close(True)  # type: ignore
                    self._interpreter.set_session_handle()
                else:
                    Session._sync_root.acquire()
                    self._interpreter.close(True)  # type: ignore
                    del Session._instr_map._data[self._resource_name]
                    self._interpreter.set_session_handle()
                    self.is_disposed = True
                    self._reference_count = 0
                    Session._sync_root.release()
        except errors.RFmxError:
            self._interpreter.set_session_handle()
        self._session_function_lock.exit_write_lock()

    @_raise_if_disposed
    def get_warning(self):
        r"""Retrieves and then clears the warning information for the session.

        Returns:
            Tuple (warning_code, warning_message):

            warning_code (int):
                Contains the latest warning code.

            warning_message (string):
                Contains the latest warning description.
        """
        try:
            self._session_function_lock.enter_read_lock()
            warning_code, warning_message = self._interpreter.get_error()
        finally:
            self._session_function_lock.exit_read_lock()

        return warning_code, warning_message

    @_raise_if_disposed
    def get_error_string(self, error_code):
        r"""Gets the description of a driver error code.

        Args:
            error_code (int):
                Specifies an error or warning code.

        Returns:
            string:
                Contains the error description.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_message = self._interpreter.get_error_string(error_code)
        finally:
            self._session_function_lock.exit_read_lock()

        return error_message

    @_raise_if_disposed
    def get_frequency_reference_source(self, selector_string):
        r"""Gets the frequency reference source.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        All other devices default value is **OnboardClock**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                  | Description                                                                                                              |
        +===============================+==========================================================================================================================+
        | OnboardClock (OnboardClock)   | PXIe-5663/5663E: The RFmx driver locks the PXIe-5663/5663E to the PXIe-5652 LO source onboard clock. Connect the REF     |
        |                               | OUT2 connector (if it exists) on the PXIe-5652 to the PXIe-5622 CLK IN terminal. On versions of the PXIe-5663/5663E      |
        |                               | that lack a REF OUT2 connector on the PXIe-5652, connect the REF IN/OUT connector on the PXIe-5652 to the PXIe-5622 CLK  |
        |                               | IN terminal.                                                                                                             |
        |                               | PXIe-5665: The RFmx driver locks the PXIe-5665 to the PXIe-5653 LO source onboard clock. Connect the 100 MHz REF OUT     |
        |                               | terminal on the PXIe-5653 to the PXIe-5622 CLK IN terminal.                                                              |
        |                               | PXIe-5668: Lock the PXIe-5668 to the PXIe-5653 LO SOURCE onboard clock. Connect the LO2 OUT connector on the PXIe-5606   |
        |                               | to the CLK IN connector on the PXIe-5624.                                                                                |
        |                               | PXIe-5644/5645/5646, PXIe-5820/5840/5841/5842/5860: The RFmx driver locks the device to its onboard clock.               |
        |                               | PXIe-5830/5831/5832: For PXIe-5830, connect the PXIe-5820 REF IN connector to the PXIe-3621 REF OUT connector. For       |
        |                               | PXIe-5831, connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. For PXIe-5832, connect the         |
        |                               | PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector.                                                           |
        |                               | PXIe-5831 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3622 REF IN connector.                                                  |
        |                               | PXIe-5832 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3623 REF IN connector.                                                  |
        |                               | PXIe-5842: Lock to the associated PXIe-5655 onboard clock. Cables between modules are required as shown in the Getting   |
        |                               | Started Guide for the instrument.                                                                                        |
        |                               | PXIe-5860: Lock to the PXIe-5860 onboard clock.                                                                          |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefIn (RefIn)                 | PXIe-5663/5663E: Connect the external signal to the PXIe-5652 REF IN/OUT connector. Connect the REF OUT2 connector (if   |
        |                               | it exists) on the PXIe-5652 to the PXIe-5622 CLK IN terminal.                                                            |
        |                               | PXIe-5665: Connect the external signal to the PXIe-5653 REF IN connector. Connect the 100 MHz REF OUT terminal on the    |
        |                               | PXIe-5653 to the PXIe-5622 CLK IN connector. If your external clock signal frequency is set to a frequency other than    |
        |                               | 10 MHz, set the Frequency Reference Frequency attribute according to the frequency of your external clock signal.        |
        |                               | PXIe-5668: Connect the external signal to the PXIe-5653 REF IN connector. Connect the LO2 OUT on the PXIe-5606 to the    |
        |                               | CLK IN connector on the PXIe-5622. If your external clock signal frequency is set to a frequency other than 10 MHz, set  |
        |                               | the Frequency Reference Frequency attribute according to the frequency of your external clock signal.                    |
        |                               | PXIe-5644/5645/5646, PXIe-5820/5840/5841/5842/5860: The RFmx driver locks the device to the signal at the external REF   |
        |                               | IN connector.                                                                                                            |
        |                               | PXIe-5830/5831/5832: For PXIe-5830, connect the PXIe-5820 REF IN connector to the PXIe-3621 REF OUT connector. For       |
        |                               | PXIe-5831, connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. For PXIe-5832, connect the         |
        |                               | PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. For PXIe-5830, lock the external signal to the PXIe-3621  |
        |                               | REF IN connector. For PXIe-5831, lock the external signal to the PXIe-3622 REF IN connector. For PXIe-5832, lock the     |
        |                               | external signal to the PXIe-3623 REF IN connector.                                                                       |
        |                               | PXIe-5831 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3622 REF IN connector. Lock the external signal to the PXIe-5653 REF    |
        |                               | IN connector.                                                                                                            |
        |                               | PXIe-5832 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3623 REF IN connector. Lock the external signal to the PXIe-5653 REF    |
        |                               | IN connector.                                                                                                            |
        |                               | PXIe-5842: Lock to the signal at the REF IN connector on the associated PXIe-5655. Cables between modules are required   |
        |                               | as shown in the Getting Started Guide for the instrument.                                                                |
        |                               | PXIe-5860:Lock to the signal at the REF IN connector on the PXIe-5860.                                                   |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Clk (PXI_Clk)             | PXIe-5668: Lock the PXIe-5653 to the PXI backplane clock. Connect the PXIe-5606 LO2 OUT to the LO2 IN connector on the   |
        |                               | PXIe-5624.                                                                                                               |
        |                               | PXIe-5644/5645/5646, PXIe-5663/5663E/5665, and PXIe-5820/5840/5841/5860: The RFmx driver locks the device to the PXI     |
        |                               | backplane clock.                                                                                                         |
        |                               | PXIe-5830/5831/5832 with PXIe-5653/5841 with PXIe-5655, PXIe-5842/5860: The RFmx driver locks the device to the PXI      |
        |                               | backplane clock. Cables between modules are required as shown in the Getting Started Guide for the instrument.           |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkIn (ClkIn)                 | PXIe-5663/5663E: The RFmx driver locks the PXIe-5663/5663E to an external 10 MHz signal. Connect the external signal to  |
        |                               | the PXIe-5622 CLK IN connector, and connect the PXIe-5622 CLK OUT connector to the FREQ REF IN connector on the          |
        |                               | PXIe-5652.                                                                                                               |
        |                               | PXIe-5665: The RFmx driver locks the PXIe-5665 to an external 100 MHz signal. Connect the external signal to the         |
        |                               | PXIe-5622 CLK IN connector, and connect the PXIe-5622 CLK OUT connector to the REF IN connector on the PXIe-5653. Set    |
        |                               | the Frequency Reference Frequency attribute to 100 MHz.                                                                  |
        |                               | PXIe-5668: Lock the PXIe-5668 to an external 100 MHz signal. Connect the external signal to the CLK IN connector on the  |
        |                               | PXIe-5624, and connect the PXIe-5624 CLK OUT connector to the REF IN connector on the PXIe-5653. Set the Frequency       |
        |                               | Reference Frequency attribute to 100 MHz.                                                                                |
        |                               | PXIe-5644/5645/5646, PXIe-5820/5830/5831/5831 with PXIe-5653/5832/5832 with PXIe-5653/5840/5841/5842/5840/5860 with      |
        |                               | PXIe-5653: This configuration does not apply.                                                                            |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefIn2 (RefIn2)               |                                                                                                                          |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_ClkMaster (PXI_ClkMaster) | PXIe-5831 with PXIe-5653: The RFmx driver configures the PXIe-5653 to export the reference clock and configures the      |
        |                               | PXIe-5820 and PXIe-3622 to use PXI_Clk as the reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz)    |
        |                               | connector to the PXI chassis REF IN connector.                                                                           |
        |                               | PXIe-5832 with PXIe-5653: The RFmx driver configures the PXIe-5653 to export the reference clock and configures the      |
        |                               | PXIe-5820 and PXIe-3623 to use PXI_Clk as the reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz)    |
        |                               | connector to the PXI chassis REF IN connector.                                                                           |
        |                               | PXIe-5840 with PXIe-5653: The RFmx driver configures the PXIe-5653 to export the reference clock, and configures the     |
        |                               | PXIe-5840 to use PXI_Clk. For best performance, configure all other devices in the system to use PXI_Clk as the          |
        |                               | reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz) connector to the PXIe-5840 REF IN connector for  |
        |                               | this configuration.                                                                                                      |
        |                               | PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860: This configuration does    |
        |                               | not apply.                                                                                                               |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the frequency reference source.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_reference_source(self, selector_string, value):
        r"""Sets the frequency reference source.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        All other devices default value is **OnboardClock**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                  | Description                                                                                                              |
        +===============================+==========================================================================================================================+
        | OnboardClock (OnboardClock)   | PXIe-5663/5663E: The RFmx driver locks the PXIe-5663/5663E to the PXIe-5652 LO source onboard clock. Connect the REF     |
        |                               | OUT2 connector (if it exists) on the PXIe-5652 to the PXIe-5622 CLK IN terminal. On versions of the PXIe-5663/5663E      |
        |                               | that lack a REF OUT2 connector on the PXIe-5652, connect the REF IN/OUT connector on the PXIe-5652 to the PXIe-5622 CLK  |
        |                               | IN terminal.                                                                                                             |
        |                               | PXIe-5665: The RFmx driver locks the PXIe-5665 to the PXIe-5653 LO source onboard clock. Connect the 100 MHz REF OUT     |
        |                               | terminal on the PXIe-5653 to the PXIe-5622 CLK IN terminal.                                                              |
        |                               | PXIe-5668: Lock the PXIe-5668 to the PXIe-5653 LO SOURCE onboard clock. Connect the LO2 OUT connector on the PXIe-5606   |
        |                               | to the CLK IN connector on the PXIe-5624.                                                                                |
        |                               | PXIe-5644/5645/5646, PXIe-5820/5840/5841/5842/5860: The RFmx driver locks the device to its onboard clock.               |
        |                               | PXIe-5830/5831/5832: For PXIe-5830, connect the PXIe-5820 REF IN connector to the PXIe-3621 REF OUT connector. For       |
        |                               | PXIe-5831, connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. For PXIe-5832, connect the         |
        |                               | PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector.                                                           |
        |                               | PXIe-5831 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3622 REF IN connector.                                                  |
        |                               | PXIe-5832 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3623 REF IN connector.                                                  |
        |                               | PXIe-5842: Lock to the associated PXIe-5655 onboard clock. Cables between modules are required as shown in the Getting   |
        |                               | Started Guide for the instrument.                                                                                        |
        |                               | PXIe-5860: Lock to the PXIe-5860 onboard clock.                                                                          |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefIn (RefIn)                 | PXIe-5663/5663E: Connect the external signal to the PXIe-5652 REF IN/OUT connector. Connect the REF OUT2 connector (if   |
        |                               | it exists) on the PXIe-5652 to the PXIe-5622 CLK IN terminal.                                                            |
        |                               | PXIe-5665: Connect the external signal to the PXIe-5653 REF IN connector. Connect the 100 MHz REF OUT terminal on the    |
        |                               | PXIe-5653 to the PXIe-5622 CLK IN connector. If your external clock signal frequency is set to a frequency other than    |
        |                               | 10 MHz, set the Frequency Reference Frequency attribute according to the frequency of your external clock signal.        |
        |                               | PXIe-5668: Connect the external signal to the PXIe-5653 REF IN connector. Connect the LO2 OUT on the PXIe-5606 to the    |
        |                               | CLK IN connector on the PXIe-5622. If your external clock signal frequency is set to a frequency other than 10 MHz, set  |
        |                               | the Frequency Reference Frequency attribute according to the frequency of your external clock signal.                    |
        |                               | PXIe-5644/5645/5646, PXIe-5820/5840/5841/5842/5860: The RFmx driver locks the device to the signal at the external REF   |
        |                               | IN connector.                                                                                                            |
        |                               | PXIe-5830/5831/5832: For PXIe-5830, connect the PXIe-5820 REF IN connector to the PXIe-3621 REF OUT connector. For       |
        |                               | PXIe-5831, connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. For PXIe-5832, connect the         |
        |                               | PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. For PXIe-5830, lock the external signal to the PXIe-3621  |
        |                               | REF IN connector. For PXIe-5831, lock the external signal to the PXIe-3622 REF IN connector. For PXIe-5832, lock the     |
        |                               | external signal to the PXIe-3623 REF IN connector.                                                                       |
        |                               | PXIe-5831 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3622 REF IN connector. Lock the external signal to the PXIe-5653 REF    |
        |                               | IN connector.                                                                                                            |
        |                               | PXIe-5832 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. Connect the         |
        |                               | PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3623 REF IN connector. Lock the external signal to the PXIe-5653 REF    |
        |                               | IN connector.                                                                                                            |
        |                               | PXIe-5842: Lock to the signal at the REF IN connector on the associated PXIe-5655. Cables between modules are required   |
        |                               | as shown in the Getting Started Guide for the instrument.                                                                |
        |                               | PXIe-5860:Lock to the signal at the REF IN connector on the PXIe-5860.                                                   |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Clk (PXI_Clk)             | PXIe-5668: Lock the PXIe-5653 to the PXI backplane clock. Connect the PXIe-5606 LO2 OUT to the LO2 IN connector on the   |
        |                               | PXIe-5624.                                                                                                               |
        |                               | PXIe-5644/5645/5646, PXIe-5663/5663E/5665, and PXIe-5820/5840/5841/5860: The RFmx driver locks the device to the PXI     |
        |                               | backplane clock.                                                                                                         |
        |                               | PXIe-5830/5831/5832 with PXIe-5653/5841 with PXIe-5655, PXIe-5842/5860: The RFmx driver locks the device to the PXI      |
        |                               | backplane clock. Cables between modules are required as shown in the Getting Started Guide for the instrument.           |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkIn (ClkIn)                 | PXIe-5663/5663E: The RFmx driver locks the PXIe-5663/5663E to an external 10 MHz signal. Connect the external signal to  |
        |                               | the PXIe-5622 CLK IN connector, and connect the PXIe-5622 CLK OUT connector to the FREQ REF IN connector on the          |
        |                               | PXIe-5652.                                                                                                               |
        |                               | PXIe-5665: The RFmx driver locks the PXIe-5665 to an external 100 MHz signal. Connect the external signal to the         |
        |                               | PXIe-5622 CLK IN connector, and connect the PXIe-5622 CLK OUT connector to the REF IN connector on the PXIe-5653. Set    |
        |                               | the Frequency Reference Frequency attribute to 100 MHz.                                                                  |
        |                               | PXIe-5668: Lock the PXIe-5668 to an external 100 MHz signal. Connect the external signal to the CLK IN connector on the  |
        |                               | PXIe-5624, and connect the PXIe-5624 CLK OUT connector to the REF IN connector on the PXIe-5653. Set the Frequency       |
        |                               | Reference Frequency attribute to 100 MHz.                                                                                |
        |                               | PXIe-5644/5645/5646, PXIe-5820/5830/5831/5831 with PXIe-5653/5832/5832 with PXIe-5653/5840/5841/5842/5840/5860 with      |
        |                               | PXIe-5653: This configuration does not apply.                                                                            |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefIn2 (RefIn2)               |                                                                                                                          |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_ClkMaster (PXI_ClkMaster) | PXIe-5831 with PXIe-5653: The RFmx driver configures the PXIe-5653 to export the reference clock and configures the      |
        |                               | PXIe-5820 and PXIe-3622 to use PXI_Clk as the reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz)    |
        |                               | connector to the PXI chassis REF IN connector.                                                                           |
        |                               | PXIe-5832 with PXIe-5653: The RFmx driver configures the PXIe-5653 to export the reference clock and configures the      |
        |                               | PXIe-5820 and PXIe-3623 to use PXI_Clk as the reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz)    |
        |                               | connector to the PXI chassis REF IN connector.                                                                           |
        |                               | PXIe-5840 with PXIe-5653: The RFmx driver configures the PXIe-5653 to export the reference clock, and configures the     |
        |                               | PXIe-5840 to use PXI_Clk. For best performance, configure all other devices in the system to use PXI_Clk as the          |
        |                               | reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz) connector to the PXIe-5840 REF IN connector for  |
        |                               | this configuration.                                                                                                      |
        |                               | PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860: This configuration does    |
        |                               | not apply.                                                                                                               |
        +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the frequency reference source.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_reference_frequency(self, selector_string):
        r"""Gets the Reference Clock rate, when the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE`
        attribute is set to **ClkIn** or **RefIn**. This value is expressed in Hz.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 10 MHz.

        **Valid values**

        +-------------------------------------------------------------------------------+------------------------------------------------------+
        | Name (value)                                                                  | Description                                          |
        +===============================================================================+======================================================+
        | PXIe-5644/5645/5646, PXIe-5663/5663E, PXIe-5820/5830/5831/5832/5840/5841/5842 | 10 MHz                                               |
        +-------------------------------------------------------------------------------+------------------------------------------------------+
        | PXIe-5665/5668                                                                | 5 MHz to 100 MHz (inclusive), in increments of 1 MHz |
        +-------------------------------------------------------------------------------+------------------------------------------------------+
        | PXIe-5860                                                                     | 10 MHz, 100 MHz                                      |
        +-------------------------------------------------------------------------------+------------------------------------------------------+

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the Reference Clock rate, when the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE`
                attribute is set to **ClkIn** or **RefIn**. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_REFERENCE_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_reference_frequency(self, selector_string, value):
        r"""Sets the Reference Clock rate, when the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE`
        attribute is set to **ClkIn** or **RefIn**. This value is expressed in Hz.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 10 MHz.

        **Valid values**

        +-------------------------------------------------------------------------------+------------------------------------------------------+
        | Name (value)                                                                  | Description                                          |
        +===============================================================================+======================================================+
        | PXIe-5644/5645/5646, PXIe-5663/5663E, PXIe-5820/5830/5831/5832/5840/5841/5842 | 10 MHz                                               |
        +-------------------------------------------------------------------------------+------------------------------------------------------+
        | PXIe-5665/5668                                                                | 5 MHz to 100 MHz (inclusive), in increments of 1 MHz |
        +-------------------------------------------------------------------------------+------------------------------------------------------+
        | PXIe-5860                                                                     | 10 MHz, 100 MHz                                      |
        +-------------------------------------------------------------------------------+------------------------------------------------------+

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the Reference Clock rate, when the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE`
                attribute is set to **ClkIn** or **RefIn**. This value is expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_REFERENCE_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_reference_exported_terminal(self, selector_string):
        r"""Gets a comma-separated list of the terminals at which to export the frequency reference.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **None**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | None ()           | The Reference Clock is not exported. This value is not valid for the PXIe-5644/5645/5646.                                |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)   | Export the clock on the REF IN/OUT terminal on the PXIe-5652, the REF OUT terminals on the PXIe-5653, or the REF OUT     |
        |                   | terminal on the PXIe-5694, PXIe-5644/5645/5646, or PXIe-5820/5830/5831/5832/5840/5841/5860.                              |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2) | Export the clock on the REF OUT2 terminal on the PXIe-5652. This value is valid only for the PXIe-5663E.                 |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)   | Export the Reference Clock on the CLK OUT terminal on the Digitizer. This value is not valid for the                     |
        |                   | PXIe-5644/5645/5646 or PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                     |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies a comma-separated list of the terminals at which to export the frequency reference.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_REFERENCE_EXPORTED_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_reference_exported_terminal(self, selector_string, value):
        r"""Sets a comma-separated list of the terminals at which to export the frequency reference.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **None**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | None ()           | The Reference Clock is not exported. This value is not valid for the PXIe-5644/5645/5646.                                |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)   | Export the clock on the REF IN/OUT terminal on the PXIe-5652, the REF OUT terminals on the PXIe-5653, or the REF OUT     |
        |                   | terminal on the PXIe-5694, PXIe-5644/5645/5646, or PXIe-5820/5830/5831/5832/5840/5841/5860.                              |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2) | Export the clock on the REF OUT2 terminal on the PXIe-5652. This value is valid only for the PXIe-5663E.                 |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)   | Export the Reference Clock on the CLK OUT terminal on the Digitizer. This value is not valid for the                     |
        |                   | PXIe-5644/5645/5646 or PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                     |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies a comma-separated list of the terminals at which to export the frequency reference.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.FREQUENCY_REFERENCE_EXPORTED_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rf_attenuation_auto(self, selector_string):
        r"""Gets whether the RFmx driver computes the RF attenuation.

        If you set this attribute to **True**, the RFmx driver chooses an attenuation setting based on the reference
        level configured on the personality.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **True**.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665/5668

        +--------------+-------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                     |
        +==============+=================================================================================================+
        | False (0)    | Specifies that the RFmx driver uses the value configured using RF Attenuation Value             |
        |              | attribute.                                                                                      |
        +--------------+-------------------------------------------------------------------------------------------------+
        | True (1)     | Specifies that the RFmx driver computes the RF attenuation.                                     |
        +--------------+-------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.RFAttenuationAuto):
                Specifies whether the RFmx driver computes the RF attenuation.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.RF_ATTENUATION_AUTO.value
            )
            attr_val = enums.RFAttenuationAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rf_attenuation_auto(self, selector_string, value):
        r"""Sets whether the RFmx driver computes the RF attenuation.

        If you set this attribute to **True**, the RFmx driver chooses an attenuation setting based on the reference
        level configured on the personality.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **True**.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665/5668

        +--------------+-------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                     |
        +==============+=================================================================================================+
        | False (0)    | Specifies that the RFmx driver uses the value configured using RF Attenuation Value             |
        |              | attribute.                                                                                      |
        +--------------+-------------------------------------------------------------------------------------------------+
        | True (1)     | Specifies that the RFmx driver computes the RF attenuation.                                     |
        +--------------+-------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.RFAttenuationAuto, int):
                Specifies whether the RFmx driver computes the RF attenuation.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.RFAttenuationAuto else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.RF_ATTENUATION_AUTO.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rf_attenuation_value(self, selector_string):
        r"""Gets the nominal attenuation setting for all attenuators before the first mixer in the RF signal chain. This value
        is expressed in dB.

        The RFmx driver uses the value of this attribute as the attenuation setting when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.RF_ATTENUATION_AUTO` attribute to **False**.

        +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)             | Description                                                                                                              |
        +==========================+==========================================================================================================================+
        | PXIe-5663/5663E          | You can change the attenuation value to modify the amount of noise and distortion. Higher attenuation levels increase    |
        |                          | the noise level but decreases distortion; lower attenuation levels decrease the noise level but increases distortion.    |
        +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5603/5605/5665/5668 | Refer to the PXIe-5665 or the PXIe-5668 RF Attenuation and Signal Levels topic in the NI RF Vector Signal Analyzers      |
        |                          | Help for more information about configuring attenuation.                                                                 |
        +--------------------------+--------------------------------------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The valid values for this attribute depend on the device configuration.

        **Supported devices**: PXIe-5663/5663E/5603/5605/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the nominal attenuation setting for all attenuators before the first mixer in the RF signal chain. This value
                is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RF_ATTENUATION_VALUE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rf_attenuation_value(self, selector_string, value):
        r"""Sets the nominal attenuation setting for all attenuators before the first mixer in the RF signal chain. This value
        is expressed in dB.

        The RFmx driver uses the value of this attribute as the attenuation setting when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.RF_ATTENUATION_AUTO` attribute to **False**.

        +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)             | Description                                                                                                              |
        +==========================+==========================================================================================================================+
        | PXIe-5663/5663E          | You can change the attenuation value to modify the amount of noise and distortion. Higher attenuation levels increase    |
        |                          | the noise level but decreases distortion; lower attenuation levels decrease the noise level but increases distortion.    |
        +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5603/5605/5665/5668 | Refer to the PXIe-5665 or the PXIe-5668 RF Attenuation and Signal Levels topic in the NI RF Vector Signal Analyzers      |
        |                          | Help for more information about configuring attenuation.                                                                 |
        +--------------------------+--------------------------------------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The valid values for this attribute depend on the device configuration.

        **Supported devices**: PXIe-5663/5663E/5603/5605/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the nominal attenuation setting for all attenuators before the first mixer in the RF signal chain. This value
                is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RF_ATTENUATION_VALUE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_mechanical_attenuation_auto(self, selector_string):
        r"""Gets whether the RFmx driver chooses an attenuation setting based on the hardware settings.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **True**.

        **Supported devices**: PXIe-5663/5663E/5665/5668

        +--------------+---------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                             |
        +==============+=========================================================================================================+
        | False (0)    | Specifies that the RFmx driver uses the value configured in the Mechanical Attenuation Value attribute. |
        +--------------+---------------------------------------------------------------------------------------------------------+
        | True (1)     | Specifies that the measurement computes the mechanical attenuation.                                     |
        +--------------+---------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.MechanicalAttenuationAuto):
                Specifies whether the RFmx driver chooses an attenuation setting based on the hardware settings.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.MECHANICAL_ATTENUATION_AUTO.value
            )
            attr_val = enums.MechanicalAttenuationAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_mechanical_attenuation_auto(self, selector_string, value):
        r"""Sets whether the RFmx driver chooses an attenuation setting based on the hardware settings.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **True**.

        **Supported devices**: PXIe-5663/5663E/5665/5668

        +--------------+---------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                             |
        +==============+=========================================================================================================+
        | False (0)    | Specifies that the RFmx driver uses the value configured in the Mechanical Attenuation Value attribute. |
        +--------------+---------------------------------------------------------------------------------------------------------+
        | True (1)     | Specifies that the measurement computes the mechanical attenuation.                                     |
        +--------------+---------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.MechanicalAttenuationAuto, int):
                Specifies whether the RFmx driver chooses an attenuation setting based on the hardware settings.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.MechanicalAttenuationAuto else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.MECHANICAL_ATTENUATION_AUTO.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_mechanical_attenuation_value(self, selector_string):
        r"""Gets the level of mechanical attenuation for the RF path. This value is expressed in dB.

        The RFmx driver uses the value of this attribute as the attenuation setting when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.MECHANICAL_ATTENUATION_AUTO` attribute to **False**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Valid values**

        +-------------------------------+--------------------------------------------------------------+
        | Name (value)                  | Description                                                  |
        +===============================+==============================================================+
        | PXIe-5663/5663E               | 0, 16                                                        |
        +-------------------------------+--------------------------------------------------------------+
        | PXIe-5665 (3.6 GHz)           | 0, 10, 20, 30                                                |
        +-------------------------------+--------------------------------------------------------------+
        | PXIe-5665 (14 GHz), PXIe-5668 | 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75 |
        +-------------------------------+--------------------------------------------------------------+

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the level of mechanical attenuation for the RF path. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.MECHANICAL_ATTENUATION_VALUE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_mechanical_attenuation_value(self, selector_string, value):
        r"""Sets the level of mechanical attenuation for the RF path. This value is expressed in dB.

        The RFmx driver uses the value of this attribute as the attenuation setting when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.MECHANICAL_ATTENUATION_AUTO` attribute to **False**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Valid values**

        +-------------------------------+--------------------------------------------------------------+
        | Name (value)                  | Description                                                  |
        +===============================+==============================================================+
        | PXIe-5663/5663E               | 0, 16                                                        |
        +-------------------------------+--------------------------------------------------------------+
        | PXIe-5665 (3.6 GHz)           | 0, 10, 20, 30                                                |
        +-------------------------------+--------------------------------------------------------------+
        | PXIe-5665 (14 GHz), PXIe-5668 | 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75 |
        +-------------------------------+--------------------------------------------------------------+

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the level of mechanical attenuation for the RF path. This value is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.MECHANICAL_ATTENUATION_VALUE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_leakage_avoidance_enabled(self, selector_string):
        r"""Gets whether to reduce the effects of the instrument leakage by placing the LO outside the band of acquisition.

        This attribute is ignored if:

        - the bandwidth required by the measurement is more than the available instrument bandwidth after offsetting the LO.

        - you set the :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY` or :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_FREQUENCY_OFFSET` attributes.

        .. note::
           When using a DPD applied signal for performing measurements like ModAcc, PvT, or TXP, you must set this attribute to
           **False** when the :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SOURCE` attribute is set to
           **Automatic_SG_SA_Shared**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value for PXIe-5830/5831/5832/5840/5841/5842 is **True**, else the default value is **False**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | RFmx does not modify the Downconverter Frequency Offset attribute.                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | RFmx calculates the required LO offset based on the measurement configuration and appropriately sets the Downconverter   |
        |              | Frequency Offset attribute.                                                                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LOLeakageAvoidanceEnabled):
                Specifies whether to reduce the effects of the instrument leakage by placing the LO outside the band of acquisition.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_LEAKAGE_AVOIDANCE_ENABLED.value
            )
            attr_val = enums.LOLeakageAvoidanceEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_leakage_avoidance_enabled(self, selector_string, value):
        r"""Sets whether to reduce the effects of the instrument leakage by placing the LO outside the band of acquisition.

        This attribute is ignored if:

        - the bandwidth required by the measurement is more than the available instrument bandwidth after offsetting the LO.

        - you set the :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY` or :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_FREQUENCY_OFFSET` attributes.

        .. note::
           When using a DPD applied signal for performing measurements like ModAcc, PvT, or TXP, you must set this attribute to
           **False** when the :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SOURCE` attribute is set to
           **Automatic_SG_SA_Shared**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value for PXIe-5830/5831/5832/5840/5841/5842 is **True**, else the default value is **False**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | RFmx does not modify the Downconverter Frequency Offset attribute.                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | RFmx calculates the required LO offset based on the measurement configuration and appropriately sets the Downconverter   |
        |              | Frequency Offset attribute.                                                                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LOLeakageAvoidanceEnabled, int):
                Specifies whether to reduce the effects of the instrument leakage by placing the LO outside the band of acquisition.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.LOLeakageAvoidanceEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_LEAKAGE_AVOIDANCE_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_source(self, selector_string):
        r"""Gets the local oscillator (LO) signal source used to downconvert the RF input signal.

        If this attribute is set to "" (empty string), RFmx uses the internal LO source. For PXIe-5830/5831/5832, if
        you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of the selector string. You do not need
        to use a selector string or use "lo1, lo2" as part of the selector string if you want to configure this attribute for
        both channels. You can also use :py:meth:`build_lo_string` utility function to create the LO String. For all other
        devices, lo channel string is not allowed.

        If no signal downconversion is required, this attribute is ignored.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Onboard**.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                                    | Description                                                                                                              |
        +=================================================+==========================================================================================================================+
        | None (None)                                     | Specifies that no LO source is required to downconvert the RF input signal.                                              |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Onboard (Onboard)                               | Specifies that the onboard synthesizer is used to generate the LO signal that downconverts the RF input signal.          |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | LO_In (LO_In)                                   | Specifies that the LO source used to downconvert the RF input signal is connected to the LO IN connector on the front    |
        |                                                 | panel.                                                                                                                   |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Secondary (Secondary)                           | Specifies that the LO source uses the PXIe-5830/5831/5832/5840 internal LO. This value is valid on only the PXIe-5840    |
        |                                                 | with PXIe-5653, PXIe-5831 with PXIe-5653 (LO1 stage only), or PXIe-5832 with PXIe-5653 (LO1 stage only).                 |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | SG_SA_Shared (SG_SA_Shared)                     | Specifies that the internal LO can be shared between RFmx and RFSG sessions. RFmx selects an internal synthesizer and    |
        |                                                 | the synthesizer signal is switched to both the RX and TX mixers. This value is valid only on                             |
        |                                                 | PXIe-5830/5831/5832/5841/5842.                                                                                           |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Automatic_SG_SA_Shared (Automatic_SG_SA_Shared) | Specifies whether RFmx automatically configures the signal analyzer to use the LO utilized by the signal generator on    |
        |                                                 | the same vector signal transceiver (VST) based on the configured measurements.                                           |
        |                                                 | When using instruments that do not have LOs with excellent phase noise and to minimize the contribution of the           |
        |                                                 | instrument's phase noise affecting your measurements, NI recommends to share the LO between the signal generator (SG)    |
        |                                                 | and the signal analyzer (SA).                                                                                            |
        |                                                 | This value is recommended in test setups that use a VST with NI-RFSG to generate a signal at the DUT's input and RFmx    |
        |                                                 | to measure the signal at the DUT's output.                                                                               |
        |                                                 | This value automatically:                                                                                                |
        |                                                 | determines whether the SG LO can be shared with SA based on the test instrument used, selected measurement, and the      |
        |                                                 | measurement settings.                                                                                                    |
        |                                                 | configures instrument specific attributes on SA to share the LO between the generator and analyzer, whenever possible.   |
        |                                                 | To enable automatically sharing SG LO with SA, you must first setup the required device specific physical connections    |
        |                                                 | mentioned below and then follow the steps in the recommended order.                                                      |
        |                                                 | PXIe-5840/5841/5842: SG LO is shared with SA via an external path. Hence, you must connect RF Out LO Out to RF In LO In  |
        |                                                 | using a cable.                                                                                                           |
        |                                                 | PXIe-5830/5831/5832: SG LO is shared with SA via an internal path. Hence, an external cable connection is not required.  |
        |                                                 | NI recommends the following order of steps:                                                                              |
        |                                                 | Set LO Source attribute to Automatic SG SA Shared in NI-RFSG (or enable Automatic SG SA shared LO on NI-RFSG Playback    |
        |                                                 | Library).                                                                                                                |
        |                                                 | Set LO Source attribute to Automatic_SG_SA_Shared in RFmx.                                                               |
        |                                                 | Configure any additional settings on RFSG and RFmx, including selecting waveforms.                                       |
        |                                                 | Initiate RFSG.                                                                                                           |
        |                                                 | Initiate RFmx.                                                                                                           |
        |                                                 | When using a DPD applied signal for performing measurements like ModAcc, PvT, or TXP, you must set the LO Leakage        |
        |                                                 | Avoidance Enabled attribute to False and LO Source attribute to Automatic_SG_SA_Shared.                                  |
        |                                                 | Refer to following methods for examples in RFmx WLAN and RFmx NR that show the behavior of Automatic SG SA Shared LO.    |
        |                                                 | <LabVIEW directory>\examples\RFmx\WLAN\RFmxWLAN FEM Test with Automatic SG SA Shared LO.vi                               |
        |                                                 | <LabVIEW directory>\examples\RFmx\NR\RFmxNR FEM Test with Automatic SG SA Shared LO.vi                                   |
        |                                                 | This value is valid only on PXIe-5830/5831/5832/5840/5841/5842.                                                          |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the local oscillator (LO) signal source used to downconvert the RF input signal.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.LO_SOURCE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_source(self, selector_string, value):
        r"""Sets the local oscillator (LO) signal source used to downconvert the RF input signal.

        If this attribute is set to "" (empty string), RFmx uses the internal LO source. For PXIe-5830/5831/5832, if
        you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of the selector string. You do not need
        to use a selector string or use "lo1, lo2" as part of the selector string if you want to configure this attribute for
        both channels. You can also use :py:meth:`build_lo_string` utility function to create the LO String. For all other
        devices, lo channel string is not allowed.

        If no signal downconversion is required, this attribute is ignored.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Onboard**.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                                    | Description                                                                                                              |
        +=================================================+==========================================================================================================================+
        | None (None)                                     | Specifies that no LO source is required to downconvert the RF input signal.                                              |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Onboard (Onboard)                               | Specifies that the onboard synthesizer is used to generate the LO signal that downconverts the RF input signal.          |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | LO_In (LO_In)                                   | Specifies that the LO source used to downconvert the RF input signal is connected to the LO IN connector on the front    |
        |                                                 | panel.                                                                                                                   |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Secondary (Secondary)                           | Specifies that the LO source uses the PXIe-5830/5831/5832/5840 internal LO. This value is valid on only the PXIe-5840    |
        |                                                 | with PXIe-5653, PXIe-5831 with PXIe-5653 (LO1 stage only), or PXIe-5832 with PXIe-5653 (LO1 stage only).                 |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | SG_SA_Shared (SG_SA_Shared)                     | Specifies that the internal LO can be shared between RFmx and RFSG sessions. RFmx selects an internal synthesizer and    |
        |                                                 | the synthesizer signal is switched to both the RX and TX mixers. This value is valid only on                             |
        |                                                 | PXIe-5830/5831/5832/5841/5842.                                                                                           |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Automatic_SG_SA_Shared (Automatic_SG_SA_Shared) | Specifies whether RFmx automatically configures the signal analyzer to use the LO utilized by the signal generator on    |
        |                                                 | the same vector signal transceiver (VST) based on the configured measurements.                                           |
        |                                                 | When using instruments that do not have LOs with excellent phase noise and to minimize the contribution of the           |
        |                                                 | instrument's phase noise affecting your measurements, NI recommends to share the LO between the signal generator (SG)    |
        |                                                 | and the signal analyzer (SA).                                                                                            |
        |                                                 | This value is recommended in test setups that use a VST with NI-RFSG to generate a signal at the DUT's input and RFmx    |
        |                                                 | to measure the signal at the DUT's output.                                                                               |
        |                                                 | This value automatically:                                                                                                |
        |                                                 | determines whether the SG LO can be shared with SA based on the test instrument used, selected measurement, and the      |
        |                                                 | measurement settings.                                                                                                    |
        |                                                 | configures instrument specific attributes on SA to share the LO between the generator and analyzer, whenever possible.   |
        |                                                 | To enable automatically sharing SG LO with SA, you must first setup the required device specific physical connections    |
        |                                                 | mentioned below and then follow the steps in the recommended order.                                                      |
        |                                                 | PXIe-5840/5841/5842: SG LO is shared with SA via an external path. Hence, you must connect RF Out LO Out to RF In LO In  |
        |                                                 | using a cable.                                                                                                           |
        |                                                 | PXIe-5830/5831/5832: SG LO is shared with SA via an internal path. Hence, an external cable connection is not required.  |
        |                                                 | NI recommends the following order of steps:                                                                              |
        |                                                 | Set LO Source attribute to Automatic SG SA Shared in NI-RFSG (or enable Automatic SG SA shared LO on NI-RFSG Playback    |
        |                                                 | Library).                                                                                                                |
        |                                                 | Set LO Source attribute to Automatic_SG_SA_Shared in RFmx.                                                               |
        |                                                 | Configure any additional settings on RFSG and RFmx, including selecting waveforms.                                       |
        |                                                 | Initiate RFSG.                                                                                                           |
        |                                                 | Initiate RFmx.                                                                                                           |
        |                                                 | When using a DPD applied signal for performing measurements like ModAcc, PvT, or TXP, you must set the LO Leakage        |
        |                                                 | Avoidance Enabled attribute to False and LO Source attribute to Automatic_SG_SA_Shared.                                  |
        |                                                 | Refer to following methods for examples in RFmx WLAN and RFmx NR that show the behavior of Automatic SG SA Shared LO.    |
        |                                                 | <LabVIEW directory>\examples\RFmx\WLAN\RFmxWLAN FEM Test with Automatic SG SA Shared LO.vi                               |
        |                                                 | <LabVIEW directory>\examples\RFmx\NR\RFmxNR FEM Test with Automatic SG SA Shared LO.vi                                   |
        |                                                 | This value is valid only on PXIe-5830/5831/5832/5840/5841/5842.                                                          |
        +-------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the local oscillator (LO) signal source used to downconvert the RF input signal.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.LO_SOURCE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_frequency(self, selector_string):
        r"""Gets the LO signal frequency for the configured center frequency. This value is expressed in Hz.

        If you are using the vector signal analyzer with an external LO, use this attribute to specify the LO frequency
        that the external LO source passes into the LO IN or LO1 IN connector on the RF downconverter front panel. If you are
        using an external LO, reading the value of this attribute after configuring the rest of the parameters returns the LO
        frequency needed by the device.

        You can set this attribute to the actual LO frequency because RFmx corrects for any difference between expected
        and actual LO frequencies.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        Selector Strings topic for information about the string syntax.

        The default value is 0.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the LO signal frequency for the configured center frequency. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_frequency(self, selector_string, value):
        r"""Sets the LO signal frequency for the configured center frequency. This value is expressed in Hz.

        If you are using the vector signal analyzer with an external LO, use this attribute to specify the LO frequency
        that the external LO source passes into the LO IN or LO1 IN connector on the RF downconverter front panel. If you are
        using an external LO, reading the value of this attribute after configuring the rest of the parameters returns the LO
        frequency needed by the device.

        You can set this attribute to the actual LO frequency because RFmx corrects for any difference between expected
        and actual LO frequencies.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        Selector Strings topic for information about the string syntax.

        The default value is 0.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the LO signal frequency for the configured center frequency. This value is expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_export_enabled(self, selector_string):
        r"""Gets whether to enable the LO OUT terminals on the installed devices.

        +--------------+-------------------------------+
        | Name (value) | Description                   |
        +==============+===============================+
        | TRUE         | Enables the LO OUT terminals. |
        +--------------+-------------------------------+
        | FALSE        | Disables the LO OUT terminals |
        +--------------+-------------------------------+

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default value**:

        - PXIe-5663/5663E: TRUE

        - PXIe-5644/5645/5646, PXIe-5665/5668, PXIe-5830/5831/5832/5840/5841/5842: FALSE

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable the LO OUT terminals on the installed devices.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_EXPORT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_export_enabled(self, selector_string, value):
        r"""Sets whether to enable the LO OUT terminals on the installed devices.

        +--------------+-------------------------------+
        | Name (value) | Description                   |
        +==============+===============================+
        | TRUE         | Enables the LO OUT terminals. |
        +--------------+-------------------------------+
        | FALSE        | Disables the LO OUT terminals |
        +--------------+-------------------------------+

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default value**:

        - PXIe-5663/5663E: TRUE

        - PXIe-5644/5645/5646, PXIe-5665/5668, PXIe-5830/5831/5832/5840/5841/5842: FALSE

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the LO OUT terminals on the installed devices.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_EXPORT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo2_export_enabled(self, selector_string):
        r"""Gets whether to enable the LO2 OUT terminals in the installed devices.

        Set this attribute to **Enabled** to export the 4 GHz LO signal from the LO2 IN terminal to the LO2 OUT
        terminal. You can also export the LO2 signal by setting the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_EXPORT_ENABLED` attribute to TRUE.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported Devices:** PXIe-5665/5668

        +--------------+---------------------------------+
        | Name (Value) | Description                     |
        +==============+=================================+
        | Disabled (0) | Disables the LO2 OUT terminals. |
        +--------------+---------------------------------+
        | Enabled (1)  | Enables the LO2 OUT terminals.  |
        +--------------+---------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LO2ExportEnabled):
                Specifies whether to enable the LO2 OUT terminals in the installed devices.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO2_EXPORT_ENABLED.value
            )
            attr_val = enums.LO2ExportEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo2_export_enabled(self, selector_string, value):
        r"""Sets whether to enable the LO2 OUT terminals in the installed devices.

        Set this attribute to **Enabled** to export the 4 GHz LO signal from the LO2 IN terminal to the LO2 OUT
        terminal. You can also export the LO2 signal by setting the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_EXPORT_ENABLED` attribute to TRUE.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported Devices:** PXIe-5665/5668

        +--------------+---------------------------------+
        | Name (Value) | Description                     |
        +==============+=================================+
        | Disabled (0) | Disables the LO2 OUT terminals. |
        +--------------+---------------------------------+
        | Enabled (1)  | Enables the LO2 OUT terminals.  |
        +--------------+---------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LO2ExportEnabled, int):
                Specifies whether to enable the LO2 OUT terminals in the installed devices.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.LO2ExportEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO2_EXPORT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_in_power(self, selector_string):
        r"""Gets the power level expected at the LO IN terminal when the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SOURCE` attribute is set to **LO_In**. This value is expressed in dBm.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           For PXIe-5644/5645/5646, this attribute is always read-only.

        The default value is 0.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the power level expected at the LO IN terminal when the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SOURCE` attribute is set to **LO_In**. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_IN_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_in_power(self, selector_string, value):
        r"""Sets the power level expected at the LO IN terminal when the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SOURCE` attribute is set to **LO_In**. This value is expressed in dBm.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           For PXIe-5644/5645/5646, this attribute is always read-only.

        The default value is 0.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the power level expected at the LO IN terminal when the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SOURCE` attribute is set to **LO_In**. This value is expressed in dBm.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_IN_POWER.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_out_power(self, selector_string):
        r"""Gets the power level of the signal at the LO OUT terminal when the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_EXPORT_ENABLED` attribute is set to TRUE. This value is expressed in
        dBm.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the power level of the signal at the LO OUT terminal when the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_EXPORT_ENABLED` attribute is set to TRUE. This value is expressed in
                dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_OUT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_out_power(self, selector_string, value):
        r"""Sets the power level of the signal at the LO OUT terminal when the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_EXPORT_ENABLED` attribute is set to TRUE. This value is expressed in
        dBm.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the power level of the signal at the LO OUT terminal when the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_EXPORT_ENABLED` attribute is set to TRUE. This value is expressed in
                dBm.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_OUT_POWER.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_tuning_speed(self, selector_string):
        r"""Makes tradeoffs between tuning speed and phase noise.

        .. note::
           This attribute is not supported if you are using an external LO.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           The PXIe-5830/5831/5832/5840/5841/5842 supports only **Medium** for this attribute.

        **Default value**: **Normal** for PXIe-5663/5663E/5665/5668,  **Medium** for PXIe-5644/5645/5646 and
        PXIe-5830/5831/5832/5840/5841/5842

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Normal (0)   | PXIe-5665/5668: Adjusts the YIG main coil on the LO for an underdamped response.                                         |
        |              | PXIe-5663/5663E/5644/5645/5646: Specifies that the RF downconverter module uses a narrow loop bandwidth.                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Medium (1)   | Specifies that the RF downconverter module uses a medium loop bandwidth. This value is not supported on                  |
        |              | PXIe-5663/5663E/5665/5668 devices.                                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Fast (2)     | PXIe-5665/5668: Adjusts the YIG main coil on the LO for an overdamped response. Setting this attribute to Fast allows    |
        |              | the frequency to settle significantly faster for some frequency transitions at the expense of increased phase noise.     |
        |              | PXIe-5663/5663E/5644/5645/5646: Specifies that the RF downconverter module uses a wide loop bandwidth.                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TuningSpeed):
                Makes tradeoffs between tuning speed and phase noise.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.TUNING_SPEED.value
            )
            attr_val = enums.TuningSpeed(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_tuning_speed(self, selector_string, value):
        r"""Makes tradeoffs between tuning speed and phase noise.

        .. note::
           This attribute is not supported if you are using an external LO.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           The PXIe-5830/5831/5832/5840/5841/5842 supports only **Medium** for this attribute.

        **Default value**: **Normal** for PXIe-5663/5663E/5665/5668,  **Medium** for PXIe-5644/5645/5646 and
        PXIe-5830/5831/5832/5840/5841/5842

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Normal (0)   | PXIe-5665/5668: Adjusts the YIG main coil on the LO for an underdamped response.                                         |
        |              | PXIe-5663/5663E/5644/5645/5646: Specifies that the RF downconverter module uses a narrow loop bandwidth.                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Medium (1)   | Specifies that the RF downconverter module uses a medium loop bandwidth. This value is not supported on                  |
        |              | PXIe-5663/5663E/5665/5668 devices.                                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Fast (2)     | PXIe-5665/5668: Adjusts the YIG main coil on the LO for an overdamped response. Setting this attribute to Fast allows    |
        |              | the frequency to settle significantly faster for some frequency transitions at the expense of increased phase noise.     |
        |              | PXIe-5663/5663E/5644/5645/5646: Specifies that the RF downconverter module uses a wide loop bandwidth.                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TuningSpeed, int):
                Makes tradeoffs between tuning speed and phase noise.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.TuningSpeed else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.TUNING_SPEED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_downconverter_frequency_offset(self, selector_string):
        r"""Gets an offset from the center frequency value for the downconverter. Use this attribute to offset the measurement
        away from the LO leakage or DC Offset of analyzers that use a direct conversion architecture.  You must set this
        attribute to half the bandwidth or span of the measurement + guardband. The guardband is needed to ensure that the LO
        leakage is not inside the analog or digital filter rolloffs.  This value is expressed in Hz.

        NI recommends using the :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_LEAKAGE_AVOIDANCE_ENABLED` attribute
        instead of the Downconverter Frequency Offset attribute. The LO Leakage Avoidance Enabled attribute automatically
        configures the Downconverter Frequency Offset attribute to an appropriate offset based on the bandwidth or span of the
        measurement.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values:** For spectrum acquisition types, the RFmx driver automatically calculates the default value
        to avoid residual LO power. For I/Q acquisition types, the default value is 0 Hz. If the center frequency is set to a
        non-multiple of :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_FREQUENCY_STEP_SIZE` attribute, this attribute is set
        to compensate for the difference.

        The following valid values correspond to their respective devices:

        +-------------------------------+----------------------+
        | Name (value)                  | Description          |
        +===============================+======================+
        | PXIe-5646                     | -100 MHz to +100 MHz |
        +-------------------------------+----------------------+
        | PXIe-5830/5831/5832/5840/5841 | -500 MHz to +500 MHz |
        +-------------------------------+----------------------+
        | PXIe-5842                     | -1 GHz to +1 GHz     |
        +-------------------------------+----------------------+
        | Other devices                 | -42 MHz to +42 MHz   |
        +-------------------------------+----------------------+

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an offset from the center frequency value for the downconverter. Use this attribute to offset the measurement
                away from the LO leakage or DC Offset of analyzers that use a direct conversion architecture.  You must set this
                attribute to half the bandwidth or span of the measurement + guardband. The guardband is needed to ensure that the LO
                leakage is not inside the analog or digital filter rolloffs.  This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DOWNCONVERTER_FREQUENCY_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_downconverter_frequency_offset(self, selector_string, value):
        r"""Sets an offset from the center frequency value for the downconverter. Use this attribute to offset the measurement
        away from the LO leakage or DC Offset of analyzers that use a direct conversion architecture.  You must set this
        attribute to half the bandwidth or span of the measurement + guardband. The guardband is needed to ensure that the LO
        leakage is not inside the analog or digital filter rolloffs.  This value is expressed in Hz.

        NI recommends using the :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_LEAKAGE_AVOIDANCE_ENABLED` attribute
        instead of the Downconverter Frequency Offset attribute. The LO Leakage Avoidance Enabled attribute automatically
        configures the Downconverter Frequency Offset attribute to an appropriate offset based on the bandwidth or span of the
        measurement.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values:** For spectrum acquisition types, the RFmx driver automatically calculates the default value
        to avoid residual LO power. For I/Q acquisition types, the default value is 0 Hz. If the center frequency is set to a
        non-multiple of :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_FREQUENCY_STEP_SIZE` attribute, this attribute is set
        to compensate for the difference.

        The following valid values correspond to their respective devices:

        +-------------------------------+----------------------+
        | Name (value)                  | Description          |
        +===============================+======================+
        | PXIe-5646                     | -100 MHz to +100 MHz |
        +-------------------------------+----------------------+
        | PXIe-5830/5831/5832/5840/5841 | -500 MHz to +500 MHz |
        +-------------------------------+----------------------+
        | PXIe-5842                     | -1 GHz to +1 GHz     |
        +-------------------------------+----------------------+
        | Other devices                 | -42 MHz to +42 MHz   |
        +-------------------------------+----------------------+

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an offset from the center frequency value for the downconverter. Use this attribute to offset the measurement
                away from the LO leakage or DC Offset of analyzers that use a direct conversion architecture.  You must set this
                attribute to half the bandwidth or span of the measurement + guardband. The guardband is needed to ensure that the LO
                leakage is not inside the analog or digital filter rolloffs.  This value is expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DOWNCONVERTER_FREQUENCY_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_downconverter_center_frequency(self, selector_string):
        r"""Enables in-band retuning and specifies the current frequency of the RF downconverter. This value is expressed in Hz.

        After you set this attribute, the RF downconverter is locked to that frequency until the value is changed or
        the attribute is reset. Locking the downconverter to a fixed value allows frequencies within the instantaneous
        bandwidth of the downconverter to be measured without the overhead of retuning the LO and waiting for the LO to settle.
        This method is called in-band retuning and it has the highest benefit on analyzers that have larger LO settling times.
        After setting the downconverter center frequency, you can set the center frequency to the frequencies at which you
        want to take the measurements.

        If you want to avoid the LO leakage or DC offset of analyzers that use a direct conversion architecture, it is
        more convenient to use the :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_FREQUENCY_OFFSET` or
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_LEAKAGE_AVOIDANCE_ENABLED` attributes.

        If you set this attribute, any measurements outside the instantaneous bandwidth of the device are invalid. To
        disable in-band retuning, reset this attribute or call the :py:meth:`reset_to_default` method.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is the carrier frequency or spectrum center frequency.

        Valid Values: Any supported tuning frequency of the device.

        .. note::
           PXIe-5820: The only valid value for this attribute is 0 Hz.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Enables in-band retuning and specifies the current frequency of the RF downconverter. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_downconverter_center_frequency(self, selector_string, value):
        r"""Enables in-band retuning and specifies the current frequency of the RF downconverter. This value is expressed in Hz.

        After you set this attribute, the RF downconverter is locked to that frequency until the value is changed or
        the attribute is reset. Locking the downconverter to a fixed value allows frequencies within the instantaneous
        bandwidth of the downconverter to be measured without the overhead of retuning the LO and waiting for the LO to settle.
        This method is called in-band retuning and it has the highest benefit on analyzers that have larger LO settling times.
        After setting the downconverter center frequency, you can set the center frequency to the frequencies at which you
        want to take the measurements.

        If you want to avoid the LO leakage or DC offset of analyzers that use a direct conversion architecture, it is
        more convenient to use the :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_FREQUENCY_OFFSET` or
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_LEAKAGE_AVOIDANCE_ENABLED` attributes.

        If you set this attribute, any measurements outside the instantaneous bandwidth of the device are invalid. To
        disable in-band retuning, reset this attribute or call the :py:meth:`reset_to_default` method.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is the carrier frequency or spectrum center frequency.

        Valid Values: Any supported tuning frequency of the device.

        .. note::
           PXIe-5820: The only valid value for this attribute is 0 Hz.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Enables in-band retuning and specifies the current frequency of the RF downconverter. This value is expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_injection_side(self, selector_string):
        r"""Gets the LO injection side.

        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)        | Description                                                                                                              |
        +=====================+==========================================================================================================================+
        | PXIe-5663/5663E     | For frequencies below 517.5 MHz or above 6.4125 GHz, the LO injection side is fixed, and the RFmx driver returns an      |
        |                     | error if you specify an incorrect value. If you do not configure this attribute, the RFmx driver selects the default LO  |
        |                     | injection side based on the downconverter center frequency. Reset this attribute to return to automatic behavior.        |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5665 (3.6 GHz) | Setting this attribute to Low Side is not supported for this device.                                                     |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5665 (14 GHz)  | Setting this attribute to Low Side is supported for this device for frequencies greater than 4 GHz, but this             |
        |                     | configuration is not calibrated, and device specifications are not guaranteed.                                           |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5668           | Setting this attribute to Low Side is supported for some frequencies in high band, varying by the final IF frequency.    |
        |                     | This configuration is not calibrated and device specifications are not guaranteed.                                       |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        ** Default value:**

        - PXIe-5663/5663E (frequencies < 3.0 GHz): **High Side**

        - PXIe-5663/5663E (frequencies >=  3.0 GHz): **Low Side**

        - PXIe-5665/5668: **High Side**

        **Supported devices**: PXIe-5663/5663E/5665/5668

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | High Side (0) | Configures the LO signal that the device generates at a frequency higher than the RF signal. This LO frequency is given  |
        |               | by the following formula: fLO = fRF + fIF                                                                                |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Low Side (1)  | Configures the LO signal that the device generates at a frequency lower than the RF signal. This LO frequency is given   |
        |               | by the following formula: fLO = fRF – fIF                                                                                |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LOInjectionSide):
                Specifies the LO injection side.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_INJECTION_SIDE.value
            )
            attr_val = enums.LOInjectionSide(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_injection_side(self, selector_string, value):
        r"""Sets the LO injection side.

        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)        | Description                                                                                                              |
        +=====================+==========================================================================================================================+
        | PXIe-5663/5663E     | For frequencies below 517.5 MHz or above 6.4125 GHz, the LO injection side is fixed, and the RFmx driver returns an      |
        |                     | error if you specify an incorrect value. If you do not configure this attribute, the RFmx driver selects the default LO  |
        |                     | injection side based on the downconverter center frequency. Reset this attribute to return to automatic behavior.        |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5665 (3.6 GHz) | Setting this attribute to Low Side is not supported for this device.                                                     |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5665 (14 GHz)  | Setting this attribute to Low Side is supported for this device for frequencies greater than 4 GHz, but this             |
        |                     | configuration is not calibrated, and device specifications are not guaranteed.                                           |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5668           | Setting this attribute to Low Side is supported for some frequencies in high band, varying by the final IF frequency.    |
        |                     | This configuration is not calibrated and device specifications are not guaranteed.                                       |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        ** Default value:**

        - PXIe-5663/5663E (frequencies < 3.0 GHz): **High Side**

        - PXIe-5663/5663E (frequencies >=  3.0 GHz): **Low Side**

        - PXIe-5665/5668: **High Side**

        **Supported devices**: PXIe-5663/5663E/5665/5668

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | High Side (0) | Configures the LO signal that the device generates at a frequency higher than the RF signal. This LO frequency is given  |
        |               | by the following formula: fLO = fRF + fIF                                                                                |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Low Side (1)  | Configures the LO signal that the device generates at a frequency lower than the RF signal. This LO frequency is given   |
        |               | by the following formula: fLO = fRF – fIF                                                                                |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LOInjectionSide, int):
                Specifies the LO injection side.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.LOInjectionSide else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_INJECTION_SIDE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_frequency_step_size(self, selector_string):
        r"""Gets the step size for tuning the LO phase-locked loop (PLL).

        You can only tune the LO frequency in multiples of the LO Frequency Step Size attribute. Therefore, the LO
        frequency can be offset from the requested center frequency by as much as half of the LO Frequency Step Size attribute.
        This offset is corrected by digitally frequency shifting the LO frequency to the value requested in
        :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY` attribute.

        .. note::
           For PXIe-5831 with PXIe-5653, PXIe-5832 with PXIe-5653, this attribute is ignored if PXIe-5653 is used as the LO
           source.

        The valid values for this attribute depend on the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_PLL_FRACTIONAL_MODE` attribute.

        **PXIe-5644/5645/5646:** If you set the LO PLL Fractional Mode attribute to **Disabled**, the specified value
        is coerced to the nearest valid value.

        **PXIe-5840:** If you set the LO PLL Fractional Mode attribute to **Disabled**, the specified value is coerced
        to the nearest valid value that is less than or equal to the desired step size.

        +-------------------------------------------------+----------------------------------------------------------------+-----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------------------------+--------------------------------------------------------------------------------------+
        | LO PLL Fractional Mode Enabled Property Setting | LO Frequency Step Size Property Valid Values on PXIe-5644/5645 | LO Frequency Step Size Property Valid Values on PXIe-5646 | LO Frequency Step Size Property Valid Values on PXIe-5840/5841 | LO Frequency Step Size Property Valid Values on PXIe-5830/5831/5832 | LO Frequency Step Size Property Valid Values on PXIe-5841 with PXIe-5655, PXIe-5842* |
        +=================================================+================================================================+===========================================================+================================================================+=====================================================================+======================================================================================+
        | Enabled                                         | 50 kHz to 24 MHz                                               | 50 kHz to 25 MHz                                          | 50 kHz to 100 MHz                                              | LO1: 8 Hz to 400 MHz  LO2: 4 kHz to 400 MHz                         | 1 nHz to 50 MHz                                                                      |
        +-------------------------------------------------+----------------------------------------------------------------+-----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------------------------+--------------------------------------------------------------------------------------+
        | Disabled                                        | 4 MHz, 5 MHz, 6 MHz, 12 MHz, 24 MHz                            | 2 MHz, 5 MHz, 10 MHz, 25 MHz                              | 1 MHz, 5 MHz, 10 MHz, 25 MHz, 50 MHz, 100 MHz                  | LO1: --  LO2: --                                                    | 1 nHz to 50 MHz                                                                      |
        +-------------------------------------------------+----------------------------------------------------------------+-----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------------------------+--------------------------------------------------------------------------------------+

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values**

        +--------------------------+--------------+
        | Name (value)             | Description  |
        +==========================+==============+
        | PXIe-5644/5645/5646      | 200 kHz      |
        +--------------------------+--------------+
        | PXIe-5830                | 2 MHz        |
        +--------------------------+--------------+
        | PXIe-5831/5832 (RF port) | 8 MHz        |
        +--------------------------+--------------+
        | PXIe-5831/5832 (IF port) | 2 MHz, 4 MHz |
        +--------------------------+--------------+
        | PXIe-5840/5841           | 500 kHz      |
        +--------------------------+--------------+
        | PXIe-5842                | 1 Hz         |
        +--------------------------+--------------+

        .. note::
           The default value for PXIe-5831/5832 depends on the frequency range of the selected port for your instrument
           configuration. Use :py:meth:`get_available_ports` method to get the valid port names.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the step size for tuning the LO phase-locked loop (PLL).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_FREQUENCY_STEP_SIZE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_frequency_step_size(self, selector_string, value):
        r"""Sets the step size for tuning the LO phase-locked loop (PLL).

        You can only tune the LO frequency in multiples of the LO Frequency Step Size attribute. Therefore, the LO
        frequency can be offset from the requested center frequency by as much as half of the LO Frequency Step Size attribute.
        This offset is corrected by digitally frequency shifting the LO frequency to the value requested in
        :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY` attribute.

        .. note::
           For PXIe-5831 with PXIe-5653, PXIe-5832 with PXIe-5653, this attribute is ignored if PXIe-5653 is used as the LO
           source.

        The valid values for this attribute depend on the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_PLL_FRACTIONAL_MODE` attribute.

        **PXIe-5644/5645/5646:** If you set the LO PLL Fractional Mode attribute to **Disabled**, the specified value
        is coerced to the nearest valid value.

        **PXIe-5840:** If you set the LO PLL Fractional Mode attribute to **Disabled**, the specified value is coerced
        to the nearest valid value that is less than or equal to the desired step size.

        +-------------------------------------------------+----------------------------------------------------------------+-----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------------------------+--------------------------------------------------------------------------------------+
        | LO PLL Fractional Mode Enabled Property Setting | LO Frequency Step Size Property Valid Values on PXIe-5644/5645 | LO Frequency Step Size Property Valid Values on PXIe-5646 | LO Frequency Step Size Property Valid Values on PXIe-5840/5841 | LO Frequency Step Size Property Valid Values on PXIe-5830/5831/5832 | LO Frequency Step Size Property Valid Values on PXIe-5841 with PXIe-5655, PXIe-5842* |
        +=================================================+================================================================+===========================================================+================================================================+=====================================================================+======================================================================================+
        | Enabled                                         | 50 kHz to 24 MHz                                               | 50 kHz to 25 MHz                                          | 50 kHz to 100 MHz                                              | LO1: 8 Hz to 400 MHz  LO2: 4 kHz to 400 MHz                         | 1 nHz to 50 MHz                                                                      |
        +-------------------------------------------------+----------------------------------------------------------------+-----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------------------------+--------------------------------------------------------------------------------------+
        | Disabled                                        | 4 MHz, 5 MHz, 6 MHz, 12 MHz, 24 MHz                            | 2 MHz, 5 MHz, 10 MHz, 25 MHz                              | 1 MHz, 5 MHz, 10 MHz, 25 MHz, 50 MHz, 100 MHz                  | LO1: --  LO2: --                                                    | 1 nHz to 50 MHz                                                                      |
        +-------------------------------------------------+----------------------------------------------------------------+-----------------------------------------------------------+----------------------------------------------------------------+---------------------------------------------------------------------+--------------------------------------------------------------------------------------+

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values**

        +--------------------------+--------------+
        | Name (value)             | Description  |
        +==========================+==============+
        | PXIe-5644/5645/5646      | 200 kHz      |
        +--------------------------+--------------+
        | PXIe-5830                | 2 MHz        |
        +--------------------------+--------------+
        | PXIe-5831/5832 (RF port) | 8 MHz        |
        +--------------------------+--------------+
        | PXIe-5831/5832 (IF port) | 2 MHz, 4 MHz |
        +--------------------------+--------------+
        | PXIe-5840/5841           | 500 kHz      |
        +--------------------------+--------------+
        | PXIe-5842                | 1 Hz         |
        +--------------------------+--------------+

        .. note::
           The default value for PXIe-5831/5832 depends on the frequency range of the selected port for your instrument
           configuration. Use :py:meth:`get_available_ports` method to get the valid port names.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the step size for tuning the LO phase-locked loop (PLL).

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_FREQUENCY_STEP_SIZE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_vco_frequency_step_size(self, selector_string):
        r"""Gets the step size for tuning the internal voltage-controlled oscillator (VCO) used to generate the LO signal. The
        valid values for LO1 include 1 Hz to 50 MHz and for LO2 include 1 Hz to 100 MHz.

        .. note::
           Do not set this attribute with the :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_FREQUENCY_STEP_SIZE` attribute.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 1 MHz.

        **Supported devices**: PXIe-5830/5831/5832

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the step size for tuning the internal voltage-controlled oscillator (VCO) used to generate the LO signal. The
                valid values for LO1 include 1 Hz to 50 MHz and for LO2 include 1 Hz to 100 MHz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_VCO_FREQUENCY_STEP_SIZE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_vco_frequency_step_size(self, selector_string, value):
        r"""Sets the step size for tuning the internal voltage-controlled oscillator (VCO) used to generate the LO signal. The
        valid values for LO1 include 1 Hz to 50 MHz and for LO2 include 1 Hz to 100 MHz.

        .. note::
           Do not set this attribute with the :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_FREQUENCY_STEP_SIZE` attribute.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 1 MHz.

        **Supported devices**: PXIe-5830/5831/5832

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the step size for tuning the internal voltage-controlled oscillator (VCO) used to generate the LO signal. The
                valid values for LO1 include 1 Hz to 50 MHz and for LO2 include 1 Hz to 100 MHz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_VCO_FREQUENCY_STEP_SIZE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_pll_fractional_mode(self, selector_string):
        r"""Gets whether to use fractional mode for the LO phase-locked loop (PLL).

        Fractional mode provides a finer frequency step resolution, but may result in non harmonic spurs. Refer to the
        specifications document of your device for more information about fractional mode and non harmonic spurs.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           The LO PLL Fractional Mode attribute is applicable only when using the internal LO.

        .. note::
           For PXIe-5831 with PXIe-5653, PXIe-5832 with PXIe-5653, this attribute is ignored if the PXIe-5653 is used as the LO
           source.

        The default value is **Enabled**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+-------------------------------------------+
        | Name (Value) | Description                               |
        +==============+===========================================+
        | Disabled (0) | Indicates that the attribute is disabled. |
        +--------------+-------------------------------------------+
        | Enabled (1)  | Indicates that the attribute is enabled.  |
        +--------------+-------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LOPllFractionalMode):
                Specifies whether to use fractional mode for the LO phase-locked loop (PLL).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_PLL_FRACTIONAL_MODE.value
            )
            attr_val = enums.LOPllFractionalMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_pll_fractional_mode(self, selector_string, value):
        r"""Sets whether to use fractional mode for the LO phase-locked loop (PLL).

        Fractional mode provides a finer frequency step resolution, but may result in non harmonic spurs. Refer to the
        specifications document of your device for more information about fractional mode and non harmonic spurs.

        For PXIe-5830/5831/5832, if you want to configure or read on LO1 or LO2 channel, use "lo1" or "lo2" as part of
        the selector string. You do not need to use a selector string or use "lo1, lo2" as part of the selector string if you
        want to configure this attribute for both channels. You can also use :py:meth:`build_lo_string` utility function to
        create the LO String. For all other devices, lo channel string is not allowed.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read on that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           The LO PLL Fractional Mode attribute is applicable only when using the internal LO.

        .. note::
           For PXIe-5831 with PXIe-5653, PXIe-5832 with PXIe-5653, this attribute is ignored if the PXIe-5653 is used as the LO
           source.

        The default value is **Enabled**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+-------------------------------------------+
        | Name (Value) | Description                               |
        +==============+===========================================+
        | Disabled (0) | Indicates that the attribute is disabled. |
        +--------------+-------------------------------------------+
        | Enabled (1)  | Indicates that the attribute is enabled.  |
        +--------------+-------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LOPllFractionalMode, int):
                Specifies whether to use fractional mode for the LO phase-locked loop (PLL).

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.LOPllFractionalMode else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_PLL_FRACTIONAL_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trigger_export_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the exported Reference Trigger. You can also choose not to export any signal.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646 and PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on PXIe-5652, and the REF OUT terminal on PXIe-5644/5645/5646 and          |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists on only PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal                                                                                                       |
        |                           | to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841 PFI 0.                 |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for the PXIe-5644/5645/5646.                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid on only for                                     |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the exported Reference Trigger. You can also choose not to export any signal.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.TRIGGER_EXPORT_OUTPUT_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_trigger_export_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the exported Reference Trigger. You can also choose not to export any signal.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646 and PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on PXIe-5652, and the REF OUT terminal on PXIe-5644/5645/5646 and          |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists on only PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal                                                                                                       |
        |                           | to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841 PFI 0.                 |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for the PXIe-5644/5645/5646.                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid on only for                                     |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the exported Reference Trigger. You can also choose not to export any signal.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.TRIGGER_EXPORT_OUTPUT_TERMINAL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trigger_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        .. note::
           This attribute is not supported on a MIMO session.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/RefTrigger*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/RefTrigger*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/RefTrigger,*, where *ModuleName *is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/RefTrigger*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.TRIGGER_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_start_trigger_type(self, selector_string):
        r"""Gets whether the start trigger is a digital edge or a software trigger.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **None**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)     | Description                                                                                                              |
        +==================+==========================================================================================================================+
        | None (0)         | No start trigger is configured.                                                                                          |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Digital Edge (1) | The start trigger is not asserted until a digital edge is detected. The source of the digital edge is specified by the   |
        |                  | Start Trigger Digital Edge Source attribute.                                                                             |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Software (3)     | The start trigger is not asserted until a software trigger occurs. You can assert the software trigger by calling the    |
        |                  | RFmxInstr Send Software Edge Trigger method.                                                                             |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.StartTriggerType):
                Specifies whether the start trigger is a digital edge or a software trigger.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_TYPE.value
            )
            attr_val = enums.StartTriggerType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_start_trigger_type(self, selector_string, value):
        r"""Sets whether the start trigger is a digital edge or a software trigger.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **None**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)     | Description                                                                                                              |
        +==================+==========================================================================================================================+
        | None (0)         | No start trigger is configured.                                                                                          |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Digital Edge (1) | The start trigger is not asserted until a digital edge is detected. The source of the digital edge is specified by the   |
        |                  | Start Trigger Digital Edge Source attribute.                                                                             |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Software (3)     | The start trigger is not asserted until a software trigger occurs. You can assert the software trigger by calling the    |
        |                  | RFmxInstr Send Software Edge Trigger method.                                                                             |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.StartTriggerType, int):
                Specifies whether the start trigger is a digital edge or a software trigger.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.StartTriggerType else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_start_trigger_digital_edge_source(self, selector_string):
        r"""Gets the source terminal for the start trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value of this attribute is "" (empty string).

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | PFI0 (PFI0)               | The trigger is received on PFI 0. For the PXIe-5841 with PXIe-5655, the trigger is received on the PXIe-5841 PFI 0.      |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | The trigger is received on PFI 1.                                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | The trigger is received on PXI trigger line 0.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | The trigger is received on PXI trigger line 1.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | The trigger is received on PXI trigger line 2.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | The trigger is received on PXI trigger line 3.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | The trigger is received on PXI trigger line 4.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | The trigger is received on PXI trigger line 5.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | The trigger is received on PXI trigger line 6.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | The trigger is received on PXI trigger line 7.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | The trigger is received on the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarB (PXIe_DStarB) | The trigger is received on the PXIe DStar B trigger line. This value is valid only for                                   |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | TimerEvent (TimerEvent)   | The trigger is received from the timer event. This value is valid only for PXIe-5820/5840/5841/5842/5860 and for         |
        |                           | digital edge advance triggers on PXIe-5663E/5665.                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | The trigger is received on PFI 0 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | The trigger is received on PFI 1 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | The trigger is received on PFI 2 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | The trigger is received on PFI 3 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | The trigger is received on PFI 4 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | The trigger is received on PFI 5 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | The trigger is received on PFI 6 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | The trigger is received on PFI 7 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the source terminal for the start trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_DIGITAL_EDGE_SOURCE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_start_trigger_digital_edge_source(self, selector_string, value):
        r"""Sets the source terminal for the start trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value of this attribute is "" (empty string).

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | PFI0 (PFI0)               | The trigger is received on PFI 0. For the PXIe-5841 with PXIe-5655, the trigger is received on the PXIe-5841 PFI 0.      |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | The trigger is received on PFI 1.                                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | The trigger is received on PXI trigger line 0.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | The trigger is received on PXI trigger line 1.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | The trigger is received on PXI trigger line 2.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | The trigger is received on PXI trigger line 3.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | The trigger is received on PXI trigger line 4.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | The trigger is received on PXI trigger line 5.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | The trigger is received on PXI trigger line 6.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | The trigger is received on PXI trigger line 7.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | The trigger is received on the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarB (PXIe_DStarB) | The trigger is received on the PXIe DStar B trigger line. This value is valid only for                                   |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | TimerEvent (TimerEvent)   | The trigger is received from the timer event. This value is valid only for PXIe-5820/5840/5841/5842/5860 and for         |
        |                           | digital edge advance triggers on PXIe-5663E/5665.                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | The trigger is received on PFI 0 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | The trigger is received on PFI 1 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | The trigger is received on PFI 2 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | The trigger is received on PFI 3 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | The trigger is received on PFI 4 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | The trigger is received on PFI 5 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | The trigger is received on PFI 6 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | The trigger is received on PFI 7 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the source terminal for the start trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.START_TRIGGER_DIGITAL_EDGE_SOURCE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_start_trigger_digital_edge(self, selector_string):
        r"""Gets the active edge for the start trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Rising Edge**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +------------------+--------------------------------------------------------+
        | Name (Value)     | Description                                            |
        +==================+========================================================+
        | Rising Edge (0)  | The trigger asserts on the rising edge of the signal.  |
        +------------------+--------------------------------------------------------+
        | Falling Edge (1) | The trigger asserts on the falling edge of the signal. |
        +------------------+--------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.StartTriggerDigitalEdge):
                Specifies the active edge for the start trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_DIGITAL_EDGE.value
            )
            attr_val = enums.StartTriggerDigitalEdge(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_start_trigger_digital_edge(self, selector_string, value):
        r"""Sets the active edge for the start trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Rising Edge**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +------------------+--------------------------------------------------------+
        | Name (Value)     | Description                                            |
        +==================+========================================================+
        | Rising Edge (0)  | The trigger asserts on the rising edge of the signal.  |
        +------------------+--------------------------------------------------------+
        | Falling Edge (1) | The trigger asserts on the falling edge of the signal. |
        +------------------+--------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.StartTriggerDigitalEdge, int):
                Specifies the active edge for the start trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_TYPE` attribute to **Digital Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.StartTriggerDigitalEdge else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_DIGITAL_EDGE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_start_trigger_export_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the exported start trigger.

        You can also choose not to export any signal.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on PXIe-5652, and the REF OUT terminal on PXIe-5644/5645/5646 and          |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal                                                                                                       |
        |                           | to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841 PFI 0.                 |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the exported start trigger.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_EXPORT_OUTPUT_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_start_trigger_export_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the exported start trigger.

        You can also choose not to export any signal.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on PXIe-5652, and the REF OUT terminal on PXIe-5644/5645/5646 and          |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal                                                                                                       |
        |                           | to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841 PFI 0.                 |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the exported start trigger.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.START_TRIGGER_EXPORT_OUTPUT_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_start_trigger_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/StartTrigger*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/StartTrigger*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/StartTrigger,*, where *ModuleName *is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/StartTrigger*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.START_TRIGGER_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_advance_trigger_type(self, selector_string):
        r"""Gets whether the advance trigger is a digital edge or a software trigger.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **None**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)     | Description                                                                                                              |
        +==================+==========================================================================================================================+
        | None (0)         | No advance trigger is configured.                                                                                        |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Digital Edge (1) | The advance trigger is not asserted until a digital edge is detected. The source of the digital edge is specified with   |
        |                  | the Advance Trigger Digital Edge Source attribute.                                                                       |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Software (3)     | The advance trigger is not asserted until a software trigger occurs. You can assert the software trigger by calling the  |
        |                  | RFmxInstr Send Software Edge Trigger method.                                                                             |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AdvanceTriggerType):
                Specifies whether the advance trigger is a digital edge or a software trigger.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.ADVANCE_TRIGGER_TYPE.value
            )
            attr_val = enums.AdvanceTriggerType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_advance_trigger_type(self, selector_string, value):
        r"""Sets whether the advance trigger is a digital edge or a software trigger.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **None**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)     | Description                                                                                                              |
        +==================+==========================================================================================================================+
        | None (0)         | No advance trigger is configured.                                                                                        |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Digital Edge (1) | The advance trigger is not asserted until a digital edge is detected. The source of the digital edge is specified with   |
        |                  | the Advance Trigger Digital Edge Source attribute.                                                                       |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Software (3)     | The advance trigger is not asserted until a software trigger occurs. You can assert the software trigger by calling the  |
        |                  | RFmxInstr Send Software Edge Trigger method.                                                                             |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AdvanceTriggerType, int):
                Specifies whether the advance trigger is a digital edge or a software trigger.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.AdvanceTriggerType else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.ADVANCE_TRIGGER_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_advance_trigger_digital_edge_source(self, selector_string):
        r"""Gets the source terminal for the advance trigger.

        This attribute is used only when the :py:attr:`~nirfmxinstr.attributes.AttributeID.ADVANCE_TRIGGER_TYPE`
        attribute is set to **Digital Edge**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value of this attribute is "" (empty string).

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | PFI0 (PFI0)               | The trigger is received on PFI 0. For the PXIe-5841 with PXIe-5655, the trigger is received on the PXIe-5841 PFI 0.      |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | The trigger is received on PFI 1.                                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | The trigger is received on PXI trigger line 0.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | The trigger is received on PXI trigger line 1.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | The trigger is received on PXI trigger line 2.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | The trigger is received on PXI trigger line 3.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | The trigger is received on PXI trigger line 4.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | The trigger is received on PXI trigger line 5.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | The trigger is received on PXI trigger line 6.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | The trigger is received on PXI trigger line 7.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | The trigger is received on the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarB (PXIe_DStarB) | The trigger is received on the PXIe DStar B trigger line. This value is valid only for                                   |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | TimerEvent (TimerEvent)   | The trigger is received from the timer event. This value is valid only for PXIe-5820/5840/5841/5842/5860 and for         |
        |                           | digital edge advance triggers on PXIe-5663E/5665.                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | The trigger is received on PFI 0 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | The trigger is received on PFI 1 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | The trigger is received on PFI 2 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | The trigger is received on PFI 3 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | The trigger is received on PFI 4 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | The trigger is received on PFI 5 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | The trigger is received on PFI 6 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | The trigger is received on PFI 7 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the source terminal for the advance trigger.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.ADVANCE_TRIGGER_DIGITAL_EDGE_SOURCE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_advance_trigger_digital_edge_source(self, selector_string, value):
        r"""Sets the source terminal for the advance trigger.

        This attribute is used only when the :py:attr:`~nirfmxinstr.attributes.AttributeID.ADVANCE_TRIGGER_TYPE`
        attribute is set to **Digital Edge**.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value of this attribute is "" (empty string).

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | PFI0 (PFI0)               | The trigger is received on PFI 0. For the PXIe-5841 with PXIe-5655, the trigger is received on the PXIe-5841 PFI 0.      |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | The trigger is received on PFI 1.                                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | The trigger is received on PXI trigger line 0.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | The trigger is received on PXI trigger line 1.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | The trigger is received on PXI trigger line 2.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | The trigger is received on PXI trigger line 3.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | The trigger is received on PXI trigger line 4.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | The trigger is received on PXI trigger line 5.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | The trigger is received on PXI trigger line 6.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | The trigger is received on PXI trigger line 7.                                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | The trigger is received on the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarB (PXIe_DStarB) | The trigger is received on the PXIe DStar B trigger line. This value is valid only for                                   |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | TimerEvent (TimerEvent)   | The trigger is received from the timer event. This value is valid only for PXIe-5820/5840/5841/5842/5860 and for         |
        |                           | digital edge advance triggers on PXIe-5663E/5665.                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | The trigger is received on PFI 0 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | The trigger is received on PFI 1 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | The trigger is received on PFI 2 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | The trigger is received on PFI 3 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | The trigger is received on PFI 4 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | The trigger is received on PFI 5 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | The trigger is received on PFI 6 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | The trigger is received on PFI 7 of the DIO front panel connector.                                                       |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the source terminal for the advance trigger.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.ADVANCE_TRIGGER_DIGITAL_EDGE_SOURCE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_advance_trigger_export_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the exported advance trigger.

        You can also choose not to export any signal.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the exported advance trigger.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.ADVANCE_TRIGGER_EXPORT_OUTPUT_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_advance_trigger_export_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the exported advance trigger.

        You can also choose not to export any signal.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the exported advance trigger.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.ADVANCE_TRIGGER_EXPORT_OUTPUT_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_advance_trigger_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/AdvanceTrigger*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/AdvanceTrigger*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/AdvanceTrigger,*, where *ModuleName *is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/AdvanceTrigger*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.ADVANCE_TRIGGER_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_ready_for_start_event_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the Ready for Start event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the Ready for Start event.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.READY_FOR_START_EVENT_OUTPUT_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_ready_for_start_event_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the Ready for Start event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the Ready for Start event.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.READY_FOR_START_EVENT_OUTPUT_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_ready_for_start_event_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/ReadyForStartEvent*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/ReadyForStartEvent*, where *BasebandModule*is the name of the baseband module for your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/ReadyForStartEvent*, where *ModuleName * is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/ReadyForStartEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.READY_FOR_START_EVENT_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_ready_for_advance_event_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the Ready for Advance event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the Ready for Advance event.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.READY_FOR_ADVANCE_EVENT_OUTPUT_TERMINAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_ready_for_advance_event_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the Ready for Advance event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the Ready for Advance event.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.READY_FOR_ADVANCE_EVENT_OUTPUT_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_ready_for_advance_event_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/ReadyForAdvanceEvent*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/ReadyForAdvanceEvent*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/ReadyForAdvanceEvent*, where *ModuleName * is the name of your device in MAX and ChannelNumber is the channel number (0 or 1)

        - **All other devices**: */DigitizerName/ReadyForAdvanceEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.READY_FOR_ADVANCE_EVENT_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_ready_for_reference_event_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the Ready for Reference event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the Ready for Reference event.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.READY_FOR_REFERENCE_EVENT_OUTPUT_TERMINAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_ready_for_reference_event_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the Ready for Reference event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the Ready for Reference event.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.READY_FOR_REFERENCE_EVENT_OUTPUT_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_ready_for_reference_event_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/ReadyForReferenceEvent*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/ReadyForReferenceEvent*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/ReadyForReferenceEvent*, where *BasebandModule*is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/ReadyForReferenceEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.READY_FOR_REFERENCE_EVENT_TERMINAL_NAME.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_end_of_record_event_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the End of Record event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the End of Record event.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.END_OF_RECORD_EVENT_OUTPUT_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_end_of_record_event_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the End of Record event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the End of Record event.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string,
                attributes.AttributeID.END_OF_RECORD_EVENT_OUTPUT_TERMINAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_end_of_record_event_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/EndOfRecordEvent*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/EndOfRecordEvent*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/EndOfRecordEvent*, where *ModuleName * is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/EndOfRecordEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.END_OF_RECORD_EVENT_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_done_event_output_terminal(self, selector_string):
        r"""Gets the destination terminal for the Done event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the destination terminal for the Done event.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.DONE_EVENT_OUTPUT_TERMINAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_done_event_output_terminal(self, selector_string, value):
        r"""Sets the destination terminal for the Done event.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Do not export signal**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | Do not export signal ()   | Does not export the signal.                                                                                              |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | ClkOut (ClkOut)           | Exports the signal to the CLK OUT connector on the PXIe-5622/5624 front panel.                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut (RefOut)           | Exports the signal to the REF IN/OUT terminal on the PXIe-5652, and the REF OUT terminal on the PXIe-5644/5645/5646 and  |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RefOut2 (RefOut2)         | Exports the signal to the REF OUT2 terminal on the LO. This connector exists only on PXIe-5652.                          |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI0 (PFI0)               | Exports the signal to the PFI 0 connector. For the PXIe-5841 with PXIe-5655, the signal is exported to the PXIe-5841     |
        |                           | PFI 0.                                                                                                                   |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PFI1 (PFI1)               | Exports the signal to the PFI 1 connector on PXIe-5142 and PXIe-5622.                                                    |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig0 (PXI_Trig0)     | Exports the signal to the PXI trigger line 0.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig1 (PXI_Trig1)     | Exports the signal to the PXI trigger line 1.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig2 (PXI_Trig2)     | Exports the signal to the PXI trigger line 2.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig3 (PXI_Trig3)     | Exports the signal to the PXI trigger line 3.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig4 (PXI_Trig4)     | Exports the signal to the PXI trigger line 4.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig5 (PXI_Trig5)     | Exports the signal to the PXI trigger line 5.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig6 (PXI_Trig6)     | Exports the signal to the PXI trigger line 6.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_Trig7 (PXI_Trig7)     | Exports the signal to the PXI trigger line 7.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXI_STAR (PXI_STAR)       | Exports the signal to the PXI star trigger line. This value is not valid for PXIe-5644/5645/5646.                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe_DStarC (PXIe_DStarC) | Exports the signal to the PXIe DStar C trigger line. This value is valid only for                                        |
        |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI0 (DIO/PFI0)       | Exports the signal to the PFI 0 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI1 (DIO/PFI1)       | Exports the signal to the PFI 1 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI2 (DIO/PFI2)       | Exports the signal to the PFI 2 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI3 (DIO/PFI3)       | Exports the signal to the PFI 3 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI4 (DIO/PFI4)       | Exports the signal to the PFI 4 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI5 (DIO/PFI5)       | Exports the signal to the PFI 5 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI6 (DIO/PFI6)       | Exports the signal to the PFI 6 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | DIO/PFI7 (DIO/PFI7)       | Exports the signal to the PFI 7 on the DIO front panel connector.                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the destination terminal for the Done event.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.DONE_EVENT_OUTPUT_TERMINAL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_done_event_terminal_name(self, selector_string):
        r"""Gets the fully qualified signal name as a string.

        The standard format is as follows:

        - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/DoneEvent*, where *ModuleName* is the name of your device in MAX.

        - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/DoneEvent*, where *BasebandModule* is the name of your device in MAX.

        - **PXIe-5860**: */ModuleName/ai/ChannelNumber/DoneEvent*, where *ModuleName* is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).

        - **All other devices**: */DigitizerName/DoneEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.

        .. note::
           This attribute is not supported on a MIMO session.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the fully qualified signal name as a string.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.DONE_EVENT_TERMINAL_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_device_temperature(self, selector_string):
        r"""Gets the current temperature of the module. This value is expressed in degrees Celsius.

        To use this attribute for PXIe-5830/5831/5832, you must first use the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ attribute to specify the name of the
        channel you are configuring. When you are reading the device temperature, you must specify the context in the Selector
        String input as "module::<ModuleName>". You can also use the :py:meth:`build_module_string` method to build the module
        string. For all other devices, the only valid value for the selector string is "" (empty string).

        On a MIMO session, use "port::<deviceName>/<channelNumber>"  as the selector string to read this attribute. You
        can use the :py:meth:`build_port_string` method to build the selector string. For PXIe-5830/5831/5832, you must specify
        the context in the selector string input as port::<deviceName>/<channelNumber>/module::<moduleName>.

        Refer to the following table to determine which strings are valid for your configuration.

        +----------------------------+---------------------------+-------------------------+
        | Hardware Module            | TRX Port Type             | Selector String         |
        +============================+===========================+=========================+
        | PXIe-3621/3622/3623        | -                         | if or "" (empty string) |
        +----------------------------+---------------------------+-------------------------+
        | PXIe-5820                  | -                         | fpga                    |
        +----------------------------+---------------------------+-------------------------+
        | First connected mmRH-5582  | DIRECT TRX PORTS Only     | rf0                     |
        +----------------------------+---------------------------+-------------------------+
        | First connected mmRH-5582  | SWITCHED TRX PORTS [0-7]  | rf0switch0              |
        +----------------------------+---------------------------+-------------------------+
        | First connected mmRH-5582  | SWITCHED TRX PORTS [8-15] | rf0switch1              |
        +----------------------------+---------------------------+-------------------------+
        | Second connected mmRH-5582 | DIRECT TRX PORTS Only     | rf1                     |
        +----------------------------+---------------------------+-------------------------+
        | Second connected mmRH-5582 | SWITCHED TRX PORTS [0-7]  | rf1switch0              |
        +----------------------------+---------------------------+-------------------------+
        | Second connected mmRH-5582 | SWITCHED TRX PORTS [8-15] | rf1switch1              |
        +----------------------------+---------------------------+-------------------------+

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the current temperature of the module. This value is expressed in degrees Celsius.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DEVICE_TEMPERATURE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_digitizer_temperature(self, selector_string):
        r"""Gets the current temperature of the digitizer module. This value is expressed in degrees Celsius.

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        .. note::
           This attribute is not supported if you are using an external digitizer.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the current temperature of the digitizer module. This value is expressed in degrees Celsius.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DIGITIZER_TEMPERATURE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lo_temperature(self, selector_string):
        r"""Gets the current temperature of the LO module associated with the device. This value is expressed in degrees
        Celsius.

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        .. note::
           This attribute is not supported if you are using an external LO.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the current temperature of the LO module associated with the device. This value is expressed in degrees
                Celsius.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.LO_TEMPERATURE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_serial_number(self, selector_string):
        r"""Gets the serial number of the RF downconverter module.

        .. note::
           For PXIe-5644/5645/5646 and PXIe-5820/5840/5841/5842/5860, this attribute returns the serial number of the VST module.
           For PXIe-5830/5831/5832, this attribute returns the serial number of PXIe-3621/3622/3623.

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the serial number of the RF downconverter module.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.SERIAL_NUMBER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_instrument_model(self, selector_string):
        r"""Gets a string that contains the model number or name of the RF device that you are currently using.

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns a string that contains the model number or name of the RF device that you are currently using.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.INSTRUMENT_MODEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_module_revision(self, selector_string):
        r"""Gets the revision of the RF downconverter module.

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        .. note::
           For PXIe-5644/5645/5646 and PXIe-5820/5830/5831/5832/5840/5841/5842/5860, this attribute returns the revision of the
           VST module.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns the revision of the RF downconverter module.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.MODULE_REVISION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_instrument_firmware_revision(self, selector_string):
        r"""Gets a string containing the firmware revision information of the RF downconverter for the composite device you are
        currently using.

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Returns a string containing the firmware revision information of the RF downconverter for the composite device you are
                currently using.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.INSTRUMENT_FIRMWARE_REVISION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_preselector_present(self, selector_string):
        r"""Indicates whether a preselector is available on the RF downconverter module.

        +--------------+---------------------------------------------------+
        | Name (value) | Description                                       |
        +==============+===================================================+
        | TRUE         | A preselector is available on the downconverter.  |
        +--------------+---------------------------------------------------+
        | FALSE        | No preselector is available on the downconverter. |
        +--------------+---------------------------------------------------+

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Indicates whether a preselector is available on the RF downconverter module.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.PRESELECTOR_PRESENT.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_rf_preamp_present(self, selector_string):
        r"""Indicates whether an RF preamplifier is available on the RF downconverter module.

        +--------------+----------------------------------------------------+
        | Name (value) | Description                                        |
        +==============+====================================================+
        | TRUE         | A preamplifier is available on the downconverter.  |
        +--------------+----------------------------------------------------+
        | FALSE        | No preamplifier is available on the downconverter. |
        +--------------+----------------------------------------------------+

        On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
        :py:meth:`build_port_string` method to build the selector string.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Indicates whether an RF preamplifier is available on the RF downconverter module.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.RF_PREAMP_PRESENT.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_preamp_enabled(self, selector_string):
        r"""Gets whether the RF preamplifier is enabled in the system.

        PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842/5860: If you set this attribute to **Automatic**, RFmx
        selects the preamplifier state based on the value of the Reference Level attribute and the center frequency. For
        PXIe-5830/5831/5832, the value is not coerced.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value for PXIe-5644/5645/5646 and PXIe-5830/5831/5832/5840/5841/5842 is **Automatic**, else the
        default value is **Disabled**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Disabled (0)  | Disables the RF preamplifier.                                                                                            |
        |               | Supported Devices: PXIe-5663/5663E/5665/5668                                                                             |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Enabled (1)   | Enables the RF preamplifier when it is in the signal path and disables it when it is not in the signal path. Only        |
        |               | devices with an RF preamplifier on the downconverter and an RF preselector support this option. Use the RF Preamp        |
        |               | Present                                                                                                                  |
        |               | attribute to determine whether the downconverter has a preamplifier.                                                     |
        |               | Supported Devices: PXIe-5663/5663E/5665/5668                                                                             |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Automatic (3) | Automatically enables the RF preamplifier based on the value of the reference level.                                     |
        |               | Supported Devices: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842/5860                                          |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PreampEnabled):
                Specifies whether the RF preamplifier is enabled in the system.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.PREAMP_ENABLED.value
            )
            attr_val = enums.PreampEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_preamp_enabled(self, selector_string, value):
        r"""Sets whether the RF preamplifier is enabled in the system.

        PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842/5860: If you set this attribute to **Automatic**, RFmx
        selects the preamplifier state based on the value of the Reference Level attribute and the center frequency. For
        PXIe-5830/5831/5832, the value is not coerced.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value for PXIe-5644/5645/5646 and PXIe-5830/5831/5832/5840/5841/5842 is **Automatic**, else the
        default value is **Disabled**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Disabled (0)  | Disables the RF preamplifier.                                                                                            |
        |               | Supported Devices: PXIe-5663/5663E/5665/5668                                                                             |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Enabled (1)   | Enables the RF preamplifier when it is in the signal path and disables it when it is not in the signal path. Only        |
        |               | devices with an RF preamplifier on the downconverter and an RF preselector support this option. Use the RF Preamp        |
        |               | Present                                                                                                                  |
        |               | attribute to determine whether the downconverter has a preamplifier.                                                     |
        |               | Supported Devices: PXIe-5663/5663E/5665/5668                                                                             |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Automatic (3) | Automatically enables the RF preamplifier based on the value of the reference level.                                     |
        |               | Supported Devices: PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842/5860                                          |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PreampEnabled, int):
                Specifies whether the RF preamplifier is enabled in the system.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.PreampEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.PREAMP_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_channel_coupling(self, selector_string):
        r"""Gets whether the RF IN connector is AC- or DC-coupled on the downconverter.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | -            | NoteFor the PXIe-5665/5668, this attribute must be set to AC Coupled when the DC block is present, and set to DC         |
        |              | Coupled when the DC block is not present to ensure device specifications are met and proper calibration data is used.    |
        |              | For more information about removing or attaching the DC block, refer to the PXIe-5665 Theory of Operation or the         |
        |              | PXIe-5668 Theory of Operation topics in the NI RF Vector Signal Analyzers Help.                                          |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **AC Coupled**.

        **Valid values**

        - PXIe-5665 (3.6 GHz): AC Coupled DC Coupled

        - PXIe-5665 (14 GHz): AC Coupled, DC Coupled

        - PXIe-5668: AC Coupled

        **Supported devices**: PXIe-5665/5668

        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)   | Description                                                                                                              |
        +================+==========================================================================================================================+
        | AC Coupled (0) | Specifies that the RF input channel is AC-coupled. For low frequencies (<10 MHz), accuracy decreases because RFmxInstr   |
        |                | does not calibrate the configuration.                                                                                    |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | DC Coupled (1) | Specifies that the RF input channel is DC-coupled. The RFmx driver enforces a minimum RF attenuation for device          |
        |                | protection.                                                                                                              |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.ChannelCoupling):
                Specifies whether the RF IN connector is AC- or DC-coupled on the downconverter.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.CHANNEL_COUPLING.value
            )
            attr_val = enums.ChannelCoupling(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_channel_coupling(self, selector_string, value):
        r"""Sets whether the RF IN connector is AC- or DC-coupled on the downconverter.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | -            | NoteFor the PXIe-5665/5668, this attribute must be set to AC Coupled when the DC block is present, and set to DC         |
        |              | Coupled when the DC block is not present to ensure device specifications are met and proper calibration data is used.    |
        |              | For more information about removing or attaching the DC block, refer to the PXIe-5665 Theory of Operation or the         |
        |              | PXIe-5668 Theory of Operation topics in the NI RF Vector Signal Analyzers Help.                                          |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **AC Coupled**.

        **Valid values**

        - PXIe-5665 (3.6 GHz): AC Coupled DC Coupled

        - PXIe-5665 (14 GHz): AC Coupled, DC Coupled

        - PXIe-5668: AC Coupled

        **Supported devices**: PXIe-5665/5668

        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)   | Description                                                                                                              |
        +================+==========================================================================================================================+
        | AC Coupled (0) | Specifies that the RF input channel is AC-coupled. For low frequencies (<10 MHz), accuracy decreases because RFmxInstr   |
        |                | does not calibrate the configuration.                                                                                    |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | DC Coupled (1) | Specifies that the RF input channel is DC-coupled. The RFmx driver enforces a minimum RF attenuation for device          |
        |                | protection.                                                                                                              |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.ChannelCoupling, int):
                Specifies whether the RF IN connector is AC- or DC-coupled on the downconverter.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.ChannelCoupling else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.CHANNEL_COUPLING.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_downconverter_preselector_enabled(self, selector_string):
        r"""Gets whether the tunable preselector is enabled on the downconverter.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Disabled (0) | Disables the preselector.                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Enabled (1)  | The preselector is automatically enabled when it is in the signal path and is automatically disabled when it is not in   |
        |              | the signal path. Use the Preselector Present attribute to determine if the downconverter has a preselector.              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DownconverterPreselectorEnabled):
                Specifies whether the tunable preselector is enabled on the downconverter.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.DOWNCONVERTER_PRESELECTOR_ENABLED.value
            )
            attr_val = enums.DownconverterPreselectorEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_downconverter_preselector_enabled(self, selector_string, value):
        r"""Sets whether the tunable preselector is enabled on the downconverter.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Disabled (0) | Disables the preselector.                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Enabled (1)  | The preselector is automatically enabled when it is in the signal path and is automatically disabled when it is not in   |
        |              | the signal path. Use the Preselector Present attribute to determine if the downconverter has a preselector.              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DownconverterPreselectorEnabled, int):
                Specifies whether the tunable preselector is enabled on the downconverter.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.DownconverterPreselectorEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string,
                attributes.AttributeID.DOWNCONVERTER_PRESELECTOR_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_mixer_level(self, selector_string):
        r"""Gets the mixer level. This value is expressed in dBm.

        The mixer level represents the attenuation value to apply to the input RF signal as it reaches the first mixer
        in the signal chain. If you do not set this attribute, the RFmx driver automatically selects an optimal mixer level
        value based on the reference level.

        If you set the :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL` and
        :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL_OFFSET` attributes at the same time, the RFmx driver returns
        an error.

        This attribute is read-only for PXIe-5663/5663E devices.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values**

        +-------------------+-------------+
        | Name (value)      | Description |
        +===================+=============+
        | PXIe-5665/5668    | -10         |
        +-------------------+-------------+
        | All other devices | N/A         |
        +-------------------+-------------+

        The valid values for this attribute depend on your device configuration.

        **Supported devices**: PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the mixer level. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.MIXER_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_mixer_level(self, selector_string, value):
        r"""Sets the mixer level. This value is expressed in dBm.

        The mixer level represents the attenuation value to apply to the input RF signal as it reaches the first mixer
        in the signal chain. If you do not set this attribute, the RFmx driver automatically selects an optimal mixer level
        value based on the reference level.

        If you set the :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL` and
        :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL_OFFSET` attributes at the same time, the RFmx driver returns
        an error.

        This attribute is read-only for PXIe-5663/5663E devices.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values**

        +-------------------+-------------+
        | Name (value)      | Description |
        +===================+=============+
        | PXIe-5665/5668    | -10         |
        +-------------------+-------------+
        | All other devices | N/A         |
        +-------------------+-------------+

        The valid values for this attribute depend on your device configuration.

        **Supported devices**: PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the mixer level. This value is expressed in dBm.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.MIXER_LEVEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_mixer_level_offset(self, selector_string):
        r"""Gets the number of dB by which to adjust the device mixer level.

        Specifying a positive value for this attribute configures the device for moderate distortion and low noise,
        and specifying a negative value results in low distortion and higher noise.
        You cannot set the :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL_OFFSET`  and
        :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL` attributes at the same time.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0. The default value specifies device settings that are the best compromise between
        distortion and noise.

        **Supported devices**: PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the number of dB by which to adjust the device mixer level.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.MIXER_LEVEL_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_mixer_level_offset(self, selector_string, value):
        r"""Sets the number of dB by which to adjust the device mixer level.

        Specifying a positive value for this attribute configures the device for moderate distortion and low noise,
        and specifying a negative value results in low distortion and higher noise.
        You cannot set the :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL_OFFSET`  and
        :py:attr:`~nirfmxinstr.attributes.AttributeID.MIXER_LEVEL` attributes at the same time.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0. The default value specifies device settings that are the best compromise between
        distortion and noise.

        **Supported devices**: PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the number of dB by which to adjust the device mixer level.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.MIXER_LEVEL_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rf_attenuation_step_size(self, selector_string):
        r"""Gets the step size for the RF attenuation level. This value is expressed in dB. The actual RF attenuation is
        coerced up to the next highest multiple of the specified step size. If the mechanical attenuators are not available to
        implement the coerced RF attenuation, the solid state attenuators are used.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values**:

        +-----------------------------------------+-------------+
        | Name (value)                            | Description |
        +=========================================+=============+
        | PXIe-5601/5663/5663E                    | 0.0         |
        +-----------------------------------------+-------------+
        | PXIe-5603/5665 (3.6 GHz)                | 1.0         |
        +-----------------------------------------+-------------+
        | PXIe-5605/5665 (14 GHz), PXIe-5606/5668 | 5.0         |
        +-----------------------------------------+-------------+

        **Valid values**:

        +-----------------------------------------------------------------+-----------------------------+
        | Name (value)                                                    | Description                 |
        +=================================================================+=============================+
        | PXIe-5601/5663/5663E                                            | 0.0 to 93.0, continuous     |
        +-----------------------------------------------------------------+-----------------------------+
        | PXIe-5603/5665 (3.6 GHz)                                        | 1.0 to 74.0, in 1 dB steps  |
        +-----------------------------------------------------------------+-----------------------------+
        | PXIe-5605/5665 (14 GHz) (low band), PXIe-5606/5668 (low band)   | 1.0 to 106.0, in 1 dB steps |
        +-----------------------------------------------------------------+-----------------------------+
        | PXIe-5605/5665 (14 GHz) (high band), PXIe-5606/5668 (high band) | 5.0 to 75.0, in 5 dB steps  |
        +-----------------------------------------------------------------+-----------------------------+

        **Supported devices**: PXIe-5663, PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the step size for the RF attenuation level. This value is expressed in dB. The actual RF attenuation is
                coerced up to the next highest multiple of the specified step size. If the mechanical attenuators are not available to
                implement the coerced RF attenuation, the solid state attenuators are used.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RF_ATTENUATION_STEP_SIZE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rf_attenuation_step_size(self, selector_string, value):
        r"""Sets the step size for the RF attenuation level. This value is expressed in dB. The actual RF attenuation is
        coerced up to the next highest multiple of the specified step size. If the mechanical attenuators are not available to
        implement the coerced RF attenuation, the solid state attenuators are used.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default values**:

        +-----------------------------------------+-------------+
        | Name (value)                            | Description |
        +=========================================+=============+
        | PXIe-5601/5663/5663E                    | 0.0         |
        +-----------------------------------------+-------------+
        | PXIe-5603/5665 (3.6 GHz)                | 1.0         |
        +-----------------------------------------+-------------+
        | PXIe-5605/5665 (14 GHz), PXIe-5606/5668 | 5.0         |
        +-----------------------------------------+-------------+

        **Valid values**:

        +-----------------------------------------------------------------+-----------------------------+
        | Name (value)                                                    | Description                 |
        +=================================================================+=============================+
        | PXIe-5601/5663/5663E                                            | 0.0 to 93.0, continuous     |
        +-----------------------------------------------------------------+-----------------------------+
        | PXIe-5603/5665 (3.6 GHz)                                        | 1.0 to 74.0, in 1 dB steps  |
        +-----------------------------------------------------------------+-----------------------------+
        | PXIe-5605/5665 (14 GHz) (low band), PXIe-5606/5668 (low band)   | 1.0 to 106.0, in 1 dB steps |
        +-----------------------------------------------------------------+-----------------------------+
        | PXIe-5605/5665 (14 GHz) (high band), PXIe-5606/5668 (high band) | 5.0 to 75.0, in 5 dB steps  |
        +-----------------------------------------------------------------+-----------------------------+

        **Supported devices**: PXIe-5663, PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the step size for the RF attenuation level. This value is expressed in dB. The actual RF attenuation is
                coerced up to the next highest multiple of the specified step size. If the mechanical attenuators are not available to
                implement the coerced RF attenuation, the solid state attenuators are used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RF_ATTENUATION_STEP_SIZE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_osp_delay_enabled(self, selector_string):
        r"""Gets whether to enable the digitizer OSP block to delay Reference Triggers, along with the data samples, moving
        through the OSP block.

        If you set this attribute to **Disabled**, the Reference Triggers bypass the OSP block and are processed
        immediately.

        Enabling this attribute requires the following equipment configurations:

        - All digitizers being used must be the same model and hardware revision.

        - All digitizers must use the same firmware.

        - All digitizers must be configured with the same I/Q rate.

        - All devices must use the same signal path.

        For more information about the digitizer OSP block and Reference Triggers, refer to the following topics in the
        *NI High-Speed Digitizers Help*:

        - PXIe-5622 Onboard Signal Processing (OSP)

        - PXIe-5142 Onboard Signal Processing (OSP)

        - PXIe-5622 Trigger Sources

        - PXI-5142 Trigger Sources

        - PXIe-5622 Block Diagram

        - PXI-5142 Trigger Sources

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Enabled**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +--------------+-------------------------+
        | Name (Value) | Description             |
        +==============+=========================+
        | Disabled (0) | Disables the attribute. |
        +--------------+-------------------------+
        | Enabled (1)  | Enables the attribute.  |
        +--------------+-------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.OspDelayEnabled):
                Specifies whether to enable the digitizer OSP block to delay Reference Triggers, along with the data samples, moving
                through the OSP block.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.OSP_DELAY_ENABLED.value
            )
            attr_val = enums.OspDelayEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_osp_delay_enabled(self, selector_string, value):
        r"""Sets whether to enable the digitizer OSP block to delay Reference Triggers, along with the data samples, moving
        through the OSP block.

        If you set this attribute to **Disabled**, the Reference Triggers bypass the OSP block and are processed
        immediately.

        Enabling this attribute requires the following equipment configurations:

        - All digitizers being used must be the same model and hardware revision.

        - All digitizers must use the same firmware.

        - All digitizers must be configured with the same I/Q rate.

        - All devices must use the same signal path.

        For more information about the digitizer OSP block and Reference Triggers, refer to the following topics in the
        *NI High-Speed Digitizers Help*:

        - PXIe-5622 Onboard Signal Processing (OSP)

        - PXIe-5142 Onboard Signal Processing (OSP)

        - PXIe-5622 Trigger Sources

        - PXI-5142 Trigger Sources

        - PXIe-5622 Block Diagram

        - PXI-5142 Trigger Sources

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Enabled**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +--------------+-------------------------+
        | Name (Value) | Description             |
        +==============+=========================+
        | Disabled (0) | Disables the attribute. |
        +--------------+-------------------------+
        | Enabled (1)  | Enables the attribute.  |
        +--------------+-------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.OspDelayEnabled, int):
                Specifies whether to enable the digitizer OSP block to delay Reference Triggers, along with the data samples, moving
                through the OSP block.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.OspDelayEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.OSP_DELAY_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_phase_offset(self, selector_string):
        r"""Gets the offset to apply to the initial I and Q phases.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        Valid values are -180 degrees to 180 degrees, inclusive.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the offset to apply to the initial I and Q phases.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.PHASE_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_phase_offset(self, selector_string, value):
        r"""Sets the offset to apply to the initial I and Q phases.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        Valid values are -180 degrees to 180 degrees, inclusive.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the offset to apply to the initial I and Q phases.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.PHASE_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_width(self, selector_string):
        r"""Gets the FFT width of the device. The FFT width is the effective bandwidth of the signal path during each signal
        acquisition.

        The lower limit for all devices that support setting the FFT Width attribute is 7.325 kHz.

        **PXIe-5663/5663E**: The FFT width upper limit for the PXIe-5663/5663E depends on the RF frequency and on the
        module revision of the PXIe-5601. For more information about determining which revision of the PXIe-5601 RF
        downconverter you have installed, refer to the Identifying Module Revision topic in the *NI RF Vector Signal Analyzers
        Help*.

        .. note::
           The maximum FFT width for your device is constrained to 50 MHz or 25 MHz, depending on the digitizer option you
           purchased.

        .. note::
           You can use the FFT Width attribute with in-band retuning. For more information about in-band retuning, refer to the
           :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY` attribute.

        The RFmx driver treats the device instantaneous bandwidth as the effective real-time bandwidth of the signal
        path. The span specifies the frequency range of the computed spectrum. A signal analyzer can acquire a bandwidth only
        within the device instantaneous bandwidth. If the span you choose is greater than the device instantaneous bandwidth,
        the RFmx driver obtains multiple acquisitions and combines them into a single spectrum. By specifying the FFT width,
        you can control the specific bandwidth obtained in each signal acquisition.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported devices**: PXIe-5663/5663E/5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the FFT width of the device. The FFT width is the effective bandwidth of the signal path during each signal
                acquisition.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.FFT_WIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_width(self, selector_string, value):
        r"""Sets the FFT width of the device. The FFT width is the effective bandwidth of the signal path during each signal
        acquisition.

        The lower limit for all devices that support setting the FFT Width attribute is 7.325 kHz.

        **PXIe-5663/5663E**: The FFT width upper limit for the PXIe-5663/5663E depends on the RF frequency and on the
        module revision of the PXIe-5601. For more information about determining which revision of the PXIe-5601 RF
        downconverter you have installed, refer to the Identifying Module Revision topic in the *NI RF Vector Signal Analyzers
        Help*.

        .. note::
           The maximum FFT width for your device is constrained to 50 MHz or 25 MHz, depending on the digitizer option you
           purchased.

        .. note::
           You can use the FFT Width attribute with in-band retuning. For more information about in-band retuning, refer to the
           :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_CENTER_FREQUENCY` attribute.

        The RFmx driver treats the device instantaneous bandwidth as the effective real-time bandwidth of the signal
        path. The span specifies the frequency range of the computed spectrum. A signal analyzer can acquire a bandwidth only
        within the device instantaneous bandwidth. If the span you choose is greater than the device instantaneous bandwidth,
        the RFmx driver obtains multiple acquisitions and combines them into a single spectrum. By specifying the FFT width,
        you can control the specific bandwidth obtained in each signal acquisition.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported devices**: PXIe-5663/5663E/5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the FFT width of the device. The FFT width is the effective bandwidth of the signal path during each signal
                acquisition.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.FFT_WIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cleaner_spectrum(self, selector_string):
        r"""Gets how to obtain the lowest noise floor or faster measurement speed.

        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)                             | Description                                                                                                              |
        +==========================================+==========================================================================================================================+
        | PXIe-5665                                | Sets the FFT Width attribute to take narrower bandwidth acquisitions and avoid digitizer spurs. Uses IF filters to       |
        |                                          | reduce the noise floor for frequencies below 80 MHz.                                                                     |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5644/5645/5646, PXIe-5840/5841/5842 | Returns the best possible spectrum.                                                                                      |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5668                                | Returns the best possible spectrum. To provide the best spectrum measurement, the acquisition is reduced to 100 MHz      |
        |                                          | segments for any center frequency.                                                                                       |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Other devices                            | This attribute is ignored.                                                                                               |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        .. note::
           Some measurements, such as Spurious Emissions enable the Cleaner Spectrum attribute by default.  You can speed up those
           measurements by disabling the Cleaner Spectrum attribute.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported devices**: PXIe-5665, PXIe-5668, PXIe-5644/5645/5646, PXIe-5840/5841/5842/5860

        +--------------+--------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                    |
        +==============+================================================================================+
        | Disabled (0) | Disable this attribute to get faster measurement speed.                        |
        +--------------+--------------------------------------------------------------------------------+
        | Enabled (1)  | Enable this attribute to get the lowest noise floor and avoid digitizer spurs. |
        +--------------+--------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.CleanerSpectrum):
                Specifies how to obtain the lowest noise floor or faster measurement speed.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.CLEANER_SPECTRUM.value
            )
            attr_val = enums.CleanerSpectrum(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cleaner_spectrum(self, selector_string, value):
        r"""Sets how to obtain the lowest noise floor or faster measurement speed.

        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)                             | Description                                                                                                              |
        +==========================================+==========================================================================================================================+
        | PXIe-5665                                | Sets the FFT Width attribute to take narrower bandwidth acquisitions and avoid digitizer spurs. Uses IF filters to       |
        |                                          | reduce the noise floor for frequencies below 80 MHz.                                                                     |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5644/5645/5646, PXIe-5840/5841/5842 | Returns the best possible spectrum.                                                                                      |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5668                                | Returns the best possible spectrum. To provide the best spectrum measurement, the acquisition is reduced to 100 MHz      |
        |                                          | segments for any center frequency.                                                                                       |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Other devices                            | This attribute is ignored.                                                                                               |
        +------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        .. note::
           Some measurements, such as Spurious Emissions enable the Cleaner Spectrum attribute by default.  You can speed up those
           measurements by disabling the Cleaner Spectrum attribute.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported devices**: PXIe-5665, PXIe-5668, PXIe-5644/5645/5646, PXIe-5840/5841/5842/5860

        +--------------+--------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                    |
        +==============+================================================================================+
        | Disabled (0) | Disable this attribute to get faster measurement speed.                        |
        +--------------+--------------------------------------------------------------------------------+
        | Enabled (1)  | Enable this attribute to get the lowest noise floor and avoid digitizer spurs. |
        +--------------+--------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.CleanerSpectrum, int):
                Specifies how to obtain the lowest noise floor or faster measurement speed.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.CleanerSpectrum else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.CLEANER_SPECTRUM.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_if_output_power_level_offset(self, selector_string):
        r"""Gets the power offset by which to adjust the default IF output power level. This value is expressed in dB.

        This attribute does not depend on absolute IF output power levels; therefore, you can use this attribute to
        adjust the IF output power level on all RFmx-supported devices without knowing the exact default value. Use this
        attribute to increase or decrease the nominal output level to achieve better measurement results.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Supported devices**: PXIe-5663/5663E/5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the power offset by which to adjust the default IF output power level. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.IF_OUTPUT_POWER_LEVEL_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_if_output_power_level_offset(self, selector_string, value):
        r"""Sets the power offset by which to adjust the default IF output power level. This value is expressed in dB.

        This attribute does not depend on absolute IF output power levels; therefore, you can use this attribute to
        adjust the IF output power level on all RFmx-supported devices without knowing the exact default value. Use this
        attribute to increase or decrease the nominal output level to achieve better measurement results.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Supported devices**: PXIe-5663/5663E/5665, PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the power offset by which to adjust the default IF output power level. This value is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.IF_OUTPUT_POWER_LEVEL_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_digitizer_dither_enabled(self, selector_string):
        r"""Gets whether dithering is enabled on the digitizer.

        Dithering adds band-limited noise in the analog signal path to help reduce the quantization effects of the ADC
        and improve spectral performance. On the PXIe-5622, this out-of-band noise is added at low frequencies of up to
        approximately 12 MHz.

        **PXIe-5663/5663E/5665:** When you enable dithering, the maximum signal level is reduced by up to 3 dB. This
        signal level reduction is accounted for in the nominal input ranges of the PXIe-5622. Therefore, you can overrange the
        input by up to 3 dB with dither disabled. For example, the +4 dBm input range can handle signal levels up to +7 dBm
        with dither disabled.

        For wider bandwidth acquisitions, such as 40 MHz, disable dithering to eliminate residual leakage of the dither
        signal into the lower frequencies of the IF passband, which starts at 12.5 MHz and ends at 62.5 MHz. This leakage can
        slightly raise the noise floor in the lower frequencies, thus degrading the performance in high-sensitivity
        applications. When performing spectral measurements, this leakage can also appear as a wide, low-amplitude signal near
        the 12.5 MHz and 62.5 MHz frequencies. The width and amplitude of the signal depends on your resolution bandwidth and
        the type of time-domain window you apply to your FFT.

        **PXIe-5668**: When you enable dithering, the maximum signal level is reduced by up to 2 dB. For the PXIe-5624,
        the maximum input power with dither off is 8 dBm and the maximum input power level with dither on is 6 dBm. When
        acquiring an 800 MHz bandwidth signal, the I/Q data contains the dither even if the dither signal is not in the
        displayed spectrum. The dither can affect actions like power level triggering.

        +--------------+------------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                    |
        +==============+================================================================================================+
        | -            | Note For the PXIe-5668, disabling dithering can negatively affect absolute amplitude accuracy. |
        +--------------+------------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           For PXIe-5820/5830/5831/5832/5840/5841/5842, only **Enabled** is supported.

        The default value is **Enabled**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842

        +--------------+-------------------------+
        | Name (Value) | Description             |
        +==============+=========================+
        | Disabled (0) | Disables the attribute. |
        +--------------+-------------------------+
        | Enabled (1)  | Enables the attribute.  |
        +--------------+-------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DigitizerDitherEnabled):
                Specifies whether dithering is enabled on the digitizer.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.DIGITIZER_DITHER_ENABLED.value
            )
            attr_val = enums.DigitizerDitherEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_digitizer_dither_enabled(self, selector_string, value):
        r"""Sets whether dithering is enabled on the digitizer.

        Dithering adds band-limited noise in the analog signal path to help reduce the quantization effects of the ADC
        and improve spectral performance. On the PXIe-5622, this out-of-band noise is added at low frequencies of up to
        approximately 12 MHz.

        **PXIe-5663/5663E/5665:** When you enable dithering, the maximum signal level is reduced by up to 3 dB. This
        signal level reduction is accounted for in the nominal input ranges of the PXIe-5622. Therefore, you can overrange the
        input by up to 3 dB with dither disabled. For example, the +4 dBm input range can handle signal levels up to +7 dBm
        with dither disabled.

        For wider bandwidth acquisitions, such as 40 MHz, disable dithering to eliminate residual leakage of the dither
        signal into the lower frequencies of the IF passband, which starts at 12.5 MHz and ends at 62.5 MHz. This leakage can
        slightly raise the noise floor in the lower frequencies, thus degrading the performance in high-sensitivity
        applications. When performing spectral measurements, this leakage can also appear as a wide, low-amplitude signal near
        the 12.5 MHz and 62.5 MHz frequencies. The width and amplitude of the signal depends on your resolution bandwidth and
        the type of time-domain window you apply to your FFT.

        **PXIe-5668**: When you enable dithering, the maximum signal level is reduced by up to 2 dB. For the PXIe-5624,
        the maximum input power with dither off is 8 dBm and the maximum input power level with dither on is 6 dBm. When
        acquiring an 800 MHz bandwidth signal, the I/Q data contains the dither even if the dither signal is not in the
        displayed spectrum. The dither can affect actions like power level triggering.

        +--------------+------------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                    |
        +==============+================================================================================================+
        | -            | Note For the PXIe-5668, disabling dithering can negatively affect absolute amplitude accuracy. |
        +--------------+------------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        .. note::
           For PXIe-5820/5830/5831/5832/5840/5841/5842, only **Enabled** is supported.

        The default value is **Enabled**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842

        +--------------+-------------------------+
        | Name (Value) | Description             |
        +==============+=========================+
        | Disabled (0) | Disables the attribute. |
        +--------------+-------------------------+
        | Enabled (1)  | Enables the attribute.  |
        +--------------+-------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DigitizerDitherEnabled, int):
                Specifies whether dithering is enabled on the digitizer.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.DigitizerDitherEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.DIGITIZER_DITHER_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_if_filter_bandwidth(self, selector_string):
        r"""Gets the IF filter path bandwidth for your device configuration.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | -            | Note For composite devices, such as the PXIe-5665/5668, the IF filter path bandwidth includes all IF filters across the  |
        |              | component modules of a composite device.                                                                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        RFmx chooses an appropriate IF filter as default IF Filter based on measurement configuration, center
        frequency, cleaner spectrum and downconverter preselector.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the IF filter path bandwidth for your device configuration.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.IF_FILTER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_if_filter_bandwidth(self, selector_string, value):
        r"""Sets the IF filter path bandwidth for your device configuration.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | -            | Note For composite devices, such as the PXIe-5665/5668, the IF filter path bandwidth includes all IF filters across the  |
        |              | component modules of a composite device.                                                                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        RFmx chooses an appropriate IF filter as default IF Filter based on measurement configuration, center
        frequency, cleaner spectrum and downconverter preselector.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the IF filter path bandwidth for your device configuration.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.IF_FILTER_BANDWIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_settling_units(self, selector_string):
        r"""Gets the delay duration units and interpretation for LO settling.

        Specify the actual settling value using the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_SETTLING`
        attribute.

        +--------------+-----------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                   |
        +==============+===============================================================================================+
        | -            | Note The Frequency Settling Units attribute is not supported if you are using an external LO. |
        +--------------+-----------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **PPM**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        +------------------------+----------------------------------------------------------------+
        | Name (Value)           | Description                                                    |
        +========================+================================================================+
        | PPM (0)                | Specifies the frequency settling in parts per million (ppm).   |
        +------------------------+----------------------------------------------------------------+
        | Seconds After Lock (1) | Specifies the frequency settling in time after lock (seconds). |
        +------------------------+----------------------------------------------------------------+
        | Seconds After I/O (2)  | Specifies the frequency settling in time after I/O (seconds).  |
        +------------------------+----------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.FrequencySettlingUnits):
                Specifies the delay duration units and interpretation for LO settling.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_SETTLING_UNITS.value
            )
            attr_val = enums.FrequencySettlingUnits(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_settling_units(self, selector_string, value):
        r"""Sets the delay duration units and interpretation for LO settling.

        Specify the actual settling value using the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_SETTLING`
        attribute.

        +--------------+-----------------------------------------------------------------------------------------------+
        | Name (value) | Description                                                                                   |
        +==============+===============================================================================================+
        | -            | Note The Frequency Settling Units attribute is not supported if you are using an external LO. |
        +--------------+-----------------------------------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **PPM**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        +------------------------+----------------------------------------------------------------+
        | Name (Value)           | Description                                                    |
        +========================+================================================================+
        | PPM (0)                | Specifies the frequency settling in parts per million (ppm).   |
        +------------------------+----------------------------------------------------------------+
        | Seconds After Lock (1) | Specifies the frequency settling in time after lock (seconds). |
        +------------------------+----------------------------------------------------------------+
        | Seconds After I/O (2)  | Specifies the frequency settling in time after I/O (seconds).  |
        +------------------------+----------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.FrequencySettlingUnits, int):
                Specifies the delay duration units and interpretation for LO settling.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.FrequencySettlingUnits else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_SETTLING_UNITS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_settling(self, selector_string):
        r"""Gets the value used for LO frequency settling.

        Specify the units and interpretation for this scalar value using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_SETTLING_UNITS` attribute.

        **Valid values**

        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+
        | Frequency Settling Units Property Value | PXIe-5663/5663E                                 | PXIe-5665/5668                                  | PXIe-5644/5645/5646               | PXIe-5830/5831/5832/5840/5841/5842, PXIe-5831 with PXIe-5653 (using PXIe-3622 LO), PXIe-5832 with PXIe-5653 (using PXIe-3623 LO) | PXIe-5831 with PXIe-5653 (using PXIe-5653 LO) and PXIe-5832 with PXIe-5653 (using PXIe-5653 LO) |
        +=========================================+=================================================+=================================================+===================================+==================================================================================================================================+=================================================================================================+
        | Seconds After Lock                      | 2 µs to 80 ms, resolution of approximately 2 µs | 4 µs to 80 ms, resolution of approximately 4 µs | 1 µs to 65 ms, resolution of 1 µs | 1 µs to 10s, resolution of 1 µs                                                                                                  | 4 µs to 80 ms, resolution of approximately 4 µs                                                 |
        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+
        | Seconds After I/O                       | 0 µs to 80 ms, resolution of 1 µs               | 0 µs to 80 ms, resolution of 1 µs               | 1 µs to 65 ms, resolution of 1 µs | 0 µs to 10s, resolution of 1 µs                                                                                                  | 0 µs to 80 ms, resolution of 1 µs                                                               |
        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+
        | PPM                                     | 1.0, 0.1, 0.01                                  | 1.0, 0.1, 0.01, 0.001                           | 1.0, 0.1, 0.01                    | 1.0 to 0.01                                                                                                                      | 1.0 to 0.01                                                                                     |
        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+

        +--------------+-----------------------------------------------------------------------+
        | Name (value) | Description                                                           |
        +==============+=======================================================================+
        | -            | Note This attribute is not supported if you are using an external LO. |
        +--------------+-----------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.1.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the value used for LO frequency settling.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_SETTLING.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_settling(self, selector_string, value):
        r"""Sets the value used for LO frequency settling.

        Specify the units and interpretation for this scalar value using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_SETTLING_UNITS` attribute.

        **Valid values**

        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+
        | Frequency Settling Units Property Value | PXIe-5663/5663E                                 | PXIe-5665/5668                                  | PXIe-5644/5645/5646               | PXIe-5830/5831/5832/5840/5841/5842, PXIe-5831 with PXIe-5653 (using PXIe-3622 LO), PXIe-5832 with PXIe-5653 (using PXIe-3623 LO) | PXIe-5831 with PXIe-5653 (using PXIe-5653 LO) and PXIe-5832 with PXIe-5653 (using PXIe-5653 LO) |
        +=========================================+=================================================+=================================================+===================================+==================================================================================================================================+=================================================================================================+
        | Seconds After Lock                      | 2 µs to 80 ms, resolution of approximately 2 µs | 4 µs to 80 ms, resolution of approximately 4 µs | 1 µs to 65 ms, resolution of 1 µs | 1 µs to 10s, resolution of 1 µs                                                                                                  | 4 µs to 80 ms, resolution of approximately 4 µs                                                 |
        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+
        | Seconds After I/O                       | 0 µs to 80 ms, resolution of 1 µs               | 0 µs to 80 ms, resolution of 1 µs               | 1 µs to 65 ms, resolution of 1 µs | 0 µs to 10s, resolution of 1 µs                                                                                                  | 0 µs to 80 ms, resolution of 1 µs                                                               |
        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+
        | PPM                                     | 1.0, 0.1, 0.01                                  | 1.0, 0.1, 0.01, 0.001                           | 1.0, 0.1, 0.01                    | 1.0 to 0.01                                                                                                                      | 1.0 to 0.01                                                                                     |
        +-----------------------------------------+-------------------------------------------------+-------------------------------------------------+-----------------------------------+----------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+

        +--------------+-----------------------------------------------------------------------+
        | Name (value) | Description                                                           |
        +==============+=======================================================================+
        | -            | Note This attribute is not supported if you are using an external LO. |
        +--------------+-----------------------------------------------------------------------+

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.1.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the value used for LO frequency settling.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.FREQUENCY_SETTLING.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rf_highpass_filter_frequency(self, selector_string):
        r"""Gets the maximum corner frequency of the high pass filter in the RF signal path. The device uses the highest
        frequency high-pass filter option below or equal to the value you specify and returns a coerced value. Specifying a
        value of 0 disables high pass filtering silly.

        For multispan acquisitions, the device uses the appropriate filter for each subspan during acquisition,
        depending on the details of your application and the value you specify. In multispan acquisition spectrum applications,
        this attribute returns the value you specified rather than a coerced value if multiple high-pass filters are used
        during the acquisition.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        The valid values range from 0 to 26.5.

        **Supported devices**: PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the maximum corner frequency of the high pass filter in the RF signal path. The device uses the highest
                frequency high-pass filter option below or equal to the value you specify and returns a coerced value. Specifying a
                value of 0 disables high pass filtering silly.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RF_HIGHPASS_FILTER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rf_highpass_filter_frequency(self, selector_string, value):
        r"""Sets the maximum corner frequency of the high pass filter in the RF signal path. The device uses the highest
        frequency high-pass filter option below or equal to the value you specify and returns a coerced value. Specifying a
        value of 0 disables high pass filtering silly.

        For multispan acquisitions, the device uses the appropriate filter for each subspan during acquisition,
        depending on the details of your application and the value you specify. In multispan acquisition spectrum applications,
        this attribute returns the value you specified rather than a coerced value if multiple high-pass filters are used
        during the acquisition.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        The valid values range from 0 to 26.5.

        **Supported devices**: PXIe-5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the maximum corner frequency of the high pass filter in the RF signal path. The device uses the highest
                frequency high-pass filter option below or equal to the value you specify and returns a coerced value. Specifying a
                value of 0 disables high pass filtering silly.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RF_HIGHPASS_FILTER_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_subspan_overlap(self, selector_string):
        r"""Use subspan overlap process to eliminate or reduce analyzer spurs. To enable this feature, specify a non-zero
        percentage overlap between consecutive subspans in a spectrum acquisition.

        If a value greater than 0 is specified, then for each spectral line in the resulting spectrum, the driver
        acquires data twice with slightly different hardware settings, so that the analyzer spurs, if any, are present at
        different frequencies in the two acquisitions. Typically, LO frequency is shifted between the acquisitions causing
        analyzer spurs that are relative to the LO frequency, to move from one frequency to another. Those spurs, which are
        present in only one of the acquisitions for each spectral line, get removed.

        The subspan overlap feature will not remove any spurs from the Device Under Test or modify the signal being
        measured; unlike the analyzer spurs, the spurs in the signal being measured stay at a constant frequency in the two
        acquisitions.

        .. note::
           Subspan overlap process effectively is performing minimum averaging, which might reduce the measured noise floor level.
           RFmx Spectrum Averaging can be enabled to minimize the effect of subspan overlap on the noise floor.

        .. note::
           RFmx may apply further shifts to the specified value to accommodate fixed-frequency edges of components such as
           preselectors.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Valid values**

        +-----------------------------------------+-------------+
        | Name (value)                            | Description |
        +=========================================+=============+
        | PXIe-5820/5830/5831/5832/5840/5841/5860 | 0           |
        +-----------------------------------------+-------------+
        | PXIe-5842                               | 0, 50       |
        +-----------------------------------------+-------------+
        | PXIe-5665/5668                          | 0 to <100   |
        +-----------------------------------------+-------------+

        **Supported devices**: PXIe-5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Use subspan overlap process to eliminate or reduce analyzer spurs. To enable this feature, specify a non-zero
                percentage overlap between consecutive subspans in a spectrum acquisition.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.SUBSPAN_OVERLAP.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_subspan_overlap(self, selector_string, value):
        r"""Use subspan overlap process to eliminate or reduce analyzer spurs. To enable this feature, specify a non-zero
        percentage overlap between consecutive subspans in a spectrum acquisition.

        If a value greater than 0 is specified, then for each spectral line in the resulting spectrum, the driver
        acquires data twice with slightly different hardware settings, so that the analyzer spurs, if any, are present at
        different frequencies in the two acquisitions. Typically, LO frequency is shifted between the acquisitions causing
        analyzer spurs that are relative to the LO frequency, to move from one frequency to another. Those spurs, which are
        present in only one of the acquisitions for each spectral line, get removed.

        The subspan overlap feature will not remove any spurs from the Device Under Test or modify the signal being
        measured; unlike the analyzer spurs, the spurs in the signal being measured stay at a constant frequency in the two
        acquisitions.

        .. note::
           Subspan overlap process effectively is performing minimum averaging, which might reduce the measured noise floor level.
           RFmx Spectrum Averaging can be enabled to minimize the effect of subspan overlap on the noise floor.

        .. note::
           RFmx may apply further shifts to the specified value to accommodate fixed-frequency edges of components such as
           preselectors.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Valid values**

        +-----------------------------------------+-------------+
        | Name (value)                            | Description |
        +=========================================+=============+
        | PXIe-5820/5830/5831/5832/5840/5841/5860 | 0           |
        +-----------------------------------------+-------------+
        | PXIe-5842                               | 0, 50       |
        +-----------------------------------------+-------------+
        | PXIe-5665/5668                          | 0 to <100   |
        +-----------------------------------------+-------------+

        **Supported devices**: PXIe-5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Use subspan overlap process to eliminate or reduce analyzer spurs. To enable this feature, specify a non-zero
                percentage overlap between consecutive subspans in a spectrum acquisition.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.SUBSPAN_OVERLAP.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_downconverter_gain(self, selector_string):
        r"""Gets the net signal gain for the device at the current RFmx settings and temperature. RFmx scales the acquired I/Q
        and spectrum data from the digitizer using the value of this attribute.

        For a vector signal analyzer (VSA), the system is defined as the RF downconverter for all interfaces between
        the RF IN connector on the RF downconverter front panel and the IF IN connector on the digitizer front panel. For a
        spectrum monitoring receiver, the system is defined as the RF preselector, RF downconverter, and IF conditioning
        modules including all interfaces between the RF IN  connector on the RF preselector module front panel and the IF IN
        connector on the digitizer front panel.

        .. note::
           This attribute is not supported on a MIMO session.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is N/A.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the net signal gain for the device at the current RFmx settings and temperature. RFmx scales the acquired I/Q
                and spectrum data from the digitizer using the value of this attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DOWNCONVERTER_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_amplitude_settling(self, selector_string):
        r"""Gets the amplitude settling accuracy value. This value is expressed in decibels. RFmx waits until the RF power
        attains the specified accuracy level after calling the RFmx Initiate method.

        Any specified amplitude settling value that is above the acceptable minimum value is coerced down to the
        closest valid value.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the amplitude settling accuracy value. This value is expressed in decibels. RFmx waits until the RF power
                attains the specified accuracy level after calling the RFmx Initiate method.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.AMPLITUDE_SETTLING.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_amplitude_settling(self, selector_string, value):
        r"""Sets the amplitude settling accuracy value. This value is expressed in decibels. RFmx waits until the RF power
        attains the specified accuracy level after calling the RFmx Initiate method.

        Any specified amplitude settling value that is above the acceptable minimum value is coerced down to the
        closest valid value.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the amplitude settling accuracy value. This value is expressed in decibels. RFmx waits until the RF power
                attains the specified accuracy level after calling the RFmx Initiate method.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.AMPLITUDE_SETTLING.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_overflow_error_reporting(self, selector_string):
        r"""Configures error reporting for ADC and overflows occurred during onboard signal processing. Overflows lead to clipping
        of the waveform.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Warning**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +--------------+-------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                               |
        +==============+===========================================================================================+
        | Warning (0)  | RFmx returns a warning when an ADC or an onboard signal processing (OSP) overflow occurs. |
        +--------------+-------------------------------------------------------------------------------------------+
        | Disabled (1) | RFmx does not return an error or a warning when an ADC or OSP overflow occurs.            |
        +--------------+-------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.OverflowErrorReporting):
                Configures error reporting for ADC and overflows occurred during onboard signal processing. Overflows lead to clipping
                of the waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.OVERFLOW_ERROR_REPORTING.value
            )
            attr_val = enums.OverflowErrorReporting(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_overflow_error_reporting(self, selector_string, value):
        r"""Configures error reporting for ADC and overflows occurred during onboard signal processing. Overflows lead to clipping
        of the waveform.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Warning**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +--------------+-------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                               |
        +==============+===========================================================================================+
        | Warning (0)  | RFmx returns a warning when an ADC or an onboard signal processing (OSP) overflow occurs. |
        +--------------+-------------------------------------------------------------------------------------------+
        | Disabled (1) | RFmx does not return an error or a warning when an ADC or OSP overflow occurs.            |
        +--------------+-------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.OverflowErrorReporting, int):
                Configures error reporting for ADC and overflows occurred during onboard signal processing. Overflows lead to clipping
                of the waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.OverflowErrorReporting else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.OVERFLOW_ERROR_REPORTING.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_common_mode_level(self, selector_string):
        r"""Gets the common-mode level presented at each differential input terminal. The common-mode level shifts both
        positive and negative terminals in the same direction. This must match the common-mode level of the device under test
        (DUT). This value is expressed in Volts.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Supported devices**: PXIe-5820

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the common-mode level presented at each differential input terminal. The common-mode level shifts both
                positive and negative terminals in the same direction. This must match the common-mode level of the device under test
                (DUT). This value is expressed in Volts.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.COMMON_MODE_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_common_mode_level(self, selector_string, value):
        r"""Sets the common-mode level presented at each differential input terminal. The common-mode level shifts both
        positive and negative terminals in the same direction. This must match the common-mode level of the device under test
        (DUT). This value is expressed in Volts.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 0.

        **Supported devices**: PXIe-5820

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the common-mode level presented at each differential input terminal. The common-mode level shifts both
                positive and negative terminals in the same direction. This must match the common-mode level of the device under test
                (DUT). This value is expressed in Volts.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.COMMON_MODE_LEVEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_smu_resource_name(self, selector_string):
        r"""Gets the resource name assigned by Measurement and Automation Explorer (MAX) for NI Source Measure Units (SMU)
        which is used  as the noise source power supply for Noise Figure (NF) measurement, for example, PXI1Slot3, where
        PXI1Slot3 is an instrument resource name. SMU Resource Name can also be a logical IVI name.

        **Supported devices:** PXIe-4138, PXIe-4139, PXIe-4139 (40 W), and PXIe-4143 SMUs.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the resource name assigned by Measurement and Automation Explorer (MAX) for NI Source Measure Units (SMU)
                which is used  as the noise source power supply for Noise Figure (NF) measurement, for example, PXI1Slot3, where
                PXI1Slot3 is an instrument resource name. SMU Resource Name can also be a logical IVI name.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.SMU_RESOURCE_NAME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_smu_resource_name(self, selector_string, value):
        r"""Sets the resource name assigned by Measurement and Automation Explorer (MAX) for NI Source Measure Units (SMU)
        which is used  as the noise source power supply for Noise Figure (NF) measurement, for example, PXI1Slot3, where
        PXI1Slot3 is an instrument resource name. SMU Resource Name can also be a logical IVI name.

        **Supported devices:** PXIe-4138, PXIe-4139, PXIe-4139 (40 W), and PXIe-4143 SMUs.

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the resource name assigned by Measurement and Automation Explorer (MAX) for NI Source Measure Units (SMU)
                which is used  as the noise source power supply for Noise Figure (NF) measurement, for example, PXI1Slot3, where
                PXI1Slot3 is an instrument resource name. SMU Resource Name can also be a logical IVI name.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.SMU_RESOURCE_NAME.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_smu_channel(self, selector_string):
        r"""Gets the output channel to be used for noise figure (NF) measurement in RFmx.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the output channel to be used for noise figure (NF) measurement in RFmx.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.SMU_CHANNEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_smu_channel(self, selector_string, value):
        r"""Sets the output channel to be used for noise figure (NF) measurement in RFmx.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the output channel to be used for noise figure (NF) measurement in RFmx.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                selector_string, attributes.AttributeID.SMU_CHANNEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_optimize_path_for_signal_bandwidth(self, selector_string):
        r"""Optimizes RF path for the signal bandwidth that is centered on the IQ carrier frequency.

        You can disable this attribute to avoid changes to the RF path when changing the signal bandwidth.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Automatic**.

        **Supported devices**: PXIe-5830/5831/5832/5841/5842

        +---------------+-------------------------------------------------------------------------+
        | Name (Value)  | Description                                                             |
        +===============+=========================================================================+
        | Disabled (0)  | Disables the optimized path for signal bandwidth.                       |
        +---------------+-------------------------------------------------------------------------+
        | Enabled (1)   | Enables the optimized path for signal bandwidth.                        |
        +---------------+-------------------------------------------------------------------------+
        | Automatic (2) | Automatically enables the optimized path based on other configurations. |
        +---------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.OptimizePathForSignalBandwidth):
                Optimizes RF path for the signal bandwidth that is centered on the IQ carrier frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.OPTIMIZE_PATH_FOR_SIGNAL_BANDWIDTH.value
            )
            attr_val = enums.OptimizePathForSignalBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_optimize_path_for_signal_bandwidth(self, selector_string, value):
        r"""Optimizes RF path for the signal bandwidth that is centered on the IQ carrier frequency.

        You can disable this attribute to avoid changes to the RF path when changing the signal bandwidth.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Automatic**.

        **Supported devices**: PXIe-5830/5831/5832/5841/5842

        +---------------+-------------------------------------------------------------------------+
        | Name (Value)  | Description                                                             |
        +===============+=========================================================================+
        | Disabled (0)  | Disables the optimized path for signal bandwidth.                       |
        +---------------+-------------------------------------------------------------------------+
        | Enabled (1)   | Enables the optimized path for signal bandwidth.                        |
        +---------------+-------------------------------------------------------------------------+
        | Automatic (2) | Automatically enables the optimized path based on other configurations. |
        +---------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.OptimizePathForSignalBandwidth, int):
                Optimizes RF path for the signal bandwidth that is centered on the IQ carrier frequency.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.OptimizePathForSignalBandwidth else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string,
                attributes.AttributeID.OPTIMIZE_PATH_FOR_SIGNAL_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_input_isolation_enabled(self, selector_string):
        r"""Gets whether input isolation is enabled.

        Enabling this attribute isolates the input signal at the RF IN connector on the RF downconverter from the rest
        of the RF downconverter signal path. Disabling this attribute reintegrates the input signal into the RF downconverter
        signal path.

        .. note::
           If you enable input isolation for your device, the device impedance is changed from the characteristic 50-ohm
           impedance. A change in the device impedance may increase the VSWR value higher than the device specifications.

        For PXIe-5830/5831/5832, input isolation is supported for all available ports for your hardware configuration.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +--------------+-------------------------------------------+
        | Name (Value) | Description                               |
        +==============+===========================================+
        | Disabled (0) | Indicates that the attribute is disabled. |
        +--------------+-------------------------------------------+
        | Enabled (1)  | Indicates that the attribute is enabled.  |
        +--------------+-------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.InputIsolationEnabled):
                Specifies whether input isolation is enabled.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.INPUT_ISOLATION_ENABLED.value
            )
            attr_val = enums.InputIsolationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_input_isolation_enabled(self, selector_string, value):
        r"""Sets whether input isolation is enabled.

        Enabling this attribute isolates the input signal at the RF IN connector on the RF downconverter from the rest
        of the RF downconverter signal path. Disabling this attribute reintegrates the input signal into the RF downconverter
        signal path.

        .. note::
           If you enable input isolation for your device, the device impedance is changed from the characteristic 50-ohm
           impedance. A change in the device impedance may increase the VSWR value higher than the device specifications.

        For PXIe-5830/5831/5832, input isolation is supported for all available ports for your hardware configuration.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is **Disabled**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        +--------------+-------------------------------------------+
        | Name (Value) | Description                               |
        +==============+===========================================+
        | Disabled (0) | Indicates that the attribute is disabled. |
        +--------------+-------------------------------------------+
        | Enabled (1)  | Indicates that the attribute is enabled.  |
        +--------------+-------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.InputIsolationEnabled, int):
                Specifies whether input isolation is enabled.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.InputIsolationEnabled else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.INPUT_ISOLATION_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_thermal_correction_headroom_range(self, selector_string):
        r"""Gets the expected thermal operating range of the instrument from the self-calibration temperature returned from
        the :py:attr:`~nirfmxinstr.attributes.AttributeID.DEVICE_TEMPERATURE` attribute. This value is expressed in degree
        Celsius.

        For example, if this attribute is set to 5.0, and the device is self-calibrated at 35 degrees Celsius, then you
        can expect to run the device from 30 degrees Celsius to 40 degrees Celsius with corrected accuracy and no overflows.
        Setting this attribute with a smaller value can result in improved dynamic range, but you must ensure thermal stability
        while the instrument is running. Operating the instrument outside of the specified range may cause degraded performance
        and ADC or DSP overflows.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default value**

        +-------------------------------+-------------+
        | Name (value)                  | Description |
        +===============================+=============+
        | PXIe-5830/5831/5832/5842/5860 | 5           |
        +-------------------------------+-------------+
        | PXIe-5840/5841                | 10          |
        +-------------------------------+-------------+

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the expected thermal operating range of the instrument from the self-calibration temperature returned from
                the :py:attr:`~nirfmxinstr.attributes.AttributeID.DEVICE_TEMPERATURE` attribute. This value is expressed in degree
                Celsius.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.THERMAL_CORRECTION_HEADROOM_RANGE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_thermal_correction_headroom_range(self, selector_string, value):
        r"""Sets the expected thermal operating range of the instrument from the self-calibration temperature returned from
        the :py:attr:`~nirfmxinstr.attributes.AttributeID.DEVICE_TEMPERATURE` attribute. This value is expressed in degree
        Celsius.

        For example, if this attribute is set to 5.0, and the device is self-calibrated at 35 degrees Celsius, then you
        can expect to run the device from 30 degrees Celsius to 40 degrees Celsius with corrected accuracy and no overflows.
        Setting this attribute with a smaller value can result in improved dynamic range, but you must ensure thermal stability
        while the instrument is running. Operating the instrument outside of the specified range may cause degraded performance
        and ADC or DSP overflows.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default value**

        +-------------------------------+-------------+
        | Name (value)                  | Description |
        +===============================+=============+
        | PXIe-5830/5831/5832/5842/5860 | 5           |
        +-------------------------------+-------------+
        | PXIe-5840/5841                | 10          |
        +-------------------------------+-------------+

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the expected thermal operating range of the instrument from the self-calibration temperature returned from
                the :py:attr:`~nirfmxinstr.attributes.AttributeID.DEVICE_TEMPERATURE` attribute. This value is expressed in degree
                Celsius.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string,
                attributes.AttributeID.THERMAL_CORRECTION_HEADROOM_RANGE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_temperature_read_interval(self, selector_string):
        r"""Gets the minimum time difference between temperature sensor readings. This value is expressed in seconds.

        When you call the RFmx Initiate method, RFmx checks if the amount of time specified by this attribute has elapsed
        before reading the hardware temperature.

        .. note::
           RFmx ignores Temperature Read Interval attribute if you read the
           :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_GAIN` attribute.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 30 seconds.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the minimum time difference between temperature sensor readings. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.TEMPERATURE_READ_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_temperature_read_interval(self, selector_string, value):
        r"""Sets the minimum time difference between temperature sensor readings. This value is expressed in seconds.

        When you call the RFmx Initiate method, RFmx checks if the amount of time specified by this attribute has elapsed
        before reading the hardware temperature.

        .. note::
           RFmx ignores Temperature Read Interval attribute if you read the
           :py:attr:`~nirfmxinstr.attributes.AttributeID.DOWNCONVERTER_GAIN` attribute.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        The default value is 30 seconds.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the minimum time difference between temperature sensor readings. This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.TEMPERATURE_READ_INTERVAL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_thermal_correction_temperature_resolution(self, selector_string):
        r"""Gets the temperature change required before RFmx recalculates the thermal correction settings when entering the
        running state. This value is expressed in degree Celsius.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default value**

        +-------------------------------+-------------+
        | Name (value)                  | Description |
        +===============================+=============+
        | PXIe-5830/5831/5832/5842/5860 | 0.2         |
        +-------------------------------+-------------+
        | PXIe-5840/5841                | 1.0         |
        +-------------------------------+-------------+

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the temperature change required before RFmx recalculates the thermal correction settings when entering the
                running state. This value is expressed in degree Celsius.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string,
                attributes.AttributeID.THERMAL_CORRECTION_TEMPERATURE_RESOLUTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_thermal_correction_temperature_resolution(self, selector_string, value):
        r"""Sets the temperature change required before RFmx recalculates the thermal correction settings when entering the
        running state. This value is expressed in degree Celsius.

        You do not need to use a selector string if you want to configure this attribute for all signal instances.
        Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax.

        **Default value**

        +-------------------------------+-------------+
        | Name (value)                  | Description |
        +===============================+=============+
        | PXIe-5830/5831/5832/5842/5860 | 0.2         |
        +-------------------------------+-------------+
        | PXIe-5840/5841                | 1.0         |
        +-------------------------------+-------------+

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the temperature change required before RFmx recalculates the thermal correction settings when entering the
                running state. This value is expressed in degree Celsius.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string,
                attributes.AttributeID.THERMAL_CORRECTION_TEMPERATURE_RESOLUTION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_raw_iq_records(self, selector_string):
        r"""Gets the number of raw IQ records to acquire to complete measurement averaging.

        .. note::
           This attribute returns a value of 0 when RFmx cannot provide I/Q data for the specified measurement configuration.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the number of raw IQ records to acquire to complete measurement averaging.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.NUMBER_OF_RAW_IQ_RECORDS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_digital_gain(self, selector_string):
        r"""Gets the scaling factor applied to the time-domain voltage data in the digitizer. This value is expressed in dB.
        RFmx does not compensate for the specified digital gain.

        You can use this attribute to account for external gain changes without changing the analog signal path.

        .. note::
           The PXIe-5644/5645/5646 applies this gain when the data is scaled. The raw data does not include this scaling on these
           devices.

        **Default Value**
        : 0 dB

        **Supported Devices**
        : PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the scaling factor applied to the time-domain voltage data in the digitizer. This value is expressed in dB.
                RFmx does not compensate for the specified digital gain.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DIGITAL_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_digital_gain(self, selector_string, value):
        r"""Sets the scaling factor applied to the time-domain voltage data in the digitizer. This value is expressed in dB.
        RFmx does not compensate for the specified digital gain.

        You can use this attribute to account for external gain changes without changing the analog signal path.

        .. note::
           The PXIe-5644/5645/5646 applies this gain when the data is scaled. The raw data does not include this scaling on these
           devices.

        **Default Value**
        : 0 dB

        **Supported Devices**
        : PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the scaling factor applied to the time-domain voltage data in the digitizer. This value is expressed in dB.
                RFmx does not compensate for the specified digital gain.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.DIGITAL_GAIN.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_self_calibration_validity_check(self, selector_string):
        r"""Gets whether the RFmx driver validates the self-calibration data.

        You can specify the time interval required to perform the check using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK_TIME_INTERVAL` attribute.

        NI recommends to perform self-calibration using the :py:meth:`self_calibrate` method when RFmx reports an
        invalid self-calibration data warning.

        .. note::
           The RFmx driver does not consider self-calibration range data during self calibration validity check.

        The default value is **Off**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646,
        PXIe-5820/5830/5831/5832/5833/5840/5841/5842/5860

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Off (0)      | Indicates that RFmx does not check whether device self-calibration data is valid.                                        |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Enabled (1)  | Indicates that RFmx checks whether device self-calibration data is valid and reports a warning from the RFmx Commit and  |
        |              | RFmx Initiate methods when the data is invalid.                                                                          |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SelfCalibrationValidityCheck):
                Specifies whether the RFmx driver validates the self-calibration data.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK.value
            )
            attr_val = enums.SelfCalibrationValidityCheck(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_self_calibration_validity_check(self, selector_string, value):
        r"""Sets whether the RFmx driver validates the self-calibration data.

        You can specify the time interval required to perform the check using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK_TIME_INTERVAL` attribute.

        NI recommends to perform self-calibration using the :py:meth:`self_calibrate` method when RFmx reports an
        invalid self-calibration data warning.

        .. note::
           The RFmx driver does not consider self-calibration range data during self calibration validity check.

        The default value is **Off**.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646,
        PXIe-5820/5830/5831/5832/5833/5840/5841/5842/5860

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Off (0)      | Indicates that RFmx does not check whether device self-calibration data is valid.                                        |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Enabled (1)  | Indicates that RFmx checks whether device self-calibration data is valid and reports a warning from the RFmx Commit and  |
        |              | RFmx Initiate methods when the data is invalid.                                                                          |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SelfCalibrationValidityCheck, int):
                Specifies whether the RFmx driver validates the self-calibration data.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.SelfCalibrationValidityCheck else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_self_calibration_validity_check_time_interval(self, selector_string):
        r"""Gets the minimum time between two self calibration validity checks. This value is expressed in seconds.

        When you call RFmx Commit or Initiate methods by enabling the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK` attribute, the RFmx driver checks if the
        amount of time specified by the Self Calibration Validity Check Time Interval attribute has elapsed before validating
        the calibration data.

        The default value is 30 seconds.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646,
        PXIe-5820/5830/5831/5832/5833/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the minimum time between two self calibration validity checks. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string,
                attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK_TIME_INTERVAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_self_calibration_validity_check_time_interval(self, selector_string, value):
        r"""Sets the minimum time between two self calibration validity checks. This value is expressed in seconds.

        When you call RFmx Commit or Initiate methods by enabling the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK` attribute, the RFmx driver checks if the
        amount of time specified by the Self Calibration Validity Check Time Interval attribute has elapsed before validating
        the calibration data.

        The default value is 30 seconds.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646,
        PXIe-5820/5830/5831/5832/5833/5840/5841/5842/5860

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the minimum time between two self calibration validity checks. This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                selector_string,
                attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK_TIME_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_sharing_mode(self, selector_string):
        r"""Gets the RFmx session with the respective LO sharing mode.

        The following figures illustrate different connection configuration topologies for different LO Sharing modes.

        You must set the :py:attr:`~nirfmxinstr.attributes.AttributeID.NUMBER_OF_LO_SHARING_GROUPS` attribute to 1 for
        the following LO connection configurations.
        <img src="Fig1.png" />
        <img src="Fig2.png" />
        <img src="Fig9.png" />

        You must set the Num LO Sharing Groups attribute to 2 for the following LO connection configurations.
        <img src="Fig3.png" />
        <img src="Fig4.png" />

        The default value is **Disabled**.

        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                 | Description                                                                                                              |
        +==============================+==========================================================================================================================+
        | Disabled (0)                 | LO Sharing is disabled.                                                                                                  |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | External Star (3)            | The LO connection configuration is configured as External Star.                                                          |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | External Daisy Chain (4)     | The LO connection configuration is configured as External Daisy Chain.                                                   |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Splitter and Daisy Chain (5) | The LO connection configuration is configured as Splitter and Daisy Chain.                                               |
        |                              | With this option, the only allowed value for the Number of LO Sharing Groups attribute is 1.                             |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LOSharingMode):
                Specifies the RFmx session with the respective LO sharing mode.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_SHARING_MODE.value
            )
            attr_val = enums.LOSharingMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_sharing_mode(self, selector_string, value):
        r"""Sets the RFmx session with the respective LO sharing mode.

        The following figures illustrate different connection configuration topologies for different LO Sharing modes.

        You must set the :py:attr:`~nirfmxinstr.attributes.AttributeID.NUMBER_OF_LO_SHARING_GROUPS` attribute to 1 for
        the following LO connection configurations.
        <img src="Fig1.png" />
        <img src="Fig2.png" />
        <img src="Fig9.png" />

        You must set the Num LO Sharing Groups attribute to 2 for the following LO connection configurations.
        <img src="Fig3.png" />
        <img src="Fig4.png" />

        The default value is **Disabled**.

        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                 | Description                                                                                                              |
        +==============================+==========================================================================================================================+
        | Disabled (0)                 | LO Sharing is disabled.                                                                                                  |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | External Star (3)            | The LO connection configuration is configured as External Star.                                                          |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | External Daisy Chain (4)     | The LO connection configuration is configured as External Daisy Chain.                                                   |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Splitter and Daisy Chain (5) | The LO connection configuration is configured as Splitter and Daisy Chain.                                               |
        |                              | With this option, the only allowed value for the Number of LO Sharing Groups attribute is 1.                             |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LOSharingMode, int):
                Specifies the RFmx session with the respective LO sharing mode.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = value.value if type(value) is enums.LOSharingMode else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.LO_SHARING_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_lo_sharing_groups(self, selector_string):
        r"""Gets the RFmx session with the number of LO sharing groups.

        The default value is 1.

        The valid values are 1 and 2.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the RFmx session with the number of LO sharing groups.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.NUMBER_OF_LO_SHARING_GROUPS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_lo_sharing_groups(self, selector_string, value):
        r"""Sets the RFmx session with the number of LO sharing groups.

        The default value is 1.

        The valid values are 1 and 2.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the RFmx session with the number of LO sharing groups.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.NUMBER_OF_LO_SHARING_GROUPS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_splitter_loss_frequency(self, selector_string):
        r"""Gets the frequencies corresponding to the insertion loss inherent to the RF Splitter, as specified by the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY` attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequencies corresponding to the insertion loss inherent to the RF Splitter, as specified by the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64_array(  # type: ignore
                selector_string, attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_splitter_loss_frequency(self, selector_string, value):
        r"""Sets the frequencies corresponding to the insertion loss inherent to the RF Splitter, as specified by the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY` attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequencies corresponding to the insertion loss inherent to the RF Splitter, as specified by the
                :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY` attribute. This value is expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64_array(  # type: ignore
                selector_string, attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lo_splitter_loss(self, selector_string):
        r"""Gets an array of the insertion losses inherent to the RF Splitter. This value is expressed in dB.

        You must specify the frequencies at which the losses were measured using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the insertion losses inherent to the RF Splitter. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64_array(  # type: ignore
                selector_string, attributes.AttributeID.LO_SPLITTER_LOSS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lo_splitter_loss(self, selector_string, value):
        r"""Sets an array of the insertion losses inherent to the RF Splitter. This value is expressed in dB.

        You must specify the frequencies at which the losses were measured using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the insertion losses inherent to the RF Splitter. This value is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.set_attribute_f64_array(  # type: ignore
                selector_string, attributes.AttributeID.LO_SPLITTER_LOSS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_load_options(self, selector_string):
        r"""Gets the configurations to skip while loading from a file using the :py:meth:`load_configurations` method .

        +------------------+----------------------------------------------------------------+
        | Name (value)     | Description                                                    |
        +==================+================================================================+
        | Skip None (0)    | RFmx loads all the configurations to the session.              |
        +------------------+----------------------------------------------------------------+
        | Skip RFInstr (1) | RFmx skips loading the RFmxInstr configurations to the session |
        +------------------+----------------------------------------------------------------+

        The default value is an empty array.

        +------------------+-----------------------------------------------------------------+
        | Name (Value)     | Description                                                     |
        +==================+=================================================================+
        | Skip None (0)    | RFmx loads all the configurations to the session.               |
        +------------------+-----------------------------------------------------------------+
        | Skip RFInstr (1) | RFmx skips loading the RFmxInstr configurations to the session. |
        +------------------+-----------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LoadOptions):
                Specifies the configurations to skip while loading from a file using the :py:meth:`load_configurations` method .

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32_array(  # type: ignore
                selector_string, attributes.AttributeID.LOAD_OPTIONS.value
            )
            attr_val = enums.LoadOptions(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_load_options(self, selector_string, value):
        r"""Sets the configurations to skip while loading from a file using the :py:meth:`load_configurations` method .

        +------------------+----------------------------------------------------------------+
        | Name (value)     | Description                                                    |
        +==================+================================================================+
        | Skip None (0)    | RFmx loads all the configurations to the session.              |
        +------------------+----------------------------------------------------------------+
        | Skip RFInstr (1) | RFmx skips loading the RFmxInstr configurations to the session |
        +------------------+----------------------------------------------------------------+

        The default value is an empty array.

        +------------------+-----------------------------------------------------------------+
        | Name (Value)     | Description                                                     |
        +==================+=================================================================+
        | Skip None (0)    | RFmx loads all the configurations to the session.               |
        +------------------+-----------------------------------------------------------------+
        | Skip RFInstr (1) | RFmx skips loading the RFmxInstr configurations to the session. |
        +------------------+-----------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LoadOptions, int):
                Specifies the configurations to skip while loading from a file using the :py:meth:`load_configurations` method .

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            value = (
                [v.value for v in value]
                if (
                    isinstance(value, list) and all(isinstance(v, enums.LoadOptions) for v in value)
                )
                else value
            )
            error_code = self._interpreter.set_attribute_i32_array(  # type: ignore
                selector_string, attributes.AttributeID.LOAD_OPTIONS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_recommended_acquisition_type(self, selector_string):
        r"""Gets the recommended acquisition type for the last committed measurement configuration.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | IQ (0)             | Indicates that the recommended acquisition type is I/Q. Use the Analyze (IQ) method to perform the measurement.          |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Spectral (1)       | Indicates that the recommended acquisition type is Spectral. Use Analyze (Spectrum) method to perform the measurement.   |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | IQ or Spectral (2) | Indicates that the recommended acquisition type is I/Q or Spectral. Use either Analyze (IQ) or Analyze (Spectrum)        |
        |                    | method to perform the measurement.                                                                                       |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.RecommendedAcquisitionType):
                Returns the recommended acquisition type for the last committed measurement configuration.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_ACQUISITION_TYPE.value
            )
            attr_val = enums.RecommendedAcquisitionType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_center_frequency(self, selector_string):
        r"""Gets the recommended center frequency of the RF signal. This value is expressed in Hz.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended center frequency of the RF signal. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_CENTER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_number_of_records(self, selector_string):
        r"""Gets the recommended number of records to acquire to complete measurement averaging.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the recommended number of records to acquire to complete measurement averaging.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_NUMBER_OF_RECORDS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_trigger_minimum_quiet_time(self, selector_string):
        r"""Gets the recommended minimum quiet time during which the signal level must be below the trigger value for triggering
        to occur. This value is expressed in seconds.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended minimum quiet time during which the signal level must be below the trigger value for triggering
                to occur. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_TRIGGER_MINIMUM_QUIET_TIME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_iq_acquisition_time(self, selector_string):
        r"""Gets the recommended acquisition time for I/Q acquisition. This value is expressed in seconds.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended acquisition time for I/Q acquisition. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_IQ_ACQUISITION_TIME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_iq_minimum_sample_rate(self, selector_string):
        r"""Gets the recommended minimum sample rate for I/Q acquisition. This value is expressed in Hz.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended minimum sample rate for I/Q acquisition. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_IQ_MINIMUM_SAMPLE_RATE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_iq_pre_trigger_time(self, selector_string):
        r"""Gets the recommended pretrigger time for I/Q acquisition. This value is expressed in seconds.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended pretrigger time for I/Q acquisition. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_IQ_PRE_TRIGGER_TIME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_spectral_acquisition_span(self, selector_string):
        r"""Gets the recommended acquisition span for spectral acquisition. This value is expressed in Hz.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended acquisition span for spectral acquisition. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_SPECTRAL_ACQUISITION_SPAN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_spectral_fft_window(self, selector_string):
        r"""Gets the recommended FFT window type for spectral acquisition.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        +---------------------+---------------------------------------------------------------------------------------+
        | Name (Value)        | Description                                                                           |
        +=====================+=======================================================================================+
        | None (0)            | Indicates that the measurement does not use FFT windowing to reduce spectral leakage. |
        +---------------------+---------------------------------------------------------------------------------------+
        | Flat Top (1)        | Indicates a Flat Top FFT window type.                                                 |
        +---------------------+---------------------------------------------------------------------------------------+
        | Hanning (2)         | Indicates a Hanning FFT window type.                                                  |
        +---------------------+---------------------------------------------------------------------------------------+
        | Hamming (3)         | Indicates a Hamming FFT window type.                                                  |
        +---------------------+---------------------------------------------------------------------------------------+
        | Gaussian (4)        | Indicates a Gaussian FFT window type.                                                 |
        +---------------------+---------------------------------------------------------------------------------------+
        | Blackman (5)        | Indicates a Blackman FFT window type.                                                 |
        +---------------------+---------------------------------------------------------------------------------------+
        | Blackman-Harris (6) | Indicates a Blackman-Harris FFT window type.                                          |
        +---------------------+---------------------------------------------------------------------------------------+
        | Kaiser-Bessel (7)   | Indicates a Kaiser-Bessel FFT window type.                                            |
        +---------------------+---------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.RecommendedSpectralFftWindow):
                Returns the recommended FFT window type for spectral acquisition.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                selector_string, attributes.AttributeID.RECOMMENDED_SPECTRAL_FFT_WINDOW.value
            )
            attr_val = enums.RecommendedSpectralFftWindow(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_recommended_spectral_resolution_bandwidth(self, selector_string):
        r"""Gets the recommended FFT bin width for spectral acquisition. This value is expressed in Hz.

        .. note::
           This attribute is supported only when:

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or

        - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the recommended FFT bin width for spectral acquisition. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                selector_string,
                attributes.AttributeID.RECOMMENDED_SPECTRAL_RESOLUTION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def check_acquisition_status(self):
        r"""Checks the status of the acquisition. Use this method to check for any errors that may occur during acquisition, or to
        check whether RFmx has completed the acquisition operation.

        Returns:
            Tuple (acquisition_done, error_code):

            acquisition_done (bool):
                This parameter indicates whether the acquisition is complete. The default value is FALSE.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            acquisition_done, error_code = (
                self._interpreter.check_acquisition_status()  # type: ignore
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return acquisition_done, error_code

    @_raise_if_disposed
    def configure_external_attenuation_table(
        self, selector_string, table_name, frequency, external_attenuation
    ):
        r"""Stores the external attenuation table in the calibration plane specified by the **Selector String** parameter. On a
        MIMO session, the external attenuation table is stored for each MIMO port in the specified calibration plane.

        If there is only one table configured in any calibration plane, it is automatically selected as the active
        table.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which the external attenuation table is stored. This input
                accepts the calibration plane name with the "calplane::" prefix. If you do not specify the calibration plane name, the
                default calibration plane instance is used.

                On a MIMO session if you do not specify the port name, this configuration is applied to all MIMO ports in the session
                for the default calibration plane instance. To configure external attenuation table for a specific MIMO port, use the
                port specifier with or without the calplane name.

                Example: "calplane::plane1/port::myrfsa1/0".

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. For a MIMO port, the valid selector string is
                   "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". If you specify "port::all", all MIMO ports
                   are considered configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0, port::myrfsa2/0"

                "calplane::plane0/port::myrfsa1/0/if0"

            table_name (string):
                This parameter specifies the name to be associated with external attenuation table within a calibration plane. Provide
                a unique name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

            frequency (numpy.float64):
                This parameter specifies an array of frequencies in the external attenuation table. This value is expressed in Hz.

            external_attenuation (numpy.float64):
                This parameter specifies an array of attenuations corresponding to the frequency specified by the **Frequency**
                parameter. This value is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            error_code = self._interpreter.configure_external_attenuation_table(  # type: ignore
                selector_string, table_name, frequency, external_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def select_active_external_attenuation_table(self, selector_string, table_name):
        r"""Activates the external attenuation table set by the **Table Name** parameter in the calibration plane specified by the
        **Selector String** parameter. On a MIMO session, this method selects the active external attenuation table for the
        specified MIMO port. The specified table will be used for amplitude correction during measurement.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used.

                On a MIMO session, the default "" (empty string) selects the active external attenuation table for all the MIMO
                Ports. To configure external attenuation type for a specific MIMO port, use the port specifier with or without the
                calplane name.

                Example: "calplane::plane1/port::myrfsa1/0".

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. For a MIMO port, the valid selector string is
                   "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". If you specify "port::all", all ports are
                   considered configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0, port::myrfsa2/0"

                "calplane::plane0/port::myrfsa1/0/if0"

            table_name (string):
                This parameter specifies the name to be associated with external attenuation table within a calibration plane. Provide
                a unique name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            error_code = self._interpreter.select_active_external_attenuation_table(  # type: ignore
                selector_string, table_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def delete_external_attenuation_table(self, selector_string, table_name):
        r"""Deletes the external attenuation table set by the **Table Name** parameter in the calibration plane specified by the
        **Selector String** parameter. On a MIMO session, this method deletes the external attenuation table for the specified
        MIMO port.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which the external attenuation table is stored. This input
                accepts the calibration plane name with the "calplane::" prefix. If you do not specify the calibration plane name, the
                default calibration plane instance is used.

                On a MIMO session, the default "" (empty string) deletes the active external attenuation table for all the MIMO
                Ports. To delete an external attenuation type for a specific MIMO port, use the port specifier with or without the
                calplane name.

                Example: "calplane::plane1/port::myrfsa1/0".

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. For a MIMO port, the valid selector string is
                   "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". If you specify "port::all", all MIMO ports
                   are considered configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0, port::myrfsa2/0"

                "calplane::plane0/port::myrfsa1/0/if0"

            table_name (string):
                This parameter specifies the name to be associated with external attenuation table within a calibration plane. Provide
                a unique name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            error_code = self._interpreter.delete_external_attenuation_table(  # type: ignore
                selector_string, table_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def delete_all_external_attenuation_tables(self, selector_string):
        r"""Deletes all the external attenuation tables in the calibration plane specified by the **Selector String** parameter. On
        a MIMO session, this method deletes all the external attenuation tables for the specified MIMO port.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used. If you
                specify "calplane::all", all the calibration planes are deleted.

                On a MIMO session, the default "" (empty string) deletes all the external attenuation tables for all MIMO Ports. To
                delete an external attenuation type for a specific MIMO port, use the port specifier with or without the calplane name.

                Example: "calplane::plane1/port::myrfsa1/0".

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. For a MIMO port, the valid selector string is
                   "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". If you specify "port::all", all MIMO ports
                   are considered configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::all"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

                "calplane::all/port::all"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0, port::myrfsa2/0"

                "calplane::plane0/port::myrfsa1/0/if0"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.delete_all_external_attenuation_tables(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def enable_calibration_plane(self, selector_string):
        r"""Enables the calibration plane specified by the **Selector String** parameter for amplitude correction.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which the external attenuation table or S-parameter is stored.
                This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the calibration plane
                name, the default calibration plane instance is used. If "calplane::all" is
                specified, all the calibration planes are enabled.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::all"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.enable_calibration_plane(selector_string)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def disable_calibration_plane(self, selector_string):
        r"""Disables the calibration plane specified by the **Selector String** parameter for amplitude correction.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which the external attenuation table is stored. This input
                accepts the calibration plane name with the "calplane::" prefix. If you do not specify the calibration plane name, the
                default calibration plane instance is used. If you specify "calplane::all", all
                the calibration planes are disabled.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::all"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            error_code = self._interpreter.disable_calibration_plane(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def check_if_signal_exists(self, signal_name):
        r"""Returns whether the signal you specify in the **Signal Name** parameter exists, and also returns the corresponding
        personality of the signal, if the signal exists. This method does not support an empty ("") signal name.

        Args:
            signal_name (string):
                This parameter specifies the name of the signal. This parameter accepts the signal name with or without the "signal::"
                prefix.

                **Example:**

                "signal::sig1"

                "sig1"

        Returns:
            Tuple (signal_configuration_exists, personality, error_code):

            signal_configuration_exists (bool):
                This parameter indicates whether the signal exists or not.

                +--------------+-------------------------------------------+
                | Name (value) | Description                               |
                +==============+===========================================+
                | FALSE        | Indicates that the signal does not exist. |
                +--------------+-------------------------------------------+
                | TRUE         | Indicates that the signal exists.         |
                +--------------+-------------------------------------------+

            personality (enums.Personalities):
                This parameter indicates the personality of the signal if the signal exists.

                +--------------+----------------------------------------------------+
                | Name (Value) | Description                                        |
                +==============+====================================================+
                | None (0)     | Indicates that the given signal does not exist.    |
                +--------------+----------------------------------------------------+
                | SpecAn (1)   | Indicates that the signal personality is SpecAn.   |
                +--------------+----------------------------------------------------+
                | Demod (2)    | Indicates that the signal personality is Demod.    |
                +--------------+----------------------------------------------------+
                | LTE (4)      | Indicates that the signal personality is LTE.      |
                +--------------+----------------------------------------------------+
                | GSM (8)      | Indicates that the signal personality is GSM.      |
                +--------------+----------------------------------------------------+
                | WCDMA (16)   | Indicates that the signal personality is WCDMA.    |
                +--------------+----------------------------------------------------+
                | CDMA2k (32)  | Indicates that the signal personality is CDMA2k.   |
                +--------------+----------------------------------------------------+
                | TDSCDMA (64) | Indicates that the signal personality is TD-SCDMA. |
                +--------------+----------------------------------------------------+
                | EVDO (128)   | Indicates that the signal personality is EV-DO.    |
                +--------------+----------------------------------------------------+
                | NR (256)     | Indicates that the signal personality is NR.       |
                +--------------+----------------------------------------------------+
                | WLAN (512)   | Indicates that the signal personality is WLAN.     |
                +--------------+----------------------------------------------------+
                | BT (1024)    | Indicates that the signal personality is BT.       |
                +--------------+----------------------------------------------------+

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(signal_name, "signal_name")
            signal_configuration_exists, personality, error_code = self._interpreter.check_if_signal_exists(  # type: ignore
                signal_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return signal_configuration_exists, personality, error_code

    @_raise_if_disposed
    def load_s_parameter_external_attenuation_table_from_s2p_file(
        self, selector_string, table_name, s2p_file_path, s_parameter_orientation
    ):
        r"""Stores the S-parameter table from the S2P file in the calibration plane specified by the **Selector String** parameter.
        S-parameter tables are used for fixture de-embedding. On a MIMO session, the S-parameter table is stored for each MIMO
        port in the specified calibration plane.

        .. note::
           If there is only one table configured in any calibration plane, it is automatically selected as the active table.

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which the external attenuation table is stored. This input
                accepts the calibration plane name with the "calplane::" prefix. If you do not specify the calibration plane name, the
                default calibration plane instance is used.

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. For a MIMO port, the valid selector string is
                   "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". If you specify "port::all", all MIMO ports
                   are considered configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0, port::myrfsa2/0"

                "calplane::plane0/port::myrfsa1/0/if0"

            table_name (string):
                This parameter specifies the name to be associated with S-parameter table within a calibration plane. Provide a unique
                name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

            s2p_file_path (string):
                This parameter specifies the path to the S2P file that contains S-parameter table information for the specified port.

            s_parameter_orientation (enums.SParameterOrientation, int):
                This parameter specifies the orientation of the data in the S-parameter table relative to the port you specify. The
                default value is **Port2 Towards DUT**.

                +-----------------------+------------------------------------------------+
                | Name (Value)          | Description                                    |
                +=======================+================================================+
                | Port1 Towards DUT (0) | Port 1 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+
                | Port2 Towards DUT (1) | Port 2 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            _helper.validate_not_none(s2p_file_path, "s2p_file_path")
            s_parameter_orientation = (
                s_parameter_orientation.value
                if type(s_parameter_orientation) is enums.SParameterOrientation
                else s_parameter_orientation
            )
            error_code = self._interpreter.load_s_parameter_external_attenuation_table_from_s2p_file(  # type: ignore
                selector_string, table_name, s2p_file_path, s_parameter_orientation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_external_attenuation_interpolation_nearest(self, selector_string, table_name):
        r"""Selects the nearest interpolation method when interpolating S-parameters for a specified table. The parameters of the
        table nearest to the carrier frequency are used.

        .. note::
           Currently interpolation is supported only for S-parameter tables.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used.

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

            table_name (string):
                This parameter specifies the name to be associated with either the S-parameter table or the external attenuation table
                within a calibration plane. Provide a unique name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            error_code = self._interpreter.configure_external_attenuation_interpolation_nearest(  # type: ignore
                selector_string, table_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_external_attenuation_interpolation_linear(
        self, selector_string, table_name, format
    ):
        r"""Selects the linear interpolation method when interpolating S-parameters for the specified table. If the carrier
        frequency does not match a row in the S-parameter table, this method performs a linear interpolation based on the
        entries above and below the row in the table.

        .. note::
           Currently interpolation is supported only for S-parameter tables.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used.

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

            table_name (string):
                This parameter specifies the name to be associated with either the S-parameter table or the external attenuation table
                within a calibration plane. Provide a unique name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

            format (enums.LinearInterpolationFormat, int):
                This parameter specifies the format of parameters to interpolate. The default value is **Real and Imaginary**.

                +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)                 | Description                                                                                                              |
                +==============================+==========================================================================================================================+
                | Real and Imaginary (0)       | Results in a linear interpolation of the real portion of the complex number and a separate linear interpolation of the   |
                |                              | complex portion.                                                                                                         |
                +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Magnitude and Phase (1)      | Results in a linear interpolation.                                                                                       |
                +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Magnitude and Phase (dB) (2) | Results in a linear interpolation.                                                                                       |
                +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            format = format.value if type(format) is enums.LinearInterpolationFormat else format
            error_code = self._interpreter.configure_external_attenuation_interpolation_linear(  # type: ignore
                selector_string, table_name, format
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_external_attenuation_interpolation_spline(self, selector_string, table_name):
        r"""Selects the spline interpolation method when interpolating parameters for the specified table. If the carrier frequency
        does not match a row in the S-parameter table, this method performs a spline interpolation based on the entries above
        and below the row in the table.

        .. note::
           Currently interpolation is supported only for S-parameter tables.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used.

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. Use :py:meth:`get_available_ports` method to get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

            table_name (string):
                This parameter specifies the name to be associated with either the S-parameter table or the external attenuation table
                within a calibration plane. Provide a unique name, such as "table1" to configure the table.
                The default value is "" (empty string).

                **Example:**

                ""

                "table1"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            error_code = self._interpreter.configure_external_attenuation_interpolation_spline(  # type: ignore
                selector_string, table_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_s_parameter_external_attenuation_type(self, selector_string, s_parameter_type):
        r"""Configures the type of S-parameter to apply to measurements on the specified port for a Calplane. You can use the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ input to specify the name
        of the Calplane and port to configure for S-parameter.

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used.

                On a MIMO session if you do not specify the port name, this configuration is applied to all MIMO ports in the session
                for the default calibration plane instance. To configure S-parameter external attenuation type for a specific MIMO
                port, use the port specifier with or without the calplane name.

                Example: "calplane::plane1/port::myrfsa1/0".

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". If you specify "port::all", all ports are  considered
                   configured. Use :py:meth:`get_available_ports` method to get the valid port names. For a MIMO port, the valid selector
                   string is "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". If you specify "port::all", all
                   MIMO ports are considered configured.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::all"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0, port::myrfsa2/0"

                "calplane::plane0/port::myrfsa1/0/if0"

            s_parameter_type (enums.SParameterType, int):
                This parameter specifies the type of S-parameter which applies to measurements on the specified port for a Calplane. If
                you set this parameter to **Scalar** or **Vector**, RFmx adjusts the instrument settings and the returned data to
                remove the effects of the external network between the instrument and the DUT.

                **PXIe-5831/5832**: Valid values for this parameter are **Scalar** and **Vector**. **Vector** is only supported
                for TRX ports in a semiconductor test system (STS).

                **PXIe-5840/5841/5842/5860**: The only valid value for this parameter is **Scalar**.

                The default value is **Scalar**.

                +--------------+------------------------------------------------------------------------+
                | Name (Value) | Description                                                            |
                +==============+========================================================================+
                | Scalar (1)   | De-embeds the measurement using the gain term.                         |
                +--------------+------------------------------------------------------------------------+
                | Vector (2)   | De-embeds the measurement using the gain term and the reflection term. |
                +--------------+------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            s_parameter_type = (
                s_parameter_type.value
                if type(s_parameter_type) is enums.SParameterType
                else s_parameter_type
            )
            error_code = self._interpreter.configure_s_parameter_external_attenuation_type(  # type: ignore
                selector_string, s_parameter_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def send_software_edge_start_trigger(self):
        r"""Sends a trigger to the waiting device when you choose a software version of Start trigger. You can also use this method
        to override a hardware trigger.

        This method returns an error if:

        - You configure an invalid trigger.

        - You have not previously called the RFmx Initiate method.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.send_software_edge_start_trigger()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def send_software_edge_advance_trigger(self):
        r"""Sends a trigger to the waiting device when you choose a software version of the Advance trigger. You can also use this
        method to override a hardware trigger.

        This method returns an error if:

        - You configure an invalid trigger.

        - You have not previously called the RFmx Initiate method.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
        PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.send_software_edge_advance_trigger()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency_reference(
        self, selector_string, frequency_reference_source, frequency_reference_frequency
    ):
        r"""Configures the Reference Clock and the frequency reference source.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            frequency_reference_source (string):
                This parameter specifies the frequency reference source.

                The default value for PXIe-5840 with PXIe-5653 is **RefIn2**, else the default value is **OnboardClock**.

                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)                  | Description                                                                                                              |
                +===============================+==========================================================================================================================+
                | OnboardClock (OnboardClock)   | PXIe-5663/5663E: RFmx locks the PXIe-5663/5663E to the PXIe-5652 LO source onboard clock. Connect the REF OUT2           |
                |                               | connector (if it exists) on the PXIe-5652 to the PXIe-5622 CLK IN terminal. On versions of the PXIe-5663/5663E that      |
                |                               | lack a REF OUT2 connector on the PXIe-5652, connect the REF IN/OUT connector on the PXIe-5652 to the PXIe-5622 CLK IN    |
                |                               | terminal.PXIe-5665: RFmx locks the PXIe-5665 to the PXIe-5653 LO source onboard clock. Connect the 100 MHz REF OUT       |
                |                               | terminal on the PXIe-5653 to the PXIe-5622 CLK IN terminal.PXIe-5668: Lock the PXIe-5668 to the PXIe-5653 LO SOURCE      |
                |                               | onboard clock. Connect the LO2 OUT connector on the PXIe-5606 to the CLK IN connector on the                             |
                |                               | PXIe-5624.PXIe-5644/5645/5646, PXIe-5820/5840/5841/5842/5860: RFmx locks the device to its onboard                       |
                |                               | clock.PXIe-5830/5831/5832: For PXIe-5830, connect the PXIe-5820 REF IN connector to the PXIe-3621 REF OUT connector.     |
                |                               | For PXIe-5831, connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. For PXIe-5832, connect the     |
                |                               | PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector.PXIe-5831 with PXIe-5653: Connect the PXIe-5820 REF IN     |
                |                               | connector to the PXIe-3622 REF OUT connector. Connect the PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3622 REF IN   |
                |                               | connector.PXIe-5832 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector. Connect   |
                |                               | the PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3623 REF IN connector.PXIe-5842: Lock to the PXIe-5655 onboard      |
                |                               | clock. Cables between modules are required as shown in the Getting Started Guide for the instrument.PXIe-5860:Lock to    |
                |                               | the PXIe-5860 onboard clock                                                                                              |
                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | RefIn (RefIn)                 | PXIe-5663/5663E: Connect the external signal to the PXIe-5652 REF IN/OUT connector. Connect the REF OUT2 connector (if   |
                |                               | it exists) on the PXIe-5652 to the PXIe-5622 CLK IN terminal.PXIe-5665: Connect the external signal to the PXIe-5653     |
                |                               | REF IN connector. Connect the 100 MHz REF OUT terminal on the PXIe-5653 to the PXIe-5622 CLK IN connector. If your       |
                |                               | external clock signal frequency is set to a frequency other than 10 MHz, set the Frequency Reference Frequency           |
                |                               | attribute according to the frequency of your external clock signal.PXIe-5668: Connect the external signal to the         |
                |                               | PXIe-5653 REF IN connector. Connect the LO2 OUT on the PXIe-5606 to the CLK IN connector on the PXIe-5622. If your       |
                |                               | external clock signal frequency is set to a frequency other than 10 MHz, set the Frequency Reference Frequency           |
                |                               | attribute according to the frequency of your external clock signal.PXIe-5644/5645/5646, PXIe-5820/5840/5841/5842: RFmx   |
                |                               | locks the device to the signal at the external REF IN connector.PXIe-5830/5831/5832: For PXIe-5830, connect the          |
                |                               | PXIe-5820 REF IN connector to the PXIe-3621 REF OUT connector. For PXIe-5831, connect the PXIe-5820 REF IN connector to  |
                |                               | the PXIe-3622 REF OUT connector. For PXIe-5832, connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT          |
                |                               | connector. For PXIe-5830, lock the external signal to the PXIe-3621 REF IN connector. For PXIe-5831, lock the external   |
                |                               | signal to the PXIe-3622 REF IN connector. For PXIe-5832, lock the external signal to the PXIe-3623 REF IN                |
                |                               | connector.PXIe-5831 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3622 REF OUT connector. Connect   |
                |                               | the PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3622 REF IN connector. Lock the external signal to the PXIe-5653    |
                |                               | REF IN connector.PXIe-5832 with PXIe-5653: Connect the PXIe-5820 REF IN connector to the PXIe-3623 REF OUT connector.    |
                |                               | Connect the PXIe-5653 REF OUT (10 MHz) connector to the PXIe-3623 REF IN connector. Lock the external signal to the      |
                |                               | PXIe-5653 REF IN connector.PXIe-5842: Lock to the signal at the REF IN connector on the associated PXIe-5655. Cables     |
                |                               | between modules are required as shown in the Getting Started Guide for the instrument.PXIe-5860:Lock to the signal at    |
                |                               | the REF IN connector on the PXIe-5860.                                                                                   |
                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Clk (PXI_Clk)             | PXIe-5668: Lock the PXIe-5653 to the PXI backplane clock. Connect the PXIe-5606 LO2 OUT to the LO2 IN connector on the   |
                |                               | PXIe-5624.PXIe-5830/5831/5832/5841 with PXIe-5655/5842: Lock LO module to the PXI backplane clock. Cables between        |
                |                               | modules are required as shown in the Getting Started Guide for the instrument.PXIe-5644/5645/5646,                       |
                |                               | PXIe-5663/5663E/5665, and PXIe-5820/5840/5841/5842/5860: RFmx locks the device to the PXI backplane clock.               |
                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | ClkIn (ClkIn)                 | PXIe-5663/5663E: RFmx locks the PXIe-5663/5663E to an external 10 MHz signal. Connect the external signal to the         |
                |                               | PXIe-5622 CLK IN connector, and connect the PXIe-5622 CLK OUT connector to the FREQ REF IN connector on the              |
                |                               | PXIe-5652.PXIe-5665: RFmx locks the PXIe-5665 to an external 100 MHz signal. Connect the external signal to the          |
                |                               | PXIe-5622 CLK IN connector, and connect the PXIe-5622 CLK OUT connector to the REF IN connector on the PXIe-5653. Set    |
                |                               | the Frequency Reference Frequency attribute to 100 MHz.PXIe-5668: Lock the PXIe-5668 to an external 100 MHz signal.      |
                |                               | Connect the external signal to the CLK IN connector on the PXIe-5624, and connect the PXIe-5624 CLK OUT connector to     |
                |                               | the REF IN connector on the PXIe-5653. Set the Frequency Reference Frequency attribute to 100 MHz.PXIe-5644/5645/5646,   |
                |                               | PXIe-5820/5830/5831/5831 with PXIe-5653/5832/5832 with PXIe-5653/5840/5841/5842/5860: This configuration does not        |
                |                               | apply.                                                                                                                   |
                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | RefIn2 (RefIn2)               | Configure open NI-RFSG sessions to the device to use RefIn for the PXIe-5840 or OnboardClock for the PXIe-5840 with      |
                |                               | PXIe-5653.PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, and PXIe-5820/5830/5831/5831 with PXIe-5653/5832/5832 with     |
                |                               | PXIe-5653/5840/5841/5842/5860: This configuration does not apply.                                                        |
                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_ClkMaster (PXI_ClkMaster) | PXIe-5831 with PXIe-5653: RFmx configures the PXIe-5653 to export the reference clock and configures the PXIe-5820 and   |
                |                               | PXIe-3622 to use PXI_Clk as the reference clock source. You must connect the PXIe-5653 REF OUT (10 MHz) connector to     |
                |                               | the PXI chassis REF IN connector.PXIe-5832 with PXIe-5653: RFmx configures the PXIe-5653 to export the reference clock   |
                |                               | and configures the PXIe-5820 and PXIe-3623 to use PXI_Clk as the reference clock source. You must connect the PXIe-5653  |
                |                               | REF OUT (10 MHz) connector to the PXI chassis REF IN connector.PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646,           |
                |                               | PXIe-5820/5830/5831/5832/5840/5841/5842/5860: This configuration does not apply.                                         |
                +-------------------------------+--------------------------------------------------------------------------------------------------------------------------+

            frequency_reference_frequency (float):
                This parameter specifies the Reference Clock rate when the **Frequency Reference Source** parameter is set to **ClkIn**
                or **RefIn**. This value is expressed in Hz.

                The default value is 10 MHz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(frequency_reference_source, "frequency_reference_source")
            error_code = self._interpreter.configure_frequency_reference(  # type: ignore
                selector_string, frequency_reference_source, frequency_reference_frequency
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_mechanical_attenuation(
        self, selector_string, mechanical_attenuation_auto, mechanical_attenuation_value
    ):
        r"""Configures the mechanical attenuation and the RFmx driver attenuation hardware settings.

        **Supported devices:** PXIe-5663/5663E, PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            mechanical_attenuation_auto (enums.MechanicalAttenuationAuto, int):
                This parameter specifies whether RFmx automatically chooses an attenuation setting based on the hardware settings.

                The default value is **True**.

                +--------------+----------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                            |
                +==============+========================================================================================+
                | False (0)    | Specifies that RFmx uses the value configured in the Mechanical Attenuation parameter. |
                +--------------+----------------------------------------------------------------------------------------+
                | True (1)     | Specifies that the measurement computes the mechanical attenuation.                    |
                +--------------+----------------------------------------------------------------------------------------+

            mechanical_attenuation_value (float):
                This parameter specifies the level of mechanical attenuation for the RF path. This value is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            mechanical_attenuation_auto = (
                mechanical_attenuation_auto.value
                if type(mechanical_attenuation_auto) is enums.MechanicalAttenuationAuto
                else mechanical_attenuation_auto
            )
            error_code = self._interpreter.configure_mechanical_attenuation(  # type: ignore
                selector_string, mechanical_attenuation_auto, mechanical_attenuation_value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rf_attenuation(self, selector_string, rf_attenuation_auto, rf_attenuation_value):
        r"""Configures the nominal attenuation and the RFmx driver setting.

        **Supported devices:** PXIe-5663/5663E, PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rf_attenuation_auto (enums.RFAttenuationAuto, int):
                This parameter specifies whether RFmx computes the RF attenuation.

                If you set this parameter to **True**, RFmx automatically chooses an attenuation
                setting based on the reference level configured on the personality.

                The default value is **True**.

                +--------------+-------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                   |
                +==============+===============================================================================+
                | False (0)    | Specifies that RFmx uses the value configured using RF Attenuation parameter. |
                +--------------+-------------------------------------------------------------------------------+
                | True (1)     | Specifies that RFmx computes the RF attenuation automatically.                |
                +--------------+-------------------------------------------------------------------------------+

            rf_attenuation_value (float):
                This parameter specifies the nominal attenuation setting for all attenuators before the first mixer in the RF signal
                chain. This value is expressed in dB.

                If you set the **RF Attenuation Auto** parameter to **True**, RFmx chooses an attenuation setting
                automatically.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            rf_attenuation_auto = (
                rf_attenuation_auto.value
                if type(rf_attenuation_auto) is enums.RFAttenuationAuto
                else rf_attenuation_auto
            )
            error_code = self._interpreter.configure_rf_attenuation(  # type: ignore
                selector_string, rf_attenuation_auto, rf_attenuation_value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def wait_for_acquisition_complete(self, timeout):
        r"""Waits and blocks the data flow until the acquisition is complete. This method is typically called after a specific
        initiate method.

        Args:
            timeout (float):
                This parameter specifies the time to wait for an ongoing acquisition to complete before returning a timeout error. A
                value of -1 specifies that the method waits indefinitely for acquisition to complete. This value is expressed in
                seconds. The default value is 10.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.wait_for_acquisition_complete(timeout)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def reset_to_default(self):
        r"""Resets the RFmxInstr attributes to their default values.

        This method disables all the calibration planes.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.reset_to_default()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def reset_driver(self):
        r"""Restores the NI-RFSA driver state to a default state to avoid RFmx using any hardware or driver state that was set by
        the RF toolkits or other custom NI-RFSA code.

        Use this method when you switch back to using RFmx to perform measurements after you have used the NI-RFSA
        handle to perform measurements with RF toolkits or you have used other custom NI-RFSA code. Unlike the
        :py:meth:`reset_to_default` method, the RfmxInstr Reset Driver method does not reset RFmx attributes configured on the
        RFmx session. Hence, you do not need to set RFmx attributes again when switching back to RFmx measurements. Refer to
        `RFmx SpecAn CHP - WCDMA ModAcc - CHP Example (LabVIEW) <https://decibel.ni.com/content/docs/DOC-39161>`_  for more
        information about using RFmx to perform measurements.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.reset_driver()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def save_all_configurations(self, file_path):
        r"""Saves all the configured attributes in the RFmx session to a file in the specified file path. Use this method to save
        the current state of the RFmx session. On a MIMO session, this method saves all the configured attributes for the
        specified MIMO port.

        .. note::
           List configurations, reference waveforms and external attenuation tables are not saved by this method.

        Args:
            file_path (string):
                This parameter specifies the complete path to the file to which the configurations are to be saved. Default file
                extension: .rfmxconfig

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(file_path, "file_path")
            error_code = self._interpreter.save_all_configurations(file_path)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def reset_entire_session(self):
        r"""Deletes all the named signal in the session and resets all attributes for the default signal instances of already
        loaded personalities in the session.

        This method disables all the calibration planes.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.reset_entire_session()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def reset_attribute(self, selector_string, attribute_id):
        r"""Resets an attribute that you specify in the **attributeID** parameter to default values.

        Args:
            selector_string (string):
                Specifies the selector string for the attribute being reset. Refer to the Selector String (C or LabWindows/CVI) topic
                for more information about configuring the selector string.

            attribute_id (enums.AttributeID, int):
                Pass the ID of an attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            attribute_id = (
                attribute_id.value if type(attribute_id) is attributes.AttributeID else attribute_id
            )
            error_code = self._interpreter.reset_attribute(  # type: ignore
                selector_string, attribute_id
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def export_signal(self, export_signal_source, export_signal_output_terminal):
        r"""Routes signals (triggers, clocks, and events) to the specified output terminal.

        .. note::
           This method is not supported on a MIMO session.

        Args:
            export_signal_source (enums.ExportSignalSource, int):
                This parameter controls the source to export signals.

                +-----------------------------+---------------------------------------+
                | Name (Value)                | Description                           |
                +=============================+=======================================+
                | Start Trigger (0)           | Start trigger is sourced.             |
                +-----------------------------+---------------------------------------+
                | Ref Trigger (1)             | Reference trigger is sourced.         |
                +-----------------------------+---------------------------------------+
                | Advance Trigger (2)         | Advance trigger is sourced.           |
                +-----------------------------+---------------------------------------+
                | Ready for Start Event (3)   | Ready for Start event is sourced.     |
                +-----------------------------+---------------------------------------+
                | Ready for Advance Event (4) | Ready for Advance event is sourced.   |
                +-----------------------------+---------------------------------------+
                | Ready for Ref Event (5)     | Ready for Reference event is sourced. |
                +-----------------------------+---------------------------------------+
                | End of Record Event (6)     | End of Record event is sourced.       |
                +-----------------------------+---------------------------------------+
                | Done Event (7)              | Done event is sourced.                |
                +-----------------------------+---------------------------------------+
                | Reference Clock (8)         | Reference clock is sourced.           |
                +-----------------------------+---------------------------------------+

            export_signal_output_terminal (string):
                This parameter specifies the terminal where the signal is exported. You can also choose not to export any signal.

                The default value is "" (empty string).

                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)              | Description                                                                                                              |
                +===========================+==========================================================================================================================+
                | Do not export signal (()) | The signal is not exported.                                                                                              |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | ClkOut (ClkOut)           | Export the Reference Clock on the CLK OUT terminal on the digitizer. This value is not valid for the                     |
                |                           | PXIe-5644/5645/5646 or PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                     |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | RefOut (RefOut)           | The signal is exported to the REF IN/OUT terminal on the PXIe-5652, the REF OUT terminals on the PXIe-5653, or the REF   |
                |                           | OUT terminal on the PXIe-5644/5645/5646, or PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | RefOut2 (RefOut2)         | The signal is exported to the REF OUT2 terminal on the LO. This connector exists only on some versions of the            |
                |                           | PXIe-5652.                                                                                                               |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PFI0 (PFI0)               | The signal is exported to the PFI 0 connector on the PXIe-5142 and PXIe-5624.                                            |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PFI1 (PFI1)               | The signal is exported to the PFI 1 connector on the PXIe-5142 and PXIe-5622.                                            |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig0 (PXI_Trig0)     | The signal is exported to the PXI trigger line 0.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig1 (PXI_Trig1)     | The signal is exported to the PXI trigger line 1.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig2 (PXI_Trig2)     | The signal is exported to the PXI trigger line 2.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig3 (PXI_Trig3)     | The signal is exported to the PXI trigger line 3.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig4 (PXI_Trig4)     | The signal is exported to the PXI trigger line 4.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig5 (PXI_Trig5)     | The signal is exported to the PXI trigger line 5.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXI_Trig6 (PXI_Trig6)     | The signal is exported to the PXI trigger line 6.                                                                        |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | PXIe_DStarC (PXIe_DStarC) | The signal is exported to the PXI DStar C trigger line. This value is valid only on                                      |
                |                           | PXIe-5820/5830/5831/5832/5840/5841/5842/5860.                                                                            |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            export_signal_source = (
                export_signal_source.value
                if type(export_signal_source) is enums.ExportSignalSource
                else export_signal_source
            )
            _helper.validate_not_none(
                export_signal_output_terminal, "export_signal_output_terminal"
            )
            error_code = self._interpreter.export_signal(  # type: ignore
                export_signal_source, export_signal_output_terminal
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def self_calibrate(self, selector_string, steps_to_omit):
        r"""Self-calibrates the NI-RFSA device and associated modules that support self-calibration. If self-calibration completes
        successfully, the new calibration constants are stored immediately in the nonvolatile memory of the module. On a MIMO
        session, this method self-calibrates all NI-RFSA devices and associated modules that support self-calibration.

        Refer to the specifications document for your device for more information about how often to self-calibrate.
        For more information about Self Calibrate, refer to the *niRFSA Self Cal VI* topic for your device in the *NI RF Vector
        Signal Analyzers Help*.

        .. note::
           For PXIe-5644/5645/5646, RFmx internally closes the RFSA session, performs self-calibration and opens a new session for
           the same device. If the RFSA session has been accessed from RFmx, using the get nirfsa session method before calling
           the RFmxInstr Self Calibrate method, the RFSA session will become invalid upon calling the RFmxInstr Self Calibrate.

        **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                Specifies a selector string. Pass an empty string.

            steps_to_omit (enums.SelfCalibrateSteps, int):
                This parameter specifies which calibration steps to skip during the self-calibration process. The default value is an
                empty array, which indicates that all calibration steps are performed. The only valid value for
                PXIe-5820/5830/5831/5832/5840/5841/5842/5860 is an empty array.

                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)                | Description                                                                                                              |
                +=============================+==========================================================================================================================+
                | Preselector Alignment (1)   | Omits the Preselector Alignment step. If you omit this step and the niRFSA Is Self Cal Valid method indicates the        |
                |                             | calibration data for this step is invalid, the preselector alignment specifications are not guaranteed. This step        |
                |                             | applies only to the PXIe-5605/5606.                                                                                      |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Gain Reference (2)          | Omits the Gain Reference step. If you omit this step and the niRFSA Is Self Cal Valid method indicates the calibration   |
                |                             | data for this step is invalid, the absolute accuracy of the device is not guaranteed.                                    |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | IF Flatness (4)             | Omits the IF Flatness step. If you omit this step and the niRFSA Is Self Cal, valid method indicates the calibration     |
                |                             | data for this step is invalid, the IF flatness specifications are not guaranteed.                                        |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Digitizer Self Cal (8)      | Omits the Digitizer Self Cal step. If you omit this step and the niRFSA Is Self Cal Valid method indicates the           |
                |                             | calibration data for this step is invalid, the absolute accuracy of the device is not guaranteed.                        |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | LO Self Cal (10)            | Omits the LO Self Cal step. If you omit this step and the niRFSA Is Self Cal Valid method indicates the calibration      |
                |                             | data for this step is invalid, the LO PLL may fail to lock.                                                              |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Amplitude Accuracy (20)     | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Residual LO Power (40)      | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Image Suppression (80)      | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Synthesizer Alignment (100) | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | DC Offset (200)             | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            steps_to_omit = (
                steps_to_omit.value
                if type(steps_to_omit) is enums.SelfCalibrateSteps
                else steps_to_omit
            )
            error_code = self._interpreter.self_calibrate(  # type: ignore
                selector_string, steps_to_omit
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def self_calibrate_range(
        self,
        selector_string,
        steps_to_omit,
        minimum_frequency,
        maximum_frequency,
        minimum_reference_level,
        maximum_reference_level,
    ):
        r"""Self-calibrates all configurations within the specified frequency and reference level limits. If there is an open
        session for NI-RFSG for your device, it may remain open but cannot be used while this method runs. NI recommends that
        no external signals are present on the RF In port while the calibration is taking place. For more information about
        Self Calibrate Range, refer to the *niRFSA Self Calibrate Range* method topic for your device in the *NI RF Vector
        Signal Analyzers Help*. On a MIMO session, this method self-calibrates all NI-RFSA devices and associated modules that
        support self-calibration.

        **Supported devices:** PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842

        .. note::
           This method does not update self-calibration date and temperature. Self-calibration range data is not saved to your
           device if you restart the system.

        Args:
            selector_string (string):
                Specifies a selector string. Pass an empty string.

            steps_to_omit (enums.SelfCalibrateSteps, int):
                This parameter specifies which calibration steps to skip during the self-calibration process. The default value is an
                empty array, which indicates that all calibration steps are performed. The only valid value for the
                PXIe-5820/5830/5831/5832/5840/5841/5842 is an empty array.

                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)                | Description                                                                                                              |
                +=============================+==========================================================================================================================+
                | Preselector Alignment (1)   | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Gain Reference (2)          | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | IF Flatness (4)             | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Digitizer Self Cal (8)      | Not used by this method.                                                                                                 |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | LO Self Cal (10)            | Omits the LO Self Cal step. If you omit this step and the niRFSA Is Self Cal Valid method indicates the calibration      |
                |                             | data for this step is invalid, the LO PLL may fail to lock.                                                              |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Amplitude Accuracy (20)     | Omits the Amplitude Accuracy step. If you omit this step, the absolute accuracy ofthe device is not adjusted.            |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Residual LO Power (40)      | Omits the Residual LO Power step. If you omit this step, the Residual LO Powerperformance is not adjusted.               |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Image Suppression (80)      | Omits the Image Suppression step. If you omit this step, the Residual SidebandImage performance is not adjusted.         |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Synthesizer Alignment (100) | Omits the VCO Alignment step. If you omit this step, the LO PLL will not getadjusted.                                    |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | DC Offset (200)             | Omits the DC Offset step.                                                                                                |
                +-----------------------------+--------------------------------------------------------------------------------------------------------------------------+

            minimum_frequency (float):
                This parameter specifies the minimum frequency for the custom self calibration range. This value is expressed in Hz.

                .. note::
                   For PXIe-5830/5831/5832, only the applicable ports within the specified frequency range are calibrated.

            maximum_frequency (float):
                This parameter specifies the maximum frequency for the custom self calibration range. This value is expressed in Hz.

            minimum_reference_level (float):
                This parameter specifies the minimum reference level for the custom self calibration range. This value is expressed in
                dBm.

            maximum_reference_level (float):
                This parameter specifies the maximum reference level for the custom self calibration range. This value is expressed
                dBm.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            steps_to_omit = (
                steps_to_omit.value
                if type(steps_to_omit) is enums.SelfCalibrateSteps
                else steps_to_omit
            )
            error_code = self._interpreter.self_calibrate_range(  # type: ignore
                selector_string,
                steps_to_omit,
                minimum_frequency,
                maximum_frequency,
                minimum_reference_level,
                maximum_reference_level,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_configurations(self, file_path):
        r"""Loads the attributes of an RFmx session saved in a file. This file can be generated using
        :py:meth:`save_all_configurations` method or using the RF Signal Analyzer panel in InstrumentStudio.

        You can specify the configurations to skip while loading from a file using the
        :py:attr:`~nirfmxinstr.attributes.AttributeID.LOAD_OPTIONS` attribute.

        .. note::
           If the file contains a named signal configuration which is already present in the session, then this method will return
           an error. NI recommendeds to call the :py:meth:`reset_entire_session` method to delete all the named signal
           configurations in the session.

        Args:
            file_path (string):
                This parameter specifies the complete path to the file from which the configurations are to be loaded. Default file
                extension: .rfmxconfig

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(file_path, "file_path")
            error_code = self._interpreter.load_configurations(file_path)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def is_self_calibrate_valid(self, selector_string):
        r"""Returns an array to indicate which calibration steps contain valid calibration data. To omit steps with the valid
        calibration data from self-calibration, you can pass the **Valid Steps** parameter to the **Steps To Omit** parameter
        of the :py:meth:`self_calibrate` method. On a MIMO session, use the **Selector String** parameter to get the
        self-calibration validity for a specific MIMO port.

        **Supported devices:** PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of a MIMO port on a MIMO
                session.

                **Example:**

                ""

                "port::myrfsa1/0"

                You can use the :py:meth:`build_port_string` method to build the selector string.

        Returns:
            Tuple (self_calibrate_valid, valid_steps, error_code):

            self_calibrate_valid (int):
                This parameter returns TRUE if all the calibration data is valid and FALSE if any of the calibration data is invalid.

            valid_steps (enums.SelfCalibrateSteps):
                This parameter returns an array of valid steps.

                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)              | Description                                                                                                              |
                +===========================+==========================================================================================================================+
                | Preselector Alignment (1) | Indicates the Preselector Alignment calibration data is valid. This step generates coefficients to align the             |
                |                           | preselector across the frequency range for your device.                                                                  |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Gain Reference (2)        | Indicates the Gain Reference calibration data is valid. This step measures the changes in gain since the last external   |
                |                           | calibration was run.                                                                                                     |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | IF Flatness (4)           | Indicates the IF Flatness calibration data is valid. This step measures the IF response of the entire system for each    |
                |                           | of the supported IF filters.                                                                                             |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Digitizer Self Cal (8)    | Indicates the Digitizer Self Cal calibration data is valid. This step calls for digitizer self-calibration if the        |
                |                           | digitizer is associated with the RF downconverter.                                                                       |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | LO Self Cal (10)          | Indicates the LO Self Cal calibration data is valid. This step calls for LO self-calibration if the LO source module is  |
                |                           | associated with the RF downconverter.                                                                                    |
                +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            self_calibrate_valid, valid_steps, error_code = self._interpreter.is_self_calibrate_valid(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return self_calibrate_valid, valid_steps, error_code

    @_raise_if_disposed
    def get_s_parameter_external_attenuation_type(self, selector_string):
        r"""Returns the type of S-parameter that is applied to the measurements on the specified port on a Calplane. You can use
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ input to specify the
        name of the Calplane and port to configure for S-parameter.

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies the calibration plane name in which either S-parameter or external attenuation table is
                stored. This input accepts the calibration plane name with the "calplane::" prefix. If you do not specify the
                calibration plane name, the default calibration plane instance is used.

                On a MIMO session if you do not specify the port name, this method will return an error. To get S-parameter external
                attenuation type from a specific MIMO port, use the port specifier with or without the calplane name.

                Example:
                "calplane::plane1/port::myrfsa1/0".

                .. note::
                   For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names. Hence, the valid
                   selector string is "calplane::<calplaneName>/port::<portName>". For a MIMO port, the valid selector string is
                   "calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>". Use :py:meth:`get_available_ports` method to
                   get the valid port names.

                **Example:**

                ""

                "calplane::plane0"

                "calplane::plane0/port::if0"

                "port::if0"

                "calplane::plane0/port::myrfsa1/0"

                "calplane::plane0/port::myrfsa1/0/if0"

        Returns:
            Tuple (s_parameter_type, error_code):

            s_parameter_type (enums.SParameterType):
                This parameter returns the type of S-parameter which is applied to measurements on the specified port of a Calplane.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            s_parameter_type, error_code = self._interpreter.get_s_parameter_external_attenuation_type(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return s_parameter_type, error_code

    @_raise_if_disposed
    def get_external_attenuation_table_actual_value(self, selector_string):
        r"""Returns the external attenuation table actual value that is applied to the measurements for a specified signal and
        calibration plane.

        On a MIMO session, this method returns the external attenuation table actual value for a specified port. You can use
        the **Selector String** parameter to specify the name of the signal, calibration plane, and MIMO port to return the
        external attenuation table actual value.

        **Supported devices**: PXIe-5663/5663E, PXIe-5665, PXIe-5668, PXIe-5644/5645/5646,
        PXIe-5830/5831/5832/5840/5841/5842/5860

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of
                calibration plane name. This input accepts the calibration plane name with the "calplane::" prefix. If you do not
                specify the calibration plane name, the default calibration plane instance is used. On a MIMO session, you must use "port::<deviceName>/<channelNumber>" as part of the selector string to read
                the external attenuation table actual value for the specified port. If you do not specify the signal name, the value is
                returned for the last committed signal instance.

                **Example:**

                ""

                "signal::sig1"

                "calplane::plane0"

                "signal::sig1/calplane::plane0"

                "port::rfsa1/0"

                "signal::sig1/port::rfsa1/0"

                "calplane::plane0/port::rfsa1/0"

                "signal::sig1/calplane::plane0/port::rfsa1/0"

        Returns:
            Tuple (external_attenuation, error_code):

            external_attenuation (float):
                This parameter returns the external attenuation table actual value applied to the measurements for a specified signal
                and calibration plane. This further includes interpolation of the external attenuation table based on the specified
                signal. On a MIMO session, this value corresponds to a specified port. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            external_attenuation, error_code = self._interpreter.get_external_attenuation_table_actual_value(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return external_attenuation, error_code

    @_raise_if_disposed
    def get_available_ports(self, selector_string):
        r"""Fetches the list of ports available for use based on your instrument configuration. On a MIMO session, this method
        fetches all the ports for the initialized MIMO ports.

        Args:
            selector_string (string):
                Specifies a selector string. Pass an empty string.

        Returns:
            Tuple (available_ports, error_code):

            available_ports (string):
                This parameter returns a list of available ports.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            available_ports, error_code = self._interpreter.get_available_ports(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return available_ports, error_code

    @_raise_if_disposed
    def get_self_calibrate_last_temperature(self, selector_string, self_calibrate_step):
        r"""Returns the temperature at the last successful self-calibration. On a MIMO session, use the **Selector String**
        parameter to get the last successful self-calibration temperature for a specific MIMO port.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831 (IF only)/5832 (IF
        only)/5840/5841/5842/5860

        .. note::
           For PXIe-5644/5645/5646 devices, you must select **Image Suppression** for the **Self Calibrate Step** parameter.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of a MIMO port on a MIMO
                session.

                **Example:**

                ""

                "port::myrfsa1/0"

                You can use the :py:meth:`build_port_string` method to build the selector string.

            self_calibrate_step (enums.SelfCalibrateSteps, int):
                This parameter specifies the self-calibration step to query for the last successful self-calibration temperature data.
                The default value is **Preselector Alignment**.

                +-----------------------------+----------------------------------------------------------+
                | Name (Value)                | Description                                              |
                +=============================+==========================================================+
                | Preselector Alignment (1)   | Selects the Preselector Alignment self-calibration step. |
                +-----------------------------+----------------------------------------------------------+
                | Gain Reference (2)          | Selects the Gain Reference self-calibration step.        |
                +-----------------------------+----------------------------------------------------------+
                | IF Flatness (4)             | Selects the IF Flatness self-calibration step.           |
                +-----------------------------+----------------------------------------------------------+
                | Digitizer Self Cal (8)      | Selects the Digitizer Self Cal self-calibration step.    |
                +-----------------------------+----------------------------------------------------------+
                | LO Self Cal (10)            | Selects the LO Self Cal self-calibration step.           |
                +-----------------------------+----------------------------------------------------------+
                | Amplitude Accuracy (20)     | Selects the Amplitude Accuracy self-calibration step.    |
                +-----------------------------+----------------------------------------------------------+
                | Residual LO Power (40)      | Selects the Residual LO Power self-calibration step.     |
                +-----------------------------+----------------------------------------------------------+
                | Image Suppression (80)      | Selects the Image Suppression self-calibration step.     |
                +-----------------------------+----------------------------------------------------------+
                | Synthesizer Alignment (100) | Selects the Synthesizer Alignment self-calibration step. |
                +-----------------------------+----------------------------------------------------------+
                | DC Offset (200)             | Selects the DC Offset self-calibration step.             |
                +-----------------------------+----------------------------------------------------------+

        Returns:
            Tuple (temperature, error_code):

            temperature (float):
                This parameter returns the temperature at the last self-calibration. This value is expressed in degree Celsius.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            self_calibrate_step = (
                self_calibrate_step.value
                if type(self_calibrate_step) is enums.SelfCalibrateSteps
                else self_calibrate_step
            )
            temperature, error_code = self._interpreter.get_self_calibrate_last_temperature(  # type: ignore
                selector_string, self_calibrate_step
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return temperature, error_code

    @_raise_if_disposed
    def get_available_paths(self, selector_string):
        r"""Fetches the list of paths available for use based on your instrument configuration. On a MIMO session, this method
        fetches all the paths for the initialized MIMO paths.

        Args:
            selector_string (string):
                Specifies a selector string. Pass an empty string.

        Returns:
            Tuple (available_paths, error_code):

            available_paths (string):
                This parameter returns a list of available paths.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            available_paths, error_code = self._interpreter.get_available_paths(  # type: ignore
                selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return available_paths, error_code

    @staticmethod
    def build_lo_string(selector_string, lo_index):
        r"""Creates the LO string to use as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ for LO related attributes.

        Args:
            lo_index (int):
                This parameter specifies the LO index for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_lo_string(selector_string, lo_index)  # type: ignore

    @staticmethod
    def build_instrument_string(selector_string, instrument_number):
        r"""Creates the instrument string to use as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ for reading the recommended settings.

        Args:
            instrument_number (int):
        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_instrument_string(selector_string, instrument_number)  # type: ignore

    @staticmethod
    def build_module_string(selector_string, module_name):
        r"""Configures the module string to use as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ for reading temperature of specific
        modules of the device.

        Args:
            module_name (string):
                This parameter specifies the module for which you want the temperature to be read.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        _helper.validate_not_none(module_name, "module_name")
        return _helper.build_module_string(selector_string, module_name)  # type: ignore

    @staticmethod
    def build_calibration_plane_string(calibration_plane_name):
        r"""Creates the selector string to use with External Attenuation Table methods.

        Args:
            calibration_plane_name (string):
                Specifies the calibration plane name for building the selector string.
                This input accepts the calibration plane name with or without the "calplane::" prefix.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        _helper.validate_not_none(calibration_plane_name, "calibration_plane_name")
        return _helper.build_calibration_plane_string(calibration_plane_name)  # type: ignore

    @staticmethod
    def build_port_string(selector_string, port_name, device_name, channel_number):
        r"""Creates the port string to use as the selector string with External Attenuation Table methods.

        On a MIMO session, this method can be used to build port string to use as a selector string for configuring or reading
        port-specific methods and external attenuation table methods.

        Args:
            selector_string (string):
                Specifies the calibration plane string when used for building port string for the external attenuation table methods.
                If you do not specify the calibration plane string, the default calibration plane instance is used.

                Example:

                ""

                "calplane::plane0"

            port_name (string):
                Specifies the port for building the selector string.

            device_name (string):
                Specifies the name of the initialized device for building the selector string.

            channel_number (int):
                Specifies the channel for building the selector string. Specify 0 as the value for this parameter.

        Returns:
            int:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        _helper.validate_not_none(port_name, "port_name")
        _helper.validate_not_none(device_name, "device_name")
        return _helper.build_port_string(  # type: ignore
            selector_string, port_name, device_name, channel_number
        )

    @_raise_if_disposed
    def configure_s_parameter_external_attenuation_table(
        self, selector_string, table_name, frequency, s_parameters, s_parameter_orientation
    ):
        r"""Stores the S-parameter table in the calibration plane specified by the **Selector String** parameter.
        On a MIMO session, the S-parameter table is stored for each MIMO port in the specified calibration plane.

        **Supported devices**: PXIe-5830/5831/5832/5840/5841/5860

        .. note::  If there is only one table configured in any calibration plane, it is automatically selected as the active table.

        Args:
            selector_string (string):
                Specifies the calibration plane name in which the external attenuation table is stored.
                This input accepts the calibration plane name with the \"calplane::\" prefix.
                If you do not specify the calibration plane name, the default calibration plane instance is used.
                The default value is \"\" (empty string).

                On a MIMO session if you do not specify the port name, this configuration is applied to all MIMO ports in the session
                for the default calibration plane instance. To configure S-parameter external attenuation table for a specific MIMO port,
                use the port specifier with or without the calplane name. Example: \"calplane::plane1/port::myrfsa1/0\".

                .. note::
                    For PXIe-5830/5831/5832 devices, port names should also be specified along with Calplane names.
                    Hence, the valid selector string is \"calplane::<calplaneName>/port::<portName>\".
                    If you specify \"port::all\", all ports are considered configured.
                    For a MIMO port, the valid selector string is
                    \"calplane::<calplaneName>/port::<deviceName>/<channelNumber>/<portName>\".
                    If you specify \"port::all\", all MIMO ports are considered configured.

                **Example:**

                \"\"

                \"calplane::plane0\"

                \"calplane::plane0/port::if0\"

                \"port::if0\"

                \"calplane::plane0/port::all\"

                \"calplane::plane0/port::myrfsa1/0\"

                \"calplane::plane0/port::myrfsa1/0, port::myrfsa2/0\"

                \"calplane::plane0/port::myrfsa1/0/if0\"

            table_name (string):
                Specifies the name to be associated with S-parameter table within a calibration plane.
                Provide a unique name, such as "table1" to configure the table.

            frequency (float):
                Specifies an array of frequencies in the S-parameter table. This value is expressed in Hz.

            s_parameters (complex):
                Specifies the S-parameters for each frequency.
                The first index indicates the corresponding frequency entry, the second index corresponds to the target port for the
                S-parameter, and the third index corresponds to the the source port. For example, to index the s21 parameter for the
                fourth frequency in the table, you would use {3, 1, 0} as the indexes since they are zero-based.

            s_parameter_orientation (enums.SParameterOrientation, int):
                Specifies the orientation of the data in the S-parameter table relative to the port you specify.
                The default value is **Port2 Towards DUT**.

                +-----------------------+------------------------------------------------+
                | Name (Value)          | Description                                    |
                +=======================+================================================+
                | Port1 Towards DUT (0) | Port 1 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+
                | Port2 Towards DUT (1) | Port 2 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(table_name, "table_name")
            s_parameter_orientation = (
                s_parameter_orientation.value
                if type(s_parameter_orientation) is enums.SParameterOrientation
                else s_parameter_orientation
            )
            error_code = self._interpreter.configure_s_parameter_external_attenuation_table(  # type: ignore
                selector_string, table_name, frequency, s_parameters, s_parameter_orientation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_signal_configuration_names(self, selector_string, personality_filter):
        r"""Returns the signal names and corresponding personality type, for the personality type selected in the personalityFilter parameter.

        Args:
            selector_string  (string):
                Specifies the selector string. Pass an empty string.

            personality_filter (enums.Personalities, int):
                Returns an array of personalities where each entry corresponds to the personality of each signal name in the signalNames array.

        Returns:
            Tuple (signal_names, personality, error_code):

            signal_names (string):
                Returns an array of the signal names.

            personality (enums.Personalities):
                Returns an array of personalities where each entry corresponds to the personality of each signal name in the signalNames array.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes an error or warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            personality_filter = (
                personality_filter.value
                if type(personality_filter) is enums.Personalities
                else personality_filter
            )
            signal_names, personality, error_code = (
                self._interpreter.get_signal_configuration_names(  # type: ignore
                    selector_string, personality_filter
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return signal_names, personality, error_code

    @_raise_if_disposed
    def fetch_raw_iq_data(self, selector_string, timeout, records_to_fetch, samples_to_read, data):
        r"""Fetches I/Q data from a single record in an acquisition.

        Args:
            selector_string (string):
                Specifies a selector string. Pass an empty string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the raw IQ data.
                A value of -1 specifies that the function waits until all data is available.
                A value of 0 specifies the function immediately returns available data.
                The default value is 10.

            records_to_fetch (int):
                This parameter specifies the record to retrieve. Record numbers are zero-based. The default value is 0.

            samples_to_read (int):
                This parameter specifies the number of samples to fetch.
                A value of -1 specifies that RFmx fetches all samples.
                The default value is -1.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes an error or warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            x0, dx, error_code = self._interpreter.fetch_raw_iq_data(  # type: ignore
                selector_string, timeout, records_to_fetch, samples_to_read, data
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def get_self_calibrate_last_date_and_time(self, selector_string, self_calibrate_step):
        r"""Returns the date and time of the last successful self-calibration.
        On a MIMO session, use the **Selector String** parameter to get the last successful
        self-calibration date and time for a specific MIMO port.

        **Supported Devices:** PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860

        .. note::
           For PXIe-5644/5645/5646 devices, you must select **Image Suppression** for the **Self Calibrate Step** parameter.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of a MIMO port on a MIMO
                session. The default value is "" (empty string).

                **Example:**

                ""

                "port::myrfsa1/0"

                You can use the `RFmxInstr Build Port String <rfmxinstrvi.chm/RFmxInstr_Build_Port_String.html>`_ method to
                build the selector string.

            self_calibrate_step (enums.SelfCalibrateSteps, int):
                This parameter specifies the self-calibration step to query for the last successful self-calibration date and time
                data. The default value is **Preselector Alignment**.

                +-----------------------------+----------------------------------------------------------+
                | Name (Value)                | Description                                              |
                +=============================+==========================================================+
                | Preselector Alignment (1)   | Selects the Preselector Alignment self-calibration step. |
                +-----------------------------+----------------------------------------------------------+
                | Gain Reference (2)          | Selects the Gain Reference self-calibration step.        |
                +-----------------------------+----------------------------------------------------------+
                | IF Flatness (4)             | Selects the IF Flatness self-calibration step.           |
                +-----------------------------+----------------------------------------------------------+
                | Digitizer Self Cal (8)      | Selects the Digitizer Self Cal self-calibration step.    |
                +-----------------------------+----------------------------------------------------------+
                | LO Self Cal (10)            | Selects the LO Self Cal self-calibration step.           |
                +-----------------------------+----------------------------------------------------------+
                | Amplitude Accuracy (20)     | Selects the Amplitude Accuracy self-calibration step.    |
                +-----------------------------+----------------------------------------------------------+
                | Residual LO Power (40)      | Selects the Residual LO Power self-calibration step.     |
                +-----------------------------+----------------------------------------------------------+
                | Image Suppression (80)      | Selects the Image Suppression self-calibration step.     |
                +-----------------------------+----------------------------------------------------------+
                | Synthesizer Alignment (100) | Selects the Synthesizer Alignment self-calibration step. |
                +-----------------------------+----------------------------------------------------------+
                | DC Offset (200)             | Selects the DC Offset self-calibration step.             |
                +-----------------------------+----------------------------------------------------------+

        Returns:
            Tuple (timestamp, error_code):

            timestamp (hightime.datetime):
                This parameter returns the date and time of the last successful self-calibration.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            self_calibrate_step = (
                self_calibrate_step.value
                if type(self_calibrate_step) is enums.SelfCalibrateSteps
                else self_calibrate_step
            )
            timestamp, error_code = self._interpreter.get_self_calibrate_last_date_and_time(  # type: ignore
                selector_string, self_calibrate_step
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return timestamp, error_code


class Session(_SessionBase):
    """Defines a root class that identifies and controls the instrument session."""

    def __init__(self, resource_name, option_string="", instrument_handle=None):
        r"""Creates an RFmx session to the device you specify through the resource_name, option_string or instrument_handle parameter(s).

        Args:
            resource_name (string):
                Specifies the resource name of the device to initialize.

            option_string (string):
                Sets the initial value of certain properties for the session.
                The following attributes are used in this parameter:
                RFmxSetup,
                Simulate,
                AnalysisOnly.
                To simulate a device using the PXIe-5622 (25 MHz) digitizer, set the Digitizer field to 5622_25MHz_DDC
                and the Simulate field to 1. You can set the Digitizer field to 5622_25MHz_DDC only when using the PXIe-5665.
                To use AnalysisOnly mode, specify the string as "AnalysisOnly=1". While using this mode,
                you are responsible for waveform acquisition and RFmx will perform analysis on the I/Q waveform
                or Spectrum you specify. You must use personality specific Analyze functions to perform the measurements.
                To use external NI Source Measure Units (SMU) as the noise source power supply for
                the Noise Figure (NF) measurement, use "NoiseSourcePowerSupply" as the specifier within the RFmxSetup string.
                For example, "RFmxSetup= NoiseSourcePowerSupply:myDCPower[0]" configures RFmx to use channel 0 on myDCPower
                SMU device for powering the noise source. You should allocate a dedicated SMU channel for RFmx.
                RFmx supports PXIe-4138, PXIe-4139, and PXIe-4139 (40 W) SMUs.
                To set multiple attributes, separate their assignments with a comma.

            instrument_handle (int):
                Specifies the pre-existing instrument handle used to create a new RFmx session.

        Returns:
            session (Session):
                The RFmx session object.
        """
        super(Session, self).__init__(
            resource_name=resource_name,
            option_string=option_string,
            instrument_handle=instrument_handle,
        )  # type: ignore

        # Store the parameter list for later printing in __repr__
        pp = pprint.PrettyPrinter(indent=4)
        param_list = []
        param_list.append("resource_name=" + pp.pformat(resource_name))
        param_list.append("option_string=" + pp.pformat(option_string))
        param_list.append("instrument_handle=" + pp.pformat(instrument_handle))
        self._param_list = ", ".join(param_list)

    def __enter__(self):
        """Enables the use of the session object in a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Enables the use of the session object in a context manager."""
        self.close()  # type: ignore

    @classmethod
    def get_session(cls, resource_name, option_string):
        r"""Gets a session, if it exists for given resource name; else, returns a new one.

        Args:
            resource_name (string):
                Specifies the resource name of the device to initialize.

            option_string (string):
                Sets the initial value of certain properties for the session.
                The following attributes are used in this parameter:
                 RFmxSetup,
                 Simulate,
                 AnalysisOnly.
                To simulate a device using the NI 5622 (25 MHz) digitizer, set the Digitizer field to 5622_25MHz_DDC
                and the Simulate field to 1 You can set the Digitizerfield to 5622_25MHz_DDC only when using the NI 5665.
                To use AnalysisOnly mode, specify the string as "AnalysisOnly=1". In this mode, user is responsible
                for waveform acquisition and RFmx driver will perform analysis on user specified IQ waveform or Spectrum.
                Use personality specific Analyze functions to perform measurements.
                To set multiple attributes, separate their assignments with a comma.

        Returns:
            Tuple (session, is_new_session):

            session (Session):
                The RFmx session object.

            is_new_session (bool):
                True if new session is created; otherwise False.
        """
        session_unique_identifier = cls._get_session_unique_identifier(resource_name, option_string)

        cls._sync_root.acquire()
        if session_unique_identifier in cls._instr_map._data:
            cls._instr_map._data[session_unique_identifier]._increment_reference_count()
            session = cls._instr_map._data[session_unique_identifier]
            is_new_session = False
        else:
            session = cls(resource_name, option_string)
            is_new_session = True
        cls._sync_root.release()

        return session, is_new_session

    @staticmethod
    def _get_session_unique_identifier(resource_name: str, option_string: str) -> Any:
        """Gets a unique session identifier for the given resource name(s)."""
        comma_seperated_resource_name = resource_name
        if isinstance(resource_name, list):
            comma_seperated_resource_name = _helper.create_comma_separated_string(resource_name)

        try:
            session_unique_identifier, _ = LibraryInterpreter.get_session_unique_identifier(  # type: ignore
                comma_seperated_resource_name, option_string
            )
        except AttributeError:
            session_unique_identifier = None

        if not session_unique_identifier:
            if (isinstance(resource_name, list) and len(resource_name) > 1) or len(
                resource_name.split(",")
            ) > 1:
                raise Exception("Feature 'MIMO' is not supported.")
            session_unique_identifier = resource_name

        return session_unique_identifier

    @_raise_if_disposed
    def get_specan_signal_configuration(self, signal_name=""):
        r"""Creates a SpecAn signal configuration for specified signal name.
        Existing SpecAn signal configuration is returned if specified signal name exists.

        Args:
            signal_name (string):
                Specifies the name of the signal. This parameter accepts the signal name with or without the "signal::" prefix.
                  Example:

                  "signal::sig1"

                  "sig1"

        Returns:
            specan (SpecAn):
                Returns an object of type SpecAn.
        """
        import nirfmxspecan

        return nirfmxspecan._SpecAnSignalConfiguration.get_specan_signal_configuration(  # type: ignore
            self, signal_name
        )

    @_raise_if_disposed
    def specan_clear_noise_calibration_database(self, selector_string):
        r"""Clears the noise calibration database used for noise compensation.

        Args:
            selector_string (string):
                Pass an empty string. The signal name that is passed when creating the signal configuration is used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        import nirfmxspecan

        specan_signal = nirfmxspecan._SpecAnSignalConfiguration.get_specan_signal_configuration(  # type: ignore
            self
        )
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, specan_signal
            )
            error_code = specan_signal._interpreter.clear_noise_calibration_database(
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
