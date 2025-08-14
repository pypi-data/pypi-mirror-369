"""Provides methods to fetch and read the Marker measurement results."""

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


class MarkerResults(object):
    """Provides methods to fetch and read the Marker measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Marker measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def fetch_xy(self, selector_string):
        r"""Returns the X and Y locations of the marker.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and marker number.

                Example:

                "marker0"

                "result::r1/marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

        Returns:
            Tuple (marker_x_location, marker_y_location, error_code):

            marker_x_location (float):
                This parameter returns the marker X location.

            marker_y_location (float):
                This parameter returns the marker Y location.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            marker_x_location, marker_y_location, error_code = self._interpreter.marker_fetch_xy(
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return marker_x_location, marker_y_location, error_code

    @_raise_if_disposed
    def next_peak(self, selector_string, next_peak):
        r"""Moves the marker to the next highest or next left or next right peak above the threshold on the configured trace.
        Use "marker<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and marker number.

                Example:

                "marker0"

                "result::r1/marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            next_peak (enums.MarkerNextPeak, int):
                This parameter specifies the next peak on the trace. The default value is **Next Highest**.

                +------------------+----------------------------------------------------------------------------------------+
                | Name (Value)     | Description                                                                            |
                +==================+========================================================================================+
                | Next Highest (0) | Moves the marker to the next highest peak above the threshold on the configured trace. |
                +------------------+----------------------------------------------------------------------------------------+
                | Next Left (1)    | Moves the marker to the next peak to the left of the configured trace.                 |
                +------------------+----------------------------------------------------------------------------------------+
                | Next Right (2)   | Moves the marker to the next peak to the right of the configured trace.                |
                +------------------+----------------------------------------------------------------------------------------+

        Returns:
            Tuple (next_peak_found, error_code):

            next_peak_found (bool):
                This parameter indicates whether the method has found the next peak on the trace.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            next_peak = next_peak.value if type(next_peak) is enums.MarkerNextPeak else next_peak
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            next_peak_found, error_code = self._interpreter.marker_next_peak(
                updated_selector_string, next_peak
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return next_peak_found, error_code

    @_raise_if_disposed
    def peak_search(self, selector_string):
        r"""Moves the marker to the highest peak that satisfies peak threshold and peak excursion criteria.
        Use "marker<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and marker number.

                Example:

                "marker0"

                "result::r1/marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

        Returns:
            Tuple (number_of_peaks, error_code):

            number_of_peaks (int):
                This parameter  returns the total number of peaks above the threshold, when you set the enable the marker threshold.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            number_of_peaks, error_code = self._interpreter.marker_peak_search(
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return number_of_peaks, error_code

    @_raise_if_disposed
    def fetch_function_value(self, selector_string):
        r"""Returns the function value of the selected marker function type.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and marker number.

                Example:

                "marker0"

                "result::r1/marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

        Returns:
            Tuple (function_value, error_code):

            function_value (float):
                This parameter returns the value of the selected marker function.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            function_value, error_code = self._interpreter.marker_fetch_function_value(
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return function_value, error_code
