"""Provides methods to fetch and read the Spectrum measurement results."""

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


class SpectrumResults(object):
    """Provides methods to fetch and read the Spectrum measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Spectrum measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_peak_amplitude(self, selector_string):
        r"""Gets the peak amplitude, of the averaged spectrum.

        When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0, the measurement returns
        the peak amplitude in the time domain power trace.

        The amplitude is reported in units specified by the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak amplitude, of the averaged spectrum.

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
                attributes.AttributeID.SPECTRUM_RESULTS_PEAK_AMPLITUDE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_peak_frequency(self, selector_string):
        r"""Gets the frequency at the peak amplitude of the averaged spectrum. This value is expressed in Hz. This attribute is
        not valid if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency at the peak amplitude of the averaged spectrum. This value is expressed in Hz. This attribute is
                not valid if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0.

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
                attributes.AttributeID.SPECTRUM_RESULTS_PEAK_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_frequency_resolution(self, selector_string):
        r"""Gets the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz. This
        attribute is not valid if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz. This
                attribute is not valid if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0.

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
                attributes.AttributeID.SPECTRUM_RESULTS_FREQUENCY_RESOLUTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_measurement(self, selector_string, timeout):
        r"""Fetches the peak amplitude and frequency at which the peak occurred in the spectrum.

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
            Tuple (peak_amplitude, peak_frequency, frequency_resolution, error_code):

            peak_amplitude (float):
                This parameter returns the peak amplitude, of the averaged spectrum. When you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0, this method returns the peak amplitude in the time
                domain power trace.

            peak_frequency (float):
                This parameter returns the frequency, in Hz, at the peak amplitude of the averaged spectrum. This parameter is not
                valid if you set the Spectrum Span attribute to 0.

            frequency_resolution (float):
                This parameter returns the frequency bin spacing, in Hz, of the spectrum acquired by the measurement. This parameter is
                not valid if you set the Spectrum Span attribute to 0.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            peak_amplitude, peak_frequency, frequency_resolution, error_code = (
                self._interpreter.spectrum_fetch_measurement(updated_selector_string, timeout)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return peak_amplitude, peak_frequency, frequency_resolution, error_code

    @_raise_if_disposed
    def fetch_power_trace(self, selector_string, timeout, power):
        r"""Fetches the power trace for the Spectrum measurement.

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
            x0, dx, error_code = self._interpreter.spectrum_fetch_power_trace(
                updated_selector_string, timeout, power
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_spectrum(self, selector_string, timeout, spectrum):
        r"""Fetches the spectrum used for the Spectrum measurement.

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
                This parameter returns the averaged power, measured at each frequency bin. When you set the Spectrum Span attribute to
                0, the averaged power is measured at each sample instance in time. The units of power is as specified using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency, in Hz. When you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SPAN` attribute to 0, **x0** returns the start time, in seconds.

            dx (float):
                This parameter returns the frequency bin spacing, in Hz. When you set the Spectrum Span attribute to 0, **dx** returns
                the sample duration, in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.spectrum_fetch_spectrum(
                updated_selector_string, timeout, spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def read(self, selector_string, timeout, spectrum):
        r"""Configures hardware for acquisition, performs measurement on acquired data, and returns Spectrum measurement results.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. The default value is 10.

            spectrum (numpy.float32):
                This parameter returns the spectrum trace.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency, in Hz. When you set the %attribute{spectrum span} attribute to 0, **x0**
                returns the start time, in seconds.

            dx (float):
                This parameter returns the frequency bin spacing, in Hz. When you set the Spectrum Span attribute to 0, **dx** returns
                the sample duration, in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.spectrum_read(
                updated_selector_string, timeout, spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code
