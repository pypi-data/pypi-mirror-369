"""Provides methods to fetch and read the Harm measurement results."""

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


class HarmResults(object):
    """Provides methods to fetch and read the Harm measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Harm measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_total_harmonic_distortion(self, selector_string):
        r"""Gets the total harmonics distortion (THD), measured as a percentage of the power in the fundamental signal.

        THD (%) = SQRT (Total power of all enabled harmonics - Power in fundamental) * 100 / Power in fundamental

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the total harmonics distortion (THD), measured as a percentage of the power in the fundamental signal.

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
                attributes.AttributeID.HARM_RESULTS_TOTAL_HARMONIC_DISTORTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_average_fundamental_power(self, selector_string):
        r"""Gets the average power measured at the fundamental frequency. This value is expressed in dBm.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the average power measured at the fundamental frequency. This value is expressed in dBm.

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
                attributes.AttributeID.HARM_RESULTS_AVERAGE_FUNDAMENTAL_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_fundamental_frequency(self, selector_string):
        r"""Gets the frequency used as the fundamental frequency. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency used as the fundamental frequency. This value is expressed in Hz.

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
                attributes.AttributeID.HARM_RESULTS_FUNDAMENTAL_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_harmonic_average_absolute_power(self, selector_string):
        r"""Gets the average absolute power measured at the harmonic specified by the selector string. This value is expressed
        in dBm.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the average absolute power measured at the harmonic specified by the selector string. This value is expressed
                in dBm.

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
                attributes.AttributeID.HARM_RESULTS_HARMONIC_AVERAGE_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_harmonic_average_relative_power(self, selector_string):
        r"""Gets the average power relative to the fundamental power measured at the harmonic specified by the selector string.
        This value is expressed in dB.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the average power relative to the fundamental power measured at the harmonic specified by the selector string.
                This value is expressed in dB.

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
                attributes.AttributeID.HARM_RESULTS_HARMONIC_AVERAGE_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_harmonic_frequency(self, selector_string):
        r"""Gets the RF frequency of the harmonic. This value is expressed in Hz.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the RF frequency of the harmonic. This value is expressed in Hz.

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
                attributes.AttributeID.HARM_RESULTS_HARMONIC_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_harmonic_rbw(self, selector_string):
        r"""Gets the resolution bandwidth (RBW) which is used by the harmonic measurement, for the harmonic specified by the
        selector string. This value is expressed in Hz.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the resolution bandwidth (RBW) which is used by the harmonic measurement, for the harmonic specified by the
                selector string. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.HARM_RESULTS_HARMONIC_RBW.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_harmonic_measurement(self, selector_string, timeout):
        r"""Returns the power measured at the harmonic frequency.
        Use "harmonic<*n*>" as the selector channel string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and harmonic number.

                Example:

                "harmonic0"

                "result::r1/harmonic0"

                You can use the :py:meth:`build_harmonic_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (average_relative_power, average_absolute_power, rbw, frequency, error_code):

            average_relative_power (float):
                This parameter returns the average power, in dB, relative to the fundamental power measured at the harmonic.

            average_absolute_power (float):
                This parameter returns the average absolute power, in dBm, measured at the harmonic.

            rbw (float):
                This parameter returns the resolution bandwidth (RBW), in Hz, which is used by the harmonic measurement, for the
                harmonic.

            frequency (float):
                This parameter returns the RF frequency, in Hz, of the harmonic.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_relative_power, average_absolute_power, rbw, frequency, error_code = (
                self._interpreter.harm_fetch_harmonic_measurement(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_relative_power, average_absolute_power, rbw, frequency, error_code

    @_raise_if_disposed
    def fetch_harmonic_power_trace(self, selector_string, timeout, power):
        r"""Fetches the power trace for the harmonics measurement.
        Use "harmonic<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and harmonic number.

                Example:

                "harmonic0"

                "result::r1/harmonic0"

                You can use the :py:meth:`build_harmonic_string` method  to build the selector string.

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
            x0, dx, error_code = self._interpreter.harm_fetch_harmonic_power_trace(
                updated_selector_string, timeout, power
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_harmonic_measurement_array(self, selector_string, timeout):
        r"""Returns the array of powers measured at the harmonic frequency.

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
            Tuple (average_relative_power, average_absolute_power, rbw, frequency, error_code):

            average_relative_power (float):
                This parameter returns the array of average powers, in dB, relative to the fundamental power measured at each harmonic.

            average_absolute_power (float):
                This parameter returns the array of average absolute powers, in dBm, measured at each harmonic.

            rbw (float):
                This parameter returns the array of resolution bandwidths (RBW), in Hz, which is used by the harmonic measurement, for
                each harmonic.

            frequency (float):
                This parameter returns the array of frequencies, in Hz, of each harmonic.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_relative_power, average_absolute_power, rbw, frequency, error_code = (
                self._interpreter.harm_fetch_harmonic_measurement_array(
                    updated_selector_string, timeout
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_relative_power, average_absolute_power, rbw, frequency, error_code

    @_raise_if_disposed
    def fetch_total_harmonic_distortion(self, selector_string, timeout):
        r"""Returns the total harmonics distortion (THD), measured as a percentage of the power in the fundamental signal.

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
            Tuple (total_harmonic_distortion, average_fundamental_power, fundamental_frequency, error_code):

            total_harmonic_distortion (float):
                This parameter returns the total harmonics distortion (THD), measured as a percentage of the power in the fundamental
                signal. THD calculation involves only the harmonics that are enabled.

                THD (%) = SQRT (Total power of all enabled harmonics - Power in fundamental) * 100 / Power in fundamental.

            average_fundamental_power (float):
                This parameter returns the average power, in dBm, measured at the fundamental frequency.

            fundamental_frequency (float):
                This parameter returns the frequency, in Hz, used as the fundamental frequency.

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
                total_harmonic_distortion,
                average_fundamental_power,
                fundamental_frequency,
                error_code,
            ) = self._interpreter.harm_fetch_total_harmonic_distortion(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            total_harmonic_distortion,
            average_fundamental_power,
            fundamental_frequency,
            error_code,
        )

    @_raise_if_disposed
    def read(self, selector_string, timeout):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns Harmonics measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

        Returns:
            Tuple (total_harmonic_distortion, average_fundamental_power, error_code):

            total_harmonic_distortion (float):
                This parameter returns the total harmonics distortion (THD), measured as a percentage of the power in the fundamental
                signal. THD calculation involves only the harmonics that are enabled.

                THD (%) = SQRT (Total power of all enabled harmonics - Power in fundamental) * 100 / Power in fundamental.

            average_fundamental_power (float):
                This parameter returns the average power, in dBm, measured at the fundamental frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            total_harmonic_distortion, average_fundamental_power, error_code = (
                self._interpreter.harm_read(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return total_harmonic_distortion, average_fundamental_power, error_code
