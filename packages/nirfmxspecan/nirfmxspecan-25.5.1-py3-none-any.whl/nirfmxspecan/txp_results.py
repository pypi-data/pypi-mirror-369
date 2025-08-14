"""Provides methods to fetch and read the Txp measurement results."""

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


class TxpResults(object):
    """Provides methods to fetch and read the Txp measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Txp measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_average_mean_power(self, selector_string):
        r"""Gets the mean power of the signal. This value is expressed in dBm. Only the samples above the threshold are used by
        the measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to
        **True**. When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the
        mean power is measured using the power trace averaged over multiple acquisitions.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean power of the signal. This value is expressed in dBm. Only the samples above the threshold are used by
                the measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to
                **True**. When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the
                mean power is measured using the power trace averaged over multiple acquisitions.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.TXP_RESULTS_AVERAGE_MEAN_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_peak_to_average_ratio(self, selector_string):
        r"""Gets the ratio of the peak power of the signal to the mean power. Only the samples above the threshold are used by
        the measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to
        **True**. When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the
        peak and mean powers are measured using the power trace averaged over multiple acquisitions.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the ratio of the peak power of the signal to the mean power. Only the samples above the threshold are used by
                the measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to
                **True**. When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the
                peak and mean powers are measured using the power trace averaged over multiple acquisitions.

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
                attributes.AttributeID.TXP_RESULTS_PEAK_TO_AVERAGE_RATIO.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_maximum_power(self, selector_string):
        r"""Gets the maximum power of the averaged power trace. This value is expressed in dBm.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the maximum power of the averaged power trace. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.TXP_RESULTS_MAXIMUM_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_minimum_power(self, selector_string):
        r"""Gets the minimum power of the averaged power trace. This value is expressed in dBm.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the minimum power of the averaged power trace. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.TXP_RESULTS_MINIMUM_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_measurement(self, selector_string, timeout):
        r"""Returns the powers measured using the TXP measurement.

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
            Tuple (average_mean_power, peak_to_average_ratio, maximum_power, minimum_power, error_code):

            average_mean_power (float):
                This parameter returns the mean power, in dBm, of the signal. Only the samples above the threshold are used by the
                measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.
                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the mean
                power is measured on the power trace averaged over multiple acquisitions.

            peak_to_average_ratio (float):
                This parameter returns the ratio of the peak power of the signal to the mean power. Only the samples above the
                threshold are used by the measurement when you set the TXP Threshold Enabled attribute to **True**. When you set the
                TXP Averaging Enabled attribute to **True**, the peak and mean powers are measured using the power trace averaged over
                multiple acquisitions.

            maximum_power (float):
                This parameter returns the maximum power, in dBm, of the averaged power trace.

            minimum_power (float):
                This parameter returns the minimum power, in dBm, of the averaged power trace.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_mean_power, peak_to_average_ratio, maximum_power, minimum_power, error_code = (
                self._interpreter.txp_fetch_measurement(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_mean_power, peak_to_average_ratio, maximum_power, minimum_power, error_code

    @_raise_if_disposed
    def fetch_power_trace(self, selector_string, timeout, power):
        r"""Fetches the power trace used for the transmit power (TxP) measurement.

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

            power (numpy.float32):
                This parameter returns the measured average power, in units specified by
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute, at each time instance.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start time, in seconds.

            dx (float):
                This parameter returns the sample duration, in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.txp_fetch_power_trace(
                updated_selector_string, timeout, power
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def read(self, selector_string, timeout):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns the transmit power (TXP)
        measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

        Returns:
            Tuple (average_mean_power, peak_to_average_ratio, maximum_power, minimum_power, error_code):

            average_mean_power (float):
                This parameter returns the mean power, in dBm, of the signal. Only the samples above the threshold are used by the
                measurement when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.
                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**, the mean
                power is measured on the power trace averaged over multiple acquisitions.

            peak_to_average_ratio (float):
                This parameter returns the ratio of the peak power of the signal to the mean power. Only the samples above the
                threshold are used by the measurement when you set the TXP Threshold Enabled attribute to **True**. When you set the
                TXP Averaging Enabled attribute to **True**, the peak and mean powers are measured using the power trace averaged over
                multiple acquisitions.

            maximum_power (float):
                This parameter returns the maximum power, in dBm, of the averaged power trace.

            minimum_power (float):
                This parameter returns the minimum power, in dBm, of the averaged power trace.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_mean_power, peak_to_average_ratio, maximum_power, minimum_power, error_code = (
                self._interpreter.txp_read(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_mean_power, peak_to_average_ratio, maximum_power, minimum_power, error_code
