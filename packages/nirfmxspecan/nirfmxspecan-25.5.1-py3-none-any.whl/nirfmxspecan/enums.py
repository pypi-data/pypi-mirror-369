"""enums.py - Contains enum classes."""

from enum import Enum, IntFlag


class TriggerType(Enum):
    """TriggerType."""

    NONE = 0
    r"""No Reference Trigger is configured."""

    DIGITAL_EDGE = 1
    r"""The Reference Trigger is not asserted until a digital edge is detected. The source of the digital edge is specified
    using the :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute."""

    IQ_POWER_EDGE = 2
    r"""The Reference Trigger is asserted when the signal changes past the level specified by the slope (rising or falling),
    which is configured using the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE` attribute."""

    SOFTWARE = 3
    r"""The Reference Trigger is not asserted until a software trigger occurs."""


class DigitalEdgeTriggerEdge(Enum):
    """DigitalEdgeTriggerEdge."""

    RISING_EDGE = 0
    r"""The trigger asserts on the rising edge of the signal."""

    FALLING_EDGE = 1
    r"""The trigger asserts on the falling edge of the signal."""


class IQPowerEdgeTriggerLevelType(Enum):
    """IQPowerEdgeTriggerLevelType."""

    RELATIVE = 0
    r"""The IQ Power Edge Level attribute is relative to the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute."""

    ABSOLUTE = 1
    r"""The IQ Power Edge Level attribute specifies the absolute power."""


class IQPowerEdgeTriggerSlope(Enum):
    """IQPowerEdgeTriggerSlope."""

    RISING_SLOPE = 0
    r"""The trigger asserts when the signal power is rising."""

    FALLING_SLOPE = 1
    r"""The trigger asserts when the signal power is falling."""


class TriggerMinimumQuietTimeMode(Enum):
    """TriggerMinimumQuietTimeMode."""

    MANUAL = 0
    r"""The minimum quiet time for triggering is the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_MINIMUM_QUIET_TIME_DURATION` attribute."""

    AUTO = 1
    r"""The measurement computes the minimum quiet time used for triggering."""


class AcpCarrierMode(Enum):
    """AcpCarrierMode."""

    PASSIVE = 0
    r"""The carrier power is not considered as part of the total carrier power."""

    ACTIVE = 1
    r"""The carrier power is considered as part of the total carrier power."""


class AcpCarrierRrcFilterEnabled(Enum):
    """AcpCarrierRrcFilterEnabled."""

    FALSE = 0
    r"""The channel power of the acquired carrier channel is measured directly."""

    TRUE = 1
    r"""The measurement applies the RRC filter on the acquired carrier channel before measuring the carrier channel power."""


class AcpOffsetEnabled(Enum):
    """AcpOffsetEnabled."""

    FALSE = 0
    r"""Disables the offset channel for ACP measurement."""

    TRUE = 1
    r"""Enables the offset channel for ACP measurement."""


class AcpOffsetSideband(Enum):
    """AcpOffsetSideband."""

    NEGATIVE = 0
    r"""Configures a lower offset segment to the left of the leftmost carrier."""

    POSITIVE = 1
    r"""Configures an upper offset segment to the right of the rightmost carrier."""

    BOTH = 2
    r"""Configures both negative and positive offset segments."""


class AcpOffsetPowerReferenceCarrier(Enum):
    """AcpOffsetPowerReferenceCarrier."""

    CLOSEST = 0
    r"""The measurement uses the power measured in the carrier closest to the offset channel center frequency, as the power
    reference."""

    HIGHEST = 1
    r"""The measurement uses the highest power measured among all the active carriers as the power reference."""

    COMPOSITE = 2
    r"""The measurement uses the sum of powers measured in all the active carriers as the power reference."""

    SPECIFIC = 3
    r"""The measurement uses the power measured in the carrier that has an index specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_SPECIFIC` attribute, as the power reference."""


class AcpOffsetRrcFilterEnabled(Enum):
    """AcpOffsetRrcFilterEnabled."""

    FALSE = 0
    r"""The channel power of the acquired offset channel is measured directly."""

    TRUE = 1
    r"""The measurement applies the RRC filter on the acquired offset channel before measuring the offset channel power."""


class AcpOffsetFrequencyDefinition(Enum):
    """AcpOffsetFrequencyDefinition."""

    CENTER = 0
    r"""The offset frequency is defined from the center of the closest carrier to the center of the offset channel."""

    EDGE = 1
    r"""The offset frequency is defined from the center of the closest carrier to the nearest edge of the offset channel."""


class AcpRbwAutoBandwidth(Enum):
    """AcpRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class AcpRbwFilterType(Enum):
    """AcpRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""An RBW filter with a Gaussian response is applied."""

    FLAT = 2
    r"""An RBW filter with a flat response is applied."""


class AcpRbwFilterBandwidthDefinition(Enum):
    """AcpRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3dB bandwidth of
    the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the bin width of the spectrum computed using FFT when you set the ACP RBW Filter Type
    attribute to **FFT Based**."""


class AcpSweepTimeAuto(Enum):
    """AcpSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement calculates the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""


class AcpDetectorType(Enum):
    """AcpDetectorType."""

    NONE = 0
    r"""The detector is disabled."""

    SAMPLE = 1
    r"""The middle sample in the bucket is detected."""

    NORMAL = 2
    r"""The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If
    the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in
    alternate buckets."""

    PEAK = 3
    r"""The maximum value of the samples in the bucket is detected."""

    NEGATIVE_PEAK = 4
    r"""The minimum value of the samples in the bucket is detected."""

    AVERAGE_RMS = 5
    r"""The average RMS of all the samples in the bucket is detected."""

    AVERAGE_VOLTAGE = 6
    r"""The average voltage of all the samples in the bucket is detected."""

    AVERAGE_LOG = 7
    r"""The average log of all the samples in the bucket is detected."""


class AcpPowerUnits(Enum):
    """AcpPowerUnits."""

    DBM = 0
    r"""The absolute powers are reported in dBm."""

    DBM_PER_HZ = 1
    r"""The absolute powers are reported in dBm/Hz."""


class AcpMeasurementMethod(Enum):
    """AcpMeasurementMethod."""

    NORMAL = 0
    r"""The ACP measurement acquires the spectrum using the same signal analyzer setting across frequency bands. Use this
    method when measurement speed is desirable over higher dynamic range."""

    DYNAMIC_RANGE = 1
    r"""The ACP measurement acquires the spectrum using the hardware-specific optimizations for different frequency bands. Use
    this method to get the best dynamic range.
    
    **Supported devices**: PXIe-5665/5668"""

    SEQUENTIAL_FFT = 2
    r"""The ACP measurement acquires I/Q samples for a duration specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute. These samples are divided into smaller
    chunks. The size of each chunk is defined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE`
    attribute. The overlap between the chunks is defined by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute. FFT is computed on each of these chunks.
    The resultant FFTs are averaged to get the spectrum and is used to compute ACP.
    
    Sequential FFT method should be used for the following scenarios.
    
    #. While performing fast ACP measurements by utilizing smaller FFT sizes. However, accuracy of the results may be reduced.
    
    #. When measuring signals with time-varying spectral characteristics, sequential FFT with overlap mode set to Automatic should be used.
    
    #. For accurate power measurements when the power characteristics of the signal vary over time, averaging is allowed.
    
    The following attributes have limited support when you set the ACP Measurement Method attribute to **Sequential
    FFT**.
    
    +-----------------------------------------------------------------------------+---------------------+
    | Property                                                                    | Supported Value     |
    +=============================================================================+=====================+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH`   | True                |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_TYPE`             | FFT Based           |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO`             | False               |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT`             | >=1                 |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_ANALYSIS_THREADS`  | 1                   |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.AMPLITUDE_CORRECTION_TYPE`   | RF Center Frequency |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_ATTENUATION` | 0                   |
    +-----------------------------------------------------------------------------+---------------------+
    
    .. note::
       For multi-span FFT, the averaging count should be 1."""


class AcpNoiseCalibrationMode(Enum):
    """AcpNoiseCalibrationMode."""

    MANUAL = 0
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` attribute to **Calibrate Noise
    Floor**, you can initiate instrument noise calibration for the ACP measurement manually. When you set the ACP Meas Mode
    attribute to **Measure**, you can initiate the ACP measurement manually."""

    AUTO = 1
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_COMPENSATION_ENABLED` to **True**, RFmx sets the
    :py:attr:`~nirfmxinstr.attribute.AttributeID.INPUT_ISOLATION_ENABLED` attribute to **Enabled** and calibrates the
    instrument noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled attribute and
    performs the ACP measurement, including compensation for noise of the instrument. RFmx skips noise calibration in this
    mode if valid noise calibration data is already cached. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_COMPENSATION_ENABLED` attribute to **False**, RFmx does not
    calibrate instrument noise and only performs the ACP measurement without compensating for noise of the instrument."""


class AcpNoiseCalibrationAveragingAuto(Enum):
    """AcpNoiseCalibrationAveragingAuto."""

    FALSE = 0
    r"""RFmx uses the averages that you set for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_COUNT` attribute."""

    TRUE = 1
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Normal** or
    **Sequential FFT**, RFmx uses a noise calibration averaging count of 32. When you set the ACP Meas Method attribute to
    **Dynamic Range** and the sweep time is less than 5 ms, RFmx uses a noise calibration averaging count of 15. When you
    set the ACP Meas Method attribute to **Dynamic Range** and the sweep time is greater than or equal to 5 ms, RFmx uses a
    noise calibration averaging count of 5."""


class AcpNoiseCompensationEnabled(Enum):
    """AcpNoiseCompensationEnabled."""

    FALSE = 0
    r"""Disables noise compensation."""

    TRUE = 1
    r"""Enables noise compensation."""


class AcpNoiseCompensationType(Enum):
    """AcpNoiseCompensationType."""

    ANALYZER_AND_TERMINATION = 0
    r"""Compensates for noise from the analyzer and the 50-ohm termination. The measured power values are in excess of the
    thermal noise floor."""

    ANALYZER_ONLY = 1
    r"""Compensates for the analyzer noise only."""


class AcpAveragingEnabled(Enum):
    """AcpAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The ACP measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the ACP measurement is averaged."""


class AcpAveragingType(Enum):
    """AcpAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class AcpMeasurementMode(Enum):
    """AcpMeasurementMode."""

    MEASURE = 0
    r"""ACP measurement is performed on the acquired signal."""

    CALIBRATE_NOISE_FLOOR = 1
    r"""Manual noise calibration of the signal analyzer is performed for the ACP measurement."""


class AcpFftWindow(Enum):
    """AcpFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is
    useful for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class AcpFftOverlapMode(Enum):
    """AcpFftOverlapMode."""

    DISABLED = 0
    r"""Disables the overlap between the chunks."""

    AUTOMATIC = 1
    r"""Measurement sets the overlap based on the value you have set for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute. When you set the ACP FFT Window attribute to any
    value other than **None**, the number of overlapped samples between consecutive chunks is set to 50% of the value of
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute. When you set the ACP FFT Window
    attribute to **None**, the chunks are not overlapped and the overlap is set to 0%."""

    USER_DEFINED = 2
    r"""Measurement uses the overlap that you specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP`
    attribute."""


class AcpIFOutputPowerOffsetAuto(Enum):
    """AcpIFOutputPowerOffsetAuto."""

    FALSE = 0
    r"""The measurement sets the IF output power level offset using the values of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NEAR_IF_OUTPUT_POWER_OFFSET` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FAR_IF_OUTPUT_POWER_OFFSET` attributes."""

    TRUE = 1
    r"""The measurement automatically computes an IF output power level offset for the offset channels to improve the dynamic
    range of the ACP measurement."""


class AcpAmplitudeCorrectionType(Enum):
    """AcpAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class CcdfRbwFilterType(Enum):
    """CcdfRbwFilterType."""

    NONE = 5
    r"""The measurement does not use any RBW filtering."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter has a flat response."""

    RRC = 6
    r"""The RRC filter with the roll-off specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_RRC_ALPHA`
    attribute is used as the RBW filter."""


