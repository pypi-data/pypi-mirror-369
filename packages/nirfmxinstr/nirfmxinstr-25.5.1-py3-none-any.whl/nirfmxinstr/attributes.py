"""attributes.py - Contains the ID of all attributes belongs to the module."""

from enum import Enum


class AttributeID(Enum):
    """This enum class contains the ID of all attributes belongs to the module."""

    FREQUENCY_REFERENCE_SOURCE = 2
    r"""Specifies the frequency reference source.
    
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
    """

    FREQUENCY_REFERENCE_FREQUENCY = 3
    r"""Specifies the Reference Clock rate, when the :py:attr:`~nirfmxinstr.attributes.AttributeID.FREQUENCY_REFERENCE_SOURCE`
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
    """

    FREQUENCY_REFERENCE_EXPORTED_TERMINAL = 34
    r"""Specifies a comma-separated list of the terminals at which to export the frequency reference.
    
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
    """

    RF_ATTENUATION_AUTO = 4
    r"""Specifies whether the RFmx driver computes the RF attenuation.
    
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
    """

    RF_ATTENUATION_VALUE = 5
    r"""Specifies the nominal attenuation setting for all attenuators before the first mixer in the RF signal chain. This value
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
    """

    MECHANICAL_ATTENUATION_AUTO = 6
    r"""Specifies whether the RFmx driver chooses an attenuation setting based on the hardware settings.
    
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
    """

    MECHANICAL_ATTENUATION_VALUE = 7
    r"""Specifies the level of mechanical attenuation for the RF path. This value is expressed in dB.
    
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
    """

    LO_LEAKAGE_AVOIDANCE_ENABLED = 55
    r"""Specifies whether to reduce the effects of the instrument leakage by placing the LO outside the band of acquisition.
    
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
    """

    LO_SOURCE = 59
    r"""Specifies the local oscillator (LO) signal source used to downconvert the RF input signal.
    
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
    """

    LO_FREQUENCY = 60
    r"""Specifies the LO signal frequency for the configured center frequency. This value is expressed in Hz.
    
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
    """

    LO_EXPORT_ENABLED = 33
    r"""Specifies whether to enable the LO OUT terminals on the installed devices.
    
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
    """

    LO2_EXPORT_ENABLED = 58
    r"""Specifies whether to enable the LO2 OUT terminals in the installed devices.
    
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
    """

    LO_IN_POWER = 78
    r"""Specifies the power level expected at the LO IN terminal when the
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
    """

    LO_OUT_POWER = 79
    r"""Specifies the power level of the signal at the LO OUT terminal when the
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
    """

    TUNING_SPEED = 8
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
    """

    DOWNCONVERTER_FREQUENCY_OFFSET = 53
    r"""Specifies an offset from the center frequency value for the downconverter. Use this attribute to offset the measurement
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
    """

    DOWNCONVERTER_CENTER_FREQUENCY = 13
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
    """

    LO_INJECTION_SIDE = 18
    r"""Specifies the LO injection side.
    
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
    """

    LO_FREQUENCY_STEP_SIZE = 95
    r"""Specifies the step size for tuning the LO phase-locked loop (PLL).
    
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
    """

    LO_VCO_FREQUENCY_STEP_SIZE = 80
    r"""Specifies the step size for tuning the internal voltage-controlled oscillator (VCO) used to generate the LO signal. The
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
    """

    LO_PLL_FRACTIONAL_MODE = 90
    r"""Specifies whether to use fractional mode for the LO phase-locked loop (PLL).
    
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
    """

    TRIGGER_EXPORT_OUTPUT_TERMINAL = 35
    r"""Specifies the destination terminal for the exported Reference Trigger. You can also choose not to export any signal.
    
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
    """

    TRIGGER_TERMINAL_NAME = 36
    r"""Returns the fully qualified signal name as a string.
    
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
    """

    START_TRIGGER_TYPE = 98
    r"""Specifies whether the start trigger is a digital edge or a software trigger.
    
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
    """

    START_TRIGGER_DIGITAL_EDGE_SOURCE = 99
    r"""Specifies the source terminal for the start trigger. This attribute is used only when you set the
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
    """

    START_TRIGGER_DIGITAL_EDGE = 100
    r"""Specifies the active edge for the start trigger. This attribute is used only when you set the
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
    """

    START_TRIGGER_EXPORT_OUTPUT_TERMINAL = 101
    r"""Specifies the destination terminal for the exported start trigger.
    
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
    """

    START_TRIGGER_TERMINAL_NAME = 102
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/StartTrigger*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/StartTrigger*, where *BasebandModule* is the name of your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/StartTrigger,*, where *ModuleName *is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).
    
    - **All other devices**: */DigitizerName/StartTrigger*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    ADVANCE_TRIGGER_TYPE = 103
    r"""Specifies whether the advance trigger is a digital edge or a software trigger.
    
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
    """

    ADVANCE_TRIGGER_DIGITAL_EDGE_SOURCE = 104
    r"""Specifies the source terminal for the advance trigger.
    
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
    """

    ADVANCE_TRIGGER_EXPORT_OUTPUT_TERMINAL = 105
    r"""Specifies the destination terminal for the exported advance trigger.
    
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
    """

    ADVANCE_TRIGGER_TERMINAL_NAME = 106
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/AdvanceTrigger*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/AdvanceTrigger*, where *BasebandModule* is the name of your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/AdvanceTrigger,*, where *ModuleName *is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).
    
    - **All other devices**: */DigitizerName/AdvanceTrigger*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    READY_FOR_START_EVENT_OUTPUT_TERMINAL = 107
    r"""Specifies the destination terminal for the Ready for Start event.
    
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
    """

    READY_FOR_START_EVENT_TERMINAL_NAME = 108
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/ReadyForStartEvent*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/ReadyForStartEvent*, where *BasebandModule*is the name of the baseband module for your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/ReadyForStartEvent*, where *ModuleName * is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).
    
    - **All other devices**: */DigitizerName/ReadyForStartEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    READY_FOR_ADVANCE_EVENT_OUTPUT_TERMINAL = 109
    r"""Specifies the destination terminal for the Ready for Advance event.
    
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
    """

    READY_FOR_ADVANCE_EVENT_TERMINAL_NAME = 110
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/ReadyForAdvanceEvent*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/ReadyForAdvanceEvent*, where *BasebandModule* is the name of your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/ReadyForAdvanceEvent*, where *ModuleName * is the name of your device in MAX and ChannelNumber is the channel number (0 or 1)
    
    - **All other devices**: */DigitizerName/ReadyForAdvanceEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    READY_FOR_REFERENCE_EVENT_OUTPUT_TERMINAL = 111
    r"""Specifies the destination terminal for the Ready for Reference event.
    
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
    """

    READY_FOR_REFERENCE_EVENT_TERMINAL_NAME = 112
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/ReadyForReferenceEvent*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/ReadyForReferenceEvent*, where *BasebandModule* is the name of your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/ReadyForReferenceEvent*, where *BasebandModule*is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).
    
    - **All other devices**: */DigitizerName/ReadyForReferenceEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    END_OF_RECORD_EVENT_OUTPUT_TERMINAL = 113
    r"""Specifies the destination terminal for the End of Record event.
    
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
    """

    END_OF_RECORD_EVENT_TERMINAL_NAME = 114
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/EndOfRecordEvent*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/EndOfRecordEvent*, where *BasebandModule* is the name of your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/EndOfRecordEvent*, where *ModuleName * is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).
    
    - **All other devices**: */DigitizerName/EndOfRecordEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    DONE_EVENT_OUTPUT_TERMINAL = 115
    r"""Specifies the destination terminal for the Done event.
    
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
    """

    DONE_EVENT_TERMINAL_NAME = 116
    r"""Returns the fully qualified signal name as a string.
    
    The standard format is as follows:
    
    - **PXIe-5820/5840/5841/5842**: */ModuleName/ai/0/DoneEvent*, where *ModuleName* is the name of your device in MAX.
    
    - **PXIe-5830/5831/5832**: */BasebandModule/ai/0/DoneEvent*, where *BasebandModule* is the name of your device in MAX.
    
    - **PXIe-5860**: */ModuleName/ai/ChannelNumber/DoneEvent*, where *ModuleName* is the name of your device in MAX and ChannelNumber is the channel number (0 or 1).
    
    - **All other devices**: */DigitizerName/DoneEvent*, where *DigitizerName* is the name of your associated digitizer module in MAX.
    
    .. note::
       This attribute is not supported on a MIMO session.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    DEVICE_TEMPERATURE = 24
    r"""Returns the current temperature of the module. This value is expressed in degrees Celsius.
    
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
    """

    DIGITIZER_TEMPERATURE = 25
    r"""Returns the current temperature of the digitizer module. This value is expressed in degrees Celsius.
    
    On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
    :py:meth:`build_port_string` method to build the selector string.
    
    .. note::
       This attribute is not supported if you are using an external digitizer.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5840/5841/5842/5860
    """

    LO_TEMPERATURE = 26
    r"""Returns the current temperature of the LO module associated with the device. This value is expressed in degrees
    Celsius.
    
    On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
    :py:meth:`build_port_string` method to build the selector string.
    
    .. note::
       This attribute is not supported if you are using an external LO.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5840/5841/5842
    """

    SERIAL_NUMBER = 30
    r"""Returns the serial number of the RF downconverter module.
    
    .. note::
       For PXIe-5644/5645/5646 and PXIe-5820/5840/5841/5842/5860, this attribute returns the serial number of the VST module.
       For PXIe-5830/5831/5832, this attribute returns the serial number of PXIe-3621/3622/3623.
    
    On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
    :py:meth:`build_port_string` method to build the selector string.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
    PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    INSTRUMENT_MODEL = 28
    r"""Returns a string that contains the model number or name of the RF device that you are currently using.
    
    On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
    :py:meth:`build_port_string` method to build the selector string.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
    PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    MODULE_REVISION = 29
    r"""Returns the revision of the RF downconverter module.
    
    On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
    :py:meth:`build_port_string` method to build the selector string.
    
    .. note::
       For PXIe-5644/5645/5646 and PXIe-5820/5830/5831/5832/5840/5841/5842/5860, this attribute returns the revision of the
       VST module.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668,
    PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    INSTRUMENT_FIRMWARE_REVISION = 27
    r"""Returns a string containing the firmware revision information of the RF downconverter for the composite device you are
    currently using.
    
    On a MIMO session, use "port::<deviceName>/<channelNumber>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this attribute. You can use the
    :py:meth:`build_port_string` method to build the selector string.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    PRESELECTOR_PRESENT = 31
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
    """

    RF_PREAMP_PRESENT = 32
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
    """

    PREAMP_ENABLED = 14
    r"""Specifies whether the RF preamplifier is enabled in the system.
    
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
    """

    CHANNEL_COUPLING = 11
    r"""Specifies whether the RF IN connector is AC- or DC-coupled on the downconverter.
    
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
    """

    DOWNCONVERTER_PRESELECTOR_ENABLED = 12
    r"""Specifies whether the tunable preselector is enabled on the downconverter.
    
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
    """

    MIXER_LEVEL = 16
    r"""Specifies the mixer level. This value is expressed in dBm.
    
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
    """

    MIXER_LEVEL_OFFSET = 15
    r"""Specifies the number of dB by which to adjust the device mixer level.
    
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
    """

    RF_ATTENUATION_STEP_SIZE = 54
    r"""Specifies the step size for the RF attenuation level. This value is expressed in dB. The actual RF attenuation is
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
    """

    OSP_DELAY_ENABLED = 23
    r"""Specifies whether to enable the digitizer OSP block to delay Reference Triggers, along with the data samples, moving
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
    """

    PHASE_OFFSET = 19
    r"""Specifies the offset to apply to the initial I and Q phases.
    
    You do not need to use a selector string if you want to configure this attribute for all signal instances.
    Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax.
    
    The default value is 0.
    
    Valid values are -180 degrees to 180 degrees, inclusive.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668, PXIe-5820/5830/5831/5832/5840/5841/5842
    """

    FFT_WIDTH = 22
    r"""Specifies the FFT width of the device. The FFT width is the effective bandwidth of the signal path during each signal
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
    """

    CLEANER_SPECTRUM = 37
    r"""Specifies how to obtain the lowest noise floor or faster measurement speed.
    
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
    """

    IF_OUTPUT_POWER_LEVEL_OFFSET = 17
    r"""Specifies the power offset by which to adjust the default IF output power level. This value is expressed in dB.
    
    This attribute does not depend on absolute IF output power levels; therefore, you can use this attribute to
    adjust the IF output power level on all RFmx-supported devices without knowing the exact default value. Use this
    attribute to increase or decrease the nominal output level to achieve better measurement results.
    
    You do not need to use a selector string if you want to configure this attribute for all signal instances.
    Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax.
    
    The default value is 0.
    
    **Supported devices**: PXIe-5663/5663E/5665, PXIe-5668
    """

    DIGITIZER_DITHER_ENABLED = 21
    r"""Specifies whether dithering is enabled on the digitizer.
    
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
    """

    IF_FILTER_BANDWIDTH = 48
    r"""Specifies the IF filter path bandwidth for your device configuration.
    
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
    """

    FREQUENCY_SETTLING_UNITS = 9
    r"""Specifies the delay duration units and interpretation for LO settling.
    
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
    """

    FREQUENCY_SETTLING = 10
    r"""Specifies the value used for LO frequency settling.
    
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
    """

    RF_HIGHPASS_FILTER_FREQUENCY = 49
    r"""Specifies the maximum corner frequency of the high pass filter in the RF signal path. The device uses the highest
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
    """

    SUBSPAN_OVERLAP = 50
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
    """

    DOWNCONVERTER_GAIN = 52
    r"""Returns the net signal gain for the device at the current RFmx settings and temperature. RFmx scales the acquired I/Q
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
    """

    AMPLITUDE_SETTLING = 56
    r"""Specifies the amplitude settling accuracy value. This value is expressed in decibels. RFmx waits until the RF power
    attains the specified accuracy level after calling the RFmx Initiate method.
    
    Any specified amplitude settling value that is above the acceptable minimum value is coerced down to the
    closest valid value.
    
    You do not need to use a selector string if you want to configure this attribute for all signal instances.
    Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax.
    
    **Supported Devices:** PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5842/5860
    """

    OVERFLOW_ERROR_REPORTING = 77
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
    """

    COMMON_MODE_LEVEL = 70
    r"""Specifies the common-mode level presented at each differential input terminal. The common-mode level shifts both
    positive and negative terminals in the same direction. This must match the common-mode level of the device under test
    (DUT). This value is expressed in Volts.
    
    You do not need to use a selector string if you want to configure this attribute for all signal instances.
    Specify the signal name in the selector string if you want to configure or read that signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax.
    
    The default value is 0.
    
    **Supported devices**: PXIe-5820
    """

    SMU_RESOURCE_NAME = 71
    r"""Specifies the resource name assigned by Measurement and Automation Explorer (MAX) for NI Source Measure Units (SMU)
    which is used  as the noise source power supply for Noise Figure (NF) measurement, for example, PXI1Slot3, where
    PXI1Slot3 is an instrument resource name. SMU Resource Name can also be a logical IVI name.
    
    **Supported devices:** PXIe-4138, PXIe-4139, PXIe-4139 (40 W), and PXIe-4143 SMUs.
    """

    SMU_CHANNEL = 72
    r"""Specifies the output channel to be used for noise figure (NF) measurement in RFmx.
    
    The default value is 0.
    """

    OPTIMIZE_PATH_FOR_SIGNAL_BANDWIDTH = 91
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
    """

    INPUT_ISOLATION_ENABLED = 92
    r"""Specifies whether input isolation is enabled.
    
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
    """

    THERMAL_CORRECTION_HEADROOM_RANGE = 94
    r"""Specifies the expected thermal operating range of the instrument from the self-calibration temperature returned from
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
    """

    TEMPERATURE_READ_INTERVAL = 119
    r"""Specifies the minimum time difference between temperature sensor readings. This value is expressed in seconds.
    
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
    """

    THERMAL_CORRECTION_TEMPERATURE_RESOLUTION = 120
    r"""Specifies the temperature change required before RFmx recalculates the thermal correction settings when entering the
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
    """

    NUMBER_OF_RAW_IQ_RECORDS = 128
    r"""Returns the number of raw IQ records to acquire to complete measurement averaging.
    
    .. note::
       This attribute returns a value of 0 when RFmx cannot provide I/Q data for the specified measurement configuration.
    """

    DIGITAL_GAIN = 84
    r"""Specifies the scaling factor applied to the time-domain voltage data in the digitizer. This value is expressed in dB.
    RFmx does not compensate for the specified digital gain.
    
    You can use this attribute to account for external gain changes without changing the analog signal path.
    
    .. note::
       The PXIe-5644/5645/5646 applies this gain when the data is scaled. The raw data does not include this scaling on these
       devices.
    
    **Default Value**
    : 0 dB
    
    **Supported Devices**
    : PXIe-5644/5645/5646, PXIe-5820/5830/5831/5832/5840/5841/5860
    """

    SELF_CALIBRATION_VALIDITY_CHECK = 117
    r"""Specifies whether the RFmx driver validates the self-calibration data.
    
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
    """

    SELF_CALIBRATION_VALIDITY_CHECK_TIME_INTERVAL = 118
    r"""Specifies the minimum time between two self calibration validity checks. This value is expressed in seconds.
    
    When you call RFmx Commit or Initiate methods by enabling the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.SELF_CALIBRATION_VALIDITY_CHECK` attribute, the RFmx driver checks if the
    amount of time specified by the Self Calibration Validity Check Time Interval attribute has elapsed before validating
    the calibration data.
    
    The default value is 30 seconds.
    
    **Supported devices**: PXIe-5663/5663E/5665/5668, PXIe-5644/5645/5646,
    PXIe-5820/5830/5831/5832/5833/5840/5841/5842/5860
    """

    LO_SHARING_MODE = 68
    r"""Specifies the RFmx session with the respective LO sharing mode.
    
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
    """

    NUMBER_OF_LO_SHARING_GROUPS = 97
    r"""Specifies the RFmx session with the number of LO sharing groups.
    
    The default value is 1.
    
    The valid values are 1 and 2.
    """

    LO_SPLITTER_LOSS_FREQUENCY = 184
    r"""Specifies the frequencies corresponding to the insertion loss inherent to the RF Splitter, as specified by the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS_FREQUENCY` attribute. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    LO_SPLITTER_LOSS = 185
    r"""Specifies an array of the insertion losses inherent to the RF Splitter. This value is expressed in dB.
    
    You must specify the frequencies at which the losses were measured using the
    :py:attr:`~nirfmxinstr.attributes.AttributeID.LO_SPLITTER_LOSS` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    LOAD_OPTIONS = 163
    r"""Specifies the configurations to skip while loading from a file using the :py:meth:`load_configurations` method .
    
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
    """

    RECOMMENDED_ACQUISITION_TYPE = 39
    r"""Returns the recommended acquisition type for the last committed measurement configuration.
    
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
    """

    RECOMMENDED_CENTER_FREQUENCY = 57
    r"""Returns the recommended center frequency of the RF signal. This value is expressed in Hz.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_NUMBER_OF_RECORDS = 40
    r"""Returns the recommended number of records to acquire to complete measurement averaging.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_TRIGGER_MINIMUM_QUIET_TIME = 41
    r"""Returns the recommended minimum quiet time during which the signal level must be below the trigger value for triggering
    to occur. This value is expressed in seconds.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_IQ_ACQUISITION_TIME = 42
    r"""Returns the recommended acquisition time for I/Q acquisition. This value is expressed in seconds.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_IQ_MINIMUM_SAMPLE_RATE = 43
    r"""Returns the recommended minimum sample rate for I/Q acquisition. This value is expressed in Hz.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_IQ_PRE_TRIGGER_TIME = 44
    r"""Returns the recommended pretrigger time for I/Q acquisition. This value is expressed in seconds.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_SPECTRAL_ACQUISITION_SPAN = 45
    r"""Returns the recommended acquisition span for spectral acquisition. This value is expressed in Hz.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """

    RECOMMENDED_SPECTRAL_FFT_WINDOW = 46
    r"""Returns the recommended FFT window type for spectral acquisition.
    
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
    """

    RECOMMENDED_SPECTRAL_RESOLUTION_BANDWIDTH = 47
    r"""Returns the recommended FFT bin width for spectral acquisition. This value is expressed in Hz.
    
    .. note::
       This attribute is supported only when:
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1", or
    
    - :py:meth:`nirfmxinstr.session.Session` constructor is called with option string "AnalysisOnly=1;MaxNumWfms:<n>". Use "*instr<n>*" as the selector string to read this attribute.
    """
