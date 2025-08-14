"""Provides methods to configure the IQ measurement."""

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


class IQConfiguration(object):
    """Provides methods to configure the IQ measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the IQ measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the I/Q measurement.

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
                Specifies whether to enable the I/Q measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the I/Q measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the I/Q measurement.

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
                updated_selector_string, attributes.AttributeID.IQ_MEASUREMENT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_mode(self, selector_string):
        r"""Gets the mode for performing the IQ measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IQMeasurementMode):
                Specifies the mode for performing the IQ measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_MEASUREMENT_MODE.value
            )
            attr_val = enums.IQMeasurementMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_mode(self, selector_string, value):
        r"""Sets the mode for performing the IQ measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IQMeasurementMode, int):
                Specifies the mode for performing the IQ measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IQMeasurementMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_MEASUREMENT_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_sample_rate(self, selector_string):
        r"""Gets the acquisition sample rate. This value is expressed in samples per second (S/s).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 50 MS/s.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition sample rate. This value is expressed in samples per second (S/s).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IQ_SAMPLE_RATE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_sample_rate(self, selector_string, value):
        r"""Sets the acquisition sample rate. This value is expressed in samples per second (S/s).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 50 MS/s.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition sample rate. This value is expressed in samples per second (S/s).

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
                updated_selector_string, attributes.AttributeID.IQ_SAMPLE_RATE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_acquisition_time(self, selector_string):
        r"""Gets the acquisition time for the I/Q measurement. This value is expressed in seconds.

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
                Specifies the acquisition time for the I/Q measurement. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IQ_ACQUISITION_TIME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_acquisition_time(self, selector_string, value):
        r"""Sets the acquisition time for the I/Q measurement. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition time for the I/Q measurement. This value is expressed in seconds.

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
                updated_selector_string, attributes.AttributeID.IQ_ACQUISITION_TIME.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_pretrigger_time(self, selector_string):
        r"""Gets the pretrigger time for the I/Q measurement. This value is expressed in seconds.

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
                Specifies the pretrigger time for the I/Q measurement. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IQ_PRETRIGGER_TIME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_pretrigger_time(self, selector_string, value):
        r"""Sets the pretrigger time for the I/Q measurement. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the pretrigger time for the I/Q measurement. This value is expressed in seconds.

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
                updated_selector_string, attributes.AttributeID.IQ_PRETRIGGER_TIME.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_bandwidth_auto(self, selector_string):
        r"""Gets whether the measurement computes the minimum acquisition bandwidth.

        The default value is **True**.

        +--------------+----------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                        |
        +==============+====================================================================================================+
        | False (0)    | The measurement uses the value of the IQ Bandwidth attribute as the minimum acquisition bandwidth. |
        +--------------+----------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement uses 0.8 * sample rate as the minimum signal bandwidth.                            |
        +--------------+----------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IQBandwidthAuto):
                Specifies whether the measurement computes the minimum acquisition bandwidth.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_BANDWIDTH_AUTO.value
            )
            attr_val = enums.IQBandwidthAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_bandwidth_auto(self, selector_string, value):
        r"""Sets whether the measurement computes the minimum acquisition bandwidth.

        The default value is **True**.

        +--------------+----------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                        |
        +==============+====================================================================================================+
        | False (0)    | The measurement uses the value of the IQ Bandwidth attribute as the minimum acquisition bandwidth. |
        +--------------+----------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement uses 0.8 * sample rate as the minimum signal bandwidth.                            |
        +--------------+----------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IQBandwidthAuto, int):
                Specifies whether the measurement computes the minimum acquisition bandwidth.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IQBandwidthAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_BANDWIDTH_AUTO.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_bandwidth(self, selector_string):
        r"""Gets the minimum acquisition bandwidth when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_AUTO` attribute to **False**. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the minimum acquisition bandwidth when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_AUTO` attribute to **False**. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IQ_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_bandwidth(self, selector_string, value):
        r"""Sets the minimum acquisition bandwidth when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_AUTO` attribute to **False**. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the minimum acquisition bandwidth when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_AUTO` attribute to **False**. This value is expressed in Hz.

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
                updated_selector_string, attributes.AttributeID.IQ_BANDWIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_records(self, selector_string):
        r"""Gets the number of records to acquire.

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
                Specifies the number of records to acquire.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_NUMBER_OF_RECORDS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_records(self, selector_string, value):
        r"""Sets the number of records to acquire.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of records to acquire.

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
                updated_selector_string, attributes.AttributeID.IQ_NUMBER_OF_RECORDS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_delete_record_on_fetch(self, selector_string):
        r"""Gets whether the measurement deletes the fetched record.

        The default value is **True**.

        +--------------+-----------------------------------------------------+
        | Name (Value) | Description                                         |
        +==============+=====================================================+
        | False (0)    | The measurement does not delete the fetched record. |
        +--------------+-----------------------------------------------------+
        | True (1)     | The measurement deletes the fetched record.         |
        +--------------+-----------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IQDeleteRecordOnFetch):
                Specifies whether the measurement deletes the fetched record.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IQ_DELETE_RECORD_ON_FETCH.value
            )
            attr_val = enums.IQDeleteRecordOnFetch(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_delete_record_on_fetch(self, selector_string, value):
        r"""Sets whether the measurement deletes the fetched record.

        The default value is **True**.

        +--------------+-----------------------------------------------------+
        | Name (Value) | Description                                         |
        +==============+=====================================================+
        | False (0)    | The measurement does not delete the fetched record. |
        +--------------+-----------------------------------------------------+
        | True (1)     | The measurement deletes the fetched record.         |
        +--------------+-----------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IQDeleteRecordOnFetch, int):
                Specifies whether the measurement deletes the fetched record.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IQDeleteRecordOnFetch else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IQ_DELETE_RECORD_ON_FETCH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_acquisition(
        self, selector_string, sample_rate, number_of_records, acquisition_time, pretrigger_time
    ):
        r"""Configures the acquisition settings for the I/Q measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            sample_rate (float):
                This parameter specifies the acquisition sample rate, in samples per second (S/s). The default value is 50 MS/s.

            number_of_records (int):
                This parameter specifies the number of records to acquire. The default value is 1.

            acquisition_time (float):
                This parameter specifies the acquisition time, in seconds, for the I/Q measurement. The default value is 0.001.

            pretrigger_time (float):
                This parameter specifies the pretrigger time, in seconds, for the I/Q measurement. The default value is 0.

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
            error_code = self._interpreter.iq_configure_acquisition(
                updated_selector_string,
                sample_rate,
                number_of_records,
                acquisition_time,
                pretrigger_time,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_bandwidth(self, selector_string, bandwidth_auto, bandwidth):
        r"""Configures the bandwidth for the I/Q measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            bandwidth_auto (enums.IQBandwidthAuto, int):
                This parameter specifies whether the measurement computes the minimum acquisition bandwidth. The default value is
                **True**.

                +--------------+-------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                     |
                +==============+=================================================================================================+
                | False (0)    | The measurement uses the value of the Bandwidth parameter as the minimum acquisition bandwidth. |
                +--------------+-------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement uses 0.8 * sample rate as the minimum signal bandwidth.                         |
                +--------------+-------------------------------------------------------------------------------------------------+

            bandwidth (float):
                This parameter specifies the minimum acquisition bandwidth, in Hz, when you set the **Bandwidth Auto** parameter to
                **False**. The default value is 1 MHz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            bandwidth_auto = (
                bandwidth_auto.value
                if type(bandwidth_auto) is enums.IQBandwidthAuto
                else bandwidth_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.iq_configure_bandwidth(
                updated_selector_string, bandwidth_auto, bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
