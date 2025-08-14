"""enums.py - Contains enum classes."""

from enum import Enum, IntFlag


class RFAttenuationAuto(Enum):
    """RFAttenuationAuto."""

    FALSE = 0
    r"""Specifies that the RFmx driver uses the value configured using
    :py:attr:`~nirfmxinstr.attributes.AttributeID.RF_ATTENUATION_VALUE`  attribute."""

    TRUE = 1
    r"""Specifies that the RFmx driver computes the RF attenuation."""


class MechanicalAttenuationAuto(Enum):
    """MechanicalAttenuationAuto."""

    FALSE = 0
    r"""Specifies that the RFmx driver uses the value configured in the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.MECHANICAL_ATTENUATION_VALUE` attribute."""

    TRUE = 1
    r"""Specifies that the measurement computes the mechanical attenuation."""


class LOLeakageAvoidanceEnabled(Enum):
    """LOLeakageAvoidanceEnabled."""

    FALSE = 0
    r"""RFmx does not modify the Downconverter Frequency Offset attribute."""

    TRUE = 1
    r"""RFmx calculates the required LO offset based on the measurement configuration and appropriately sets the Downconverter
    Frequency Offset attribute."""


class LO2ExportEnabled(Enum):
    """LO2ExportEnabled."""

    DISABLED = 0
    r"""Disables the LO2 OUT terminals."""

    ENABLED = 1
    r"""Enables the LO2 OUT terminals."""


class TuningSpeed(Enum):
    """TuningSpeed."""

    NORMAL = 0
    r"""PXIe-5665/5668: Adjusts the YIG main coil on the LO for an underdamped response.
    
    PXIe-5663/5663E/5644/5645/5646: Specifies that the RF downconverter module uses a narrow loop bandwidth."""

    MEDIUM = 1
    r"""Specifies that the RF downconverter module uses a medium loop bandwidth. This value is not supported on
    PXIe-5663/5663E/5665/5668 devices."""

    FAST = 2
    r"""PXIe-5665/5668: Adjusts the YIG main coil on the LO for an overdamped response. Setting this attribute to **Fast**
    allows the frequency to settle significantly faster for some frequency transitions at the expense of increased phase
    noise.
    
    PXIe-5663/5663E/5644/5645/5646: Specifies that the RF downconverter module uses a wide loop bandwidth."""


class LOInjectionSide(Enum):
    """LOInjectionSide."""

    HIGH_SIDE = 0
    r"""Configures the LO signal that the device generates at a frequency higher than the RF signal. This LO frequency is given
    by the following formula: *f\ :sub:`LO`\ = f\ :sub:`RF`\ + f\ :sub:`IF`\
    *"""

    LOW_SIDE = 1
    r"""Configures the LO signal that the device generates at a frequency lower than the RF signal. This LO frequency is given
    by the following formula: *f\ :sub:`LO`\ = f\ :sub:`RF`\ – f\ :sub:`IF`\
    *"""


class LOPllFractionalMode(Enum):
    """LOPllFractionalMode."""

    DISABLED = 0
    r"""Indicates that the attribute is disabled."""

    ENABLED = 1
    r"""Indicates that the attribute is enabled."""


class StartTriggerType(Enum):
    """StartTriggerType."""

    NONE = 0
    r"""No start trigger is configured."""

    DIGITAL_EDGE = 1
    r"""The start trigger is not asserted until a digital edge is detected. The source of the digital edge is specified by the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.START_TRIGGER_DIGITAL_EDGE_SOURCE` attribute."""

    SOFTWARE = 3
    r"""The start trigger is not asserted until a software trigger occurs. You can assert the software trigger by calling the
    RFmxInstr Send Software Edge Trigger method."""


class StartTriggerDigitalEdge(Enum):
    """StartTriggerDigitalEdge."""

    RISING = 0
    r"""The trigger asserts on the rising edge of the signal."""

    FALLING = 1
    r"""The trigger asserts on the falling edge of the signal."""


