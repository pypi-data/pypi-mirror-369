"""Provides methods to fetch and read the Obw measurement results."""

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


class ObwResults(object):
    """Provides methods to fetch and read the Obw measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Obw measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_occupied_bandwidth(self, selector_string):
        r"""Gets the bandwidth that occupies the percentage of the total power of the signal that you specify in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_PERCENTAGE` attribute. This value is expressed in Hz.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the bandwidth that occupies the percentage of the total power of the signal that you specify in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.BANDWIDTH_PERCENTAGE` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.OBW_RESULTS_OCCUPIED_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_average_power(self, selector_string):
        r"""Gets the total integrated power, in dBm, of the averaged spectrum acquired by the OBW measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. The OBW Results Avg Pwr attribute
        returns the power spectral density, in dBm/Hz,  when you set the OBW Power Units attribute to **dBm/Hz**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the total integrated power, in dBm, of the averaged spectrum acquired by the OBW measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. The OBW Results Avg Pwr attribute
                returns the power spectral density, in dBm/Hz,  when you set the OBW Power Units attribute to **dBm/Hz**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.OBW_RESULTS_AVERAGE_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_start_frequency(self, selector_string):
        r"""Gets the start frequency of the OBW. This value is expressed in Hz.

        The OBW is calculated using the following formula: OBW = stop frequency - start frequency

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the start frequency of the OBW. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.OBW_RESULTS_START_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_stop_frequency(self, selector_string):
        r"""Gets the stop frequency of the OBW. This value is expressed in Hz.

        The OBW is calculated using the following formula: OBW = stop frequency - start frequency

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the stop frequency of the OBW. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.OBW_RESULTS_STOP_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_frequency_resolution(self, selector_string):
        r"""Gets the frequency bin spacing of the spectrum acquired by the OBW measurement. This value is expressed in Hz.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency bin spacing of the spectrum acquired by the OBW measurement. This value is expressed in Hz.

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
                attributes.AttributeID.OBW_RESULTS_FREQUENCY_RESOLUTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_measurement(self, selector_string, timeout):
        r"""Returns the occupied bandwidth (OBW) measurement.

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
            Tuple (occupied_bandwidth, average_power, frequency_resolution, start_frequency, stop_frequency, error_code):

            occupied_bandwidth (float):
                This parameter returns the occupied bandwidth, in Hz.

            average_power (float):
                This parameter returns the total integrated power of the averaged spectrum acquired by the OBW measurement when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. This method returns the power
                spectral density when you set the OBW Power Units attribute to **dBm/Hz**.

            frequency_resolution (float):
                This parameter returns the frequency bin spacing, in Hz, of the spectrum acquired by the measurement.

            start_frequency (float):
                This parameter returns the start frequency, in Hz, of the OBW. The OBW is calculated using the following formula: OBW =
                stop frequency - start frequency

            stop_frequency (float):
                This parameter returns the stop frequency, in Hz, of the OBW.

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
                occupied_bandwidth,
                average_power,
                frequency_resolution,
                start_frequency,
                stop_frequency,
                error_code,
            ) = self._interpreter.obw_fetch_measurement(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            occupied_bandwidth,
            average_power,
            frequency_resolution,
            start_frequency,
            stop_frequency,
            error_code,
        )

    @_raise_if_disposed
    def fetch_spectrum_trace(self, selector_string, timeout, spectrum):
        r"""Fetches the spectrum trace used for the OBW measurement.

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
            x0, dx, error_code = self._interpreter.obw_fetch_spectrum_trace(
                updated_selector_string, timeout, spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def read(self, selector_string, timeout):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns occupied bandwidth (OBW)
        measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

        Returns:
            Tuple (occupied_bandwidth, average_power, frequency_resolution, start_frequency, stop_frequency, error_code):

            occupied_bandwidth (float):
                This parameter returns the occupied bandwidth, in Hz.

            average_power (float):
                This parameter returns the total integrated power of the averaged spectrum acquired by the OBW measurement when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. This method returns the power
                spectral density when you set the OBW Power Units attribute to **dBm/Hz**.

            frequency_resolution (float):
                This parameter returns the frequency bin spacing, in Hz, of the spectrum acquired by the OBW measurement.

            start_frequency (float):
                This parameter returns the start frequency, in Hz, of the OBW. The OBW is calculated using the following formula: OBW =
                stop frequency - start frequency

            stop_frequency (float):
                This parameter returns the stop frequency, in Hz, of the OBW.

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
                occupied_bandwidth,
                average_power,
                frequency_resolution,
                start_frequency,
                stop_frequency,
                error_code,
            ) = self._interpreter.obw_read(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            occupied_bandwidth,
            average_power,
            frequency_resolution,
            start_frequency,
            stop_frequency,
            error_code,
        )
