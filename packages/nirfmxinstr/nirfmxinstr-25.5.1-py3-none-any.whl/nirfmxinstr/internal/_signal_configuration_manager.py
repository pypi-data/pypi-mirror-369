"""This class contains implementation of signal manager."""

from typing import Any


class SignalConfigurationManager:
    """This class contains implementation of signal manager."""

    _default_signal_name = ""

    def __init__(self):
        self._signals = []

    def add_signal_configuration(self, signal_configuration: Any) -> None:
        self._signals.append(signal_configuration)

    def remove_signal_configuration(self, signal_configuration: Any) -> None:
        self._signals.remove(signal_configuration)

    def find_signal_configuration(self, signal_type: Any, signal_name: str) -> Any:
        return next(
            (
                s
                for s in self._signals
                if s.signal_configuration_name.lower() == signal_name.lower()
                and str(s.signal_configuration_type) == str(signal_type)
            ),
            None,
        )

    def clear_named_signal_configurations(self) -> None:
        self._signals = [
            s for s in self._signals if s.signal_name.lower() == self._default_signal_name.lower()
        ]

    @property
    def number_of_signal_configurations(self):
        return len(self._signals)
