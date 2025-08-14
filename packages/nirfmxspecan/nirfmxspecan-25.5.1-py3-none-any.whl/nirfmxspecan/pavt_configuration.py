"""Provides methods to configure the Pavt measurement."""

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


class PavtConfiguration(object):
    """Provides methods to configure the Pavt measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Pavt measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the Phase Amplitude Versus Time (PAVT) measurement.

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
                Specifies whether to enable the Phase Amplitude Versus Time (PAVT) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the Phase Amplitude Versus Time (PAVT) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the Phase Amplitude Versus Time (PAVT) measurement.

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
                attributes.AttributeID.PAVT_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_location_type(self, selector_string):
        r"""Gets whether the location at which the segment is measured is indicated by time or trigger.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PavtMeasurementLocationType):
                Specifies whether the location at which the segment is measured is indicated by time or trigger.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_LOCATION_TYPE.value
            )
            attr_val = enums.PavtMeasurementLocationType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_location_type(self, selector_string, value):
        r"""Sets whether the location at which the segment is measured is indicated by time or trigger.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PavtMeasurementLocationType, int):
                Specifies whether the location at which the segment is measured is indicated by time or trigger.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PavtMeasurementLocationType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PAVT_MEASUREMENT_LOCATION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_bandwidth(self, selector_string):
        r"""Gets the bandwidth over which the signal is measured. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth over which the signal is measured. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth over which the signal is measured. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth over which the signal is measured. This value is expressed in Hz.

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
                attributes.AttributeID.PAVT_MEASUREMENT_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_interval_mode(self, selector_string):
        r"""Gets the mode of configuring the measurement interval.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PavtMeasurementIntervalMode):
                Specifies the mode of configuring the measurement interval.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_INTERVAL_MODE.value
            )
            attr_val = enums.PavtMeasurementIntervalMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_interval_mode(self, selector_string, value):
        r"""Sets the mode of configuring the measurement interval.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PavtMeasurementIntervalMode, int):
                Specifies the mode of configuring the measurement interval.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PavtMeasurementIntervalMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PAVT_MEASUREMENT_INTERVAL_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_segments(self, selector_string):
        r"""Gets the number of segments to be measured.

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
                Specifies the number of segments to be measured.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_NUMBER_OF_SEGMENTS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_segments(self, selector_string, value):
        r"""Sets the number of segments to be measured.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of segments to be measured.

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
                updated_selector_string, attributes.AttributeID.PAVT_NUMBER_OF_SEGMENTS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_type(self, selector_string):
        r"""Gets the type of segment.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PavtSegmentType):
                Specifies the type of segment.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_SEGMENT_TYPE.value
            )
            attr_val = enums.PavtSegmentType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_type(self, selector_string, value):
        r"""Sets the type of segment.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PavtSegmentType, int):
                Specifies the type of segment.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PavtSegmentType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_SEGMENT_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_start_time(self, selector_string):
        r"""Gets the start time of measurement of the segments. This value is expressed in seconds. You can use this attribute
        only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LOCATION_TYPE` attribute to **Time**.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start time of measurement of the segments. This value is expressed in seconds. You can use this attribute
                only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LOCATION_TYPE` attribute to **Time**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PAVT_SEGMENT_START_TIME.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_start_time(self, selector_string, value):
        r"""Sets the start time of measurement of the segments. This value is expressed in seconds. You can use this attribute
        only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LOCATION_TYPE` attribute to **Time**.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start time of measurement of the segments. This value is expressed in seconds. You can use this attribute
                only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LOCATION_TYPE` attribute to **Time**.

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
                updated_selector_string, attributes.AttributeID.PAVT_SEGMENT_START_TIME.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_offset(self, selector_string):
        r"""Gets the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
        error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

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
                Specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_offset(self, selector_string, value):
        r"""Sets the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
        error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

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
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_length(self, selector_string):
        r"""Gets the duration within the segment over which the phase and amplitude, amplitude, or frequency error values are
        computed. This value is expressed in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 millisecond.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the duration within the segment over which the phase and amplitude, amplitude, or frequency error values are
                computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_LENGTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_length(self, selector_string, value):
        r"""Sets the duration within the segment over which the phase and amplitude, amplitude, or frequency error values are
        computed. This value is expressed in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 millisecond.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the duration within the segment over which the phase and amplitude, amplitude, or frequency error values are
                computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**.

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
                updated_selector_string, attributes.AttributeID.PAVT_MEASUREMENT_LENGTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_measurement_offset(self, selector_string):
        r"""Gets the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
        error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

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
                attributes.AttributeID.PAVT_SEGMENT_MEASUREMENT_OFFSET.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_measurement_offset(self, selector_string, value):
        r"""Sets the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
        error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

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
                attributes.AttributeID.PAVT_SEGMENT_MEASUREMENT_OFFSET.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_measurement_length(self, selector_string):
        r"""Gets the duration within each segment over which the phase and amplitude, amplitude, or frequency error values are
        computed. This value is expressed in seconds. This attribute is valid when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 millisecond.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the duration within each segment over which the phase and amplitude, amplitude, or frequency error values are
                computed. This value is expressed in seconds. This attribute is valid when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

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
                attributes.AttributeID.PAVT_SEGMENT_MEASUREMENT_LENGTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_measurement_length(self, selector_string, value):
        r"""Sets the duration within each segment over which the phase and amplitude, amplitude, or frequency error values are
        computed. This value is expressed in seconds. This attribute is valid when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 millisecond.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the duration within each segment over which the phase and amplitude, amplitude, or frequency error values are
                computed. This value is expressed in seconds. This attribute is valid when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**.

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
                attributes.AttributeID.PAVT_SEGMENT_MEASUREMENT_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_phase_unwrap_enabled(self, selector_string):
        r"""Gets whether the phase measurement results are unwrapped or wrapped.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PavtPhaseUnwrapEnabled):
                Specifies whether the phase measurement results are unwrapped or wrapped.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_PHASE_UNWRAP_ENABLED.value
            )
            attr_val = enums.PavtPhaseUnwrapEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_phase_unwrap_enabled(self, selector_string, value):
        r"""Sets whether the phase measurement results are unwrapped or wrapped.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PavtPhaseUnwrapEnabled, int):
                Specifies whether the phase measurement results are unwrapped or wrapped.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PavtPhaseUnwrapEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PAVT_PHASE_UNWRAP_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_offset_correction_enabled(self, selector_string):
        r"""Gets whether to enable frequency offset correction for the measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PavtFrequencyOffsetCorrectionEnabled):
                Specifies whether to enable frequency offset correction for the measurement.

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
                attributes.AttributeID.PAVT_FREQUENCY_OFFSET_CORRECTION_ENABLED.value,
            )
            attr_val = enums.PavtFrequencyOffsetCorrectionEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_offset_correction_enabled(self, selector_string, value):
        r"""Sets whether to enable frequency offset correction for the measurement.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PavtFrequencyOffsetCorrectionEnabled, int):
                Specifies whether to enable frequency offset correction for the measurement.

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
                value.value if type(value) is enums.PavtFrequencyOffsetCorrectionEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PAVT_FREQUENCY_OFFSET_CORRECTION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_tracking_enabled(self, selector_string):
        r"""Gets whether to enable frequency offset correction per segment for the measurement. While you set this attribute
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PavtFrequencyTrackingEnabled):
                Specifies whether to enable frequency offset correction per segment for the measurement. While you set this attribute
                to **True**, ensure that the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_OFFSET_CORRECTION_ENABLED`
                attribute is set to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_TYPE` attribute is set to
                **Phase and Amplitude**.

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
                attributes.AttributeID.PAVT_FREQUENCY_TRACKING_ENABLED.value,
            )
            attr_val = enums.PavtFrequencyTrackingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_tracking_enabled(self, selector_string, value):
        r"""Sets whether to enable frequency offset correction per segment for the measurement. While you set this attribute
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PavtFrequencyTrackingEnabled, int):
                Specifies whether to enable frequency offset correction per segment for the measurement. While you set this attribute
                to **True**, ensure that the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_OFFSET_CORRECTION_ENABLED`
                attribute is set to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_TYPE` attribute is set to
                **Phase and Amplitude**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PavtFrequencyTrackingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PAVT_FREQUENCY_TRACKING_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the PAVT measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the PAVT measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PAVT_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the PAVT measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the PAVT measurement.

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
                updated_selector_string, attributes.AttributeID.PAVT_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_bandwidth(self, selector_string, measurement_bandwidth):
        r"""Configures the measurement  bandwidth.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_bandwidth (float):
                This parameter specifies the bandwidth over which the signal is measured. This value is expressed in Hz. The default
                value is 10 MHz.

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
            error_code = self._interpreter.pavt_configure_measurement_bandwidth(
                updated_selector_string, measurement_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval_mode(self, selector_string, measurement_interval_mode):
        r"""Configures the measurement interval mode.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_interval_mode (enums.PavtMeasurementIntervalMode, int):
                This parameter specifies the mode of configuring the measurement interval. The default value is **Uniform**.

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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            measurement_interval_mode = (
                measurement_interval_mode.value
                if type(measurement_interval_mode) is enums.PavtMeasurementIntervalMode
                else measurement_interval_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.pavt_configure_measurement_interval_mode(
                updated_selector_string, measurement_interval_mode
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval(
        self, selector_string, measurement_offset, measurement_length
    ):
        r"""Configures the measurement offset and measurement length for the segments.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_offset (float):
                This parameter specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or
                frequency error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**. The default value
                is 0.

            measurement_length (float):
                This parameter specifies the duration within each segment over which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Uniform**. The default value
                is 1 millisecond.

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
            error_code = self._interpreter.pavt_configure_measurement_interval(
                updated_selector_string, measurement_offset, measurement_length
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_location_type(self, selector_string, measurement_location_type):
        r"""Configures the measurement location type for the segments.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_location_type (enums.PavtMeasurementLocationType, int):
                This parameter specifies whether the location at which the segment is measured is indicated by time or trigger. The
                default value is **Time**.

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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            measurement_location_type = (
                measurement_location_type.value
                if type(measurement_location_type) is enums.PavtMeasurementLocationType
                else measurement_location_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.pavt_configure_measurement_location_type(
                updated_selector_string, measurement_location_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_segments(self, selector_string, number_of_segments):
        r"""Configures the number of segments.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_segments (int):
                This parameter specifies the number of segments to be measured. The default value is 1.

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
            error_code = self._interpreter.pavt_configure_number_of_segments(
                updated_selector_string, number_of_segments
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_segment_measurement_interval_array(
        self, selector_string, segment_measurement_offset, segment_measurement_length
    ):
        r"""Configures an array of segment measurement offsets and lengths for the segments.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            segment_measurement_offset (float):
                This parameter specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or
                frequency error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**. The default value
                is 0.

            segment_measurement_length (float):
                This parameter specifies the duration within each segment over which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**. The default value
                is 1 millisecond.

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
            error_code = self._interpreter.pavt_configure_segment_measurement_interval_array(
                updated_selector_string, segment_measurement_offset, segment_measurement_length
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_segment_measurement_interval(
        self, selector_string, segment_measurement_offset, segment_measurement_length
    ):
        r"""Configures the segment measurement offset and length for the segments.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of segment
                number.

                Example:

                "segment0"

                You can use the :py:meth:`build_segment_string` method to build the selector string.

            segment_measurement_offset (float):
                This parameter specifies the time offset from the start of the segment for which the phase and amplitude, amplitude, or
                frequency error values are computed. This value is expressed in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**. The default value
                is 0.

            segment_measurement_length (float):
                This parameter specifies the duration within each segment over which the phase and amplitude, amplitude, or frequency
                error values are computed. This value is expressed in seconds. This attribute is valid when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_INTERVAL_MODE` attribute to **Variable**. The default value
                is 1 millisecond.

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
            error_code = self._interpreter.pavt_configure_segment_measurement_interval(
                updated_selector_string, segment_measurement_offset, segment_measurement_length
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_segment_start_time_list(self, selector_string, segment_start_time):
        r"""Configures the list of the segment start times.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            segment_start_time (float):
                This parameter specifies the start time of measurement of the segments. This value is expressed in seconds. You can use
                this parameter only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_LOCATION_TYPE`
                attribute to **Time**.

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
            error_code = self._interpreter.pavt_configure_segment_start_time_list(
                updated_selector_string, segment_start_time
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_segment_start_time_step(
        self, selector_string, number_of_segments, segment0_start_time, segment_interval
    ):
        r"""Configures the list of the segment start times based on **Segment0 Start Time** and **Segment Interval**. This method
        is used when the segments to be measured have equal duration.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_segments (int):
                This parameter specifies the number of segments to be measured. The default value is 1.

            segment0_start_time (float):
                This parameter specifies the start time for segment0. This value is expressed in seconds.

            segment_interval (float):
                This parameter specifies the difference in the start times between consecutive segments. This value is expressed in
                seconds.

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
            error_code = self._interpreter.pavt_configure_segment_start_time_step(
                updated_selector_string, number_of_segments, segment0_start_time, segment_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_segment_type_array(self, selector_string, segment_type):
        r"""Configures an array of segment types.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            segment_type (enums.PavtSegmentType, int):
                This parameter specifies the type of segment. The default value is **Phase and Amplitude**.

                +---------------------------------+--------------------------------------------------+
                | Name (Value)                    | Description                                      |
                +=================================+==================================================+
                | Phase and Amplitude (0)         | Phase and amplitude is measured in this segment. |
                +---------------------------------+--------------------------------------------------+
                | Amplitude (1)                   | Amplitude is measured in this segment.           |
                +---------------------------------+--------------------------------------------------+
                | Frequency Error Measurement (2) | Frequency error is measured in this segment.     |
                +---------------------------------+--------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            segment_type = (
                [v.value for v in segment_type]
                if (
                    isinstance(segment_type, list)
                    and all(isinstance(v, enums.PavtSegmentType) for v in segment_type)
                )
                else segment_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.pavt_configure_segment_type_array(
                updated_selector_string, segment_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_segment_type(self, selector_string, segment_type):
        r"""Configures the segment type.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of segment
                number.

                Example:

                "segment0"

                You can use the :py:meth:`build_segment_string` method to build the selector string.

            segment_type (enums.PavtSegmentType, int):
                This parameter specifies the type of segment. The default value is **Phase and Amplitude**.

                +---------------------------------+--------------------------------------------------+
                | Name (Value)                    | Description                                      |
                +=================================+==================================================+
                | Phase and Amplitude (0)         | Phase and amplitude is measured in this segment. |
                +---------------------------------+--------------------------------------------------+
                | Amplitude (1)                   | Amplitude is measured in this segment.           |
                +---------------------------------+--------------------------------------------------+
                | Frequency Error Measurement (2) | Frequency error is measured in this segment.     |
                +---------------------------------+--------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            segment_type = (
                segment_type.value if type(segment_type) is enums.PavtSegmentType else segment_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.pavt_configure_segment_type(
                updated_selector_string, segment_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
