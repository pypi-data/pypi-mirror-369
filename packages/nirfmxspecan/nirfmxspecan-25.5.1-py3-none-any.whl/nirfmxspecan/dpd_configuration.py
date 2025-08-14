"""Provides methods to configure the Dpd measurement."""

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


class DpdConfiguration(object):
    """Provides methods to configure the Dpd measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Dpd measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable DPD measurement.

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
                Specifies whether to enable DPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable DPD measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable DPD measurement.

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
                updated_selector_string, attributes.AttributeID.DPD_MEASUREMENT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_sample_rate_mode(self, selector_string):
        r"""Gets the acquisition sample rate configuration mode.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdMeasurementSampleRateMode):
                Specifies the acquisition sample rate configuration mode.

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
                attributes.AttributeID.DPD_MEASUREMENT_SAMPLE_RATE_MODE.value,
            )
            attr_val = enums.DpdMeasurementSampleRateMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_sample_rate_mode(self, selector_string, value):
        r"""Sets the acquisition sample rate configuration mode.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdMeasurementSampleRateMode, int):
                Specifies the acquisition sample rate configuration mode.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdMeasurementSampleRateMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_MEASUREMENT_SAMPLE_RATE_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_sample_rate(self, selector_string):
        r"""Gets the acquisition sample rate when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
        expressed in Samples per second (S/s).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition sample rate when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
                expressed in Samples per second (S/s).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_MEASUREMENT_SAMPLE_RATE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_sample_rate(self, selector_string, value):
        r"""Sets the acquisition sample rate when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
        expressed in Samples per second (S/s).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition sample rate when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_SAMPLE_RATE_MODE` attribute to **User**. This value is
                expressed in Samples per second (S/s).

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
                attributes.AttributeID.DPD_MEASUREMENT_SAMPLE_RATE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_interval(self, selector_string):
        r"""Gets the duration of the reference waveform considered for the DPD measurement. When the reference waveform
        contains an idle duration, the DPD measurement neglects the idle samples in the reference waveform leading up to the
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
                Specifies the duration of the reference waveform considered for the DPD measurement. When the reference waveform
                contains an idle duration, the DPD measurement neglects the idle samples in the reference waveform leading up to the
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
                updated_selector_string, attributes.AttributeID.DPD_MEASUREMENT_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_interval(self, selector_string, value):
        r"""Sets the duration of the reference waveform considered for the DPD measurement. When the reference waveform
        contains an idle duration, the DPD measurement neglects the idle samples in the reference waveform leading up to the
        start of the first active portion of the reference waveform. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100E-6.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the duration of the reference waveform considered for the DPD measurement. When the reference waveform
                contains an idle duration, the DPD measurement neglects the idle samples in the reference waveform leading up to the
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
                attributes.AttributeID.DPD_MEASUREMENT_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_signal_type(self, selector_string):
        r"""Gets whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdSignalType):
                Specifies whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
                time-align the sinusoidal reference waveform to the acquired signal, set the DPD Signal Type attribute to **Tones**,
                which switches the DPD measurement alignment algorithm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_SIGNAL_TYPE.value
            )
            attr_val = enums.DpdSignalType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_signal_type(self, selector_string, value):
        r"""Sets whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdSignalType, int):
                Specifies whether the reference waveform is a modulated signal or a combination of one or more sinusoidal signals. To
                time-align the sinusoidal reference waveform to the acquired signal, set the DPD Signal Type attribute to **Tones**,
                which switches the DPD measurement alignment algorithm.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdSignalType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_SIGNAL_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_synchronization_method(self, selector_string):
        r"""Gets the method used for synchronization of the acquired waveform with the reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdSynchronizationMethod):
                Specifies the method used for synchronization of the acquired waveform with the reference waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_SYNCHRONIZATION_METHOD.value
            )
            attr_val = enums.DpdSynchronizationMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_synchronization_method(self, selector_string, value):
        r"""Sets the method used for synchronization of the acquired waveform with the reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdSynchronizationMethod, int):
                Specifies the method used for synchronization of the acquired waveform with the reference waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdSynchronizationMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_SYNCHRONIZATION_METHOD.value,
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

            attr_val (enums.DpdAutoCarrierDetectionEnabled):
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
                attributes.AttributeID.DPD_AUTO_CARRIER_DETECTION_ENABLED.value,
            )
            attr_val = enums.DpdAutoCarrierDetectionEnabled(attr_val)
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

            value (enums.DpdAutoCarrierDetectionEnabled, int):
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
            value = value.value if type(value) is enums.DpdAutoCarrierDetectionEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_AUTO_CARRIER_DETECTION_ENABLED.value,
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
                updated_selector_string, attributes.AttributeID.DPD_NUMBER_OF_CARRIERS.value
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
                updated_selector_string, attributes.AttributeID.DPD_NUMBER_OF_CARRIERS.value, value
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
                updated_selector_string, attributes.AttributeID.DPD_CARRIER_OFFSET.value
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
                updated_selector_string, attributes.AttributeID.DPD_CARRIER_OFFSET.value, value
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
                updated_selector_string, attributes.AttributeID.DPD_CARRIER_BANDWIDTH.value
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
                updated_selector_string, attributes.AttributeID.DPD_CARRIER_BANDWIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_average_input_power(self, selector_string):
        r"""Gets the average power of the signal at the device under test input port. This value is expressed in dBm.

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
                Specifies the average power of the signal at the device under test input port. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_DUT_AVERAGE_INPUT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_average_input_power(self, selector_string, value):
        r"""Sets the average power of the signal at the device under test input port. This value is expressed in dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dBm.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the average power of the signal at the device under test input port. This value is expressed in dBm.

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
                attributes.AttributeID.DPD_DUT_AVERAGE_INPUT_POWER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_model(self, selector_string):
        r"""Gets the DPD model used by the DPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdModel):
                Specifies the DPD model used by the DPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_MODEL.value
            )
            attr_val = enums.DpdModel(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_model(self, selector_string, value):
        r"""Sets the DPD model used by the DPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdModel, int):
                Specifies the DPD model used by the DPD measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdModel else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_MODEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_target_gain_type(self, selector_string):
        r"""Gets the gain expected from the DUT after applying DPD on the input waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdTargetGainType):
                Specifies the gain expected from the DUT after applying DPD on the input waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_TARGET_GAIN_TYPE.value
            )
            attr_val = enums.DpdTargetGainType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_target_gain_type(self, selector_string, value):
        r"""Sets the gain expected from the DUT after applying DPD on the input waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdTargetGainType, int):
                Specifies the gain expected from the DUT after applying DPD on the input waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdTargetGainType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_TARGET_GAIN_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_type(self, selector_string):
        r"""Gets the type of the DPD lookup table (LUT).

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdLookupTableType):
                Specifies the type of the DPD lookup table (LUT).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_LOOKUP_TABLE_TYPE.value
            )
            attr_val = enums.DpdLookupTableType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_type(self, selector_string, value):
        r"""Sets the type of the DPD lookup table (LUT).

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdLookupTableType, int):
                Specifies the type of the DPD lookup table (LUT).

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdLookupTableType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_LOOKUP_TABLE_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_am_to_am_curve_fit_order(self, selector_string):
        r"""Gets the degree of the polynomial used to approximate the device under test AM-to-AM characteristic  when you set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                Specifies the degree of the polynomial used to approximate the device under test AM-to-AM characteristic  when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_AM_CURVE_FIT_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_am_to_am_curve_fit_order(self, selector_string, value):
        r"""Sets the degree of the polynomial used to approximate the device under test AM-to-AM characteristic  when you set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 7.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the degree of the polynomial used to approximate the device under test AM-to-AM characteristic  when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_AM_CURVE_FIT_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_am_to_am_curve_fit_type(self, selector_string):
        r"""Gets the polynomial approximation cost-function of the device under test AM-to-AM characteristic when you set the
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdLookupTableAMToAMCurveFitType):
                Specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_AM_CURVE_FIT_TYPE.value,
            )
            attr_val = enums.DpdLookupTableAMToAMCurveFitType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_am_to_am_curve_fit_type(self, selector_string, value):
        r"""Sets the polynomial approximation cost-function of the device under test AM-to-AM characteristic when you set the
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdLookupTableAMToAMCurveFitType, int):
                Specifies the polynomial approximation cost-function of the device under test AM-to-AM characteristic when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdLookupTableAMToAMCurveFitType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_AM_CURVE_FIT_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_am_to_pm_curve_fit_order(self, selector_string):
        r"""Gets the degree of the polynomial used to approximate the device under test AM-to-PM characteristic when you set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                Specifies the degree of the polynomial used to approximate the device under test AM-to-PM characteristic when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_PM_CURVE_FIT_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_am_to_pm_curve_fit_order(self, selector_string, value):
        r"""Sets the degree of the polynomial used to approximate the device under test AM-to-PM characteristic when you set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 7.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the degree of the polynomial used to approximate the device under test AM-to-PM characteristic when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_PM_CURVE_FIT_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_am_to_pm_curve_fit_type(self, selector_string):
        r"""Gets the polynomial approximation cost-function of the device under test AM-to-PM characteristic when you set the
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdLookupTableAMToPMCurveFitType):
                Specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_PM_CURVE_FIT_TYPE.value,
            )
            attr_val = enums.DpdLookupTableAMToPMCurveFitType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_am_to_pm_curve_fit_type(self, selector_string, value):
        r"""Sets the polynomial approximation cost-function of the device under test AM-to-PM characteristic when you set the
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdLookupTableAMToPMCurveFitType, int):
                Specifies the polynomial approximation cost-function of the device under test AM-to-PM characteristic when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdLookupTableAMToPMCurveFitType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_AM_TO_PM_CURVE_FIT_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_threshold_enabled(self, selector_string):
        r"""Gets whether to enable thresholding of the acquired samples to be used for the DPD measurement when you set the
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdLookupTableThresholdEnabled):
                Specifies whether to enable thresholding of the acquired samples to be used for the DPD measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_ENABLED.value,
            )
            attr_val = enums.DpdLookupTableThresholdEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_threshold_enabled(self, selector_string, value):
        r"""Sets whether to enable thresholding of the acquired samples to be used for the DPD measurement when you set the
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdLookupTableThresholdEnabled, int):
                Specifies whether to enable thresholding of the acquired samples to be used for the DPD measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdLookupTableThresholdEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_threshold_type(self, selector_string):
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

            attr_val (enums.DpdLookupTableThresholdType):
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
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_TYPE.value,
            )
            attr_val = enums.DpdLookupTableThresholdType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_threshold_type(self, selector_string, value):
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

            value (enums.DpdLookupTableThresholdType, int):
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
            value = value.value if type(value) is enums.DpdLookupTableThresholdType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_threshold_level(self, selector_string):
        r"""Gets either the relative or absolute threshold power level based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOOKUP_TABLE_THRESHOLD_TYPE` attribute. This value is expressed in dB or
        dBm.

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
                Specifies either the relative or absolute threshold power level based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOOKUP_TABLE_THRESHOLD_TYPE` attribute. This value is expressed in dB or
                dBm.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_LEVEL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_threshold_level(self, selector_string, value):
        r"""Sets either the relative or absolute threshold power level based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOOKUP_TABLE_THRESHOLD_TYPE` attribute. This value is expressed in dB or
        dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies either the relative or absolute threshold power level based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOOKUP_TABLE_THRESHOLD_TYPE` attribute. This value is expressed in dB or
                dBm.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_LEVEL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_threshold_definition(self, selector_string):
        r"""Gets the definition to use for thresholding acquired and reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdLookupTableThresholdDefinition):
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
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_DEFINITION.value,
            )
            attr_val = enums.DpdLookupTableThresholdDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_threshold_definition(self, selector_string, value):
        r"""Sets the definition to use for thresholding acquired and reference waveform.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdLookupTableThresholdDefinition, int):
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
            value = value.value if type(value) is enums.DpdLookupTableThresholdDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_LOOKUP_TABLE_THRESHOLD_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_step_size(self, selector_string):
        r"""Gets the step size of the input power levels in the predistortion lookup table when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**. This value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1 dB.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the step size of the input power levels in the predistortion lookup table when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_LOOKUP_TABLE_STEP_SIZE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_step_size(self, selector_string, value):
        r"""Sets the step size of the input power levels in the predistortion lookup table when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**. This value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the step size of the input power levels in the predistortion lookup table when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**. This value is expressed in dB.

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
                attributes.AttributeID.DPD_LOOKUP_TABLE_STEP_SIZE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_order(self, selector_string):
        r"""Gets the order of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This order value corresponds to K\ :sub:`a`\
        in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.
        
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.
        
        The default value is 3.

        Args:
            selector_string (string): 
                Pass an empty string.
        
        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the order of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
                attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This order value corresponds to K\ :sub:`a`\
                in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.

            error_code (int): 
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_order(self, selector_string, value):
        r"""Sets the order of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This order value corresponds to K\ :sub:`a`\
        in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.
        
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.
        
        The default value is 3.

        Args:
            selector_string (string): 
                Pass an empty string.

            value (int): 
                Specifies the order of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
                attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This order value corresponds to K\ :sub:`a`\
                in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_memory_depth(self, selector_string):
        r"""Gets the memory depth of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This depth value corresponds to Q\ :sub:`a`\
        in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.
        
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.
        
        The default value is 0.

        Args:
            selector_string (string): 
                Pass an empty string.
        
        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the memory depth of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
                attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This depth value corresponds to Q\ :sub:`a`\
                in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_MEMORY_DEPTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_memory_depth(self, selector_string, value):
        r"""Sets the memory depth of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This depth value corresponds to Q\ :sub:`a`\
        in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.
        
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.
        
        The default value is 0.

        Args:
            selector_string (string): 
                Pass an empty string.

            value (int): 
                Specifies the memory depth of the DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
                attribute to **Memory Polynomial** or **Generalized Memory Polynomial**. This depth value corresponds to Q\ :sub:`a`\
                in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_order_type(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdMemoryPolynomialOrderType):
                Configures the type of terms of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
                Polynomial**.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_ORDER_TYPE.value,
            )
            attr_val = enums.DpdMemoryPolynomialOrderType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_order_type(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdMemoryPolynomialOrderType, int):
                Configures the type of terms of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
                Polynomial**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdMemoryPolynomialOrderType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_ORDER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_lead_order(self, selector_string):
        r"""Gets the lead order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *K\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lead order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *K\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LEAD_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_lead_order(self, selector_string, value):
        r"""Sets the lead order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *K\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lead order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *K\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LEAD_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_lag_order(self, selector_string):
        r"""Gets the lag order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *K\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lag order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *K\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LAG_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_lag_order(self, selector_string, value):
        r"""Sets the lag order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *K\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lag order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *K\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LAG_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_lead_memory_depth(self, selector_string):
        r"""Gets the lead memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *Q\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.  The value of the DPD Mem Poly Lead Mem Depth attribute must be greater than or equal to
        the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lead memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *Q\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.  The value of the DPD Mem Poly Lead Mem Depth attribute must be greater than or equal to
                the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LEAD_MEMORY_DEPTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_lead_memory_depth(self, selector_string, value):
        r"""Sets the lead memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *Q\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.  The value of the DPD Mem Poly Lead Mem Depth attribute must be greater than or equal to
        the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lead memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *Q\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.  The value of the DPD Mem Poly Lead Mem Depth attribute must be greater than or equal to
                the value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LEAD_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_lag_memory_depth(self, selector_string):
        r"""Gets the lag memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *Q\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lag memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *Q\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LAG_MEMORY_DEPTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_lag_memory_depth(self, selector_string, value):
        r"""Sets the lag memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *Q\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lag memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *Q\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LAG_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_maximum_lead(self, selector_string):
        r"""Gets the maximum lead stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *M\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum lead stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *M\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_MAXIMUM_LEAD.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_maximum_lead(self, selector_string, value):
        r"""Sets the maximum lead stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *M\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum lead stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *M\ :sub:`c*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_MAXIMUM_LEAD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_maximum_lag(self, selector_string):
        r"""Gets the maximum lag stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *M\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum lag stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *M\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_MAXIMUM_LAG.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_maximum_lag(self, selector_string, value):
        r"""Sets the maximum lag stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
        corresponds to *M\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum lag stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. This term value
                corresponds to *M\ :sub:`b*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                generalized memory polynomial.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_MAXIMUM_LAG.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_lead_order_type(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdMemoryPolynomialLeadOrderType):
                Configures the type of terms of the lead order DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LEAD_ORDER_TYPE.value,
            )
            attr_val = enums.DpdMemoryPolynomialLeadOrderType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_lead_order_type(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdMemoryPolynomialLeadOrderType, int):
                Configures the type of terms of the lead order DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdMemoryPolynomialLeadOrderType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LEAD_ORDER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_polynomial_lag_order_type(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdMemoryPolynomialLagOrderType):
                Configures the type of terms of the lag order DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**.

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
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LAG_ORDER_TYPE.value,
            )
            attr_val = enums.DpdMemoryPolynomialLagOrderType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_polynomial_lag_order_type(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdMemoryPolynomialLagOrderType, int):
                Configures the type of terms of the lag order DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdMemoryPolynomialLagOrderType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_MEMORY_POLYNOMIAL_LAG_ORDER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dvr_number_of_segments(self, selector_string):
        r"""Gets the number of segments of the Decomposed Vector Rotation model when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
        corresponds to *K* in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the Decomposed Vector
        Rotation model.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 4. This value must be greater than or equal to 1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of segments of the Decomposed Vector Rotation model when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
                corresponds to *K* in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the Decomposed Vector
                Rotation model.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_DVR_NUMBER_OF_SEGMENTS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dvr_number_of_segments(self, selector_string, value):
        r"""Sets the number of segments of the Decomposed Vector Rotation model when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
        corresponds to *K* in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the Decomposed Vector
        Rotation model.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 4. This value must be greater than or equal to 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of segments of the Decomposed Vector Rotation model when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
                corresponds to *K* in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the Decomposed Vector
                Rotation model.

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
                attributes.AttributeID.DPD_DVR_NUMBER_OF_SEGMENTS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dvr_linear_memory_depth(self, selector_string):
        r"""Gets the linear memory depth of the Decomposed Vector Rotation model when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
        corresponds to *M\ :sub:`l*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the decomposed
        vector rotation model.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 21. This value must be greater than or equal to 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the linear memory depth of the Decomposed Vector Rotation model when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
                corresponds to *M\ :sub:`l*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the decomposed
                vector rotation model.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_DVR_LINEAR_MEMORY_DEPTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dvr_linear_memory_depth(self, selector_string, value):
        r"""Sets the linear memory depth of the Decomposed Vector Rotation model when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
        corresponds to *M\ :sub:`l*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the decomposed
        vector rotation model.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 21. This value must be greater than or equal to 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the linear memory depth of the Decomposed Vector Rotation model when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
                corresponds to *M\ :sub:`l*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the decomposed
                vector rotation model.

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
                attributes.AttributeID.DPD_DVR_LINEAR_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dvr_nonlinear_memory_depth(self, selector_string):
        r"""Gets the nonlinear memory depth of the Decomposed Vector Rotation model when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
        corresponds to *M\ :sub:`nl*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        decomposed vector rotation model.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 2. This value must be greater than or equal to 1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the nonlinear memory depth of the Decomposed Vector Rotation model when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
                corresponds to *M\ :sub:`nl*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                decomposed vector rotation model.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_DVR_NONLINEAR_MEMORY_DEPTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dvr_nonlinear_memory_depth(self, selector_string, value):
        r"""Sets the nonlinear memory depth of the Decomposed Vector Rotation model when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
        corresponds to *M\ :sub:`nl*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
        decomposed vector rotation model.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 2. This value must be greater than or equal to 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the nonlinear memory depth of the Decomposed Vector Rotation model when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**. This value
                corresponds to *M\ :sub:`nl*`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                decomposed vector rotation model.

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
                attributes.AttributeID.DPD_DVR_NONLINEAR_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dvr_ddr_enabled(self, selector_string):
        r"""Gets whether to enable the Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdDvrDdrEnabled):
                Specifies whether to enable the Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector
                Rotation Model when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector
                Rotation**. For more details, refer to the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                decomposed vector rotation model.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_DVR_DDR_ENABLED.value
            )
            attr_val = enums.DpdDvrDdrEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dvr_ddr_enabled(self, selector_string, value):
        r"""Sets whether to enable the Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdDvrDdrEnabled, int):
                Specifies whether to enable the Dynamic Deviation Reduction (DDR) terms which are a subset of Decomposed Vector
                Rotation Model when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector
                Rotation**. For more details, refer to the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the
                decomposed vector rotation model.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdDvrDdrEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_DVR_DDR_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_mode(self, selector_string):
        r"""Gets if the training waveform required for the extraction of the DPD model coefficients is acquired from the
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdMeasurementMode):
                Specifies if the training waveform required for the extraction of the DPD model coefficients is acquired from the
                hardware or is configured by the user.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_MEASUREMENT_MODE.value
            )
            attr_val = enums.DpdMeasurementMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_mode(self, selector_string, value):
        r"""Sets if the training waveform required for the extraction of the DPD model coefficients is acquired from the
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdMeasurementMode, int):
                Specifies if the training waveform required for the extraction of the DPD model coefficients is acquired from the
                hardware or is configured by the user.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdMeasurementMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_MEASUREMENT_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iterative_dpd_enabled(self, selector_string):
        r"""Gets whether to enable iterative computation of the DPD Results DPD Polynomial using `DPD
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdIterativeDpdEnabled):
                Specifies whether to enable iterative computation of the DPD Results DPD Polynomial using `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_ITERATIVE_DPD_ENABLED.value
            )
            attr_val = enums.DpdIterativeDpdEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iterative_dpd_enabled(self, selector_string, value):
        r"""Sets whether to enable iterative computation of the DPD Results DPD Polynomial using `DPD
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdIterativeDpdEnabled, int):
                Specifies whether to enable iterative computation of the DPD Results DPD Polynomial using `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdIterativeDpdEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_ITERATIVE_DPD_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_offset_correction_enabled(self, selector_string):
        r"""Gets whether to enable frequency offset correction for the DPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdFrequencyOffsetCorrectionEnabled):
                Specifies whether to enable frequency offset correction for the DPD measurement.

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
                attributes.AttributeID.DPD_FREQUENCY_OFFSET_CORRECTION_ENABLED.value,
            )
            attr_val = enums.DpdFrequencyOffsetCorrectionEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_offset_correction_enabled(self, selector_string, value):
        r"""Sets whether to enable frequency offset correction for the DPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdFrequencyOffsetCorrectionEnabled, int):
                Specifies whether to enable frequency offset correction for the DPD measurement.

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
                value.value if type(value) is enums.DpdFrequencyOffsetCorrectionEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_FREQUENCY_OFFSET_CORRECTION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iq_origin_offset_correction_enabled(self, selector_string):
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdIQOriginOffsetCorrectionEnabled):
                Enables the IQ origin offset correction for the measurement.

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
                attributes.AttributeID.DPD_IQ_ORIGIN_OFFSET_CORRECTION_ENABLED.value,
            )
            attr_val = enums.DpdIQOriginOffsetCorrectionEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iq_origin_offset_correction_enabled(self, selector_string, value):
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdIQOriginOffsetCorrectionEnabled, int):
                Enables the IQ origin offset correction for the measurement.

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
                value.value if type(value) is enums.DpdIQOriginOffsetCorrectionEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_IQ_ORIGIN_OFFSET_CORRECTION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the DPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdAveragingEnabled):
                Specifies whether to enable averaging for the DPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_AVERAGING_ENABLED.value
            )
            attr_val = enums.DpdAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the DPD measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdAveragingEnabled, int):
                Specifies whether to enable averaging for the DPD measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.DPD_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.DPD_AVERAGING_COUNT.value, value
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
                updated_selector_string, attributes.AttributeID.DPD_MAXIMUM_TIMING_ERROR.value
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
                attributes.AttributeID.DPD_MAXIMUM_TIMING_ERROR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_nmse_enabled(self, selector_string):
        r"""Gets whether to enable the normalized mean-squared error (NMSE) computation.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdNmseEnabled):
                Specifies whether to enable the normalized mean-squared error (NMSE) computation.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_NMSE_ENABLED.value
            )
            attr_val = enums.DpdNmseEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_nmse_enabled(self, selector_string, value):
        r"""Sets whether to enable the normalized mean-squared error (NMSE) computation.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdNmseEnabled, int):
                Specifies whether to enable the normalized mean-squared error (NMSE) computation.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdNmseEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_NMSE_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the DPD measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the DPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the DPD measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the DPD measurement.

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
                updated_selector_string, attributes.AttributeID.DPD_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism of the DPD measurement.

        The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
        may not all be used in calculations. The actual number of threads used depends on the problem size, system resources,
        data availability, and other considerations.

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
                Specifies the maximum number of threads used for parallelism of the DPD measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_NUMBER_OF_ANALYSIS_THREADS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism of the DPD measurement.

        The number of threads can range from 1 to the number of physical cores. However, the number of threads you set
        may not all be used in calculations. The actual number of threads used depends on the problem size, system resources,
        data availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of threads used for parallelism of the DPD measurement.

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
                attributes.AttributeID.DPD_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(self, selector_string, averaging_enabled, averaging_count):
        r"""Configures averaging for the DPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.DpdAveragingEnabled, int):
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
                if type(averaging_enabled) is enums.DpdAveragingEnabled
                else averaging_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_dpd_model(self, selector_string, dpd_model):
        r"""Specifies the DPD model used by the DPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dpd_model (enums.DpdModel, int):
                This parameter specifies the DPD model used by the DPD measurement. The default value is **Lookup Table**.

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
                | Decomposed Vector Rotation (3)    | This model computes the decomposed vector rotation predistortion coefficients used to linearize wideband systems with    |
                |                                   | significant memory effects.                                                                                              |
                +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            dpd_model = dpd_model.value if type(dpd_model) is enums.DpdModel else dpd_model
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_dpd_model(
                updated_selector_string, dpd_model
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_dut_average_input_power(self, selector_string, dut_average_input_power):
        r"""Configures the average power, in dBm, of the signal at the input port of the device under test (DUT).

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_average_input_power (float):
                This parameter specifies the average power of the signal at the input port of the DUT. The default value is -20 dBm.

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
            error_code = self._interpreter.dpd_configure_dut_average_input_power(
                updated_selector_string, dut_average_input_power
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_generalized_memory_polynomial_cross_terms(
        self,
        selector_string,
        memory_polynomial_lead_order,
        memory_polynomial_lag_order,
        memory_polynomial_lead_memory_depth,
        memory_polynomial_lag_memory_depth,
        memory_polynomial_maximum_lead,
        memory_polynomial_maximum_lag,
    ):
        r"""Configures the cross terms of the generalized memory polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Generalized Memory Polynomial**. Use the
        :py:meth:`configure_memory_polynomial` method to configure the normal terms in the DPD polynomial, along with
        configuring the cross terms when you set the DPD Model attribute to **Generalized Memory Polynomial**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            memory_polynomial_lead_order (int):
                This parameter specifies the lead order cross term of the DPD polynomial when you set the DPD Model attribute to
                **Generalized Memory Polynomial**. This value corresponds to K\ :sub:`c`\ in the `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial. The default value is
                0.

            memory_polynomial_lag_order (int):
                This parameter specifies the lag order cross term of the DPD polynomial when you set the DPD Model attribute to
                **Generalized Memory Polynomial**. This value corresponds to K\ :sub:`b`\ in the `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial. The default value is
                0.

            memory_polynomial_lead_memory_depth (int):
                This parameter specifies the lead memory depth cross term of the DPD polynomial when you set the DPD Model attribute to
                **Generalized Memory Polynomial**. This value corresponds to Q\ :sub:`c`\ in the `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial. The value of this
                parameter must be greater than or equal to the value of the **Memory Polynomial Max Lead** parameter. The default value
                is 0.

            memory_polynomial_lag_memory_depth (int):
                This parameter specifies the lag memory depth cross term of the DPD polynomial when you set the DPD Model attribute to
                **Generalized Memory Polynomial**. This value corresponds to Q\ :sub:`b`\ in the `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory polynomial. The default value is
                0.

            memory_polynomial_maximum_lead (int):
                This parameter specifies the maximum lead stagger cross term of the DPD polynomial when you set the DPD Model attribute
                to  **Generalized Memory Polynomial**. This value corresponds to M\ :sub:`c`\ in the equation for the generalized
                memory polynomial. The default value is 0.

            memory_polynomial_maximum_lag (int):
                This parameter specifies the maximum lag stagger cross term of the DPD polynomial when you set the DPD Model attribute
                to **Generalized Memory Polynomial**. This value corresponds to M\ :sub:`b`\ in the equation for the generalized memory
                polynomial. The default value is 0.

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
            error_code = self._interpreter.dpd_configure_generalized_memory_polynomial_cross_terms(
                updated_selector_string,
                memory_polynomial_lead_order,
                memory_polynomial_lag_order,
                memory_polynomial_lead_memory_depth,
                memory_polynomial_lag_memory_depth,
                memory_polynomial_maximum_lead,
                memory_polynomial_maximum_lag,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_iterative_dpd_enabled(self, selector_string, iterative_dpd_enabled):
        r"""Configures the iterative computation of the DPD polynomial in accordance with the `DPD
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
        Polynomial**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            iterative_dpd_enabled (enums.DpdIterativeDpdEnabled, int):
                This parameter specifies whether to enable iterative computation of the DPD Results DPD Polynomial using `DPD
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_. The default value is **False**.

                +--------------+--------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                  |
                +==============+==============================================================================================================+
                | False (0)    | The DPD Results DPD Polynomial is computed without considering the value of the DPD Previous DPD Polynomial. |
                +--------------+--------------------------------------------------------------------------------------------------------------+
                | True (1)     | The DPD Results DPD Polynomial is computed based on the value of the DPD Previous DPD Polynomial.            |
                +--------------+--------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            iterative_dpd_enabled = (
                iterative_dpd_enabled.value
                if type(iterative_dpd_enabled) is enums.DpdIterativeDpdEnabled
                else iterative_dpd_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_iterative_dpd_enabled(
                updated_selector_string, iterative_dpd_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_lookup_table_am_to_am_curve_fit(
        self, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
    ):
        r"""Configures the degree of the polynomial and the approximation method used for polynomial approximation of the AM-to-AM
        response of the device under test (DUT) when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        attribute to **Lookup Table**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            am_to_am_curve_fit_order (int):
                This parameter specifies the degree of the polynomial used to approximate the AM-to-AM characteristic of the DUT when
                you set the DPD Model attribute to **Lookup Table**. The default value is 7.

            am_to_am_curve_fit_type (enums.DpdLookupTableAMToAMCurveFitType, int):
                This parameter specifies the polynomial approximation cost-function of the DUT AM-to-AM characteristic when you set the
                DPD Model attribute to **Lookup Table**. The default value is **Least Absolute Residual**.

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
                if type(am_to_am_curve_fit_type) is enums.DpdLookupTableAMToAMCurveFitType
                else am_to_am_curve_fit_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_lookup_table_am_to_am_curve_fit(
                updated_selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_lookup_table_am_to_pm_curve_fit(
        self, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
    ):
        r"""Configures the degree of the polynomial and the approximation method, used for polynomial approximation of the AM-to-PM
        response of the device under test (DUT) when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        attribute to **Lookup Table**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            am_to_pm_curve_fit_order (int):
                This parameter specifies the degree of the polynomial used to approximate the AM-to-PM characteristic of the DUT when
                you set the DPD Model attribute to **Lookup Table**. The default value is 7.

            am_to_pm_curve_fit_type (enums.DpdLookupTableAMToPMCurveFitType, int):
                This parameter specifies the polynomial approximation cost-function of the DUT AM-to-PM characteristic when you set the
                DPD Model attribute to **Lookup Table**. The default value is **Least Absolute Residual**.

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
                if type(am_to_pm_curve_fit_type) is enums.DpdLookupTableAMToPMCurveFitType
                else am_to_pm_curve_fit_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_lookup_table_am_to_pm_curve_fit(
                updated_selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_lookup_table_step_size(self, selector_string, step_size):
        r"""Configures the step size, in dB, of input power levels in the predistortion lookup table when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            step_size (float):
                This parameter specifies the step size, in dB, of the input power levels in the predistortion lookup table when you set
                the DPD Model attribute to **Lookup Table**. The default value is 0.1 dB.

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
            error_code = self._interpreter.dpd_configure_lookup_table_step_size(
                updated_selector_string, step_size
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_lookup_table_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        r"""Configures the threshold level for the samples that are considered for the DPD measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**.  Set the **Threshold Enabled**
        parameter to **True** to reject low-power signals affected by noise and distortion.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            threshold_enabled (enums.DpdLookupTableThresholdEnabled, int):
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

            threshold_type (enums.DpdLookupTableThresholdType, int):
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
                if type(threshold_enabled) is enums.DpdLookupTableThresholdEnabled
                else threshold_enabled
            )
            threshold_type = (
                threshold_type.value
                if type(threshold_type) is enums.DpdLookupTableThresholdType
                else threshold_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_lookup_table_threshold(
                updated_selector_string, threshold_enabled, threshold_level, threshold_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_lookup_table_type(self, selector_string, lookup_table_type):
        r"""Configuers the type of DPD Lookup Table.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            lookup_table_type (enums.DpdLookupTableType, int):
                This parameter specifies the type of the DPD lookup table (LUT). The default value is **Log**.

                +--------------+-------------------------------------------------+
                | Name (Value) | Description                                     |
                +==============+=================================================+
                | Log (0)      | Input powers in the LUT are specified in dBm.   |
                +--------------+-------------------------------------------------+
                | Linear (1)   | Input powers in the LUT are specified in watts. |
                +--------------+-------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            lookup_table_type = (
                lookup_table_type.value
                if type(lookup_table_type) is enums.DpdLookupTableType
                else lookup_table_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_lookup_table_type(
                updated_selector_string, lookup_table_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval(self, selector_string, measurement_interval):
        r"""Configures the acquisition time, in seconds, for the DPD measurement.

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
            error_code = self._interpreter.dpd_configure_measurement_interval(
                updated_selector_string, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_sample_rate(self, selector_string, sample_rate_mode, sample_rate):
        r"""Configures the acquisition sample rate, in Samples per second (S/s), for the DPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            sample_rate_mode (enums.DpdMeasurementSampleRateMode, int):
                This parameter specifies the acquisition sample rate configuration mode. The default value is **User**.

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
                if type(sample_rate_mode) is enums.DpdMeasurementSampleRateMode
                else sample_rate_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_measurement_sample_rate(
                updated_selector_string, sample_rate_mode, sample_rate
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_memory_polynomial(
        self, selector_string, memory_polynomial_order, memory_polynomial_memory_depth
    ):
        r"""Configures the order and memory depth of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
        Polynomial**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            memory_polynomial_order (int):
                This parameter specifies the order of the DPD polynomial when you set the DPD Model attribute to  **Memory Polynomial**
                or  **Generalized Memory Polynomial**. This value corresponds to K\ :sub:`a`\ in the equation for the generalized
                memory polynomial. The default value is 3.

            memory_polynomial_memory_depth (int):
                This parameter specifies the memory depth of the DPD polynomial when you set the DPD Model attribute to **Memory
                Polynomial** or  **Generalized Memory Polynomial**. This value corresponds to Q\ :sub:`a`\ in the equation for the
                generalized memory polynomial. The default value is 0.

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
            error_code = self._interpreter.dpd_configure_memory_polynomial(
                updated_selector_string, memory_polynomial_order, memory_polynomial_memory_depth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_previous_dpd_polynomial(self, selector_string, previous_dpd_polynomial):
        r"""Configures the previous DPD polynomial when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute
        to **Memory Polynomial** or **Generalized Memory Polynomial**. Set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.ITERATIVE_DPD_ENABLED` attribute to **True**, to apply the previous DPD
        polynomial on the reference waveform, which is used to compute the value of the DPD polynomial for the current
        iteration.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            previous_dpd_polynomial (numpy.complex64):
                This parameter specifies the value of the previous DPD polynomial.

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
            error_code = self._interpreter.dpd_configure_previous_dpd_polynomial(
                updated_selector_string, previous_dpd_polynomial
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_waveform(
        self, selector_string, x0, dx, reference_waveform, idle_duration_present, signal_type
    ):
        r"""Configures the complex baseband equivalent of the RF signal applied at the input port of the DUT when performing the
        DPD measurement.

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

            idle_duration_present (enums.DpdReferenceWaveformIdleDurationPresent, int):
                This parameter specifies whether the reference waveform contains an idle duration. The default value is **False**.

                +--------------+-----------------------------------------------------------+
                | Name (Value) | Description                                               |
                +==============+===========================================================+
                | False (0)    | The reference waveform does not contain an idle duration. |
                +--------------+-----------------------------------------------------------+
                | True (1)     | The reference waveform contains an idle duration.         |
                +--------------+-----------------------------------------------------------+

            signal_type (enums.DpdSignalType, int):
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
                if type(idle_duration_present) is enums.DpdReferenceWaveformIdleDurationPresent
                else idle_duration_present
            )
            signal_type = (
                signal_type.value if type(signal_type) is enums.DpdSignalType else signal_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_reference_waveform(
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
    def configure_extract_model_target_waveform(self, selector_string, x0, dx, target_waveform):
        r"""Configures the complex baseband equivalent of the Target waveform desired at the output of the Predistorter Model to be
        extracted when performing the DPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            x0 (float):
                This parameter specifies the start time, in seconds.

            dx (float):
                This parameter specifies the sample duration, in seconds.

            target_waveform (numpy.complex64):
                This parameter specifies the complex baseband samples, in volts.

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
            error_code = self._interpreter.dpd_configure_extract_model_target_waveform(
                updated_selector_string, x0, dx, target_waveform
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

            synchronization_method (enums.DpdSynchronizationMethod, int):
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
                |                     | Refer to DPD concept help for more information.                                                                          |
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
                if type(synchronization_method) is enums.DpdSynchronizationMethod
                else synchronization_method
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_synchronization_method(
                updated_selector_string, synchronization_method
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
