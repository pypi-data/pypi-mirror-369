"""Provides methods to configure the Spectrum measurement."""

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


class SpectrumConfiguration(object):
    """Provides methods to configure the Spectrum measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Spectrum measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the spectrum measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable the spectrum measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the spectrum measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the spectrum measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_span(self, selector_string):
        r"""Gets the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
        Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
                Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_SPAN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_span(self, selector_string, value):
        r"""Sets the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
        Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency range around the center frequency, to acquire for the measurement. This value is expressed in
                Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_SPAN.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_power_units(self, selector_string):
        r"""Gets the units for the absolute power.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **dBm**.

        +-------------------+---------------------------------------------+
        | Name (Value)      | Description                                 |
        +===================+=============================================+
        | dBm (0)           | The absolute powers are reported in dBm.    |
        +-------------------+---------------------------------------------+
        | dBm/Hz (1)        | The absolute powers are reported in dBm/Hz. |
        +-------------------+---------------------------------------------+
        | dBW (2)           | The absolute powers are reported in dBW.    |
        +-------------------+---------------------------------------------+
        | dBV (3)           | The absolute powers are reported in dBV.    |
        +-------------------+---------------------------------------------+
        | dBmV (4)          | The absolute powers are reported in dBmV.   |
        +-------------------+---------------------------------------------+
        | dBuV (5)          | The absolute powers are reported in dBuV.   |
        +-------------------+---------------------------------------------+
        | W (6)             | The absolute powers are reported in W.      |
        +-------------------+---------------------------------------------+
        | Volts (7)         | The absolute powers are reported in volts.  |
        +-------------------+---------------------------------------------+
        | Volts Squared (8) | The absolute powers are reported in volts2. |
        +-------------------+---------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumPowerUnits):
                Specifies the units for the absolute power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_POWER_UNITS.value
            )
            attr_val = enums.SpectrumPowerUnits(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_power_units(self, selector_string, value):
        r"""Sets the units for the absolute power.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **dBm**.

        +-------------------+---------------------------------------------+
        | Name (Value)      | Description                                 |
        +===================+=============================================+
        | dBm (0)           | The absolute powers are reported in dBm.    |
        +-------------------+---------------------------------------------+
        | dBm/Hz (1)        | The absolute powers are reported in dBm/Hz. |
        +-------------------+---------------------------------------------+
        | dBW (2)           | The absolute powers are reported in dBW.    |
        +-------------------+---------------------------------------------+
        | dBV (3)           | The absolute powers are reported in dBV.    |
        +-------------------+---------------------------------------------+
        | dBmV (4)          | The absolute powers are reported in dBmV.   |
        +-------------------+---------------------------------------------+
        | dBuV (5)          | The absolute powers are reported in dBuV.   |
        +-------------------+---------------------------------------------+
        | W (6)             | The absolute powers are reported in W.      |
        +-------------------+---------------------------------------------+
        | Volts (7)         | The absolute powers are reported in volts.  |
        +-------------------+---------------------------------------------+
        | Volts Squared (8) | The absolute powers are reported in volts2. |
        +-------------------+---------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumPowerUnits, int):
                Specifies the units for the absolute power.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumPowerUnits else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_POWER_UNITS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the measurement computes the resolution bandwidth (RBW).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                  |
        +==============+==============================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the Spectrum RBW attribute. |
        +--------------+------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                            |
        +--------------+------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumRbwAutoBandwidth):
                Specifies whether the measurement computes the resolution bandwidth (RBW).

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
                attributes.AttributeID.SPECTRUM_RBW_FILTER_AUTO_BANDWIDTH.value,
            )
            attr_val = enums.SpectrumRbwAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the measurement computes the resolution bandwidth (RBW).

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                  |
        +==============+==============================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the Spectrum RBW attribute. |
        +--------------+------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                            |
        +--------------+------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumRbwAutoBandwidth, int):
                Specifies whether the measurement computes the resolution bandwidth (RBW).

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumRbwAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_RBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
                expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_RBW_FILTER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This value is
                expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_RBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_type(self, selector_string):
        r"""Gets the shape of the digital resolution bandwidth (RBW) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Gaussian**.

        +---------------+-----------------------------------------+
        | Name (Value)  | Description                             |
        +===============+=========================================+
        | FFT Based (0) | No RBW filtering is performed.          |
        +---------------+-----------------------------------------+
        | Gaussian (1)  | The RBW filter has a Gaussian response. |
        +---------------+-----------------------------------------+
        | Flat (2)      | The RBW filter has a flat response.     |
        +---------------+-----------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumRbwFilterType):
                Specifies the shape of the digital resolution bandwidth (RBW) filter.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_RBW_FILTER_TYPE.value
            )
            attr_val = enums.SpectrumRbwFilterType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_type(self, selector_string, value):
        r"""Sets the shape of the digital resolution bandwidth (RBW) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Gaussian**.

        +---------------+-----------------------------------------+
        | Name (Value)  | Description                             |
        +===============+=========================================+
        | FFT Based (0) | No RBW filtering is performed.          |
        +---------------+-----------------------------------------+
        | Gaussian (1)  | The RBW filter has a Gaussian response. |
        +---------------+-----------------------------------------+
        | Flat (2)      | The RBW filter has a flat response.     |
        +---------------+-----------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumRbwFilterType, int):
                Specifies the shape of the digital resolution bandwidth (RBW) filter.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_RBW_FILTER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_bandwidth_definition(self, selector_string):
        r"""Gets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to  |
        |               | FFT Based, RBW is the 3dB bandwidth of the window specified by the Spectrum FFT Window attribute.                        |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | 6dB (1)       | Defines the RBW in terms of the 6dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to  |
        |               | FFT Based, RBW is the 6dB bandwidth of the window specified by the Spectrum FFT Window attribute.                        |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spectrum RBW Filter Type          |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | ENBW (3)      | Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute    |
        |               | to FFT Based, RBW is the ENBW                                                                                            |
        |               | bandwidth of the window specified by the Spectrum FFT Window attribute.                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumRbwFilterBandwidthDefinition):
                Specifies the bandwidth definition which you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.

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
                attributes.AttributeID.SPECTRUM_RBW_FILTER_BANDWIDTH_DEFINITION.value,
            )
            attr_val = enums.SpectrumRbwFilterBandwidthDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_bandwidth_definition(self, selector_string, value):
        r"""Sets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to  |
        |               | FFT Based, RBW is the 3dB bandwidth of the window specified by the Spectrum FFT Window attribute.                        |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | 6dB (1)       | Defines the RBW in terms of the 6dB bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute to  |
        |               | FFT Based, RBW is the 6dB bandwidth of the window specified by the Spectrum FFT Window attribute.                        |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spectrum RBW Filter Type          |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | ENBW (3)      | Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spectrum RBW Filter Type attribute    |
        |               | to FFT Based, RBW is the ENBW                                                                                            |
        |               | bandwidth of the window specified by the Spectrum FFT Window attribute.                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumRbwFilterBandwidthDefinition, int):
                Specifies the bandwidth definition which you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = (
                value.value if type(value) is enums.SpectrumRbwFilterBandwidthDefinition else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_RBW_FILTER_BANDWIDTH_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_vbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Specify the video bandwidth in the Spectrum VBW attribute. The Spectrum VBW to RBW Ratio attribute is disregarded in     |
        |              | this mode.                                                                                                               |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
        |              | the Spectrum VBW to RBW Ratio attribute and the Spectrum RBW attribute. The value of the Spectrum VBW attribute is       |
        |              | disregarded in this mode.                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumVbwFilterAutoBandwidth):
                Specifies whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.

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
                attributes.AttributeID.SPECTRUM_VBW_FILTER_AUTO_BANDWIDTH.value,
            )
            attr_val = enums.SpectrumVbwFilterAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_vbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Specify the video bandwidth in the Spectrum VBW attribute. The Spectrum VBW to RBW Ratio attribute is disregarded in     |
        |              | this mode.                                                                                                               |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
        |              | the Spectrum VBW to RBW Ratio attribute and the Spectrum RBW attribute. The value of the Spectrum VBW attribute is       |
        |              | disregarded in this mode.                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumVbwFilterAutoBandwidth, int):
                Specifies whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumVbwFilterAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_VBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_vbw_filter_bandwidth(self, selector_string):
        r"""Gets the video bandwidth (VBW) in Hz when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 30000.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the video bandwidth (VBW) in Hz when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_VBW_FILTER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_vbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the video bandwidth (VBW) in Hz when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 30000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the video bandwidth (VBW) in Hz when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_VBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_vbw_filter_vbw_to_rbw_ratio(self, selector_string):
        r"""Gets the VBW to RBW Ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True** .

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the VBW to RBW Ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True** .

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
                attributes.AttributeID.SPECTRUM_VBW_FILTER_VBW_TO_RBW_RATIO.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_vbw_filter_vbw_to_rbw_ratio(self, selector_string, value):
        r"""Sets the VBW to RBW Ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True** .

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the VBW to RBW Ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True** .

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_VBW_FILTER_VBW_TO_RBW_RATIO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_sweep_time_auto(self, selector_string):
        r"""Gets whether the measurement computes the sweep time.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+---------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                 |
        +==============+=============================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the Spectrum Sweep Time attribute.  |
        +--------------+---------------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the Spectrum RBW attribute. |
        +--------------+---------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumSweepTimeAuto):
                Specifies whether the measurement computes the sweep time.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_SWEEP_TIME_AUTO.value
            )
            attr_val = enums.SpectrumSweepTimeAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_sweep_time_auto(self, selector_string, value):
        r"""Sets whether the measurement computes the sweep time.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+---------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                 |
        +==============+=============================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the Spectrum Sweep Time attribute.  |
        +--------------+---------------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the Spectrum RBW attribute. |
        +--------------+---------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumSweepTimeAuto, int):
                Specifies whether the measurement computes the sweep time.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumSweepTimeAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_SWEEP_TIME_AUTO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_sweep_time_interval(self, selector_string):
        r"""Gets the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
        **False**. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
                **False**. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_SWEEP_TIME_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_sweep_time_interval(self, selector_string, value):
        r"""Sets the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
        **False**. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.SWEEP_TIME_AUTO` attribute to
                **False**. This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_SWEEP_TIME_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_detector_type(self, selector_string):
        r"""Gets the type of detector to be used.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **None**.

        Refer to `Spectral Measurements Concepts
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
        detector types.

        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)        | Description                                                                                                              |
        +=====================+==========================================================================================================================+
        | None (0)            | The detector is disabled.                                                                                                |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
        |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
        |                     | alternate buckets.                                                                                                       |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumDetectorType):
                Specifies the type of detector to be used.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_DETECTOR_TYPE.value
            )
            attr_val = enums.SpectrumDetectorType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_detector_type(self, selector_string, value):
        r"""Sets the type of detector to be used.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **None**.

        Refer to `Spectral Measurements Concepts
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
        detector types.

        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)        | Description                                                                                                              |
        +=====================+==========================================================================================================================+
        | None (0)            | The detector is disabled.                                                                                                |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
        |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
        |                     | alternate buckets.                                                                                                       |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumDetectorType, int):
                Specifies the type of detector to be used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumDetectorType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_DETECTOR_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_detector_points(self, selector_string):
        r"""Gets the number of trace points after the detector is applied.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1001.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of trace points after the detector is applied.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_DETECTOR_POINTS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_detector_points(self, selector_string, value):
        r"""Sets the number of trace points after the detector is applied.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of trace points after the detector is applied.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_DETECTOR_POINTS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_calibration_mode(self, selector_string):
        r"""Gets whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
        Refer to the measurement guidelines section in the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Auto**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | When you set the Spectrum Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration    |
        |              | for the spectrum measurement manually. When you set the Spectrum Meas Mode attribute to Measure, you can initiate the    |
        |              | spectrum measurement manually.                                                                                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Auto (1)     | When you set the Spectrum Noise Comp Enabled attribute to True, RFmx sets the Input Isolation Enabled attribute to       |
        |              | Enabled and calibrates the intrument noise in the current state of the instrument. RFmx then resets the Input Isolation  |
        |              | Enabled attribute and performs the spectrum measurement, including compensation for noise from the instrument. RFmx      |
        |              | skips noise calibration in this mode if valid noise calibration data is already cached. When you set the Spectrum Noise  |
        |              | Comp Enabled attribute to False, RFmx does not calibrate instrument noise and performs only the spectrum measurement     |
        |              | without compensating for the noise from the instrument.                                                                  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumNoiseCalibrationMode):
                Specifies whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
                Refer to the measurement guidelines section in the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

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
                attributes.AttributeID.SPECTRUM_NOISE_CALIBRATION_MODE.value,
            )
            attr_val = enums.SpectrumNoiseCalibrationMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_calibration_mode(self, selector_string, value):
        r"""Sets whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
        Refer to the measurement guidelines section in the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Auto**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | When you set the Spectrum Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration    |
        |              | for the spectrum measurement manually. When you set the Spectrum Meas Mode attribute to Measure, you can initiate the    |
        |              | spectrum measurement manually.                                                                                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Auto (1)     | When you set the Spectrum Noise Comp Enabled attribute to True, RFmx sets the Input Isolation Enabled attribute to       |
        |              | Enabled and calibrates the intrument noise in the current state of the instrument. RFmx then resets the Input Isolation  |
        |              | Enabled attribute and performs the spectrum measurement, including compensation for noise from the instrument. RFmx      |
        |              | skips noise calibration in this mode if valid noise calibration data is already cached. When you set the Spectrum Noise  |
        |              | Comp Enabled attribute to False, RFmx does not calibrate instrument noise and performs only the spectrum measurement     |
        |              | without compensating for the noise from the instrument.                                                                  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumNoiseCalibrationMode, int):
                Specifies whether the noise calibration and measurement is performed manually by the user or automatically by RFmx.
                Refer to the measurement guidelines section in the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumNoiseCalibrationMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_NOISE_CALIBRATION_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_calibration_averaging_auto(self, selector_string):
        r"""Gets whether RFmx automatically computes the averaging count used for instrument noise calibration.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+-------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                               |
        +==============+===========================================================================================+
        | False (0)    | RFmx uses the averages that you set for the Spectrum Noise Cal Averaging Count attribute. |
        +--------------+-------------------------------------------------------------------------------------------+
        | True (1)     | RFmx uses a noise calibration averaging count of 32.                                      |
        +--------------+-------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumNoiseCalibrationAveragingAuto):
                Specifies whether RFmx automatically computes the averaging count used for instrument noise calibration.

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
                attributes.AttributeID.SPECTRUM_NOISE_CALIBRATION_AVERAGING_AUTO.value,
            )
            attr_val = enums.SpectrumNoiseCalibrationAveragingAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_calibration_averaging_auto(self, selector_string, value):
        r"""Sets whether RFmx automatically computes the averaging count used for instrument noise calibration.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+-------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                               |
        +==============+===========================================================================================+
        | False (0)    | RFmx uses the averages that you set for the Spectrum Noise Cal Averaging Count attribute. |
        +--------------+-------------------------------------------------------------------------------------------+
        | True (1)     | RFmx uses a noise calibration averaging count of 32.                                      |
        +--------------+-------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumNoiseCalibrationAveragingAuto, int):
                Specifies whether RFmx automatically computes the averaging count used for instrument noise calibration.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = (
                value.value if type(value) is enums.SpectrumNoiseCalibrationAveragingAuto else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_NOISE_CALIBRATION_AVERAGING_AUTO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_calibration_averaging_count(self, selector_string):
        r"""Gets the averaging count used for noise calibration when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO`
        attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 32.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the averaging count used for noise calibration when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO`
                attribute to **False**.

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
                attributes.AttributeID.SPECTRUM_NOISE_CALIBRATION_AVERAGING_COUNT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_calibration_averaging_count(self, selector_string, value):
        r"""Sets the averaging count used for noise calibration when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO`
        attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 32.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the averaging count used for noise calibration when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO`
                attribute to **False**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_NOISE_CALIBRATION_AVERAGING_COUNT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_compensation_enabled(self, selector_string):
        r"""Gets whether RFmx compensates for the instrument noise while performing the measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the
        Spectrum Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
        **Measure**. Refer to the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        **Supported Devices:** PXIe-5663/5665/5668, PXIe-5830/5831/5832

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables compensation of the spectrum for the noise floor of the signal analyzer.                                        |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables compensation of the spectrum for the noise floor of the signal analyzer. The noise floor of the signal analyzer  |
        |              | is measured for the RF path used by the Spectrum measurement and cached for future use. If signal analyzer or            |
        |              | measurement parameters change, noise floors are measured again.                                                          |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumNoiseCompensationEnabled):
                Specifies whether RFmx compensates for the instrument noise while performing the measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the
                Spectrum Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
                **Measure**. Refer to the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

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
                attributes.AttributeID.SPECTRUM_NOISE_COMPENSATION_ENABLED.value,
            )
            attr_val = enums.SpectrumNoiseCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_compensation_enabled(self, selector_string, value):
        r"""Sets whether RFmx compensates for the instrument noise while performing the measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the
        Spectrum Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
        **Measure**. Refer to the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        **Supported Devices:** PXIe-5663/5665/5668, PXIe-5830/5831/5832

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables compensation of the spectrum for the noise floor of the signal analyzer.                                        |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables compensation of the spectrum for the noise floor of the signal analyzer. The noise floor of the signal analyzer  |
        |              | is measured for the RF path used by the Spectrum measurement and cached for future use. If signal analyzer or            |
        |              | measurement parameters change, noise floors are measured again.                                                          |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumNoiseCompensationEnabled, int):
                Specifies whether RFmx compensates for the instrument noise while performing the measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the
                Spectrum Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
                **Measure**. Refer to the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumNoiseCompensationEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_NOISE_COMPENSATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_compensation_type(self, selector_string):
        r"""Gets the noise compensation type. Refer to the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Analyzer and Termination**.

        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                 | Description                                                                                                              |
        +==============================+==========================================================================================================================+
        | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50 ohm termination. The measured power values are in excess of the       |
        |                              | thermal noise floor.                                                                                                     |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumNoiseCompensationType):
                Specifies the noise compensation type. Refer to the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

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
                attributes.AttributeID.SPECTRUM_NOISE_COMPENSATION_TYPE.value,
            )
            attr_val = enums.SpectrumNoiseCompensationType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_compensation_type(self, selector_string, value):
        r"""Sets the noise compensation type. Refer to the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Analyzer and Termination**.

        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                 | Description                                                                                                              |
        +==============================+==========================================================================================================================+
        | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50 ohm termination. The measured power values are in excess of the       |
        |                              | thermal noise floor.                                                                                                     |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumNoiseCompensationType, int):
                Specifies the noise compensation type. Refer to the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumNoiseCompensationType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_NOISE_COMPENSATION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the spectrum measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The spectrum measurement uses the Spectrum Averaging Count attribute as the number of acquisitions over which the        |
        |              | spectrum measurement is averaged.                                                                                        |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumAveragingEnabled):
                Specifies whether to enable averaging for the spectrum measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_AVERAGING_ENABLED.value
            )
            attr_val = enums.SpectrumAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the spectrum measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The spectrum measurement uses the Spectrum Averaging Count attribute as the number of acquisitions over which the        |
        |              | spectrum measurement is averaged.                                                                                        |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumAveragingEnabled, int):
                Specifies whether to enable averaging for the spectrum measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_AVERAGING_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_count(self, selector_string):
        r"""Gets the number of acquisitions used for averaging when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of acquisitions used for averaging when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_AVERAGING_COUNT.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_count(self, selector_string, value):
        r"""Sets the number of acquisitions used for averaging when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of acquisitions used for averaging when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_ENABLED` attribute to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_AVERAGING_COUNT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spectrum
        measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                 |
        +==============+=============================================================================================================+
        | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
        +--------------+-------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumAveragingType):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spectrum
                measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_AVERAGING_TYPE.value
            )
            attr_val = enums.SpectrumAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spectrum
        measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                 |
        +==============+=============================================================================================================+
        | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
        +--------------+-------------------------------------------------------------------------------------------------------------+
        | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
        +--------------+-------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumAveragingType, int):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spectrum
                measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_AVERAGING_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_mode(self, selector_string):
        r"""Gets whether the measurement calibrates the noise floor of analyzer or performs the spectrum measurement. Refer to
        the measurement guidelines section in the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------------------+--------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                |
        +===========================+============================================================================================+
        | Measure (0)               | Spectrum measurement is performed on the acquired signal.                                  |
        +---------------------------+--------------------------------------------------------------------------------------------+
        | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the spectrum measurement. |
        +---------------------------+--------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumMeasurementMode):
                Specifies whether the measurement calibrates the noise floor of analyzer or performs the spectrum measurement. Refer to
                the measurement guidelines section in the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_MEASUREMENT_MODE.value
            )
            attr_val = enums.SpectrumMeasurementMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_mode(self, selector_string, value):
        r"""Sets whether the measurement calibrates the noise floor of analyzer or performs the spectrum measurement. Refer to
        the measurement guidelines section in the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------------------+--------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                |
        +===========================+============================================================================================+
        | Measure (0)               | Spectrum measurement is performed on the acquired signal.                                  |
        +---------------------------+--------------------------------------------------------------------------------------------+
        | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the spectrum measurement. |
        +---------------------------+--------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumMeasurementMode, int):
                Specifies whether the measurement calibrates the noise floor of analyzer or performs the spectrum measurement. Refer to
                the measurement guidelines section in the `Noise Compensation Algorithm
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumMeasurementMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_MEASUREMENT_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_window(self, selector_string):
        r"""Gets the FFT window type to use to reduce spectral leakage.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Flat Top**.

        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)        | Description                                                                                                              |
        +=====================+==========================================================================================================================+
        | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
        |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
        |                     | better frequency resolution for noise measurements.                                                                      |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
        |                     | useful for time-frequency analysis.                                                                                      |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
        |                     | main lobe.                                                                                                               |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumFftWindow):
                Specifies the FFT window type to use to reduce spectral leakage.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_WINDOW.value
            )
            attr_val = enums.SpectrumFftWindow(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_window(self, selector_string, value):
        r"""Sets the FFT window type to use to reduce spectral leakage.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Flat Top**.

        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)        | Description                                                                                                              |
        +=====================+==========================================================================================================================+
        | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
        |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
        |                     | better frequency resolution for noise measurements.                                                                      |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. Hence, this windowing is   |
        |                     | useful for time-frequency analysis.                                                                                      |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
        |                     | main lobe.                                                                                                               |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumFftWindow, int):
                Specifies the FFT window type to use to reduce spectral leakage.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumFftWindow else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_WINDOW.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_padding(self, selector_string):
        r"""Gets the factor by which the time-domain waveform is zero-padded before FFT. The FFT size is given by the
        following formula:

        waveform size * padding

        This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
        device.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the factor by which the time-domain waveform is zero-padded before FFT. The FFT size is given by the
                following formula:

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_PADDING.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_padding(self, selector_string, value):
        r"""Sets the factor by which the time-domain waveform is zero-padded before FFT. The FFT size is given by the
        following formula:

        waveform size * padding

        This attribute is used only when the acquisition span is less than the device instantaneous bandwidth of the
        device.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the factor by which the time-domain waveform is zero-padded before FFT. The FFT size is given by the
                following formula:

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_PADDING.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_overlap_mode(self, selector_string):
        r"""Gets the overlap mode when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        attribute to **Sequential FFT**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Disabled**.

        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)     | Description                                                                                                              |
        +==================+==========================================================================================================================+
        | Disabled (0)     | Disables the overlap between the chunks.                                                                                 |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Automatic (1)    | Measurement sets the overlap based on the value you have set for the Spectrum FFT Window attribute. When you set the     |
        |                  | Spectrum FFT Window attribute to any value other than None, the number of overlapped samples between consecutive chunks  |
        |                  | is set to 50% of the value of the Spectrum Sequential FFT Size attribute. When you set the Spectrum FFT Window           |
        |                  | attribute to None, the chunks are not overlapped and the overlap is set to 0%.                                           |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | User Defined (2) | Measurement uses the overlap that you specify in the Spectrum FFT Overlap (%) attribute.                                 |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumFftOverlapMode):
                Specifies the overlap mode when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Sequential FFT**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_OVERLAP_MODE.value
            )
            attr_val = enums.SpectrumFftOverlapMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_overlap_mode(self, selector_string, value):
        r"""Sets the overlap mode when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        attribute to **Sequential FFT**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Disabled**.

        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)     | Description                                                                                                              |
        +==================+==========================================================================================================================+
        | Disabled (0)     | Disables the overlap between the chunks.                                                                                 |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Automatic (1)    | Measurement sets the overlap based on the value you have set for the Spectrum FFT Window attribute. When you set the     |
        |                  | Spectrum FFT Window attribute to any value other than None, the number of overlapped samples between consecutive chunks  |
        |                  | is set to 50% of the value of the Spectrum Sequential FFT Size attribute. When you set the Spectrum FFT Window           |
        |                  | attribute to None, the chunks are not overlapped and the overlap is set to 0%.                                           |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | User Defined (2) | Measurement uses the overlap that you specify in the Spectrum FFT Overlap (%) attribute.                                 |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumFftOverlapMode, int):
                Specifies the overlap mode when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Sequential FFT**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumFftOverlapMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_FFT_OVERLAP_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_overlap(self, selector_string):
        r"""Gets the samples to overlap between the consecutive chunks as a percentage of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT** and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute to **User Defined**. This value is expressed
        as a percentage.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the samples to overlap between the consecutive chunks as a percentage of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute to **User Defined**. This value is expressed
                as a percentage.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_OVERLAP.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_overlap(self, selector_string, value):
        r"""Sets the samples to overlap between the consecutive chunks as a percentage of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT** and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute to **User Defined**. This value is expressed
        as a percentage.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the samples to overlap between the consecutive chunks as a percentage of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.SEQUENTIAL_FFT_SIZE` attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FFT_OVERLAP_MODE` attribute to **User Defined**. This value is expressed
                as a percentage.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_OVERLAP.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_overlap_type(self, selector_string):
        r"""Gets the overlap type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        attribute to **Sequential FFT**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | RMS (0)      | Linear averaging of the FFTs taken over different chunks of data is performed. RMS averaging reduces signal              |
        |              | fluctuations but not the noise floor.                                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one chunk FFT to the next.                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumFftOverlapType):
                Specifies the overlap type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Sequential FFT**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_FFT_OVERLAP_TYPE.value
            )
            attr_val = enums.SpectrumFftOverlapType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_overlap_type(self, selector_string, value):
        r"""Sets the overlap type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        attribute to **Sequential FFT**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | RMS (0)      | Linear averaging of the FFTs taken over different chunks of data is performed. RMS averaging reduces signal              |
        |              | fluctuations but not the noise floor.                                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one chunk FFT to the next.                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumFftOverlapType, int):
                Specifies the overlap type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Sequential FFT**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumFftOverlapType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_FFT_OVERLAP_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_amplitude_correction_type(self, selector_string):
        r"""Gets whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
        at the RF center frequency, or at the individual frequency bins. Use the
        :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
        attenuation table.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RF Center Frequency**.

        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)               | Description                                                                                                              |
        +============================+==========================================================================================================================+
        | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
        |                            | RF center frequency.                                                                                                     |
        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
        |                            | frequency.                                                                                                               |
        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumAmplitudeCorrectionType):
                Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
                at the RF center frequency, or at the individual frequency bins. Use the
                :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
                attenuation table.

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
                attributes.AttributeID.SPECTRUM_AMPLITUDE_CORRECTION_TYPE.value,
            )
            attr_val = enums.SpectrumAmplitudeCorrectionType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_amplitude_correction_type(self, selector_string, value):
        r"""Sets whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
        at the RF center frequency, or at the individual frequency bins. Use the
        :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
        attenuation table.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RF Center Frequency**.

        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)               | Description                                                                                                              |
        +============================+==========================================================================================================================+
        | RF Center Frequency (0)    | All the frequency bins in the spectrum are compensated with a single external attenuation value that corresponds to the  |
        |                            | RF center frequency.                                                                                                     |
        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Spectrum Frequency Bin (1) | An individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
        |                            | frequency.                                                                                                               |
        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumAmplitudeCorrectionType, int):
                Specifies whether the amplitude of the frequency bins, used in the measurement, is corrected for external attenuation
                at the RF center frequency, or at the individual frequency bins. Use the
                :py:meth:`nirfmxinstr.session.Session.configure_external_attenuation_table` method to configure the external
                attenuation table.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumAmplitudeCorrectionType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_AMPLITUDE_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_method(self, selector_string):
        r"""Gets the method for performing the Spectrum measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Normal**.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | Normal (0)         | The Spectrum measurement acquires the spectrum using the same signal analyzer setting across frequency bands.            |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sequential FFT (2) | The Spectrum measurement acquires I/Q samples for a duration specified by the Spectrum Sweep Time attribute. These       |
        |                    | samples are divided into smaller chunks. If the attribute Spectrum RBW Auto is True, The size of each chunk is defined   |
        |                    | by the Spectrum Sequential FFT Size attribute. If the attribute Spectrum RBW Auto is False, the Spectrum Sequential FFT  |
        |                    | Size                                                                                                                     |
        |                    | is auto computed based on the configured Spectrum RBW. The overlap between the chunks is defined by the Spectrum FFT     |
        |                    | Overlap Mode attribute. FFT is computed on each of these chunks. The resultant FFTs are averaged as per the configured   |
        |                    | averaging type in the attribute Spectrum FFT Overlap Typeto get the spectrum.                                            |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumMeasurementMethod):
                Specifies the method for performing the Spectrum measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_MEASUREMENT_METHOD.value
            )
            attr_val = enums.SpectrumMeasurementMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_method(self, selector_string, value):
        r"""Sets the method for performing the Spectrum measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Normal**.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | Normal (0)         | The Spectrum measurement acquires the spectrum using the same signal analyzer setting across frequency bands.            |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sequential FFT (2) | The Spectrum measurement acquires I/Q samples for a duration specified by the Spectrum Sweep Time attribute. These       |
        |                    | samples are divided into smaller chunks. If the attribute Spectrum RBW Auto is True, The size of each chunk is defined   |
        |                    | by the Spectrum Sequential FFT Size attribute. If the attribute Spectrum RBW Auto is False, the Spectrum Sequential FFT  |
        |                    | Size                                                                                                                     |
        |                    | is auto computed based on the configured Spectrum RBW. The overlap between the chunks is defined by the Spectrum FFT     |
        |                    | Overlap Mode attribute. FFT is computed on each of these chunks. The resultant FFTs are averaged as per the configured   |
        |                    | averaging type in the attribute Spectrum FFT Overlap Typeto get the spectrum.                                            |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumMeasurementMethod, int):
                Specifies the method for performing the Spectrum measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumMeasurementMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_MEASUREMENT_METHOD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_sequential_fft_size(self, selector_string):
        r"""Gets the FFT size when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**. If the
        attribute :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` is False, FFT Size is auto computed
        based on the configured :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH`

        The default value is 512.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the FFT size when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**. If the
                attribute :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` is False, FFT Size is auto computed
                based on the configured :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH`

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_SEQUENTIAL_FFT_SIZE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_sequential_fft_size(self, selector_string, value):
        r"""Sets the FFT size when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**. If the
        attribute :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` is False, FFT Size is auto computed
        based on the configured :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH`

        The default value is 512.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the FFT size when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**. If the
                attribute :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_AUTO_BANDWIDTH` is False, FFT Size is auto computed
                based on the configured :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH`

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_SEQUENTIAL_FFT_SIZE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_analysis_input(self, selector_string):
        r"""Gets whether to analyze just the real I or Q component of the acquired IQ data, or analyze the complex IQ data.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **IQ**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | IQ (0)       | Measurement analyzes the acquired I+jQ data, resulting generally in a spectrum that is not symmetric around 0 Hz.        |
        |              | Spectrum trace result contains both positive and negative frequencies. Since the RMS power of the complex envelope is    |
        |              | 3.01 dB higher than that of its equivalent real RF signal, the spectrum trace result of the acquired I+jQ data is        |
        |              | scaled by -3.01 dB.                                                                                                      |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | I Only (1)   | Measurement ignores the Q data from the acquired I+jQ data and analyzes I+j0, resulting in a spectrum that is symmetric  |
        |              | around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of I+j0 data is scaled by +3.01 dB to    |
        |              | account for the power of the negative frequencies that are not returned in the spectrum trace.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Q Only (2)   | Measurement ignores the I data from the acquired I+jQ data and analyzes Q+j0, resulting in a spectrum that is symmetric  |
        |              | around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of Q+j0 data is scaled by +3.01 dB to    |
        |              | account for the power of the negative frequencies that are not returned in the spectrum trace.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpectrumAnalysisInput):
                Specifies whether to analyze just the real I or Q component of the acquired IQ data, or analyze the complex IQ data.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_ANALYSIS_INPUT.value
            )
            attr_val = enums.SpectrumAnalysisInput(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_analysis_input(self, selector_string, value):
        r"""Sets whether to analyze just the real I or Q component of the acquired IQ data, or analyze the complex IQ data.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **IQ**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | IQ (0)       | Measurement analyzes the acquired I+jQ data, resulting generally in a spectrum that is not symmetric around 0 Hz.        |
        |              | Spectrum trace result contains both positive and negative frequencies. Since the RMS power of the complex envelope is    |
        |              | 3.01 dB higher than that of its equivalent real RF signal, the spectrum trace result of the acquired I+jQ data is        |
        |              | scaled by -3.01 dB.                                                                                                      |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | I Only (1)   | Measurement ignores the Q data from the acquired I+jQ data and analyzes I+j0, resulting in a spectrum that is symmetric  |
        |              | around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of I+j0 data is scaled by +3.01 dB to    |
        |              | account for the power of the negative frequencies that are not returned in the spectrum trace.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Q Only (2)   | Measurement ignores the I data from the acquired I+jQ data and analyzes Q+j0, resulting in a spectrum that is symmetric  |
        |              | around 0 Hz. Spectrum trace result contains positive frequencies only. Spectrum of Q+j0 data is scaled by +3.01 dB to    |
        |              | account for the power of the negative frequencies that are not returned in the spectrum trace.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpectrumAnalysisInput, int):
                Specifies whether to analyze just the real I or Q component of the acquired IQ data, or analyze the complex IQ data.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpectrumAnalysisInput else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPECTRUM_ANALYSIS_INPUT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for spectrum measurement.

        The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
        be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum number of threads used for parallelism for spectrum measurement.

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
                attributes.AttributeID.SPECTRUM_NUMBER_OF_ANALYSIS_THREADS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for spectrum measurement.

        The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
        be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of threads used for parallelism for spectrum measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPECTRUM_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the spectrum measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.SpectrumAveragingEnabled, int):
                This parameter specifies whether to enable averaging for the measurement. The default value is **False**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | The measurement is performed on a single acquisition.                                                                    |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement uses the value of the Averaging Count parameter to calculate the number of acquisitions over which the   |
                |              | measurement is averaged.                                                                                                 |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            averaging_count (int):
                This parameter specifies the number of acquisitions used for averaging when you set the **Averaging Enabled** parameter
                to **True**. The default value is 10.

            averaging_type (enums.SpectrumAveragingType, int):
                This parameter specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used
                for the measurement. Refer to the Averaging section of the `Spectral Measurements Concepts
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information about
                averaging types. The default value is **RMS**.

                +--------------+-------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                 |
                +==============+=============================================================================================================+
                | RMS (0)      | The power spectrum is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
                +--------------+-------------------------------------------------------------------------------------------------------------+
                | Log (1)      | The power spectrum is averaged in a logarithmic scale.                                                      |
                +--------------+-------------------------------------------------------------------------------------------------------------+
                | Scalar (2)   | The square root of the power spectrum is averaged.                                                          |
                +--------------+-------------------------------------------------------------------------------------------------------------+
                | Max (3)      | The peak power in the spectrum at each frequency bin is retained from one acquisition to the next.          |
                +--------------+-------------------------------------------------------------------------------------------------------------+
                | Min (4)      | The least power in the spectrum at each frequency bin is retained from one acquisition to the next.         |
                +--------------+-------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            averaging_enabled = (
                averaging_enabled.value
                if type(averaging_enabled) is enums.SpectrumAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.SpectrumAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_detector(self, selector_string, detector_type, detector_points):
        r"""Configures the detector settings, including detector type and the number of points to be detected.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            detector_type (enums.SpectrumDetectorType, int):
                This parameter specifies the type of detector to be used. The default value is **None**. Refer to `Spectral
                Measurements Concepts <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for
                more information on detectors.

                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)        | Description                                                                                                              |
                +=====================+==========================================================================================================================+
                | None (0)            | The detector is disabled.                                                                                                |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Sample (1)          | The middle sample in the bucket is detected.                                                                             |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Normal (2)          | The maximum value of the samples within the bucket is detected if the signal only rises or if the signal only falls. If  |
                |                     | the signal, within a bucket, both rises and falls, then the maximum and minimum values of the samples are detected in    |
                |                     | alternate buckets.                                                                                                       |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Peak (3)            | The maximum value of the samples in the bucket is detected.                                                              |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Negative Peak (4)   | The minimum value of the samples in the bucket is detected.                                                              |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Average RMS (5)     | The average RMS of all the samples in the bucket is detected.                                                            |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Average Voltage (6) | The average voltage of all the samples in the bucket is detected.                                                        |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Average Log (7)     | The average log of all the samples in the bucket is detected.                                                            |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+

            detector_points (int):
                This parameter specifies the number of points after the detector is applied. The default value is 1001.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            detector_type = (
                detector_type.value
                if type(detector_type) is enums.SpectrumDetectorType
                else detector_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_detector(
                updated_selector_string, detector_type, detector_points
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fft(self, selector_string, fft_window, fft_padding):
        r"""Configures window and FFT to obtain a spectrum for the spectrum measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            fft_window (enums.SpectrumFftWindow, int):
                This parameter specifies the FFT window type to use to reduce spectral leakage. Refer to the Window and FFT section of
                the `Spectral Measurements Concepts
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information about
                FFT window types. The default value is **Flat Top**.

                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)        | Description                                                                                                              |
                +=====================+==========================================================================================================================+
                | None (0)            | Analyzes transients for which duration is shorter than the window length. You can also use this window type to separate  |
                |                     | two tones with frequencies close to each other but with almost equal amplitudes.                                         |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Flat Top (1)        | Measures single-tone amplitudes accurately.                                                                              |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Hanning (2)         | Analyzes transients for which duration is longer than the window length. You can also use this window type to provide    |
                |                     | better frequency resolution for noise measurements.                                                                      |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Hamming (3)         | Analyzes closely-spaced sine waves.                                                                                      |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Gaussian (4)        | Provides a balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful for    |
                |                     | time-frequency analysis.                                                                                                 |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Blackman-Harris (6) | Useful as a general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide main      |
                |                     | lobe.                                                                                                                    |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+

            fft_padding (float):
                This parameter specifies the factor by which the time-domain waveform is zero-padded before an FFT. The FFT size is
                given by the following formula: *FFT size* = *waveform size* * *padding*. This parameter is used only when the
                acquisition span is less than the device instantaneous bandwidth. The default value is -1.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            fft_window = (
                fft_window.value if type(fft_window) is enums.SpectrumFftWindow else fft_window
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_fft(
                updated_selector_string, fft_window, fft_padding
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency_start_stop(self, selector_string, start_frequency, stop_frequency):
        r"""Configures the start frequency and stop frequency for the spectrum measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            start_frequency (float):
                This parameter specifies the start frequency, in Hz, for the spectrum measurement. The default value is 995 MHz.

            stop_frequency (float):
                This parameter specifies the stop frequency, in Hz, for the spectrum measurement. The default value is 1.005 GHz.

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
            error_code = self._interpreter.spectrum_configure_frequency_start_stop(
                updated_selector_string, start_frequency, stop_frequency
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_noise_compensation_enabled(self, selector_string, noise_compensation_enabled):
        r"""Configures compensation of the spectrum for the inherent noise floor of the signal analyzer.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            noise_compensation_enabled (enums.SpectrumNoiseCompensationEnabled, int):
                This parameter specifies whether to enable compensation of the spectrum for the inherent noise floor of the signal
                analyzer. The default value is **False**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Disables compensation of the spectrum for the noise floor of the signal analyzer.                                        |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Enables compensation of the spectrum for the noise floor of the signal analyzer. The noise floor of the signal analyzer  |
                |              | is measured for the RF path used by the Spectrum measurement and cached for future use. If signal analyzer or            |
                |              | measurement parameters change, noise floors are measured again.                                                          |
                |              | Supported Devices: PXIe-5663/5665/5668, PXIe-5830/5831/5832                                                              |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            noise_compensation_enabled = (
                noise_compensation_enabled.value
                if type(noise_compensation_enabled) is enums.SpectrumNoiseCompensationEnabled
                else noise_compensation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_noise_compensation_enabled(
                updated_selector_string, noise_compensation_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_power_units(self, selector_string, spectrum_power_units):
        r"""Configures the units for the absolute power.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            spectrum_power_units (enums.SpectrumPowerUnits, int):
                This parameter specifies the units for the absolute power. The default value is **dBm**.

                +-------------------+---------------------------------------------+
                | Name (Value)      | Description                                 |
                +===================+=============================================+
                | dBm (0)           | The absolute powers are reported in dBm.    |
                +-------------------+---------------------------------------------+
                | dBm/Hz (1)        | The absolute powers are reported in dBm/Hz. |
                +-------------------+---------------------------------------------+
                | dBW (2)           | The absolute powers are reported in dBW.    |
                +-------------------+---------------------------------------------+
                | dBV (3)           | The absolute powers are reported in dBV.    |
                +-------------------+---------------------------------------------+
                | dBmV (4)          | The absolute powers are reported in dBmV.   |
                +-------------------+---------------------------------------------+
                | dBuV (5)          | The absolute powers are reported in dBuV.   |
                +-------------------+---------------------------------------------+
                | W (6)             | The absolute powers are reported in W.      |
                +-------------------+---------------------------------------------+
                | Volts (7)         | The absolute powers are reported in volts.  |
                +-------------------+---------------------------------------------+
                | Volts Squared (8) | The absolute powers are reported in volts2. |
                +-------------------+---------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            spectrum_power_units = (
                spectrum_power_units.value
                if type(spectrum_power_units) is enums.SpectrumPowerUnits
                else spectrum_power_units
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_power_units(
                updated_selector_string, spectrum_power_units
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the resolution bandwidth (RBW) filter.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw_auto (enums.SpectrumRbwAutoBandwidth, int):
                This parameter specifies whether the measurement computes the RBW. Refer to the RBW and Sweep Time section in the
                `Spectral Measurements Concepts <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_
                topic for more details on RBW and sweep time. The default value is **True**.

                +--------------+---------------------------------------------------------------------+
                | Name (Value) | Description                                                         |
                +==============+=====================================================================+
                | False (0)    | The measurement uses the RBW that you specify in the RBW parameter. |
                +--------------+---------------------------------------------------------------------+
                | True (1)     | The measurement computes the RBW.                                   |
                +--------------+---------------------------------------------------------------------+

            rbw (float):
                This parameter specifies the bandwidth of the RBW filter used to sweep the acquired signal, when you set the **RBW
                Auto** parameter to **False**. This value is expressed in Hz. The default value is 10 kHz.

            rbw_filter_type (enums.SpectrumRbwFilterType, int):
                This parameter specifies the response of the digital RBW filter. The default value is **Gaussian**.

                +---------------+----------------------------------------------------+
                | Name (Value)  | Description                                        |
                +===============+====================================================+
                | FFT Based (0) | No RBW filtering is performed.                     |
                +---------------+----------------------------------------------------+
                | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
                +---------------+----------------------------------------------------+
                | Flat (2)      | An RBW filter with a flat response is applied.     |
                +---------------+----------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            rbw_auto = (
                rbw_auto.value if type(rbw_auto) is enums.SpectrumRbwAutoBandwidth else rbw_auto
            )
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.SpectrumRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_rbw_filter(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_span(self, selector_string, span):
        r"""Configures the frequency range, in Hz, around the center frequency, to acquire for the spectrum measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            span (float):
                This parameter specifies the frequency range, in Hz, around the center frequency, to acquire for the measurement.	The
                default value is 1 MHz.

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
            error_code = self._interpreter.spectrum_configure_span(updated_selector_string, span)
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        r"""Configures the sweep time.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            sweep_time_auto (enums.SpectrumSweepTimeAuto, int):
                This parameter specifies whether the measurement computes the sweep time. The default value is **True**.

                +--------------+---------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                 |
                +==============+=============================================================================================+
                | False (0)    | The measurement uses the sweep time that you specify in the Sweep Time Interval parameter.  |
                +--------------+---------------------------------------------------------------------------------------------+
                | True (1)     | The measurement calculates the sweep time based on the value of the Spectrum RBW attribute. |
                +--------------+---------------------------------------------------------------------------------------------+

            sweep_time_interval (float):
                This parameter specifies the sweep time, in seconds, when you set the **Sweep Time Auto** parameter to **False**. The
                default value is 1 ms.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            sweep_time_auto = (
                sweep_time_auto.value
                if type(sweep_time_auto) is enums.SpectrumSweepTimeAuto
                else sweep_time_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_sweep_time(
                updated_selector_string, sweep_time_auto, sweep_time_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_vbw_filter(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        r"""Configures the VBW settings including VBW Auto, VBW(Hz) and VBW to RBW ratio.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            vbw_auto (enums.SpectrumVbwFilterAutoBandwidth, int):
                This parameter specifies whether the VBW is expressed directly or computed based on VBW to RBW ratio. This value is
                expressed in Hz. The default value is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Specify the video bandwidth in the VBW parameter. The VBW to RBW Ratio parameter is disregarded in this mode.            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
                |              | the Spectrum VBW to RBW Ratio attribute and the Spectrum RBW attribute. The value of the VBW parameter is disregarded    |
                |              | in this mode.                                                                                                            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            vbw (float):
                This parameter specifies the video bandwidth when you set the **VBW Auto** parameter **False**. This value is expressed
                in Hz. The default value is 30KHz.

            vbw_to_rbw_ratio (float):
                This parameter specifies the VBW to RBW Ratio when you set the **VBW Auto** parameter to **True**. The default value is
                3.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            vbw_auto = (
                vbw_auto.value
                if type(vbw_auto) is enums.SpectrumVbwFilterAutoBandwidth
                else vbw_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_vbw_filter(
                updated_selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def validate_noise_calibration_data(self, selector_string):
        r"""Indicates whether calibration data is valid for the configuration specified by the signal name in the **Selector
        string** parameter.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            Tuple (noise_calibration_data_valid, error_code):

            noise_calibration_data_valid (enums.SpectrumNoiseCalibrationDataValid):
                This parameter returns whether the calibration data is valid.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Returns false if the calibration data is not present for the specified configuration or if the difference between the    |
                |              | current device temperature and the calibration temperature exceeds the [-5 °C, 5 °C] range.                              |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Returns true if the calibration data is present for the configuration specified by the signal name in the Selector       |
                |              | string parameter.                                                                                                        |
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
            noise_calibration_data_valid, error_code = (
                self._interpreter.spectrum_validate_noise_calibration_data(updated_selector_string)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return noise_calibration_data_valid, error_code

    @_raise_if_disposed
    def configure_measurement_method(self, selector_string, measurement_method):
        r"""Configures the method for performing the Spectrum measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_method (enums.SpectrumMeasurementMethod, int):
                This parameter specifies the method for performing the Spectrum measurement. The default value is **Normal**.

                +--------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)       | Description                                                                                                              |
                +====================+==========================================================================================================================+
                | Normal (0)         | The Spectrum measurement acquires the spectrum with the same signal analyzer setting across frequency bands.             |
                +--------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Sequential FFT (2) | The Spectrum measurement acquires I/Q samples for a duration specified by the Spectrum Sweep Time attribute. These       |
                |                    | samples are divided into smaller chunks. If the attribute                                                                |
                |                    | Spectrum RBW Auto is True, the size of each chunk is defined by the Spectrum Sequential FFT Size attribute. If the       |
                |                    | attribute                                                                                                                |
                |                    | Spectrum RBW Auto is False, the Spectrum Sequential FFT Size is auto computed based on the configured                    |
                |                    | Spectrum RBW . The overlap between the chunks is defined by the Spectrum FFT Overlap Mode attribute. FFT is computed on  |
                |                    | each of these chunks. The resultant FFTs are averaged as per the configured averaging type in the attribute              |
                |                    | Spectrum FFT Overlap Typeto get the spectrum.                                                                            |
                +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            measurement_method = (
                measurement_method.value
                if type(measurement_method) is enums.SpectrumMeasurementMethod
                else measurement_method
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spectrum_configure_measurement_method(
                updated_selector_string, measurement_method
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
