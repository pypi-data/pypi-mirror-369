"""Provides methods to fetch and read the Pavt measurement results."""

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


class PavtResults(object):
    """Provides methods to fetch and read the Pavt measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Pavt measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_mean_relative_phase(self, selector_string):
        r"""Gets the mean phase of the segment, relative to the phase of the reference segment. This value is expressed in
        degrees.
        
        Mean Relative Phase = Q\ :sub:`i`\ - Q\ :sub:`r`\
        
        Q\ :sub:`i`\ is the absolute phase of the segment i, expressed in degrees
        
        Q\ :sub:`r`\ is the absolute phase of the reference segment r, expressed in degrees
        
        where,
        r = 1, if Segment0 is configured as Frequency Error Measurement segment
        r = 0, otherwise
        
        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string): 
                Pass an empty string.
        
        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean phase of the segment, relative to the phase of the reference segment. This value is expressed in
                degrees.

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
                attributes.AttributeID.PAVT_RESULTS_MEAN_RELATIVE_PHASE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_relative_amplitude(self, selector_string):
        r"""Gets the mean amplitude of the segment, relative to the amplitude of the reference segment. This value is expressed
        in dB.
        
        Mean Relative Amplitude = a\ :sub:`i`\ - a\ :sub:`r`\
        
        a\ :sub:`i`\ is the absolute amplitude of the segment i, expressed in dBm
        
        a\ :sub:`r`\ is the absolute amplitude of the reference segment r, expressed in dBm
        
        where,
        r = 1, if Segment0 is configured as Frequency Error Measurement segment
        r = 0, otherwise
        
        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string): 
                Pass an empty string.
        
        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean amplitude of the segment, relative to the amplitude of the reference segment. This value is expressed
                in dB.

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
                attributes.AttributeID.PAVT_RESULTS_MEAN_RELATIVE_AMPLITUDE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_absolute_phase(self, selector_string):
        r"""Gets the mean absolute phase of the segment. This value is expressed in degrees.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean absolute phase of the segment. This value is expressed in degrees.

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
                attributes.AttributeID.PAVT_RESULTS_MEAN_ABSOLUTE_PHASE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_mean_absolute_amplitude(self, selector_string):
        r"""Gets the mean absolute amplitude of the segment. This value is expressed in dBm.

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean absolute amplitude of the segment. This value is expressed in dBm.

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
                attributes.AttributeID.PAVT_RESULTS_MEAN_ABSOLUTE_AMPLITUDE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_frequency_error_mean(self, selector_string):
        r"""Gets the mean frequency error of the segment. This value is expressed in Hz

        Use "segment<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the mean frequency error of the segment. This value is expressed in Hz

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
                attributes.AttributeID.PAVT_RESULTS_FREQUENCY_ERROR_MEAN.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_amplitude_trace(self, selector_string, timeout, trace_index, amplitude):
        r"""Fetches the amplitude trace for the measurement.

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
                This parameter specifies the timeout for fetching the specified measurement. This value is expressed in seconds. Set
                this value to an appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the
                method waits until the measurement is complete. The default value is 10.

            trace_index (int):
                Specifies the index of the trace to fetch. The **traceIndex** can range from 0 to (Number of carriers + 2*Number of
                offsets).

            amplitude (numpy.float32):
                This parameter returns the amplitude values of the complex baseband samples, in dBm.

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
            x0, dx, error_code = self._interpreter.pavt_fetch_amplitude_trace(
                updated_selector_string, timeout, trace_index, amplitude
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_phase_and_amplitude_array(self, selector_string, timeout):
        r"""Fetches an array of mean values of phase and amplitude of the segments.

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
                This parameter specifies the timeout for fetching the specified measurement. This value is expressed in seconds. Set
                this value to an appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the
                method waits until the measurement is complete. The default value is 10.

        Returns:
            Tuple (mean_relative_phase, mean_relative_amplitude, mean_absolute_phase, mean_absolute_amplitude, error_code):

            mean_relative_phase (float):
                This parameter returns an array of the mean phase of the segment relative to the first segment of the measurement. This
                value is expressed in degrees.

            mean_relative_amplitude (float):
                This parameter returns an array of the mean amplitude of the segment relative to the first segment of the measurement.
                This value is expressed in dB.

            mean_absolute_phase (float):
                This parameter returns an array of the mean absolute phase of the segment. This value is expressed in degrees.

            mean_absolute_amplitude (float):
                This parameter returns an array of the mean absolute amplitude of the segment. This value is expressed in dBm.

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
                mean_relative_phase,
                mean_relative_amplitude,
                mean_absolute_phase,
                mean_absolute_amplitude,
                error_code,
            ) = self._interpreter.pavt_fetch_phase_and_amplitude_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            mean_relative_phase,
            mean_relative_amplitude,
            mean_absolute_phase,
            mean_absolute_amplitude,
            error_code,
        )

    @_raise_if_disposed
    def fetch_phase_and_amplitude(self, selector_string, timeout):
        r"""Fetches the mean values of phase and amplitude of the segment.

        Use "segment<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and segment number.

                Example:

                "segment0"

                "result::r1/segment0"

                You can use the :py:meth:`build_segment_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout for fetching the specified measurement. This value is expressed in seconds. Set
                this value to an appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the
                method waits until the measurement is complete. The default value is 10.

        Returns:
            Tuple (mean_relative_phase, mean_relative_amplitude, mean_absolute_phase, mean_absolute_amplitude, error_code):

            mean_relative_phase (float):
                This parameter returns the mean phase of the segment, relative to the phase of the reference segment. This value is
                expressed in degrees.

            mean_relative_amplitude (float):
                This parameter returns the mean amplitude of the segment, relative to the amplitude of the reference segment. This
                value is expressed in dB.

            mean_absolute_phase (float):
                This parameter returns the mean absolute phase of the segment. This value is expressed in degrees.

            mean_absolute_amplitude (float):
                This parameter returns the mean absolute amplitude of the segment. This value is expressed in dBm.

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
                mean_relative_phase,
                mean_relative_amplitude,
                mean_absolute_phase,
                mean_absolute_amplitude,
                error_code,
            ) = self._interpreter.pavt_fetch_phase_and_amplitude(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            mean_relative_phase,
            mean_relative_amplitude,
            mean_absolute_phase,
            mean_absolute_amplitude,
            error_code,
        )

    @_raise_if_disposed
    def fetch_phase_trace(self, selector_string, timeout, trace_index, phase):
        r"""Fetches the phase trace for the measurement.

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
                This parameter specifies the timeout for fetching the specified measurement. This value is expressed in seconds. Set
                this value to an appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the
                method waits until the measurement is complete. The default value is 10.

            trace_index (int):
                Specifies the index of the trace to fetch. The **traceIndex** can range from 0 to (Number of carriers + 2*Number of
                offsets).

            phase (numpy.float32):
                This parameter returns the phase values of the complex baseband samples, in degrees.

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
            x0, dx, error_code = self._interpreter.pavt_fetch_phase_trace(
                updated_selector_string, timeout, trace_index, phase
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code
