"""Provides methods to fetch and read the Idpd measurement results."""

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


class IdpdResults(object):
    """Provides methods to fetch and read the Idpd measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Idpd measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_gain(self, selector_string):
        r"""Gets the gain of the device under test. This value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the gain of the device under test. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_RESULTS_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_rms_evm(self, selector_string):
        r"""Gets the ratio of L2 norm of difference between the normalized reference and acquired waveforms, to the L2 norm of
        the normalized reference waveform. This value is expressed either as a percentage or in dB depending on the configured
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EVM_UNIT`,

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the ratio of L2 norm of difference between the normalized reference and acquired waveforms, to the L2 norm of
                the normalized reference waveform. This value is expressed either as a percentage or in dB depending on the configured
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EVM_UNIT`,

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IDPD_RESULTS_MEAN_RMS_EVM.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_processed_mean_acquired_waveform(
        self, selector_string, timeout, processed_mean_acquired_waveform
    ):
        r"""Fetches the averaged acquired waveform, corrected for frequency, phase, and DC offsets, used to perform the IDPD
        measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

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
            x0, dx, error_code = self._interpreter.idpd_fetch_processed_mean_acquired_waveform(
                updated_selector_string, timeout, processed_mean_acquired_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_processed_reference_waveform(
        self, selector_string, timeout, processed_reference_waveform
    ):
        r"""Fetches the reference waveform used to perform the IDPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

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
            x0, dx, error_code = self._interpreter.idpd_fetch_processed_reference_waveform(
                updated_selector_string, timeout, processed_reference_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_predistorted_waveform(self, selector_string, timeout, predistorted_waveform):
        r"""Fetches the predistorted waveform output after the IDPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            predistorted_waveform (numpy.complex64):
                This parameter returns the complex baseband samples, in volts.

        Returns:
            Tuple (x0, dx, papr, power_offset, gain, error_code):

            x0 (float):
                This parameter returns the start time, in seconds.

            dx (float):
                This parameter returns the sample duration, in seconds.

            papr (float):
                This parameter returns the peak-to-average power ratio of the waveform obtained after applying digital predistortion.
                This value is expressed in dB.

            power_offset (float):
                This parameter returns the change in the average power in the waveform due to applying digital predistortion. This
                value is expressed in dB.

            gain (float):
                This parameter returns the gain of the device under test. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, papr, power_offset, gain, error_code = (
                self._interpreter.idpd_fetch_predistorted_waveform(
                    updated_selector_string, timeout, predistorted_waveform
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, papr, power_offset, gain, error_code

    @_raise_if_disposed
    def fetch_equalizer_coefficients(self, selector_string, timeout, equalizer_coefficients):
        r"""Fetches the trained equalizer coefficients.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            equalizer_coefficients (numpy.complex64):
                This parameter returns the updated equalizer coefficients.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter this parameter always returns 0.

            dx (float):
                This parameter returns the spacing between the coefficients.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.idpd_fetch_equalizer_coefficients(
                updated_selector_string, timeout, equalizer_coefficients
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def get_equalizer_reference_waveform(self, selector_string, equalizer_reference_waveform):
        r"""Gets the equalizer reference waveform used to perform the IDPD measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            equalizer_reference_waveform (numpy.complex64):
                This parameter returns the complex baseband samples, in volts.

        Returns:
            Tuple (x0, dx, papr, error_code):

            x0 (float):
                This parameter returns the start time, in seconds.

            dx (float):
                This parameter returns the sample duration, in seconds.

            papr (float):
                This parameter returns the peak-to-average power ratio of the waveform obtained after applying digital predistortion.
                This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, papr, error_code = self._interpreter.idpd_get_equalizer_reference_waveform(
                updated_selector_string, equalizer_reference_waveform
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, papr, error_code