class CcdfThresholdEnabled(Enum):
    """CcdfThresholdEnabled."""

    FALSE = 0
    r"""All samples are considered for the CCDF measurement."""

    TRUE = 1
    r"""The samples above the threshold level specified in the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_LEVEL`
    attribute are considered for the CCDF measurement."""


class CcdfThresholdType(Enum):
    """CcdfThresholdType."""

    RELATIVE = 0
    r"""The threshold is relative to the peak power of the acquired samples."""

    ABSOLUTE = 1
    r"""The threshold is the absolute power, in dBm."""


class ChpCarrierRrcFilterEnabled(Enum):
    """ChpCarrierRrcFilterEnabled."""

    FALSE = 0
    r"""The channel power of the acquired channel is measured directly."""

    TRUE = 1
    r"""The measurement applies the RRC filter on the acquired channel before measuring the channel power."""


class ChpRbwAutoBandwidth(Enum):
    """ChpRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class ChpRbwFilterType(Enum):
    """ChpRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""An RBW filter with a Gaussian response is applied."""

    FLAT = 2
    r"""An RBW filter with a flat response is applied."""


class ChpRbwFilterBandwidthDefinition(Enum):
    """ChpRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3 dB bandwidth
    of the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the CHP RBW Filter Type attribute
    to **FFT Based**."""


class ChpSweepTimeAuto(Enum):
    """ChpSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement calculates the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""


class ChpDetectorType(Enum):
    """ChpDetectorType."""

    NONE = 0
    r"""The detector is disabled."""

    SAMPLE = 1
    r"""The middle sample in the bucket is detected."""

    NORMAL = 2
    r"""The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If
    the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in
    alternate buckets."""

    PEAK = 3
    r"""The maximum value of the samples in the bucket is detected."""

    NEGATIVE_PEAK = 4
    r"""The minimum value of the samples in the bucket is detected."""

    AVERAGE_RMS = 5
    r"""The average RMS of all the samples in the bucket is detected."""

    AVERAGE_VOLTAGE = 6
    r"""The average voltage of all the samples in the bucket is detected."""

    AVERAGE_LOG = 7
    r"""The average log of all the samples in the bucket is detected."""


class ChpNoiseCalibrationMode(Enum):
    """ChpNoiseCalibrationMode."""

    MANUAL = 0
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` attribute to **Calibrate Noise
    Floor**, you can initiate instrument noise calibration for the CHP measurement manually. When you set the CHP Meas Mode
    attribute to **Measure**, you can initiate the CHP measurement manually."""

    AUTO = 1
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_COMPENSATION_ENABLED` attribute to **True**, RFmx
    sets :py:attr:`~nirfmxinstr.attribute.AttributeID.INPUT_ISOLATION_ENABLED` to **Enabled** and calibrates the intrument
    noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled attribute and performs the
    CHP measurement, including compensation for noise of the instrument. RFmx skips noise calibration in this mode if valid
    noise calibration data is already cached. When you set the CHP Noise Comp Enabled attribute to **False**, RFmx does not
    calibrate instrument noise and performs only the CHP measurement without compensating for the noise contribution of the
    instrument."""


class ChpNoiseCalibrationAveragingAuto(Enum):
    """ChpNoiseCalibrationAveragingAuto."""

    FALSE = 0
    r"""RFmx uses the averages that you set for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_COUNT` attribute."""

    TRUE = 1
    r"""RFmx uses a noise calibration averaging count of 32."""


class ChpNoiseCompensationEnabled(Enum):
    """ChpNoiseCompensationEnabled."""

    FALSE = 0
    r"""Disables noise compensation."""

    TRUE = 1
    r"""Enables noise compensation."""


class ChpNoiseCompensationType(Enum):
    """ChpNoiseCompensationType."""

    ANALYZER_AND_TERMINATION = 0
    r"""Compensates for noise from the analyzer and the 50 ohm termination. The measured power values are in excess of the
    thermal noise floor."""

    ANALYZER_ONLY = 1
    r"""Compensates for the analyzer noise only."""


class ChpAveragingEnabled(Enum):
    """ChpAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The CHP measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the CHP measurement is averaged."""


class ChpAveragingType(Enum):
    """ChpAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class ChpMeasurementMode(Enum):
    """ChpMeasurementMode."""

    MEASURE = 0
    r"""CHP measurement is performed on the acquired signal."""

    CALIBRATE_NOISE_FLOOR = 1
    r"""Manual noise calibration of the signal analyzer is performed for the CHP measurement."""


class ChpFftWindow(Enum):
    """ChpFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is
    useful for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class ChpAmplitudeCorrectionType(Enum):
    """ChpAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class FcntRbwFilterType(Enum):
    """FcntRbwFilterType."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter has a flat response."""

    NONE = 5
    r"""The measurement does not use any RBW filtering."""

    RRC = 6
    r"""The RRC filter with the roll-off specified by :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_RRC_ALPHA`
    attribute is used as the RBW filter."""


class FcntThresholdEnabled(Enum):
    """FcntThresholdEnabled."""

    FALSE = 0
    r"""All samples are considered for the FCnt measurement."""

    TRUE = 1
    r"""The samples above the threshold level specified in the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_LEVEL`
    attribute are considered for the FCnt measurement."""


class FcntThresholdType(Enum):
    """FcntThresholdType."""

    RELATIVE = 0
    r"""The threshold is relative to the peak power of the acquired samples."""

    ABSOLUTE = 1
    r"""The threshold is the absolute power, in dBm."""


class FcntAveragingEnabled(Enum):
    """FcntAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The FCnt measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute as the number
    of acquisitions over which the FCnt measurement is averaged."""


class FcntAveragingType(Enum):
    """FcntAveragingType."""

    MAXIMUM = 3
    r"""The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement."""

    MINIMUM = 4
    r"""The minimum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement."""

    MEAN = 6
    r"""The mean of the instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement."""

    MINMAX = 7
    r"""The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement. The
    sign of the phase difference is ignored to find the maximum instantaneous value."""


class HarmRbwFilterType(Enum):
    """HarmRbwFilterType."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter  has a flat response."""

    NONE = 5
    r"""The measurement does not use any RBW filtering."""

    RRC = 6
    r"""The RRC filter with the roll-off specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FUNDAMENTAL_RBW_FILTER_ALPHA` attribute is used as the RBW filter."""


class HarmAutoHarmonicsSetupEnabled(Enum):
    """HarmAutoHarmonicsSetupEnabled."""

    FALSE = 0
    r"""The measurement uses manual configuration for the harmonic order, harmonic bandwidth, and harmonic measurement
    interval."""

    TRUE = 1
    r"""The measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_HARMONICS` attribute and
    configuration of the fundamental to configure successive harmonics.
    
    Bandwidth of Nth order harmonic = N * (Bandwidth of fundamental).
    
    Measurement interval of Nth order harmonics = (Measurement interval of fundamental)/N"""


class HarmHarmonicEnabled(Enum):
    """HarmHarmonicEnabled."""

    FALSE = 0
    r"""Disables the harmonic for measurement."""

    TRUE = 1
    r"""Enables the harmonic for measurement."""


class HarmMeasurementMethod(Enum):
    """HarmMeasurementMethod."""

    TIME_DOMAIN = 0
    r"""The harmonics measurement acquires the signal using the same signal analyzer setting across frequency bands. Use this
    method when the measurement speed is desirable over higher dynamic range.
    
    **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5665/5668"""

    DYNAMIC_RANGE = 2
    r"""The harmonics measurement acquires the signal using the hardware-specific features, such as the IF filter and IF gain,
    for different frequency bands. Use this method to get the best dynamic range.
    
    **Supported devices**: PXIe-5665/5668"""


class HarmNoiseCompensationEnabled(Enum):
    """HarmNoiseCompensationEnabled."""

    FALSE = 0
    r"""Disables compensation of the average harmonic powers for the noise floor of the signal analyzer."""

    TRUE = 1
    r"""Enables compensation of the average harmonic powers for the noise floor of the signal analyzer. The noise floor of the
    signal analyzer is measured for the RF path used by the harmonics measurement and cached for future use. If the signal
    analyzer or measurement parameters change, noise floors are measured again.
    
    **Supported devices**: PXIe-5663/5665/5668"""


class HarmAveragingEnabled(Enum):
    """HarmAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The Harmonics measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the
    number of acquisitions over which the Harmonics measurement is averaged."""


class HarmAveragingType(Enum):
    """HarmAveragingType."""

    RMS = 0
    r"""The power trace is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power trace is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power trace is averaged."""

    MAXIMUM = 3
    r"""The maximum instantaneous power in the power trace is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The minimum instantaneous power in the power trace is retained from one acquisition to the next."""


class ObwPowerUnits(Enum):
    """ObwPowerUnits."""

    DBM = 0
    r"""The absolute powers are reported in dBm."""

    DBM_PER_HZ = 1
    r"""The absolute powers are reported in dBm/Hz."""


class ObwRbwAutoBandwidth(Enum):
    """ObwRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class ObwRbwFilterType(Enum):
    """ObwRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter  has a flat response."""


class ObwRbwFilterBandwidthDefinition(Enum):
    """ObwRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3 dB bandwidth
    of the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the OBW RBW Filter Type attribute
    to **FFT Based**."""


class ObwSweepTimeAuto(Enum):
    """ObwSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement calculates the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""


class ObwAveragingEnabled(Enum):
    """ObwAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The OBW measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the OBW measurement is averaged."""


class ObwAveragingType(Enum):
    """ObwAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class ObwFftWindow(Enum):
    """ObwFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is
    useful for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class ObwAmplitudeCorrectionType(Enum):
    """ObwAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class SemCarrierEnabled(Enum):
    """SemCarrierEnabled."""

    FALSE = 0
    r"""The carrier power is not considered as part of the total carrier power."""

    TRUE = 1
    r"""The carrier power is considered as part of the total carrier power."""


class SemCarrierRbwAutoBandwidth(Enum):
    """SemCarrierRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class SemCarrierRbwFilterType(Enum):
    """SemCarrierRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter has a flat response."""


class SemCarrierRbwFilterBandwidthDefinition(Enum):
    """SemCarrierRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3 dB
    bandwidth of the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the SEM Carrier RBW Filter Type
    attribute to **FFT Based**."""


class SemCarrierRrcFilterEnabled(Enum):
    """SemCarrierRrcFilterEnabled."""

    FALSE = 0
    r"""The channel power of the acquired carrier channel is measured directly."""

    TRUE = 1
    r"""The measurement applies the RRC filter on the acquired carrier channel before measuring the carrier channel power."""


class SemOffsetEnabled(Enum):
    """SemOffsetEnabled."""

    FALSE = 0
    r"""Disables the offset segment for the SEM measurement."""

    TRUE = 1
    r"""Enables the offset segment for the SEM measurement."""


class SemOffsetSideband(Enum):
    """SemOffsetSideband."""

    NEGATIVE = 0
    r"""Configures a lower offset segment to the left of the leftmost carrier."""

    POSITIVE = 1
    r"""Configures an upper offset segment to the right of the rightmost carrier."""

    BOTH = 2
    r"""Configures both negative and positive offset segments."""


class SemOffsetRbwAutoBandwidth(Enum):
    """SemOffsetRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class SemOffsetRbwFilterType(Enum):
    """SemOffsetRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter has a flat response."""


class SemOffsetRbwFilterBandwidthDefinition(Enum):
    """SemOffsetRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3dB
    bandwidth of the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the spectrum bin width computed using FFT when you set the SEM Offset RBW Filter Type
    attribute to **FFT Based**."""


class SemOffsetLimitFailMask(Enum):
    """SemOffsetLimitFailMask."""

    ABSOLUTE_AND_RELATIVE = 0
    r"""The measurement fails if the power in the segment exceeds both the absolute and relative masks."""

    ABSOLUTE_OR_RELATIVE = 1
    r"""The measurement fails if the power in the segment exceeds either the absolute or relative mask."""

    ABSOLUTE = 2
    r"""The measurement fails if the power in the segment exceeds the absolute mask."""

    RELATIVE = 3
    r"""The measurement fails if the power in the segment exceeds the relative mask."""


class SemOffsetAbsoluteLimitMode(Enum):
    """SemOffsetAbsoluteLimitMode."""

    MANUAL = 0
    r"""The line specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_START` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_STOP` attribute values as the two ends is
    considered as the mask."""

    COUPLE = 1
    r"""The two ends of the line are coupled to the value of the SEM Offset Abs Limit Start attribute."""


class SemOffsetRelativeLimitMode(Enum):
    """SemOffsetRelativeLimitMode."""

    MANUAL = 0
    r"""The line specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_START` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_STOP` attribute values as the two ends is
    considered as the mask."""

    COUPLE = 1
    r"""The two ends of the line are coupled to the value of the SEM Offset Rel Limit Start attribute."""


class SemOffsetFrequencyDefinition(Enum):
    """SemOffsetFrequencyDefinition."""

    CENTER_TO_MEASUREMENT_BANDWIDTH_CENTER = 0
    r"""The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the
    center of the offset segment measurement bandwidth.
    
    Measurement Bandwidth = Resolution Bandwidth * Bandwidth Integral."""

    CENTER_TO_MEASUREMENT_BANDWIDTH_EDGE = 1
    r"""The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the
    nearest edge of the offset segment measurement bandwidth."""

    EDGE_TO_MEASUREMENT_BANDWIDTH_CENTER = 2
    r"""The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to
    the center of the nearest offset segment measurement bandwidth."""

    EDGE_TO_MEASUREMENT_BANDWIDTH_EDGE = 3
    r"""The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to
    the edge of the nearest offset segment measurement bandwidth."""


class SemPowerUnits(Enum):
    """SemPowerUnits."""

    DBM = 0
    r"""The absolute powers are reported in dBm."""

    DBM_PER_HZ = 1
    r"""The absolute powers are reported in dBm/Hz."""


class SemReferenceType(Enum):
    """SemReferenceType."""

    INTEGRATION = 0
    r"""The power reference is the integrated power of the closest carrier."""

    PEAK = 1
    r"""The power reference is the peak power of the closest carrier."""


class SemSweepTimeAuto(Enum):
    """SemSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement calculates the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attributes."""


class SemAveragingEnabled(Enum):
    """SemAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The SEM measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the SEM measurement is averaged."""


class SemAveragingType(Enum):
    """SemAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class SemFftWindow(Enum):
    """SemFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is
    useful for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class SemAmplitudeCorrectionType(Enum):
    """SemAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class SemCompositeMeasurementStatus(Enum):
    """SemCompositeMeasurementStatus."""

    FAIL = 0
    r"""Indicates that the measurement has failed."""

    PASS = 1
    r"""Indicates that the measurement has passed."""


class SemLowerOffsetMeasurementStatus(Enum):
    """SemLowerOffsetMeasurementStatus."""

    FAIL = 0
    r"""Indicates that the measurement has failed."""

    PASS = 1
    r"""Indicates that the measurement has passed."""


class SemUpperOffsetMeasurementStatus(Enum):
    """SemUpperOffsetMeasurementStatus."""

    FAIL = 0
    r"""Indicates that the measurement has failed."""

    PASS = 1
    r"""Indicates that the measurement has passed."""


class SpectrumPowerUnits(Enum):
    """SpectrumPowerUnits."""

    DBM = 0
    r"""The absolute powers are reported in dBm."""

    DBM_PER_HZ = 1
    r"""The absolute powers are reported in dBm/Hz."""

    DBW = 2
    r"""The absolute powers are reported in dBW."""

    DBV = 3
    r"""The absolute powers are reported in dBV."""

    DBMV = 4
    r"""The absolute powers are reported in dBmV."""

    DBUV = 5
    r"""The absolute powers are reported in dBuV."""

    WATTS = 6
    r"""The absolute powers are reported in W."""

    VOLTS = 7
    r"""The absolute powers are reported in volts."""

    VOLTS_SQUARED = 8
    r"""The absolute powers are reported in volts\ :sup:`2`\."""


class SpectrumRbwAutoBandwidth(Enum):
    """SpectrumRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class SpectrumRbwFilterType(Enum):
    """SpectrumRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter has a flat response."""


class SpectrumRbwFilterBandwidthDefinition(Enum):
    """SpectrumRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3dB bandwidth of
    the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BANDWIDTH_DEFINITION_6DB = 1
    r"""Defines the RBW in terms of the 6dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to
    **FFT Based**, RBW is the 6dB bandwidth of the window specified by the Spectrum FFT Window attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spectrum RBW Filter Type
    attribute to **FFT Based**."""

    ENBW = 3
    r"""Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute
    to **FFT Based**, RBW is the ENBW  bandwidth of the window specified by the Spectrum FFT Window attribute."""


class SpectrumVbwFilterAutoBandwidth(Enum):
    """SpectrumVbwFilterAutoBandwidth."""

    FALSE = 0
    r"""Specify the video bandwidth in the :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_BANDWIDTH` attribute. The
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_VBW_TO_RBW_RATIO` attribute is disregarded in this mode."""

    TRUE = 1
    r"""Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_VBW_TO_RBW_RATIO` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute. The value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_BANDWIDTH` attribute is disregarded in this mode."""


class SpectrumSweepTimeAuto(Enum):
    """SpectrumSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement calculates the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""


class SpectrumDetectorType(Enum):
    """SpectrumDetectorType."""

    NONE = 0
    r"""The detector is disabled."""

    SAMPLE = 1
    r"""The middle sample in the bucket is detected."""

    NORMAL = 2
    r"""The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If
    the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in
    alternate buckets."""

    PEAK = 3
    r"""The maximum value of the samples in the bucket is detected."""

    NEGATIVE_PEAK = 4
    r"""The minimum value of the samples in the bucket is detected."""

    AVERAGE_RMS = 5
    r"""The average RMS of all the samples in the bucket is detected."""

    AVERAGE_VOLTAGE = 6
    r"""The average voltage of all the samples in the bucket is detected."""

    AVERAGE_LOG = 7
    r"""The average log of all the samples in the bucket is detected."""


class SpectrumNoiseCalibrationMode(Enum):
    """SpectrumNoiseCalibrationMode."""

    MANUAL = 0
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` attribute to **Calibrate Noise
    Floor**, you can initiate instrument noise calibration for the spectrum measurement manually. When you set the Spectrum
    Meas Mode attribute to **Measure**, you can initiate the spectrum measurement manually."""

    AUTO = 1
    r"""When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_COMPENSATION_ENABLED` attribute to **True**, RFmx
    sets the :py:attr:`~nirfmxinstr.attribute.AttributeID.INPUT_ISOLATION_ENABLED` attribute to **Enabled** and calibrates
    the intrument noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled attribute and
    performs the spectrum measurement, including compensation for noise from the instrument. RFmx skips noise calibration
    in this mode if valid noise calibration data is already cached. When you set the Spectrum Noise Comp Enabled attribute
    to **False**, RFmx does not calibrate instrument noise and performs only the spectrum measurement without compensating
    for the noise from the instrument."""


class SpectrumNoiseCalibrationAveragingAuto(Enum):
    """SpectrumNoiseCalibrationAveragingAuto."""

    FALSE = 0
    r"""RFmx uses the averages that you set for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_COUNT` attribute."""

    TRUE = 1
    r"""RFmx uses a noise calibration averaging count of 32."""


class SpectrumNoiseCompensationEnabled(Enum):
    """SpectrumNoiseCompensationEnabled."""

    FALSE = 0
    r"""Disables compensation of the spectrum for the noise floor of the signal analyzer."""

    TRUE = 1
    r"""Enables compensation of the spectrum for the noise floor of the signal analyzer. The noise floor of the signal analyzer
    is measured for the RF path used by the Spectrum measurement and cached for future use. If signal analyzer or
    measurement parameters change, noise floors are measured again."""


class SpectrumNoiseCompensationType(Enum):
    """SpectrumNoiseCompensationType."""

    ANALYZER_AND_TERMINATION = 0
    r"""Compensates for noise from the analyzer and the 50 ohm termination. The measured power values are in excess of the
    thermal noise floor."""

    ANALYZER_ONLY = 1
    r"""Compensates for the analyzer noise only."""


class SpectrumAveragingEnabled(Enum):
    """SpectrumAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The spectrum measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the
    number of acquisitions over which the spectrum measurement is averaged."""


class SpectrumAveragingType(Enum):
    """SpectrumAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class SpectrumMeasurementMode(Enum):
    """SpectrumMeasurementMode."""

    MEASURE = 0
    r"""Spectrum measurement is performed on the acquired signal."""

    CALIBRATE_NOISE_FLOOR = 1
    r"""Manual noise calibration of the signal analyzer is performed for the spectrum measurement."""


