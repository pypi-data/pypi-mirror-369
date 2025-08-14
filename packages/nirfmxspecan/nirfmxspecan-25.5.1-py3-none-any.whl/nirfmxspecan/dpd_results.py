"""Provides methods to fetch and read the Dpd measurement results."""

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


class DpdResults(object):
    """Provides methods to fetch and read the Dpd measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Dpd measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_average_gain(self, selector_string):
        r"""Gets the average gain of the device under test. This value is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the average gain of the device under test. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_RESULTS_AVERAGE_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_nmse(self, selector_string):
        r"""Gets the normalized mean-squared DPD modeling error when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute to **True**. This value is expressed in dB. NaN
        is returned when the :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute is set to **False**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the normalized mean-squared DPD modeling error when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute to **True**. This value is expressed in dB. NaN
                is returned when the :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute is set to **False**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_RESULTS_NMSE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_average_gain(self, selector_string, timeout):
        r"""Fetches the average gain, in dB, of the device under test (DUT) for the DPD measurement.

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
            Tuple (average_gain, error_code):

            average_gain (float):
                This parameter returns the average gain, in dB, of the DUT.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            average_gain, error_code = self._interpreter.dpd_fetch_average_gain(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return average_gain, error_code

    @_raise_if_disposed
    def fetch_dpd_polynomial(self, selector_string, timeout, dpd_polynomial):
        r"""Fetches the memory polynomial or generalized memory polynomial coefficients when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
        Polynomial**.

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

            dpd_polynomial (numpy.complex64):
                This parameter returns the memory polynomial or generalized memory polynomial coefficients when you set the DPD Model
                attribute to **Memory Polynomial** or **Generalized Memory Polynomial**.

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
            error_code = self._interpreter.dpd_fetch_dpd_polynomial(
                updated_selector_string, timeout, dpd_polynomial
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def fetch_dvr_model(self, selector_string, timeout, dvr_model):
        r"""Fetches the decomposed vector rotation model coefficients when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Decomposed Vector Rotation**.

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

            dvr_model (numpy.complex64):
                This parameter returns the decomposed vector rotation model coefficients when you set the DPD Model attribute to
                **Decomposed Vector Rotation**.

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
            error_code = self._interpreter.dpd_fetch_dvr_model(
                updated_selector_string, timeout, dvr_model
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def fetch_lookup_table(self, selector_string, timeout, complex_gains):
        r"""Fetches the predistortion lookup table when
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        property to
        **
        Lookup Table
        **
        .

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

            complex_gains (numpy.complex64):
                This parameter returns the lookup table complex gain values, in dB, for magnitude and phase predistortion.

        Returns:
            Tuple (input_powers, error_code):

            input_powers (float):
                This parameter returns the lookup table power levels, in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            input_powers, error_code = self._interpreter.dpd_fetch_lookup_table(
                updated_selector_string, timeout, complex_gains
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return input_powers, error_code

    @_raise_if_disposed
    def fetch_nmse(self, selector_string, timeout):
        r"""Fetches the normalized mean-squared DPD modeling error.

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
            Tuple (nmse, error_code):

            nmse (float):
                This parameter returns the normalized mean-squared DPD modeling error when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NMSE_ENABLED` attribute to **True**. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            nmse, error_code = self._interpreter.dpd_fetch_nmse(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return nmse, error_code

    @_raise_if_disposed
    def fetch_processed_mean_acquired_waveform(
        self, selector_string, timeout, processed_mean_acquired_waveform
    ):
        r"""Fetches the averaged acquired waveform, corrected for frequency, phase and DC offsets, used to perform the DPD
        measurement.

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

            processed_mean_acquired_waveform (numpy.complex64):
                This parameter returns the complex baseband samples, in volts.

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
            x0, dx, error_code = self._interpreter.dpd_fetch_processed_mean_acquired_waveform(
                updated_selector_string, timeout, processed_mean_acquired_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_processed_reference_waveform(
        self, selector_string, timeout, processed_reference_waveform
    ):
        r"""Fetches the segment of the reference waveform used to perform the DPD measurement.

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

            processed_reference_waveform (numpy.complex64):
                This parameter returns the complex baseband samples, in volts.

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
            x0, dx, error_code = self._interpreter.dpd_fetch_processed_reference_waveform(
                updated_selector_string, timeout, processed_reference_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code
