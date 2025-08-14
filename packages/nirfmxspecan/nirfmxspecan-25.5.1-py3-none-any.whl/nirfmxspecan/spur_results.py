"""Provides methods to fetch and read the Spur measurement results."""

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


class SpurResults(object):
    """Provides methods to fetch and read the Spur measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Spur measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_status(self, selector_string):
        r"""Indicates the overall measurement status.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                            |
        +==============+========================================================================================================+
        | Fail (0)     | A detected spur in the range is greater than the value of the Spur Results Spur Abs Limits attribute.  |
        +--------------+--------------------------------------------------------------------------------------------------------+
        | Pass (1)     | All detected spurs in the range are lower than the value of the Spur Results Spur Abs Limit attribute. |
        +--------------+--------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurMeasurementStatus):
                Indicates the overall measurement status.

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
                attributes.AttributeID.SPUR_RESULTS_MEASUREMENT_STATUS.value,
            )
            attr_val = enums.SpurMeasurementStatus(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_range_measurement_status(self, selector_string):
        r"""Indicates the measurement status for the frequency range.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        **Supported devices**: PXIe-5665/5668

        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                 |
        +==============+=============================================================================================================+
        | Fail (0)     | The amplitude of the detected spurs is greater than the value of the Spur Results Spur Abs Limit attribute. |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Pass (1)     | The amplitude of the detected spurs is lower than the value of the Spur Results Spur Abs Limit attribute.   |
        +--------------+-------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurRangeStatus):
                Indicates the measurement status for the frequency range.

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
                attributes.AttributeID.SPUR_RESULTS_RANGE_MEASUREMENT_STATUS.value,
            )
            attr_val = enums.SpurRangeStatus(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_range_spur_number_of_detected_spurs(self, selector_string):
        r"""Gets the number of detected spurious emissions (Spur) in the specified frequency range.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the number of detected spurious emissions (Spur) in the specified frequency range.

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
                attributes.AttributeID.SPUR_RESULTS_RANGE_NUMBER_OF_DETECTED_SPURS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_range_spur_frequency(self, selector_string):
        r"""Gets the frequency of the detected spurious emissions (Spur). This value is expressed in Hz.

        Use "range<*n*>/spur<*k*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency of the detected spurious emissions (Spur). This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RESULTS_RANGE_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_range_spur_margin(self, selector_string):
        r"""Gets the difference between the amplitude and the absolute limit of the detected spurious emissions (Spur) at the
        Spur frequency.

        Use "range<*n*>/spur<*k*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the difference between the amplitude and the absolute limit of the detected spurious emissions (Spur) at the
                Spur frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RESULTS_RANGE_MARGIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_range_spur_amplitude(self, selector_string):
        r"""Gets the amplitude of the detected spurious emissions (Spur). This value is expressed in dBm.

        Use "range<*n*>/spur<*k*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the amplitude of the detected spurious emissions (Spur). This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RESULTS_RANGE_AMPLITUDE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_range_spur_absolute_limit(self, selector_string):
        r"""Gets the threshold used to calculate the margin of the detected spurious emissions (Spur). This value is expressed
        in dBm. The measurement calculates the threshold using the absolute limit line specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute.

        Use "range<*n*>/spur<*k*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the threshold used to calculate the margin of the detected spurious emissions (Spur). This value is expressed
                in dBm. The measurement calculates the threshold using the absolute limit line specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute.

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
                attributes.AttributeID.SPUR_RESULTS_RANGE_ABSOLUTE_LIMIT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_all_spurs(self, selector_string, timeout):
        r"""Fetches all the spurs across all ranges.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (spur_frequency, spur_amplitude, spur_margin, spur_absolute_limit, spur_range_index, error_code):

            spur_frequency (float):
                This parameter returns the array of frequencies, in Hz, of all detected spurs across all ranges.

            spur_amplitude (float):
                This parameter returns the array of powers, in dBm, of all detected spurs across all ranges.

            spur_margin (float):
                This parameter returns the array of the differences between the spur amplitude and the absolute limit at the spur
                frequency.

            spur_absolute_limit (float):
                This parameter  returns the array of thresholds, in dBm, used to calculate the margin of the detected spur.

            spur_range_index (int):
                This parameter returns the array containing range indices corresponding to the detected spurs.

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
                spur_frequency,
                spur_amplitude,
                spur_margin,
                spur_absolute_limit,
                spur_range_index,
                error_code,
            ) = self._interpreter.spur_fetch_all_spurs(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            spur_frequency,
            spur_amplitude,
            spur_margin,
            spur_absolute_limit,
            spur_range_index,
            error_code,
        )

    @_raise_if_disposed
    def fetch_measurement_status(self, selector_string, timeout):
        r"""Indicates the overall Spur measurement status.

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
            Tuple (measurement_status, error_code):

            measurement_status (enums.SpurMeasurementStatus):
                This parameter indicates the overall measurement status.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Fail (0)     | Indicates that the amplitude of the detected spurs is greater than the value of the Spur Results Spur Abs Limit          |
                |              | attribute.                                                                                                               |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Pass (1)     | Indicates that the amplitude of the detected spurs is lower than the value of the Spur Results Spur Abs Limit            |
                |              | attribute.                                                                                                               |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            measurement_status, error_code = self._interpreter.spur_fetch_measurement_status(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return measurement_status, error_code

    @_raise_if_disposed
    def fetch_range_absolute_limit_trace(self, selector_string, timeout, absolute_limit):
        r"""Fetches the absolute limit line used in the range.
        Use "range<n>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and range number.

                Example:

                "range0"

                "result::r1/range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            absolute_limit (numpy.float32):
                This parameter returns the absolute limit, in dBm, at each frequency bin in the range.

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
            x0, dx, error_code = self._interpreter.spur_fetch_range_absolute_limit_trace(
                updated_selector_string, timeout, absolute_limit
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_range_spectrum_trace(self, selector_string, timeout, range_spectrum):
        r"""Fetches the measured range spectrum trace. You can fetch traces only for the range index specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRACE_RANGE_INDEX`
        property.

        Use "range<n>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and range number.

                Example:

                "range0"

                "result::r1/range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            range_spectrum (numpy.float32):
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
            x0, dx, error_code = self._interpreter.spur_fetch_range_spectrum_trace(
                updated_selector_string, timeout, range_spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_range_status_array(self, selector_string, timeout):
        r"""Fetches the range status for Spur measurements.

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
            Tuple (range_status, number_of_detected_spurs, error_code):

            range_status (enums.SpurRangeStatus):
                This parameter indicates the array of measurement statuses for each frequency range.

            number_of_detected_spurs (int):
                This parameter returns the array of number of detected spurious emissions (Spur) in each frequency range.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            range_status, number_of_detected_spurs, error_code = (
                self._interpreter.spur_fetch_range_status_array(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return range_status, number_of_detected_spurs, error_code

    @_raise_if_disposed
    def fetch_range_status(self, selector_string, timeout):
        r"""Fetches the range status for Spur measurements.

        Use "range<n>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and range number.

                Example:

                "range0"

                "result::r1/range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (range_status, detected_spurs, error_code):

            range_status (enums.SpurRangeStatus):
                This parameter indicates the measurement status for the frequency range.

            detected_spurs (int):
                This parameter returns the number of detected spurious emissions (Spur) in the specified frequency range.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            range_status, detected_spurs, error_code = self._interpreter.spur_fetch_range_status(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return range_status, detected_spurs, error_code

    @_raise_if_disposed
    def fetch_spur_measurement_array(self, selector_string, timeout):
        r"""Fetches the information of Spurs in the range.
        Use "range<n>" as the active channel string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and range number.

                Example:

                "range0"

                "result::r1/range0"

                You can use the :py:meth:`build_range_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (spur_frequency, spur_amplitude, spur_absolute_limit, spur_margin, error_code):

            spur_frequency (float):
                This parameter returns the array of frequencies, in Hz, of the detected spurs.

            spur_amplitude (float):
                This parameter returns the array of powers, in dBm, of the detected spurs.

            spur_absolute_limit (float):
                This parameter  returns the array of thresholds, in dBm, used to calculate the margin of the detected spurs.

            spur_margin (float):
                This parameter returns the array of differences between the spur amplitude and the absolute limit at the spur
                frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            spur_frequency, spur_amplitude, spur_absolute_limit, spur_margin, error_code = (
                self._interpreter.spur_fetch_spur_measurement_array(
                    updated_selector_string, timeout
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return spur_frequency, spur_amplitude, spur_absolute_limit, spur_margin, error_code

    @_raise_if_disposed
    def fetch_spur_measurement(self, selector_string, timeout):
        r"""Fetches the information of Spurs in the range.
        Use "range<n>/spur<k>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, range number, and spur number.

                Example:

                "range0/spur0"

                "result::r1/range0/spur0"

                You can use the :py:meth:`build_spur_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (spur_frequency, spur_amplitude, spur_margin, spur_absolute_limit, error_code):

            spur_frequency (float):
                This parameter returns the frequency, in Hz, of the detected spur.

            spur_amplitude (float):
                This parameter returns the power, in dBm, of the detected spur.

            spur_margin (float):
                This parameter returns the difference between the spur amplitude and the absolute limit at the spur frequency.

            spur_absolute_limit (float):
                This parameter  returns the threshold, in dBm, used to calculate the margin of the detected spur.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            spur_frequency, spur_amplitude, spur_margin, spur_absolute_limit, error_code = (
                self._interpreter.spur_fetch_spur_measurement(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return spur_frequency, spur_amplitude, spur_margin, spur_absolute_limit, error_code