class SpectrumFftWindow(Enum):
    """SpectrumFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is
    useful for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class SpectrumFftOverlapMode(Enum):
    """SpectrumFftOverlapMode."""

    DISABLED = 0
    r"""Disables the overlap between the chunks."""

    AUTOMATIC = 1
    r"""Measurement sets the overlap based on the value you have set for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute. When you set the Spectrum FFT Window attribute to
    any value other than **None**, the number of overlapped samples between consecutive chunks is set to 50% of the value
    of the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute. When you set the Spectrum FFT
    Window attribute to **None**, the chunks are not overlapped and the overlap is set to 0%."""

    USER_DEFINED = 2
    r"""Measurement uses the overlap that you specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP`
    attribute."""


class SpectrumFftOverlapType(Enum):
    """SpectrumFftOverlapType."""

    RMS = 0
    r"""Linear averaging of the FFTs taken over different chunks of data is performed. RMS averaging reduces signal
    fluctuations but not the noise floor."""

    MAX = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one chunk FFT to the next."""


class SpectrumAmplitudeCorrectionType(Enum):
    """SpectrumAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class SpectrumMeasurementMethod(Enum):
    """SpectrumMeasurementMethod."""

    NORMAL = 0
    r"""The Spectrum measurement acquires the spectrum using the same signal analyzer setting across frequency bands."""

    SEQUENTIAL_FFT = 2
    r"""The Spectrum measurement acquires I/Q samples for a duration specified by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute. These samples are divided into smaller
    chunks. If the attribute :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` is True, The size of
    each chunk is defined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute. If the
    attribute Spectrum RBW Auto is False, the Spectrum Sequential FFT Size  is auto computed based on the configured
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH`. The overlap between the chunks is defined by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute. FFT is computed on each of these chunks.
    The resultant FFTs are averaged as per the configured averaging type in the attribute
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_TYPE`to get the spectrum.
    
    Sequential FFT method should be used for the following scenarios.
    
    #. While performing fast Spectrum measurements by utilizing smaller FFT sizes. However, accuracy of the results may be reduced.
    
    #. When measuring signals with time-varying spectral characteristics, sequential FFT with overlap mode set to Automatic should be used.
    
    #. For accurate power measurements when the power characteristics of the signal vary over time, averaging is allowed.
    
    The following attributes have limited support when you set the Spectrum Measurement Method attribute to
    **Sequential FFT**.
    
    +-----------------------------------------------------------------------------+---------------------+
    | Property                                                                    | Supported Value     |
    +=============================================================================+=====================+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH`   | True                |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_TYPE`             | FFT Based           |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO`             | False               |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT`             | >=1                 |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_ANALYSIS_THREADS`  | 1                   |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.AMPLITUDE_CORRECTION_TYPE`   | RF Center Frequency |
    +-----------------------------------------------------------------------------+---------------------+
    | :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_VBW_TO_RBW_RATIO` | >=3                 |
    +-----------------------------------------------------------------------------+---------------------+
    
    .. note::
       For multi-span FFT, the averaging count should be 1."""


class SpectrumAnalysisInput(Enum):
    """SpectrumAnalysisInput."""

    IQ = 0
    r"""Measurement analyzes the acquired I+jQ data, resulting generally in a spectrum that is not symmetric around 0 Hz.
    Spectrum trace result contains both positive and negative frequencies. Since the RMS power of the complex envelope is
    3.01 dB higher than that of its equivalent real RF signal, the spectrum trace result of the acquired I+jQ data is
    scaled by -3.01 dB."""

    I_ONLY = 1
    r"""Measurement ignores the Q data from the acquired I+jQ data and analyzes I+j0, resulting in a spectrum that is symmetric
    around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of I+j0 data is scaled by +3.01 dB to
    account for the power of the negative frequencies that are not returned in the spectrum trace."""

    Q_ONLY = 2
    r"""Measurement ignores the I data from the acquired I+jQ data and analyzes Q+j0, resulting in a spectrum that is symmetric
    around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of Q+j0 data is scaled by +3.01 dB to
    account for the power of the negative frequencies that are not returned in the spectrum trace."""


class SpurRangeEnabled(Enum):
    """SpurRangeEnabled."""

    FALSE = 0
    r"""Disables the acquisition of the frequency range."""

    TRUE = 1
    r"""Enables measurement of Spurs in the frequency range."""


class SpurRbwAutoBandwidth(Enum):
    """SpurRbwAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class SpurRbwFilterType(Enum):
    """SpurRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""An RBW filter with a Gaussian response is applied."""

    FLAT = 2
    r"""An RBW filter with a flat response is applied."""


class SpurRbwFilterBandwidthDefinition(Enum):
    """SpurRbwFilterBandwidthDefinition."""

    BANDWIDTH_DEFINITION_3DB = 0
    r"""Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_TYPE` attribute to **FFT Based**, RBW is the 3dB
    bandwidth of the window specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_WINDOW` attribute."""

    BIN_WIDTH = 2
    r"""Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spur Range RBW Filter Type
    attribute to **FFT Based**."""

    ENBW = 3
    r"""Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spur  RBW Filter Type attribute to
    **FFT Based**, RBW is the ENBW  bandwidth of the window specified by the Spur FFT Window attribute."""


class SpurRangeVbwFilterAutoBandwidth(Enum):
    """SpurRangeVbwFilterAutoBandwidth."""

    FALSE = 0
    r"""Specify the video bandwidth in the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_BANDWIDTH`
    attribute. The :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_VBW_TO_RBW_RATIO` attribute is
    disregarded in this mode."""

    TRUE = 1
    r"""Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute. The value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_BANDWIDTH` attribute is disregarded in this mode."""


class SpurSweepTimeAuto(Enum):
    """SpurSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement calculates the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute."""


class SpurRangeDetectorType(Enum):
    """SpurRangeDetectorType."""

    NONE = 0
    r"""The detector is disabled."""

    SAMPLE = 1
    r"""The middle sample in the bucket is detected."""

    NORMAL = 2
    r"""The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If
    the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in
    alternate buckets."""

    PEAK = 3
    r"""The maximum value of the samples in the bucket is detected."""

    NEGATIVE_PEAK = 4
    r"""The minimum value of the samples in the bucket is detected."""

    AVERAGE_RMS = 5
    r"""The average RMS of all the samples in the bucket is detected."""

    AVERAGE_VOLTAGE = 6
    r"""The average voltage of all the samples in the bucket is detected."""

    AVERAGE_LOG = 7
    r"""The average log of all the samples in the bucket is detected."""


class SpurAbsoluteLimitMode(Enum):
    """SpurAbsoluteLimitMode."""

    MANUAL = 0
    r"""The line specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_START` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_STOP` attribute  values as the two ends is
    considered as the threshold."""

    COUPLE = 1
    r"""The two ends of the line are coupled to the value of the Spur Range Abs Limit Start attribute."""


class SpurAveragingEnabled(Enum):
    """SpurAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The Spur measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number
    of acquisitions over which the Spur measurement is averaged."""


class SpurAveragingType(Enum):
    """SpurAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class SpurFftWindow(Enum):
    """SpurFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful for
    time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class SpurAmplitudeCorrectionType(Enum):
    """SpurAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class SpurMeasurementStatus(Enum):
    """SpurMeasurementStatus."""

    FAIL = 0
    r"""A detected spur in the range is greater than the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SPUR_ABSOLUTE_LIMIT` attribute."""

    PASS = 1
    r"""All detected spurs in the range are lower than the value of the Spur Results Spur Abs Limit attribute."""


