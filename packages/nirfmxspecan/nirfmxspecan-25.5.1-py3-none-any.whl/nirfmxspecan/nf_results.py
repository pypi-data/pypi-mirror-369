"""Provides methods to fetch and read the NF measurement results."""

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


class NFResults(object):
    """Provides methods to fetch and read the NF measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the NF measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_dut_noise_figure(self, selector_string):
        r"""Gets an array of the noise figures of the DUT measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns an array of the noise figures of the DUT measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_RESULTS_DUT_NOISE_FIGURE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_dut_noise_temperature(self, selector_string):
        r"""Gets an array of the equivalent thermal noise temperatures of the DUT measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns an array of the equivalent thermal noise temperatures of the DUT measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in kelvin.

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
                attributes.AttributeID.NF_RESULTS_DUT_NOISE_TEMPERATURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_dut_gain(self, selector_string):
        r"""Gets an array of the available gains of the DUT measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns an array of the available gains of the DUT measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_RESULTS_DUT_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_analyzer_noise_figure(self, selector_string):
        r"""Gets an array of the noise figures of the analyzer measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns an array of the noise figures of the analyzer measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

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
                attributes.AttributeID.NF_RESULTS_ANALYZER_NOISE_FIGURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_measurement_y_factor(self, selector_string):
        r"""Gets an array of the measurement Y-Factors measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. A valid result
        is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to
        **Y-Factor**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns an array of the measurement Y-Factors measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. A valid result
                is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to
                **Y-Factor**.

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
                attributes.AttributeID.NF_RESULTS_MEASUREMENT_Y_FACTOR.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_calibration_y_factor(self, selector_string):
        r"""Gets an array of the calibration Y-Factors measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. A valid result
        is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to
        **Y-Factor**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns an array of the calibration Y-Factors measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. A valid result
                is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to
                **Y-Factor**.

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
                attributes.AttributeID.NF_RESULTS_CALIBRATION_Y_FACTOR.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_y_factor_hot_power(self, selector_string):
        r"""Gets the array of powers measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is enabled. This value
        is expressed in dBm. A valid result is returned only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the array of powers measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is enabled. This value
                is expressed in dBm. A valid result is returned only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_RESULTS_Y_FACTOR_HOT_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_y_factor_cold_power(self, selector_string):
        r"""Gets the array of powers measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is disabled. This value
        is expressed in dBm. A valid result is returned only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the array of powers measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is disabled. This value
                is expressed in dBm. A valid result is returned only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_RESULTS_Y_FACTOR_COLD_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_cold_source_power(self, selector_string):
        r"""Gets the power measured at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dBm. A valid
        result is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute
        to **Cold-source**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dBm. A valid
                result is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute
                to **Cold-source**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_RESULTS_COLD_SOURCE_POWER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_analyzer_noise_figure(self, selector_string, timeout):
        r"""Fetches the noise figure of the analyzer.

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
            Tuple (analyzer_noise_figure, error_code):

            analyzer_noise_figure (float):
                This parameter  returns an array of the noise figure values of the analyzer measured at the frequencies specified by
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            analyzer_noise_figure, error_code = self._interpreter.nf_fetch_analyzer_noise_figure(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return analyzer_noise_figure, error_code

    @_raise_if_disposed
    def fetch_cold_source_power(self, selector_string, timeout):
        r"""Fetches the power measured by the analyzer when the cold source based noise figure (NF) measurement is performed.

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
            Tuple (cold_source_power, error_code):

            cold_source_power (float):
                This parameter  returns the array of powers measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dBm. A valid
                result is returned only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute
                to **Cold Source**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            cold_source_power, error_code = self._interpreter.nf_fetch_cold_source_power(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return cold_source_power, error_code

    @_raise_if_disposed
    def fetch_dut_noise_figure_and_gain(self, selector_string, timeout):
        r"""Fetches the DUT noise figure, noise temperature and gain results.

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
            Tuple (dut_noise_figure, dut_noise_temperature, dut_gain, error_code):

            dut_noise_figure (float):
                This parameter  returns an array of the noise figures of the DUT measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

            dut_noise_temperature (float):
                This parameter returns an array of the equivalent thermal noise temperatures of the DUT measured at the frequencies
                specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in
                kelvin.

            dut_gain (float):
                This parameter returns an array of the available gains of the DUT measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            dut_noise_figure, dut_noise_temperature, dut_gain, error_code = (
                self._interpreter.nf_fetch_dut_noise_figure_and_gain(
                    updated_selector_string, timeout
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return dut_noise_figure, dut_noise_temperature, dut_gain, error_code

    @_raise_if_disposed
    def fetch_y_factor_powers(self, selector_string, timeout):
        r"""Fetches the hot and cold powers measured when the Y-Factor based noise figure (NF) measurement is performed.

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
            Tuple (hot_power, cold_power, error_code):

            hot_power (float):
                This parameter returns an array of powers measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is enabled. This value
                is expressed in dBm. A valid result is returned only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            cold_power (float):
                This parameter returns an array of powers measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute, when the noise source is disabled. This value
                is expressed in dBm. A valid result is returned only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            hot_power, cold_power, error_code = self._interpreter.nf_fetch_y_factor_powers(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return hot_power, cold_power, error_code

    @_raise_if_disposed
    def fetch_y_factors(self, selector_string, timeout):
        r"""Returns the measurement Y-factor and calibration Y-factor values.

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
            Tuple (measurement_y_factor, calibration_y_factor, error_code):

            measurement_y_factor (float):
                This parameter returns the array of measurement Y-Factor values measured at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in dB. This method
                returns a valid result only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Y-Factor**.

            calibration_y_factor (float):
                This parameter returns the array of calibration Y-Factor values measured at the frequencies specified by the NF Freq
                List attribute. This value is expressed in dB. This method returns a valid result only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            measurement_y_factor, calibration_y_factor, error_code = (
                self._interpreter.nf_fetch_y_factors(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return measurement_y_factor, calibration_y_factor, error_code
