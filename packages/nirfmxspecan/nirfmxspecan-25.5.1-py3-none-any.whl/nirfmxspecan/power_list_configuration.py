"""Provides methods to configure the PowerList measurement."""

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


class PowerListConfiguration(object):
    """Provides methods to configure the PowerList measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the PowerList measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the PowerList measurement.

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
                Specifies whether to enable the PowerList measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.POWERLIST_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the PowerList measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the PowerList measurement.

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
                attributes.AttributeID.POWERLIST_MEASUREMENT_ENABLED.value,
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
                updated_selector_string, attributes.AttributeID.POWERLIST_NUMBER_OF_SEGMENTS.value
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
                updated_selector_string,
                attributes.AttributeID.POWERLIST_NUMBER_OF_SEGMENTS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_length(self, selector_string):
        r"""Gets an array of durations, each corresponding to a segment, where each value must be at least the sum of
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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of durations, each corresponding to a segment, where each value must be at least the sum of
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_LENGTH` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_OFFSET` when the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute is set to **TimerEvent**. This
                value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.POWERLIST_SEGMENT_LENGTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_length(self, selector_string, value):
        r"""Sets an array of durations, each corresponding to a segment, where each value must be at least the sum of
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

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of durations, each corresponding to a segment, where each value must be at least the sum of
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_LENGTH` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SEGMENT_MEASUREMENT_OFFSET` when the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute is set to **TimerEvent**. This
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
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_frequency(self, selector_string):
        r"""Gets an array of expected carrier frequencies for the RF signal to be acquired, each corresponding to a segment,
        to which the signal analyzer tunes. This value is expressed in Hz.

        RFmx returns an error if this attribute is not configured or if the size of the configured values is smaller
        than the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of expected carrier frequencies for the RF signal to be acquired, each corresponding to a segment,
                to which the signal analyzer tunes. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.POWERLIST_SEGMENT_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_frequency(self, selector_string, value):
        r"""Sets an array of expected carrier frequencies for the RF signal to be acquired, each corresponding to a segment,
        to which the signal analyzer tunes. This value is expressed in Hz.

        RFmx returns an error if this attribute is not configured or if the size of the configured values is smaller
        than the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of expected carrier frequencies for the RF signal to be acquired, each corresponding to a segment,
                to which the signal analyzer tunes. This value is expressed in Hz.

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
                attributes.AttributeID.POWERLIST_SEGMENT_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_reference_level(self, selector_string):
        r"""Gets an array of reference levels, each representing the maximum expected power of the RF input signal for its
        corresponding segment. This value is configured in dBm for RF devices.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of reference levels, each representing the maximum expected power of the RF input signal for its
                corresponding segment. This value is configured in dBm for RF devices.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_REFERENCE_LEVEL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_reference_level(self, selector_string, value):
        r"""Sets an array of reference levels, each representing the maximum expected power of the RF input signal for its
        corresponding segment. This value is configured in dBm for RF devices.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of reference levels, each representing the maximum expected power of the RF input signal for its
                corresponding segment. This value is configured in dBm for RF devices.

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
                attributes.AttributeID.POWERLIST_SEGMENT_REFERENCE_LEVEL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_measurement_length(self, selector_string):
        r"""Gets an array of durations, each corresponding to a segment, over which the power value is computed. This value is
        expressed in seconds.

        RFmx returns an error if this attribute is not configured or if the size of the configured values is smaller
        than the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of durations, each corresponding to a segment, over which the power value is computed. This value is
                expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_MEASUREMENT_LENGTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_measurement_length(self, selector_string, value):
        r"""Sets an array of durations, each corresponding to a segment, over which the power value is computed. This value is
        expressed in seconds.

        RFmx returns an error if this attribute is not configured or if the size of the configured values is smaller
        than the :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of durations, each corresponding to a segment, over which the power value is computed. This value is
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
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_MEASUREMENT_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_measurement_offset(self, selector_string):
        r"""Gets an array of time offsets from the start of each segment, over which the power value is computed. This value
        is expressed in seconds.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of time offsets from the start of each segment, over which the power value is computed. This value
                is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_MEASUREMENT_OFFSET.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_measurement_offset(self, selector_string, value):
        r"""Sets an array of time offsets from the start of each segment, over which the power value is computed. This value
        is expressed in seconds.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of time offsets from the start of each segment, over which the power value is computed. This value
                is expressed in seconds.

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
                attributes.AttributeID.POWERLIST_SEGMENT_MEASUREMENT_OFFSET.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_rbw_filter_bandwidth(self, selector_string):
        r"""Gets an array of bandwidth of the resolution bandwidth (RBW) filters used to measure the signal corresponding to
        each segment. This value is expressed in Hz.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100 kHz. RFmx applies this default value for all segments when the attribute is either
        unconfigured or reset to its default.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of bandwidth of the resolution bandwidth (RBW) filters used to measure the signal corresponding to
                each segment. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_RBW_FILTER_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets an array of bandwidth of the resolution bandwidth (RBW) filters used to measure the signal corresponding to
        each segment. This value is expressed in Hz.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100 kHz. RFmx applies this default value for all segments when the attribute is either
        unconfigured or reset to its default.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of bandwidth of the resolution bandwidth (RBW) filters used to measure the signal corresponding to
                each segment. This value is expressed in Hz.

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
                attributes.AttributeID.POWERLIST_SEGMENT_RBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_rbw_filter_type(self, selector_string):
        r"""Gets an array of digital resolution bandwidth (RBW) filter shapes, each corresponding to a segment.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies an array of digital resolution bandwidth (RBW) filter shapes, each corresponding to a segment.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_RBW_FILTER_TYPE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_rbw_filter_type(self, selector_string, value):
        r"""Sets an array of digital resolution bandwidth (RBW) filter shapes, each corresponding to a segment.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies an array of digital resolution bandwidth (RBW) filter shapes, each corresponding to a segment.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_RBW_FILTER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_rbw_filter_alpha(self, selector_string):
        r"""Gets an array of roll-off factor for the root-raised-cosine (RRC) filter, each corresponding to a segment.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1. RFmx applies this default value for all segments when the attribute is either
        unconfigured or reset to its default.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of roll-off factor for the root-raised-cosine (RRC) filter, each corresponding to a segment.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_RBW_FILTER_ALPHA.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_rbw_filter_alpha(self, selector_string, value):
        r"""Sets an array of roll-off factor for the root-raised-cosine (RRC) filter, each corresponding to a segment.

        RFmx returns an error if the size of the configured values is smaller than the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NUMBER_OF_SEGMENTS`.
        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1. RFmx applies this default value for all segments when the attribute is either
        unconfigured or reset to its default.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of roll-off factor for the root-raised-cosine (RRC) filter, each corresponding to a segment.

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
                attributes.AttributeID.POWERLIST_SEGMENT_RBW_FILTER_ALPHA.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_segment_trigger_type(self, selector_string):
        r"""Gets an array of trigger type, each corresponding to a segment.

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

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies an array of trigger type, each corresponding to a segment.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32_array(
                updated_selector_string, attributes.AttributeID.POWERLIST_SEGMENT_TRIGGER_TYPE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_segment_trigger_type(self, selector_string, value):
        r"""Sets an array of trigger type, each corresponding to a segment.

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

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies an array of trigger type, each corresponding to a segment.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32_array(
                updated_selector_string,
                attributes.AttributeID.POWERLIST_SEGMENT_TRIGGER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rbw_filter_array(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        r"""Configures array of the resolution bandwidth (RBW) filter to measure the power of the signal as seen through this
        filter, each corresponding to a segment.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw (float):
                This parameter specifies an array of bandwidths, in Hz, of the resolution bandwidth (RBW) filter used to acquire the
                fundamental signal, each corresponding to a segment.

            rbw_filter_type (int):
                This parameterSpecifies an array of digital resolution bandwidth (RBW) filter shapes, each corresponding to a segment.

                +--------------+----------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                  |
                +==============+==============================================================================================+
                | None (1)     | The measurement does not use any RBW filtering.                                              |
                +--------------+----------------------------------------------------------------------------------------------+
                | Gaussian (2) | The RBW filter has a Gaussian response.                                                      |
                +--------------+----------------------------------------------------------------------------------------------+
                | Flat (3)     | The RBW filter has a flat response.                                                          |
                +--------------+----------------------------------------------------------------------------------------------+
                | RRC (4)      | The RRC filter with the roll-off specified by RRC Alpha parameter is used as the RBW filter. |
                +--------------+----------------------------------------------------------------------------------------------+

            rrc_alpha (float):
                This parameter specifies an array of roll-off factor for the root-raised-cosine (RRC) filter, each corresponding to a
                segment.

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
            error_code = self._interpreter.powerlist_configure_rbw_filter_array(
                updated_selector_string, rbw, rbw_filter_type, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