class SpurRangeStatus(Enum):
    """SpurRangeStatus."""

    FAIL = 0
    r"""The amplitude of the detected spurs is greater than the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SPUR_ABSOLUTE_LIMIT` attribute."""

    PASS = 1
    r"""The amplitude of the detected spurs is lower than the value of the Spur Results Spur Abs Limit attribute."""


class TxpRbwFilterType(Enum):
    """TxpRbwFilterType."""

    GAUSSIAN = 1
    r"""The RBW filter has a Gaussian response."""

    FLAT = 2
    r"""The RBW filter has a flat response."""

    NONE = 5
    r"""The measurement does not use any RBW filtering."""

    RRC = 6
    r"""The RRC filter with the roll-off specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_ALPHA`
    attribute is used as the RBW filter."""


class TxpVbwFilterAutoBandwidth(Enum):
    """TxpVbwFilterAutoBandwidth."""

    FALSE = 0
    r"""Specify the video bandwidth in the :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_BANDWIDTH` attribute. The
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_VBW_TO_RBW_RATIO` attribute is disregarded in this mode."""

    TRUE = 1
    r"""Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using
    the :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_VBW_TO_RBW_RATIO` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute. The value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_BANDWIDTH` attribute is disregarded in this mode."""


class TxpThresholdEnabled(Enum):
    """TxpThresholdEnabled."""

    FALSE = 0
    r"""All the acquired samples are considered for the TXP measurement."""

    TRUE = 1
    r"""The samples above the threshold level specified in the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_LEVEL`
    attribute are considered for the TXP measurement."""


class TxpThresholdType(Enum):
    """TxpThresholdType."""

    RELATIVE = 0
    r"""The threshold is relative to the peak power of the acquired samples."""

    ABSOLUTE = 1
    r"""The threshold is the absolute power, in dBm."""


class TxpAveragingEnabled(Enum):
    """TxpAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The TXP measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the TXP measurement is averaged."""


class TxpAveragingType(Enum):
    """TxpAveragingType."""

    RMS = 0
    r"""The power trace is linearly averaged."""

    LOG = 1
    r"""The power trace is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power trace is averaged."""

    MAXIMUM = 3
    r"""The maximum instantaneous power in the power trace is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The minimum instantaneous power in the power trace is retained from one acquisition to the next."""


class AmpmMeasurementSampleRateMode(Enum):
    """AmpmMeasurementSampleRateMode."""

    USER = 0
    r"""The acquisition sample rate is defined by the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE` attribute."""

    REFERENCE_WAVEFORM = 1
    r"""The acquisition sample rate is set to match the sample rate of the reference waveform."""


class AmpmSignalType(Enum):
    """AmpmSignalType."""

    MODULATED = 0
    r"""The reference waveform is a cellular or connectivity standard signal."""

    TONES = 1
    r"""The reference waveform is a continuous signal comprising of one or more tones."""


class AmpmSynchronizationMethod(Enum):
    """AmpmSynchronizationMethod."""

    DIRECT = 1
    r"""Synchronizes the acquired and reference waveforms assuming that sample rate is sufficient to prevent aliasing in
    intermediate operations. This method is recommended when the measurement sampling rate is high."""

    ALIAS_PROTECTED = 2
    r"""Synchronizes the acquired and  reference waveforms while ascertaining that intermediate operations are not impacted by
    aliasing. This method is recommended for non-contiguous carriers separated by a large gap, and/or when the measurement
    sampling rate is low. Refer to AMPM concept help for more information."""


class AmpmAutoCarrierDetectionEnabled(Enum):
    """AmpmAutoCarrierDetectionEnabled."""

    FALSE = 0
    r"""Disables auto detection of carrier offset and carrier bandwidth."""

    TRUE = 1
    r"""Enables auto detection of carrier offset and carrier bandwidth."""


class AmpmAMToAMCurveFitType(Enum):
    """AmpmAMToAMCurveFitType."""

    LEAST_SQUARE = 0
    r"""The measurement minimizes the energy of the polynomial approximation error."""

    LEAST_ABSOLUTE_RESIDUAL = 1
    r"""The measurement minimizes the magnitude of the polynomial approximation error."""

    BISQUARE = 2
    r"""The measurement excludes the effect of data outliers while minimizing the energy of the polynomial approximation error."""


class AmpmAMToPMCurveFitType(Enum):
    """AmpmAMToPMCurveFitType."""

    LEAST_SQUARE = 0
    r"""The measurement minimizes the energy of the polynomial approximation error."""

    LEAST_ABSOLUTE_RESIDUAL = 1
    r"""The measurement minimizes the magnitude of the polynomial approximation error."""

    BISQUARE = 2
    r"""The measurement excludes the effect of data outliers while minimizing the energy of the polynomial approximation error."""


class AmpmThresholdEnabled(Enum):
    """AmpmThresholdEnabled."""

    FALSE = 0
    r"""All samples are considered for the AMPM measurement."""

    TRUE = 1
    r"""Samples above the threshold level specified in the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_LEVEL`
    attribute are considered for the AMPM measurement."""


class AmpmThresholdType(Enum):
    """AmpmThresholdType."""

    RELATIVE = 0
    r"""The threshold is relative to the peak power of the acquired samples."""

    ABSOLUTE = 1
    r"""The threshold is the absolute power, in dBm."""


class AmpmThresholdDefinition(Enum):
    """AmpmThresholdDefinition."""

    INPUT_AND_OUTPUT = 0
    r"""Corresponding acquired and reference waveform samples are used for AMPM measurement when both samples are greater or
    equal to the threshold level."""

    REFERENCE_POWER_TYPE = 1
    r"""Corresponding acquired and reference waveform samples are used for AMPM measurement when reference waveform sample is
    greater than or equal to the threshold level and :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE`
    attribute is set to Input. Corresponding acquired and reference waveform samples are used for AMPM measurement when
    acquired waveform sample is greater than or equal to the threshold level and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute is set to Output."""


class AmpmFrequencyOffsetCorrectionEnabled(Enum):
    """AmpmFrequencyOffsetCorrectionEnabled."""

    FALSE = 0
    r"""The measurement does not perform frequency offset correction."""

    TRUE = 1
    r"""The measurement computes and corrects any frequency offset between the reference and the acquired waveforms."""


class AmpmIQOriginOffsetCorrectionEnabled(Enum):
    """AmpmIQOriginOffsetCorrectionEnabled."""

    FALSE = 0
    r"""Disables IQ origin offset correction."""

    TRUE = 1
    r"""Enables IQ origin offset correction."""


class AmpmAMToAMEnabled(Enum):
    """AmpmAMToAMEnabled."""

    FALSE = 0
    r"""Disables the computation of following scalar results and traces. Empty array is returned if the disabled result is an
    array. NaN is returned otherwise.
    
    The following scalar results are disabled:
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_LINEAR_GAIN`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.1_DB_COMPRESSION_POINT`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.INPUT_COMPRESSION_POINT`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.OUTPUT_COMPRESSION_POINT`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.GAIN_ERROR_RANGE`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AM_TO_AM_CURVE_FIT_RESIDUAL`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AM_TO_AM_CURVE_FIT_COEFFICIENTS`
    
    The following traces are disabled:
    
    Measured AM to AM
    
    Curve Fit AM to AM
    
    Relative Power Trace"""

    TRUE = 1
    r"""Enables the computation of AM to AM results and traces."""


class AmpmAMToPMEnabled(Enum):
    """AmpmAMToPMEnabled."""

    FALSE = 0
    r"""Disables the computation of following scalar results and traces. Empty array is returned if the disabled result is an
    array. NaN is returned otherwise.
    
    The following scalar results are disabled:
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_PHASE_ERROR`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.PHASE_ERROR_RANGE`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AM_TO_PM_CURVE_FIT_RESIDUAL`
    
    :py:attr:`~nirfmxspecan.attributes.AttributeID.AM_TO_PM_CURVE_FIT_COEFFICIENTS`
    
    The following traces are disabled:
    
    Measured AM to PM
    
    Curve Fit AM to PM
    
    Relative Phase Trace"""

    TRUE = 1
    r"""Enables the computation of AM to PM results and traces."""