class AdvanceTriggerType(Enum):
    """AdvanceTriggerType."""

    NONE = 0
    r"""No advance trigger is configured."""

    DIGITAL_EDGE = 1
    r"""The advance trigger is not asserted until a digital edge is detected. The source of the digital edge is specified with
    the :py:attr:`~nirfmxinstr.attributes.AttributeID.ADVANCE_TRIGGER_DIGITAL_EDGE_SOURCE` attribute."""

    SOFTWARE = 3
    r"""The advance trigger is not asserted until a software trigger occurs. You can assert the software trigger by calling the
    RFmxInstr Send Software Edge Trigger method."""


class PreampEnabled(Enum):
    """PreampEnabled."""

    DISABLED = 0
    r"""Disables the RF preamplifier.
    
    **Supported Devices:** PXIe-5663/5663E/5665/5668"""

    ENABLED = 1
    r"""Enables the RF preamplifier when it is in the signal path and disables it when it is not in the signal path. Only
    devices with an RF preamplifier on the downconverter and an RF preselector support this option. Use the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.RF_PREAMP_PRESENT`  attribute to determine whether the downconverter has
    a preamplifier.
    
    **Supported Devices:** PXIe-5663/5663E/5665/5668"""

    AUTOMATIC = 3
    r"""Automatically enables the RF preamplifier based on the value of the reference level.
    
    **Supported Devices:** PXIe-5644/5645/5646, PXIe-5830/5831/5832/5840/5841/5842/5860"""


class ChannelCoupling(Enum):
    """ChannelCoupling."""

    AC_COUPLED = 0
    r"""Specifies that the RF input channel is AC-coupled. For low frequencies (<10 MHz), accuracy decreases because RFmxInstr
    does not calibrate the configuration."""

    DC_COUPLED = 1
    r"""Specifies that the RF input channel is DC-coupled. The RFmx driver enforces a minimum RF attenuation for device
    protection."""


class DownconverterPreselectorEnabled(Enum):
    """DownconverterPreselectorEnabled."""

    DISABLED = 0
    r"""Disables the preselector."""

    ENABLED = 1
    r"""The preselector is automatically enabled when it is in the signal path and is automatically disabled when it is not in
    the signal path. Use the :py:attr:`~nirfmxinstr.attributes.AttributeID.PRESELECTOR_PRESENT` attribute to determine if
    the downconverter has a preselector."""


class OspDelayEnabled(Enum):
    """OspDelayEnabled."""

    DISABLED = 0
    r"""Disables the attribute."""

    ENABLED = 1
    r"""Enables the attribute."""


class CleanerSpectrum(Enum):
    """CleanerSpectrum."""

    DISABLED = 0
    r"""Disable this attribute to get faster measurement speed."""

    ENABLED = 1
    r"""Enable this attribute to get the lowest noise floor and avoid digitizer spurs."""


class DigitizerDitherEnabled(Enum):
    """DigitizerDitherEnabled."""

    DISABLED = 0
    r"""Disables the attribute."""

    ENABLED = 1
    r"""Enables the attribute."""


class FrequencySettlingUnits(Enum):
    """FrequencySettlingUnits."""

    PPM = 0
    r"""Specifies the frequency settling in parts per million (ppm)."""

    SECONDS_AFTER_LOCK = 1
    r"""Specifies the frequency settling in time after lock (seconds)."""

    SECONDS_AFTER_IO = 2
    r"""Specifies the frequency settling in time after I/O (seconds)."""


class OverflowErrorReporting(Enum):
    """OverflowErrorReporting."""

    WARNING = 0
    r"""RFmx returns a warning when an ADC or an onboard signal processing (OSP) overflow occurs."""

    DISABLED = 1
    r"""RFmx does not return an error or a warning when an ADC or OSP overflow occurs."""


