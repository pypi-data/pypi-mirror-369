"""Provides methods to fetch and read the IQ measurement results."""

import functools

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


class IQResults(object):
    """Provides methods to fetch and read the IQ measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the IQ measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def fetch_data(self, selector_string, timeout, record_to_fetch, samples_to_read, data):
        r"""Fetches I/Q data from a single record in an acquisition.

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

            record_to_fetch (int):
                This parameter specifies the record to retrieve. Record numbers are zero-based. The default value is 0.

            samples_to_read (int):
                This parameter specifies the number of samples to fetch. A value of -1 specifies that RFmx fetches all samples. The
                default value is -1.

            data (numpy.complex64):
                This parameter returns the complex-value time domain data array. The real and imaginary parts of this complex data
                array correspond to the in-phase (I) and quadrature-phase (Q) data, respectively. To calculate the instantaneous power
                of a sampled I/Q point, use the equation (*I*
                \ :sup:`2`\ + *Q*
                \ :sup:`2`\) / 2*R*, where *R* is the input impedance in ohms. For RFmx, *R* = 50 ohms.

        Returns:
            Tuple (t0, dt, error_code):

            t0 (float):
                This parameter returns the start time of the first sample. The timestamp corresponds to the difference, in seconds,
                between the first sample returned and the Reference Trigger location.

            dt (float):
                This parameter returns the time interval between data points in the acquired signal. The I/Q data sample rate is the
                reciprocal of this value.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            t0, dt, error_code = self._interpreter.iq_fetch_data(
                updated_selector_string, timeout, record_to_fetch, samples_to_read, data
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return t0, dt, error_code

    @_raise_if_disposed
    def get_records_done(self, selector_string):
        r"""Fetches the number of records that RFmx has acquired.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

        Returns:
            Tuple (records_done, error_code):

            records_done (int):
                This parameter returns the number of records that RFmx has acquired.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            records_done, error_code = self._interpreter.iq_get_records_done(
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return records_done, error_code
