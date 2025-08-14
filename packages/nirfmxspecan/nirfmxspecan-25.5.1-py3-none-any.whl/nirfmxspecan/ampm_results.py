"""Provides methods to fetch and read the Ampm measurement results."""

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


class AmpmResults(object):
    """Provides methods to fetch and read the Ampm measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Ampm measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_mean_linear_gain(self, selector_string):
        r"""Gets the average linear gain of the device under test, computed by rejecting signal samples containing gain
        compression. This value is expressed in dB.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the average linear gain of the device under test, computed by rejecting signal samples containing gain
                compression. This value is expressed in dB.
            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_RESULTS_MEAN_LINEAR_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_1_db_compression_point(self, selector_string):
        r"""Gets the theoretical output power at which the gain of the device under test drops by 1 dB from a gain reference
        computed based on the value that you specify for the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute. This value is expressed in
        dBm. This attribute returns NaN when the AM-to-AM characteristics of the device under test are flat.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the theoretical output power at which the gain of the device under test drops by 1 dB from a gain reference
                computed based on the value that you specify for the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute. This value is expressed in
                dBm. This attribute returns NaN when the AM-to-AM characteristics of the device under test are flat.

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
                attributes.AttributeID.AMPM_RESULTS_1_DB_COMPRESSION_POINT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_input_compression_point(self, selector_string):
        r"""Gets the theoretical input power at which the gain of the device drops by a compression level, specified through the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute, from a gain reference computed based
        on the value that you specify for the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE`
        attribute. This value is expressed in dBm.

        You do not need to use a selector string to read this attribute for the default signal and result instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the theoretical input power at which the gain of the device drops by a compression level, specified through the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute, from a gain reference computed based
                on the value that you specify for the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE`
                attribute. This value is expressed in dBm.

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
                attributes.AttributeID.AMPM_RESULTS_INPUT_COMPRESSION_POINT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_output_compression_point(self, selector_string):
        r"""Gets the theoretical output power at which the gain of the device drops by a compression level, specified through
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute, from a gain reference computed
        based on the value that you specify for the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute. This value is expressed in
        dBm.

        You do not need to use a selector string to read this attribute for the default signal and result instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the theoretical output power at which the gain of the device drops by a compression level, specified through
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` attribute, from a gain reference computed
                based on the value that you specify for the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_GAIN_REFERENCE` attribute. This value is expressed in
                dBm.

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
                attributes.AttributeID.AMPM_RESULTS_OUTPUT_COMPRESSION_POINT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_compression_point_gain_reference(self, selector_string):
        r"""Gets the gain reference used for compression point calculation. This value is expressed in dB.

        You do not need to use a selector string to read this attribute for the default signal and result instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the gain reference used for compression point calculation. This value is expressed in dB.

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
                attributes.AttributeID.AMPM_RESULTS_COMPRESSION_POINT_GAIN_REFERENCE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_peak_reference_power(self, selector_string):
        r"""Gets the peak reference power. This value is expressed in dBm.

        You do not need to use a selector string to read this attribute for the default signal and result instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak reference power. This value is expressed in dBm.

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
                attributes.AttributeID.AMPM_RESULTS_PEAK_REFERENCE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_peak_reference_power_gain(self, selector_string):
        r"""Gets the gain at the peak reference power. This value is expressed in dB.

        You do not need to use a selector string to read this attribute for the default signal and result instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the gain at the peak reference power. This value is expressed in dB.

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
                attributes.AttributeID.AMPM_RESULTS_PEAK_REFERENCE_POWER_GAIN.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_rms_evm(self, selector_string):
        r"""Gets the ratio, as a percentage, of l\ :sup:`2`\ norm of difference between the normalized reference and acquired
        waveforms, to the l\ :sup:`2`\ norm of the normalized reference waveform.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the ratio, as a percentage, of l\ :sup:`2`\ norm of difference between the normalized reference and acquired
                waveforms, to the l\ :sup:`2`\ norm of the normalized reference waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_RESULTS_MEAN_RMS_EVM.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_gain_error_range(self, selector_string):
        r"""Gets the peak-to-peak deviation of the device under test gain. This value is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak-to-peak deviation of the device under test gain. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_RESULTS_GAIN_ERROR_RANGE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_phase_error_range(self, selector_string):
        r"""Gets the peak-to-peak deviation of the phase distortion of the acquired signal relative to the reference waveform
        caused by the device under test. This value is expressed in degrees.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak-to-peak deviation of the phase distortion of the acquired signal relative to the reference waveform
                caused by the device under test. This value is expressed in degrees.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_RESULTS_PHASE_ERROR_RANGE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_phase_error(self, selector_string):
        r"""Gets the mean phase error of the acquired signal relative to the reference waveform caused by the device under test.
        This value is expressed in degrees.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean phase error of the acquired signal relative to the reference waveform caused by the device under test.
                This value is expressed in degrees.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.AMPM_RESULTS_MEAN_PHASE_ERROR.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_am_to_am_curve_fit_residual(self, selector_string):
        r"""Gets the approximation error of the polynomial approximation of the measured device under test AM-to-AM
        characteristic. This value is expressed in dB.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the approximation error of the polynomial approximation of the measured device under test AM-to-AM
                characteristic. This value is expressed in dB.

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
                attributes.AttributeID.AMPM_RESULTS_AM_TO_AM_CURVE_FIT_RESIDUAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_am_to_pm_curve_fit_residual(self, selector_string):
        r"""Gets the approximation error of the polynomial approximation of the measured AM-to-PM characteristic of the device
        under test. This value is expressed in degrees.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the approximation error of the polynomial approximation of the measured AM-to-PM characteristic of the device
                under test. This value is expressed in degrees.

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
                attributes.AttributeID.AMPM_RESULTS_AM_TO_PM_CURVE_FIT_RESIDUAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_am_to_am_curve_fit_coefficients(self, selector_string):
        r"""Gets the coefficients of the polynomial that approximates the measured AM-to-AM characteristic of the device under
        test.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the coefficients of the polynomial that approximates the measured AM-to-AM characteristic of the device under
                test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f32_array(
                updated_selector_string,
                attributes.AttributeID.AMPM_RESULTS_AM_TO_AM_CURVE_FIT_COEFFICIENTS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_am_to_pm_curve_fit_coefficients(self, selector_string):
        r"""Gets the coefficients of the polynomial that approximates the measured AM-to-PM characteristic of the device under
        test.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the coefficients of the polynomial that approximates the measured AM-to-PM characteristic of the device under
                test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f32_array(
                updated_selector_string,
                attributes.AttributeID.AMPM_RESULTS_AM_TO_PM_CURVE_FIT_COEFFICIENTS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_am_to_am_trace(self, selector_string, timeout):
        r"""Fetches the AM to AM trace, where the **Reference Powers** array forms the x-axis of the trace; and the **Measured AM
        to AM** and **Curve Fit AM to AM** arrays form the y-axis of the trace.

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
            Tuple (reference_powers, measured_am_to_am, curve_fit_am_to_am, error_code):

            reference_powers (float):
                This parameter returns the array of reference powers.  This value is expressed in dBm.

                Reference Powers are the instantaneous powers at the input port of the DUT when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute to **Input**, and Reference Powers are
                the instantaneous powers at the output port of the DUT when you set the AMPM Ref Pwr Type attribute to **Output**.

            measured_am_to_am (float):
                This parameter returns the gain values corresponding to the reference powers. This value is expressed in dB.

            curve_fit_am_to_am (float):
                This parameter returns the polynomial fit gain values corresponding to the reference powers. This value is expressed in
                dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            reference_powers, measured_am_to_am, curve_fit_am_to_am, error_code = (
                self._interpreter.ampm_fetch_am_to_am_trace(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return reference_powers, measured_am_to_am, curve_fit_am_to_am, error_code

    @_raise_if_disposed
    def fetch_am_to_pm_trace(self, selector_string, timeout):
        r"""Fetches the AM to PM trace, where the **Reference Powers** array forms the x-axis of the trace; and the **Measured AM
        to PM** and **Curve Fit AM to PM** arrays form the y-axis of the trace.

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
            Tuple (reference_powers, measured_am_to_pm, curve_fit_am_to_pm, error_code):

            reference_powers (float):
                This parameter returns the array of reference powers.  This value is expressed in dBm.

                Reference Powers are the instantaneous powers at the input port of the DUT when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_POWER_TYPE` attribute to **Input**, and Reference Powers are
                the instantaneous powers at the output port of the DUT when you set the AMPM Ref Pwr Type attribute to **Output**.

            measured_am_to_pm (float):
                This parameter returns the polynomial fit phase distortion values corresponding to the reference powers. This value is
                expressed in degrees.

            curve_fit_am_to_pm (float):
                This parameter returns the phase distortion values corresponding to the reference powers. This value is expressed in
                degrees.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            reference_powers, measured_am_to_pm, curve_fit_am_to_pm, error_code = (
                self._interpreter.ampm_fetch_am_to_pm_trace(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return reference_powers, measured_am_to_pm, curve_fit_am_to_pm, error_code

    @_raise_if_disposed
    def fetch_compression_points(self, selector_string, timeout):
        r"""Fetches the compression points.

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
            Tuple (input_compression_point, output_compression_point, error_code):

            input_compression_point (float):
                This parameter returns the theoretical input power at which the device gain drops by the compression level, specified
                by the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` parameter, from its mean linear gain.
                This value is expressed in dBm.

            output_compression_point (float):
                This parameter returns the theoretical output power at which device gain drops by the compression level, specified by
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.COMPRESSION_POINT_LEVEL` parameter, from its mean linear gain. This
                value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            input_compression_point, output_compression_point, error_code = (
                self._interpreter.ampm_fetch_compression_points(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return input_compression_point, output_compression_point, error_code

    @_raise_if_disposed
    def fetch_curve_fit_coefficients(self, selector_string, timeout):
        r"""Fetches the coefficients of the polynomials that approximate the AM-to-AM and AM-to-PM responses of the device under
        test.

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
            Tuple (am_to_am_coefficients, am_to_pm_coefficients, error_code):

            am_to_am_coefficients (float):
                This parameter returns the coefficients of the polynomial that approximates the AM-to-AM characteristic of the device
                under test.

            am_to_pm_coefficients (float):
                This parameter returns the coefficients of the polynomial that approximates the AM-to-PM characteristic of the device
                under test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            am_to_am_coefficients, am_to_pm_coefficients, error_code = (
                self._interpreter.ampm_fetch_curve_fit_coefficients(
                    updated_selector_string, timeout
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return am_to_am_coefficients, am_to_pm_coefficients, error_code

    @_raise_if_disposed
    def fetch_curve_fit_residual(self, selector_string, timeout):
        r"""Fetches the polynomial approximation residuals for AM-to-AM and AM-to-PM response of the device under test.

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
            Tuple (am_to_am_residual, am_to_pm_residual, error_code):

            am_to_am_residual (float):
                This parameter returns the approximation error, in dB, in the polynomial approximation of the AM-to-AM characteristic
                of the device under test.

            am_to_pm_residual (float):
                This parameter returns the approximation error, in degrees, in the polynomial approximation of the AM-to-PM
                characteristic of the device under test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            am_to_am_residual, am_to_pm_residual, error_code = (
                self._interpreter.ampm_fetch_curve_fit_residual(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return am_to_am_residual, am_to_pm_residual, error_code

    @_raise_if_disposed
    def fetch_dut_characteristics(self, selector_string, timeout):
        r"""Fetches the mean linear gain, 1 dB compression point, and mean RMS EVM of the DUT.

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
            Tuple (mean_linear_gain, one_db_compression_point, mean_rms_evm, error_code):

            mean_linear_gain (float):
                This parameter returns the average linear gain, in dB, of the device under test, computed by rejecting signal samples
                suffering gain compression.

            one_db_compression_point (float):
                This parameter returns the theoretical output power, in dBm, at which gain of the device under test drops by 1 dB from
                its mean linear gain. This parameter returns NaN when the AM-to-AM characteristics of the device under test are flat.

            mean_rms_evm (float):
                This parameter returns the ratio, as a percentage, of l\ :sup:`2`\ norm of difference between the normalized reference
                and acquired waveforms, to the l\ :sup:`2`\ norm of the normalized reference waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            mean_linear_gain, one_db_compression_point, mean_rms_evm, error_code = (
                self._interpreter.ampm_fetch_dut_characteristics(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return mean_linear_gain, one_db_compression_point, mean_rms_evm, error_code

    @_raise_if_disposed
    def fetch_error(self, selector_string, timeout):
        r"""Fetches the maximum gain error range, phase error range, and mean phase error for the DUT.

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
            Tuple (gain_error_range, phase_error_range, mean_phase_error, error_code):

            gain_error_range (float):
                This parameter returns the peak-to-peak deviation, in dB, in the gain of the device under test.

            phase_error_range (float):
                This parameter returns the peak-to-peak deviation, in degrees, in the phase distortion of the acquired signal relative
                to the reference waveform caused by the device under test.

            mean_phase_error (float):
                This parameter returns the mean phase error, in degrees, of the acquired signal relative to the reference waveform
                caused by the device under test.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            gain_error_range, phase_error_range, mean_phase_error, error_code = (
                self._interpreter.ampm_fetch_error(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return gain_error_range, phase_error_range, mean_phase_error, error_code

    @_raise_if_disposed
    def fetch_processed_mean_acquired_waveform(
        self, selector_string, timeout, processed_mean_acquired_waveform
    ):
        r"""Fetches the averaged acquired waveform, corrected for frequency, phase and DC offsets, used to perform the AMPM
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
            x0, dx, error_code = self._interpreter.ampm_fetch_processed_mean_acquired_waveform(
                updated_selector_string, timeout, processed_mean_acquired_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_processed_reference_waveform(
        self, selector_string, timeout, processed_reference_waveform
    ):
        r"""Fetches the segment of the reference waveform used to perform the AMPM measurement.

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
            x0, dx, error_code = self._interpreter.ampm_fetch_processed_reference_waveform(
                updated_selector_string, timeout, processed_reference_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_relative_phase_trace(self, selector_string, timeout, relative_phase):
        r"""Fetches the phase of the processed mean acquired waveform relative to the processed reference waveform.

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

            relative_phase (numpy.float32):
                This parameter returns the instantaneous relative phase. This value is expressed in degree.

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
            x0, dx, error_code = self._interpreter.ampm_fetch_relative_phase_trace(
                updated_selector_string, timeout, relative_phase
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_relative_power_trace(self, selector_string, timeout, relative_power):
        r"""Fetches the power of the processed mean acquired waveform relative to the processed reference waveform.

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

            relative_power (numpy.float32):
                This parameter returns the instantaneous relative power, in dB.

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
            x0, dx, error_code = self._interpreter.ampm_fetch_relative_power_trace(
                updated_selector_string, timeout, relative_power
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code
