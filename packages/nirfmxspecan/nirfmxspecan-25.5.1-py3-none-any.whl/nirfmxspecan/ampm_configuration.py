"""Provides methods to configure the Ampm measurement."""

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


class AmpmConfiguration(object):
    """Provides methods to configure the Ampm measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Ampm measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the AMPM measurement.

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
                Specifies whether to enable the AMPM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the AMPM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the AMPM measurement.

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
                attributes.AttributeID.AMPM_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_sample_rate_mode(self, selector_string):
        r"""Gets whether the acquisition sample rate is based on the reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmMeasurementSampleRateMode):
                Specifies whether the acquisition sample rate is based on the reference waveform.

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
                attributes.AttributeID.AMPM_MEASUREMENT_SAMPLE_RATE_MODE.value,
            )
            attr_val = enums.AmpmMeasurementSampleRateMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_sample_rate_mode(self, selector_string, value):
        r"""Sets whether the acquisition sample rate is based on the reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmMeasurementSampleRateMode, int):
                Specifies whether the acquisition sample rate is based on the reference waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmMeasurementSampleRateMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_MEASUREMENT_SAMPLE_RATE_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_sample_rate(self, selector_string):
        r"""Gets the acquisition sample rate when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
        expressed in samples per second (S/s).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120,000,000.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition sample rate when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
                expressed in samples per second (S/s).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_MEASUREMENT_SAMPLE_RATE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_sample_rate(self, selector_string, value):
        r"""Sets the acquisition sample rate when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
        expressed in samples per second (S/s).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120,000,000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition sample rate when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
                expressed in samples per second (S/s).

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
                attributes.AttributeID.AMPM_MEASUREMENT_SAMPLE_RATE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_interval(self, selector_string):
        r"""Gets the duration of the reference waveform considered for the AMPM measurement. When the reference waveform
        contains an idle duration, the AMPM measurement neglects the idle samples in the reference waveform leading up to the
        start of the first active portion of the reference waveform. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100E-6.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the duration of the reference waveform considered for the AMPM measurement. When the reference waveform
                contains an idle duration, the AMPM measurement neglects the idle samples in the reference waveform leading up to the
                start of the first active portion of the reference waveform. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_MEASUREMENT_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_interval(self, selector_string, value):
        r"""Sets the duration of the reference waveform considered for the AMPM measurement. When the reference waveform
        contains an idle duration, the AMPM measurement neglects the idle samples in the reference waveform leading up to the
        start of the first active portion of the reference waveform. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100E-6.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the duration of the reference waveform considered for the AMPM measurement. When the reference waveform
                contains an idle duration, the AMPM measurement neglects the idle samples in the reference waveform leading up to the
                start of the first active portion of the reference waveform. This value is expressed in seconds.

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
                attributes.AttributeID.AMPM_MEASUREMENT_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_signal_type(self, selector_string):
        r"""Gets whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmSignalType):
                Specifies whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
                time-align the sinusoidal reference waveform to the acquired signal, set the AMPM Signal Type attribute to **Tones**,
                which switches the AMPM measurement alignment algorithm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_SIGNAL_TYPE.value
            )
            attr_val = enums.AmpmSignalType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_signal_type(self, selector_string, value):
        r"""Sets whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmSignalType, int):
                Specifies whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
                time-align the sinusoidal reference waveform to the acquired signal, set the AMPM Signal Type attribute to **Tones**,
                which switches the AMPM measurement alignment algorithm.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmSignalType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_SIGNAL_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_synchronization_method(self, selector_string):
        r"""Gets the method used for synchronization of acquired waveform with reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmSynchronizationMethod):
                Specifies the method used for synchronization of acquired waveform with reference waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_SYNCHRONIZATION_METHOD.value
            )
            attr_val = enums.AmpmSynchronizationMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_synchronization_method(self, selector_string, value):
        r"""Sets the method used for synchronization of acquired waveform with reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmSynchronizationMethod, int):
                Specifies the method used for synchronization of acquired waveform with reference waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmSynchronizationMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_SYNCHRONIZATION_METHOD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_auto_carrier_detection_enabled(self, selector_string):
        r"""Gets if auto detection of carrier offset and carrier bandwidth is enabled.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmAutoCarrierDetectionEnabled):
                Specifies if auto detection of carrier offset and carrier bandwidth is enabled.

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
                attributes.AttributeID.AMPM_AUTO_CARRIER_DETECTION_ENABLED.value,
            )
            attr_val = enums.AmpmAutoCarrierDetectionEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_auto_carrier_detection_enabled(self, selector_string, value):
        r"""Sets if auto detection of carrier offset and carrier bandwidth is enabled.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmAutoCarrierDetectionEnabled, int):
                Specifies if auto detection of carrier offset and carrier bandwidth is enabled.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmAutoCarrierDetectionEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_AUTO_CARRIER_DETECTION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_carriers(self, selector_string):
        r"""Gets the number of carriers in the reference waveform when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**.

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
                Specifies the number of carriers in the reference waveform when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_NUMBER_OF_CARRIERS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_carriers(self, selector_string, value):
        r"""Sets the number of carriers in the reference waveform when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of carriers in the reference waveform when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**.

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
                updated_selector_string, attributes.AttributeID.AMPM_NUMBER_OF_CARRIERS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_offset(self, selector_string):
        r"""Gets the carrier offset when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
        expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the carrier offset when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
                expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_CARRIER_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_offset(self, selector_string, value):
        r"""Sets the carrier offset when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
        expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the carrier offset when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
                expressed in Hz.

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
                updated_selector_string, attributes.AttributeID.AMPM_CARRIER_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_bandwidth(self, selector_string):
        r"""Gets the carrier bandwidth when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
        expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 20 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the carrier bandwidth when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
                expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_CARRIER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_bandwidth(self, selector_string, value):
        r"""Sets the carrier bandwidth when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
        expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 20 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the carrier bandwidth when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_CARRIER_DETECTION_ENABLED` attribute to **False**. This value is
                expressed in Hz.

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
                updated_selector_string, attributes.AttributeID.AMPM_CARRIER_BANDWIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_average_input_power(self, selector_string):
        r"""Gets the average power of the signal at the input port of the device under test. This value is expressed in dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dBm.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the average power of the signal at the input port of the device under test. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_DUT_AVERAGE_INPUT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_average_input_power(self, selector_string, value):
        r"""Sets the average power of the signal at the input port of the device under test. This value is expressed in dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dBm.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the average power of the signal at the input port of the device under test. This value is expressed in dBm.

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
                attributes.AttributeID.AMPM_DUT_AVERAGE_INPUT_POWER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_am_to_am_curve_fit_order(self, selector_string):
        r"""Gets the degree of the polynomial used to approximate the AM-to-AM characteristic of the device under test (DUT).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 7.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the degree of the polynomial used to approximate the AM-to-AM characteristic of the device under test (DUT).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_AM_CURVE_FIT_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_am_to_am_curve_fit_order(self, selector_string, value):
        r"""Sets the degree of the polynomial used to approximate the AM-to-AM characteristic of the device under test (DUT).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 7.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the degree of the polynomial used to approximate the AM-to-AM characteristic of the device under test (DUT).

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
                attributes.AttributeID.AMPM_AM_TO_AM_CURVE_FIT_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_am_to_am_curve_fit_type(self, selector_string):
        r"""Gets the polynomial approximation cost-function of the device under test AM-to-AM characteristic.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmAMToAMCurveFitType):
                Specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_AM_CURVE_FIT_TYPE.value
            )
            attr_val = enums.AmpmAMToAMCurveFitType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_am_to_am_curve_fit_type(self, selector_string, value):
        r"""Sets the polynomial approximation cost-function of the device under test AM-to-AM characteristic.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmAMToAMCurveFitType, int):
                Specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmAMToAMCurveFitType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_AM_TO_AM_CURVE_FIT_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_am_to_pm_curve_fit_order(self, selector_string):
        r"""Gets the degree of the polynomial used to approximate the AM-to-PM characteristic of the device under test.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 7.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the degree of the polynomial used to approximate the AM-to-PM characteristic of the device under test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_PM_CURVE_FIT_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_am_to_pm_curve_fit_order(self, selector_string, value):
        r"""Sets the degree of the polynomial used to approximate the AM-to-PM characteristic of the device under test.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 7.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the degree of the polynomial used to approximate the AM-to-PM characteristic of the device under test.

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
                attributes.AttributeID.AMPM_AM_TO_PM_CURVE_FIT_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_am_to_pm_curve_fit_type(self, selector_string):
        r"""Gets the polynomial approximation cost-function of the device under test AM-to-PM characteristic.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmAMToPMCurveFitType):
                Specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_PM_CURVE_FIT_TYPE.value
            )
            attr_val = enums.AmpmAMToPMCurveFitType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_am_to_pm_curve_fit_type(self, selector_string, value):
        r"""Sets the polynomial approximation cost-function of the device under test AM-to-PM characteristic.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmAMToPMCurveFitType, int):
                Specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmAMToPMCurveFitType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_AM_TO_PM_CURVE_FIT_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_enabled(self, selector_string):
        r"""Gets whether to enable thresholding of the acquired samples used for the AMPM measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmThresholdEnabled):
                Specifies whether to enable thresholding of the acquired samples used for the AMPM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_ENABLED.value
            )
            attr_val = enums.AmpmThresholdEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_enabled(self, selector_string, value):
        r"""Sets whether to enable thresholding of the acquired samples used for the AMPM measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmThresholdEnabled, int):
                Specifies whether to enable thresholding of the acquired samples used for the AMPM measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmThresholdEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_type(self, selector_string):
        r"""Gets the reference for the power level used for thresholding.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmThresholdType):
                Specifies the reference for the power level used for thresholding.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_TYPE.value
            )
            attr_val = enums.AmpmThresholdType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_type(self, selector_string, value):
        r"""Sets the reference for the power level used for thresholding.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmThresholdType, int):
                Specifies the reference for the power level used for thresholding.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmThresholdType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_level(self, selector_string):
        r"""Gets either the relative or absolute threshold power level, based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dB.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies either the relative or absolute threshold power level, based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_level(self, selector_string, value):
        r"""Sets either the relative or absolute threshold power level, based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies either the relative or absolute threshold power level, based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

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
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_LEVEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_definition(self, selector_string):
        r"""Gets the definition to use for thresholding acquired and reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmThresholdDefinition):
                Specifies the definition to use for thresholding acquired and reference waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_THRESHOLD_DEFINITION.value
            )
            attr_val = enums.AmpmThresholdDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_definition(self, selector_string, value):
        r"""Sets the definition to use for thresholding acquired and reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmThresholdDefinition, int):
                Specifies the definition to use for thresholding acquired and reference waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmThresholdDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_THRESHOLD_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_offset_correction_enabled(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmFrequencyOffsetCorrectionEnabled):
                Enables frequency offset correction for the measurement.

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
                attributes.AttributeID.AMPM_FREQUENCY_OFFSET_CORRECTION_ENABLED.value,
            )
            attr_val = enums.AmpmFrequencyOffsetCorrectionEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_offset_correction_enabled(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmFrequencyOffsetCorrectionEnabled, int):
                Enables frequency offset correction for the measurement.

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
                value.value if type(value) is enums.AmpmFrequencyOffsetCorrectionEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_FREQUENCY_OFFSET_CORRECTION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iq_origin_offset_correction_enabled(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmIQOriginOffsetCorrectionEnabled):
                Enables IQ origin offset correction for the measurement.

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
                attributes.AttributeID.AMPM_IQ_ORIGIN_OFFSET_CORRECTION_ENABLED.value,
            )
            attr_val = enums.AmpmIQOriginOffsetCorrectionEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iq_origin_offset_correction_enabled(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmIQOriginOffsetCorrectionEnabled, int):
                Enables IQ origin offset correction for the measurement.

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
                value.value if type(value) is enums.AmpmIQOriginOffsetCorrectionEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_IQ_ORIGIN_OFFSET_CORRECTION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_am_to_am_enabled(self, selector_string):
        r"""Gets whether to enable the results that rely on the AM to AM characteristics.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmAMToAMEnabled):
                Specifies whether to enable the results that rely on the AM to AM characteristics.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_AM_ENABLED.value
            )
            attr_val = enums.AmpmAMToAMEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_am_to_am_enabled(self, selector_string, value):
        r"""Sets whether to enable the results that rely on the AM to AM characteristics.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmAMToAMEnabled, int):
                Specifies whether to enable the results that rely on the AM to AM characteristics.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmAMToAMEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_AM_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_am_to_pm_enabled(self, selector_string):
        r"""Gets whether to enable the results that rely on AM to PM characteristics.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmAMToPMEnabled):
                Specifies whether to enable the results that rely on AM to PM characteristics.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_PM_ENABLED.value
            )
            attr_val = enums.AmpmAMToPMEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_am_to_pm_enabled(self, selector_string, value):
        r"""Sets whether to enable the results that rely on AM to PM characteristics.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmAMToPMEnabled, int):
                Specifies whether to enable the results that rely on AM to PM characteristics.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmAMToPMEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AM_TO_PM_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_evm_enabled(self, selector_string):
        r"""Gets whether to enable the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_RMS_EVM` attribute.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmEvmEnabled):
                Specifies whether to enable the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_RMS_EVM` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_EVM_ENABLED.value
            )
            attr_val = enums.AmpmEvmEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_evm_enabled(self, selector_string, value):
        r"""Sets whether to enable the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_RMS_EVM` attribute.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmEvmEnabled, int):
                Specifies whether to enable the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEAN_RMS_EVM` attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmEvmEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_EVM_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_equalizer_mode(self, selector_string):
        r"""Gets whether the measurement equalizes the channel.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmEqualizerMode):
                Specifies whether the measurement equalizes the channel.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_EQUALIZER_MODE.value
            )
            attr_val = enums.AmpmEqualizerMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_equalizer_mode(self, selector_string, value):
        r"""Sets whether the measurement equalizes the channel.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmEqualizerMode, int):
                Specifies whether the measurement equalizes the channel.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmEqualizerMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_EQUALIZER_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_equalizer_filter_length(self, selector_string):
        r"""Gets the length of the equalizer filter. The measurement maintains the filter length as an odd number by
        incrementing any even numbered value by one.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 21.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the length of the equalizer filter. The measurement maintains the filter length as an odd number by
                incrementing any even numbered value by one.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_EQUALIZER_FILTER_LENGTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_equalizer_filter_length(self, selector_string, value):
        r"""Sets the length of the equalizer filter. The measurement maintains the filter length as an odd number by
        incrementing any even numbered value by one.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 21.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the length of the equalizer filter. The measurement maintains the filter length as an odd number by
                incrementing any even numbered value by one.

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
                attributes.AttributeID.AMPM_EQUALIZER_FILTER_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the AMPM measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmAveragingEnabled):
                Specifies whether to enable averaging for the AMPM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AVERAGING_ENABLED.value
            )
            attr_val = enums.AmpmAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the AMPM measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmAveragingEnabled, int):
                Specifies whether to enable averaging for the AMPM measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AVERAGING_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_count(self, selector_string):
        r"""Gets the number of acquisitions used for averaging when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

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
                Specifies the number of acquisitions used for averaging when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_AVERAGING_COUNT.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_count(self, selector_string, value):
        r"""Sets the number of acquisitions used for averaging when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of acquisitions used for averaging when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

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
                updated_selector_string, attributes.AttributeID.AMPM_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_compression_point_enabled(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmCompressionPointEnabled):
                Enables computation of compression points corresponding to the respective compression levels specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_COMPRESSION_POINT_ENABLED.value
            )
            attr_val = enums.AmpmCompressionPointEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_compression_point_enabled(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmCompressionPointEnabled, int):
                Enables computation of compression points corresponding to the respective compression levels specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmCompressionPointEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_COMPRESSION_POINT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_compression_point_level(self, selector_string):
        r"""Gets the compression levels for which the compression points are computed when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the compression levels for which the compression points are computed when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.AMPM_COMPRESSION_POINT_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_compression_point_level(self, selector_string, value):
        r"""Sets the compression levels for which the compression points are computed when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the compression levels for which the compression points are computed when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_ENABLED` attribute to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.AMPM_COMPRESSION_POINT_LEVEL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_compression_point_gain_reference(self, selector_string):
        r"""Gets the gain reference for compression point calculation.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmCompressionPointGainReference):
                Specifies the gain reference for compression point calculation.

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
                attributes.AttributeID.AMPM_COMPRESSION_POINT_GAIN_REFERENCE.value,
            )
            attr_val = enums.AmpmCompressionPointGainReference(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_compression_point_gain_reference(self, selector_string, value):
        r"""Sets the gain reference for compression point calculation.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmCompressionPointGainReference, int):
                Specifies the gain reference for compression point calculation.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmCompressionPointGainReference else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_COMPRESSION_POINT_GAIN_REFERENCE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_compression_point_gain_reference_power(self, selector_string):
        r"""Gets the reference power corresponding to the gain reference to be used for compression point calculation when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **Reference
        Power**. The reference power can be configured as either input or output power based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute. This value is expressed in dBm.

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
                Specifies the reference power corresponding to the gain reference to be used for compression point calculation when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **Reference
                Power**. The reference power can be configured as either input or output power based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute. This value is expressed in dBm.

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
                attributes.AttributeID.AMPM_COMPRESSION_POINT_GAIN_REFERENCE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_compression_point_gain_reference_power(self, selector_string, value):
        r"""Sets the reference power corresponding to the gain reference to be used for compression point calculation when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **Reference
        Power**. The reference power can be configured as either input or output power based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute. This value is expressed in dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the reference power corresponding to the gain reference to be used for compression point calculation when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **Reference
                Power**. The reference power can be configured as either input or output power based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute. This value is expressed in dBm.

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
                attributes.AttributeID.AMPM_COMPRESSION_POINT_GAIN_REFERENCE_POWER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_compression_point_user_gain(self, selector_string):
        r"""Gets the gain to be used as the gain reference for compression point calculation when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **User Defined**. This
        value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 20.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the gain to be used as the gain reference for compression point calculation when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **User Defined**. This
                value is expressed in dB.

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
                attributes.AttributeID.AMPM_COMPRESSION_POINT_USER_GAIN.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_compression_point_user_gain(self, selector_string, value):
        r"""Sets the gain to be used as the gain reference for compression point calculation when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **User Defined**. This
        value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the gain to be used as the gain reference for compression point calculation when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute to **User Defined**. This
                value is expressed in dB.

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
                attributes.AttributeID.AMPM_COMPRESSION_POINT_USER_GAIN.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_maximum_timing_error(self, selector_string):
        r"""Gets the maximum time alignment error expected between the acquired and the reference waveforms. This value is
        expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.00002.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the maximum time alignment error expected between the acquired and the reference waveforms. This value is
                expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_MAXIMUM_TIMING_ERROR.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_maximum_timing_error(self, selector_string, value):
        r"""Sets the maximum time alignment error expected between the acquired and the reference waveforms. This value is
        expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.00002.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the maximum time alignment error expected between the acquired and the reference waveforms. This value is
                expressed in seconds.

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
                attributes.AttributeID.AMPM_MAXIMUM_TIMING_ERROR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_reference_power_type(self, selector_string):
        r"""Gets the reference power used for AM to AM and AM to PM traces.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AmpmReferencePowerType):
                Specifies the reference power used for AM to AM and AM to PM traces.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_REFERENCE_POWER_TYPE.value
            )
            attr_val = enums.AmpmReferencePowerType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_reference_power_type(self, selector_string, value):
        r"""Sets the reference power used for AM to AM and AM to PM traces.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AmpmReferencePowerType, int):
                Specifies the reference power used for AM to AM and AM to PM traces.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AmpmReferencePowerType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.AMPM_REFERENCE_POWER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the AMPM measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the AMPM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.AMPM_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the AMPM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the AMPM measurement.

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
                updated_selector_string, attributes.AttributeID.AMPM_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for the AMPM measurement.

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
                Specifies the maximum number of threads used for parallelism for the AMPM measurement.

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
                attributes.AttributeID.AMPM_NUMBER_OF_ANALYSIS_THREADS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for the AMPM measurement.

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
                Specifies the maximum number of threads used for parallelism for the AMPM measurement.

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
                attributes.AttributeID.AMPM_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_am_to_am_curve_fit(
        self, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
    ):
        r"""Configures the degree of the polynomial and the cost-function for approximating the measured AM-to-AM response of the
        device under test.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            am_to_am_curve_fit_order (int):
                This parameter specifies the degree of the polynomial used to approximate the AM-to-AM characteristic of the device
                under test. The default value is 7.

            am_to_am_curve_fit_type (enums.AmpmAMToAMCurveFitType, int):
                This parameter specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic.
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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            am_to_am_curve_fit_type = (
                am_to_am_curve_fit_type.value
                if type(am_to_am_curve_fit_type) is enums.AmpmAMToAMCurveFitType
                else am_to_am_curve_fit_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_am_to_am_curve_fit(
                updated_selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_am_to_pm_curve_fit(
        self, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
    ):
        r"""Configures the degree of the polynomial and the cost-function, for approximating the measured AM-to-PM response of the
        device under test.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            am_to_pm_curve_fit_order (int):
                This parameter specifies the degree of the polynomial used to approximate the AM-to-PM characteristic of the device
                under test. The default value is 7.

            am_to_pm_curve_fit_type (enums.AmpmAMToPMCurveFitType, int):
                This parameter specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic.
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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            am_to_pm_curve_fit_type = (
                am_to_pm_curve_fit_type.value
                if type(am_to_pm_curve_fit_type) is enums.AmpmAMToPMCurveFitType
                else am_to_pm_curve_fit_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_am_to_pm_curve_fit(
                updated_selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(self, selector_string, averaging_enabled, averaging_count):
        r"""Configures averaging for the AMPM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.AmpmAveragingEnabled, int):
                This parameter specifies whether to enable averaging for the measurement. The default value is **False**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | The measurement is performed on a single acquisition.                                                                    |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement uses the value of the Averaging Count parameter to calculate the number of acquisitions over which the   |
                |              | measurement is averaged.                                                                                                 |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            averaging_count (int):
                This parameter specifies the number of acquisitions used for averaging when you set the **Averaging Enabled** parameter
                to **True**. The default value is 10.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            averaging_enabled = (
                averaging_enabled.value
                if type(averaging_enabled) is enums.AmpmAveragingEnabled
                else averaging_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_compression_points(
        self, selector_string, compression_point_enabled, compression_level
    ):
        r"""Configures the compression point computation.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            compression_point_enabled (enums.AmpmCompressionPointEnabled, int):
                This parameter enables computation of compression points corresponding to the compression levels specified by the
                **Compression Level** parameter.

            compression_level (float):
                This parameter specifies the compression levels for which the compression points are computed when the **Compression
                Point Enabled** parameter is set to **True**. This value is expressed in dB.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            compression_point_enabled = (
                compression_point_enabled.value
                if type(compression_point_enabled) is enums.AmpmCompressionPointEnabled
                else compression_point_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_compression_points(
                updated_selector_string, compression_point_enabled, compression_level
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_dut_average_input_power(self, selector_string, dut_average_input_power):
        r"""Configures the average power, in dBm, of the signal at the input port of the device under test.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_average_input_power (float):
                This parameter specifies the average power, in dBm, of the signal at the input port of the device under test. The
                default value is -20 dBm.

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
            error_code = self._interpreter.ampm_configure_dut_average_input_power(
                updated_selector_string, dut_average_input_power
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval(self, selector_string, measurement_interval):
        r"""Configures the acquisition time, in seconds, for the AMPM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_interval (float):
                This parameter specifies the duration, in seconds, of the reference waveform considered for the measurement. When the
                reference waveform contains an idle duration, the measurement neglects the idle samples in the reference waveform
                leading up to the start of the first active portion of the reference waveform. The default value is 100E-6.

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
            error_code = self._interpreter.ampm_configure_measurement_interval(
                updated_selector_string, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_sample_rate(self, selector_string, sample_rate_mode, sample_rate):
        r"""Configures the acquisition sample rate, in Samples per second (S/s),  for the AMPM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            sample_rate_mode (enums.AmpmMeasurementSampleRateMode, int):
                This parameter specifies whether the acquisition sample rate is based on the reference waveform. The default value is
                **Reference Waveform**.

                +------------------------+----------------------------------------------------------------------------------------+
                | Name (Value)           | Description                                                                            |
                +========================+========================================================================================+
                | User (0)               | The acquisition sample rate is defined by the value of the Sample Rate parameter.      |
                +------------------------+----------------------------------------------------------------------------------------+
                | Reference Waveform (1) | The acquisition sample rate is set to match the sample rate of the reference waveform. |
                +------------------------+----------------------------------------------------------------------------------------+

            sample_rate (float):
                This parameter specifies the acquisition sample rate, in S/s, when you set the **Sample Rate Mode** parameter to
                **User**. The default value is 120 MHz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            sample_rate_mode = (
                sample_rate_mode.value
                if type(sample_rate_mode) is enums.AmpmMeasurementSampleRateMode
                else sample_rate_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_measurement_sample_rate(
                updated_selector_string, sample_rate_mode, sample_rate
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_power_type(self, selector_string, reference_power_type):
        r"""Configures the reference power to be used for AM to AM and AM to PM traces.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            reference_power_type (enums.AmpmReferencePowerType, int):
                This parameter specifies the reference power used for AM to AM and AM to PM traces. The default value is **Input**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Input (0)    | The instantaneous powers at the input port of the device under test (DUT) forms the x-axis of AM to AM and AM to PM      |
                |              | traces.                                                                                                                  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Output (1)   | The instantaneous powers at the output port of the DUT forms the x-axis of AM to AM and AM to PM traces.                 |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            reference_power_type = (
                reference_power_type.value
                if type(reference_power_type) is enums.AmpmReferencePowerType
                else reference_power_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_reference_power_type(
                updated_selector_string, reference_power_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_waveform(
        self, selector_string, x0, dx, reference_waveform, idle_duration_present, signal_type
    ):
        r"""Configures the reference waveform and its attributes for the AMPM measurement.

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

            idle_duration_present (enums.AmpmReferenceWaveformIdleDurationPresent, int):
                This parameter specifies whether the reference waveform contains an idle duration. The default value is **False**.

                +--------------+-----------------------------------------------------------+
                | Name (Value) | Description                                               |
                +==============+===========================================================+
                | False (0)    | The reference waveform does not contain an idle duration. |
                +--------------+-----------------------------------------------------------+
                | True (1)     | The reference waveform contains an idle duration.         |
                +--------------+-----------------------------------------------------------+

            signal_type (enums.AmpmSignalType, int):
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
                if type(idle_duration_present) is enums.AmpmReferenceWaveformIdleDurationPresent
                else idle_duration_present
            )
            signal_type = (
                signal_type.value if type(signal_type) is enums.AmpmSignalType else signal_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_reference_waveform(
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
    def configure_synchronization_method(self, selector_string, synchronization_method):
        r"""Configures the synchronization method used to synchronize the reference waveform and acquired waveform.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            synchronization_method (enums.AmpmSynchronizationMethod, int):
                This parameter specifies the method used for time-synchronization of acquired waveform with reference waveform.

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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            synchronization_method = (
                synchronization_method.value
                if type(synchronization_method) is enums.AmpmSynchronizationMethod
                else synchronization_method
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_synchronization_method(
                updated_selector_string, synchronization_method
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        r"""Configures the threshold level for the samples that need to be considered for the AMPM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            threshold_enabled (enums.AmpmThresholdEnabled, int):
                This parameter specifies whether to enable thresholding of the acquired samples to be used for the measurement. The
                default value is **False**.

                +--------------+----------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                          |
                +==============+======================================================================================================================+
                | False (0)    | All samples are considered for the measurement.                                                                      |
                +--------------+----------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The samples above the threshold level specified in the Threshold Level parameter are considered for the measurement. |
                +--------------+----------------------------------------------------------------------------------------------------------------------+

            threshold_level (float):
                This parameter specifies either the relative or absolute threshold power level based on the value of the **Threshold
                Type** parameter. The default value is -20 dB.

            threshold_type (enums.AmpmThresholdType, int):
                This parameter specifies the reference for the power level used for thresholding. The default value is **Relative**.

                +--------------+------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                  |
                +==============+==============================================================================+
                | Relative (0) | The threshold is relative to the peak power, in dB, of the acquired samples. |
                +--------------+------------------------------------------------------------------------------+
                | Absolute (1) | The threshold is the absolute power, in dBm.                                 |
                +--------------+------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            threshold_enabled = (
                threshold_enabled.value
                if type(threshold_enabled) is enums.AmpmThresholdEnabled
                else threshold_enabled
            )
            threshold_type = (
                threshold_type.value
                if type(threshold_type) is enums.AmpmThresholdType
                else threshold_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.ampm_configure_threshold(
                updated_selector_string, threshold_enabled, threshold_level, threshold_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
