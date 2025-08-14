"""Provides methods to fetch and read the IM measurement results."""

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


class IMResults(object):
    """Provides methods to fetch and read the IM measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the IM measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_fundamental_lower_tone_power(self, selector_string):
        r"""Gets the peak power measured around the lower tone frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
        expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
        power at the lower tone frequency.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured around the lower tone frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the lower tone frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IM_RESULTS_LOWER_TONE_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_fundamental_upper_tone_power(self, selector_string):
        r"""Gets the peak power measured around the upper tone frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
        expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
        power at the upper tone frequency.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured around the upper tone frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the upper tone frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IM_RESULTS_UPPER_TONE_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_intermod_order(self, selector_string):
        r"""Gets the order of the intermod.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the order of the intermod.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_RESULTS_INTERMOD_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_intermod_power(self, selector_string):
        r"""Gets the peak power measured around the lower intermod frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
        expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
        power at the lower intermod frequency.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured around the lower intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the lower intermod frequency.

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
                attributes.AttributeID.IM_RESULTS_LOWER_INTERMOD_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_intermod_power(self, selector_string):
        r"""Gets the peak power measured around the upper intermod frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
        expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
        power at the upper intermod frequency.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured around the upper intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the upper intermod frequency.

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
                attributes.AttributeID.IM_RESULTS_UPPER_INTERMOD_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_worst_case_intermod_absolute_power(self, selector_string):
        r"""Gets the worst case intermod power that is equal to the maximum of the values of both the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_POWER` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_POWER` results. This value is expressed in dBm.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the worst case intermod power that is equal to the maximum of the values of both the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_POWER` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_POWER` results. This value is expressed in dBm.

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
                attributes.AttributeID.IM_RESULTS_WORST_CASE_INTERMOD_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_intermod_relative_power(self, selector_string):
        r"""Gets the relative peak power measured around the lower intermod frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
        expressed in dBc. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
        relative power at the lower intermod frequency.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the relative peak power measured around the lower intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBc. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                relative power at the lower intermod frequency.

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
                attributes.AttributeID.IM_RESULTS_LOWER_INTERMOD_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_intermod_relative_power(self, selector_string):
        r"""Gets the relative peak power measured around the upper intermod frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
        expressed in dBc. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
        relative power at the upper intermod frequency.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the relative peak power measured around the upper intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBc. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                relative power at the upper intermod frequency.

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
                attributes.AttributeID.IM_RESULTS_UPPER_INTERMOD_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_worst_case_intermod_relative_power(self, selector_string):
        r"""Gets the worst case intermod relative power that is equal to the maximum of the values of both the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_RELATIVE_POWER` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_RELATIVE_POWER` results. This value is expressed in dBc.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the worst case intermod relative power that is equal to the maximum of the values of both the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_INTERMOD_RELATIVE_POWER` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_INTERMOD_RELATIVE_POWER` results. This value is expressed in dBc.

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
                attributes.AttributeID.IM_RESULTS_WORST_CASE_INTERMOD_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_output_intercept_power(self, selector_string):
        r"""Gets the lower output intercept power. This value is expressed in dBm. Refer to the IM topic for more information
        about this result.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the lower output intercept power. This value is expressed in dBm. Refer to the IM topic for more information
                about this result.

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
                attributes.AttributeID.IM_RESULTS_LOWER_OUTPUT_INTERCEPT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_output_intercept_power(self, selector_string):
        r"""Gets the upper output intercept power. This value is expressed in dBm. Refer to the IM topic for more information
        about this result.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the upper output intercept power. This value is expressed in dBm. Refer to the IM topic for more information
                about this result.

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
                attributes.AttributeID.IM_RESULTS_UPPER_OUTPUT_INTERCEPT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_worst_case_output_intercept_power(self, selector_string):
        r"""Gets the worst case output intercept power which is equal to the minimum of the values of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OUTPUT_INTERCEPT_POWER` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OUTPUT_INTERCEPT_POWER` results. This value is expressed in dBm.

        Use "intermod<*n*>" as the selector string to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the worst case output intercept power which is equal to the minimum of the values of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OUTPUT_INTERCEPT_POWER` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OUTPUT_INTERCEPT_POWER` results. This value is expressed in dBm.

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
                attributes.AttributeID.IM_RESULTS_WORST_CASE_OUTPUT_INTERCEPT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_fundamental_measurement(self, selector_string, timeout):
        r"""Fetches the peak powers of the two fundamental tones.

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
            Tuple (lower_tone_power, upper_tone_power, error_code):

            lower_tone_power (float):
                This parameter returns the peak power measured around the lower tone frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FUNDAMENTAL_LOWER_TONE_POWER` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the lower tone frequency.

            upper_tone_power (float):
                This parameter returns the peak power measured around the upper tone frequency when you set the IM Local Peak Search
                Enabled attribute to **True**. This value is expressed in dBm. When you set the IM Local Peak Search Enabled attribute
                to **False**, the measurement returns the power at the upper tone frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            lower_tone_power, upper_tone_power, error_code = (
                self._interpreter.im_fetch_fundamental_measurement(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return lower_tone_power, upper_tone_power, error_code

    @_raise_if_disposed
    def fetch_intercept_power_array(self, selector_string, timeout):
        r"""Fetches the output intercept powers for the intermod.

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
            Tuple (intermod_order, worst_case_output_intercept_power, lower_output_intercept_power, upper_output_intercept_power, error_code):

            intermod_order (int):
                This parameter returns an array of the orders of the intermods.

            worst_case_output_intercept_power (float):
                This parameter returns an array of the worst case output intercept powers which are equal to the minimum of the values
                of the :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OUTPUT_INTERCEPT_POWER` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OUTPUT_INTERCEPT_POWER` results. This value is expressed in dBm.

            lower_output_intercept_power (float):
                This parameter returns an array of the lower output intercept power values. This value is expressed in dBm.

            upper_output_intercept_power (float):
                This parameter returns an array of the upper output intercept power values. This value is expressed in dBm.

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
                intermod_order,
                worst_case_output_intercept_power,
                lower_output_intercept_power,
                upper_output_intercept_power,
                error_code,
            ) = self._interpreter.im_fetch_intercept_power_array(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            intermod_order,
            worst_case_output_intercept_power,
            lower_output_intercept_power,
            upper_output_intercept_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_intercept_power(self, selector_string, timeout):
        r"""Fetches the output intercept powers for the intermod.

        Use "intermod<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and intermod number.

                Example:

                "intermod0"

                "result::r1/intermod0"

                You can use the :py:meth:`build_intermod_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (intermod_order, worst_case_output_intercept_power, lower_output_intercept_power, upper_output_intercept_power, error_code):

            intermod_order (int):
                This parameter returns the order of the intermod.

            worst_case_output_intercept_power (float):
                This parameter returns the worst case output intercept power which is equal to the minimum of the values of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.UPPER_OUTPUT_INTERCEPT_POWER` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOWER_OUTPUT_INTERCEPT_POWER` results. This value is expressed in dBm.

            lower_output_intercept_power (float):
                This parameter returns the lower output intercept power. This value is expressed in dBm.

            upper_output_intercept_power (float):
                This parameter returns the upper output intercept power. This value is expressed in dBm.

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
                intermod_order,
                worst_case_output_intercept_power,
                lower_output_intercept_power,
                upper_output_intercept_power,
                error_code,
            ) = self._interpreter.im_fetch_intercept_power(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            intermod_order,
            worst_case_output_intercept_power,
            lower_output_intercept_power,
            upper_output_intercept_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_intermod_measurement_array(self, selector_string, timeout):
        r"""Fetches an array of peak powers of the lower and upper intermods.

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
            Tuple (intermod_order, lower_intermod_absolute_power, upper_intermod_absolute_power, error_code):

            intermod_order (int):
                This parameter returns an array of the orders of the intermods.

            lower_intermod_absolute_power (float):
                This parameter returns an array of the peak power values measured around the lower intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the lower intermod frequency.

            upper_intermod_absolute_power (float):
                This parameter returns an array of the peak power values measured around the upper intermod frequency when you set the
                IM Local Peak Search Enabled attribute to **True**. This value is expressed in dBm. When you set the IM Local Peak
                Search Enabled attribute to **False**, the measurement returns the power at the upper intermod frequency.

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
                intermod_order,
                lower_intermod_absolute_power,
                upper_intermod_absolute_power,
                error_code,
            ) = self._interpreter.im_fetch_intermod_measurement_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            intermod_order,
            lower_intermod_absolute_power,
            upper_intermod_absolute_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_intermod_measurement(self, selector_string, timeout):
        r"""Fetches the peak powers of the lower and upper intermods.

        Use "intermod<
        *
        n
        *
        >" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and intermod number.

                Example:

                "intermod0"

                "result::r1/intermod0"

                You can use the :py:meth:`build_intermod_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (intermod_order, lower_intermod_absolute_power, upper_intermod_absolute_power, error_code):

            intermod_order (int):
                This parameter returns the order of the intermod.

            lower_intermod_absolute_power (float):
                This parameter returns the peak power measured around the lower intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the lower intermod frequency.

            upper_intermod_absolute_power (float):
                This parameter returns the peak power measured around the upper intermod frequency when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.LOCAL_PEAK_SEARCH_ENABLED` attribute to **True**. This value is
                expressed in dBm. When you set the IM Local Peak Search Enabled attribute to **False**, the measurement returns the
                power at the upper intermod frequency.

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
                intermod_order,
                lower_intermod_absolute_power,
                upper_intermod_absolute_power,
                error_code,
            ) = self._interpreter.im_fetch_intermod_measurement(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            intermod_order,
            lower_intermod_absolute_power,
            upper_intermod_absolute_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_spectrum(self, selector_string, timeout, spectrum_index, spectrum):
        r"""Fetches the array of spectrums used for the IM measurement. The
        **
        Spectrums
        **
        parameter contains one spectrum element when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        property to
        **
        Normal
        **
        .
        When you set the IM Meas Method attribute to
        **
        Dynamic Range
        **
        or
        **
        Segmented
        **
        , each tone and intermod has a separate spectrum element in the
        **
        Spectrums
        **
        parameter.

        This array is populated in the following order:

        - Lower tone spectrum

        - Upper tone spectrum

        - Lower intermod<
        *
        n
        *
        > spectrum

        - Upper intermod<
        *
        n
        *
        > spectrum

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

            spectrum_index (int):
                This parameter returns the data for the spectrum. This value is expressed in dBm.

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
            x0, dx, error_code = self._interpreter.im_fetch_spectrum(
                updated_selector_string, timeout, spectrum_index, spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code
