"""Provides methods to fetch and read the Acp measurement results."""

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


class AcpResults(object):
    """Provides methods to fetch and read the Acp measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Acp measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_total_carrier_power(self, selector_string):
        r"""Gets the total integrated power, in dBm, of all the active carriers measured when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**.

        Returns the power spectral density, in dBm/Hz, based on the power in all the active carriers measured when you
        set the ACP Power Units attribute to **dBm/Hz**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the total integrated power, in dBm, of all the active carriers measured when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**.

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
                attributes.AttributeID.ACP_RESULTS_TOTAL_CARRIER_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_frequency_resolution(self, selector_string):
        r"""Gets the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.

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
                attributes.AttributeID.ACP_RESULTS_FREQUENCY_RESOLUTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_frequency(self, selector_string):
        r"""Gets the center frequency of the carrier relative to the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the center frequency of the carrier relative to the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.ACP_RESULTS_CARRIER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_integration_bandwidth(self, selector_string):
        r"""Gets the frequency range, over which the measurement integrates the carrier power. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency range, over which the measurement integrates the carrier power. This value is expressed in Hz.

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
                attributes.AttributeID.ACP_RESULTS_CARRIER_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_absolute_power(self, selector_string):
        r"""Gets the measured carrier power.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        The carrier power is reported in dBm when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the ACP
        Power Units attribute to **dBm/Hz**.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the measured carrier power.

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
                attributes.AttributeID.ACP_RESULTS_CARRIER_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_total_relative_power(self, selector_string):
        r"""Gets the carrier power measured relative to the total carrier power of all active carriers. This value is expressed
        in dB.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the carrier power measured relative to the total carrier power of all active carriers. This value is expressed
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
                updated_selector_string,
                attributes.AttributeID.ACP_RESULTS_CARRIER_TOTAL_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_frequency_reference_carrier(self, selector_string):
        r"""Gets the index of the carrier used as a reference to define the center frequency of the lower (negative) offset
        channel. Lower offset channels are channels that are to the left of the carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the index of the carrier used as a reference to define the center frequency of the lower (negative) offset
                channel. Lower offset channels are channels that are to the left of the carrier.

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
                attributes.AttributeID.ACP_RESULTS_LOWER_OFFSET_FREQUENCY_REFERENCE_CARRIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_frequency(self, selector_string):
        r"""Gets the center frequency of the lower offset channel relative to the center frequency of the closest carrier. The
        offset frequency has a negative value.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the center frequency of the lower offset channel relative to the center frequency of the closest carrier. The
                offset frequency has a negative value.

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
                attributes.AttributeID.ACP_RESULTS_LOWER_OFFSET_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_integration_bandwidth(self, selector_string):
        r"""Gets the integration bandwidth used to measure the power in the lower offset channel.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the integration bandwidth used to measure the power in the lower offset channel.

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
                attributes.AttributeID.ACP_RESULTS_LOWER_OFFSET_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_power_reference_carrier(self, selector_string):
        r"""Gets the index of the carrier used as the power reference to measure the lower (negative) offset channel relative
        power.

        A value of -1 indicates that the total power of all active carriers is used as the reference power. The
        measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to set
        the power reference.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the index of the carrier used as the power reference to measure the lower (negative) offset channel relative
                power.

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
                attributes.AttributeID.ACP_RESULTS_LOWER_OFFSET_POWER_REFERENCE_CARRIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_absolute_power(self, selector_string):
        r"""Gets the lower offset channel power.

        The offset channel power is reported in dBm when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the ACP
        Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the lower offset channel power.

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
                attributes.AttributeID.ACP_RESULTS_LOWER_OFFSET_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_relative_power(self, selector_string):
        r"""Gets the lower offset channel power measured relative to the integrated power of the power reference carrier. This
        value is expressed in dB.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the lower offset channel power measured relative to the integrated power of the power reference carrier. This
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
                attributes.AttributeID.ACP_RESULTS_LOWER_OFFSET_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_frequency_reference_carrier(self, selector_string):
        r"""Gets the index of the carrier used as a reference to define the center frequency of the upper (positive) offset
        channel. Upper offset channels are channels that are to the right of the carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the index of the carrier used as a reference to define the center frequency of the upper (positive) offset
                channel. Upper offset channels are channels that are to the right of the carrier.

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
                attributes.AttributeID.ACP_RESULTS_UPPER_OFFSET_FREQUENCY_REFERENCE_CARRIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_frequency(self, selector_string):
        r"""Gets the center frequency of the upper offset channel relative to the center frequency of the closest carrier. The
        offset frequency has a positive value.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the center frequency of the upper offset channel relative to the center frequency of the closest carrier. The
                offset frequency has a positive value.

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
                attributes.AttributeID.ACP_RESULTS_UPPER_OFFSET_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_integration_bandwidth(self, selector_string):
        r"""Gets the integration bandwidth used to measure the power in the upper offset channel.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the integration bandwidth used to measure the power in the upper offset channel.

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
                attributes.AttributeID.ACP_RESULTS_UPPER_OFFSET_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_power_reference_carrier(self, selector_string):
        r"""Gets the index of the carrier used as the power reference to measure the upper (positive) offset channel relative
        power.

        A value of -1 indicates that the total power of all active carriers is used as the reference power. The
        measurement uses the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to set
        the power reference.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the index of the carrier used as the power reference to measure the upper (positive) offset channel relative
                power.

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
                attributes.AttributeID.ACP_RESULTS_UPPER_OFFSET_POWER_REFERENCE_CARRIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_absolute_power(self, selector_string):
        r"""Gets the upper offset channel power.

        The offset channel power is reported in dBm when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the ACP
        Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the upper offset channel power.

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
                attributes.AttributeID.ACP_RESULTS_UPPER_OFFSET_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_relative_power(self, selector_string):
        r"""Gets the upper offset channel power measured relative to the integrated power of the power reference carrier. This
        value is expressed in dB.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the upper offset channel power measured relative to the integrated power of the power reference carrier. This
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
                attributes.AttributeID.ACP_RESULTS_UPPER_OFFSET_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_absolute_powers_trace(
        self, selector_string, timeout, trace_index, absolute_powers_trace
    ):
        r"""Fetches the absolute powers trace for adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            trace_index (int):
                Specifies the index of the trace to fetch. The **traceIndex** can range from 0 to (Number of carriers + 2*Number of
                offsets).

            absolute_powers_trace (numpy.float32):
                This parameter returns the integrated power in dBm, or power spectral density in dBm/Hz, in the channel based on the
                power units specified.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency of the channel. This value is expressed in Hz.

            dx (float):
                This parameter returns the frequency bin spacing. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.acp_fetch_absolute_powers_trace(
                updated_selector_string, timeout, trace_index, absolute_powers_trace
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_carrier_measurement(self, selector_string, timeout):
        r"""Returns the measured carrier power.

        Use "carrier<
        *
        n
        *
        >" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and carrier number.

                Example:

                "carrier0"

                "result::r1/carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (absolute_power, total_relative_power, carrier_offset, integration_bandwidth, error_code):

            absolute_power (float):
                This parameter returns the measured carrier power. The carrier power is reported in dBm or dBm/Hz based on the value of
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute.

            total_relative_power (float):
                This parameter returns the carrier power, in dB, measured relative to the total carrier power of all active carriers.

            carrier_offset (float):
                This parameter returns the center frequency, in Hz, of the carrier relative to the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute.

            integration_bandwidth (float):
                This parameter returns the frequency range, in Hz, over which the measurement integrates the carrier power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                absolute_power,
                total_relative_power,
                carrier_offset,
                integration_bandwidth,
                error_code,
            ) = self._interpreter.acp_fetch_carrier_measurement(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            absolute_power,
            total_relative_power,
            carrier_offset,
            integration_bandwidth,
            error_code,
        )

    @_raise_if_disposed
    def fetch_frequency_resolution(self, selector_string, timeout):
        r"""Returns the frequency resolution, in Hz, of the spectrum acquired by the measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (frequency_resolution, error_code):

            frequency_resolution (float):
                This parameter returns the frequency bin spacing, in Hz, of the spectrum acquired by the measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            frequency_resolution, error_code = self._interpreter.acp_fetch_frequency_resolution(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return frequency_resolution, error_code

    @_raise_if_disposed
    def fetch_offset_measurement_array(self, selector_string, timeout):
        r"""Returns the absolute and relative powers measured in the offset channel. The relative powers are measured relative to
        the integrated power of the power reference carrier. The relative powers are not measured if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute for the reference carrier to **Passive**.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (lower_relative_power, upper_relative_power, lower_absolute_power, upper_absolute_power, error_code):

            lower_relative_power (float):
                This parameter returns the array of lower offset channel powers, in dB,  measured relative to the integrated power of
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OFFSET_POWER_REFERENCE_CARRIER` attribute.

            upper_relative_power (float):
                This parameter returns the array of upper offset channel powers, in dB,  measured relative to the integrated power of
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OFFSET_POWER_REFERENCE_CARRIER` attribute.

            lower_absolute_power (float):
                This parameter returns the array of lower offset channel powers.

            upper_absolute_power (float):
                This parameter returns the array of upper offset channel powers.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                lower_relative_power,
                upper_relative_power,
                lower_absolute_power,
                upper_absolute_power,
                error_code,
            ) = self._interpreter.acp_fetch_offset_measurement_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            lower_relative_power,
            upper_relative_power,
            lower_absolute_power,
            upper_absolute_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_offset_measurement(self, selector_string, timeout):
        r"""Returns the absolute and relative powers measured in the offset channel. The relative powers are measured relative to
        the integrated power of the power reference carrier. The relative powers are not measured if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute to **Passive**.

        Use "offset<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and offset number.

                Example:

                "offset0"

                "result::r1/offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (lower_relative_power, upper_relative_power, lower_absolute_power, upper_absolute_power, error_code):

            lower_relative_power (float):
                This parameter returns the lower offset channel power, in dB,  measured relative to the integrated power of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OFFSET_POWER_REFERENCE_CARRIER` attribute.

            upper_relative_power (float):
                This parameter returns the upper offset channel power, in dB,  measured relative to the integrated power of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OFFSET_POWER_REFERENCE_CARRIER` attribute.

            lower_absolute_power (float):
                This parameter returns the lower offset channel power.

            upper_absolute_power (float):
                This parameter returns the upper offset channel power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                lower_relative_power,
                upper_relative_power,
                lower_absolute_power,
                upper_absolute_power,
                error_code,
            ) = self._interpreter.acp_fetch_offset_measurement(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            lower_relative_power,
            upper_relative_power,
            lower_absolute_power,
            upper_absolute_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_relative_powers_trace(
        self, selector_string, timeout, trace_index, relative_powers_trace
    ):
        r"""Fetches the relative powers trace for adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            trace_index (int):
                Specifies the index of the trace to fetch. The **traceIndex** can range from 0 to (Number of carriers + 2*Number of
                offsets).

            relative_powers_trace (numpy.float32):
                This parameter returns the relative power, in dB, measured in each channel relative to power reference carrier.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency of the channel. This value is expressed in Hz.

            dx (float):
                This parameter returns the frequency bin spacing. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.acp_fetch_relative_powers_trace(
                updated_selector_string, timeout, trace_index, relative_powers_trace
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_spectrum(self, selector_string, timeout, spectrum):
        r"""Fetches the spectrum used for adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            spectrum (numpy.float32):
                This parameter returns the array of averaged powers measured at each frequency bin. This value is expressed in dBm.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency. This value is expressed in Hz.

            dx (float):
                This parameter returns the frequency bin spacing. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.acp_fetch_spectrum(
                updated_selector_string, timeout, spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_total_carrier_power(self, selector_string, timeout):
        r"""Fetches the total integrated power of all the active carriers measured when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. This method returns the power
        spectral density based on the power in all the active carriers measured when you set the ACP Power Units attribute to
        **dBm/Hz**.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (total_carrier_power, error_code):

            total_carrier_power (float):
                This parameter returns the total integrated power of all the active carriers measured when you set the ACP Power Units
                attribute to **dBm**. This parameter returns the power spectral density based on the power in all the active carriers
                measured when you set the ACP Power Units attribute to **dBm/Hz**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            total_carrier_power, error_code = self._interpreter.acp_fetch_total_carrier_power(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return total_carrier_power, error_code

    @_raise_if_disposed
    def read(self, selector_string, timeout):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns the adjacent channel power
        (ACP) measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

        Returns:
            Tuple (carrier_absolute_power, offset_ch0_lower_relative_power, offset_ch0_upper_relative_power, offset_ch1_lower_relative_power, offset_ch1_upper_relative_power, error_code):

            carrier_absolute_power (float):
                This parameter returns the power measured in carrier 0. The carrier power is reported in dBm or dBm/Hz based on the
                value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute.

            offset_ch0_lower_relative_power (float):
                This parameter returns the power measured in offset 0 in the negative band, relative to the power measured in the
                reference carrier specified using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OFFSET_POWER_REFERENCE_CARRIER` attribute.

            offset_ch0_upper_relative_power (float):
                This parameter returns the power measured in offset 0 in the positive band, relative to the power measured in the
                reference carrier specified using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OFFSET_POWER_REFERENCE_CARRIER` attribute.

            offset_ch1_lower_relative_power (float):
                This parameter returns the power measured in offset 1 in the negative band, relative to the power measured in the
                reference carrier specified using the ACP Results Lower Offset Pwr Ref Carrier attribute.

            offset_ch1_upper_relative_power (float):
                This parameter returns the power measured in offset 1 in the positive band, relative to the power measured in the
                reference carrier specified using the ACP Results Upper Offset Pwr Ref Carrier attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                carrier_absolute_power,
                offset_ch0_lower_relative_power,
                offset_ch0_upper_relative_power,
                offset_ch1_lower_relative_power,
                offset_ch1_upper_relative_power,
                error_code,
            ) = self._interpreter.acp_read(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            carrier_absolute_power,
            offset_ch0_lower_relative_power,
            offset_ch0_upper_relative_power,
            offset_ch1_lower_relative_power,
            offset_ch1_upper_relative_power,
            error_code,
        )
