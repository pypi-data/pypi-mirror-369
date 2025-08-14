"""Provides methods to configure the Idpd measurement."""

import functools

import nirfmxspecan.attributes as attributes
import nirfmxspecan.enums as enums
import nirfmxspecan.errors as errors
import nirfmxspecan.internal._helper as _helper


def _raise_if_disposed(f):
    """From https://stackoverflow.com/questions/5929107/decorators-with-parameters."""

    @functools.wraps(f)
    def aux(*xs, **kws):
        meas_obj = xs[0]  # parameter 0 is 'self' which is the measurement object
        if meas_obj._signal_obj.is_disposed:
            raise Exception("Cannot access a disposed SpecAn signal configuration")
        return f(*xs, **kws)

    return aux


class IdpdConfiguration(object):
    """Provides methods to configure the Idpd measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Idpd measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable IDPD measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable IDPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable IDPD measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable IDPD measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_equalizer_mode(self, selector_string):
        r"""Gets whether to enable equalization.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdEqualizerMode):
                Specifies whether to enable equalization.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EQUALIZER_MODE.value
            )
            attr_val = enums.IdpdEqualizerMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_equalizer_mode(self, selector_string, value):
        r"""Sets whether to enable equalization.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdEqualizerMode, int):
                Specifies whether to enable equalization.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IdpdEqualizerMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EQUALIZER_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_equalizer_filter_length(self, selector_string):
        r"""Gets the length of the equalizer filter to be trained.

        This attribute is applicable when you set :py:attr:`~nirfmxspecan.attributes.AttributeID.EQUALIZER_MODE` to
        **Train**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 101.
        Valid values are 1 to 4096, inclusive.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the length of the equalizer filter to be trained.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EQUALIZER_FILTER_LENGTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_equalizer_filter_length(self, selector_string, value):
        r"""Sets the length of the equalizer filter to be trained.

        This attribute is applicable when you set :py:attr:`~nirfmxspecan.attributes.AttributeID.EQUALIZER_MODE` to
        **Train**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 101.
        Valid values are 1 to 4096, inclusive.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the length of the equalizer filter to be trained.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_EQUALIZER_FILTER_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_sample_rate_mode(self, selector_string):
        r"""Gets acquisition sample rate configuration mode.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdMeasurementSampleRateMode):
                Specifies acquisition sample rate configuration mode.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_MEASUREMENT_SAMPLE_RATE_MODE.value,
            )
            attr_val = enums.IdpdMeasurementSampleRateMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_sample_rate_mode(self, selector_string, value):
        r"""Sets acquisition sample rate configuration mode.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdMeasurementSampleRateMode, int):
                Specifies acquisition sample rate configuration mode.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IdpdMeasurementSampleRateMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_MEASUREMENT_SAMPLE_RATE_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_sample_rate(self, selector_string):
        r"""Gets the acquisition sample rate, in S/s, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` is **User.**

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120000000.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition sample rate, in S/s, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` is **User.**

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_MEASUREMENT_SAMPLE_RATE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_sample_rate(self, selector_string, value):
        r"""Sets the acquisition sample rate, in S/s, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` is **User.**

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120000000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition sample rate, in S/s, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` is **User.**

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_MEASUREMENT_SAMPLE_RATE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_signal_type(self, selector_string):
        r"""Gets the type of reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdSignalType):
                Specifies the type of reference waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_SIGNAL_TYPE.value
            )
            attr_val = enums.IdpdSignalType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_signal_type(self, selector_string, value):
        r"""Sets the type of reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdSignalType, int):
                Specifies the type of reference waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IdpdSignalType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_SIGNAL_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_reference_waveform_idle_duration_present(self, selector_string):
        r"""Gets whether the reference waveform contains idle duration or dead time.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdReferenceWaveformIdleDurationPresent):
                Specifies whether the reference waveform contains idle duration or dead time.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_REFERENCE_WAVEFORM_IDLE_DURATION_PRESENT.value,
            )
            attr_val = enums.IdpdReferenceWaveformIdleDurationPresent(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_reference_waveform_idle_duration_present(self, selector_string, value):
        r"""Sets whether the reference waveform contains idle duration or dead time.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdReferenceWaveformIdleDurationPresent, int):
                Specifies whether the reference waveform contains idle duration or dead time.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = (
                value.value
                if type(value) is enums.IdpdReferenceWaveformIdleDurationPresent
                else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_REFERENCE_WAVEFORM_IDLE_DURATION_PRESENT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_average_input_power(self, selector_string):
        r"""Gets the initial (first itertion) average power of the signal at the input port of the device under test.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the initial (first itertion) average power of the signal at the input port of the device under test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_DUT_AVERAGE_INPUT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_average_input_power(self, selector_string, value):
        r"""Sets the initial (first itertion) average power of the signal at the input port of the device under test.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the initial (first itertion) average power of the signal at the input port of the device under test.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_DUT_AVERAGE_INPUT_POWER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the IDPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdAveragingEnabled):
                Specifies whether to enable averaging for the IDPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_AVERAGING_ENABLED.value
            )
            attr_val = enums.IdpdAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the IDPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdAveragingEnabled, int):
                Specifies whether to enable averaging for the IDPD measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IdpdAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_AVERAGING_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_count(self, selector_string):
        r"""Gets the number of acquisitions used for averaging when
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` is **TRUE**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of acquisitions used for averaging when
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` is **TRUE**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_AVERAGING_COUNT.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_count(self, selector_string, value):
        r"""Sets the number of acquisitions used for averaging when
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` is **TRUE**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of acquisitions used for averaging when
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` is **TRUE**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_evm_enabled(self, selector_string):
        r"""Gets whether to enable EVM computation.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdEvmEnabled):
                Specifies whether to enable EVM computation.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EVM_ENABLED.value
            )
            attr_val = enums.IdpdEvmEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_evm_enabled(self, selector_string, value):
        r"""Sets whether to enable EVM computation.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdEvmEnabled, int):
                Specifies whether to enable EVM computation.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IdpdEvmEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EVM_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_evm_unit(self, selector_string):
        r"""Gets the units of the EVM results.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IdpdEvmUnit):
                Specifies the units of the EVM results.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EVM_UNIT.value
            )
            attr_val = enums.IdpdEvmUnit(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_evm_unit(self, selector_string, value):
        r"""Sets the units of the EVM results.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IdpdEvmUnit, int):
                Specifies the units of the EVM results.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IdpdEvmUnit else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_EVM_UNIT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_impairment_estimation_start(self, selector_string):
        r"""Gets the start time of the impairment estimation interval relative to the start of the reference waveform. This
        value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start time of the impairment estimation interval relative to the start of the reference waveform. This
                value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_IMPAIRMENT_ESTIMATION_START.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_impairment_estimation_start(self, selector_string, value):
        r"""Sets the start time of the impairment estimation interval relative to the start of the reference waveform. This
        value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start time of the impairment estimation interval relative to the start of the reference waveform. This
                value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_IMPAIRMENT_ESTIMATION_START.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_impairment_estimation_stop(self, selector_string):
        r"""Gets the stop time of the impairment estimation interval relative to the start of the reference waveform. This
        value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the stop time of the impairment estimation interval relative to the start of the reference waveform. This
                value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_IMPAIRMENT_ESTIMATION_STOP.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_impairment_estimation_stop(self, selector_string, value):
        r"""Sets the stop time of the impairment estimation interval relative to the start of the reference waveform. This
        value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the stop time of the impairment estimation interval relative to the start of the reference waveform. This
                value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_IMPAIRMENT_ESTIMATION_STOP.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_synchronization_estimation_start(self, selector_string):
        r"""Gets the start time of the synchronization estimation interval relative to the start of the reference waveform.
        This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start time of the synchronization estimation interval relative to the start of the reference waveform.
                This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_SYNCHRONIZATION_ESTIMATION_START.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_synchronization_estimation_start(self, selector_string, value):
        r"""Sets the start time of the synchronization estimation interval relative to the start of the reference waveform.
        This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start time of the synchronization estimation interval relative to the start of the reference waveform.
                This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_SYNCHRONIZATION_ESTIMATION_START.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_synchronization_estimation_stop(self, selector_string):
        r"""Gets the stop time of the synchronization estimation interval relative to the start of the reference waveform.
        This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the stop time of the synchronization estimation interval relative to the start of the reference waveform.
                This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_SYNCHRONIZATION_ESTIMATION_STOP.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_synchronization_estimation_stop(self, selector_string, value):
        r"""Sets the stop time of the synchronization estimation interval relative to the start of the reference waveform.
        This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the stop time of the synchronization estimation interval relative to the start of the reference waveform.
                This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_SYNCHRONIZATION_ESTIMATION_STOP.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_gain_expansion(self, selector_string):
        r"""Gets the increase of input power relative to the peak power value of the reference signal. This value is expressed
        in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 6.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the increase of input power relative to the peak power value of the reference signal. This value is expressed
                in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_GAIN_EXPANSION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_gain_expansion(self, selector_string, value):
        r"""Sets the increase of input power relative to the peak power value of the reference signal. This value is expressed
        in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 6.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the increase of input power relative to the peak power value of the reference signal. This value is expressed
                in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_GAIN_EXPANSION.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_target_gain(self, selector_string):
        r"""Gets the Target gain when the configured pre-distorted waveform is non-empty.

        When the configured pre-distorted waveform is empty, this attribute is ignored. It is recommended to use the
        Gain result from the previous iteration to configure this attribute.

        The default value is 20.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the Target gain when the configured pre-distorted waveform is non-empty.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_TARGET_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_target_gain(self, selector_string, value):
        r"""Sets the Target gain when the configured pre-distorted waveform is non-empty.

        When the configured pre-distorted waveform is empty, this attribute is ignored. It is recommended to use the
        Gain result from the previous iteration to configure this attribute.

        The default value is 20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the Target gain when the configured pre-distorted waveform is non-empty.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_TARGET_GAIN.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_power_linearity_tradeoff(self, selector_string):
        r"""Gets the gain tradeoff factor that sets the gain expected from the DUT after applying IDPD on the input waveform.
        This value is expressed as a percentage.

        The percentages zero corresponds to the gain at maximum linearity, hundred corresponds to the gain at maximum
        power, and fifty corresponds to the gain at average power output from the DUT.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 50.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the gain tradeoff factor that sets the gain expected from the DUT after applying IDPD on the input waveform.
                This value is expressed as a percentage.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_POWER_LINEARITY_TRADEOFF.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_power_linearity_tradeoff(self, selector_string, value):
        r"""Sets the gain tradeoff factor that sets the gain expected from the DUT after applying IDPD on the input waveform.
        This value is expressed as a percentage.

        The percentages zero corresponds to the gain at maximum linearity, hundred corresponds to the gain at maximum
        power, and fifty corresponds to the gain at average power output from the DUT.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 50.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the gain tradeoff factor that sets the gain expected from the DUT after applying IDPD on the input waveform.
                This value is expressed as a percentage.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.IDPD_POWER_LINEARITY_TRADEOFF.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the IDPD measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the IDPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the IDPD measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the IDPD measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IDPD_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_numberof_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for the IDPD measurement.

        The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
        may not be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum number of threads used for parallelism for the IDPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_NUMBER_OF_ANALYSIS_THREADS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_numberof_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for the IDPD measurement.

        The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
        may not be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of threads used for parallelism for the IDPD measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IDPD_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_waveform(
        self, selector_string, x0, dx, reference_waveform, idle_duration_present, signal_type
    ):
        r"""Configures the reference waveform for the IDPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            x0 (float):
                This parameter specifies the start time, in seconds.

            dx (float):
                This parameter specifies the sample duration, in seconds.

            reference_waveform (numpy.complex64):
                This parameter specifies the complex baseband samples, in volts.

            idle_duration_present (enums.IdpdReferenceWaveformIdleDurationPresent, int):
                This parameter specifies whether the reference waveform contains an idle duration. The default value is **False**.

                +--------------+-----------------------------------------------------------+
                | Name (Value) | Description                                               |
                +==============+===========================================================+
                | False (0)    | The reference waveform does not contain an idle duration. |
                +--------------+-----------------------------------------------------------+
                | True (1)     | The reference waveform contains an idle duration.         |
                +--------------+-----------------------------------------------------------+

            signal_type (enums.IdpdSignalType, int):
                This parameter specifies whether the reference waveform is a modulated signal or tones. The default value is
                **Modulated**.

                +---------------+-------------------------------------------------------------------------------+
                | Name (Value)  | Description                                                                   |
                +===============+===============================================================================+
                | Modulated (0) | The reference waveform is a cellular or connectivity standard signal.         |
                +---------------+-------------------------------------------------------------------------------+
                | Tones (1)     | The reference waveform is continuous signals comprising of one or more tones. |
                +---------------+-------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            idle_duration_present = (
                idle_duration_present.value
                if type(idle_duration_present) is enums.IdpdReferenceWaveformIdleDurationPresent
                else idle_duration_present
            )
            signal_type = (
                signal_type.value if type(signal_type) is enums.IdpdSignalType else signal_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.idpd_configure_reference_waveform(
                updated_selector_string,
                x0,
                dx,
                reference_waveform,
                idle_duration_present,
                signal_type,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_predistorted_waveform(
        self, selector_string, x0, dx, predistorted_waveform, target_gain
    ):
        r"""Configures the predistorted waveform for the IDPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            x0 (float):
                This parameter specifies the start time, in seconds.

            dx (float):
                This parameter specifies the sample duration, in seconds.

            predistorted_waveform (numpy.complex64):
                This parameter specifies the complex baseband samples, in volts.

            target_gain (float):
                This parameter specifies the target gain when the configured pre-distorted waveform is non-empty. This value is
                expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.idpd_configure_predistorted_waveform(
                updated_selector_string, x0, dx, predistorted_waveform, target_gain
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_equalizer_coefficients(self, selector_string, x0, dx, equalizer_coefficients):
        r"""Configures the equalizer coefficients for the IDPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            x0 (float):
                This parameter always pass 0 to this parameter. Any other values are ignored.

            dx (float):
                This parameter specifies the spacing between the coefficients.

            equalizer_coefficients (numpy.complex64):
                This parameter specifies the coefficients to be used by the equalizer.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.idpd_configure_equalizer_coefficients(
                updated_selector_string, x0, dx, equalizer_coefficients
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