class AmpmEvmEnabled(Enum):
    """AmpmEvmEnabled."""

    FALSE = 0
    r"""Disables EVM computation. NaN is returned as Mean RMS EVM."""

    TRUE = 1
    r"""Enables EVM computation."""


class AmpmEqualizerMode(Enum):
    """AmpmEqualizerMode."""

    OFF = 0
    r"""Equalization is not performed."""

    TRAIN = 1
    r"""The equalizer is turned on to compensate for the effect of the channel."""


class AmpmAveragingEnabled(Enum):
    """AmpmAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The AMPM measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number
    of acquisitions over which the signal for the AMPM measurement is averaged."""


class AmpmCompressionPointEnabled(Enum):
    """AmpmCompressionPointEnabled."""

    FALSE = 0
    r"""Disables computation of compression points."""

    TRUE = 1
    r"""Enables computation of compression points."""


class AmpmCompressionPointGainReference(Enum):
    """AmpmCompressionPointGainReference."""

    AUTO = 0
    r"""Measurement computes the gain reference to be used for compression point calculation. The computed gain reference is
    also returned as :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_LINEAR_GAIN` result."""

    REFERENCE_POWER = 1
    r"""Measurement uses the gain corresponding to the reference power that you specify for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE_POWER` attribute as gain reference. The
    reference power can be configured as either input or output power based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute."""

    MAX_GAIN = 2
    r"""Measurement uses the maximum gain as gain reference for compression point calculation."""

    USER_DEFINED = 3
    r"""Measurement uses the gain that you specify for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_USER_GAIN` attribute as gain reference for compression
    point calculation."""


class AmpmReferencePowerType(Enum):
    """AmpmReferencePowerType."""

    INPUT = 0
    r"""The instantaneous powers at the input port of device under test (DUT) forms the x-axis of AM to AM and AM to PM traces."""

    OUTPUT = 1
    r"""The instantaneous powers at the output port of DUT forms the x-axis of AM to AM and AM to PM traces."""


class DpdMeasurementSampleRateMode(Enum):
    """DpdMeasurementSampleRateMode."""

    USER = 0
    r"""The acquisition sample rate is defined by the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE` attribute."""

    REFERENCE_WAVEFORM = 1
    r"""The acquisition sample rate is set to match the sample rate of the reference waveform."""


class DpdSignalType(Enum):
    """DpdSignalType."""

    MODULATED = 0
    r"""The reference waveform is a cellular or connectivity standard signal."""

    TONES = 1
    r"""The reference waveform is a continuous signal comprising one or more tones."""


class DpdSynchronizationMethod(Enum):
    """DpdSynchronizationMethod."""

    DIRECT = 1
    r"""Synchronizes the acquired and reference waveforms assuming that sample rate is sufficient to prevent aliasing in
    intermediate operations. This method is recommended when measurement sampling rate is high."""

    ALIAS_PROTECTED = 2
    r"""Synchronizes the acquired and  reference waveforms while ascertaining that intermediate operations are not impacted by
    aliasing. This method is recommended for non-contiguous carriers separated by a large gap, and/or when measurement
    sampling rate is low. Refer to DPD concept help for more information."""


class DpdAutoCarrierDetectionEnabled(Enum):
    """DpdAutoCarrierDetectionEnabled."""

    FALSE = 0
    r"""Disables auto detection of carrier offset and carrier bandwidth."""

    TRUE = 1
    r"""Enables auto detection of carrier offset and carrier bandwidth."""


class DpdModel(Enum):
    """DpdModel."""

    LOOKUP_TABLE = 0
    r"""This model computes the complex gain coefficients applied when performing digital predistortion to linearize systems
    with negligible memory effects."""

    MEMORY_POLYNOMIAL = 1
    r"""This model computes the memory polynomial predistortion coefficients used to linearize systems with moderate memory
    effects."""

    GENERALIZED_MEMORY_POLYNOMIAL = 2
    r"""This model computes the generalized memory polynomial predistortion coefficients used to linearize systems with
    significant memory effects."""

    DECOMPOSED_VECTOR_ROTATION = 3
    r"""This model computes the Decomposed Vector Rotation model predistortion coefficients used to linearize wideband systems
    with significant memory effects."""


class DpdTargetGainType(Enum):
    """DpdTargetGainType."""

    AVERAGE_GAIN = 0
    r"""The DPD polynomial or lookup table is computed by assuming that the linearized gain expected from the DUT after
    applying DPD on the input waveform is equal to the average power gain provided by the DUT without DPD."""

    LINEAR_REGION_GAIN = 1
    r"""The DPD polynomial or lookup table is computed by assuming that the linearized gain expected from the DUT after
    applying DPD on the input waveform is equal to the gain provided by the DUT, without DPD, to the parts of the reference
    waveform that do not drive the DUT into non-linear gain-expansion or compression regions of its input-output
    characteristics.
    
    The measurement computes the linear region gain as the average gain experienced by the parts of the reference
    waveform that are below a threshold which is computed as shown in the following equation:
    
    *Linear region threshold (dBm)* = Max {-25, Min {*reference waveform power*} + 6, *DUT Average Input Power*
    -15}"""

    PEAK_INPUT_POWER_GAIN = 2
    r"""The DPD polynomial or lookup table is computed by assuming that the linearized gain expected from the DUT after
    applying DPD on the input waveform is equal to the average power gain provided by the DUT, without DPD, to all the
    samples of the reference waveform for which the magnitude is greater than the peak power in the reference waveform
    (dBm) - 0.5dB."""


class DpdLookupTableType(Enum):
    """DpdLookupTableType."""

    LOG = 0
    r"""Input powers in the LUT are specified in dBm."""

    LINEAR = 1
    r"""Input powers in the LUT are specified in watts."""


class DpdLookupTableAMToAMCurveFitType(Enum):
    """DpdLookupTableAMToAMCurveFitType."""

    LEAST_SQUARE = 0
    r"""Minimizes the energy of the polynomial approximation error."""

    LEAST_ABSOLUTE_RESIDUAL = 1
    r"""Minimizes the magnitude of the polynomial approximation error."""

    BISQUARE = 2
    r"""Excludes the effect of data outliers while minimizing the energy of the polynomial approximation error."""


class DpdLookupTableAMToPMCurveFitType(Enum):
    """DpdLookupTableAMToPMCurveFitType."""

    LEAST_SQUARE = 0
    r"""Minimizes the energy of the polynomial approximation error."""

    LEAST_ABSOLUTE_RESIDUAL = 1
    r"""Minimizes the magnitude of the polynomial approximation error."""

    BISQUARE = 2
    r"""Excludes the effect of data outliers while minimizing the energy of the polynomial approximation error."""


class DpdLookupTableThresholdEnabled(Enum):
    """DpdLookupTableThresholdEnabled."""

    FALSE = 0
    r"""All samples are considered for the DPD measurement."""

    TRUE = 1
    r"""Only samples above the threshold level which you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOOKUP_TABLE_THRESHOLD_LEVEL` attribute are considered for the DPD
    measurement."""


class DpdLookupTableThresholdType(Enum):
    """DpdLookupTableThresholdType."""

    RELATIVE = 0
    r"""The threshold is relative to the peak power of the acquired samples."""

    ABSOLUTE = 1
    r"""The threshold is the absolute power, in dBm."""


class DpdLookupTableThresholdDefinition(Enum):
    """DpdLookupTableThresholdDefinition."""

    INPUT_AND_OUTPUT = 0
    r"""Corresponding acquired and reference waveform samples are used for AMPM measurement when both samples are greater or
    equal to the threshold level."""

    INPUT = 1
    r"""Corresponding acquired and reference waveform samples are used for AMPM measurement when reference waveform sample is
    greater than or equal to the threshold level."""


class DpdMemoryPolynomialOrderType(Enum):
    """DpdMemoryPolynomialOrderType."""

    ALL_ORDERS = 0
    r"""The memory polynomial will compute all the terms for the given order."""

    ODD_ORDERS_ONLY = 1
    r"""The memory polynomial will compute the non-zero coefficients only for the odd terms."""

    EVEN_ORDERS_ONLY = 2
    r"""The memory polynomial will compute the non-zero coefficents only for the first linear term and all even terms."""


class DpdMemoryPolynomialLeadOrderType(Enum):
    """DpdMemoryPolynomialLeadOrderType."""

    ALL_ORDERS = 0
    r"""The memory polynomial will compute all the terms for the given order."""

    ODD_ORDERS_ONLY = 1
    r"""The memory polynomial will compute the non-zero coefficients only for the odd terms."""

    EVEN_ORDERS_ONLY = 2
    r"""The memory polynomial will compute the non-zero coefficents only for the even terms."""


class DpdMemoryPolynomialLagOrderType(Enum):
    """DpdMemoryPolynomialLagOrderType."""

    ALL_ORDERS = 0
    r"""The memory polynomial will compute all the terms for the given order."""

    ODD_ORDERS_ONLY = 1
    r"""The memory polynomial will compute the non-zero coefficients only for the odd terms."""

    EVEN_ORDERS_ONLY = 2
    r"""The memory polynomial will compute the non-zero coefficents only for the even terms."""


class DpdDvrDdrEnabled(Enum):
    """DpdDvrDdrEnabled."""

    FALSE = 0
    r"""The Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector Rotation model are disabled."""

    TRUE = 1
    r"""The Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector Rotation model are enabled."""


class DpdMeasurementMode(Enum):
    """DpdMeasurementMode."""

    ACQUIRE_AND_EXTRACT = 0
    r"""The measurement acquires the training waveform required for the extraction of the DPD model coefficients from the
    hardware and then computes the model coefficients.
    
    In this mode, the supported :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` are **Lookup Table**,
    **Memory Polynomial **, and **Generalized Memory Polynomial**."""

    EXTRACT_ONLY = 1
    r"""The measurement uses the user configured training waveform required for the extraction of the DPD model coefficients.
    
    In this mode, the only supported :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` is **Decomposed Vector
    Rotation**."""


class DpdIterativeDpdEnabled(Enum):
    """DpdIterativeDpdEnabled."""

    FALSE = 0
    r"""RFmx computes the DPD Results DPD Polynomial without considering the value of the DPD Previous DPD Polynomial."""

    TRUE = 1
    r"""RFmx computes the DPD Results DPD Polynomial based on the value of the DPD Previous DPD Polynomial."""


class DpdFrequencyOffsetCorrectionEnabled(Enum):
    """DpdFrequencyOffsetCorrectionEnabled."""

    FALSE = 0
    r"""The measurement computes and corrects any frequency offset between the reference and the acquired waveforms."""

    TRUE = 1
    r"""The measurement does not perform frequency offset correction."""


class DpdIQOriginOffsetCorrectionEnabled(Enum):
    """DpdIQOriginOffsetCorrectionEnabled."""

    FALSE = 0
    r"""Disables IQ origin offset correction."""

    TRUE = 1
    r"""Enables IQ origin offset correction."""


class DpdAveragingEnabled(Enum):
    """DpdAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The DPD measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the signal for the DPD measurement is averaged."""


class DpdNmseEnabled(Enum):
    """DpdNmseEnabled."""

    FALSE = 0
    r"""Disables NMSE computation. NaN is returned as NMSE."""

    TRUE = 1
    r"""Enables NMSE computation."""


class DpdPreDpdCfrEnabled(Enum):
    """DpdPreDpdCfrEnabled."""

    FALSE = 0
    r"""Disables the CFR. The :py:meth:`apply_pre_dpd_signal_conditioning` method returns an error when the CFR is disabled."""

    TRUE = 1
    r"""Enables the CFR."""


