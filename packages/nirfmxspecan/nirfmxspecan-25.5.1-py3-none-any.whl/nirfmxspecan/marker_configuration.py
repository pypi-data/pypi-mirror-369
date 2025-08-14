"""Provides methods to configure the Marker measurement."""

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


class MarkerConfiguration(object):
    """Provides methods to configure the Marker measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Marker measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def configure_number_of_markers(self, selector_string, number_of_markers):
        r"""Configures the number of markers.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_markers (int):
                This parameter specifies the number of markers. The default value is 12.

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
            error_code = self._interpreter.marker_configure_number_of_markers(
                updated_selector_string, number_of_markers
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_peak_excursion(self, selector_string, peak_excursion_enabled, peak_excursion):
        r"""Configures the peak excursion.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            peak_excursion_enabled (enums.MarkerPeakExcursionEnabled, int):
                This parameter specifies whether to enable the peak excursion check for the trace while finding the peaks. The default
                value is **False**.

                +--------------+--------------------------------------------------------------------------+
                | Name (Value) | Description                                                              |
                +==============+==========================================================================+
                | False (0)    | Disables the peak excursion check for the trace while finding the peaks. |
                +--------------+--------------------------------------------------------------------------+
                | True (1)     | Enables the peak excursion check for the trace while finding the peaks.  |
                +--------------+--------------------------------------------------------------------------+

            peak_excursion (float):
                This parameter specifies the peak excursion value for finding the peaks on trace when you set the **Peak Excursion
                Enabled** parameter to **True**. The signal should rise and fall by at least the peak excursion value, above the
                threshold, to be considered as a peak. The default value is 6.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            peak_excursion_enabled = (
                peak_excursion_enabled.value
                if type(peak_excursion_enabled) is enums.MarkerPeakExcursionEnabled
                else peak_excursion_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.marker_configure_peak_excursion(
                updated_selector_string, peak_excursion_enabled, peak_excursion
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_marker(self, selector_string, reference_marker):
        r"""Configures the reference marker to a delta marker.

        Use "marker<
        *
        n
        *
        >" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            reference_marker (int):
                This parameter specifies the marker to be used as reference marker when you set the Marker Type attribute to **Delta**.
                This parameter is not used when you set the Marker Type attribute to **Normal** or **Fixed**.

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
            error_code = self._interpreter.marker_configure_reference_marker(
                updated_selector_string, reference_marker
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_threshold(self, selector_string, threshold_enabled, threshold):
        r"""Configures the threshold to use for peak search.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            threshold_enabled (enums.MarkerThresholdEnabled, int):
                This parameter specifies whether to enable the threshold for the trace while finding the peaks. The default value is
                **False**.

                +--------------+--------------------------------------------------------------+
                | Name (Value) | Description                                                  |
                +==============+==============================================================+
                | False (0)    | Disables the threshold for the trace while finding the peaks |
                +--------------+--------------------------------------------------------------+
                | True (1)     | Enables the threshold for the trace while finding the peaks  |
                +--------------+--------------------------------------------------------------+

            threshold (float):
                This parameter specifies the threshold for finding the peaks on the trace. The default value is -90.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            threshold_enabled = (
                threshold_enabled.value
                if type(threshold_enabled) is enums.MarkerThresholdEnabled
                else threshold_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.marker_configure_threshold(
                updated_selector_string, threshold_enabled, threshold
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_trace(self, selector_string, trace):
        r"""Configures the measurement trace to be used by the marker.
        Use "marker<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            trace (enums.MarkerTrace, int):
                This parameter specifies the trace. The default value is **Spectrum**.

                +---------------------------------------+--------------------------------------------------------+
                | Name (Value)                          | Description                                            |
                +=======================================+========================================================+
                | ACP Spectrum (0)                      | The marker uses the ACP spectrum trace.                |
                +---------------------------------------+--------------------------------------------------------+
                | CCDF Gaussian Probabilities Trace (1) | The marker uses the CCDF Gaussian probabilities trace. |
                +---------------------------------------+--------------------------------------------------------+
                | CCDF Probabilities Trace (2)          | The marker uses the CCDF probabilities trace.          |
                +---------------------------------------+--------------------------------------------------------+
                | CHP Spectrum (3)                      | The marker uses the CHP spectrum trace.                |
                +---------------------------------------+--------------------------------------------------------+
                | FCnt Power Trace (4)                  | The marker uses the FCnt power trace.                  |
                +---------------------------------------+--------------------------------------------------------+
                | OBW Spectrum (5)                      | The marker uses the OBW spectrum trace.                |
                +---------------------------------------+--------------------------------------------------------+
                | SEM Spectrum (6)                      | The marker uses the SEM spectrum trace.                |
                +---------------------------------------+--------------------------------------------------------+
                | Spectrum (7)                          | The marker uses the Spectrum trace.                    |
                +---------------------------------------+--------------------------------------------------------+
                | TXP Power Trace (8)                   | The marker uses the TXP power trace.                   |
                +---------------------------------------+--------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            trace = trace.value if type(trace) is enums.MarkerTrace else trace
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.marker_configure_trace(updated_selector_string, trace)
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_type(self, selector_string, marker_type):
        r"""Configures the marker type.
        Use "marker<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            marker_type (enums.MarkerType, int):
                This parameter specifies whether the marker is disabled (Off) or is enabled (On) as a normal marker, delta marker or a
                fixed marker. The default value is **Off**.

                +--------------+-------------------------------------------+
                | Name (Value) | Description                               |
                +==============+===========================================+
                | Off (0)      | The marker is disabled.                   |
                +--------------+-------------------------------------------+
                | Normal (1)   | The marker is enabled as a normal marker. |
                +--------------+-------------------------------------------+
                | Delta (3)    | The marker is enabled as a delta marker.  |
                +--------------+-------------------------------------------+
                | Fixed (4)    | The marker is enabled as a fixed marker.  |
                +--------------+-------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            marker_type = (
                marker_type.value if type(marker_type) is enums.MarkerType else marker_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.marker_configure_type(
                updated_selector_string, marker_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_x_location(self, selector_string, marker_x_location):
        r"""Configures the X location of the marker. You must configure the reference marker X location or perform peak search on
        the reference marker before configuring the X location for the Delta marker.
        Use "marker<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            marker_x_location (float):
                This parameter specifies the X location of the marker on the trace when you set the Marker Type parameter to **Normal**
                or **Fixed**. The X location is relative to the value of the reference marker when you set the Marker Type parameter to
                **Delta**.

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
            error_code = self._interpreter.marker_configure_x_location(
                updated_selector_string, marker_x_location
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_y_location(self, selector_string, marker_y_location):
        r"""Configures the Y location of the marker. You must configure the reference marker Y location or perform peak search on
        the reference marker before configuring the X location for the Delta marker.

        Use "marker<*n*>" as the selector string to configure this method.

        .. note::
           You can configure the Y location of the marker only if you set the Marker Type parameter to **Fixed**.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            marker_y_location (float):
                This parameter specifies the Y location of the marker when you set the Marker Type parameter to **Fixed**.

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
            error_code = self._interpreter.marker_configure_y_location(
                updated_selector_string, marker_y_location
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_function_type(self, selector_string, function_type):
        r"""Configures the marker function type.

        Use "marker<
        *
        n
        *
        >" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            function_type (enums.MarkerFunctionType, int):
                This parameter specifies the function type for the selected marker. The default value is **Off**.

                +----------------+---------------------------------------------------+
                | Name (Value)   | Description                                       |
                +================+===================================================+
                | Off (0)        | The marker function is disabled.                  |
                +----------------+---------------------------------------------------+
                | Band Power (1) | Band Power is computed within the specified span. |
                +----------------+---------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            function_type = (
                function_type.value
                if type(function_type) is enums.MarkerFunctionType
                else function_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.marker_configure_function_type(
                updated_selector_string, function_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_band_span(self, selector_string, span):
        r"""Configures the band span of the selected marker.
        Use "marker<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of marker
                number.

                Example:

                "marker0"

                You can use the :py:meth:`build_marker_string` method  to build the selector string.

            span (float):
                This parameter specifies the width of the span for the selected marker. This attribute selects the trace data within
                the specified span to perform specified marker function.

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
            error_code = self._interpreter.marker_configure_band_span(updated_selector_string, span)
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
