"""attributes.py - Contains the ID of all attributes belongs to the module."""

from enum import Enum


class AttributeID(Enum):
    """This enum class contains the ID of all attributes belongs to the module."""

    SELECTED_PORTS = 1052669
    r"""Specifies the instrument port to be configured to acquire a signal. Use
    :py:meth:`nirfmxinstr.session.Session.get_available_ports` method to get the valid port names.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    **Valid values**
    
    +----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (value)   | Description                                                                                                              |
    +================+==========================================================================================================================+
    | PXIe-5830      | if0, if1                                                                                                                 |
    +----------------+--------------------------------------------------------------------------------------------------------------------------+
    | PXIe-5831/5832 | if0, if1, rf<0-1>/port<x>, where 0-1 indicates one (0) or two (1) mmRH-5582 connections and x is the port number on the  |
    |                | mmRH-5582 front panel                                                                                                    |
    +----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Other devices  | "" (empty string)                                                                                                        |
    +----------------+--------------------------------------------------------------------------------------------------------------------------+
    
    **Default values**
    
    +---------------------+-------------------+
    | Name (value)        | Description       |
    +=====================+===================+
    | PXIe-5830/5831/5832 | if1               |
    +---------------------+-------------------+
    | Other devices       | "" (empty string) |
    +---------------------+-------------------+
    """

    CENTER_FREQUENCY = 1048577
    r"""Specifies the expected carrier frequency of the RF signal that needs to be acquired. This value is expressed in Hz. The
    signal analyzer tunes to this frequency.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default of this attribute is hardware dependent.
    """

    REFERENCE_LEVEL = 1048578
    r"""Specifies the reference level which represents the maximum expected power of the RF input signal. This value is
    configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default of this attribute is hardware dependent.
    """

    EXTERNAL_ATTENUATION = 1048579
    r"""Specifies the attenuation of a switch (or cable) connected to the RF IN connector of the signal analyzer. This value is
    expressed in dB. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your
    device in the *NI RF Vector Signal Analyzers Help*.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    REFERENCE_LEVEL_HEADROOM = 1052668
    r"""Specifies the margin RFmx adds to the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute. The
    margin avoids clipping and overflow warnings if the input signal exceeds the configured reference level.
    
    RFmx configures the input gain to avoid clipping and associated overflow warnings provided the instantaneous
    power of the input signal remains within the Reference Level plus the Reference Level Headroom. If you know the input
    power of the signal precisely or previously included the margin in the Reference Level, you could improve the
    signal-to-noise ratio by reducing the Reference Level Headroom.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    **Supported devices: **PXIe-5668, PXIe-5830/5831/5832/5840/5841/5842/5860.
    
    **Default values**
    
    +------------------------------------+-------------+
    | Name (value)                       | Description |
    +====================================+=============+
    | PXIe-5668                          | 6 dB        |
    +------------------------------------+-------------+
    | PXIe-5830/5831/5832/5841/5842/5860 | 1 dB        |
    +------------------------------------+-------------+
    | PXIe-5840                          | 0 dB        |
    +------------------------------------+-------------+
    """

    TRIGGER_TYPE = 1048580
    r"""Specifies the trigger type.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **None**.
    
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)      | Description                                                                                                              |
    +===================+==========================================================================================================================+
    | None (0)          | No Reference Trigger is configured.                                                                                      |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Digital Edge (1)  | The Reference Trigger is not asserted until a digital edge is detected. The source of the digital edge is specified      |
    |                   | using the Digital Edge Source attribute.                                                                                 |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | IQ Power Edge (2) | The Reference Trigger is asserted when the signal changes past the level specified by the slope (rising or falling),     |
    |                   | which is configured using the IQ Power Edge Slope attribute.                                                             |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Software (3)      | The Reference Trigger is not asserted until a software trigger occurs.                                                   |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DIGITAL_EDGE_TRIGGER_SOURCE = 1048581
    r"""Specifies the source terminal for the digital edge trigger. This attribute is used only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default of this attribute is hardware dependent.
    """

    DIGITAL_EDGE_TRIGGER_EDGE = 1048582
    r"""Specifies the active edge for the trigger. This attribute is used only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Rising Edge**.
    
    +------------------+--------------------------------------------------------+
    | Name (Value)     | Description                                            |
    +==================+========================================================+
    | Rising Edge (0)  | The trigger asserts on the rising edge of the signal.  |
    +------------------+--------------------------------------------------------+
    | Falling Edge (1) | The trigger asserts on the falling edge of the signal. |
    +------------------+--------------------------------------------------------+
    """

    IQ_POWER_EDGE_TRIGGER_SOURCE = 1048583
    r"""Specifies the channel from which the device monitors the trigger. This attribute is used only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default of this attribute is hardware dependent.
    """

    IQ_POWER_EDGE_TRIGGER_LEVEL = 1048584
    r"""Specifies the power level at which the device triggers. This value is expressed in dB when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` attribute to **Relative** and is
    expressed in dBm when you set the IQ Power Edge Level Type attribute to **Absolute**. The device asserts the trigger
    when the signal exceeds the level specified by the value of this attribute, taking into consideration the specified
    slope. This attribute is used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`
    attribute to **IQ Power Edge**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default of this attribute is hardware dependent.
    """

    IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE = 1052671
    r"""Specifies the reference for the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL` attribute.
    The IQ Power Edge Level Type attribute is used only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Absolute**.
    
    +--------------+----------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                  |
    +==============+==============================================================================================+
    | Relative (0) | The IQ Power Edge Level attribute is relative to the value of the Reference Level attribute. |
    +--------------+----------------------------------------------------------------------------------------------+
    | Absolute (1) | The IQ Power Edge Level attribute specifies the absolute power.                              |
    +--------------+----------------------------------------------------------------------------------------------+
    """

    IQ_POWER_EDGE_TRIGGER_SLOPE = 1048585
    r"""Specifies whether the device asserts the trigger when the signal power is rising or when it is falling. The device
    asserts the trigger when the signal power exceeds the specified level with the slope you specify. This attribute is
    used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`  attribute to **IQ Power
    Edge**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Rising Slope**.
    
    +-------------------+-------------------------------------------------------+
    | Name (Value)      | Description                                           |
    +===================+=======================================================+
    | Rising Slope (0)  | The trigger asserts when the signal power is rising.  |
    +-------------------+-------------------------------------------------------+
    | Falling Slope (1) | The trigger asserts when the signal power is falling. |
    +-------------------+-------------------------------------------------------+
    """

    TRIGGER_DELAY = 1048586
    r"""Specifies the trigger delay time. This value is expressed in seconds.
    
    If the delay is negative, the measurement acquires pre-trigger samples. If the delay is positive, the
    measurement acquires post-trigger samples.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    TRIGGER_MINIMUM_QUIET_TIME_MODE = 1048587
    r"""Specifies whether the measurement computes the minimum quiet time used for triggering.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Manual**.
    
    +--------------+---------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                 |
    +==============+=============================================================================================+
    | Manual (0)   | The minimum quiet time for triggering is the value of the Trigger Min Quiet Time attribute. |
    +--------------+---------------------------------------------------------------------------------------------+
    | Auto (1)     | The measurement computes the minimum quiet time used for triggering.                        |
    +--------------+---------------------------------------------------------------------------------------------+
    """

    TRIGGER_MINIMUM_QUIET_TIME_DURATION = 1048588
    r"""Specifies the time duration for which the signal must be quiet before the signal analyzer arms the I/Q power edge
    trigger. This value is expressed in seconds. If you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE` attribute to **Rising Slope**, the signal
    is quiet below the trigger level.  If you set the IQ Power Edge Slope attribute to **Falling Slope**, the signal is
    quiet above the trigger level.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default of this attribute is hardware dependent.
    """

    NUMBER_OF_STEPS = 1052664
    r"""Specifies the number of active steps in a list.
    
    You need to use a selector string to configure or read this attribute for the list instance.
    
    The default value is 0.
    """

    LIST_STEP_TIMER_DURATION = 1052665
    r"""Specifies the duration of a given list step. This value is expressed in seconds.
    
    You need to use a selector string to configure or read this attribute for the list step instance.
    
    The default value is 0.
    """

    LIST_STEP_TIMER_OFFSET = 1052663
    r"""Specifies the time offset from the start of the step for which the measurements are computed. This value is expressed
    in seconds. This attribute is valid only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute to **TimerEvent**.
    
    You need to use a selector string to configure or read this attribute for the list step instance.
    
    The default value is 0.
    """

    ACP_MEASUREMENT_ENABLED = 1052672
    r"""Specifies whether to enable the ACP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    ACP_NUMBER_OF_CARRIERS = 1052674
    r"""Specifies the number of carriers.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    ACP_CARRIER_MODE = 1052675
    r"""Specifies whether to consider the carrier power as part of the total carrier power measurement.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Active**.
    
    +--------------+-------------------------------------------------------------------------+
    | Name (Value) | Description                                                             |
    +==============+=========================================================================+
    | Passive (0)  | The carrier power is not considered as part of the total carrier power. |
    +--------------+-------------------------------------------------------------------------+
    | Active (1)   | The carrier power is considered as part of the total carrier power.     |
    +--------------+-------------------------------------------------------------------------+
    """

    ACP_CARRIER_FREQUENCY = 1052676
    r"""Specifies the center frequency of the carrier, relative to the RF
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    ACP_CARRIER_INTEGRATION_BANDWIDTH = 1052677
    r"""Specifies the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 MHz.
    """

    ACP_CARRIER_RRC_FILTER_ENABLED = 1052678
    r"""Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before measuring the
    carrier channel power.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                        |
    +==============+====================================================================================================================+
    | False (0)    | The channel power of the acquired carrier channel is measured directly.                                            |
    +--------------+--------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement applies the RRC filter on the acquired carrier channel before measuring the carrier channel power. |
    +--------------+--------------------------------------------------------------------------------------------------------------------+
    """

    ACP_CARRIER_RRC_FILTER_ALPHA = 1052679
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.1.
    """

    ACP_NUMBER_OF_OFFSETS = 1052680
    r"""Specifies the number of offset channels.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    ACP_OFFSET_ENABLED = 1052681
    r"""Specifies whether to enable the offset channel for ACP measurement.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------+
    | Name (Value) | Description                                      |
    +==============+==================================================+
    | False (0)    | Disables the offset channel for ACP measurement. |
    +--------------+--------------------------------------------------+
    | True (1)     | Enables the offset channel for ACP measurement.  |
    +--------------+--------------------------------------------------+
    """

    ACP_OFFSET_FREQUENCY = 1052682
    r"""Specifies the center or edge frequency of the offset channel, relative to the center frequency of the closest carrier
    as determined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value
    is expressed in Hz. The sign of offset frequency is ignored and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_SIDEBAND` attribute determines whether the upper, lower, or both
    offsets are measured.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 MHz.
    """

    ACP_OFFSET_SIDEBAND = 1052683
    r"""Specifies whether the offset channel is present on one side, or on both sides of the carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Both**.
    
    +--------------+---------------------------------------------------------------------------+
    | Name (Value) | Description                                                               |
    +==============+===========================================================================+
    | Neg (0)      | Configures a lower offset segment to the left of the leftmost carrier.    |
    +--------------+---------------------------------------------------------------------------+
    | Pos (1)      | Configures an upper offset segment to the right of the rightmost carrier. |
    +--------------+---------------------------------------------------------------------------+
    | Both (2)     | Configures both negative and positive offset segments.                    |
    +--------------+---------------------------------------------------------------------------+
    """

    ACP_OFFSET_POWER_REFERENCE_CARRIER = 1052684
    r"""Specifies the carrier to be used as power reference to measure the offset channel relative power. The offset channel
    power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute of the
    reference carrier to **Active**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Closest**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | Closest (0)   | The measurement uses the power measured in the carrier closest to the offset channel center frequency, as the power      |
    |               | reference.                                                                                                               |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Highest (1)   | The measurement uses the highest power measured among all the active carriers as the power reference.                    |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Composite (2) | The measurement uses the sum of powers measured in all the active carriers as the power reference.                       |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Specific (3)  | The measurement uses the power measured in the carrier that has an index specified by the ACP Offset Pwr Ref Specific    |
    |               | attribute, as the power reference.                                                                                       |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_OFFSET_POWER_REFERENCE_SPECIFIC = 1052685
    r"""Specifies the index of the carrier to be used as the reference carrier. The power measured in this carrier is used as
    the power reference for measuring the offset channel relative power, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to **Specific**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    ACP_OFFSET_INTEGRATION_BANDWIDTH = 1052686
    r"""Specifies the frequency range, over which the measurement integrates the offset channel power. This value is expressed
    in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 MHz.
    """

    ACP_OFFSET_RELATIVE_ATTENUATION = 1052687
    r"""Specifies the attenuation relative to the external attenuation specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
    ACP Offset Rel Attn attribute to compensate for variations in external attenuation when the offset channels are spread
    wide in frequency.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    ACP_OFFSET_RRC_FILTER_ENABLED = 1052688
    r"""Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before measuring the
    offset channel power.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **False**.
    
    +--------------+------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                      |
    +==============+==================================================================================================================+
    | False (0)    | The channel power of the acquired offset channel is measured directly.                                           |
    +--------------+------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement applies the RRC filter on the acquired offset channel before measuring the offset channel power. |
    +--------------+------------------------------------------------------------------------------------------------------------------+
    """

    ACP_OFFSET_RRC_FILTER_ALPHA = 1052689
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.1.
    """

    ACP_OFFSET_FREQUENCY_DEFINITION = 1052727
    r"""Specifies the offset frequency definition used to specify the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY` attribute.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Carrier Center to Offset Center**.
    
    +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                        | Description                                                                                                       |
    +=====================================+===================================================================================================================+
    | Carrier Center to Offset Center (0) | The offset frequency is defined from the center of the closest carrier to the center of the offset channel.       |
    +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
    | Carrier Center to Offset Edge (1)   | The offset frequency is defined from the center of the closest carrier to the nearest edge of the offset channel. |
    +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
    """

    ACP_RBW_FILTER_AUTO_BANDWIDTH = 1052699
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+-------------------------------------------------------------------------+
    | Name (Value) | Description                                                             |
    +==============+=========================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the ACP RBW attribute. |
    +--------------+-------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                       |
    +--------------+-------------------------------------------------------------------------+
    """

    ACP_RBW_FILTER_BANDWIDTH = 1052700
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 kHz.
    """

    ACP_RBW_FILTER_TYPE = 1052701
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    +---------------+----------------------------------------------------+
    | Name (Value)  | Description                                        |
    +===============+====================================================+
    | FFT Based (0) | No RBW filtering is performed.                     |
    +---------------+----------------------------------------------------+
    | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
    +---------------+----------------------------------------------------+
    | Flat (2)      | An RBW filter with a flat response is applied.     |
    +---------------+----------------------------------------------------+
    """

    ACP_RBW_FILTER_BANDWIDTH_DEFINITION = 1052728
    r"""Specifies the bandwidth definition which you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the ACP RBW Filter Type attribute to FFT   |
    |               | Based, RBW is the 3dB bandwidth of the window specified by the ACP FFT Window attribute.                                 |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the bin width of the spectrum computed using FFT when you set the ACP RBW Filter Type        |
    |               | attribute to FFT Based.                                                                                                  |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_SWEEP_TIME_AUTO = 1052702
    r"""Specifies whether the measurement computes the sweep time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+----------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                            |
    +==============+========================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the ACP Sweep Time attribute.  |
    +--------------+----------------------------------------------------------------------------------------+
    | True (1)     | The measurement calculates the sweep time based on the value of the ACP RBW attribute. |
    +--------------+----------------------------------------------------------------------------------------+
    """

    ACP_SWEEP_TIME_INTERVAL = 1052703
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
    **False**. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    ACP_DETECTOR_TYPE = 1052738
    r"""Specifies the type of detector to be used.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **None**.
    
    Refer to `Spectral Measurements Concepts
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
    detector types.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | The detector is disabled.                                                                                                |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
    |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
    |                     | alternate buckets.                                                                                                       |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_DETECTOR_POINTS = 1052739
    r"""Specifies the number of trace points after the detector is applied.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1001.
    """

    ACP_POWER_UNITS = 1052691
    r"""Specifies the units for the absolute power.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **dBm**.
    
    +--------------+---------------------------------------------+
    | Name (Value) | Description                                 |
    +==============+=============================================+
    | dBm (0)      | The absolute powers are reported in dBm.    |
    +--------------+---------------------------------------------+
    | dBm/Hz (1)   | The absolute powers are reported in dBm/Hz. |
    +--------------+---------------------------------------------+
    """

    ACP_MEASUREMENT_METHOD = 1052690
    r"""Specifies the method for performing the ACP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Normal**.
    
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)       | Description                                                                                                              |
    +====================+==========================================================================================================================+
    | Normal (0)         | The ACP measurement acquires the spectrum using the same signal analyzer setting across frequency bands. Use this        |
    |                    | method when measurement speed is desirable over higher dynamic range.                                                    |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Dynamic Range (1)  | The ACP measurement acquires the spectrum using the hardware-specific optimizations for different frequency bands. Use   |
    |                    | this method to get the best dynamic range.                                                                               |
    |                    | Supported devices: PXIe-5665/5668                                                                                        |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sequential FFT (2) | The ACP measurement acquires I/Q samples for a duration specified by the ACP Sweep Time attribute. These samples are     |
    |                    | divided into smaller chunks. The size of each chunk is defined by the ACP Sequential FFT Size attribute. The overlap     |
    |                    | between the chunks is defined by the ACP FFT Overlap Mode                                                                |
    |                    | attribute. FFT is computed on each of these chunks. The resultant FFTs are averaged to get the spectrum and is used to   |
    |                    | compute ACP.                                                                                                             |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_NOISE_CALIBRATION_MODE = 1052737
    r"""Specifies whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
    Refer to the measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Auto**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | When you set the ACP Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration for     |
    |              | the ACP measurement manually. When you set the ACP Meas Mode attribute to Measure, you can initiate the ACP measurement  |
    |              | manually.                                                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Auto (1)     | When you set the ACP Noise Comp Enabled to True, RFmx sets the Input Isolation Enabled attribute to Enabled and          |
    |              | calibrates the instrument noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled     |
    |              | attribute and performs the ACP measurement, including compensation for noise of the instrument. RFmx skips noise         |
    |              | calibration in this mode if valid noise calibration data is already cached. When you set the ACP Noise Comp Enabled      |
    |              | attribute to False, RFmx does not calibrate instrument noise and only performs the ACP measurement without compensating  |
    |              | for noise of the instrument.                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_NOISE_CALIBRATION_AVERAGING_AUTO = 1052736
    r"""Specifies whether RFmx automatically computes the averaging count used for instrument noise calibration.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | RFmx uses the averages that you set for the ACP Noise Cal Averaging Count attribute.                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | When you set the ACP Meas Method attribute to Normal or Sequential FFT, RFmx uses a noise calibration averaging count    |
    |              | of 32. When you set the ACP Meas Method attribute to Dynamic Range and the sweep time is less than 5 ms, RFmx uses a     |
    |              | noise calibration averaging count of 15. When you set the ACP Meas Method attribute to Dynamic Range and the sweep time  |
    |              | is greater than or equal to 5 ms, RFmx uses a noise calibration averaging count of 5.                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_NOISE_CALIBRATION_AVERAGING_COUNT = 1052735
    r"""Specifies the averaging count used for noise calibration when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 32.
    """

    ACP_NOISE_COMPENSATION_ENABLED = 1052704
    r"""Specifies whether RFmx compensates for the instrument noise while performing the measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the ACP
    Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
    **Measure**. Refer to the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+------------------------------+
    | Name (Value) | Description                  |
    +==============+==============================+
    | False (0)    | Disables noise compensation. |
    +--------------+------------------------------+
    | True (1)     | Enables noise compensation.  |
    +--------------+------------------------------+
    """

    ACP_NOISE_COMPENSATION_TYPE = 1052734
    r"""Specifies the noise compensation type. Refer to the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Analyzer and Termination**.
    
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                 | Description                                                                                                              |
    +==============================+==========================================================================================================================+
    | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50-ohm termination. The measured power values are in excess of the       |
    |                              | thermal noise floor.                                                                                                     |
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_AVERAGING_ENABLED = 1052694
    r"""Specifies whether to enable averaging for the ACP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The ACP measurement uses the ACP Averaging Count attribute as the number of acquisitions over which the ACP measurement  |
    |              | is averaged.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_AVERAGING_COUNT = 1052693
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    ACP_AVERAGING_TYPE = 1052696
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for ACP
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    ACP_MEASUREMENT_MODE = 1052733
    r"""Specifies whether the measurement calibrates the noise floor of analyzer or performs the ACP measurement. Refer to the
    measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Measure**.
    
    +---------------------------+---------------------------------------------------------------------------------------+
    | Name (Value)              | Description                                                                           |
    +===========================+=======================================================================================+
    | Measure (0)               | ACP measurement is performed on the acquired signal.                                  |
    +---------------------------+---------------------------------------------------------------------------------------+
    | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the ACP measurement. |
    +---------------------------+---------------------------------------------------------------------------------------+
    """

    ACP_FFT_WINDOW = 1052697
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
    |                     | useful for time-frequency analysis.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_FFT_PADDING = 1052698
    r"""Specifies the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
    is given by the following formula:
    
    waveform size * padding
    
    This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
    device.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    """

    ACP_FFT_OVERLAP_MODE = 1052731
    r"""Specifies the overlap mode when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
    attribute to **Sequential FFT**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Disabled**.
    
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)     | Description                                                                                                              |
    +==================+==========================================================================================================================+
    | Disabled (0)     | Disables the overlap between the chunks.                                                                                 |
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Automatic (1)    | Measurement sets the overlap based on the value you have set for the ACP FFT Window attribute. When you set the ACP FFT  |
    |                  | Window attribute to any value other than None, the number of overlapped samples between consecutive chunks is set to     |
    |                  | 50% of the value of the ACP Sequential FFT Size attribute. When you set the ACP FFT Window attribute to None, the        |
    |                  | chunks are not overlapped and the overlap is set to 0%.                                                                  |
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    | User Defined (2) | Measurement uses the overlap that you specify in the ACP FFT Overlap attribute.                                          |
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_FFT_OVERLAP = 1052732
    r"""Specifies the samples to overlap between the consecutive chunks as a percentage of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT** and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute to **User Defined**. This value is expressed
    as a percentage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    ACP_IF_OUTPUT_POWER_OFFSET_AUTO = 1052724
    r"""Specifies whether the measurement computes an IF output power level offset for the offset channels to improve the
    dynamic range of the ACP measurement. This attribute is used only if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement sets the IF output power level offset using the values of the ACP Near IF Output Power Offset and ACP    |
    |              | Far IF Output Power Offset attributes.                                                                                   |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement automatically computes an IF output power level offset for the offset channels to improve the dynamic    |
    |              | range of the ACP measurement.                                                                                            |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_NEAR_IF_OUTPUT_POWER_OFFSET = 1052725
    r"""Specifies the offset by which to adjust the IF output power level for offset channels that are near to the carrier
    channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 dB.
    """

    ACP_FAR_IF_OUTPUT_POWER_OFFSET = 1052726
    r"""Specifies the offset by which to adjust the IF output power level for offset channels that are far from the carrier
    channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 20 dB.
    """

    ACP_SEQUENTIAL_FFT_SIZE = 1052730
    r"""Specifies the FFT size when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**.
    
    The default value is 512.
    """

    ACP_AMPLITUDE_CORRECTION_TYPE = 1052729
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    ACP_ALL_TRACES_ENABLED = 1052705
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the ACP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    ACP_NUMBER_OF_ANALYSIS_THREADS = 1052692
    r"""Specifies the maximum number of threads used for parallelism for adjacent channel power  (ACP) measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    ACP_RESULTS_TOTAL_CARRIER_POWER = 1052706
    r"""Returns the total integrated power, in dBm, of all the active carriers measured when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**.
    
    Returns the power spectral density, in dBm/Hz, based on the power in all the active carriers measured when you
    set the ACP Power Units attribute to **dBm/Hz**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    ACP_RESULTS_FREQUENCY_RESOLUTION = 1052707
    r"""Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    ACP_RESULTS_CARRIER_FREQUENCY = 1052708
    r"""Returns the center frequency of the carrier relative to the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_CARRIER_INTEGRATION_BANDWIDTH = 1052709
    r"""Returns the frequency range, over which the measurement integrates the carrier power. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_CARRIER_ABSOLUTE_POWER = 1052710
    r"""Returns the measured carrier power.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    The carrier power is reported in dBm when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the ACP
    Power Units attribute to **dBm/Hz**.
    """

    ACP_RESULTS_CARRIER_TOTAL_RELATIVE_POWER = 1052711
    r"""Returns the carrier power measured relative to the total carrier power of all active carriers. This value is expressed
    in dB.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_LOWER_OFFSET_FREQUENCY_REFERENCE_CARRIER = 1052712
    r"""Returns the index of the carrier used as a reference to define the center frequency of the lower (negative) offset
    channel. Lower offset channels are channels that are to the left of the carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_LOWER_OFFSET_FREQUENCY = 1052713
    r"""Returns the center frequency of the lower offset channel relative to the center frequency of the closest carrier. The
    offset frequency has a negative value.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_LOWER_OFFSET_INTEGRATION_BANDWIDTH = 1052714
    r"""Returns the integration bandwidth used to measure the power in the lower offset channel.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_LOWER_OFFSET_POWER_REFERENCE_CARRIER = 1052715
    r"""Returns the index of the carrier used as the power reference to measure the lower (negative) offset channel relative
    power.
    
    A value of -1 indicates that the total power of all active carriers is used as the reference power. The
    measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to set
    the power reference.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_LOWER_OFFSET_ABSOLUTE_POWER = 1052716
    r"""Returns the lower offset channel power.
    
    The offset channel power is reported in dBm when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the ACP
    Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_LOWER_OFFSET_RELATIVE_POWER = 1052717
    r"""Returns the lower offset channel power measured relative to the integrated power of the power reference carrier. This
    value is expressed in dB.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_UPPER_OFFSET_FREQUENCY_REFERENCE_CARRIER = 1052718
    r"""Returns the index of the carrier used as a reference to define the center frequency of the upper (positive) offset
    channel. Upper offset channels are channels that are to the right of the carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_UPPER_OFFSET_FREQUENCY = 1052719
    r"""Returns the center frequency of the upper offset channel relative to the center frequency of the closest carrier. The
    offset frequency has a positive value.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_UPPER_OFFSET_INTEGRATION_BANDWIDTH = 1052720
    r"""Returns the integration bandwidth used to measure the power in the upper offset channel.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_UPPER_OFFSET_POWER_REFERENCE_CARRIER = 1052721
    r"""Returns the index of the carrier used as the power reference to measure the upper (positive) offset channel relative
    power.
    
    A value of -1 indicates that the total power of all active carriers is used as the reference power. The
    measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to set
    the power reference.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_UPPER_OFFSET_ABSOLUTE_POWER = 1052722
    r"""Returns the upper offset channel power.
    
    The offset channel power is reported in dBm when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the ACP
    Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    ACP_RESULTS_UPPER_OFFSET_RELATIVE_POWER = 1052723
    r"""Returns the upper offset channel power measured relative to the integrated power of the power reference carrier. This
    value is expressed in dB.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    CCDF_MEASUREMENT_ENABLED = 1056768
    r"""Specifies whether to enable the CCDF measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    CCDF_MEASUREMENT_INTERVAL = 1056770
    r"""Specifies the acquisition time for the CCDF measurement. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    CCDF_NUMBER_OF_RECORDS = 1056772
    r"""Specifies the number of acquisitions used for the CCDF measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    CCDF_RBW_FILTER_BANDWIDTH = 1056775
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
    Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100 kHz.
    """

    CCDF_RBW_FILTER_TYPE = 1056776
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **None**.
    
    +--------------+-----------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                               |
    +==============+===========================================================================================================+
    | None (5)     | The measurement does not use any RBW filtering.                                                           |
    +--------------+-----------------------------------------------------------------------------------------------------------+
    | Gaussian (1) | The RBW filter has a Gaussian response.                                                                   |
    +--------------+-----------------------------------------------------------------------------------------------------------+
    | Flat (2)     | The RBW filter has a flat response.                                                                       |
    +--------------+-----------------------------------------------------------------------------------------------------------+
    | RRC (6)      | The RRC filter with the roll-off specified by the CCDF RBW RRC Alpha attribute is used as the RBW filter. |
    +--------------+-----------------------------------------------------------------------------------------------------------+
    """

    CCDF_RBW_FILTER_RRC_ALPHA = 1056774
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.1.
    """

    CCDF_THRESHOLD_ENABLED = 1056777
    r"""Specifies whether to enable thresholding of the acquired samples to be used for the CCDF measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | All samples are considered for the CCDF measurement.                                                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The samples above the threshold level specified in the CCDF Threshold Level attribute are considered for the CCDF        |
    |              | measurement.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CCDF_THRESHOLD_TYPE = 1056779
    r"""Specifies the reference for the power level used for thresholding.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Relative**.
    
    +--------------+----------------------------------------------------------------------+
    | Name (Value) | Description                                                          |
    +==============+======================================================================+
    | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
    +--------------+----------------------------------------------------------------------+
    | Absolute (1) | The threshold is the absolute power, in dBm.                         |
    +--------------+----------------------------------------------------------------------+
    """

    CCDF_THRESHOLD_LEVEL = 1056778
    r"""Specifies either the relative or absolute threshold power level based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20.
    """

    CCDF_ALL_TRACES_ENABLED = 1056781
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the CCDF measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    CCDF_NUMBER_OF_ANALYSIS_THREADS = 1056771
    r"""Specifies the maximum number of threads used for parallelism for CCDF measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    CCDF_RESULTS_MEAN_POWER = 1056782
    r"""Returns the average power of all the samples. This value is expressed in dBm. If you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**, samples above the threshold
    are measured.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_MEAN_POWER_PERCENTILE = 1056783
    r"""Returns the percentage of samples that have more power than the mean power.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_TEN_PERCENT_POWER = 1056784
    r"""Returns the power above the mean power, over which 10% of the total samples in the signal are present. This value is
    expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_ONE_PERCENT_POWER = 1056785
    r"""Returns the power above the mean power, over which 1% of the total samples in the signal are present. This value is
    expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_ONE_TENTH_PERCENT_POWER = 1056786
    r"""Returns the power above the mean power, over which 0.1% of the total samples in the signal are present. This value is
    expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_ONE_HUNDREDTH_PERCENT_POWER = 1056787
    r"""Returns the power above the mean power, over which 0.01% of the total samples in the signal are present. This value is
    expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_ONE_THOUSANDTH_PERCENT_POWER = 1056788
    r"""Returns the power above the mean power, over which 0.001% of the total samples in the signal are present. This value is
    expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_ONE_TEN_THOUSANDTH_PERCENT_POWER = 1056789
    r"""Returns the power above the mean power, over which 0.0001% of the total samples in the signal are present. This value
    is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CCDF_RESULTS_PEAK_POWER = 1056790
    r"""Returns the peak power of the acquired signal, relative to the mean power.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    CCDF_RESULTS_MEASURED_SAMPLES_COUNT = 1056791
    r"""Returns the total number of samples measured. The total number of samples includes only the samples above the
    threshold, when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CHP_MEASUREMENT_ENABLED = 1060864
    r"""Specifies whether to enable the CHP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    CHP_SPAN = 1060868
    r"""Specifies the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
    Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 MHz.
    """

    CHP_NUMBER_OF_CARRIERS = 1060888
    r"""Specifies the number of carriers.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    CHP_CARRIER_FREQUENCY = 1060889
    r"""Specifies the center frequency of the carrier, relative to the RF
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    CHP_CARRIER_INTEGRATION_BANDWIDTH = 1060866
    r"""Specifies the frequency range, over which the measurement integrates the power. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 MHz.
    """

    CHP_CARRIER_RRC_FILTER_ENABLED = 1060879
    r"""Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired channel before measuring the channel
    power.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **False**.
    
    +--------------+----------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                        |
    +==============+====================================================================================================+
    | False (0)    | The channel power of the acquired channel is measured directly.                                    |
    +--------------+----------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement applies the RRC filter on the acquired channel before measuring the channel power. |
    +--------------+----------------------------------------------------------------------------------------------------+
    """

    CHP_CARRIER_RRC_FILTER_ALPHA = 1060880
    r"""Specifies the roll-off factor of the root-raised-cosine (RRC) filter.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.1.
    """

    CHP_RBW_FILTER_AUTO_BANDWIDTH = 1060876
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+-------------------------------------------------------------------------+
    | Name (Value) | Description                                                             |
    +==============+=========================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the CHP RBW attribute. |
    +--------------+-------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                       |
    +--------------+-------------------------------------------------------------------------+
    """

    CHP_RBW_FILTER_BANDWIDTH = 1060877
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 kHz.
    """

    CHP_RBW_FILTER_TYPE = 1060878
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    +---------------+----------------------------------------------------+
    | Name (Value)  | Description                                        |
    +===============+====================================================+
    | FFT Based (0) | No RBW filtering is performed.                     |
    +---------------+----------------------------------------------------+
    | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
    +---------------+----------------------------------------------------+
    | Flat (2)      | An RBW filter with a flat response is applied.     |
    +---------------+----------------------------------------------------+
    """

    CHP_RBW_FILTER_BANDWIDTH_DEFINITION = 1060894
    r"""Specifies the bandwidth definition that you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the CHP RBW Filter Type attribute to FFT  |
    |               | Based, RBW is the 3 dB bandwidth of the window specified by the CHP FFT Window attribute.                                |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the CHP RBW Filter Type attribute  |
    |               | to FFT Based.                                                                                                            |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_SWEEP_TIME_AUTO = 1060881
    r"""Specifies whether the measurement computes the sweep time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+----------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                            |
    +==============+========================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the CHP Sweep Time attribute.  |
    +--------------+----------------------------------------------------------------------------------------+
    | True (1)     | The measurement calculates the sweep time based on the value of the CHP RBW attribute. |
    +--------------+----------------------------------------------------------------------------------------+
    """

    CHP_SWEEP_TIME_INTERVAL = 1060882
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
    **False**. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    CHP_DETECTOR_TYPE = 1060883
    r"""Specifies the type of detector to be used.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **None**.
    
    Refer to `Spectral Measurements Concepts
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
    detector types.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | The detector is disabled.                                                                                                |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
    |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
    |                     | alternate buckets.                                                                                                       |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_DETECTOR_POINTS = 1060902
    r"""Specifies the number of trace points after the detector is applied.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1001.
    """

    CHP_NOISE_CALIBRATION_MODE = 1060901
    r"""Specifies whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
    Refer to the measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Auto**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | When you set the CHP Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration for     |
    |              | the CHP measurement manually. When you set the CHP Meas Mode attribute to Measure, you can initiate the CHP measurement  |
    |              | manually.                                                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Auto (1)     | When you set the CHP Noise Comp Enabled attribute to True, RFmx sets Input Isolation Enabled to Enabled and calibrates   |
    |              | the intrument noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled attribute and   |
    |              | performs the CHP measurement, including compensation for noise of the instrument. RFmx skips noise calibration in this   |
    |              | mode if valid noise calibration data is already cached. When you set the CHP Noise Comp Enabled attribute to False,      |
    |              | RFmx does not calibrate instrument noise and performs only the CHP measurement without compensating for the noise        |
    |              | contribution of the instrument.                                                                                          |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_NOISE_CALIBRATION_AVERAGING_AUTO = 1060900
    r"""Specifies whether RFmx automatically computes the averaging count used for instrument noise calibration.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                          |
    +==============+======================================================================================+
    | False (0)    | RFmx uses the averages that you set for the CHP Noise Cal Averaging Count attribute. |
    +--------------+--------------------------------------------------------------------------------------+
    | True (1)     | RFmx uses a noise calibration averaging count of 32.                                 |
    +--------------+--------------------------------------------------------------------------------------+
    """

    CHP_NOISE_CALIBRATION_AVERAGING_COUNT = 1060899
    r"""Specifies the averaging count used for noise calibration when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 32.
    """

    CHP_NOISE_COMPENSATION_ENABLED = 1060897
    r"""Specifies whether RFmx compensates for the instrument noise when performing the measurement. To compensate for
    instrument noise when performing a CHP measurement, set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or set the CHP Noise Cal
    Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` attribute to
    **Measure**.
    Refer to the measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+------------------------------+
    | Name (Value) | Description                  |
    +==============+==============================+
    | False (0)    | Disables noise compensation. |
    +--------------+------------------------------+
    | True (1)     | Enables noise compensation.  |
    +--------------+------------------------------+
    """

    CHP_NOISE_COMPENSATION_TYPE = 1060898
    r"""Specifies the noise compensation type. Refer to the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Analyzer and Termination**.
    
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                 | Description                                                                                                              |
    +==============================+==========================================================================================================================+
    | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50 ohm termination. The measured power values are in excess of the       |
    |                              | thermal noise floor.                                                                                                     |
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_AVERAGING_ENABLED = 1060871
    r"""Specifies whether to enable averaging for the CHP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The CHP measurement uses the CHP Averaging Count attribute as the number of acquisitions over which the CHP measurement  |
    |              | is averaged.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_AVERAGING_COUNT = 1060870
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    CHP_AVERAGING_TYPE = 1060873
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for CHP
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    CHP_MEASUREMENT_MODE = 1060896
    r"""Specifies whether the measurement calibrates the noise floor of analyzer or performs the CHP measurement. Refer to the
    measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Measure**.
    
    +---------------------------+---------------------------------------------------------------------------------------+
    | Name (Value)              | Description                                                                           |
    +===========================+=======================================================================================+
    | Measure (0)               | CHP measurement is performed on the acquired signal.                                  |
    +---------------------------+---------------------------------------------------------------------------------------+
    | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the CHP measurement. |
    +---------------------------+---------------------------------------------------------------------------------------+
    """

    CHP_FFT_WINDOW = 1060874
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
    |                     | useful for time-frequency analysis.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_FFT_PADDING = 1060875
    r"""Specifies the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
    is given by the following formula:
    
    waveform size * padding
    
    This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
    device.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    """

    CHP_AMPLITUDE_CORRECTION_TYPE = 1060895
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    CHP_ALL_TRACES_ENABLED = 1060884
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the CHP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    CHP_NUMBER_OF_ANALYSIS_THREADS = 1060867
    r"""Specifies the maximum number of threads used for parallelism for CHP measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    CHP_RESULTS_TOTAL_CARRIER_POWER = 1060890
    r"""Returns the total integrated carrier power of all carriers, in dBm.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CHP_RESULTS_FREQUENCY_RESOLUTION = 1060887
    r"""Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    CHP_RESULTS_CARRIER_FREQUENCY = 1060891
    r"""Returns the center frequency of the carrier relative to the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    CHP_RESULTS_CARRIER_INTEGRATION_BANDWIDTH = 1060892
    r"""Returns the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    CHP_RESULTS_CARRIER_ABSOLUTE_POWER = 1060885
    r"""Returns the carrier power measured in the integration bandwidth that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_INTEGRATION_BANDWIDTH` attribute. This value is expressed in
    dBm.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    CHP_RESULTS_CARRIER_PSD = 1060886
    r"""Returns the power spectral density of the channel. This value is expressed in dBm/Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    CHP_RESULTS_CARRIER_RELATIVE_POWER = 1060893
    r"""Returns the carrier power measured relative to the total carrier power of all carriers. This value is expressed in dB.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    FCNT_MEASUREMENT_ENABLED = 1064960
    r"""Specifies whether to enable the FCnt measurement.
    
    You do not need to use a selector string to read this result for default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    
    The default value is FALSE.
    """

    FCNT_MEASUREMENT_INTERVAL = 1064962
    r"""Specifies the acquisition time for the FCnt measurement. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    FCNT_RBW_FILTER_BANDWIDTH = 1064970
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
    Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100 kHz.
    """

    FCNT_RBW_FILTER_TYPE = 1064971
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **None**.
    
    +--------------+-------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                           |
    +==============+=======================================================================================================+
    | None (5)     | The measurement does not use any RBW filtering.                                                       |
    +--------------+-------------------------------------------------------------------------------------------------------+
    | Gaussian (1) | The RBW filter has a Gaussian response.                                                               |
    +--------------+-------------------------------------------------------------------------------------------------------+
    | Flat (2)     | The RBW filter has a flat response.                                                                   |
    +--------------+-------------------------------------------------------------------------------------------------------+
    | RRC (6)      | The RRC filter with the roll-off specified by FCnt RBW RRC Alpha attribute is used as the RBW filter. |
    +--------------+-------------------------------------------------------------------------------------------------------+
    """

    FCNT_RBW_FILTER_RRC_ALPHA = 1064969
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.1.
    """

    FCNT_THRESHOLD_ENABLED = 1064972
    r"""Specifies whether to enable thresholding of the acquired samples to be used for the FCnt measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | All samples are considered for the FCnt measurement.                                                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The samples above the threshold level specified in the FCnt Threshold Level attribute are considered for the FCnt        |
    |              | measurement.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    FCNT_THRESHOLD_TYPE = 1064974
    r"""Specifies the reference for the power level used for thresholding.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Relative**.
    
    +--------------+----------------------------------------------------------------------+
    | Name (Value) | Description                                                          |
    +==============+======================================================================+
    | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
    +--------------+----------------------------------------------------------------------+
    | Absolute (1) | The threshold is the absolute power, in dBm.                         |
    +--------------+----------------------------------------------------------------------+
    """

    FCNT_THRESHOLD_LEVEL = 1064973
    r"""Specifies either the relative or absolute threshold power level based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20.
    """

    FCNT_AVERAGING_ENABLED = 1064966
    r"""Specifies whether to enable averaging for the FCnt measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The FCnt measurement uses the FCnt Averaging Count attribute as the number of acquisitions over which the FCnt           |
    |              | measurement is averaged.                                                                                                 |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    FCNT_AVERAGING_COUNT = 1064965
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    FCNT_AVERAGING_TYPE = 1064968
    r"""Specifies the averaging type for the FCnt measurement. The averaged instantaneous signal phase difference is used for
    the measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Mean**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Mean (6)     | The mean of the instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The minimum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Min Max (7)  | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement. The  |
    |              | sign of the phase difference is ignored to find the maximum instantaneous value.                                         |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    FCNT_ALL_TRACES_ENABLED = 1064976
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the FCnt measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    FCNT_NUMBER_OF_ANALYSIS_THREADS = 1064963
    r"""Specifies the maximum number of threads used for parallelism for FCnt measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    FCNT_RESULTS_AVERAGE_RELATIVE_FREQUENCY = 1064977
    r"""Returns the signal frequency relative to the RF center frequency. Only samples above the threshold are used when you
    set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    FCNT_RESULTS_AVERAGE_ABSOLUTE_FREQUENCY = 1064979
    r"""Returns the RF signal frequency. Only samples above the threshold are used when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    FCNT_RESULTS_MEAN_PHASE = 1064978
    r"""Returns the net phase of the vector sum of the I/Q samples used for frequency measurement.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    FCNT_RESULTS_ALLAN_DEVIATION = 1064980
    r"""Returns the two-sample deviation of the measured frequency.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    HARM_MEASUREMENT_ENABLED = 1069056
    r"""Specifies whether to enable the Harmonics measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_FUNDAMENTAL_RBW_FILTER_BANDWIDTH = 1069060
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the fundamental signal. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100 kHz.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_FUNDAMENTAL_RBW_FILTER_TYPE = 1069061
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+-----------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                           |
    +==============+=======================================================================================================================+
    | None (5)     | The measurement does not use any RBW filtering.                                                                       |
    +--------------+-----------------------------------------------------------------------------------------------------------------------+
    | Gaussian (1) | The RBW filter has a Gaussian response.                                                                               |
    +--------------+-----------------------------------------------------------------------------------------------------------------------+
    | Flat (2)     | The RBW filter                                                                                                        |
    |              | has a flat response.                                                                                                  |
    +--------------+-----------------------------------------------------------------------------------------------------------------------+
    | RRC (6)      | The RRC filter with the roll-off specified by the Harm Fundamental RBW RRC Alpha attribute is used as the RBW filter. |
    +--------------+-----------------------------------------------------------------------------------------------------------------------+
    """

    HARM_FUNDAMENTAL_RBW_FILTER_ALPHA = 1069059
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.1.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_FUNDAMENTAL_MEASUREMENT_INTERVAL = 1069062
    r"""Specifies the acquisition time for the Harmonics measurement of the fundamental signal. This value is expressed in
    seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_NUMBER_OF_HARMONICS = 1069063
    r"""Specifies the number of harmonics, including fundamental, to measure.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 3.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_AUTO_SETUP_ENABLED = 1069064
    r"""Specifies whether to enable auto configuration of successive harmonics.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement uses manual configuration for the harmonic order, harmonic bandwidth, and harmonic measurement           |
    |              | interval.                                                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement uses the Harm Num Harmonics attribute and configuration of the fundamental to configure successive       |
    |              | harmonics.                                                                                                               |
    |              | Bandwidth of Nth order harmonic = N * (Bandwidth of fundamental).                                                        |
    |              | Measurement interval of Nth order harmonics = (Measurement interval of fundamental)/N                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    HARM_HARMONIC_ENABLED = 1069065
    r"""Specifies whether to enable a particular harmonic for measurement. Only the enabled harmonics are used to measure the
    total harmonic distortion (THD). This attribute is not used if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+----------------------------------------+
    | Name (Value) | Description                            |
    +==============+========================================+
    | False (0)    | Disables the harmonic for measurement. |
    +--------------+----------------------------------------+
    | True (1)     | Enables the harmonic for measurement.  |
    +--------------+----------------------------------------+
    """

    HARM_HARMONIC_ORDER = 1069066
    r"""Specifies the order of the harmonic. This attribute is not used if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.
    
    Frequency of Nth order harmonic = N * (Frequency of fundamental)
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_HARMONIC_BANDWIDTH = 1069080
    r"""Specifies the resolution bandwidth for the harmonic. This attribute is not used if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**. This value is expressed in Hz.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 100 kHz.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_HARMONIC_MEASUREMENT_INTERVAL = 1069067
    r"""Specifies the acquisition time for the harmonic. This value is expressed in seconds. This attribute is not used if you
    set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 ms.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_MEASUREMENT_METHOD = 1069082
    r"""Specifies the method used to perform the harmonics measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Time Domain**.
    
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)      | Description                                                                                                              |
    +===================+==========================================================================================================================+
    | Time Domain (0)   | The harmonics measurement acquires the signal using the same signal analyzer setting across frequency bands. Use this    |
    |                   | method when the measurement speed is desirable over higher dynamic range.                                                |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Dynamic Range (2) | The harmonics measurement acquires the signal using the hardware-specific features, such as the IF filter and IF gain,   |
    |                   | for different frequency bands. Use this method to get the best dynamic range.                                            |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    HARM_NOISE_COMPENSATION_ENABLED = 1069083
    r"""Specifies whether to enable compensation of the average harmonic powers for inherent noise floor of the signal
    analyzer.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables compensation of the average harmonic powers for the noise floor of the signal analyzer.                         |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables compensation of the average harmonic powers for the noise floor of the signal analyzer. The noise floor of the   |
    |              | signal analyzer is measured for the RF path used by the harmonics measurement and cached for future use. If the signal   |
    |              | analyzer or measurement parameters change, noise floors are measured again.                                              |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    HARM_AVERAGING_ENABLED = 1069069
    r"""Specifies whether to enable averaging for the Harmonics measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The Harmonics measurement uses the Harm Averaging Count attribute as the number of acquisitions over which the           |
    |              | Harmonics measurement is averaged.                                                                                       |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    HARM_AVERAGING_COUNT = 1069068
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668
    """

    HARM_AVERAGING_TYPE = 1069071
    r"""Specifies the averaging type for the Harmonics measurement. The averaged power trace is used for the measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668
    
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                              |
    +==============+==========================================================================================================+
    | RMS (0)      | The power trace is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power trace is averaged in a logarithmic scale.                                                      |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power trace is averaged.                                                          |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Max (3)      | The maximum instantaneous power in the power trace is retained from one acquisition to the next.         |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Min (4)      | The minimum instantaneous power in the power trace is retained from one acquisition to the next.         |
    +--------------+----------------------------------------------------------------------------------------------------------+
    """

    HARM_ALL_TRACES_ENABLED = 1069072
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the Harmonics measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_NUMBER_OF_ANALYSIS_THREADS = 1069058
    r"""Specifies the maximum number of threads used for parallelism for Harmonics measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    
    **Supported devices**: PXIe-5665/5668
    """

    HARM_RESULTS_TOTAL_HARMONIC_DISTORTION = 1069075
    r"""Returns the total harmonics distortion (THD), measured as a percentage of the power in the fundamental signal.
    
    THD (%) = SQRT (Total power of all enabled harmonics - Power in fundamental) * 100 / Power in fundamental
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    HARM_RESULTS_AVERAGE_FUNDAMENTAL_POWER = 1069074
    r"""Returns the average power measured at the fundamental frequency. This value is expressed in dBm.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    HARM_RESULTS_FUNDAMENTAL_FREQUENCY = 1069073
    r"""Returns the frequency used as the fundamental frequency. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    HARM_RESULTS_HARMONIC_AVERAGE_ABSOLUTE_POWER = 1069078
    r"""Returns the average absolute power measured at the harmonic specified by the selector string. This value is expressed
    in dBm.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    HARM_RESULTS_HARMONIC_AVERAGE_RELATIVE_POWER = 1069079
    r"""Returns the average power relative to the fundamental power measured at the harmonic specified by the selector string.
    This value is expressed in dB.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    HARM_RESULTS_HARMONIC_FREQUENCY = 1069076
    r"""Returns the RF frequency of the harmonic. This value is expressed in Hz.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    HARM_RESULTS_HARMONIC_RBW = 1069077
    r"""Returns the resolution bandwidth (RBW) which is used by the harmonic measurement, for the harmonic specified by the
    selector string. This value is expressed in Hz.
    
    Use "harmonic<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    OBW_MEASUREMENT_ENABLED = 1073152
    r"""Specifies whether to enable OBW measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    OBW_SPAN = 1073156
    r"""Specifies the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
    Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 MHz.
    """

    OBW_BANDWIDTH_PERCENTAGE = 1073154
    r"""Specifies the percentage of the total power that is contained in the OBW.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 99%.
    """

    OBW_POWER_UNITS = 1073176
    r"""Specifies the units for the absolute power.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **dBm**.
    
    +--------------+---------------------------------------------+
    | Name (Value) | Description                                 |
    +==============+=============================================+
    | dBm (0)      | The absolute powers are reported in dBm.    |
    +--------------+---------------------------------------------+
    | dBm/Hz (1)   | The absolute powers are reported in dBm/Hz. |
    +--------------+---------------------------------------------+
    """

    OBW_RBW_FILTER_AUTO_BANDWIDTH = 1073164
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+-------------------------------------------------------------------------+
    | Name (Value) | Description                                                             |
    +==============+=========================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the OBW RBW attribute. |
    +--------------+-------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                       |
    +--------------+-------------------------------------------------------------------------+
    """

    OBW_RBW_FILTER_BANDWIDTH = 1073165
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 kHz.
    """

    OBW_RBW_FILTER_TYPE = 1073166
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    +---------------+-----------------------------------------+
    | Name (Value)  | Description                             |
    +===============+=========================================+
    | FFT Based (0) | No RBW filtering is performed.          |
    +---------------+-----------------------------------------+
    | Gaussian (1)  | The RBW filter has a Gaussian response. |
    +---------------+-----------------------------------------+
    | Flat (2)      | The RBW filter                          |
    |               | has a flat response.                    |
    +---------------+-----------------------------------------+
    """

    OBW_RBW_FILTER_BANDWIDTH_DEFINITION = 1073177
    r"""Specifies the bandwidth definition that you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the OBW RBW Filter Type attribute to FFT  |
    |               | Based, RBW is the 3 dB bandwidth of the window specified by the OBW FFT Window attribute.                                |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the OBW RBW Filter Type attribute  |
    |               | to FFT Based.                                                                                                            |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    OBW_SWEEP_TIME_AUTO = 1073167
    r"""Specifies whether the measurement computes the sweep time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+----------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                            |
    +==============+========================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the OBW Sweep Time attribute.  |
    +--------------+----------------------------------------------------------------------------------------+
    | True (1)     | The measurement calculates the sweep time based on the value of the OBW RBW attribute. |
    +--------------+----------------------------------------------------------------------------------------+
    """

    OBW_SWEEP_TIME_INTERVAL = 1073168
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
    **False**. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    OBW_AVERAGING_ENABLED = 1073159
    r"""Specifies whether to enable averaging for the OBW measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The OBW measurement uses the OBW Averaging Count attribute as the number of acquisitions over which the OBW measurement  |
    |              | is averaged.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    OBW_AVERAGING_COUNT = 1073158
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    OBW_AVERAGING_TYPE = 1073161
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for OBW
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    OBW_FFT_WINDOW = 1073162
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
    |                     | useful for time-frequency analysis.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    OBW_FFT_PADDING = 1073163
    r"""Specifies the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
    is given by the following formula:
    
    waveform size * padding
    
    This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
    device.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    """

    OBW_AMPLITUDE_CORRECTION_TYPE = 1073178
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    OBW_ALL_TRACES_ENABLED = 1073170
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the OBW.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    OBW_NUMBER_OF_ANALYSIS_THREADS = 1073155
    r"""Specifies the maximum number of threads used for parallelism for the OBW measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    OBW_RESULTS_OCCUPIED_BANDWIDTH = 1073171
    r"""Returns the bandwidth that occupies the percentage of the total power of the signal that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_PERCENTAGE` attribute. This value is expressed in Hz.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    OBW_RESULTS_AVERAGE_POWER = 1073172
    r"""Returns the total integrated power, in dBm, of the averaged spectrum acquired by the OBW measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. The OBW Results Avg Pwr attribute
    returns the power spectral density, in dBm/Hz,  when you set the OBW Power Units attribute to **dBm/Hz**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    OBW_RESULTS_START_FREQUENCY = 1073173
    r"""Returns the start frequency of the OBW. This value is expressed in Hz.
    
    The OBW is calculated using the following formula: OBW = stop frequency - start frequency
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    OBW_RESULTS_STOP_FREQUENCY = 1073174
    r"""Returns the stop frequency of the OBW. This value is expressed in Hz.
    
    The OBW is calculated using the following formula: OBW = stop frequency - start frequency
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    OBW_RESULTS_FREQUENCY_RESOLUTION = 1073175
    r"""Returns the frequency bin spacing of the spectrum acquired by the OBW measurement. This value is expressed in Hz.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    SEM_MEASUREMENT_ENABLED = 1081344
    r"""Specifies whether to enable the SEM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    SEM_NUMBER_OF_CARRIERS = 1081346
    r"""Specifies the number of carriers.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    SEM_CARRIER_ENABLED = 1081347
    r"""Specifies whether to consider the carrier power as part of the total carrier power measurement.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+-------------------------------------------------------------------------+
    | Name (Value) | Description                                                             |
    +==============+=========================================================================+
    | False (0)    | The carrier power is not considered as part of the total carrier power. |
    +--------------+-------------------------------------------------------------------------+
    | True (1)     | The carrier power is considered as part of the total carrier power.     |
    +--------------+-------------------------------------------------------------------------+
    """

    SEM_CARRIER_FREQUENCY = 1081348
    r"""Specifies the center frequency of the carrier, relative to the RF
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    SEM_CARRIER_INTEGRATION_BANDWIDTH = 1081349
    r"""Specifies the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 2 MHz.
    """

    SEM_CARRIER_CHANNEL_BANDWIDTH = 1081419
    r"""Specifies the channel bandwidth of the carrier. This parameter is used to calculate the values of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_START_FREQUENCY` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_STOP_FREQUENCY` attributes when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute to **Carrier Edge to Meas BW
    Center** or **Carrier Edge to Meas BW Edge**.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 2 MHz.
    """

    SEM_CARRIER_RBW_FILTER_AUTO_BANDWIDTH = 1081350
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW) of the carrier.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+---------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                     |
    +==============+=================================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the SEM Carrier RBW attribute. |
    +--------------+---------------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                               |
    +--------------+---------------------------------------------------------------------------------+
    """

    SEM_CARRIER_RBW_FILTER_BANDWIDTH = 1081351
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired carrier signal, when you
    set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
    value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 10 kHz.
    """

    SEM_CARRIER_RBW_FILTER_TYPE = 1081352
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Gaussian**.
    
    +---------------+-----------------------------------------+
    | Name (Value)  | Description                             |
    +===============+=========================================+
    | FFT Based (0) | No RBW filtering is performed.          |
    +---------------+-----------------------------------------+
    | Gaussian (1)  | The RBW filter has a Gaussian response. |
    +---------------+-----------------------------------------+
    | Flat (2)      | The RBW filter has a flat response.     |
    +---------------+-----------------------------------------+
    """

    SEM_CARRIER_RBW_FILTER_BANDWIDTH_DEFINITION = 1081422
    r"""Specifies the bandwidth definition that you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attribute.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the SEM Carrier RBW Filter Type           |
    |               | attribute to FFT Based, RBW is the 3 dB bandwidth of the window specified by the SEM FFT Window attribute.               |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the SEM Carrier RBW Filter Type    |
    |               | attribute to FFT Based.                                                                                                  |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_CARRIER_RRC_FILTER_ENABLED = 1081353
    r"""Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before measuring the
    carrier channel power.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                        |
    +==============+====================================================================================================================+
    | False (0)    | The channel power of the acquired carrier channel is measured directly.                                            |
    +--------------+--------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement applies the RRC filter on the acquired carrier channel before measuring the carrier channel power. |
    +--------------+--------------------------------------------------------------------------------------------------------------------+
    """

    SEM_CARRIER_RRC_FILTER_ALPHA = 1081354
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter to apply on the acquired carrier channel before
    measuring the carrier channel power.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.1.
    """

    SEM_NUMBER_OF_OFFSETS = 1081355
    r"""Specifies the number of offset segments.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    SEM_OFFSET_ENABLED = 1081362
    r"""Specifies whether to enable the offset segment for SEM measurement.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------+
    | Name (Value) | Description                                          |
    +==============+======================================================+
    | False (0)    | Disables the offset segment for the SEM measurement. |
    +--------------+------------------------------------------------------+
    | True (1)     | Enables the offset segment for the SEM measurement.  |
    +--------------+------------------------------------------------------+
    """

    SEM_OFFSET_START_FREQUENCY = 1081364
    r"""Specifies the start frequency of the offset segment relative to the closest configured carrier channel bandwidth center
    or carrier channel bandwidth edge based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 MHz.
    """

    SEM_OFFSET_STOP_FREQUENCY = 1081365
    r"""Specifies the stop frequency of the offset segment relative to the closest configured carrier  channel bandwidth center
    or carrier channel bandwidth edge based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 2 MHz.
    """

    SEM_OFFSET_SIDEBAND = 1081363
    r"""Specifies whether the offset segment is present on one side, or on both sides of the carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Both**.
    
    +--------------+---------------------------------------------------------------------------+
    | Name (Value) | Description                                                               |
    +==============+===========================================================================+
    | Neg (0)      | Configures a lower offset segment to the left of the leftmost carrier.    |
    +--------------+---------------------------------------------------------------------------+
    | Pos (1)      | Configures an upper offset segment to the right of the rightmost carrier. |
    +--------------+---------------------------------------------------------------------------+
    | Both (2)     | Configures both negative and positive offset segments.                    |
    +--------------+---------------------------------------------------------------------------+
    """

    SEM_OFFSET_RBW_FILTER_AUTO_BANDWIDTH = 1081366
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW).
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                    |
    +==============+================================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the SEM Offset RBW attribute. |
    +--------------+--------------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                              |
    +--------------+--------------------------------------------------------------------------------+
    """

    SEM_OFFSET_RBW_FILTER_BANDWIDTH = 1081367
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired offset segment, when you
    set the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
    value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 10 kHz.
    """

    SEM_OFFSET_RBW_FILTER_TYPE = 1081368
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Gaussian**.
    
    +---------------+-----------------------------------------+
    | Name (Value)  | Description                             |
    +===============+=========================================+
    | FFT Based (0) | No RBW filtering is performed.          |
    +---------------+-----------------------------------------+
    | Gaussian (1)  | The RBW filter has a Gaussian response. |
    +---------------+-----------------------------------------+
    | Flat (2)      | The RBW filter has a flat response.     |
    +---------------+-----------------------------------------+
    """

    SEM_OFFSET_RBW_FILTER_BANDWIDTH_DEFINITION = 1081421
    r"""Specifies the bandwidth definition which you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` attribute.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the SEM Offset RBW Filter Type attribute   |
    |               | to FFT Based, RBW is the 3dB bandwidth of the window specified by the SEM FFT Window attribute.                          |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the SEM Offset RBW Filter Type        |
    |               | attribute to FFT Based.                                                                                                  |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_OFFSET_BANDWIDTH_INTEGRAL = 1081356
    r"""Specifies the resolution of the spectrum to compare with spectral mask limits as an integer multiple of the resolution
    bandwidth (RBW).
    
    If you set this attribute to a value greater than 1, the measurement acquires the spectrum with a narrow
    resolution and then processes it digitally to get a wider resolution that is equal to the product of the bandwidth
    integral and the RBW.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1.
    """

    SEM_OFFSET_RELATIVE_ATTENUATION = 1081358
    r"""Specifies the attenuation relative to the external attenuation specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
    SEM Offset Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
    wide in frequency.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    SEM_OFFSET_LIMIT_FAIL_MASK = 1081357
    r"""Specifies the criteria to determine the measurement fail status.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Absolute**.
    
    +-----------------+-------------------------------------------------------------------------------------------------+
    | Name (Value)    | Description                                                                                     |
    +=================+=================================================================================================+
    | Abs AND Rel (0) | The measurement fails if the power in the segment exceeds both the absolute and relative masks. |
    +-----------------+-------------------------------------------------------------------------------------------------+
    | Abs OR Rel (1)  | The measurement fails if the power in the segment exceeds either the absolute or relative mask. |
    +-----------------+-------------------------------------------------------------------------------------------------+
    | Absolute (2)    | The measurement fails if the power in the segment exceeds the absolute mask.                    |
    +-----------------+-------------------------------------------------------------------------------------------------+
    | Relative (3)    | The measurement fails if the power in the segment exceeds the relative mask.                    |
    +-----------------+-------------------------------------------------------------------------------------------------+
    """

    SEM_OFFSET_ABSOLUTE_LIMIT_MODE = 1081359
    r"""Specifies whether the absolute limit mask is a flat line or a line with a slope.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Couple**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | The line specified by the SEM Offset Abs Limit Start and SEM Offset Abs Limit Stop attribute values as the two ends is   |
    |              | considered as the mask.                                                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Abs Limit Start attribute.                           |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_OFFSET_ABSOLUTE_LIMIT_START = 1081360
    r"""Specifies the absolute power limit corresponding to the beginning of the offset segment. This value is expressed in
    dBm. This power limit is also set as the stop limit for the offset segment when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -10.
    """

    SEM_OFFSET_ABSOLUTE_LIMIT_STOP = 1081361
    r"""Specifies the absolute power limit corresponding to the end of the offset segment. This value is expressed in dBm. The
    measurement ignores this attribute when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -10.
    """

    SEM_OFFSET_RELATIVE_LIMIT_MODE = 1081369
    r"""Specifies whether the relative limit mask is a flat line or a line with a slope.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Manual**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | The line specified by the SEM Offset Rel Limit Start and SEM Offset Rel Limit Stop attribute values as the two ends is   |
    |              | considered as the mask.                                                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Rel Limit Start attribute.                           |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_OFFSET_RELATIVE_LIMIT_START = 1081370
    r"""Specifies the relative power limit corresponding to the beginning of the offset segment. This value is expressed in dB.
    This power limit is also set as the stop limit for the offset segment when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -20.
    """

    SEM_OFFSET_RELATIVE_LIMIT_STOP = 1081371
    r"""Specifies the relative power limit corresponding to the end of the offset segment. This value is expressed in dB. The
    measurement ignores this attribute when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -30.
    """

    SEM_OFFSET_FREQUENCY_DEFINITION = 1081420
    r"""Specifies the definition of  the start frequency and stop frequency of the offset segments from the nearest carrier
    channels.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Carrier Center to Meas BW Center**.
    
    +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                         | Description                                                                                                              |
    +======================================+==========================================================================================================================+
    | Carrier Center to Meas BW Center (0) | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
    |                                      | center of the offset segment measurement bandwidth.                                                                      |
    |                                      | Measurement Bandwidth = Resolution Bandwidth * Bandwidth Integral.                                                       |
    +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Carrier Center to Meas BW Edge (1)   | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
    |                                      | nearest edge of the offset segment measurement bandwidth.                                                                |
    +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Carrier Edge to Meas BW Center (2)   | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
    |                                      | the center of the nearest offset segment measurement bandwidth.                                                          |
    +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Carrier Edge to Meas BW Edge (3)     | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
    |                                      | the edge of the nearest offset segment measurement bandwidth.                                                            |
    +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_POWER_UNITS = 1081372
    r"""Specifies the units for the absolute power.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **dBm**.
    
    +--------------+---------------------------------------------+
    | Name (Value) | Description                                 |
    +==============+=============================================+
    | dBm (0)      | The absolute powers are reported in dBm.    |
    +--------------+---------------------------------------------+
    | dBm/Hz (1)   | The absolute powers are reported in dBm/Hz. |
    +--------------+---------------------------------------------+
    """

    SEM_REFERENCE_TYPE = 1081380
    r"""Specifies whether the power reference is the integrated power or the peak power in the closest carrier channel.
    The leftmost carrier is the carrier closest to all the lower (negative) offset segments. The rightmost carrier
    is the carrier closest to all the upper (positive) offset segments.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Integration**.
    
    +-----------------+---------------------------------------------------------------------+
    | Name (Value)    | Description                                                         |
    +=================+=====================================================================+
    | Integration (0) | The power reference is the integrated power of the closest carrier. |
    +-----------------+---------------------------------------------------------------------+
    | Peak (1)        | The power reference is the peak power of the closest carrier.       |
    +-----------------+---------------------------------------------------------------------+
    """

    SEM_SWEEP_TIME_AUTO = 1081381
    r"""Specifies whether the measurement computes the sweep time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+---------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                         |
    +==============+=====================================================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the SEM Sweep Time attribute.                               |
    +--------------+---------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement calculates the sweep time based on the value of the SEM Offset RBW and                              |
    |              | SEM Carrier RBW attributes.                                                                                         |
    +--------------+---------------------------------------------------------------------------------------------------------------------+
    """

    SEM_SWEEP_TIME_INTERVAL = 1081382
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
    **False**. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    SEM_AVERAGING_ENABLED = 1081375
    r"""Specifies whether to enable averaging for the SEM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The SEM measurement uses the SEM Averaging Count attribute as the number of acquisitions over which the SEM measurement  |
    |              | is averaged.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_AVERAGING_COUNT = 1081374
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    SEM_AVERAGING_TYPE = 1081377
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for SEM
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    SEM_FFT_WINDOW = 1081378
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
    |                     | useful for time-frequency analysis.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_FFT_PADDING = 1081379
    r"""Specifies the factor by which the time-domain waveform is zero-padded before FFT. The FFT size is given by the
    following formula:
    
    waveform size * padding
    
    This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
    device.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    """

    SEM_AMPLITUDE_CORRECTION_TYPE = 1081423
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SEM_ALL_TRACES_ENABLED = 1081383
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the SEM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    SEM_NUMBER_OF_ANALYSIS_THREADS = 1081373
    r"""Specifies the maximum number of threads used for parallelism for SEM measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    SEM_RESULTS_TOTAL_CARRIER_POWER = 1081384
    r"""Returns the total integrated power, in dBm, of all the enabled carriers measured when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. Returns the power spectral density,
    in dBm/Hz, when you set the SEM Power Units attribute to **dBm/Hz**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    SEM_RESULTS_COMPOSITE_MEASUREMENT_STATUS = 1081385
    r"""Indicates the overall measurement status based on the measurement limits and the fail criteria that you set in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute for each offset segment.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    
    +--------------+--------------------------------------------+
    | Name (Value) | Description                                |
    +==============+============================================+
    | Fail (0)     | Indicates that the measurement has failed. |
    +--------------+--------------------------------------------+
    | Pass (1)     | Indicates that the measurement has passed. |
    +--------------+--------------------------------------------+
    """

    SEM_RESULTS_FREQUENCY_RESOLUTION = 1081386
    r"""Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    SEM_RESULTS_CARRIER_TOTAL_RELATIVE_POWER = 1081390
    r"""Returns the carrier power relative to the total carrier power of all enabled carriers. This value is expressed in dB.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_CARRIER_ABSOLUTE_POWER = 1081389
    r"""Returns the carrier power.
    
    The carrier power is reported in dBm when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the SEM
    Power Units attribute to **dBm/Hz**.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_CARRIER_PEAK_ABSOLUTE_POWER = 1081391
    r"""Returns the peak power in the carrier channel.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_CARRIER_PEAK_FREQUENCY = 1081392
    r"""Returns the frequency at which the peak power occurs in the carrier channel. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_CARRIER_FREQUENCY = 1081387
    r"""Returns the center frequency of the carrier relative to the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_CARRIER_INTEGRATION_BANDWIDTH = 1081388
    r"""Returns the frequency range, over which the measurement integrates the carrier power. This value is expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_MEASUREMENT_STATUS = 1081405
    r"""Indicates the lower offset segment measurement status based on measurement limits and the fail criteria that you
    specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    +--------------+--------------------------------------------+
    | Name (Value) | Description                                |
    +==============+============================================+
    | Fail (0)     | Indicates that the measurement has failed. |
    +--------------+--------------------------------------------+
    | Pass (1)     | Indicates that the measurement has passed. |
    +--------------+--------------------------------------------+
    """

    SEM_RESULTS_LOWER_OFFSET_TOTAL_ABSOLUTE_POWER = 1081396
    r"""Returns the power measured in the lower (negative) offset segment.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_TOTAL_RELATIVE_POWER = 1081397
    r"""Returns the power measured in the lower (negative) offset segment relative to either the integrated or peak power of
    the reference carrier.
    
    When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
    the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
    **Peak**, the reference carrier power is the peak power in the reference carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_PEAK_ABSOLUTE_POWER = 1081398
    r"""Returns the peak power measured in the lower (negative) offset segment.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_PEAK_RELATIVE_POWER = 1081399
    r"""Returns the peak power measured in the lower (negative) offset segment relative to the integrated or peak power of the
    reference carrier.
    
    When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
    the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
    **Peak**, the reference carrier power is the peak power in the reference carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_PEAK_FREQUENCY = 1081400
    r"""Returns the frequency at which the peak power occurred in the lower offset segment. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_MARGIN = 1081401
    r"""Returns the margin from the limit mask value that you set in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. This value is expressed in dB. Margin
    is defined as the maximum difference between the spectrum and the limit mask.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
    absolute limit mask.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Relative**, the margin is with reference to the
    relative limit mask.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
    margins referenced to the absolute and relative limit masks.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
    margins referenced to the absolute and relative limit masks.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_MARGIN_ABSOLUTE_POWER = 1081402
    r"""Returns the power, at which the margin occurred in the lower (negative) offset segment.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_MARGIN_RELATIVE_POWER = 1081403
    r"""Returns the power at which the margin occurred in the lower (negative) offset segment relative to the integrated or
    peak power of the reference carrier. This value is expressed in dB.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_MARGIN_FREQUENCY = 1081404
    r"""Returns the frequency at which the margin occurred in the lower (negative) offset segment. This value is expressed in
    Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_START_FREQUENCY = 1081393
    r"""Returns the start frequency of the lower (negative) offset segment. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_STOP_FREQUENCY = 1081394
    r"""Returns the stop frequency of the lower (negative) offset segment. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_LOWER_OFFSET_POWER_REFERENCE_CARRIER = 1081395
    r"""Returns the index of the carrier that was used as the power reference to define the lower (negative) offset segment
    relative power. The reference carrier is the carrier that has an offset closest to the offset segment.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_MEASUREMENT_STATUS = 1081418
    r"""Indicates the upper offset measurement status based on measurement limits and the fail criteria that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    +--------------+--------------------------------------------+
    | Name (Value) | Description                                |
    +==============+============================================+
    | Fail (0)     | Indicates that the measurement has failed. |
    +--------------+--------------------------------------------+
    | Pass (1)     | Indicates that the measurement has passed. |
    +--------------+--------------------------------------------+
    """

    SEM_RESULTS_UPPER_OFFSET_TOTAL_ABSOLUTE_POWER = 1081409
    r"""Returns the offset segment power measured in the upper (positive) offset segment.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_TOTAL_RELATIVE_POWER = 1081410
    r"""Returns the power measured in the upper (positive) offset segment relative to the integrated or peak power of the
    reference carrier.
    
    When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
    the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
    **Peak**, the reference carrier power is the peak power in the reference.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_PEAK_ABSOLUTE_POWER = 1081411
    r"""Returns the peak power measured in the upper (positive) offset segment.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_PEAK_RELATIVE_POWER = 1081412
    r"""Returns the peak power measured in the upper (positive) offset segment relative to the integrated or peak power of the
    reference carrier.
    
    When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
    the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
    **Peak**, the reference carrier power is the peak power in the reference carrier.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_PEAK_FREQUENCY = 1081413
    r"""Returns the frequency at which the peak power occurred in the upper offset segment. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_MARGIN = 1081414
    r"""Returns the margin from the limit mask value that you set in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. This value is expressed in dB. Margin
    is defined as the maximum difference between the spectrum and the limit mask.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
    absolute limit mask.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Relative**, the margin is with reference to the
    relative limit mask.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
    margin referenced to the absolute and relative limit masks.
    
    When you set the SEM Offset Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
    margin referenced to the absolute and relative limit masks.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_MARGIN_ABSOLUTE_POWER = 1081415
    r"""Returns the power, at which the margin occurred in the upper (positive) offset segment.
    
    The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
    attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_MARGIN_RELATIVE_POWER = 1081416
    r"""Returns the power at which the margin occurred in the upper (positive) offset segment relative to the integrated or
    peak power of the reference carrier. This value is expressed in dB.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_MARGIN_FREQUENCY = 1081417
    r"""Returns the frequency at which the margin occurred in the upper (positive)  offset. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_START_FREQUENCY = 1081406
    r"""Returns the start frequency of the upper (positive) offset segment. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_STOP_FREQUENCY = 1081407
    r"""Returns the stop frequency of the upper (positive) offset segment. This value is expressed in Hz.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SEM_RESULTS_UPPER_OFFSET_POWER_REFERENCE_CARRIER = 1081408
    r"""Returns the index of the carrier that was used as the power reference to define the upper (positive) offset segment
    relative power. The reference carrier is the carrier that has an offset closest to the offset segment.
    
    Use "offset<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    SPECTRUM_MEASUREMENT_ENABLED = 1085440
    r"""Specifies whether to enable the spectrum measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    SPECTRUM_SPAN = 1085443
    r"""Specifies the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
    Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 MHz.
    """

    SPECTRUM_POWER_UNITS = 1085461
    r"""Specifies the units for the absolute power.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **dBm**.
    
    +-------------------+---------------------------------------------+
    | Name (Value)      | Description                                 |
    +===================+=============================================+
    | dBm (0)           | The absolute powers are reported in dBm.    |
    +-------------------+---------------------------------------------+
    | dBm/Hz (1)        | The absolute powers are reported in dBm/Hz. |
    +-------------------+---------------------------------------------+
    | dBW (2)           | The absolute powers are reported in dBW.    |
    +-------------------+---------------------------------------------+
    | dBV (3)           | The absolute powers are reported in dBV.    |
    +-------------------+---------------------------------------------+
    | dBmV (4)          | The absolute powers are reported in dBmV.   |
    +-------------------+---------------------------------------------+
    | dBuV (5)          | The absolute powers are reported in dBuV.   |
    +-------------------+---------------------------------------------+
    | W (6)             | The absolute powers are reported in W.      |
    +-------------------+---------------------------------------------+
    | Volts (7)         | The absolute powers are reported in volts.  |
    +-------------------+---------------------------------------------+
    | Volts Squared (8) | The absolute powers are reported in volts2. |
    +-------------------+---------------------------------------------+
    """

    SPECTRUM_RBW_FILTER_AUTO_BANDWIDTH = 1085451
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                  |
    +==============+==============================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the Spectrum RBW attribute. |
    +--------------+------------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                            |
    +--------------+------------------------------------------------------------------------------+
    """

    SPECTRUM_RBW_FILTER_BANDWIDTH = 1085452
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 kHz.
    """

    SPECTRUM_RBW_FILTER_TYPE = 1085453
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    +---------------+-----------------------------------------+
    | Name (Value)  | Description                             |
    +===============+=========================================+
    | FFT Based (0) | No RBW filtering is performed.          |
    +---------------+-----------------------------------------+
    | Gaussian (1)  | The RBW filter has a Gaussian response. |
    +---------------+-----------------------------------------+
    | Flat (2)      | The RBW filter has a flat response.     |
    +---------------+-----------------------------------------+
    """

    SPECTRUM_RBW_FILTER_BANDWIDTH_DEFINITION = 1085462
    r"""Specifies the bandwidth definition which you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to  |
    |               | FFT Based, RBW is the 3dB bandwidth of the window specified by the Spectrum FFT Window attribute.                        |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | 6dB (1)       | Defines the RBW in terms of the 6dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to  |
    |               | FFT Based, RBW is the 6dB bandwidth of the window specified by the Spectrum FFT Window attribute.                        |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spectrum RBW Filter Type          |
    |               | attribute to FFT Based.                                                                                                  |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | ENBW (3)      | Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute    |
    |               | to FFT Based, RBW is the ENBW                                                                                            |
    |               | bandwidth of the window specified by the Spectrum FFT Window attribute.                                                  |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_VBW_FILTER_AUTO_BANDWIDTH = 1085466
    r"""Specifies whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Specify the video bandwidth in the Spectrum VBW attribute. The Spectrum VBW to RBW Ratio attribute is disregarded in     |
    |              | this mode.                                                                                                               |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
    |              | the Spectrum VBW to RBW Ratio attribute and the Spectrum RBW attribute. The value of the Spectrum VBW attribute is       |
    |              | disregarded in this mode.                                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_VBW_FILTER_BANDWIDTH = 1085467
    r"""Specifies the video bandwidth (VBW) in Hz when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 30000.
    """

    SPECTRUM_VBW_FILTER_VBW_TO_RBW_RATIO = 1085468
    r"""Specifies the VBW to RBW Ratio when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True** .
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 3.
    """

    SPECTRUM_SWEEP_TIME_AUTO = 1085454
    r"""Specifies whether the measurement computes the sweep time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+---------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                 |
    +==============+=============================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the Spectrum Sweep Time attribute.  |
    +--------------+---------------------------------------------------------------------------------------------+
    | True (1)     | The measurement calculates the sweep time based on the value of the Spectrum RBW attribute. |
    +--------------+---------------------------------------------------------------------------------------------+
    """

    SPECTRUM_SWEEP_TIME_INTERVAL = 1085455
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
    **False**. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    SPECTRUM_DETECTOR_TYPE = 1085464
    r"""Specifies the type of detector to be used.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **None**.
    
    Refer to `Spectral Measurements Concepts
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
    detector types.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | The detector is disabled.                                                                                                |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
    |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
    |                     | alternate buckets.                                                                                                       |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_DETECTOR_POINTS = 1085465
    r"""Specifies the number of trace points after the detector is applied.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1001.
    """

    SPECTRUM_NOISE_CALIBRATION_MODE = 1085474
    r"""Specifies whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
    Refer to the measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Auto**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | When you set the Spectrum Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration    |
    |              | for the spectrum measurement manually. When you set the Spectrum Meas Mode attribute to Measure, you can initiate the    |
    |              | spectrum measurement manually.                                                                                           |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Auto (1)     | When you set the Spectrum Noise Comp Enabled attribute to True, RFmx sets the Input Isolation Enabled attribute to       |
    |              | Enabled and calibrates the intrument noise in the current state of the instrument. RFmx then resets the Input Isolation  |
    |              | Enabled attribute and performs the spectrum measurement, including compensation for noise from the instrument. RFmx      |
    |              | skips noise calibration in this mode if valid noise calibration data is already cached. When you set the Spectrum Noise  |
    |              | Comp Enabled attribute to False, RFmx does not calibrate instrument noise and performs only the spectrum measurement     |
    |              | without compensating for the noise from the instrument.                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_NOISE_CALIBRATION_AVERAGING_AUTO = 1085473
    r"""Specifies whether RFmx automatically computes the averaging count used for instrument noise calibration.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+-------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                               |
    +==============+===========================================================================================+
    | False (0)    | RFmx uses the averages that you set for the Spectrum Noise Cal Averaging Count attribute. |
    +--------------+-------------------------------------------------------------------------------------------+
    | True (1)     | RFmx uses a noise calibration averaging count of 32.                                      |
    +--------------+-------------------------------------------------------------------------------------------+
    """

    SPECTRUM_NOISE_CALIBRATION_AVERAGING_COUNT = 1085472
    r"""Specifies the averaging count used for noise calibration when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO`
    attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 32.
    """

    SPECTRUM_NOISE_COMPENSATION_ENABLED = 1085456
    r"""Specifies whether RFmx compensates for the instrument noise while performing the measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the
    Spectrum Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
    **Measure**. Refer to the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    **Supported Devices:** PXIe-5663/5665/5668, PXIe-5830/5831/5832
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables compensation of the spectrum for the noise floor of the signal analyzer.                                        |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables compensation of the spectrum for the noise floor of the signal analyzer. The noise floor of the signal analyzer  |
    |              | is measured for the RF path used by the Spectrum measurement and cached for future use. If signal analyzer or            |
    |              | measurement parameters change, noise floors are measured again.                                                          |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_NOISE_COMPENSATION_TYPE = 1085471
    r"""Specifies the noise compensation type. Refer to the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Analyzer and Termination**.
    
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                 | Description                                                                                                              |
    +==============================+==========================================================================================================================+
    | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50 ohm termination. The measured power values are in excess of the       |
    |                              | thermal noise floor.                                                                                                     |
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
    +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_AVERAGING_ENABLED = 1085446
    r"""Specifies whether to enable averaging for the spectrum measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The spectrum measurement uses the Spectrum Averaging Count attribute as the number of acquisitions over which the        |
    |              | spectrum measurement is averaged.                                                                                        |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_AVERAGING_COUNT = 1085445
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    SPECTRUM_AVERAGING_TYPE = 1085448
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spectrum
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_MEASUREMENT_MODE = 1085470
    r"""Specifies whether the measurement calibrates the noise floor of analyzer or performs the spectrum measurement. Refer to
    the measurement guidelines section in the `Noise Compensation Algorithm
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Measure**.
    
    +---------------------------+--------------------------------------------------------------------------------------------+
    | Name (Value)              | Description                                                                                |
    +===========================+============================================================================================+
    | Measure (0)               | Spectrum measurement is performed on the acquired signal.                                  |
    +---------------------------+--------------------------------------------------------------------------------------------+
    | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the spectrum measurement. |
    +---------------------------+--------------------------------------------------------------------------------------------+
    """

    SPECTRUM_FFT_WINDOW = 1085449
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
    |                     | useful for time-frequency analysis.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_FFT_PADDING = 1085450
    r"""Specifies the factor by which the time-domain waveform is zero-padded before FFT. The FFT size is given by the
    following formula:
    
    waveform size * padding
    
    This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
    device.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    """

    SPECTRUM_FFT_OVERLAP_MODE = 1085476
    r"""Specifies the overlap mode when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
    attribute to **Sequential FFT**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Disabled**.
    
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)     | Description                                                                                                              |
    +==================+==========================================================================================================================+
    | Disabled (0)     | Disables the overlap between the chunks.                                                                                 |
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Automatic (1)    | Measurement sets the overlap based on the value you have set for the Spectrum FFT Window attribute. When you set the     |
    |                  | Spectrum FFT Window attribute to any value other than None, the number of overlapped samples between consecutive chunks  |
    |                  | is set to 50% of the value of the Spectrum Sequential FFT Size attribute. When you set the Spectrum FFT Window           |
    |                  | attribute to None, the chunks are not overlapped and the overlap is set to 0%.                                           |
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    | User Defined (2) | Measurement uses the overlap that you specify in the Spectrum FFT Overlap (%) attribute.                                 |
    +------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_FFT_OVERLAP = 1085477
    r"""Specifies the samples to overlap between the consecutive chunks as a percentage of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT** and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute to **User Defined**. This value is expressed
    as a percentage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    SPECTRUM_FFT_OVERLAP_TYPE = 1085478
    r"""Specifies the overlap type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
    attribute to **Sequential FFT**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | RMS (0)      | Linear averaging of the FFTs taken over different chunks of data is performed. RMS averaging reduces signal              |
    |              | fluctuations but not the noise floor.                                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one chunk FFT to the next.                         |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_AMPLITUDE_CORRECTION_TYPE = 1085463
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_MEASUREMENT_METHOD = 1085479
    r"""Specifies the method for performing the Spectrum measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Normal**.
    
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)       | Description                                                                                                              |
    +====================+==========================================================================================================================+
    | Normal (0)         | The Spectrum measurement acquires the spectrum using the same signal analyzer setting across frequency bands.            |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sequential FFT (2) | The Spectrum measurement acquires I/Q samples for a duration specified by the Spectrum Sweep Time attribute. These       |
    |                    | samples are divided into smaller chunks. If the attribute Spectrum RBW Auto is True, The size of each chunk is defined   |
    |                    | by the Spectrum Sequential FFT Size attribute. If the attribute Spectrum RBW Auto is False, the Spectrum Sequential FFT  |
    |                    | Size                                                                                                                     |
    |                    | is auto computed based on the configured Spectrum RBW. The overlap between the chunks is defined by the Spectrum FFT     |
    |                    | Overlap Mode attribute. FFT is computed on each of these chunks. The resultant FFTs are averaged as per the configured   |
    |                    | averaging type in the attribute Spectrum FFT Overlap Typeto get the spectrum.                                            |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_SEQUENTIAL_FFT_SIZE = 1085480
    r"""Specifies the FFT size when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**. If the
    attribute :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` is False, FFT Size is auto computed
    based on the configured :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH`
    
    The default value is 512.
    """

    SPECTRUM_ANALYSIS_INPUT = 1085475
    r"""Specifies whether to analyze just the real I or Q component of the acquired IQ data, or analyze the complex IQ data.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **IQ**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | IQ (0)       | Measurement analyzes the acquired I+jQ data, resulting generally in a spectrum that is not symmetric around 0 Hz.        |
    |              | Spectrum trace result contains both positive and negative frequencies. Since the RMS power of the complex envelope is    |
    |              | 3.01 dB higher than that of its equivalent real RF signal, the spectrum trace result of the acquired I+jQ data is        |
    |              | scaled by -3.01 dB.                                                                                                      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | I Only (1)   | Measurement ignores the Q data from the acquired I+jQ data and analyzes I+j0, resulting in a spectrum that is symmetric  |
    |              | around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of I+j0 data is scaled by +3.01 dB to    |
    |              | account for the power of the negative frequencies that are not returned in the spectrum trace.                           |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Q Only (2)   | Measurement ignores the I data from the acquired I+jQ data and analyzes Q+j0, resulting in a spectrum that is symmetric  |
    |              | around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of Q+j0 data is scaled by +3.01 dB to    |
    |              | account for the power of the negative frequencies that are not returned in the spectrum trace.                           |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPECTRUM_NUMBER_OF_ANALYSIS_THREADS = 1085442
    r"""Specifies the maximum number of threads used for parallelism for spectrum measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    SPECTRUM_RESULTS_PEAK_AMPLITUDE = 1085458
    r"""Returns the peak amplitude, of the averaged spectrum.
    
    When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0, the measurement returns
    the peak amplitude in the time domain power trace.
    
    The amplitude is reported in units specified by the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    SPECTRUM_RESULTS_PEAK_FREQUENCY = 1085459
    r"""Returns the frequency at the peak amplitude of the averaged spectrum. This value is expressed in Hz. This attribute is
    not valid if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    SPECTRUM_RESULTS_FREQUENCY_RESOLUTION = 1085460
    r"""Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz. This
    attribute is not valid if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    SPUR_MEASUREMENT_ENABLED = 1089536
    r"""Specifies whether to enable the spurious emission (Spur) measurement.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    
    The default value is FALSE.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_NUMBER_OF_RANGES = 1089540
    r"""Specifies the number of ranges.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_ENABLED = 1089541
    r"""Specifies whether to measure the spurious emissions (Spur) in the frequency range.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+------------------------------------------------------+
    | Name (Value) | Description                                          |
    +==============+======================================================+
    | False (0)    | Disables the acquisition of the frequency range.     |
    +--------------+------------------------------------------------------+
    | True (1)     | Enables measurement of Spurs in the frequency range. |
    +--------------+------------------------------------------------------+
    """

    SPUR_RANGE_START_FREQUENCY = 1089544
    r"""Specifies the start of the frequency range for the measurement. This value is expressed in Hz.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 500 MHz.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_STOP_FREQUENCY = 1089545
    r"""Specifies the stop of the frequency range for the measurement. This value is expressed in Hz.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1.5 GHz.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_RBW_FILTER_AUTO_BANDWIDTH = 1089555
    r"""Specifies whether the measurement computes the resolution bandwidth (RBW).
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+--------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                    |
    +==============+================================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the Spur Range RBW attribute. |
    +--------------+--------------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                              |
    +--------------+--------------------------------------------------------------------------------+
    """

    SPUR_RANGE_RBW_FILTER_BANDWIDTH = 1089556
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False.**
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 10 kHz.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_RBW_FILTER_TYPE = 1089557
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Gaussian**.
    
    **Supported devices**: PXIe-5665/5668
    
    +---------------+----------------------------------------------------+
    | Name (Value)  | Description                                        |
    +===============+====================================================+
    | FFT Based (0) | No RBW filtering is performed.                     |
    +---------------+----------------------------------------------------+
    | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
    +---------------+----------------------------------------------------+
    | Flat (2)      | An RBW filter with a flat response is applied.     |
    +---------------+----------------------------------------------------+
    """

    SPUR_RANGE_RBW_FILTER_BANDWIDTH_DEFINITION = 1089571
    r"""Specifies the bandwidth definition which you use to specify the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **3dB**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the Spur Range RBW Filter Type attribute   |
    |               | to FFT Based, RBW is the 3dB bandwidth of the window specified by the Spur FFT Window attribute.                         |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spur Range RBW Filter Type        |
    |               | attribute to FFT Based.                                                                                                  |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | ENBW (3)      | Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spur                                  |
    |               | RBW Filter Type attribute to FFT Based, RBW is the ENBW                                                                  |
    |               | bandwidth of the window specified by the Spur FFT Window attribute.                                                      |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_RANGE_VBW_FILTER_AUTO_BANDWIDTH = 1089575
    r"""Specifies whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Specify the video bandwidth in the                                                                                       |
    |              | Spur Range VBW                                                                                                           |
    |              | attribute. The Spur VBW to RBW Ratio attribute is disregarded in this mode.                                              |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
    |              | the Spur Range VBW to RBW Ratio attribute and the Spur Range RBW attribute. The value of the Spur Range VBW attribute    |
    |              | is disregarded in this mode.                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_RANGE_VBW_FILTER_BANDWIDTH = 1089576
    r"""Specifies the video bandwidth (VBW) in Hz when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 30000.
    """

    SPUR_RANGE_VBW_FILTER_VBW_TO_RBW_RATIO = 1089577
    r"""Specifies the VBW to RBW Ratio when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 3.
    """

    SPUR_RANGE_SWEEP_TIME_AUTO = 1089558
    r"""Specifies whether the measurement computes the sweep time.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+-----------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                   |
    +==============+===============================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the Spur Range Sweep Time attribute.  |
    +--------------+-----------------------------------------------------------------------------------------------+
    | True (1)     | The measurement calculates the sweep time based on the value of the Spur Range RBW attribute. |
    +--------------+-----------------------------------------------------------------------------------------------+
    """

    SPUR_RANGE_SWEEP_TIME_INTERVAL = 1089559
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SWEEP_TIME_AUTO`
    attribute to **False**. This value is expressed in seconds.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.001.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_DETECTOR_TYPE = 1089573
    r"""Specifies the type of detector to be used.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    Refer to `Spectral Measurements Concepts
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
    detector types.
    
    The default value is **None**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | The detector is disabled.                                                                                                |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
    |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
    |                     | alternate buckets.                                                                                                       |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_RANGE_DETECTOR_POINTS = 1089574
    r"""Specifies the number of range points after the detector is applied.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1001.
    """

    SPUR_RANGE_ABSOLUTE_LIMIT_MODE = 1089552
    r"""Specifies whether the absolute limit threshold is a flat line or a line with a slope.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Couple**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | The line specified by the Spur Range Abs Limit Start and Spur Range Abs Limit Stop attribute                             |
    |              | values as the two ends is considered as the threshold.                                                                   |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Couple (1)   | The two ends of the line are coupled to the value of the Spur Range Abs Limit Start attribute.                           |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_RANGE_ABSOLUTE_LIMIT_START = 1089553
    r"""Specifies the absolute power limit corresponding to the beginning of the frequency range. This value is expressed in
    dBm. This power limit is also set as the absolute power limit for the range when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -10.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_ABSOLUTE_LIMIT_STOP = 1089554
    r"""Specifies the absolute power limit corresponding to the end of the frequency range. This value is expressed in dBm. The
    measurement ignores this attribute when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -10.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_RELATIVE_ATTENUATION = 1089542
    r"""Specifies the attenuation relative to the external attenuation specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
    Spur Range Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
    wide in frequency.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_PEAK_THRESHOLD = 1089569
    r"""Specifies the threshold level above which the measurement detects spurs in the range that you specify using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attributes. This value is expressed in dBm.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -200.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_PEAK_EXCURSION = 1089570
    r"""Specifies the peak excursion value used to find the spurs in the spectrum. This value is expressed in dB. The signal
    should rise and fall by at least the peak excursion value, above the threshold, to be considered a spur.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RANGE_NUMBER_OF_SPURS_TO_REPORT = 1089543
    r"""Specifies the number of spurious emissions (Spur) that the measurement should report in the frequency range.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 10.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_AVERAGING_ENABLED = 1089547
    r"""Specifies whether to enable averaging for the spurious emission (Spur) measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The Spur measurement uses the Spur Averaging Count attribute as the number of acquisitions over which the Spur           |
    |              | measurement is averaged.                                                                                                 |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_AVERAGING_COUNT = 1089546
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_AVERAGING_TYPE = 1089549
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spurious
    emission (Spur) measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    SPUR_FFT_WINDOW = 1089551
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    **Supported devices**: PXIe-5665/5668
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful for    |
    |                     | time-frequency analysis.                                                                                                 |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_TRACE_RANGE_INDEX = 1089568
    r"""Specifies the index of the range used to store and retrieve spurious emission (Spur) traces. This attribute is not used
    if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.ALL_TRACES_ENABLED` to FALSE. When you set this attribute
    to -1, the measurement stores and retrieves traces for all enabled ranges.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_AMPLITUDE_CORRECTION_TYPE = 1089572
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SPUR_ALL_TRACES_ENABLED = 1089560
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the spurious emissions (Spur)
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_NUMBER_OF_ANALYSIS_THREADS = 1089539
    r"""Specifies the maximum number of threads used for parallelism for spurious emission (Spur) measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RESULTS_MEASUREMENT_STATUS = 1089561
    r"""Indicates the overall measurement status.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+--------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                            |
    +==============+========================================================================================================+
    | Fail (0)     | A detected spur in the range is greater than the value of the Spur Results Spur Abs Limits attribute.  |
    +--------------+--------------------------------------------------------------------------------------------------------+
    | Pass (1)     | All detected spurs in the range are lower than the value of the Spur Results Spur Abs Limit attribute. |
    +--------------+--------------------------------------------------------------------------------------------------------+
    """

    SPUR_RESULTS_RANGE_MEASUREMENT_STATUS = 1089566
    r"""Indicates the measurement status for the frequency range.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    **Supported devices**: PXIe-5665/5668
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | Fail (0)     | The amplitude of the detected spurs is greater than the value of the Spur Results Spur Abs Limit attribute. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Pass (1)     | The amplitude of the detected spurs is lower than the value of the Spur Results Spur Abs Limit attribute.   |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    SPUR_RESULTS_RANGE_NUMBER_OF_DETECTED_SPURS = 1089567
    r"""Returns the number of detected spurious emissions (Spur) in the specified frequency range.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RESULTS_RANGE_FREQUENCY = 1089562
    r"""Returns the frequency of the detected spurious emissions (Spur). This value is expressed in Hz.
    
    Use "range<*n*>/spur<*k*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RESULTS_RANGE_MARGIN = 1089565
    r"""Returns the difference between the amplitude and the absolute limit of the detected spurious emissions (Spur) at the
    Spur frequency.
    
    Use "range<*n*>/spur<*k*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RESULTS_RANGE_AMPLITUDE = 1089563
    r"""Returns the amplitude of the detected spurious emissions (Spur). This value is expressed in dBm.
    
    Use "range<*n*>/spur<*k*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    **Supported devices**: PXIe-5665/5668
    """

    SPUR_RESULTS_RANGE_ABSOLUTE_LIMIT = 1089564
    r"""Returns the threshold used to calculate the margin of the detected spurious emissions (Spur). This value is expressed
    in dBm. The measurement calculates the threshold using the absolute limit line specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute.
    
    Use "range<*n*>/spur<*k*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    
    **Supported devices**: PXIe-5665/5668
    """

    TXP_MEASUREMENT_ENABLED = 1093632
    r"""Specifies whether to enable the TXP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    TXP_MEASUREMENT_INTERVAL = 1093634
    r"""Specifies the acquisition time for the TXP measurement. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    TXP_RBW_FILTER_BANDWIDTH = 1093642
    r"""Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
    Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100 kHz.
    """

    TXP_RBW_FILTER_TYPE = 1093643
    r"""Specifies the shape of the digital resolution bandwidth (RBW) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                              |
    +==============+==========================================================================================================+
    | Gaussian (1) | The RBW filter has a Gaussian response.                                                                  |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | Flat (2)     | The RBW filter has a flat response.                                                                      |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | None (5)     | The measurement does not use any RBW filtering.                                                          |
    +--------------+----------------------------------------------------------------------------------------------------------+
    | RRC (6)      | The RRC filter with the roll-off specified by the TXP RBW RRC Alpha attribute is used as the RBW filter. |
    +--------------+----------------------------------------------------------------------------------------------------------+
    """

    TXP_RBW_FILTER_ALPHA = 1093641
    r"""Specifies the roll-off factor for the root-raised-cosine (RRC) filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.1.
    """

    TXP_VBW_FILTER_AUTO_BANDWIDTH = 1093655
    r"""Specifies whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Specify the video bandwidth in the TXP VBW                                                                               |
    |              | attribute. The TXP VBW to RBW Ratio attribute is disregarded in this mode.                                               |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
    |              | the TXP VBW to RBW Ratio attribute and the TXP RBW attribute. The value of the TXP VBW                                   |
    |              | attribute is disregarded in this mode.                                                                                   |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    TXP_VBW_FILTER_BANDWIDTH = 1093656
    r"""Specifies the video bandwidth when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 30000.
    """

    TXP_VBW_FILTER_VBW_TO_RBW_RATIO = 1093657
    r"""Specifies the VBW to RBW Ratio when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 3.
    """

    TXP_THRESHOLD_ENABLED = 1093644
    r"""Specifies whether to enable thresholding of the acquired samples to be used for the TXP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | All the acquired samples are considered for the TXP measurement.                                                         |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The samples above the threshold level specified in the TXP Threshold Level attribute are considered for the TXP          |
    |              | measurement.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    TXP_THRESHOLD_TYPE = 1093646
    r"""Specifies the reference for the power level used for thresholding.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Relative**.
    
    +--------------+----------------------------------------------------------------------+
    | Name (Value) | Description                                                          |
    +==============+======================================================================+
    | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
    +--------------+----------------------------------------------------------------------+
    | Absolute (1) | The threshold is the absolute power, in dBm.                         |
    +--------------+----------------------------------------------------------------------+
    """

    TXP_THRESHOLD_LEVEL = 1093645
    r"""Specifies either the relative or absolute threshold power level based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.
    
    The default value is -20.
    """

    TXP_AVERAGING_ENABLED = 1093638
    r"""Specifies whether to enable averaging for the TXP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The TXP measurement uses the TXP Averaging Count attribute as the number of acquisitions over which the TXP measurement  |
    |              | is averaged.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    TXP_AVERAGING_COUNT = 1093637
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    TXP_AVERAGING_TYPE = 1093640
    r"""Specifies the averaging type for the TXP measurement. The averaged power trace is used for the measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+--------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                      |
    +==============+==================================================================================================+
    | RMS (0)      | The power trace is linearly averaged.                                                            |
    +--------------+--------------------------------------------------------------------------------------------------+
    | Log (1)      | The power trace is averaged in a logarithmic scale.                                              |
    +--------------+--------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power trace is averaged.                                                  |
    +--------------+--------------------------------------------------------------------------------------------------+
    | Max (3)      | The maximum instantaneous power in the power trace is retained from one acquisition to the next. |
    +--------------+--------------------------------------------------------------------------------------------------+
    | Min (4)      | The minimum instantaneous power in the power trace is retained from one acquisition to the next. |
    +--------------+--------------------------------------------------------------------------------------------------+
    """

    TXP_ALL_TRACES_ENABLED = 1093648
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the TXP measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    TXP_NUMBER_OF_ANALYSIS_THREADS = 1093635
    r"""Specifies the maximum number of threads used for parallelism for TXP measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    TXP_RESULTS_AVERAGE_MEAN_POWER = 1093649
    r"""Returns the mean power of the signal. This value is expressed in dBm. Only the samples above the threshold are used by
    the measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to
    **True**. When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the
    mean power is measured using the power trace averaged over multiple acquisitions.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    TXP_RESULTS_PEAK_TO_AVERAGE_RATIO = 1093650
    r"""Returns the ratio of the peak power of the signal to the mean power. Only the samples above the threshold are used by
    the measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to
    **True**. When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the
    peak and mean powers are measured using the power trace averaged over multiple acquisitions.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    TXP_RESULTS_MAXIMUM_POWER = 1093651
    r"""Returns the maximum power of the averaged power trace. This value is expressed in dBm.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    TXP_RESULTS_MINIMUM_POWER = 1093652
    r"""Returns the minimum power of the averaged power trace. This value is expressed in dBm.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_MEASUREMENT_ENABLED = 1105920
    r"""Specifies whether to enable the AMPM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    AMPM_MEASUREMENT_SAMPLE_RATE_MODE = 1105931
    r"""Specifies whether the acquisition sample rate is based on the reference waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Reference Waveform**.
    
    +------------------------+---------------------------------------------------------------------------------------------+
    | Name (Value)           | Description                                                                                 |
    +========================+=============================================================================================+
    | User (0)               | The acquisition sample rate is defined by the value of the AMPM Meas Sample Rate attribute. |
    +------------------------+---------------------------------------------------------------------------------------------+
    | Reference Waveform (1) | The acquisition sample rate is set to match the sample rate of the reference waveform.      |
    +------------------------+---------------------------------------------------------------------------------------------+
    """

    AMPM_MEASUREMENT_SAMPLE_RATE = 1105932
    r"""Specifies the acquisition sample rate when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
    expressed in samples per second (S/s).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 120,000,000.
    """

    AMPM_MEASUREMENT_INTERVAL = 1105929
    r"""Specifies the duration of the reference waveform considered for the AMPM measurement. When the reference waveform
    contains an idle duration, the AMPM measurement neglects the idle samples in the reference waveform leading up to the
    start of the first active portion of the reference waveform. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100E-6.
    """

    AMPM_SIGNAL_TYPE = 1105930
    r"""Specifies whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
    time-align the sinusoidal reference waveform to the acquired signal, set the AMPM Signal Type attribute to **Tones**,
    which switches the AMPM measurement alignment algorithm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Modulated**.
    
    +---------------+--------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                    |
    +===============+================================================================================+
    | Modulated (0) | The reference waveform is a cellular or connectivity standard signal.          |
    +---------------+--------------------------------------------------------------------------------+
    | Tones (1)     | The reference waveform is a continuous signal comprising of one or more tones. |
    +---------------+--------------------------------------------------------------------------------+
    """

    AMPM_SYNCHRONIZATION_METHOD = 1105962
    r"""Specifies the method used for synchronization of acquired waveform with reference waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Direct**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | Direct (1)          | Synchronizes the acquired and reference waveforms assuming that sample rate is sufficient to prevent aliasing in         |
    |                     | intermediate operations. This method is recommended when the measurement sampling rate is high.                          |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Alias Protected (2) | Synchronizes the acquired and                                                                                            |
    |                     | reference waveforms while ascertaining that intermediate operations are not impacted by aliasing. This method is         |
    |                     | recommended for non-contiguous carriers separated by a large gap, and/or when the measurement sampling rate is low.      |
    |                     | Refer to AMPM concept help for more information.                                                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_AUTO_CARRIER_DETECTION_ENABLED = 1105963
    r"""Specifies if auto detection of carrier offset and carrier bandwidth is enabled.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------------------+
    | Name (Value) | Description                                                      |
    +==============+==================================================================+
    | False (0)    | Disables auto detection of carrier offset and carrier bandwidth. |
    +--------------+------------------------------------------------------------------+
    | True (1)     | Enables auto detection of carrier offset and carrier bandwidth.  |
    +--------------+------------------------------------------------------------------+
    """

    AMPM_NUMBER_OF_CARRIERS = 1105964
    r"""Specifies the number of carriers in the reference waveform when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    AMPM_CARRIER_OFFSET = 1105965
    r"""Specifies the carrier offset when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
    expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    AMPM_CARRIER_BANDWIDTH = 1105966
    r"""Specifies the carrier bandwidth when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
    expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 20 MHz.
    """

    AMPM_DUT_AVERAGE_INPUT_POWER = 1105936
    r"""Specifies the average power of the signal at the input port of the device under test. This value is expressed in dBm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20 dBm.
    """

    AMPM_AM_TO_AM_CURVE_FIT_ORDER = 1105922
    r"""Specifies the degree of the polynomial used to approximate the AM-to-AM characteristic of the device under test (DUT).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 7.
    """

    AMPM_AM_TO_AM_CURVE_FIT_TYPE = 1105923
    r"""Specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Least Absolute Residual**.
    
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                | Description                                                                                                             |
    +=============================+=========================================================================================================================+
    | Least Square (0)            | The measurement minimizes the energy of the polynomial approximation error.                                             |
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Least Absolute Residual (1) | The measurement minimizes the magnitude of the polynomial approximation error.                                          |
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Bisquare (2)                | The measurement excludes the effect of data outliers while minimizing the energy of the polynomial approximation error. |
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_AM_TO_PM_CURVE_FIT_ORDER = 1105924
    r"""Specifies the degree of the polynomial used to approximate the AM-to-PM characteristic of the device under test.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 7.
    """

    AMPM_AM_TO_PM_CURVE_FIT_TYPE = 1105925
    r"""Specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Least Absolute Residual**.
    
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                | Description                                                                                                             |
    +=============================+=========================================================================================================================+
    | Least Square (0)            | The measurement minimizes the energy of the polynomial approximation error.                                             |
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Least Absolute Residual (1) | The measurement minimizes the magnitude of the polynomial approximation error.                                          |
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Bisquare (2)                | The measurement excludes the effect of data outliers while minimizing the energy of the polynomial approximation error. |
    +-----------------------------+-------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_THRESHOLD_ENABLED = 1105933
    r"""Specifies whether to enable thresholding of the acquired samples used for the AMPM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | All samples are considered for the AMPM measurement.                                                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Samples above the threshold level specified in the AMPM Threshold Level attribute are considered for the AMPM            |
    |              | measurement.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_THRESHOLD_TYPE = 1105934
    r"""Specifies the reference for the power level used for thresholding.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Relative**.
    
    +--------------+----------------------------------------------------------------------+
    | Name (Value) | Description                                                          |
    +==============+======================================================================+
    | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
    +--------------+----------------------------------------------------------------------+
    | Absolute (1) | The threshold is the absolute power, in dBm.                         |
    +--------------+----------------------------------------------------------------------+
    """

    AMPM_THRESHOLD_LEVEL = 1105935
    r"""Specifies either the relative or absolute threshold power level, based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20 dB.
    """

    AMPM_THRESHOLD_DEFINITION = 1105980
    r"""Specifies the definition to use for thresholding acquired and reference waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Reference Power Type**.
    
    +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)             | Description                                                                                                              |
    +==========================+==========================================================================================================================+
    | Input AND Output (0)     | Corresponding acquired and reference waveform samples are used for AMPM measurement when both samples are greater or     |
    |                          | equal to the threshold level.                                                                                            |
    +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Reference Power Type (1) | Corresponding acquired and reference waveform samples are used for AMPM measurement when reference waveform sample is    |
    |                          | greater than or equal to the threshold level and AMPM Ref Pwr Type attribute is set to Input. Corresponding acquired     |
    |                          | and reference waveform samples are used for AMPM measurement when acquired waveform sample is greater than or equal to   |
    |                          | the threshold level and AMPM Ref Pwr Type attribute is set to Output.                                                    |
    +--------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_FREQUENCY_OFFSET_CORRECTION_ENABLED = 1105953
    r"""Enables frequency offset correction for the measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                  |
    +==============+==============================================================================================================+
    | False (0)    | The measurement does not perform frequency offset correction.                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement computes and corrects any frequency offset between the reference and the acquired waveforms. |
    +--------------+--------------------------------------------------------------------------------------------------------------+
    """

    AMPM_IQ_ORIGIN_OFFSET_CORRECTION_ENABLED = 1105961
    r"""Enables IQ origin offset correction for the measurement.
    
    When you set this attribute is set to **True**, the measurement computes and corrects any origin offset between
    the reference and the acquired waveforms. When you set this attribute to **False**, origin offset correction is not
    performed.
    
    The default value is **True**.
    
    +--------------+---------------------------------------+
    | Name (Value) | Description                           |
    +==============+=======================================+
    | False (0)    | Disables IQ origin offset correction. |
    +--------------+---------------------------------------+
    | True (1)     | Enables IQ origin offset correction.  |
    +--------------+---------------------------------------+
    """

    AMPM_AM_TO_AM_ENABLED = 1105969
    r"""Specifies whether to enable the results that rely on the AM to AM characteristics.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables the computation of following scalar results and traces. Empty array is returned if the disabled result is an    |
    |              | array. NaN is returned otherwise.                                                                                        |
    |              | The following scalar results are disabled:                                                                               |
    |              | AMPM Results Mean Linear Gain                                                                                            |
    |              | AMPM Results 1 dB Compression Point                                                                                      |
    |              | AMPM Results Input Compression Point                                                                                     |
    |              | AMPM Results Output Compression Point                                                                                    |
    |              | AMPM Results Gain Error Range                                                                                            |
    |              | AMPM Results AM to AM Curve Fit Residual                                                                                 |
    |              | AMPM Results AM to AM Curve Fit Coeff                                                                                    |
    |              | The following traces are disabled:                                                                                       |
    |              | Measured AM to AM                                                                                                        |
    |              | Curve Fit AM to AM                                                                                                       |
    |              | Relative Power Trace                                                                                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables the computation of AM to AM results and traces.                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_AM_TO_PM_ENABLED = 1105970
    r"""Specifies whether to enable the results that rely on AM to PM characteristics.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables the computation of following scalar results and traces. Empty array is returned if the disabled result is an    |
    |              | array. NaN is returned otherwise.                                                                                        |
    |              | The following scalar results are disabled:                                                                               |
    |              | AMPM Results Mean Phase Error                                                                                            |
    |              | AMPM Results Phase Error Range                                                                                           |
    |              | AMPM Results AM to PM Curve Fit Residual                                                                                 |
    |              | AMPM Results AM to PM Curve Fit Coefficients                                                                             |
    |              | The following traces are disabled:                                                                                       |
    |              | Measured AM to PM                                                                                                        |
    |              | Curve Fit AM to PM                                                                                                       |
    |              | Relative Phase Trace                                                                                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables the computation of AM to PM results and traces.                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_EVM_ENABLED = 1105971
    r"""Specifies whether to enable the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_RMS_EVM` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------------+
    | Name (Value) | Description                                                |
    +==============+============================================================+
    | False (0)    | Disables EVM computation. NaN is returned as Mean RMS EVM. |
    +--------------+------------------------------------------------------------+
    | True (1)     | Enables EVM computation.                                   |
    +--------------+------------------------------------------------------------+
    """

    AMPM_EQUALIZER_MODE = 1105967
    r"""Specifies whether the measurement equalizes the channel.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Off**.
    
    +--------------+-------------------------------------------------------------------------+
    | Name (Value) | Description                                                             |
    +==============+=========================================================================+
    | Off (0)      | Equalization is not performed.                                          |
    +--------------+-------------------------------------------------------------------------+
    | Train (1)    | The equalizer is turned on to compensate for the effect of the channel. |
    +--------------+-------------------------------------------------------------------------+
    """

    AMPM_EQUALIZER_FILTER_LENGTH = 1105968
    r"""Specifies the length of the equalizer filter. The measurement maintains the filter length as an odd number by
    incrementing any even numbered value by one.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 21.
    """

    AMPM_AVERAGING_ENABLED = 1105926
    r"""Specifies whether to enable averaging for the AMPM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The AMPM measurement uses the AMPM Averaging Count attribute as the number of acquisitions over which the signal for     |
    |              | the AMPM measurement is averaged.                                                                                        |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_AVERAGING_COUNT = 1105927
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    AMPM_COMPRESSION_POINT_ENABLED = 1105956
    r"""Enables computation of compression points corresponding to the respective compression levels specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+---------------------------------------------+
    | Name (Value) | Description                                 |
    +==============+=============================================+
    | False (0)    | Disables computation of compression points. |
    +--------------+---------------------------------------------+
    | True (1)     | Enables computation of compression points.  |
    +--------------+---------------------------------------------+
    """

    AMPM_COMPRESSION_POINT_LEVEL = 1105957
    r"""Specifies the compression levels for which the compression points are computed when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    AMPM_COMPRESSION_POINT_GAIN_REFERENCE = 1105972
    r"""Specifies the gain reference for compression point calculation.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Auto**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | Auto (0)            | Measurement computes the gain reference to be used for compression point calculation. The computed gain reference is     |
    |                     | also returned as AMPM Results Mean Linear Gain result.                                                                   |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Reference Power (1) | Measurement uses the gain corresponding to the reference power that you specify for the AMPM Compression Point Gain Ref  |
    |                     | Pwr attribute as gain reference. The reference power can be configured as either input or output power based on the      |
    |                     | value of the AMPM Ref Pwr Type attribute.                                                                                |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Max Gain (2)        | Measurement uses the maximum gain as gain reference for compression point calculation.                                   |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | User Defined (3)    | Measurement uses the gain that you specify for the AMPM Compression Point User Gain attribute as gain reference for      |
    |                     | compression point calculation.                                                                                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_COMPRESSION_POINT_GAIN_REFERENCE_POWER = 1105973
    r"""Specifies the reference power corresponding to the gain reference to be used for compression point calculation when you
    set the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **Reference
    Power**. The reference power can be configured as either input or output power based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute. This value is expressed in dBm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20.
    """

    AMPM_COMPRESSION_POINT_USER_GAIN = 1105974
    r"""Specifies the gain to be used as the gain reference for compression point calculation when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **User Defined**. This
    value is expressed in dB.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 20.
    """

    AMPM_MAXIMUM_TIMING_ERROR = 1105954
    r"""Specifies the maximum time alignment error expected between the acquired and the reference waveforms. This value is
    expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.00002.
    """

    AMPM_REFERENCE_POWER_TYPE = 1105955
    r"""Specifies the reference power used for AM to AM and AM to PM traces.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Input**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                             |
    +==============+=========================================================================================================================+
    | Input (0)    | The instantaneous powers at the input port of device under test (DUT) forms the x-axis of AM to AM and AM to PM traces. |
    +--------------+-------------------------------------------------------------------------------------------------------------------------+
    | Output (1)   | The instantaneous powers at the output port of DUT forms the x-axis of AM to AM and AM to PM traces.                    |
    +--------------+-------------------------------------------------------------------------------------------------------------------------+
    """

    AMPM_ALL_TRACES_ENABLED = 1105937
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the AMPM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    AMPM_NUMBER_OF_ANALYSIS_THREADS = 1105938
    r"""Specifies the maximum number of threads used for parallelism for the AMPM measurement.
    
    The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
    may not be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    AMPM_RESULTS_MEAN_LINEAR_GAIN = 1105942
    r"""Returns the average linear gain of the device under test, computed by rejecting signal samples containing gain
    compression. This value is expressed in dB.
    """

    AMPM_RESULTS_1_DB_COMPRESSION_POINT = 1105949
    r"""Returns the theoretical output power at which the gain of the device under test drops by 1 dB from a gain reference
    computed based on the value that you specify for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute. This value is expressed in
    dBm. This attribute returns NaN when the AM-to-AM characteristics of the device under test are flat.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_INPUT_COMPRESSION_POINT = 1105958
    r"""Returns the theoretical input power at which the gain of the device drops by a compression level, specified through the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute, from a gain reference computed based
    on the value that you specify for the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE`
    attribute. This value is expressed in dBm.
    
    You do not need to use a selector string to read this attribute for the default signal and result instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    AMPM_RESULTS_OUTPUT_COMPRESSION_POINT = 1105959
    r"""Returns the theoretical output power at which the gain of the device drops by a compression level, specified through
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute, from a gain reference computed
    based on the value that you specify for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute. This value is expressed in
    dBm.
    
    You do not need to use a selector string to read this attribute for the default signal and result instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    AMPM_RESULTS_COMPRESSION_POINT_GAIN_REFERENCE = 1105975
    r"""Returns the gain reference used for compression point calculation. This value is expressed in dB.
    
    You do not need to use a selector string to read this attribute for the default signal and result instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    AMPM_RESULTS_PEAK_REFERENCE_POWER = 1105976
    r"""Returns the peak reference power. This value is expressed in dBm.
    
    You do not need to use a selector string to read this attribute for the default signal and result instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    AMPM_RESULTS_PEAK_REFERENCE_POWER_GAIN = 1105977
    r"""Returns the gain at the peak reference power. This value is expressed in dB.
    
    You do not need to use a selector string to read this attribute for the default signal and result instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    AMPM_RESULTS_MEAN_RMS_EVM = 1105944
    r"""Returns the ratio, as a percentage, of l\ :sup:`2`\ norm of difference between the normalized reference and acquired
    waveforms, to the l\ :sup:`2`\ norm of the normalized reference waveform.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_GAIN_ERROR_RANGE = 1105947
    r"""Returns the peak-to-peak deviation of the device under test gain. This value is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_PHASE_ERROR_RANGE = 1105948
    r"""Returns the peak-to-peak deviation of the phase distortion of the acquired signal relative to the reference waveform
    caused by the device under test. This value is expressed in degrees.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_MEAN_PHASE_ERROR = 1105943
    r"""Returns the mean phase error of the acquired signal relative to the reference waveform caused by the device under test.
    This value is expressed in degrees.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_AM_TO_AM_CURVE_FIT_RESIDUAL = 1105945
    r"""Returns the approximation error of the polynomial approximation of the measured device under test AM-to-AM
    characteristic. This value is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_AM_TO_PM_CURVE_FIT_RESIDUAL = 1105946
    r"""Returns the approximation error of the polynomial approximation of the measured AM-to-PM characteristic of the device
    under test. This value is expressed in degrees.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_AM_TO_AM_CURVE_FIT_COEFFICIENTS = 1105940
    r"""Returns the coefficients of the polynomial that approximates the measured AM-to-AM characteristic of the device under
    test.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    AMPM_RESULTS_AM_TO_PM_CURVE_FIT_COEFFICIENTS = 1105941
    r"""Returns the coefficients of the polynomial that approximates the measured AM-to-PM characteristic of the device under
    test.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    DPD_MEASUREMENT_ENABLED = 1110016
    r"""Specifies whether to enable DPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    DPD_MEASUREMENT_SAMPLE_RATE_MODE = 1110018
    r"""Specifies the acquisition sample rate configuration mode.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Reference Waveform**.
    
    +------------------------+--------------------------------------------------------------------------------------------+
    | Name (Value)           | Description                                                                                |
    +========================+============================================================================================+
    | User (0)               | The acquisition sample rate is defined by the value of the DPD Meas Sample Rate attribute. |
    +------------------------+--------------------------------------------------------------------------------------------+
    | Reference Waveform (1) | The acquisition sample rate is set to match the sample rate of the reference waveform.     |
    +------------------------+--------------------------------------------------------------------------------------------+
    """

    DPD_MEASUREMENT_SAMPLE_RATE = 1110019
    r"""Specifies the acquisition sample rate when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
    expressed in Samples per second (S/s).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 120 MHz.
    """

    DPD_MEASUREMENT_INTERVAL = 1110020
    r"""Specifies the duration of the reference waveform considered for the DPD measurement. When the reference waveform
    contains an idle duration, the DPD measurement neglects the idle samples in the reference waveform leading up to the
    start of the first active portion of the reference waveform. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100E-6.
    """

    DPD_SIGNAL_TYPE = 1110021
    r"""Specifies whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
    time-align the sinusoidal reference waveform to the acquired signal, set the DPD Signal Type attribute to **Tones**,
    which switches the DPD measurement alignment algorithm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Modulated**.
    
    +---------------+-----------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                 |
    +===============+=============================================================================+
    | Modulated (0) | The reference waveform is a cellular or connectivity standard signal.       |
    +---------------+-----------------------------------------------------------------------------+
    | Tones (1)     | The reference waveform is a continuous signal comprising one or more tones. |
    +---------------+-----------------------------------------------------------------------------+
    """

    DPD_SYNCHRONIZATION_METHOD = 1110090
    r"""Specifies the method used for synchronization of the acquired waveform with the reference waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Direct**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | Direct (1)          | Synchronizes the acquired and reference waveforms assuming that sample rate is sufficient to prevent aliasing in         |
    |                     | intermediate operations. This method is recommended when measurement sampling rate is high.                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Alias Protected (2) | Synchronizes the acquired and                                                                                            |
    |                     | reference waveforms while ascertaining that intermediate operations are not impacted by aliasing. This method is         |
    |                     | recommended for non-contiguous carriers separated by a large gap, and/or when measurement sampling rate is low. Refer    |
    |                     | to DPD concept help for more information.                                                                                |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_AUTO_CARRIER_DETECTION_ENABLED = 1110091
    r"""Specifies if auto detection of carrier offset and carrier bandwidth is enabled.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------------------+
    | Name (Value) | Description                                                      |
    +==============+==================================================================+
    | False (0)    | Disables auto detection of carrier offset and carrier bandwidth. |
    +--------------+------------------------------------------------------------------+
    | True (1)     | Enables auto detection of carrier offset and carrier bandwidth.  |
    +--------------+------------------------------------------------------------------+
    """

    DPD_NUMBER_OF_CARRIERS = 1110092
    r"""Specifies the number of carriers in the reference waveform when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    DPD_CARRIER_OFFSET = 1110093
    r"""Specifies the carrier offset when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
    expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    DPD_CARRIER_BANDWIDTH = 1110094
    r"""Specifies the carrier bandwidth when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
    expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 20 MHz.
    """

    DPD_DUT_AVERAGE_INPUT_POWER = 1110023
    r"""Specifies the average power of the signal at the device under test input port. This value is expressed in dBm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20 dBm.
    """

    DPD_MODEL = 1110024
    r"""Specifies the DPD model used by the DPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Lookup Table**.
    
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                      | Description                                                                                                              |
    +===================================+==========================================================================================================================+
    | Lookup Table (0)                  | This model computes the complex gain coefficients applied when performing digital predistortion to linearize systems     |
    |                                   | with negligible memory effects.                                                                                          |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Memory Polynomial (1)             | This model computes the memory polynomial predistortion coefficients used to linearize systems with moderate memory      |
    |                                   | effects.                                                                                                                 |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Generalized Memory Polynomial (2) | This model computes the generalized memory polynomial predistortion coefficients used to linearize systems with          |
    |                                   | significant memory effects.                                                                                              |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Decomposed Vector Rotation (3)    | This model computes the Decomposed Vector Rotation model predistortion coefficients used to linearize wideband systems   |
    |                                   | with significant memory effects.                                                                                         |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_TARGET_GAIN_TYPE = 1110071
    r"""Specifies the gain expected from the DUT after applying DPD on the input waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Average Gain**.
    
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)              | Description                                                                                                              |
    +===========================+==========================================================================================================================+
    | Average Gain (0)          | The DPD polynomial or lookup table is computed by assuming that the linearized gain expected from the DUT after          |
    |                           | applying DPD on the input waveform is equal to the average power gain provided by the DUT without DPD.                   |
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Linear Region Gain (1)    | The DPD polynomial or lookup table is computed by assuming that the linearized gain expected from the DUT after          |
    |                           | applying DPD on the input waveform is equal to the gain provided by the DUT, without DPD, to the parts of the reference  |
    |                           | waveform that do not drive the DUT into non-linear gain-expansion or compression regions of its input-output             |
    |                           | characteristics.                                                                                                         |
    |                           | The measurement computes the linear region gain as the average gain experienced by the parts of the reference waveform   |
    |                           | that are below a threshold which is computed as shown in the following equation:                                         |
    |                           | Linear region threshold (dBm) = Max {-25, Min {reference waveform power} + 6, DUT Average Input Power -15}               |
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak Input Power Gain (2) | The DPD polynomial or lookup table is computed by assuming that the linearized gain expected from the DUT after          |
    |                           | applying DPD on the input waveform is equal to the average power gain provided by the DUT, without DPD, to all the       |
    |                           | samples of the reference waveform for which the magnitude is greater than the peak power in the reference waveform       |
    |                           | (dBm) - 0.5dB.                                                                                                           |
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_TYPE = 1110072
    r"""Specifies the type of the DPD lookup table (LUT).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Log**.
    
    +--------------+-------------------------------------------------+
    | Name (Value) | Description                                     |
    +==============+=================================================+
    | Log (0)      | Input powers in the LUT are specified in dBm.   |
    +--------------+-------------------------------------------------+
    | Linear (1)   | Input powers in the LUT are specified in watts. |
    +--------------+-------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_AM_TO_AM_CURVE_FIT_ORDER = 1110025
    r"""Specifies the degree of the polynomial used to approximate the device under test AM-to-AM characteristic  when you set
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 7.
    """

    DPD_LOOKUP_TABLE_AM_TO_AM_CURVE_FIT_TYPE = 1110026
    r"""Specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Least Absolute Residual**.
    
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    | Name (Value)                | Description                                                                                             |
    +=============================+=========================================================================================================+
    | Least Square (0)            | Minimizes the energy of the polynomial approximation error.                                             |
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    | Least Absolute Residual (1) | Minimizes the magnitude of the polynomial approximation error.                                          |
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    | Bisquare (2)                | Excludes the effect of data outliers while minimizing the energy of the polynomial approximation error. |
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_AM_TO_PM_CURVE_FIT_ORDER = 1110027
    r"""Specifies the degree of the polynomial used to approximate the device under test AM-to-PM characteristic when you set
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 7.
    """

    DPD_LOOKUP_TABLE_AM_TO_PM_CURVE_FIT_TYPE = 1110028
    r"""Specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Least Absolute Residual**.
    
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    | Name (Value)                | Description                                                                                             |
    +=============================+=========================================================================================================+
    | Least Square (0)            | Minimizes the energy of the polynomial approximation error.                                             |
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    | Least Absolute Residual (1) | Minimizes the magnitude of the polynomial approximation error.                                          |
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    | Bisquare (2)                | Excludes the effect of data outliers while minimizing the energy of the polynomial approximation error. |
    +-----------------------------+---------------------------------------------------------------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_THRESHOLD_ENABLED = 1110029
    r"""Specifies whether to enable thresholding of the acquired samples to be used for the DPD measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | All samples are considered for the DPD measurement.                                                                      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Only samples above the threshold level which you specify in the DPD LUT Threshold Level attribute are considered for     |
    |              | the DPD measurement.                                                                                                     |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_THRESHOLD_TYPE = 1110030
    r"""Specifies the reference for the power level used for thresholding.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Relative**.
    
    +--------------+----------------------------------------------------------------------+
    | Name (Value) | Description                                                          |
    +==============+======================================================================+
    | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
    +--------------+----------------------------------------------------------------------+
    | Absolute (1) | The threshold is the absolute power, in dBm.                         |
    +--------------+----------------------------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_THRESHOLD_LEVEL = 1110031
    r"""Specifies either the relative or absolute threshold power level based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOOKUP_TABLE_THRESHOLD_TYPE` attribute. This value is expressed in dB or
    dBm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20.
    """

    DPD_LOOKUP_TABLE_THRESHOLD_DEFINITION = 1110125
    r"""Specifies the definition to use for thresholding acquired and reference waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Input**.
    
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)         | Description                                                                                                              |
    +======================+==========================================================================================================================+
    | Input AND Output (0) | Corresponding acquired and reference waveform samples are used for AMPM measurement when both samples are greater or     |
    |                      | equal to the threshold level.                                                                                            |
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Input (1)            | Corresponding acquired and reference waveform samples are used for AMPM measurement when reference waveform sample is    |
    |                      | greater than or equal to the threshold level.                                                                            |
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_LOOKUP_TABLE_STEP_SIZE = 1110032
    r"""Specifies the step size of the input power levels in the predistortion lookup table when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**. This value is expressed in dB.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.1 dB.
    """

    DPD_MEMORY_POLYNOMIAL_ORDER = 1110033
    r"""Specifies the order of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
    attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This order value corresponds to K\ :sub:`a`\
    in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 3.
    """

    DPD_MEMORY_POLYNOMIAL_MEMORY_DEPTH = 1110034
    r"""Specifies the memory depth of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
    attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This depth value corresponds to Q\ :sub:`a`\
    in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_ORDER_TYPE = 1110095
    r"""Configures the type of terms of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
    Polynomial**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **All Orders**.
    
    +----------------------+----------------------------------------------------------------------------------------------------------------+
    | Name (Value)         | Description                                                                                                    |
    +======================+================================================================================================================+
    | All Orders (0)       | The memory polynomial will compute all the terms for the given order.                                          |
    +----------------------+----------------------------------------------------------------------------------------------------------------+
    | Odd Orders Only (1)  | The memory polynomial will compute the non-zero coefficients only for the odd terms.                           |
    +----------------------+----------------------------------------------------------------------------------------------------------------+
    | Even Orders Only (2) | The memory polynomial will compute the non-zero coefficents only for the first linear term and all even terms. |
    +----------------------+----------------------------------------------------------------------------------------------------------------+
    """

    DPD_MEMORY_POLYNOMIAL_LEAD_ORDER = 1110035
    r"""Specifies the lead order cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
    corresponds to *K\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_LAG_ORDER = 1110036
    r"""Specifies the lag order cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
    corresponds to *K\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_LEAD_MEMORY_DEPTH = 1110037
    r"""Specifies the lead memory depth cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
    corresponds to *Q\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    generalized memory polynomial.  The value of the DPD Mem Poly Lead Mem Depth attribute must be greater than or equal to
    the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_LAG_MEMORY_DEPTH = 1110038
    r"""Specifies the lag memory depth cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
    corresponds to *Q\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_MAXIMUM_LEAD = 1110039
    r"""Specifies the maximum lead stagger cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
    corresponds to *M\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_MAXIMUM_LAG = 1110040
    r"""Specifies the maximum lag stagger cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
    corresponds to *M\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_MEMORY_POLYNOMIAL_LEAD_ORDER_TYPE = 1110096
    r"""Configures the type of terms of the lead order DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **All Orders**.
    
    +----------------------+--------------------------------------------------------------------------------------+
    | Name (Value)         | Description                                                                          |
    +======================+======================================================================================+
    | All Orders (0)       | The memory polynomial will compute all the terms for the given order.                |
    +----------------------+--------------------------------------------------------------------------------------+
    | Odd Orders Only (1)  | The memory polynomial will compute the non-zero coefficients only for the odd terms. |
    +----------------------+--------------------------------------------------------------------------------------+
    | Even Orders Only (2) | The memory polynomial will compute the non-zero coefficents only for the even terms. |
    +----------------------+--------------------------------------------------------------------------------------+
    """

    DPD_MEMORY_POLYNOMIAL_LAG_ORDER_TYPE = 1110097
    r"""Configures the type of terms of the lag order DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **All Orders**.
    
    +----------------------+--------------------------------------------------------------------------------------+
    | Name (Value)         | Description                                                                          |
    +======================+======================================================================================+
    | All Orders (0)       | The memory polynomial will compute all the terms for the given order.                |
    +----------------------+--------------------------------------------------------------------------------------+
    | Odd Orders Only (1)  | The memory polynomial will compute the non-zero coefficients only for the odd terms. |
    +----------------------+--------------------------------------------------------------------------------------+
    | Even Orders Only (2) | The memory polynomial will compute the non-zero coefficents only for the even terms. |
    +----------------------+--------------------------------------------------------------------------------------+
    """

    DPD_DVR_NUMBER_OF_SEGMENTS = 1110119
    r"""Specifies the number of segments of the Decomposed Vector Rotation model when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
    corresponds to *K* in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the Decomposed Vector
    Rotation model.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 4. This value must be greater than or equal to 1.
    """

    DPD_DVR_LINEAR_MEMORY_DEPTH = 1110120
    r"""Specifies the linear memory depth of the Decomposed Vector Rotation model when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
    corresponds to *M\ :sub:`l*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the decomposed
    vector rotation model.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 21. This value must be greater than or equal to 0.
    """

    DPD_DVR_NONLINEAR_MEMORY_DEPTH = 1110121
    r"""Specifies the nonlinear memory depth of the Decomposed Vector Rotation model when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
    corresponds to *M\ :sub:`nl*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    decomposed vector rotation model.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 2. This value must be greater than or equal to 1.
    """

    DPD_DVR_DDR_ENABLED = 1110122
    r"""Specifies whether to enable the Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector
    Rotation Model when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector
    Rotation**. For more details, refer to the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
    decomposed vector rotation model.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                      |
    +==============+==================================================================================================================+
    | False (0)    | The Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector Rotation model are disabled. |
    +--------------+------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector Rotation model are enabled.  |
    +--------------+------------------------------------------------------------------------------------------------------------------+
    """

    DPD_MEASUREMENT_MODE = 1110123
    r"""Specifies if the training waveform required for the extraction of the DPD model coefficients is acquired from the
    hardware or is configured by the user.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Acquire and Extract**.
    
    +-------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)            | Description                                                                                                              |
    +=========================+==========================================================================================================================+
    | Acquire and Extract (0) | The measurement acquires the training waveform required for the extraction of the DPD model coefficients from the        |
    |                         | hardware and then computes the model coefficients.                                                                       |
    +-------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Extract Only (1)        | The measurement uses the user configured training waveform required for the extraction of the DPD model coefficients.    |
    +-------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_ITERATIVE_DPD_ENABLED = 1110042
    r"""Specifies whether to enable iterative computation of the DPD Results DPD Polynomial using `DPD
    <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+----------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                    |
    +==============+================================================================================================================+
    | False (0)    | RFmx computes the DPD Results DPD Polynomial without considering the value of the DPD Previous DPD Polynomial. |
    +--------------+----------------------------------------------------------------------------------------------------------------+
    | True (1)     | RFmx computes the DPD Results DPD Polynomial based on the value of the DPD Previous DPD Polynomial.            |
    +--------------+----------------------------------------------------------------------------------------------------------------+
    """

    DPD_FREQUENCY_OFFSET_CORRECTION_ENABLED = 1110073
    r"""Specifies whether to enable frequency offset correction for the DPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                  |
    +==============+==============================================================================================================+
    | False (0)    | The measurement computes and corrects any frequency offset between the reference and the acquired waveforms. |
    +--------------+--------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement does not perform frequency offset correction.                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------+
    """

    DPD_IQ_ORIGIN_OFFSET_CORRECTION_ENABLED = 1110117
    r"""Enables the IQ origin offset correction for the measurement.
    
    When you set this attribute to **True**, the measurement computes and corrects any origin offset between the
    reference and the acquired waveforms. When you set this attribute to **False**, origin offset correction is not
    performed.
    
    The default value is **True**.
    
    +--------------+---------------------------------------+
    | Name (Value) | Description                           |
    +==============+=======================================+
    | False (0)    | Disables IQ origin offset correction. |
    +--------------+---------------------------------------+
    | True (1)     | Enables IQ origin offset correction.  |
    +--------------+---------------------------------------+
    """

    DPD_AVERAGING_ENABLED = 1110044
    r"""Specifies whether to enable averaging for the DPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The DPD measurement uses the DPD Averaging Count attribute as the number of acquisitions over which the signal for the   |
    |              | DPD measurement is averaged.                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_AVERAGING_COUNT = 1110045
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    DPD_MAXIMUM_TIMING_ERROR = 1110074
    r"""Specifies the maximum time alignment error expected between the acquired and the reference waveforms. This value is
    expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.00002.
    """

    DPD_NMSE_ENABLED = 1110075
    r"""Specifies whether to enable the normalized mean-squared error (NMSE) computation.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+-----------------------------------------------------+
    | Name (Value) | Description                                         |
    +==============+=====================================================+
    | False (0)    | Disables NMSE computation. NaN is returned as NMSE. |
    +--------------+-----------------------------------------------------+
    | True (1)     | Enables NMSE computation.                           |
    +--------------+-----------------------------------------------------+
    """

    DPD_PRE_DPD_CFR_ENABLED = 1110076
    r"""Specifies whether to enable the crest factor reduction (CFR) when applying pre-DPD signal conditioning.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables the CFR. The RFmxSpecAn DPD Apply Pre-DPD Signal Conditioning method returns an error when the CFR is           |
    |              | disabled.                                                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables the CFR.                                                                                                         |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_PRE_DPD_CFR_METHOD = 1110078
    r"""Specifies the method used to perform crest factor reduction (CFR) when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
    information about CFR methods.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Clipping**.
    
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)       | Description                                                                                                              |
    +====================+==========================================================================================================================+
    | Clipping (0)       | Hard clips the signal such that the target PAPR is achieved.                                                             |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak Windowing (1) | Scales the peaks in the signal using weighted window function to get smooth peaks and achieve the target PAPR.           |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sigmoid (2)        | Scales the peaks using modified sigmoid transfer function to get smooth peaks and achieve the target PAPR. This method   |
    |                    | does not support the filter operation.                                                                                   |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_PRE_DPD_CFR_MAXIMUM_ITERATIONS = 1110077
    r"""Specifies the maximum number of iterations allowed to converge waveform PAPR to target PAPR, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    DPD_PRE_DPD_CFR_TARGET_PAPR = 1110081
    r"""Specifies the target peak-to-average power ratio when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. This value is expressed in dB.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 8.
    """

    DPD_PRE_DPD_CFR_WINDOW_TYPE = 1110082
    r"""Specifies the window type to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
    attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak
    Windowing**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Kaiser-Bessel**.
    
    +---------------------+----------------------------------------------------------+
    | Name (Value)        | Description                                              |
    +=====================+==========================================================+
    | Flat Top (1)        | Uses the flat top window function to scale peaks.        |
    +---------------------+----------------------------------------------------------+
    | Hanning (2)         | Uses the Hanning window function to scale peaks.         |
    +---------------------+----------------------------------------------------------+
    | Hamming (3)         | Uses the Hamming window function to scale peaks.         |
    +---------------------+----------------------------------------------------------+
    | Gaussian (4)        | Uses the Gaussian window function to scale peaks.        |
    +---------------------+----------------------------------------------------------+
    | Blackman (5)        | Uses the Blackman window function to scale peaks.        |
    +---------------------+----------------------------------------------------------+
    | Blackman-Harris (6) | Uses the Blackman-Harris window function to scale peaks. |
    +---------------------+----------------------------------------------------------+
    | Kaiser-Bessel (7)   | Uses the Kaiser-Bessel window function to scale peaks.   |
    +---------------------+----------------------------------------------------------+
    """

    DPD_PRE_DPD_CFR_WINDOW_LENGTH = 1110083
    r"""Specifies the maximum window length to be used when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True** and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak Windowing**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    DPD_PRE_DPD_CFR_SHAPING_FACTOR = 1110084
    r"""Specifies the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
    attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
    Refer to the DPD concept topic for more information about shaping factor.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 5.
    """

    DPD_PRE_DPD_CFR_SHAPING_THRESHOLD = 1110085
    r"""Specifies the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
    attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**. This
    value is expressed in dB. Refer to the DPD concept topic for more information about shaping threshold.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -5.
    """

    DPD_PRE_DPD_CFR_FILTER_ENABLED = 1110112
    r"""Specifies whether to enable the filtering operation when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
    information about filtering.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables the filter operation when performing CFR.                                                                       |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables filter operation when performing CFR. Filter operation is not supported when you set the DPD Pre-DPD CFR Method  |
    |              | attribute to Sigmoid.                                                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_PRE_DPD_CFR_NUMBER_OF_CARRIERS = 1110114
    r"""Specifies the number of carriers in the input waveform when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    DPD_PRE_DPD_CARRIER_OFFSET = 1110115
    r"""Specifies the carrier offset relative to the center of the complex baseband equivalent of the RF signal when you set
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is expressed in
    Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    DPD_PRE_DPD_CARRIER_BANDWIDTH = 1110116
    r"""Specifies the carrier bandwidth when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
    and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is
    expressed in Hz.
    
    Use "carrier<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 20 MHz.
    """

    DPD_ALL_TRACES_ENABLED = 1110047
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the DPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    DPD_NUMBER_OF_ANALYSIS_THREADS = 1110048
    r"""Specifies the maximum number of threads used for parallelism of the DPD measurement.
    
    The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
    may not all be used in calculations. The actual number of threads used depends on the problem size, system resources,
    data availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    DPD_APPLY_DPD_CONFIGURATION_INPUT = 1110049
    r"""Specifies whether to use the configuration parameters used by the DPD measurement for applying DPD.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Measurement**.
    
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)    | Description                                                                                                              |
    +=================+==========================================================================================================================+
    | Measurement (0) | Uses the computed DPD polynomial or lookup table for applying DPD on an input waveform using the same RFmx session       |
    |                 | handle. The configuration parameters for applying DPD such as the DPD DUT Avg Input Pwr, DPD Model, DPD Meas Sample      |
    |                 | Rate, DPD polynomial, and lookup table                                                                                   |
    |                 | are obtained from the DPD measurement configuration.                                                                     |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | User (1)        | Applies DPD by using a computed DPD polynomial or lookup table on an input waveform. You must set the configuration      |
    |                 | parameters for applying DPD such as the                                                                                  |
    |                 | DPD Apply DPD User DUT Avg Input Pwr, DPD Apply DPD User DPD Model, DPD Apply DPD User Meas Sample Rate, DPD             |
    |                 | polynomial, and lookup table. You do not need to call the RFmxSpecAn Initiate method when you set the DPD Apply DPD      |
    |                 | Config Input attribute User.                                                                                             |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_LOOKUP_TABLE_CORRECTION_TYPE = 1110050
    r"""Specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
    **Lookup Table**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Magnitude and Phase**.
    
    +-------------------------+----------------------------------------------------------------------------+
    | Name (Value)            | Description                                                                |
    +=========================+============================================================================+
    | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
    +-------------------------+----------------------------------------------------------------------------+
    | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
    +-------------------------+----------------------------------------------------------------------------+
    | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
    +-------------------------+----------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_MEMORY_MODEL_CORRECTION_TYPE = 1110070
    r"""Specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
    **Memory Polynomial** or ** Generalized Memory Polynomial**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Magnitude and Phase**.
    
    +-------------------------+----------------------------------------------------------------------------+
    | Name (Value)            | Description                                                                |
    +=========================+============================================================================+
    | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
    +-------------------------+----------------------------------------------------------------------------+
    | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
    +-------------------------+----------------------------------------------------------------------------+
    | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
    +-------------------------+----------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_CFR_ENABLED = 1110086
    r"""Specifies whether to enable the crest factor reduction (CFR) on the pre-distorted waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+---------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                           |
    +==============+=======================================================================================+
    | False (0)    | Disables CFR. The maximum increase in PAPR, after pre-distortion, is limited to 6 dB. |
    +--------------+---------------------------------------------------------------------------------------+
    | True (1)     | Enables CFR.                                                                          |
    +--------------+---------------------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_CFR_METHOD = 1110087
    r"""Specifies the method used to perform the crest factor reduction (CFR) when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Clipping**.
    
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)       | Description                                                                                                              |
    +====================+==========================================================================================================================+
    | Clipping (0)       | Hard clips the signal such that the target PAPR is achieved.                                                             |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Peak Windowing (1) | Scales the peaks in the signal using weighted window function to get smooth peaks and achieve the target PAPR.           |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Sigmoid (2)        | Scales the peaks using modified sigmoid transfer function to get smooth peaks and achieve the target PAPR. This method   |
    |                    | does not support the filter operation.                                                                                   |
    +--------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_CFR_MAXIMUM_ITERATIONS = 1110088
    r"""Specifies the maximum number of iterations allowed to converge waveform PAPR to target PAPR when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    DPD_APPLY_DPD_CFR_TARGET_PAPR_TYPE = 1110089
    r"""Specifies the target PAPR type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
    to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Input PAPR**.
    
    +----------------+---------------------------------------------------------------------------------------------------+
    | Name (Value)   | Description                                                                                       |
    +================+===================================================================================================+
    | Input PAPR (0) | Sets the target PAPR for pre-distorted waveform equal to the PAPR of input waveform.              |
    +----------------+---------------------------------------------------------------------------------------------------+
    | Custom (1)     | Sets the target PAPR equal to the value that you set for the Apply DPD CFR Target PAPR attribute. |
    +----------------+---------------------------------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_CFR_TARGET_PAPR = 1110106
    r"""Specifies the target PAPR when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to
    **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_TARGET_PAPR_TYPE` attribute to **Custom**. This
    value is expressed in dB.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 8.
    """

    DPD_APPLY_DPD_CFR_WINDOW_TYPE = 1110107
    r"""Specifies the window type to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
    attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak
    Windowing**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Kaiser-Bessel**.
    
    +---------------------+----------------------------------------------------------+
    | Name (Value)        | Description                                              |
    +=====================+==========================================================+
    | Flat Top (1)        | Uses the flat top window function to scale peaks.        |
    +---------------------+----------------------------------------------------------+
    | Hanning (2)         | Uses the Hanning window function to scale peaks.         |
    +---------------------+----------------------------------------------------------+
    | Hamming (3)         | Uses the Hamming window function to scale peaks.         |
    +---------------------+----------------------------------------------------------+
    | Gaussian (4)        | Uses the Gaussian window function to scale peaks.        |
    +---------------------+----------------------------------------------------------+
    | Blackman (5)        | Uses the Blackman window function to scale peaks.        |
    +---------------------+----------------------------------------------------------+
    | Blackman-Harris (6) | Uses the Blackman-Harris window function to scale peaks. |
    +---------------------+----------------------------------------------------------+
    | Kaiser-Bessel (7)   | Uses the Kaiser-Bessel window function to scale peaks.   |
    +---------------------+----------------------------------------------------------+
    """

    DPD_APPLY_DPD_CFR_WINDOW_LENGTH = 1110108
    r"""Specifies the maximum window length to be used when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True** and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak Windowing**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    DPD_APPLY_DPD_CFR_SHAPING_FACTOR = 1110109
    r"""Specifies the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
    attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
    Refer to DPD concept topic for more information about shaping factor.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 5.
    """

    DPD_APPLY_DPD_CFR_SHAPING_THRESHOLD = 1110110
    r"""Specifies the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
    attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
    This value is expressed in dB. Refer to DPD concept topic for more information about shaping threshold.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -5.
    """

    DPD_APPLY_DPD_USER_DUT_AVERAGE_INPUT_POWER = 1110053
    r"""Specifies the average input power for the device under test that was used to compute the DPD Apply DPD User DPD
    Polynomial or the DPD Apply DPD User LUT Complex Gain when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value is expressed in
    dBm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20 dBm.
    """

    DPD_APPLY_DPD_USER_DPD_MODEL = 1110054
    r"""Specifies the DPD model for applying DPD when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Lookup Table**.
    
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                      | Description                                                                                                              |
    +===================================+==========================================================================================================================+
    | Lookup Table (0)                  | This model computes the complex gain coefficients applied to linearize systems with negligible memory effects.           |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Memory Polynomial (1)             | This model computes the memory polynomial predistortion coefficients used to linearize systems with moderate memory      |
    |                                   | effects.                                                                                                                 |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Generalized Memory Polynomial (2) | This model computes the generalized memory polynomial predistortion coefficients used to linearize systems with          |
    |                                   | significant memory effects.                                                                                              |
    +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    DPD_APPLY_DPD_USER_MEASUREMENT_SAMPLE_RATE = 1110055
    r"""Specifies the acquisition sample rate used to compute the DPD Apply DPD User DPD Polynomial or DPD Apply DPD User LUT
    Complex Gain when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
    **User**. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 120 MHz.
    """

    DPD_APPLY_DPD_USER_LOOKUP_TABLE_TYPE = 1110080
    r"""Specifies the DPD Lookup Table (LUT) type when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    +--------------+-------------------------------------------------+
    | Name (Value) | Description                                     |
    +==============+=================================================+
    | Log (0)      | Input powers in the LUT are specified in dBm.   |
    +--------------+-------------------------------------------------+
    | Linear (1)   | Input powers in the LUT are specified in watts. |
    +--------------+-------------------------------------------------+
    """

    DPD_APPLY_DPD_USER_LOOKUP_TABLE_INPUT_POWER = 1105960
    r"""Specifies the input power array for the predistortion lookup table when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Lookup Table**. This value is expressed
    in dBm.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_ORDER = 1110058
    r"""Specifies the order of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
    Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
    **User**. This value corresponds to K\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
    for generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 3.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MEMORY_DEPTH = 1110059
    r"""Specifies the memory depth of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
    Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
    **User**. This value corresponds to Q\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
    for generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LEAD_ORDER = 1110060
    r"""Specifies the lead order cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
    to K\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
    polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LAG_ORDER = 1110061
    r"""Specifies the lag order cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
    to K\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
    polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LEAD_MEMORY_DEPTH = 1110062
    r"""Specifies the lead memory depth cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
    to Q\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
    polynomial.  The value of the DPD Apply DPD User Mem Poly Lead Mem Depth attribute must be greater than or equal to the
    value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LAG_MEMORY_DEPTH = 1110063
    r"""Specifies the lag memory depth cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
    Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
    **User**. This value corresponds to Q\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
    for the generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD = 1110064
    r"""Specifies the maximum lead stagger cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
    Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
    **User**. This value corresponds to M\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
    for the generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MAXIMUM_LAG = 1110065
    r"""Specifies the maximum lag stagger cross term of the DPD polynomial when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
    Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
    **User**. This value corresponds to M\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
    for the generalized memory polynomial.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    DPD_RESULTS_AVERAGE_GAIN = 1110067
    r"""Returns the average gain of the device under test. This value is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    DPD_RESULTS_NMSE = 1110111
    r"""Returns the normalized mean-squared DPD modeling error when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute to **True**. This value is expressed in dB. NaN
    is returned when the :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute is set to **False**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    IDPD_MEASUREMENT_ENABLED = 1310720
    r"""Specifies whether to enable IDPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    IDPD_EQUALIZER_MODE = 1310722
    r"""Specifies whether to enable equalization.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **OFF.**
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Off (0)      | Equalization filter is not applied.                                                                                      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Train (1)    | Train Equalization filter. The filter length is obtained from the IDPD Equalizer Filter Length attribute.                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hold (2)     | The RFmxSpecAn IDPD Configure Equalizer Coefficients method specifies the filter that acts as the equalization filter.   |
    |              | This filter is applied prior to calculating the predistorted waveform.                                                   |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IDPD_EQUALIZER_FILTER_LENGTH = 1310723
    r"""Specifies the length of the equalizer filter to be trained.
    
    This attribute is applicable when you set :py:attr:`~nirfmxspecan.attributes.AttributeID.EQUALIZER_MODE` to
    **Train**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 101.
    Valid values are 1 to 4096, inclusive.
    """

    IDPD_MEASUREMENT_SAMPLE_RATE_MODE = 1310724
    r"""Specifies acquisition sample rate configuration mode.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Reference Waveform**.
    
    +------------------------+------------------------------------------------------------------------------------+
    | Name (Value)           | Description                                                                        |
    +========================+====================================================================================+
    | User (0)               | Acquisition sample rate is defined by the IDPD Meas Sample Rate (S/s) attribute.   |
    +------------------------+------------------------------------------------------------------------------------+
    | Reference Waveform (1) | Acquisition sample rate is set to match the sample rate of the reference waveform. |
    +------------------------+------------------------------------------------------------------------------------+
    """

    IDPD_MEASUREMENT_SAMPLE_RATE = 1310725
    r"""Specifies the acquisition sample rate, in S/s, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` is **User.**
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 120000000.
    """

    IDPD_SIGNAL_TYPE = 1310726
    r"""Specifies the type of reference waveform.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Modulated.**
    
    +---------------+-----------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                         |
    +===============+=====================================================================================================+
    | Modulated (0) | Specifies the reference waveform is a banded signal like cellular or connectivity standard signals. |
    +---------------+-----------------------------------------------------------------------------------------------------+
    | Tones (1)     | Specifies the reference waveform is a continuous signal comprising of one or more tones.            |
    +---------------+-----------------------------------------------------------------------------------------------------+
    """

    IDPD_REFERENCE_WAVEFORM_IDLE_DURATION_PRESENT = 1310731
    r"""Specifies whether the reference waveform contains idle duration or dead time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------+
    | Name (Value) | Description                                |
    +==============+============================================+
    | False (0)    | Reference waveform has no idle duration.   |
    +--------------+--------------------------------------------+
    | True (1)     | Reference waveform contains idle duration. |
    +--------------+--------------------------------------------+
    """

    IDPD_DUT_AVERAGE_INPUT_POWER = 1310732
    r"""Specifies the initial (first itertion) average power of the signal at the input port of the device under test.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -20.
    """

    IDPD_AVERAGING_ENABLED = 1310735
    r"""Specifies whether to enable averaging for the IDPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | False (0)    | The number of acquisitions is 1.                                                                            |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | True (1)     | the measurement uses Averaging Count for the number of acquisitions over which the measurement is averaged. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    IDPD_AVERAGING_COUNT = 1310736
    r"""Specifies the number of acquisitions used for averaging when
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` is **TRUE**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    IDPD_EVM_ENABLED = 1310739
    r"""Specifies whether to enable EVM computation.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+-------------------------------------------------------------+
    | Name (Value) | Description                                                 |
    +==============+=============================================================+
    | False (0)    | Disables EVM computation. NaN is returned for Mean RMS EVM. |
    +--------------+-------------------------------------------------------------+
    | True (1)     | Enables EVM computation.                                    |
    +--------------+-------------------------------------------------------------+
    """

    IDPD_EVM_UNIT = 1310740
    r"""Specifies the units of the EVM results.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Percentage**.
    
    +----------------+-----------------------------------+
    | Name (Value)   | Description                       |
    +================+===================================+
    | Percentage (0) | EVM is expressed as a percentage. |
    +----------------+-----------------------------------+
    | dB (1)         | EVM is expressed in dB.           |
    +----------------+-----------------------------------+
    """

    IDPD_IMPAIRMENT_ESTIMATION_START = 1310741
    r"""Specifies the start time of the impairment estimation interval relative to the start of the reference waveform. This
    value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    IDPD_IMPAIRMENT_ESTIMATION_STOP = 1310742
    r"""Specifies the stop time of the impairment estimation interval relative to the start of the reference waveform. This
    value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    IDPD_SYNCHRONIZATION_ESTIMATION_START = 1310743
    r"""Specifies the start time of the synchronization estimation interval relative to the start of the reference waveform.
    This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    IDPD_SYNCHRONIZATION_ESTIMATION_STOP = 1310744
    r"""Specifies the stop time of the synchronization estimation interval relative to the start of the reference waveform.
    This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    IDPD_GAIN_EXPANSION = 1310745
    r"""Specifies the increase of input power relative to the peak power value of the reference signal. This value is expressed
    in dB.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 6.
    """

    IDPD_TARGET_GAIN = 1310759
    r"""Specifies the Target gain when the configured pre-distorted waveform is non-empty.
    
    When the configured pre-distorted waveform is empty, this attribute is ignored. It is recommended to use the
    Gain result from the previous iteration to configure this attribute.
    
    The default value is 20.
    """

    IDPD_POWER_LINEARITY_TRADEOFF = 1310747
    r"""Specifies the gain tradeoff factor that sets the gain expected from the DUT after applying IDPD on the input waveform.
    This value is expressed as a percentage.
    
    The percentages zero corresponds to the gain at maximum linearity, hundred corresponds to the gain at maximum
    power, and fifty corresponds to the gain at average power output from the DUT.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 50.
    """

    IDPD_RESULTS_GAIN = 1310749
    r"""Returns the gain of the device under test. This value is expressed in dB.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    IDPD_RESULTS_MEAN_RMS_EVM = 1310750
    r"""Returns the ratio of L2 norm of difference between the normalized reference and acquired waveforms, to the L2 norm of
    the normalized reference waveform. This value is expressed either as a percentage or in dB depending on the configured
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EVM_UNIT`,
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    IDPD_ALL_TRACES_ENABLED = 1310751
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the IDPD measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    IDPD_NUMBER_OF_ANALYSIS_THREADS = 1310753
    r"""Specifies the maximum number of threads used for parallelism for the IDPD measurement.
    
    The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
    may not be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    IQ_MEASUREMENT_ENABLED = 1110272
    r"""Specifies whether to enable the I/Q measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    IQ_MEASUREMENT_MODE = 1110284
    r"""Specifies the mode for performing the IQ measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Normal**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Normal (0)   | Performs the measurement in the normal RFmx execution mode and supports all the RFmx features such as overlapped         |
    |              | measurements.                                                                                                            |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | RawIQ (1)    | Reduces the overhead introduced by this measurement by not copying and storing the data in RFmx. In this mode IQ data    |
    |              | needs to be retrieved using                                                                                              |
    |              | RFmxInstr Fetch Raw IQ method instead of RFmxSpecAn IQ Fetch Data method.                                                |
    |              | RFmxInstr Fetch Raw IQ directly fetches the data from the hardware.                                                      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IQ_SAMPLE_RATE = 1110274
    r"""Specifies the acquisition sample rate. This value is expressed in samples per second (S/s).
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 50 MS/s.
    """

    IQ_ACQUISITION_TIME = 1110276
    r"""Specifies the acquisition time for the I/Q measurement. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    IQ_PRETRIGGER_TIME = 1110277
    r"""Specifies the pretrigger time for the I/Q measurement. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    IQ_BANDWIDTH_AUTO = 1110280
    r"""Specifies whether the measurement computes the minimum acquisition bandwidth.
    
    The default value is **True**.
    
    +--------------+----------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                        |
    +==============+====================================================================================================+
    | False (0)    | The measurement uses the value of the IQ Bandwidth attribute as the minimum acquisition bandwidth. |
    +--------------+----------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement uses 0.8 * sample rate as the minimum signal bandwidth.                            |
    +--------------+----------------------------------------------------------------------------------------------------+
    """

    IQ_BANDWIDTH = 1110281
    r"""Specifies the minimum acquisition bandwidth when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_AUTO` attribute to **False**. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 MHz.
    """

    IQ_NUMBER_OF_RECORDS = 1110275
    r"""Specifies the number of records to acquire.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    IQ_DELETE_RECORD_ON_FETCH = 1110282
    r"""Specifies whether the measurement deletes the fetched record.
    
    The default value is **True**.
    
    +--------------+-----------------------------------------------------+
    | Name (Value) | Description                                         |
    +==============+=====================================================+
    | False (0)    | The measurement does not delete the fetched record. |
    +--------------+-----------------------------------------------------+
    | True (1)     | The measurement deletes the fetched record.         |
    +--------------+-----------------------------------------------------+
    """

    IM_MEASUREMENT_ENABLED = 1114112
    r"""Specifies whether to enable the IM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    IM_FREQUENCY_DEFINITION = 1114114
    r"""Specifies whether the tones and intermod frequencies are relative to the RF
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`, or are absolute frequencies.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Relative**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                  |
    +==============+==============================================================================================================+
    | Relative (0) | The tone and intermod frequencies are relative to the RF center frequency.                                   |
    +--------------+--------------------------------------------------------------------------------------------------------------+
    | Absolute (1) | The tone and intermod frequencies are absolute frequencies. The measurement ignores the RF center frequency. |
    +--------------+--------------------------------------------------------------------------------------------------------------+
    """

    IM_FUNDAMENTAL_LOWER_TONE_FREQUENCY = 1114115
    r"""Specifies the frequency of the tone that has a lower frequency among the two tones in the input signal. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1 MHz.
    """

    IM_FUNDAMENTAL_UPPER_TONE_FREQUENCY = 1114116
    r"""Specifies the frequency of the tone that has a higher frequency among the two tones in the input signal. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 MHz.
    """

    IM_AUTO_INTERMODS_SETUP_ENABLED = 1114117
    r"""Specifies whether the measurement computes the intermod frequencies or uses user-specified frequencies.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement uses the values that you specify for the IM Lower Intermod Freq and IM Upper Intermod Freq attributes.   |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement computes the intermod frequencies. The maximum number of intermods that you can measure is based on the  |
    |              | value of the IM Max Intermod Order attribute.                                                                            |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_MAXIMUM_INTERMOD_ORDER = 1114118
    r"""Specifies the order up to which the RFmx driver measures odd order intermodulation products when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**. The lower and upper
    intermodulation products are measured for each order.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **3**.
    """

    IM_NUMBER_OF_INTERMODS = 1114119
    r"""Specifies the number of intermods to measure when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    IM_INTERMOD_ENABLED = 1114120
    r"""Specifies whether to enable an intermod for the IM measurement. This attribute is not used when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.
    
    Use "intermod<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **True**.
    
    +--------------+-----------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                               |
    +==============+===========================================================================================================+
    | False (0)    | Disables an intermod for the IM measurement. The results for the disabled intermods are displayed as NaN. |
    +--------------+-----------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables an intermod for the IM measurement.                                                               |
    +--------------+-----------------------------------------------------------------------------------------------------------+
    """

    IM_INTERMOD_ORDER = 1114121
    r"""Specifies the order of the intermod. This attribute is not used when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.
    
    Use "intermod<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 3.
    """

    IM_INTERMOD_SIDE = 1114122
    r"""Specifies whether to measure intermodulation products corresponding to both lower and upper intermod frequencies or
    either one of them. This attribute is not used when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.
    
    Use "intermod<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Both**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Lower (0)    | Measures the intermodulation product corresponding to the IM Lower Intermod Freq attribute.                              |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Upper (1)    | Measures the intermodulation product corresponding to the IM Upper Intermod Freq attribute.                              |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Both (2)     | Measures the intermodulation product corresponding to both IM Lower Intermod Freq and IM Upper Intermod Freq             |
    |              | attributes.                                                                                                              |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_LOWER_INTERMOD_FREQUENCY = 1114123
    r"""Specifies the frequency of the lower intermodulation product. This value is expressed in Hz. This attribute is not used
    when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.
    
    Use "intermod<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is -3 MHz.
    """

    IM_UPPER_INTERMOD_FREQUENCY = 1114124
    r"""Specifies the frequency of the upper intermodulation product. This value is expressed in Hz. This attribute is not used
    when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.
    
    Use "intermod<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 3 MHz.
    """

    IM_MEASUREMENT_METHOD = 1114125
    r"""Specifies the method used to perform the IM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Normal**.
    
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)      | Description                                                                                                              |
    +===================+==========================================================================================================================+
    | Normal (0)        | The IM measurement acquires the spectrum using the same signal analyzer settings across frequency bands. Use this        |
    |                   | method when the fundamental tone separation is not large.                                                                |
    |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668.                          |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Dynamic Range (1) | The IM measurement acquires a segmented spectrum using the signal analyzer specific optimizations for different          |
    |                   | frequency bands. The spectrum is acquired in segments, one per tone or intermod frequency to be measured. The span of    |
    |                   | each acquired spectral segment is equal to the frequency separation between the two input tones, or 1 MHz, whichever is  |
    |                   | smaller.                                                                                                                 |
    |                   | Use this method to configure the IM measurement and the signal analyzer for maximum dynamic range instead of             |
    |                   | measurement speed.                                                                                                       |
    |                   | Supported devices: PXIe-5665/5668.                                                                                       |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Segmented (2)     | Similar to the Dynamic Range method, this method also acquires a segmented spectrum, except that signal analyzer is not  |
    |                   | explicitly configured to provide maximum dynamic range. Use this method when the frequency separation of the two input   |
    |                   | tones is large and the measurement accuracy can be traded off for measurement speed.                                     |
    |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668.                          |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_LOCAL_PEAK_SEARCH_ENABLED = 1114154
    r"""Specifies whether to enable a local peak search around the tone or intermod frequencies to account for small frequency
    offsets.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+-----------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                     |
    +==============+=================================================================================================================+
    | False (0)    | The measurement returns the power at the tone and intermod frequencies.                                         |
    +--------------+-----------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement performs a local peak search around the tone and intermod frequencies to return the peak power. |
    +--------------+-----------------------------------------------------------------------------------------------------------------+
    """

    IM_RBW_FILTER_AUTO_BANDWIDTH = 1114126
    r"""Specifies whether the measurement computes the RBW.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+------------------------------------------------------------------------+
    | Name (Value) | Description                                                            |
    +==============+========================================================================+
    | False (0)    | The measurement uses the RBW that you specify in the IM RBW attribute. |
    +--------------+------------------------------------------------------------------------+
    | True (1)     | The measurement computes the RBW.                                      |
    +--------------+------------------------------------------------------------------------+
    """

    IM_RBW_FILTER_BANDWIDTH = 1114127
    r"""Specifies the bandwidth of the RBW filter used to sweep the acquired signal, when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 kHz.
    """

    IM_RBW_FILTER_TYPE = 1114128
    r"""Specifies the response of the digital RBW filter.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Gaussian**.
    
    +---------------+----------------------------------------------------+
    | Name (Value)  | Description                                        |
    +===============+====================================================+
    | FFT Based (0) | No RBW filtering is performed.                     |
    +---------------+----------------------------------------------------+
    | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
    +---------------+----------------------------------------------------+
    | Flat (2)      | An RBW filter with a flat response is applied.     |
    +---------------+----------------------------------------------------+
    """

    IM_SWEEP_TIME_AUTO = 1114129
    r"""Specifies whether the measurement computes the sweep time.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                          |
    +==============+======================================================================================+
    | False (0)    | The measurement uses the sweep time that you specify in the IM Sweep Time attribute. |
    +--------------+--------------------------------------------------------------------------------------+
    | True (1)     | The measurement computes the sweep time based on the value of the IM RBW attribute.  |
    +--------------+--------------------------------------------------------------------------------------+
    """

    IM_SWEEP_TIME_INTERVAL = 1114130
    r"""Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
    **False**. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.001.
    """

    IM_AVERAGING_ENABLED = 1114131
    r"""Specifies whether to enable averaging for the IM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The IM measurement uses the IM Averaging Count attribute as the number of acquisitions over which the IM measurement is  |
    |              | averaged.                                                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_AVERAGING_COUNT = 1114132
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    IM_AVERAGING_TYPE = 1114134
    r"""Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for the IM
    measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RMS**.
    
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                 |
    +==============+=============================================================================================================+
    | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
    +--------------+-------------------------------------------------------------------------------------------------------------+
    """

    IM_FFT_WINDOW = 1114135
    r"""Specifies the FFT window type to use to reduce spectral leakage.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Flat Top**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful   |
    |                     | for time-frequency analysis.                                                                                             |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_FFT_PADDING = 1114136
    r"""Specifies the factor by which the time-domain waveform is zero-padded before an FFT. The FFT size is given by the
    following formula:
    
    *FFT size* = *waveform size* * *padding*
    
    This attribute is used only when the acquisition span is less than the device instantaneous bandwidth.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is -1.
    """

    IM_IF_OUTPUT_POWER_OFFSET_AUTO = 1114137
    r"""Specifies whether the measurement computes an IF output power level offset for the intermods to maximize the dynamic
    range of the signal analyzer. This attribute is used only if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **True**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement sets the IF output power level offset using the values of the IM Near IF Output Power Offset and IM Far  |
    |              | IF Output Power Offset attributes.                                                                                       |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The measurement computes an IF output power level offset for the intermods to improve the dynamic range of the IM        |
    |              | measurement.                                                                                                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_NEAR_IF_OUTPUT_POWER_OFFSET = 1114138
    r"""Specifies the offset by which to adjust the IF output power level for the intermods near the carrier channel to improve
    the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only if you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 dB.
    """

    IM_FAR_IF_OUTPUT_POWER_OFFSET = 1114139
    r"""Specifies the offset by which to adjust the IF output power level for the intermods that are far from the carrier
    channel to improve the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only
    if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 20 dB.
    """

    IM_AMPLITUDE_CORRECTION_TYPE = 1114155
    r"""Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
    at the RF center frequency, or at the individual frequency bins. Use the
    :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
    attenuation table.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF Center Frequency**.
    
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)               | Description                                                                                                              |
    +============================+==========================================================================================================================+
    | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
    |                            | RF center frequency.                                                                                                     |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Spectrum Frequency Bin (1) | An Individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
    |                            | frequency.                                                                                                               |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    IM_ALL_TRACES_ENABLED = 1114140
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the IM measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    IM_NUMBER_OF_ANALYSIS_THREADS = 1114141
    r"""Specifies the maximum number of threads used for parallelism for the IM measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    IM_RESULTS_LOWER_TONE_POWER = 1114143
    r"""Returns the peak power measured around the lower tone frequency when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
    expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
    power at the lower tone frequency.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    IM_RESULTS_UPPER_TONE_POWER = 1114145
    r"""Returns the peak power measured around the upper tone frequency when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
    expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
    power at the upper tone frequency.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    IM_RESULTS_INTERMOD_ORDER = 1114146
    r"""Returns the order of the intermod.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_LOWER_INTERMOD_POWER = 1114148
    r"""Returns the peak power measured around the lower intermod frequency when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
    expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
    power at the lower intermod frequency.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_UPPER_INTERMOD_POWER = 1114150
    r"""Returns the peak power measured around the upper intermod frequency when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
    expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
    power at the upper intermod frequency.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_WORST_CASE_INTERMOD_ABSOLUTE_POWER = 1114162
    r"""Returns the worst case intermod power that is equal to the maximum of the values of both the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_POWER` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_POWER` results. This value is expressed in dBm.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_LOWER_INTERMOD_RELATIVE_POWER = 1114160
    r"""Returns the relative peak power measured around the lower intermod frequency when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
    expressed in dBc. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
    relative power at the lower intermod frequency.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_UPPER_INTERMOD_RELATIVE_POWER = 1114161
    r"""Returns the relative peak power measured around the upper intermod frequency when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
    expressed in dBc. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
    relative power at the upper intermod frequency.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_WORST_CASE_INTERMOD_RELATIVE_POWER = 1114163
    r"""Returns the worst case intermod relative power that is equal to the maximum of the values of both the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_RELATIVE_POWER` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_RELATIVE_POWER` results. This value is expressed in dBc.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_LOWER_OUTPUT_INTERCEPT_POWER = 1114151
    r"""Returns the lower output intercept power. This value is expressed in dBm. Refer to the IM topic for more information
    about this result.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_UPPER_OUTPUT_INTERCEPT_POWER = 1114152
    r"""Returns the upper output intercept power. This value is expressed in dBm. Refer to the IM topic for more information
    about this result.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    IM_RESULTS_WORST_CASE_OUTPUT_INTERCEPT_POWER = 1114153
    r"""Returns the worst case output intercept power which is equal to the minimum of the values of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OUTPUT_INTERCEPT_POWER` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OUTPUT_INTERCEPT_POWER` results. This value is expressed in dBm.
    
    Use "intermod<*n*>" as the selector string to read this result.
    """

    NF_MEASUREMENT_ENABLED = 1179649
    r"""Enables the noise figure (NF) measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    NF_DUT_TYPE = 1179706
    r"""Specifies the type of DUT.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Amplifier**.
    
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)      | Description                                                                                                              |
    +===================+==========================================================================================================================+
    | Amplifier (0)     | Specifies that the DUT only amplifies or attenuates the signal, and does not change the frequency.                       |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Downconverter (1) | Specifies that the DUT is a downconverter, that is, the IF frequency is the difference between the LO and RF             |
    |                   | frequencies.                                                                                                             |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Upconverter (2)   | Specifies that the DUT is an upconverter, that is, the IF frequency is the sum of LO and RF frequencies.                 |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_FREQUENCY_CONVERTER_LO_FREQUENCY = 1179708
    r"""Specifies the fixed LO frequency of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE`
    attribute to either **Downconverter** or **Upconverter**. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 MHz.
    """

    NF_FREQUENCY_CONVERTER_FREQUENCY_CONTEXT = 1179710
    r"""Specifies the context of the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **RF**.
    
    +--------------+---------------------------------------------+
    | Name (Value) | Description                                 |
    +==============+=============================================+
    | RF (0)       | Specifies that the frequency context is RF. |
    +--------------+---------------------------------------------+
    | IF (1)       | Specifies that the frequency context is IF. |
    +--------------+---------------------------------------------+
    """

    NF_FREQUENCY_CONVERTER_SIDEBAND = 1179711
    r"""Specifies the sideband when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE` attribute to either
    **Downconverter** or **Upconverter**, and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_CONVERTER_FREQUENCY_CONTEXT` attribute to **IF**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **LSB**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | LSB (0)      | When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is     |
    |              | treated as the RF (signal) frequency while the higher is treated as the image frequency.                                 |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | USB (1)      | When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is     |
    |              | treated as the image frequency while the higher is treated as the RF (signal) frequency.                                 |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_FREQUENCY_CONVERTER_IMAGE_REJECTION = 1179712
    r"""Specifies the gain ratio of the DUT at the image frequency to that at the RF frequency. This value is expressed in dB.
    Refer to NF concept help for more details.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 999.99 dB.
    """

    NF_FREQUENCY_LIST = 1179652
    r"""Specifies the list of frequencies at which the noise figure (NF) of the DUT is computed. This value is expressed in Hz.
    
    The default value is an empty array.
    """

    NF_MEASUREMENT_BANDWIDTH = 1179653
    r"""Specifies the effective noise-bandwidth in which power measurements are performed for the noise figure (NF)
    measurement. This value is expressed in Hz.
    
    The default value is 100 kHz.
    """

    NF_MEASUREMENT_INTERVAL = 1179654
    r"""Specifies the duration for which the signals are acquired at each frequency which you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 ms.
    """

    NF_AVERAGING_ENABLED = 1179655
    r"""Specifies whether to enable averaging for the noise figure (NF) measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | The measurement is performed on a single acquisition.                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | The NF measurement uses the value of the NF Averaging Count attribute as the number of acquisitions for each frequency   |
    |              | which you specify in the NF Freq List attribute, over which the NF measurement is averaged.                              |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_AVERAGING_COUNT = 1179656
    r"""Specifies the number of acquisitions used for averaging when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    NF_CALIBRATION_SETUP_ID = 1179700
    r"""Associates a unique string identifier with the hardware setup used to perform calibration for the NF measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty string.
    """

    NF_EXTERNAL_PREAMP_PRESENT = 1179701
    r"""Specifies if an external preamplifier is present in the signal path.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+------------------------------------------------------+
    | Name (Value) | Description                                          |
    +==============+======================================================+
    | False (0)    | No external preamplifier present in the signal path. |
    +--------------+------------------------------------------------------+
    | True (1)     | An external preamplifier present in the signal path. |
    +--------------+------------------------------------------------------+
    """

    NF_EXTERNAL_PREAMP_FREQUENCY = 1179702
    r"""Specifies the array of frequencies corresponding to the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_GAIN` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    NF_EXTERNAL_PREAMP_GAIN = 1179703
    r"""Specifies the gain of the external preamp as a function of frequency. The value is expressed in dB.
    
    Specify the frequencies at which gain values were measured using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_FREQUENCY` attribute.
    """

    NF_DUT_INPUT_LOSS_COMPENSATION_ENABLED = 1179665
    r"""Specifies whether the noise figure (NF) measurement accounts for ohmic losses between the noise source and the input
    port of the DUT, excluding the losses that are common to calibration and the measurement steps for the Y-Factor method,
    which are specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+---------------------------------------------------+
    | Name (Value) | Description                                       |
    +==============+===================================================+
    | False (0)    | The NF measurement ignores the ohmic losses.      |
    +--------------+---------------------------------------------------+
    | True (1)     | The NF measurement accounts for the ohmic losses. |
    +--------------+---------------------------------------------------+
    """

    NF_DUT_INPUT_LOSS_FREQUENCY = 1179667
    r"""Specifies an array of frequencies corresponding to the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_DUT_INPUT_LOSS = 1179666
    r"""Specifies an array of the ohmic losses between the noise source and the input port of the DUT, as a function of the
    frequency. This value is expressed in dB. This loss is accounted for by the NF measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_COMPENSATION_ENABLED` attribute to **True**. You must
    exclude any loss which is inherent to the noise source and is common between the calibration and measurement steps, and
    configure the loss using the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.
    
    Specify the frequencies at which the losses were measured using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_FREQUENCY` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_DUT_INPUT_LOSS_TEMPERATURE = 1179668
    r"""Specifies the physical temperature of the ohmic loss elements considered in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 297.
    """

    NF_DUT_OUTPUT_LOSS_COMPENSATION_ENABLED = 1179669
    r"""Specifies whether the noise figure (NF) measurement accounts for ohmic losses between the output port of the DUT and
    the input port of the analyzer.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+---------------------------------------------------+
    | Name (Value) | Description                                       |
    +==============+===================================================+
    | False (0)    | The NF measurement ignores ohmic losses.          |
    +--------------+---------------------------------------------------+
    | True (1)     | The NF measurement accounts for the ohmic losses. |
    +--------------+---------------------------------------------------+
    """

    NF_DUT_OUTPUT_LOSS_FREQUENCY = 1179671
    r"""Specifies the array of frequencies corresponding to the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS`  attribute. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_DUT_OUTPUT_LOSS = 1179670
    r"""Specifies the array of ohmic losses between the output port of the DUT and the input port of the analyzer, as a
    function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
    when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_COMPENSATION_ENABLED` attribute to
    **True**.
    
    Specify the array of frequencies at which the losses were measured using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_FREQUENCY` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_DUT_OUTPUT_LOSS_TEMPERATURE = 1179672
    r"""Specifies the physical temperature of the ohmic loss elements specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 297.
    """

    NF_CALIBRATION_LOSS_COMPENSATION_ENABLED = 1179677
    r"""Specifies whether the noise figure (NF) measurement accounts for the ohmic losses between the noise source and input
    port of the analyzer during the calibration step, excluding any losses which you have specified using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+---------------------------------------------------+
    | Name (Value) | Description                                       |
    +==============+===================================================+
    | False (0)    | The NF measurement ignores the ohmic losses.      |
    +--------------+---------------------------------------------------+
    | True (1)     | The NF measurement accounts for the ohmic losses. |
    +--------------+---------------------------------------------------+
    """

    NF_CALIBRATION_LOSS_FREQUENCY = 1179679
    r"""Specifies an array of frequencies corresponding to the ohmic losses between the source and the input port of the
    analyzer. This value is expressed in Hz. This attribute is applicable only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_MODE` attribute to **Calibrate** and set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**, or when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_MODE` attribute to **Calibrate** and set the NF Meas Method
    attribute to **Cold Source**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_CALIBRATION_LOSS = 1179678
    r"""Specifies the array of ohmic losses between the noise source and input port of the analyzer during calibration, as a
    function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
    when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_COMPENSATION_ENABLED` attribute to
    **True**. You must exclude any loss specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.
    
    This attribute specifies the frequencies at which the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_FREQUENCY` attribute measures the losses.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_CALIBRATION_LOSS_TEMPERATURE = 1179680
    r"""Specifies the physical temperature of the ohmic loss elements specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 297.
    """

    NF_MEASUREMENT_METHOD = 1179657
    r"""Specifies the measurement method used to perform the noise figure (NF) measurement. Refer to the NF concept topic for
    more information.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Y-Factor**.
    
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)    | Description                                                                                                              |
    +=================+==========================================================================================================================+
    | Y-Factor (0)    | The NF measurement computes the noise figure of the DUT using a noise source with a calibrated excess-noise ratio        |
    |                 | (ENR).                                                                                                                   |
    |                 | Refer to the NF Y-Factor NS Type attribute for information about supported devices and their corresponding noise source  |
    |                 | type.                                                                                                                    |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Cold Source (1) | The NF measurement computes the noise figure of the DUT using a 50 ohm microwave termination as the noise source.        |
    |                 | Supported Devices: PXIe-5644/5645/5646/5840/5841/5842/5860, PXIe-5830/5831/5832                                          |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_Y_FACTOR_MODE = 1179658
    r"""Specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
    characteristics of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
    attribute to **Y-Factor**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Measure**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | Measure (0)   | The noise figure (NF) measurement computes the noise characteristics of the DUT, compensating for the noise figure of    |
    |               | the analyzer.                                                                                                            |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                                   |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_Y_FACTOR_NOISE_SOURCE_TYPE = 1179713
    r"""Specifies the noise source type for performing the noise figure (NF) measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **External Noise Source**.
    
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)              | Description                                                                                                              |
    +===========================+==========================================================================================================================+
    | External Noise Source (0) | The NF measurement generates noise using an external noise source, that is controlled either by an internal noise        |
    |                           | source power supply or an NI Source Measure Unit (SMU).                                                                  |
    |                           | Supported Devices: PXIe-5665 (3.6 GHz), PXIe-5668, PXIe-5644/5645/5646*, PXIe-5840*/5841*/5842*/5860*, PXIe              |
    |                           | 5830/5831*/5832*                                                                                                         |
    |                           | *Use an external NI Source Measure Unit (SMU) as the noise source power supply for the Noise Figure measurement.         |
    |                           | During initialization, specify the SMU resource name using "NoiseSourcePowerSupply" as the specifier within the          |
    |                           | RFmxSetup string. For example, "RFmxSetup= NoiseSourcePowerSupply:myDCPower[0]" configures RFmx to use channel 0 on      |
    |                           | myDCPower SMU device for powering the noise source. You should allocate a dedicated SMU channel for RFmx.                |
    |                           | RFmx supports PXIe-4138, PXIe-4139, and PXIe-4139 (40 W) SMUs.                                                           |
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | RF Signal Generator (1)   | When you measure Y-Factor based NF using a supported NI vector signal transceiver (VST) instrument, RFmx generates       |
    |                           | noise using the vector signal generator (VSG) integrated into the same VST.                                              |
    |                           | RFmx automatically configures the vector signal generator (VSG) to generate noise at the specified bandwidth and ENR     |
    |                           | levels that you set using the NF Y-Factor NS ENR Freq and NF Y-Factor NS ENR attributes.                                 |
    |                           | Supported Devices: PXIe-5842/5860                                                                                        |
    +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_Y_FACTOR_NOISE_SOURCE_RF_SIGNAL_GENERATOR_PORT = 1179714
    r"""Specifies the vector signal generator port to be configured to generate a noise signal when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **RF Signal Generator**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is "" (empty string).
    """

    NF_Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY = 1179661
    r"""Specifies an array of frequencies corresponding to the effective noise ratio (ENR) values specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR` attribute. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_Y_FACTOR_NOISE_SOURCE_ENR = 1179660
    r"""Specifies the array of effective noise ratio (ENR) values of the noise source as a function of the frequency. This
    value is expressed in dB. The corresponding frequencies are specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY` attribute. This attribute is used
    only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_Y_FACTOR_NOISE_SOURCE_COLD_TEMPERATURE = 1179662
    r"""Specifies the calibrated cold noise temperature of the noise source used in the Y-Factor method. This value is
    expressed in kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 302.8.
    """

    NF_Y_FACTOR_NOISE_SOURCE_OFF_TEMPERATURE = 1179663
    r"""Specifies the physical temperature of the noise source used in the Y-Factor method when the noise source is turned off.
    This value is expressed in kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 297.
    """

    NF_Y_FACTOR_NOISE_SOURCE_SETTLING_TIME = 1179664
    r"""Specifies the time to wait till the noise source used in the Y-Factor method settles to either hot or cold state when
    the noise source is turned on or off. This attribute is used only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **External Noise Source**. This
    value is expressed in seconds.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    NF_Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED = 1179673
    r"""Specifies whether the noise figure (NF) measurement should account for ohmic losses inherent to the noise source used
    in the Y-Factor method common to the calibration and measurement steps.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+-------------------------------------------------------+
    | Name (Value) | Description                                           |
    +==============+=======================================================+
    | False (0)    | Ohmic losses are ignored.                             |
    +--------------+-------------------------------------------------------+
    | True (1)     | Ohmic losses are accounted for in the NF measurement. |
    +--------------+-------------------------------------------------------+
    """

    NF_Y_FACTOR_NOISE_SOURCE_LOSS_FREQUENCY = 1179675
    r"""Specifies the frequencies corresponding to the ohmic loss inherent to the noise source used in the Y-Factor method
    specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is
    expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_Y_FACTOR_NOISE_SOURCE_LOSS = 1179674
    r"""Specifies an array of the ohmic losses inherent to the noise source used in the Y-Factor method. This value is
    expressed in dB. This loss is accounted for by the NF measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED` attribute to **True**.
    
    You must specify the frequencies at which the losses were measured using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_FREQUENCY` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_Y_FACTOR_NOISE_SOURCE_LOSS_TEMPERATURE = 1179676
    r"""Specifies the physical temperature of the ohmic loss elements specified in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is expressed in
    kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 297.
    """

    NF_COLD_SOURCE_MODE = 1179691
    r"""Specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
    characteristics of the DUT for the cold source method.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Measure**.
    
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)  | Description                                                                                                              |
    +===============+==========================================================================================================================+
    | Measure (0)   | The noise figure (NF) measurement computes the noise characteristics of the DUT and compensates for the noise figure of  |
    |               | the analyzer.                                                                                                            |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                                   |
    +---------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    NF_COLD_SOURCE_INPUT_TERMINATION_VSWR = 1179692
    r"""Specifies an array of voltage standing wave ratios (VSWR) as a function of frequency of the microwave termination used
    as the noise source in cold source method. The corresponding array of frequencies is specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY` attribute.
    
    In most cases, the exact VSWR of the microwave termination may not be known. Hence, NI recommends that you set
    this attribute to an empty array, in which case the noise figure (NF) measurement assumes that the VSWR of the
    microwave termination is unity for all frequencies.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY = 1179693
    r"""Specifies an array of  frequencies corresponding to the voltage standing wave ratios (VSWR) of the microwave
    termination used in the cold source method as specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR` attribute. This value is expressed
    in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_COLD_SOURCE_INPUT_TERMINATION_TEMPERATURE = 1179694
    r"""Specifies the physical temperature of the microwave termination used as the noise source in the cold source method.
    This value is expressed in kelvin.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 297.
    """

    NF_COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY = 1179699
    r"""Specifies an array of frequencies corresponding to the s-parameters of the DUT specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S21`,
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S12`,
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S11`, and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S22` attributes. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_COLD_SOURCE_DUT_S21 = 1179695
    r"""Specifies an array of the gains of the DUT as a function of frequency, when the output port of the DUT is terminated
    with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding array of
    frequencies is specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY`
    attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_COLD_SOURCE_DUT_S12 = 1179696
    r"""Specifies an array of the input-isolations of the DUT as a function of frequency, when the input port of the DUT is
    terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
    array of frequencies is specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_COLD_SOURCE_DUT_S11 = 1179697
    r"""Specifies an array of the input-reflections of the DUT as a function of frequency, when the output port of the DUT is
    terminated with an impedance equal to the characteristic impedance. This value is expressed in dB.
    
    The corresponding array of frequencies is specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_COLD_SOURCE_DUT_S22 = 1179698
    r"""Specifies an array of the output-reflections of the DUT as a function of frequency, when the input port of the DUT is
    terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
    array of frequencies is specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    NF_DEVICE_TEMPERATURE_TOLERANCE = 1179705
    r"""Specifies the tolerance for device temperature beyond which the calibration data is considered invalid. This value  is
    expressed in Celsius.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 5.
    """

    NF_NUMBER_OF_ANALYSIS_THREADS = 1179681
    r"""Specifies the maximum number of threads used for parallelism for the noise figure (NF) measurement.
    
    The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
    be used in calculations. The actual number of threads used depends on the problem size, system resources, data
    availability, and other considerations.
    
    The default value is 1.
    """

    NF_RESULTS_DUT_NOISE_FIGURE = 1179682
    r"""Returns an array of the noise figures of the DUT measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_DUT_NOISE_TEMPERATURE = 1179683
    r"""Returns an array of the equivalent thermal noise temperatures of the DUT measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in kelvin.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_DUT_GAIN = 1179684
    r"""Returns an array of the available gains of the DUT measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_ANALYZER_NOISE_FIGURE = 1179685
    r"""Returns an array of the noise figures of the analyzer measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_MEASUREMENT_Y_FACTOR = 1179686
    r"""Returns an array of the measurement Y-Factors measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. A valid result
    is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to
    **Y-Factor**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_CALIBRATION_Y_FACTOR = 1179687
    r"""Returns an array of the calibration Y-Factors measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. A valid result
    is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to
    **Y-Factor**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_Y_FACTOR_HOT_POWER = 1179688
    r"""Returns the array of powers measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is enabled. This value
    is expressed in dBm. A valid result is returned only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_Y_FACTOR_COLD_POWER = 1179689
    r"""Returns the array of powers measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is disabled. This value
    is expressed in dBm. A valid result is returned only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    NF_RESULTS_COLD_SOURCE_POWER = 1179690
    r"""Returns the power measured at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dBm. A valid
    result is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute
    to **Cold-source**.
    
    You do not need to use a selector string to read this result for default signal and result instance. Refer to
    the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals and results.
    """

    PHASENOISE_MEASUREMENT_ENABLED = 1245184
    r"""Specifies whether to enable the phase noise measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    PHASENOISE_RANGE_DEFINITION = 1245186
    r"""Specifies how the measurement computes offset subranges.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Auto**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Manual (0)   | Specify the offset sub-ranges used for the measurement. Use the PhaseNoise Range Start Freq attribute and the            |
    |              | PhaseNoise Range Stop Freq attribute to configure single or multiple range start and range stop frequencies.             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Auto (1)     | Measurement computes offset sub-ranges by dividing the user configured offset range into multiple decade sub-ranges.     |
    |              | The range is specified by the PhaseNoise Start Freq and the PhaseNoise Stop Freq attributes.                             |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    PHASENOISE_START_FREQUENCY = 1245187
    r"""Specifies the start frequency of the offset frequency range when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1000.
    """

    PHASENOISE_STOP_FREQUENCY = 1245188
    r"""Specifies the stop frequency of the offset frequency range when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1E+06.
    """

    PHASENOISE_RBW_PERCENTAGE = 1245189
    r"""Specifies the RBW as a percentage of the start frequency of each subrange when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """

    PHASENOISE_NUMBER_OF_RANGES = 1245192
    r"""Specifies the number of manual ranges.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    PHASENOISE_RANGE_START_FREQUENCY = 1245193
    r"""Specifies the start frequency for the specified subrange when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1000.
    """

    PHASENOISE_RANGE_STOP_FREQUENCY = 1245194
    r"""Specifies the stop frequency for the specified subrange when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1E+06.
    """

    PHASENOISE_RANGE_RBW_PERCENTAGE = 1245195
    r"""Specifies the RBW as a percentage of the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY`
    attribute of the specified subrange when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION`
    attribute to **Manual**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 10.
    """

    PHASENOISE_RANGE_AVERAGING_COUNT = 1245196
    r"""Specifies the averaging count for the specified subrange when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.
    
    Use "range<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 10.
    """

    PHASENOISE_AVERAGING_MULTIPLIER = 1245190
    r"""Specifies the factor by which you increase the averaging count for each range. This setting applies to both **Auto**
    and **Manual** range definitions.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    PHASENOISE_FFT_WINDOW = 1245191
    r"""Specifies the FFT window to use.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Hamming**.
    
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)        | Description                                                                                                              |
    +=====================+==========================================================================================================================+
    | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
    |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
    |                     | better frequency resolution for noise measurements.                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
    |                     | useful for time-frequency analysis.                                                                                      |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
    |                     | main lobe.                                                                                                               |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
    +---------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    PHASENOISE_SMOOTHING_TYPE = 1245197
    r"""Specifies the smoothing type used to smoothen the measured log plot trace.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Logarithmic**.
    
    +-----------------+-------------------------------------------------------------------------------------------+
    | Name (Value)    | Description                                                                               |
    +=================+===========================================================================================+
    | None (0)        | Smoothing is disabled.                                                                    |
    +-----------------+-------------------------------------------------------------------------------------------+
    | Linear (1)      | Performs linear moving average filtering on the measured phase noise log plot trace.      |
    +-----------------+-------------------------------------------------------------------------------------------+
    | Logarithmic (2) | Performs logarithmic moving average filtering on the measured phase noise log plot trace. |
    +-----------------+-------------------------------------------------------------------------------------------+
    | Median (3)      | Performs moving median filtering on the measured phase noise log plot trace.              |
    +-----------------+-------------------------------------------------------------------------------------------+
    """

    PHASENOISE_SMOOTHING_PERCENTAGE = 1245198
    r"""Specifies the number of trace points to use in the moving average filter as a percentage of total number of points in
    the log plot trace.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 2.
    """

    PHASENOISE_SPOT_NOISE_FREQUENCY_LIST = 1245199
    r"""Specifies an array of offset frequencies at which the phase noise is measured using the smoothed log plot trace.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    PHASENOISE_INTEGRATED_NOISE_RANGE_DEFINITION = 1245200
    r"""Specifies the frequency range for integrated noise measurements.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is ** Measurement**.
    
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)    | Description                                                                                                              |
    +=================+==========================================================================================================================+
    | None (0)        | Integrated noise measurement is not computed.                                                                            |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Measurement (1) | The complete log plot frequency range, considered as a single range, is used for computing integrated measurements.      |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    | Custom (2)      | The measurement range(s) specified by                                                                                    |
    |                 | PhaseNoise Integrated Noise Start Freq attribute and the PhaseNoise Integrated Noise Stop Freq attribute is used for     |
    |                 | computing integrated measurements.                                                                                       |
    +-----------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    PHASENOISE_INTEGRATED_NOISE_START_FREQUENCY = 1245201
    r"""Specifies an array of the start frequencies for integrated noise measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    PHASENOISE_INTEGRATED_NOISE_STOP_FREQUENCY = 1245202
    r"""Specifies an array of the stop frequencies for integrated noise measurement when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    PHASENOISE_SPUR_REMOVAL_ENABLED = 1245213
    r"""Specifies whether to remove spurs from the log plot trace.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+----------------------------------------------+
    | Name (Value) | Description                                  |
    +==============+==============================================+
    | False (0)    | Disables spur removal on the log plot trace. |
    +--------------+----------------------------------------------+
    | True (1)     | Enables spur removal on the log plot trace.  |
    +--------------+----------------------------------------------+
    """

    PHASENOISE_SPUR_REMOVAL_PEAK_EXCURSION = 1245214
    r"""Specifies the peak excursion to be used when spur detection is performed.
    
    Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
    information on spur removal.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 6.
    """

    PHASENOISE_CANCELLATION_ENABLED = 1245215
    r"""Specifies whether to enable or disable the phase noise cancellation.
    
    Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
    information on phase noise cancellation.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+------------------------------------+
    | Name (Value) | Description                        |
    +==============+====================================+
    | False (0)    | Disables phase noise cancellation. |
    +--------------+------------------------------------+
    | True (1)     | Enables phase noise cancellation.  |
    +--------------+------------------------------------+
    """

    PHASENOISE_CANCELLATION_THRESHOLD = 1245216
    r"""Specifies the minimum difference between the reference and pre-cancellation traces that must exist before cancellation
    is performed.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.01.
    """

    PHASENOISE_CANCELLATION_FREQUENCY = 1245217
    r"""Specifies an array of frequencies where the reference phase noise has been measured.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    PHASENOISE_CANCELLATION_REFERENCE_PHASE_NOISE = 1245218
    r"""Specifies an array of reference phase noise at the frequencies specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CANCELLATION_FREQUENCY` attribute .
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    """

    PHASENOISE_ALL_TRACES_ENABLED = 1245203
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the Phase Noise measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    PHASENOISE_RESULTS_CARRIER_POWER = 1245205
    r"""Returns the measured carrier power.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_CARRIER_FREQUENCY = 1245206
    r"""Returns the measured carrier frequency.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_SPOT_PHASE_NOISE = 1245207
    r"""Returns the phase noise corresponding to the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPOT_NOISE_FREQUENCY_LIST`
    attribute  by using the smoothed log plot trace.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_INTEGRATED_PHASE_NOISE = 1245208
    r"""Returns the integrated phase noise.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_INTEGRATED_NOISE_RESIDUAL_PM_IN_RADIAN = 1245209
    r"""Returns the residual PM in radians.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_INTEGRATED_NOISE_RESIDUAL_PM_IN_DEGREE = 1245210
    r"""Returns the residual PM in degrees.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_INTEGRATED_NOISE_RESIDUAL_FM = 1245211
    r"""Returns the residual FM in Hz.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PHASENOISE_RESULTS_INTEGRATED_NOISE_JITTER = 1245212
    r"""Returns the jitter in seconds.
    
    You do not need to use a selector string to read this attribute for the default signal instance. Refer to the
    `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
    about the string syntax for named signals.
    """

    PAVT_MEASUREMENT_ENABLED = 1077248
    r"""Specifies whether to enable the Phase Amplitude Versus Time (PAVT) measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    PAVT_MEASUREMENT_LOCATION_TYPE = 1077250
    r"""Specifies whether the location at which the segment is measured is indicated by time or trigger.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Time**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Time (0)     | The measurement is performed over a single record across multiple segments separated in time. The measurement locations  |
    |              | of the segments are specified by the PAVT Segment Start Time attribute. The number of segments is equal to the number    |
    |              | of segment start times.                                                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Trigger (1)  | The measurement is performed across segments obtained in multiple records, where each record is obtained when a trigger  |
    |              | is received. The number of segments is equal to the number of triggers (records).                                        |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    PAVT_MEASUREMENT_BANDWIDTH = 1077261
    r"""Specifies the bandwidth over which the signal is measured. This value is expressed in Hz.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10 MHz.
    """

    PAVT_MEASUREMENT_INTERVAL_MODE = 1077269
    r"""Specifies the mode of configuring the measurement interval.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **Uniform**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Uniform (0)  | The time offset from the start of segment and the duration over which the measurement is performed is uniform for all    |
    |              | segments and is given by the PAVT Meas Offset attribute and the PAVT Meas Length attribute respectively.                 |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Variable (1) | The time offset from the start of segment and the duration over which the measurement is performed is configured         |
    |              | separately for each segment and is given by the PAVT Segment Meas Offset attribute and the PAVT Segment Meas Length      |
    |              | attribute respectively.                                                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    PAVT_NUMBER_OF_SEGMENTS = 1077251
    r"""Specifies the number of segments to be measured.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    PAVT_SEGMENT_TYPE = 1077264
    r"""Specifies the type of segment.
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is **Phase and Amplitude**.
    
    +---------------------------------+--------------------------------------------------+
    | Name (Value)                    | Description                                      |
    +=================================+==================================================+
    | Phase and Amplitude (0)         | Phase and amplitude is measured in this segment. |
    +---------------------------------+--------------------------------------------------+
    | Amplitude (1)                   | Amplitude is measured in this segment.           |
    +---------------------------------+--------------------------------------------------+
    | Frequency Error Measurement (2) | Frequency error is measured in this segment.     |
    +---------------------------------+--------------------------------------------------+
    """

    PAVT_SEGMENT_START_TIME = 1077252
    r"""Specifies the start time of measurement of the segments. This value is expressed in seconds. You can use this attribute
    only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LOCATION_TYPE` attribute to **Time**.
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    PAVT_MEASUREMENT_OFFSET = 1077253
    r"""Specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
    error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.
    """

    PAVT_MEASUREMENT_LENGTH = 1077254
    r"""Specifies the duration within the segment over which the phase and amplitude, amplitude, or frequency error values are
    computed. This value is expressed in seconds. This attribute is valid only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1 millisecond.
    """

    PAVT_SEGMENT_MEASUREMENT_OFFSET = 1077265
    r"""Specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
    error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 0.
    """

    PAVT_SEGMENT_MEASUREMENT_LENGTH = 1077266
    r"""Specifies the duration within each segment over which the phase and amplitude, amplitude, or frequency error values are
    computed. This value is expressed in seconds. This attribute is valid when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.
    
    The default value is 1 millisecond.
    """

    PAVT_PHASE_UNWRAP_ENABLED = 1077267
    r"""Specifies whether the phase measurement results are unwrapped or wrapped.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------+
    | Name (Value) | Description                                                  |
    +==============+==============================================================+
    | False (0)    | Phase measurement results are wrapped within +/-180 degrees. |
    +--------------+--------------------------------------------------------------+
    | True (1)     | Phase measurement results are unwrapped.                     |
    +--------------+--------------------------------------------------------------+
    """

    PAVT_FREQUENCY_OFFSET_CORRECTION_ENABLED = 1077260
    r"""Specifies whether to enable frequency offset correction for the measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | False (0)    | Disables the frequency offset correction.                                                                                |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables the frequency offset correction. The measurement computes and corrects any frequency offset between the          |
    |              | reference and the acquired waveforms.                                                                                    |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    PAVT_FREQUENCY_TRACKING_ENABLED = 1077270
    r"""Specifies whether to enable frequency offset correction per segment for the measurement. While you set this attribute
    to **True**, ensure that the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_OFFSET_CORRECTION_ENABLED`
    attribute is set to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_TYPE` attribute is set to
    **Phase and Amplitude**.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is **False**.
    
    +--------------+------------------------------------------------------------------------------------------------------+
    | Name (Value) | Description                                                                                          |
    +==============+======================================================================================================+
    | False (0)    | Disables the drift correction for the measurement.                                                   |
    +--------------+------------------------------------------------------------------------------------------------------+
    | True (1)     | Enables the drift correction. The measurement corrects and reports the frequency offset per segment. |
    +--------------+------------------------------------------------------------------------------------------------------+
    """

    PAVT_ALL_TRACES_ENABLED = 1077255
    r"""Specifies whether to enable the traces to be stored and retrieved after performing the PAVT measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    PAVT_RESULTS_MEAN_RELATIVE_PHASE = 1077258
    r"""Returns the mean phase of the segment, relative to the phase of the reference segment. This value is expressed in
    degrees.
    
    Mean Relative Phase = Q\ :sub:`i`\ - Q\ :sub:`r`\
    
    Q\ :sub:`i`\ is the absolute phase of the segment i, expressed in degrees
    
    Q\ :sub:`r`\ is the absolute phase of the reference segment r, expressed in degrees
    
    where,
    r = 1, if Segment0 is configured as Frequency Error Measurement segment
    r = 0, otherwise
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    PAVT_RESULTS_MEAN_RELATIVE_AMPLITUDE = 1077259
    r"""Returns the mean amplitude of the segment, relative to the amplitude of the reference segment. This value is expressed
    in dB.
    
    Mean Relative Amplitude = a\ :sub:`i`\ - a\ :sub:`r`\
    
    a\ :sub:`i`\ is the absolute amplitude of the segment i, expressed in dBm
    
    a\ :sub:`r`\ is the absolute amplitude of the reference segment r, expressed in dBm
    
    where,
    r = 1, if Segment0 is configured as Frequency Error Measurement segment
    r = 0, otherwise
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    PAVT_RESULTS_MEAN_ABSOLUTE_PHASE = 1077263
    r"""Returns the mean absolute phase of the segment. This value is expressed in degrees.
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    PAVT_RESULTS_MEAN_ABSOLUTE_AMPLITUDE = 1077262
    r"""Returns the mean absolute amplitude of the segment. This value is expressed in dBm.
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    PAVT_RESULTS_FREQUENCY_ERROR_MEAN = 1077268
    r"""Returns the mean frequency error of the segment. This value is expressed in Hz
    
    Use "segment<*n*>" as the `Selector String
    <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.
    """

    POWERLIST_MEASUREMENT_ENABLED = 1376256
    r"""Specifies whether to enable the PowerList measurement.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is FALSE.
    """

    POWERLIST_NUMBER_OF_SEGMENTS = 1376258
    r"""Specifies the number of segments to be measured.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 1.
    """

    POWERLIST_SEGMENT_LENGTH = 1376259
    r"""Specifies an array of durations, each corresponding to a segment, where each value must be at least the sum of
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_LENGTH` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_OFFSET` when the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute is set to **TimerEvent**. This
    value is expressed in seconds.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    POWERLIST_SEGMENT_FREQUENCY = 1376260
    r"""Specifies an array of expected carrier frequencies for the RF signal to be acquired, each corresponding to a segment,
    to which the signal analyzer tunes. This value is expressed in Hz.
    
    RFmx returns an error if this attribute is not configured or if the size of the configured values is smaller
    than the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    POWERLIST_SEGMENT_REFERENCE_LEVEL = 1376261
    r"""Specifies an array of reference levels, each representing the maximum expected power of the RF input signal for its
    corresponding segment. This value is configured in dBm for RF devices.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    POWERLIST_SEGMENT_MEASUREMENT_LENGTH = 1376262
    r"""Specifies an array of durations, each corresponding to a segment, over which the power value is computed. This value is
    expressed in seconds.
    
    RFmx returns an error if this attribute is not configured or if the size of the configured values is smaller
    than the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    POWERLIST_SEGMENT_MEASUREMENT_OFFSET = 1376263
    r"""Specifies an array of time offsets from the start of each segment, over which the power value is computed. This value
    is expressed in seconds.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is an empty array.
    """

    POWERLIST_SEGMENT_RBW_FILTER_BANDWIDTH = 1376264
    r"""Specifies an array of bandwidth of the resolution bandwidth (RBW) filters used to measure the signal corresponding to
    each segment. This value is expressed in Hz.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 100 kHz. RFmx applies this default value for all segments when the attribute is either
    unconfigured or reset to its default.
    """

    POWERLIST_SEGMENT_RBW_FILTER_TYPE = 1376265
    r"""Specifies an array of digital resolution bandwidth (RBW) filter shapes, each corresponding to a segment.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (value) | Description                                                                                                              |
    +==============+==========================================================================================================================+
    | Gaussian (1) | The RBW filter has a Gaussian response.                                                                                  |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | Flat (2)     | The RBW filter has a flat response.                                                                                      |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | None (5)     | The measurement does not use any RBW filtering.                                                                          |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    | RRC (6)      | The RRC filter with the roll-off specified by the                                                                        |
    |              | :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_RBW_FILTER_ALPHA` attribute is used as the RBW filter.            |
    +--------------+--------------------------------------------------------------------------------------------------------------------------+
    
    The default value is **Gaussian**. RFmx applies this default value for all segments when the attribute is
    either unconfigured or reset to its default.
    """

    POWERLIST_SEGMENT_RBW_FILTER_ALPHA = 1376266
    r"""Specifies an array of roll-off factor for the root-raised-cosine (RRC) filter, each corresponding to a segment.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 0.1. RFmx applies this default value for all segments when the attribute is either
    unconfigured or reset to its default.
    """

    POWERLIST_SEGMENT_TRIGGER_TYPE = 1376267
    r"""Specifies an array of trigger type, each corresponding to a segment.
    
    RFmx returns an error if the size of the configured values is smaller than the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (value)      | Description                                                                                                              |
    +===================+==========================================================================================================================+
    | None (0)          | No Reference Trigger is configured.                                                                                      |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Digital Edge (1)  | The Reference Trigger is not asserted until a digital edge is detected. The source of the digital edge is specified      |
    |                   | using the :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute.                         |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    | IQ Power Edge (2) | The Reference Trigger is asserted when the signal changes past the level specified by the slope (rising or falling),     |
    |                   | which is configured using the the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE`            |
    |                   | attribute.                                                                                                               |
    +-------------------+--------------------------------------------------------------------------------------------------------------------------+
    
    The default value is **None**. RFmx applies this default value for all segments when the attribute is either
    unconfigured or reset to its default.
    """

    POWERLIST_RESULTS_MEAN_ABSOLUTE_POWER = 1376268
    r"""Returns an array of mean absolute power of the signal, each corresponding to a segment. This value is expressed in dBm.
    
    You do not need to use a selector string to read this result for the default signal and result instance. Refer
    to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals and results.
    """

    POWERLIST_RESULTS_MAXIMUM_POWER = 1376269
    r"""Returns an array of maximum power of the signal, each corresponding to a segment. This value is expressed in dBm.
    
    You do not need to use a selector string to read this result for the default signal and result instance. Refer
    to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals and results.
    """

    POWERLIST_RESULTS_MINIMUM_POWER = 1376270
    r"""Returns an array of minimum power of the signal, each corresponding to a segment. This value is expressed in dBm.
    
    You do not need to use a selector string to read this result for the default signal and result instance. Refer
    to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals and results.
    """

    AUTO_LEVEL_INITIAL_REFERENCE_LEVEL = 1048589
    r"""Specifies the initial reference level, in dBm, which the :py:meth:`auto_level` method uses to estimate the peak power
    of the input signal.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 30.
    """

    LIMITED_CONFIGURATION_CHANGE = 1048590
    r"""Specifies the set of attributes that are considered by RFmx in the locked signal configuration state.
    
    If your test system performs the same measurement at different selected ports, multiple frequencies and/or
    power levels repeatedly, enabling this attribute will help achieve faster measurements. When you set this attribute to
    a value other than **Disabled**, the RFmx driver will use an optimized code path and skip some checks. Because RFmx
    skips some checks when you use this attribute, you need to be aware of the limitations of this feature, which are
    listed in the `limitations <www.ni.com/docs/en-US/bundle/rfmx-specan/page/limitations.html>`_ topic.
    
    You can also use this attribute to lock a specific instrument configuration for a signal so that every time
    that you initiate the signal, RFmx applies the RFmxInstr attributes from a locked configuration.
    
    NI recommends you use this attribute in conjunction with named signal configurations. Create named signal
    configurations for each measurement configuration in your test program and set this attribute to a value other than
    **Disabled** for one or more of the named signal configurations. This allows RFmx to precompute the acquisition
    settings for your measurement configurations and re-use the precomputed settings each time you initiate the
    measurement. You do not need to use this attribute if you create named signals for all the measurement configurations
    in your test program during test sequence initialization and do not change any RFInstr or personality attributes while
    testing each device under test. RFmx automatically optimizes that use case.
    
    Specify the named signal configuration you are setting this attribute in the selector string input.  You do not
    need to use a selector string to configure or read this attribute for the default signal instance. Refer to the
    Selector String topic for information about the string syntax for named signals.
    
    The default value is **Disabled**.
    
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Name (Value)                           | Description                                                                                                              |
    +========================================+==========================================================================================================================+
    | Disabled (0)                           | This is the normal mode of RFmx operation. All configuration changes in RFmxInstr attributes or in personality           |
    |                                        | attributes will be applied during RFmx Commit.                                                                           |
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | No Change (1)                          | Signal configuration and RFmxInstr configuration are locked after the first Commit or Initiate of the named signal       |
    |                                        | configuration. Any configuration change thereafter either in RFmxInstr attributes or personality attributes will not be  |
    |                                        | considered by subsequent RFmx Commits or Initiates of this signal.                                                       |
    |                                        | Use No Change if you have created named signal configurations for all measurement configurations but are setting some    |
    |                                        | RFmxInstr attributes. Refer to the Limitations of the Limited Configuration Change Property topic for more details       |
    |                                        | about the limitations of using this mode.                                                                                |
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Frequency (2)                          | Signal configuration, other than center frequency, external attenuation, and RFInstr configuration, is locked after      |
    |                                        | first Commit or Initiate of the named signal configuration. Thereafter, only the Center Frequency and External           |
    |                                        | Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of this signal.         |
    |                                        | Refer to the Limitations of the Limited Configuration Change Property topic for more details about the limitations of    |
    |                                        | using this mode.                                                                                                         |
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Reference Level (3)                    | Signal configuration, other than the reference level and RFInstr configuration, is locked after first Commit or          |
    |                                        | Initiate of the named signal configuration. Thereafter only the Reference Level attribute value change will be           |
    |                                        | considered by subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ     |
    |                                        | Power Edge Trigger, NI recommends that you set the IQ Power Edge Level Type to Relative so that the trigger level is     |
    |                                        | automatically adjusted as you adjust the reference level. Refer to the Limitations of the Limited Configuration Change   |
    |                                        | Property topic for more details about the limitations of using this mode.                                                |
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Freq and Ref Level (4)                 | Signal configuration, other than center frequency, reference level, external attenuation, and RFInstr configuration, is  |
    |                                        | locked after first Commit or Initiate of the named signal configuration. Thereafter only Center Frequency, Reference     |
    |                                        | Level, and External Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of  |
    |                                        | this signal. If you have configured this signal to use an IQ Power Edge Trigger, NI recommends you set the IQ Power      |
    |                                        | Edge Level Type to Relative so that the trigger level is automatically adjusted as you adjust the reference level.       |
    |                                        | Refer to the Limitations of the Limited Configuration Change Property topic for more details about the limitations of    |
    |                                        | using this mode.                                                                                                         |
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Selected Ports, Freq and Ref Level (5) | Signal configuration, other than Selected Ports, Center frequency, Reference level, External attenuation, and RFInstr    |
    |                                        | configuration, is locked after first Commit or Initiate of the named signal configuration. Thereafter only Selected      |
    |                                        | Ports, Center Frequency, Reference Level, and External Attenuation attribute value changes will be considered by         |
    |                                        | subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ Power Edge        |
    |                                        | Trigger, NI recommends you set the IQ Power Edge Level Type to Relative so that the trigger level is automatically       |
    |                                        | adjusted as you adjust the reference level. Refer to the Limitations of the Limited Configuration Change Property topic  |
    |                                        | for more details about the limitations of using this mode.                                                               |
    +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
    """

    SELECTED_PATH = 1048591
    r"""
    """

    RESULT_FETCH_TIMEOUT = 1097728
    r"""Specifies the time, in seconds, to wait before results are available in the RFmxSpecAn Attribute. Set this value to a
    time longer than expected for fetching the measurement. A value of -1 specifies that the RFmxSpecAn Attribute waits
    until the measurement is complete.
    
    You do not need to use a selector string to configure or read this attribute for the default signal instance.
    Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
    information about the string syntax for named signals.
    
    The default value is 10.
    """