class OptimizePathForSignalBandwidth(Enum):
    """OptimizePathForSignalBandwidth."""

    DISABLED = 0
    r"""Disables the optimized path for signal bandwidth."""

    ENABLED = 1
    r"""Enables the optimized path for signal bandwidth."""

    AUTOMATIC = 2
    r"""Automatically enables the optimized path based on other configurations."""


class InputIsolationEnabled(Enum):
    """InputIsolationEnabled."""

    DISABLED = 0
    r"""Indicates that the attribute is disabled."""

    ENABLED = 1
    r"""Indicates that the attribute is enabled."""


class SelfCalibrationValidityCheck(Enum):
    """SelfCalibrationValidityCheck."""

    OFF = 0
    r"""Indicates that RFmx does not check whether device self-calibration data is valid."""

    ENABLED = 1
    r"""Indicates that RFmx checks whether device self-calibration data is valid and reports a warning from the RFmx Commit and
    RFmx Initiate methods when the data is invalid."""


class LOSharingMode(Enum):
    """LOSharingMode."""

    DISABLED = 0
    r"""LO Sharing is disabled."""

    EXTERNAL_STAR = 3
    r"""The LO connection configuration is configured as External Star."""

    EXTERNAL_DAISY_CHAIN = 4
    r"""The LO connection configuration is configured as External Daisy Chain."""

    SPLITTER_AND_DAISY_CHAIN = 5
    r"""The LO connection configuration is configured as Splitter and Daisy Chain.
    
    With this option, the only allowed value for the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.NUMBER_OF_LO_SHARING_GROUPS` attribute is 1."""


class LoadOptions(Enum):
    """LoadOptions."""

    SKIP_NONE = 0
    r"""RFmx loads all the configurations to the session."""

    SKIP_RFINSTR = 1
    r"""RFmx skips loading the RFmxInstr configurations to the session."""


class RecommendedAcquisitionType(Enum):
    """RecommendedAcquisitionType."""

    IQ = 0
    r"""Indicates that the recommended acquisition type is I/Q. Use the Analyze (IQ) method to perform the measurement."""

    SPECTRAL = 1
    r"""Indicates that the recommended acquisition type is Spectral. Use Analyze (Spectrum) method to perform the measurement."""

    IQ_OR_SPECTRAL = 2
    r"""Indicates that the recommended acquisition type is I/Q or Spectral. Use either Analyze (IQ) or Analyze (Spectrum)
    method to perform the measurement."""


class RecommendedSpectralFftWindow(Enum):
    """RecommendedSpectralFftWindow."""

    NONE = 0
    r"""Indicates that the measurement does not use FFT windowing to reduce spectral leakage."""

    FLAT_TOP = 1
    r"""Indicates a Flat Top FFT window type."""

    HANNING = 2
    r"""Indicates a Hanning FFT window type."""

    HAMMING = 3
    r"""Indicates a Hamming FFT window type."""

    GAUSSIAN = 4
    r"""Indicates a Gaussian FFT window type."""

    BLACKMAN = 5
    r"""Indicates a Blackman FFT window type."""

    BLACKMAN_HARRIS = 6
    r"""Indicates a Blackman-Harris FFT window type."""

    KAISER_BESSEL = 7
    r"""Indicates a Kaiser-Bessel FFT window type."""


class ExportSignalSource(Enum):
    """ExportSignalSource."""

    START_TRIGGER = 0
    r"""Start trigger is sourced."""

    REFERENCE_TRIGGER = 1
    r"""Reference trigger event is sourced."""

    ADVANCE_TRIGGER = 2
    r"""Advance trigger event is sourced."""

    READY_FOR_START_EVENT = 3
    r"""Ready For Start Event is sourced."""

    READY_FOR_REFERENCE_EVENT = 4
    r"""Ready For Reference Event is sourced."""

    READY_FOR_ADVANCE_EVENT = 5
    r"""Ready For Advance Event is sourced."""

    END_OF_RECORD_EVENT = 6
    r"""End Of Record Event is sourced."""

    DONE_EVENT = 7
    r"""Done Event is sourced."""

    REFERENCE_CLOCK = 8
    r"""Reference Clock is sourced."""