class DpdPreDpdCfrMethod(Enum):
    """DpdPreDpdCfrMethod."""

    CLIPPING = 0
    r"""Hard clips the signal such that the target PAPR is achieved."""

    PEAK_WINDOWING = 1
    r"""Scales the peaks in the signal using weighted window function to get smooth peaks and achieve the target PAPR."""

    SIGMOID = 2
    r"""Scales the peaks using modified sigmoid transfer function to get smooth peaks and achieve the target PAPR. This method
    does not support the filter operation."""


class DpdPreDpdCfrWindowType(Enum):
    """DpdPreDpdCfrWindowType."""

    FLAT_TOP = 1
    r"""Uses the flat top window function to scale peaks."""

    HANNING = 2
    r"""Uses the Hanning window function to scale peaks."""

    HAMMING = 3
    r"""Uses the Hamming window function to scale peaks."""

    GAUSSIAN = 4
    r"""Uses the Gaussian window function to scale peaks."""

    BLACKMAN = 5
    r"""Uses the Blackman window function to scale peaks."""

    BLACKMAN_HARRIS = 6
    r"""Uses the Blackman-Harris window function to scale peaks."""

    KAISER_BESSEL = 7
    r"""Uses the Kaiser-Bessel window function to scale peaks."""


class DpdPreDpdCfrFilterEnabled(Enum):
    """DpdPreDpdCfrFilterEnabled."""

    FALSE = 0
    r"""Disables the filter operation when performing CFR."""

    TRUE = 1
    r"""Enables filter operation when performing CFR. Filter operation is not supported when you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**."""


class DpdApplyDpdConfigurationInput(Enum):
    """DpdApplyDpdConfigurationInput."""

    MEASUREMENT = 0
    r"""Uses the computed DPD polynomial or lookup table for applying DPD on an input waveform using the same RFmx session
    handle. The configuration parameters for applying DPD such as the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_AVERAGE_INPUT_POWER`,
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`,
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE`, DPD polynomial, and lookup table  are obtained
    from the DPD measurement configuration."""

    USER = 1
    r"""Applies DPD by using a computed DPD polynomial or lookup table on an input waveform. You must set the configuration
    parameters for applying DPD such as the  :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DUT_AVERAGE_INPUT_POWER`,
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL`,
    :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_MEASUREMENT_SAMPLE_RATE`, DPD polynomial, and lookup table. You do
    not need to call the :py:meth:`initiate` method when you set the DPD Apply DPD Config Input attribute **User**."""


class DpdApplyDpdLookupTableCorrectionType(Enum):
    """DpdApplyDpdLookupTableCorrectionType."""

    MAGNITUDE_AND_PHASE = 0
    r"""The measurement predistorts the magnitude and phase of the input waveform."""

    MAGNITUDE_ONLY = 1
    r"""The measurement predistorts only the magnitude of the input waveform."""

    PHASE_ONLY = 2
    r"""The measurement predistorts only the phase of the input waveform."""


class DpdApplyDpdMemoryModelCorrectionType(Enum):
    """DpdApplyDpdMemoryModelCorrectionType."""

    MAGNITUDE_AND_PHASE = 0
    r"""The measurement predistorts the magnitude and phase of the input waveform."""

    MAGNITUDE_ONLY = 1
    r"""The measurement predistorts only the magnitude of the input waveform."""

    PHASE_ONLY = 2
    r"""The measurement predistorts only the phase of the input waveform."""


class DpdApplyDpdCfrEnabled(Enum):
    """DpdApplyDpdCfrEnabled."""

    FALSE = 0
    r"""Disables CFR. The maximum increase in PAPR, after pre-distortion, is limited to 6 dB."""

    TRUE = 1
    r"""Enables CFR."""


class DpdApplyDpdCfrMethod(Enum):
    """DpdApplyDpdCfrMethod."""

    CLIPPING = 0
    r"""Hard clips the signal such that the target PAPR is achieved."""

    PEAK_WINDOWING = 1
    r"""Scales the peaks in the signal using weighted window function to get smooth peaks and achieve the target PAPR."""

    SIGMOID = 2
    r"""Scales the peaks using modified sigmoid transfer function to get smooth peaks and achieve the target PAPR. This method
    does not support the filter operation."""


class DpdApplyDpdCfrTargetPaprType(Enum):
    """DpdApplyDpdCfrTargetPaprType."""

    INPUT_PAPR = 0
    r"""Sets the target PAPR for pre-distorted waveform equal to the PAPR of input waveform."""

    CUSTOM = 1
    r"""Sets the target PAPR equal to the value that you set for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_TARGET_PAPR` attribute."""


class DpdApplyDpdCfrWindowType(Enum):
    """DpdApplyDpdCfrWindowType."""

    FLAT_TOP = 1
    r"""Uses the flat top window function to scale peaks."""

    HANNING = 2
    r"""Uses the Hanning window function to scale peaks."""

    HAMMING = 3
    r"""Uses the Hamming window function to scale peaks."""

    GAUSSIAN = 4
    r"""Uses the Gaussian window function to scale peaks."""

    BLACKMAN = 5
    r"""Uses the Blackman window function to scale peaks."""

    BLACKMAN_HARRIS = 6
    r"""Uses the Blackman-Harris window function to scale peaks."""

    KAISER_BESSEL = 7
    r"""Uses the Kaiser-Bessel window function to scale peaks."""


class DpdApplyDpdUserDpdModel(Enum):
    """DpdApplyDpdUserDpdModel."""

    LOOKUP_TABLE = 0
    r"""This model computes the complex gain coefficients applied to linearize systems with negligible memory effects."""

    MEMORY_POLYNOMIAL = 1
    r"""This model computes the memory polynomial predistortion coefficients used to linearize systems with moderate memory
    effects."""

    GENERALIZED_MEMORY_POLYNOMIAL = 2
    r"""This model computes the generalized memory polynomial predistortion coefficients used to linearize systems with
    significant memory effects."""


class DpdApplyDpdUserLookupTableType(Enum):
    """DpdApplyDpdUserLookupTableType."""

    LOG = 0
    r"""Input powers in the LUT are specified in dBm."""

    LINEAR = 1
    r"""Input powers in the LUT are specified in watts."""


class IdpdEqualizerMode(Enum):
    """IdpdEqualizerMode."""

    OFF = 0
    r"""Equalization filter is not applied."""

    TRAIN = 1
    r"""Train Equalization filter. The filter length is obtained from the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EQUALIZER_FILTER_LENGTH`."""

    HOLD = 2
    r"""The :py:meth:`configure_equalizer_coefficients` method specifies the filter that acts as the equalization filter. This
    filter is applied prior to calculating the predistorted waveform."""


class IdpdMeasurementSampleRateMode(Enum):
    """IdpdMeasurementSampleRateMode."""

    USER = 0
    r"""Acquisition sample rate is defined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE`."""

    REFERENCE_WAVEFORM = 1
    r"""Acquisition sample rate is set to match the sample rate of the reference waveform."""


class IdpdSignalType(Enum):
    """IdpdSignalType."""

    MODULATED = 0
    r"""Specifies the reference waveform is a banded signal like cellular or connectivity standard signals."""

    TONES = 1
    r"""Specifies the reference waveform is a continuous signal comprising of one or more tones.
    
    IDPD measurement chooses alignment algorithms based on the IDPD Signal Type attribute."""


class IdpdReferenceWaveformIdleDurationPresent(Enum):
    """IdpdReferenceWaveformIdleDurationPresent."""

    FALSE = 0
    r"""Reference waveform has no idle duration."""

    TRUE = 1
    r"""Reference waveform contains idle duration."""


class IdpdAveragingEnabled(Enum):
    """IdpdAveragingEnabled."""

    FALSE = 0
    r"""The number of acquisitions is 1."""

    TRUE = 1
    r"""The measurement uses :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` for the number of acquisitions
    over which the measurement is averaged."""


class IdpdEvmEnabled(Enum):
    """IdpdEvmEnabled."""

    FALSE = 0
    r"""Disables EVM computation. NaN is returned for Mean RMS EVM."""

    TRUE = 1
    r"""Enables EVM computation."""


class IdpdEvmUnit(Enum):
    """IdpdEvmUnit."""

    PERCENTAGE = 0
    r"""EVM is expressed as a percentage."""

    DB = 1
    r"""EVM is expressed in dB."""


class IQMeasurementMode(Enum):
    """IQMeasurementMode."""

    NORMAL = 0
    r"""Performs the measurement in the normal RFmx execution mode and supports all the RFmx features such as overlapped
    measurements."""

    RAWIQ = 1
    r"""Reduces the overhead introduced by this measurement by not copying and storing the data in RFmx. In this mode IQ data
    needs to be retrieved using :py:meth:`nirfmxinstr.session.Session.fetch_raw_iq_data` method instead of
    :py:meth:`fetch_data` method. :py:meth:`nirfmxinstr.session.Session.fetch_raw_iq_data` directly fetches the data from
    the hardware.
    
    The following list describes the limitations of using this mode,
    
    - No other measurements can be enabled along with this IQ measurement.
    
    - You must fetch the IQ data before initiating another RFmx measurement because the data is not stored in RFmx."""


class IQBandwidthAuto(Enum):
    """IQBandwidthAuto."""

    FALSE = 0
    r"""The measurement uses the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH` attribute as the
    minimum acquisition bandwidth."""

    TRUE = 1
    r"""The measurement uses 0.8 * sample rate as the minimum signal bandwidth."""


class IQDeleteRecordOnFetch(Enum):
    """IQDeleteRecordOnFetch."""

    FALSE = 0
    r"""The measurement does not delete the fetched record."""

    TRUE = 1
    r"""The measurement deletes the fetched record."""


class IMFrequencyDefinition(Enum):
    """IMFrequencyDefinition."""

    RELATIVE = 0
    r"""The tone and intermod frequencies are relative to the RF center frequency."""

    ABSOLUTE = 1
    r"""The tone and intermod frequencies are absolute frequencies. The measurement ignores the RF center frequency."""


class IMAutoIntermodsSetupEnabled(Enum):
    """IMAutoIntermodsSetupEnabled."""

    FALSE = 0
    r"""The measurement uses the values that you specify for the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_FREQUENCY` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_FREQUENCY` attributes."""

    TRUE = 1
    r"""The measurement computes the intermod frequencies. The maximum number of intermods that you can measure is based on the
    value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.MAXIMUM_INTERMOD_ORDER` attribute."""


class IMIntermodEnabled(Enum):
    """IMIntermodEnabled."""

    FALSE = 0
    r"""Disables an intermod for the IM measurement. The results for the disabled intermods are displayed as NaN."""

    TRUE = 1
    r"""Enables an intermod for the IM measurement."""


class IMIntermodSide(Enum):
    """IMIntermodSide."""

    LOWER = 0
    r"""Measures the intermodulation product corresponding to the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_FREQUENCY` attribute."""

    UPPER = 1
    r"""Measures the intermodulation product corresponding to the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_FREQUENCY` attribute."""

    BOTH = 2
    r"""Measures the intermodulation product corresponding to both IM Lower Intermod Freq and IM Upper Intermod Freq
    attributes."""


class IMMeasurementMethod(Enum):
    """IMMeasurementMethod."""

    NORMAL = 0
    r"""The IM measurement acquires the spectrum using the same signal analyzer settings across frequency bands. Use this
    method when the fundamental tone separation is not large.
    
    **Supported devices:** PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668."""

    DYNAMIC_RANGE = 1
    r"""The IM measurement acquires a segmented spectrum using the signal analyzer specific optimizations for different
    frequency bands. The spectrum is acquired in segments, one per tone or intermod frequency to be measured. The span of
    each acquired spectral segment is equal to the frequency separation between the two input tones, or 1 MHz, whichever is
    smaller.
    
    Use this method to configure the IM measurement and the signal analyzer for maximum dynamic range instead of
    measurement speed.
    
    **Supported devices:** PXIe-5665/5668."""

    SEGMENTED = 2
    r"""Similar to the **Dynamic Range** method, this method also acquires a segmented spectrum, except that signal analyzer is
    not explicitly configured to provide maximum dynamic range. Use this method when the frequency separation of the two
    input tones is large and the measurement accuracy can be traded off for measurement speed.
    
    **Supported devices:** PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668."""


