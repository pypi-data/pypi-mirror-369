"""Provides methods to fetch and read the Fcnt measurement results."""

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


class FcntResults(object):
    """Provides methods to fetch and read the Fcnt measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Fcnt measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_average_relative_frequency(self, selector_string):
        r"""Gets the signal frequency relative to the RF center frequency. Only samples above the threshold are used when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the signal frequency relative to the RF center frequency. Only samples above the threshold are used when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

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
                attributes.AttributeID.FCNT_RESULTS_AVERAGE_RELATIVE_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_average_absolute_frequency(self, selector_string):
        r"""Gets the RF signal frequency. Only samples above the threshold are used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the RF signal frequency. Only samples above the threshold are used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

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
                attributes.AttributeID.FCNT_RESULTS_AVERAGE_ABSOLUTE_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_phase(self, selector_string):
        r"""Gets the net phase of the vector sum of the I/Q samples used for frequency measurement.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the net phase of the vector sum of the I/Q samples used for frequency measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.FCNT_RESULTS_MEAN_PHASE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_allan_deviation(self, selector_string):
        r"""Gets the two-sample deviation of the measured frequency.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the two-sample deviation of the measured frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.FCNT_RESULTS_ALLAN_DEVIATION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_allan_deviation(self, selector_string, timeout):
        r"""Fetches the two-sample deviation of the measured frequency.

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
            Tuple (allan_deviation, error_code):

            allan_deviation (float):
                This parameter returns the two-sample deviation of the measured frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            allan_deviation, error_code = self._interpreter.fcnt_fetch_allan_deviation(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return allan_deviation, error_code

    @_raise_if_disposed
    def fetch_frequency_trace(self, selector_string, timeout, frequency_trace):
        r"""Fetches the frequency trace for FCnt measurement.

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

            frequency_trace (numpy.float32):
                This parameter returns the frequency, in Hz, measured at each time instance.

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
            x0, dx, error_code = self._interpreter.fcnt_fetch_frequency_trace(
                updated_selector_string, timeout, frequency_trace
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_measurement(self, selector_string, timeout):
        r"""Returns the frequency and phase measured using the FCnt measurement.

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
            Tuple (average_relative_frequency, average_absolute_frequency, mean_phase, error_code):

            average_relative_frequency (float):
                This parameter returns the signal frequency relative to the RF center frequency.  Only samples above the threshold are
                used when you set the FCnt Threshold Enabled attribute to **True**.

            average_absolute_frequency (float):
                This parameter returns the RF signal frequency. Only samples above the threshold are used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

            mean_phase (float):
                This parameter returns the net phase of the vector sum of the I/Q samples used for frequency measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_relative_frequency, average_absolute_frequency, mean_phase, error_code = (
                self._interpreter.fcnt_fetch_measurement(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_relative_frequency, average_absolute_frequency, mean_phase, error_code

    @_raise_if_disposed
    def fetch_phase_trace(self, selector_string, timeout, phase_trace):
        r"""Fetches the phase trace for FCnt measurement.

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

            phase_trace (numpy.float32):
                This parameter returns the averaged phase, in degrees, measured at each time instance.

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
            x0, dx, error_code = self._interpreter.fcnt_fetch_phase_trace(
                updated_selector_string, timeout, phase_trace
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_power_trace(self, selector_string, timeout, power_trace):
        r"""Fetches the power trace for FCnt measurement.

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

            power_trace (numpy.float32):
                This parameter returns the measured average power, in dBm, at each time instance.

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
            x0, dx, error_code = self._interpreter.fcnt_fetch_power_trace(
                updated_selector_string, timeout, power_trace
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def read(self, selector_string, timeout):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns the frequency count (FCnt)
        measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

        Returns:
            Tuple (average_relative_frequency, average_absolute_frequency, mean_phase, error_code):

            average_relative_frequency (float):
                This parameter returns the signal frequency relative to the RF center frequency.  Only samples above the threshold are
                used when you set the FCnt Threshold Enabled attribute to **True**.

            average_absolute_frequency (float):
                This parameter returns the RF signal frequency. Only samples above the threshold are used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

            mean_phase (float):
                This parameter returns the net phase of the vector sum of the I/Q samples used for frequency measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_relative_frequency, average_absolute_frequency, mean_phase, error_code = (
                self._interpreter.fcnt_read(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_relative_frequency, average_absolute_frequency, mean_phase, error_code
