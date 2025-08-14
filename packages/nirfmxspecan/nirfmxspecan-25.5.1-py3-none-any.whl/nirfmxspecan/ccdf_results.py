"""Provides methods to fetch and read the Ccdf measurement results."""

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


class CcdfResults(object):
    """Provides methods to fetch and read the Ccdf measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Ccdf measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_mean_power(self, selector_string):
        r"""Gets the average power of all the samples. This value is expressed in dBm. If you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**, samples above the threshold
        are measured.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the average power of all the samples. This value is expressed in dBm. If you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**, samples above the threshold
                are measured.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.CCDF_RESULTS_MEAN_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_power_percentile(self, selector_string):
        r"""Gets the percentage of samples that have more power than the mean power.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the percentage of samples that have more power than the mean power.

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
                attributes.AttributeID.CCDF_RESULTS_MEAN_POWER_PERCENTILE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_ten_percent_power(self, selector_string):
        r"""Gets the power above the mean power, over which 10% of the total samples in the signal are present. This value is
        expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power above the mean power, over which 10% of the total samples in the signal are present. This value is
                expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.CCDF_RESULTS_TEN_PERCENT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_one_percent_power(self, selector_string):
        r"""Gets the power above the mean power, over which 1% of the total samples in the signal are present. This value is
        expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power above the mean power, over which 1% of the total samples in the signal are present. This value is
                expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.CCDF_RESULTS_ONE_PERCENT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_one_tenth_percent_power(self, selector_string):
        r"""Gets the power above the mean power, over which 0.1% of the total samples in the signal are present. This value is
        expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power above the mean power, over which 0.1% of the total samples in the signal are present. This value is
                expressed in dB.

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
                attributes.AttributeID.CCDF_RESULTS_ONE_TENTH_PERCENT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_one_hundredth_percent_power(self, selector_string):
        r"""Gets the power above the mean power, over which 0.01% of the total samples in the signal are present. This value is
        expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power above the mean power, over which 0.01% of the total samples in the signal are present. This value is
                expressed in dB.

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
                attributes.AttributeID.CCDF_RESULTS_ONE_HUNDREDTH_PERCENT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_one_thousandth_percent_power(self, selector_string):
        r"""Gets the power above the mean power, over which 0.001% of the total samples in the signal are present. This value is
        expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power above the mean power, over which 0.001% of the total samples in the signal are present. This value is
                expressed in dB.

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
                attributes.AttributeID.CCDF_RESULTS_ONE_THOUSANDTH_PERCENT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_one_ten_thousandth_percent_power(self, selector_string):
        r"""Gets the power above the mean power, over which 0.0001% of the total samples in the signal are present. This value
        is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power above the mean power, over which 0.0001% of the total samples in the signal are present. This value
                is expressed in dB.

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
                attributes.AttributeID.CCDF_RESULTS_ONE_TEN_THOUSANDTH_PERCENT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_peak_power(self, selector_string):
        r"""Gets the peak power of the acquired signal, relative to the mean power.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power of the acquired signal, relative to the mean power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.CCDF_RESULTS_PEAK_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_measured_samples_count(self, selector_string):
        r"""Gets the total number of samples measured. The total number of samples includes only the samples above the
        threshold, when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the total number of samples measured. The total number of samples includes only the samples above the
                threshold, when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**.

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
                attributes.AttributeID.CCDF_RESULTS_MEASURED_SAMPLES_COUNT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_basic_power_probabilities(self, selector_string, timeout):
        r"""Returns CCDF power probabilities.

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
            Tuple (ten_percent_power, one_percent_power, one_tenth_percent_power, one_hundredth_percent_power, one_thousandth_percent_power, one_ten_thousandth_percent_power, error_code):

            ten_percent_power (float):
                This parameter returns the power, in dB, above the mean power, over which 10% of the total samples in the signal are
                present.

            one_percent_power (float):
                This parameter returns the power, in dB, above the mean power, over which 1% of the total samples in the signal are
                present.

            one_tenth_percent_power (float):
                This parameter returns the power, in dB, above the mean power, over which 0.1% of the total samples in the signal are
                present.

            one_hundredth_percent_power (float):
                This parameter returns the power, in dB, above the mean power, over which 0.01% of the total samples in the signal are
                present.

            one_thousandth_percent_power (float):
                This parameter returns the power, in dB, above the mean power, over which 0.001% of the total samples in the signal are
                present.

            one_ten_thousandth_percent_power (float):
                This parameter returns the power, in dB, above the mean power, over which 0.0001% of the total samples in the signal
                are present.

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
                ten_percent_power,
                one_percent_power,
                one_tenth_percent_power,
                one_hundredth_percent_power,
                one_thousandth_percent_power,
                one_ten_thousandth_percent_power,
                error_code,
            ) = self._interpreter.ccdf_fetch_basic_power_probabilities(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            ten_percent_power,
            one_percent_power,
            one_tenth_percent_power,
            one_hundredth_percent_power,
            one_thousandth_percent_power,
            one_ten_thousandth_percent_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_gaussian_probabilities_trace(self, selector_string, timeout, gaussian_probabilities):
        r"""Fetches the Gaussian probabilities trace for the CCDF measurement.

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

            gaussian_probabilities (numpy.float32):
                This parameter returns the Gaussian probabilities.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter represents the mean power.

            dx (float):
                This parameter returns the bin size used by the CCDF measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.ccdf_fetch_gaussian_probabilities_trace(
                updated_selector_string, timeout, gaussian_probabilities
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_power(self, selector_string, timeout):
        r"""Returns the mean power and peak power for the CCDF measurement.

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
            Tuple (mean_power, mean_power_percentile, peak_power, measured_samples_count, error_code):

            mean_power (float):
                This parameter returns the average power, in dBm, of all the samples. If you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**, samples above the threshold
                are measured.

            mean_power_percentile (float):
                This parameter returns the percentage of samples that have more power than the mean power.

            peak_power (float):
                This parameter returns the peak power of the acquired signal, relative to the mean power.

            measured_samples_count (int):
                This parameter returns the total number of samples measured.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            mean_power, mean_power_percentile, peak_power, measured_samples_count, error_code = (
                self._interpreter.ccdf_fetch_power(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return mean_power, mean_power_percentile, peak_power, measured_samples_count, error_code

    @_raise_if_disposed
    def fetch_probabilities_trace(self, selector_string, timeout, probabilities):
        r"""Returns the probabilities trace for the CCDF measurement.

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

            probabilities (numpy.float32):
                This parameter returns the probability, as a percentage, indicating the occurrence of samples in the signal with power
                greater than the mean power by x dB.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the mean power.

            dx (float):
                This parameter returns the bin size used by the CCDF measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.ccdf_fetch_probabilities_trace(
                updated_selector_string, timeout, probabilities
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def read(self, selector_string, timeout):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns complementary cumulative
        distribution function (CCDF) measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

        Returns:
            Tuple (mean_power, mean_power_percentile, peak_power, measured_samples_count, error_code):

            mean_power (float):
                This parameter returns the average power, in dBm, of all the samples. If you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_ENABLED` attribute to **True**, samples above the threshold
                are measured.

            mean_power_percentile (float):
                This parameter returns the percentage of samples that have more power than the mean power.

            peak_power (float):
                This parameter returns the peak power of the acquired signal, relative to the mean power.

            measured_samples_count (int):
                This parameter returns the total number of samples measured.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            mean_power, mean_power_percentile, peak_power, measured_samples_count, error_code = (
                self._interpreter.ccdf_read(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return mean_power, mean_power_percentile, peak_power, measured_samples_count, error_code