class IMLocalPeakSearchEnabled(Enum):
    """IMLocalPeakSearchEnabled."""

    FALSE = 0
    r"""The measurement returns the power at the tone and intermod frequencies."""

    TRUE = 1
    r"""The measurement performs a local peak search around the tone and intermod frequencies to return the peak power."""


class IMRbwFilterAutoBandwidth(Enum):
    """IMRbwFilterAutoBandwidth."""

    FALSE = 0
    r"""The measurement uses the RBW that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""

    TRUE = 1
    r"""The measurement computes the RBW."""


class IMRbwFilterType(Enum):
    """IMRbwFilterType."""

    FFT_BASED = 0
    r"""No RBW filtering is performed."""

    GAUSSIAN = 1
    r"""An RBW filter with a Gaussian response is applied."""

    FLAT = 2
    r"""An RBW filter with a flat response is applied."""


class IMSweepTimeAuto(Enum):
    """IMSweepTimeAuto."""

    FALSE = 0
    r"""The measurement uses the sweep time that you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_INTERVAL` attribute."""

    TRUE = 1
    r"""The measurement computes the sweep time based on the value of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute."""


class IMAveragingEnabled(Enum):
    """IMAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The IM measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as the number of
    acquisitions over which the IM measurement is averaged."""


class IMAveragingType(Enum):
    """IMAveragingType."""

    RMS = 0
    r"""The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor."""

    LOG = 1
    r"""The power spectrum is averaged in a logarithmic scale."""

    SCALAR = 2
    r"""The square root of the power spectrum is averaged."""

    MAXIMUM = 3
    r"""The peak power in the spectrum at each frequency bin is retained from one acquisition to the next."""

    MINIMUM = 4
    r"""The least power in the spectrum at each frequency bin is retained from one acquisition to the next."""


class IMFftWindow(Enum):
    """IMFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful
    for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class IMIFOutputPowerOffsetAuto(Enum):
    """IMIFOutputPowerOffsetAuto."""

    FALSE = 0
    r"""The measurement sets the IF output power level offset using the values of the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.NEAR_IF_OUTPUT_POWER_OFFSET` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FAR_IF_OUTPUT_POWER_OFFSET` attributes."""

    TRUE = 1
    r"""The measurement computes an IF output power level offset for the intermods to improve the dynamic range of the IM
    measurement."""


class IMAmplitudeCorrectionType(Enum):
    """IMAmplitudeCorrectionType."""

    RF_CENTER_FREQUENCY = 0
    r"""All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the
    RF center frequency."""

    SPECTRUM_FREQUENCY_BIN = 1
    r"""An Individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that
    frequency."""


class NFDutType(Enum):
    """NFDutType."""

    AMPLIFIER = 0
    r"""Specifies that the DUT only amplifies or attenuates the signal, and does not change the frequency."""

    DOWNCONVERTER = 1
    r"""Specifies that the DUT is a downconverter, that is, the IF frequency is the difference between the LO and RF
    frequencies."""

    UPCONVERTER = 2
    r"""Specifies that the DUT is an upconverter, that is, the IF frequency is the sum of LO and RF frequencies."""


class NFFrequencyConverterFrequencyContext(Enum):
    """NFFrequencyConverterFrequencyContext."""

    RF = 0
    r"""Specifies that the frequency context is RF."""

    IF = 1
    r"""Specifies that the frequency context is IF."""


class NFFrequencyConverterSideband(Enum):
    """NFFrequencyConverterSideband."""

    LSB = 0
    r"""When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is
    treated as the RF (signal) frequency while the higher is treated as the image frequency."""

    USB = 1
    r"""When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is
    treated as the image frequency while the higher is treated as the RF (signal) frequency."""


class NFAveragingEnabled(Enum):
    """NFAveragingEnabled."""

    FALSE = 0
    r"""The measurement is performed on a single acquisition."""

    TRUE = 1
    r"""The NF measurement uses the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute as
    the number of acquisitions for each frequency which you specify in the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, over which the NF measurement is averaged."""


class NFExternalPreampPresent(Enum):
    """NFExternalPreampPresent."""

    FALSE = 0
    r"""No external preamplifier present in the signal path."""

    TRUE = 1
    r"""An external preamplifier present in the signal path."""


class NFDutInputLossCompensationEnabled(Enum):
    """NFDutInputLossCompensationEnabled."""

    FALSE = 0
    r"""The NF measurement ignores the ohmic losses."""

    TRUE = 1
    r"""The NF measurement accounts for the ohmic losses."""


class NFDutOutputLossCompensationEnabled(Enum):
    """NFDutOutputLossCompensationEnabled."""

    FALSE = 0
    r"""The NF measurement ignores ohmic losses."""

    TRUE = 1
    r"""The NF measurement accounts for the ohmic losses."""


class NFCalibrationLossCompensationEnabled(Enum):
    """NFCalibrationLossCompensationEnabled."""

    FALSE = 0
    r"""The NF measurement ignores the ohmic losses."""

    TRUE = 1
    r"""The NF measurement accounts for the ohmic losses."""


class NFMeasurementMethod(Enum):
    """NFMeasurementMethod."""

    Y_FACTOR = 0
    r"""The NF measurement computes the noise figure of the DUT using a noise source with a calibrated excess-noise ratio
    (ENR).
    
    Refer to the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute for
    information about supported devices and their corresponding noise source type."""

    COLD_SOURCE = 1
    r"""The NF measurement computes the noise figure of the DUT using a 50 ohm microwave termination as the noise source.
    
    **Supported Devices:** PXIe-5644/5645/5646/5840/5841/5842/5860, PXIe-5830/5831/5832"""


class NFYFactorMode(Enum):
    """NFYFactorMode."""

    MEASURE = 0
    r"""The noise figure (NF) measurement computes the noise characteristics of the DUT, compensating for the noise figure of
    the analyzer."""

    CALIBRATE = 1
    r"""The NF measurement computes the noise characteristics of the analyzer."""


class NFYFactorNoiseSourceType(Enum):
    """NFYFactorNoiseSourceType."""

    EXTERNAL_NOISE_SOURCE = 0
    r"""The NF measurement generates noise using an external noise source, that is controlled either by an internal noise
    source power supply or an NI Source Measure Unit (SMU).
    
    **Supported Devices:** PXIe-5665 (3.6 GHz), PXIe-5668, PXIe-5644/5645/5646*, PXIe-5840*/5841*/5842*/5860*, PXIe
    5830/5831*/5832*
    
    *Use an external NI Source Measure Unit (SMU) as the noise source power supply for the Noise Figure
    measurement.
    
    During initialization, specify the SMU resource name using <span
    class="Monospace">"NoiseSourcePowerSupply"</span> as the specifier within the RFmxSetup string. For example, <span
    class="Monospace">"RFmxSetup= NoiseSourcePowerSupply:myDCPower[0]"</span> configures RFmx to use channel 0 on myDCPower
    SMU device for powering the noise source. You should allocate a dedicated SMU channel for RFmx.
    
    RFmx supports PXIe-4138, PXIe-4139, and PXIe-4139 (40 W) SMUs."""

    RF_SIGNAL_GENERATOR = 1
    r"""When you measure Y-Factor based NF using a supported NI vector signal transceiver (VST) instrument, RFmx generates
    noise using the vector signal generator (VSG) integrated into the same VST.
    
    RFmx automatically configures the vector signal generator (VSG) to generate noise at the specified bandwidth
    and ENR levels that you set using the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR` attributes.
    
    **Supported Devices:** PXIe-5842/5860"""


class NFYFactorNoiseSourceLossCompensationEnabled(Enum):
    """NFYFactorNoiseSourceLossCompensationEnabled."""

    FALSE = 0
    r"""Ohmic losses are ignored."""

    TRUE = 1
    r"""Ohmic losses are accounted for in the NF measurement."""


class NFColdSourceMode(Enum):
    """NFColdSourceMode."""

    MEASURE = 0
    r"""The noise figure (NF) measurement computes the noise characteristics of the DUT and compensates for the noise figure of
    the analyzer."""

    CALIBRATE = 1
    r"""The NF measurement computes the noise characteristics of the analyzer."""


class PhaseNoiseRangeDefinition(Enum):
    """PhaseNoiseRangeDefinition."""

    MANUAL = 0
    r"""Specify the offset sub-ranges used for the measurement. Use the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attribute to configure single or multiple range
    start and range stop frequencies."""

    AUTO = 1
    r"""Measurement computes offset sub-ranges by dividing the user configured offset range into multiple decade sub-ranges.
    The range is specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.START_FREQUENCY` and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attributes."""


class PhaseNoiseFftWindow(Enum):
    """PhaseNoiseFftWindow."""

    NONE = 0
    r"""Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate
    two tones with frequencies close to each other but with almost equal amplitudes."""

    FLAT_TOP = 1
    r"""Measures single-tone amplitudes accurately."""

    HANNING = 2
    r"""Analyzes transients for which duration is longer than the window length. You can also use this window type to provide
    better frequency resolution for noise measurements."""

    HAMMING = 3
    r"""Analyzes closely-spaced sine waves."""

    GAUSSIAN = 4
    r"""Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is
    useful for time-frequency analysis."""

    BLACKMAN = 5
    r"""Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate."""

    BLACKMAN_HARRIS = 6
    r"""Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide
    main lobe."""

    KAISER_BESSEL = 7
    r"""Separates two tones with frequencies close to each other but with widely-differing amplitudes."""


class PhaseNoiseSmoothingType(Enum):
    """PhaseNoiseSmoothingType."""

    NONE = 0
    r"""Smoothing is disabled."""

    LINEAR = 1
    r"""Performs linear moving average filtering on the measured phase noise log plot trace."""

    LOGARITHMIC = 2
    r"""Performs logarithmic moving average filtering on the measured phase noise log plot trace."""

    MEDIAN = 3
    r"""Performs moving median filtering on the measured phase noise log plot trace."""


class PhaseNoiseIntegratedNoiseRangeDefinition(Enum):
    """PhaseNoiseIntegratedNoiseRangeDefinition."""

    NONE = 0
    r"""Integrated noise measurement is not computed."""

    MEASUREMENT = 1
    r"""The complete log plot frequency range, considered as a single range, is used for computing integrated measurements."""

    CUSTOM = 2
    r"""The measurement range(s) specified by :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_START_FREQUENCY`
    attribute and the :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_STOP_FREQUENCY` attribute is used for
    computing integrated measurements."""


class PhaseNoiseSpurRemovalEnabled(Enum):
    """PhaseNoiseSpurRemovalEnabled."""

    FALSE = 0
    r"""Disables spur removal on the log plot trace."""

    TRUE = 1
    r"""Enables spur removal on the log plot trace."""


class PhaseNoiseCancellationEnabled(Enum):
    """PhaseNoiseCancellationEnabled."""

    FALSE = 0
    r"""Disables phase noise cancellation."""

    TRUE = 1
    r"""Enables phase noise cancellation."""


class PavtMeasurementLocationType(Enum):
    """PavtMeasurementLocationType."""

    TIME = 0
    r"""The measurement is performed over a single record across multiple segments separated in time. The measurement locations
    of the segments are specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_START_TIME` attribute. The
    number of segments is equal to the number of segment start times."""

    TRIGGER = 1
    r"""The measurement is performed across segments obtained in multiple records, where each record is obtained when a trigger
    is received. The number of segments is equal to the number of triggers (records)."""


class PavtMeasurementIntervalMode(Enum):
    """PavtMeasurementIntervalMode."""

    UNIFORM = 0
    r"""The time offset from the start of segment and the duration over which the measurement is performed is uniform for all
    segments and is given by the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_OFFSET` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LENGTH` attribute respectively."""

    VARIABLE = 1
    r"""The time offset from the start of segment and the duration over which the measurement is performed is configured
    separately for each segment and is given by the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_OFFSET` attribute and the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_LENGTH` attribute respectively."""


class PavtSegmentType(Enum):
    """PavtSegmentType."""

    PHASE_AND_AMPLITUDE = 0
    r"""Phase and amplitude is measured in this segment."""

    AMPLITUDE = 1
    r"""Amplitude is measured in this segment."""

    FREQUENCY_ERROR_MEASUREMENT = 2
    r"""Frequency error is measured in this segment."""


class PavtPhaseUnwrapEnabled(Enum):
    """PavtPhaseUnwrapEnabled."""

    FALSE = 0
    r"""Phase measurement results are wrapped within +/-180 degrees."""

    TRUE = 1
    r"""Phase measurement results are unwrapped."""


class PavtFrequencyOffsetCorrectionEnabled(Enum):
    """PavtFrequencyOffsetCorrectionEnabled."""

    FALSE = 0
    r"""Disables the frequency offset correction."""

    TRUE = 1
    r"""Enables the frequency offset correction. The measurement computes and corrects any frequency offset between the
    reference and the acquired waveforms."""


class PavtFrequencyTrackingEnabled(Enum):
    """PavtFrequencyTrackingEnabled."""

    FALSE = 0
    r"""Disables the drift correction for the measurement."""

    TRUE = 1
    r"""Enables the drift correction. The measurement corrects and reports the frequency offset per segment."""


class LimitedConfigurationChange(Enum):
    """LimitedConfigurationChange."""

    DISABLED = 0
    r"""This is the normal mode of RFmx operation. All configuration changes in RFmxInstr attributes or in personality
    attributes will be applied during RFmx Commit."""

    NO_CHANGE = 1
    r"""Signal configuration and RFmxInstr configuration are locked after the first Commit or Initiate of the named signal
    configuration. Any configuration change thereafter either in RFmxInstr attributes or personality attributes will not be
    considered by subsequent RFmx Commits or Initiates of this signal.  Use **No Change** if you have created named signal
    configurations for all measurement configurations but are setting some RFmxInstr attributes. Refer to the Limitations
    of the Limited Configuration Change Property topic for more details about the limitations of using this mode."""

    FREQUENCY = 2
    r"""Signal configuration, other than center frequency, external attenuation, and RFInstr configuration, is locked after
    first Commit or Initiate of the named signal configuration. Thereafter, only the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` and
    :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute value changes will be considered by
    subsequent driver Commits or Initiates of this signal.  Refer to the Limitations of the Limited Configuration Change
    Property topic for more details about the limitations of using this mode."""

    REFERENCE_LEVEL = 3
    r"""Signal configuration, other than the reference level and RFInstr configuration, is locked after first Commit or
    Initiate of the named signal configuration. Thereafter only the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute value change will be considered by subsequent
    driver Commits or Initiates of this signal. If you have configured this signal to use an IQ Power Edge Trigger, NI
    recommends that you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` to
    **Relative** so that the trigger level is automatically adjusted as you adjust the reference level. Refer to the
    Limitations of the Limited Configuration Change Property topic for more details about the limitations of using this
    mode."""

    FREQUENCY_AND_REFERENCE_LEVEL = 4
    r"""Signal configuration, other than center frequency, reference level, external attenuation, and RFInstr configuration, is
    locked after first Commit or Initiate of the named signal configuration. Thereafter only Center Frequency, Reference
    Level, and External Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of
    this signal. If you have configured this signal to use an IQ Power Edge Trigger, NI recommends you set the
    :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` to **Relative** so that the trigger
    level is automatically adjusted as you adjust the reference level. Refer to the Limitations of the Limited
    Configuration Change Property topic for more details about the limitations of using this mode."""

    SELECTED_PORTS_FREQUENCY_AND_REFERENCE_LEVEL = 5
    r"""Signal configuration, other than Selected Ports, Center frequency, Reference level, External attenuation, and RFInstr
    configuration, is locked after first Commit or Initiate of the named signal configuration. Thereafter only Selected
    Ports, Center Frequency, Reference Level, and External Attenuation attribute value changes will be considered by
    subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ Power Edge
    Trigger, NI recommends you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` to
    **Relative** so that the trigger level is automatically adjusted as you adjust the reference level. Refer to the
    Limitations of the Limited Configuration Change Property topic for more details about the limitations of using this
    mode."""


class AmpmReferenceWaveformIdleDurationPresent(Enum):
    """AmpmReferenceWaveformIdleDurationPresent."""

    FALSE = 0
    r"""The reference waveform does not contain an idle duration."""

    TRUE = 1
    r"""The reference waveform contains an idle duration."""


class DpdReferenceWaveformIdleDurationPresent(Enum):
    """DpdReferenceWaveformIdleDurationPresent."""

    FALSE = 0
    r"""The reference waveform does not contain an idle duration."""

    TRUE = 1
    r"""The reference waveform contains an idle duration."""


class MarkerNextPeak(Enum):
    """MarkerNextPeak."""

    NEXT_HIGHEST = 0
    r"""Moves the marker to the next highest peak above the threshold on the configured trace."""

    NEXT_LEFT = 1
    r"""Moves the marker to the next peak to the left of the configured trace."""

    NEXT_RIGHT = 2
    r"""Moves the marker to the next peak to the right of the configured trace."""


class MeasurementTypes(IntFlag):
    """MeasurementTypes."""

    ACP = 1 << 0
    r"""Selects ACP measurement."""

    CCDF = 1 << 1
    r"""Selects CCDF measurement."""

    CHP = 1 << 2
    r"""Selects CHP measurement."""

    FCNT = 1 << 3
    r"""Selects frequency count (Fcnt) measurement."""

    HARMONICS = 1 << 4
    r"""Selects Harmonics measurement."""

    OBW = 1 << 5
    r"""Selects OBW measurement."""

    SEM = 1 << 6
    r"""Selects SEM measurement."""

    SPECTRUM = 1 << 7
    r"""Selects Spectrum measurement."""

    SPUR = 1 << 8
    r"""Selects Spur measurement."""

    TXP = 1 << 9
    r"""Selects TXP measurement."""

    AMPM = 1 << 10
    r"""Selects AMPM measurement."""

    DPD = 1 << 11
    r"""Selects DPD measurement."""

    IQ = 1 << 12
    r"""Selects I/Q measurement."""

    IM = 1 << 13
    r"""Selects IM measurement."""

    NF = 1 << 14
    r"""Selects NF measurement."""

    PHASENOISE = 1 << 15
    r"""Selects PhaseNoise measurement."""

    PAVT = 1 << 16
    r"""Selects PAVT measurement."""

    IDPD = 1 << 17
    r"""Selects IDPD measurement."""

    POWERLIST = 1 << 18
    r""""""


class SpectrumNoiseCalibrationDataValid(Enum):
    """SpectrumNoiseCalibrationDataValid."""

    FALSE = 0
    r"""Returns false if the calibration data is not present for the specified
    configuration or if the difference between the current device temperature
    and the calibration temperature exceeds the [-5 Ã‚Â°C, 5 Ã‚Â°C] range."""

    TRUE = 1
    r"""Returns true if the calibration data is present for the configuration
    specified by the signal name in the Selector string parameter."""


class ChpNoiseCalibrationDataValid(Enum):
    """ChpNoiseCalibrationDataValid."""

    FALSE = 0
    r"""Returns false if the calibration data is not present for the specified
    configuration or if the difference between the current device temperature
    and the calibration temperature exceeds the [-5 Ã‚Â°C, 5 Ã‚Â°C] range."""

    TRUE = 1
    r"""Returns true if the calibration data is present for the configuration
    specified by the signal name in the Selector string parameter."""


class AcpNoiseCalibrationDataValid(Enum):
    """AcpNoiseCalibrationDataValid."""

    FALSE = 0
    r"""Returns false if the calibration data is not present for the specified
    configuration or if the difference between the current device temperature
    and the calibration temperature exceeds the [-5 Ã‚Â°C, 5 Ã‚Â°C] range."""

    TRUE = 1
    r"""Returns true if the calibration data is present for the configuration
    specified by the signal name in the Selector string parameter."""


class NFCalibrationDataValid(Enum):
    """NFCalibrationDataValid."""

    FALSE = 0
    r"""Calibration data is not present for one or more frequency points in the list
    or the difference between the current device temperature and the temperature
    at which calibration was performed exceeds the tolerance specified by the
    NFDeviceTemperatureTolerance method."""

    TRUE = 1
    r"""Calibration data is present for all of the frequencies in the list."""


class DpdApplyDpdIdleDurationPresent(Enum):
    """DpdApplyDpdIdleDurationPresent."""

    FALSE = 0
    r"""The reference waveform does not contain an idle duration."""

    TRUE = 1
    r"""The reference waveform contains an idle duration."""


class MarkerPeakExcursionEnabled(Enum):
    """MarkerPeakExcursionEnabled."""

    FALSE = 0
    r"""Disables the peak excursion check while finding the peaks on trace."""

    TRUE = 1
    r"""Enables the peak excursion check while finding the peaks on trace."""


class MarkerType(Enum):
    """MarkerType."""

    OFF = 0
    r"""The marker is disabled."""

    NORMAL = 1
    r"""The marker is enabled as a normal marker."""

    DELTA = 3
    r"""The marker is enabled as a delta marker."""

    FIXED = 4
    r"""The marker is enabled as a fixed marker."""


class MarkerTrace(Enum):
    """MarkerTrace."""

    ACP_SPECTRUM = 0
    r"""The marker uses the ACP spectrum trace."""

    CCDF_GAUSSIAN_PROBABILITIES_TRACE = 1
    r"""The marker uses the CCDF Gaussian probabilities trace."""

    CCDF_PROBABILITIES_TRACE = 2
    r"""The marker uses the CCDF probabilities trace."""

    CHP_SPECTRUM = 3
    r"""The marker uses the CHP spectrum trace."""

    FCNT_POWER_TRACE = 4
    r"""The marker uses the frequency count (Fcnt) power trace."""

    OBW_SPECTRUM = 5
    r"""The marker uses the OBW spectrum trace."""

    SEM_SPECTRUM = 6
    r"""The marker uses the SEM spectrum trace."""

    SPECTRUM = 7
    r"""The marker uses the Spectrum trace."""

    TXP_POWER_TRACE = 8
    r"""The marker uses the TXP power trace."""


class MarkerThresholdEnabled(Enum):
    """MarkerThresholdEnabled."""

    FALSE = 0
    r"""Disables the threshold for the trace while finding the peaks."""

    TRUE = 1
    r"""Enables the threshold for the trace while finding the peaks."""


class MarkerFunctionType(Enum):
    """MarkerFunctionType."""

    OFF = 0
    r"""The marker function is disabled."""

    BAND_POWER = 1
    r"""Band Power is computed within the specified span."""


class NFDutInputLossS2pSParameterOrientation(Enum):
    """NFDutInputLossS2pSParameterOrientation."""

    PORT1_TOWARDS_DUT = 0
    r""""""

    PORT2_TOWARDS_DUT = 1
    r""""""


class NFDutOutputLossS2pSParameterOrientation(Enum):
    """NFDutOutputLossS2pSParameterOrientation."""

    PORT1_TOWARDS_DUT = 0
    r""""""

    PORT2_TOWARDS_DUT = 1
    r""""""


class NFCalibrationLossS2pSParameterOrientation(Enum):
    """NFCalibrationLossS2pSParameterOrientation."""

    PORT1_TOWARDS_DUT = 0
    r""""""

    PORT2_TOWARDS_DUT = 1
    r""""""


class NFColdSourceDutS2pSParameterOrientation(Enum):
    """NFColdSourceDutS2pSParameterOrientation."""

    PORT1_TOWARDS_DUT = 0
    r""""""

    PORT2_TOWARDS_DUT = 1
    r""""""


class NFYFactorNoiseSourceLossS2pSParameterOrientation(Enum):
    """NFYFactorNoiseSourceLossS2pSParameterOrientation."""

    Port1_Towards_DUT = 0
    r""""""

    Port2_Towards_DUT = 1
    r""""""


class NFExternalPreampGainS2pSParameterOrientation(Enum):
    """NFExternalPreampGainS2pSParameterOrientation."""

    Port1_Towards_DUT = 0
    r""""""

    Port2_Towards_DUT = 1
    r""""""