class SelfCalibrateSteps(IntFlag):
    """SelfCalibrateSteps."""

    NONE = 0
    r"""A value of None specifies that all calibration steps are performed."""

    PRESELECTOR_ALIGNMENT = 1 << 0
    r"""Selects/Omits the Preselector Alignment self-calibration step."""

    GAIN_REFERENCE = 1 << 1
    r"""Selects/Omits the Gain Reference self-calibration step."""

    IF_FLATNESS = 1 << 2
    r"""Selects/Omits the IF Flatness self-calibration step."""

    DIGITIZER_SELF_CAL = 1 << 3
    r"""Selects/Omits the Digitizer Self Cal self-calibration step."""

    LO_SELF_CAL = 1 << 4
    r"""Selects/Omits the LO Self Cal self-calibration step."""

    AMPLITUDE_ACCURACY = 1 << 5
    r"""Selects/Omits the Amplitude Accuracy self-calibration step."""

    RESIDUAL_LO_POWER = 1 << 6
    r"""Selects/Omits the Residual LO Power self-calibration step."""

    IMAGE_SUPPRESSION = 1 << 7
    r"""Selects/Omits the Image Suppression self-calibration step."""

    SYNTHESIZER_ALIGNMENT = 1 << 8
    r"""Selects/Omits the Synthesizer Alignment self-calibration step."""

    DC_OFFSET = 1 << 9
    r"""Selects/Omits the DC Offset self-calibration step."""


class Personalities(IntFlag):
    """Personalities."""

    NONE = 0
    r"""Specifies that a signal does not exist."""

    SPECAN = 1 << 0
    r"""Specifies the SpecAn personality."""

    DEMOD = 1 << 1
    r"""Specifies the Demod personality."""

    LTE = 1 << 2
    r"""Specifies the LTE personality."""

    GSM = 1 << 3
    r"""Specifies the GSM personality."""

    WCDMA = 1 << 4
    r"""Specifies the WCDMA personality."""

    CDMA2K = 1 << 5
    r"""Specifies the CDMA2k personality."""

    TDSCDMA = 1 << 6
    r"""Specifies the TD-SCDMA personality."""

    EVDO = 1 << 7
    r"""Specifies the EV-DO personality."""

    NR = 1 << 8
    r"""Specifies the NR personality."""

    WLAN = 1 << 9
    r"""Specifies the WLAN personality."""

    BT = 1 << 10
    r"""Specifies the BT personality."""

    PULSE = 1 << 11
    r"""Specifies the Pulse personality."""

    VNA = 1 << 12
    r"""Specifies the VNA personality."""

    UWB = 1 << 13
    r"""Specifies the UWB personality."""

    ALL = 0x7FFFFFFF
    r"""Specifies all the personalities."""


class SParameterOrientation(Enum):
    """SParameterOrientation."""

    PORT1_TOWARDS_DUT = 0
    r"""Port 1 of the S2P is oriented towards the DUT."""

    PORT2_TOWARDS_DUT = 1
    r"""Port 2 of the S2P is oriented towards the DUT."""


class LinearInterpolationFormat(Enum):
    """LinearInterpolationFormat."""

    REAL_AND_IMAGINARY = 0
    r"""Results in a linear interpolation of the real portion of the complex number
    and a separate linear interpolation of the complex portion."""

    MAGNITUDE_AND_PHASE = 1
    r"""Results in a linear interpolation."""

    MAGNITUDE_DB_AND_PHASE = 2
    r"""Results in a linear interpolation."""


class SParameterType(Enum):
    """SParameterType."""

    SCALAR = 1
    r"""De-embeds the measurement using the gain term."""

    VECTOR = 2
    r"""De-embeds the measurement using the gain term and the reflection term."""
