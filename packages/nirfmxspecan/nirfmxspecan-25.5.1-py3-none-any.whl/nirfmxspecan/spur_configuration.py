"""Provides methods to configure the Spur measurement."""

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


class SpurConfiguration(object):
    """Provides methods to configure the Spur measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Spur measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the spurious emission (Spur) measurement.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        The default value is FALSE.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable the spurious emission (Spur) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the spurious emission (Spur) measurement.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        The default value is FALSE.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the spurious emission (Spur) measurement.

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
                attributes.AttributeID.SPUR_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_ranges(self, selector_string):
        r"""Gets the number of ranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of ranges.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_NUMBER_OF_RANGES.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_ranges(self, selector_string, value):
        r"""Sets the number of ranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of ranges.

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
                updated_selector_string, attributes.AttributeID.SPUR_NUMBER_OF_RANGES.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_enabled(self, selector_string):
        r"""Gets whether to measure the spurious emissions (Spur) in the frequency range.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+------------------------------------------------------+
        | Name (Value) | Description                                          |
        +==============+======================================================+
        | False (0)    | Disables the acquisition of the frequency range.     |
        +--------------+------------------------------------------------------+
        | True (1)     | Enables measurement of Spurs in the frequency range. |
        +--------------+------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurRangeEnabled):
                Specifies whether to measure the spurious emissions (Spur) in the frequency range.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_ENABLED.value
            )
            attr_val = enums.SpurRangeEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_enabled(self, selector_string, value):
        r"""Sets whether to measure the spurious emissions (Spur) in the frequency range.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+------------------------------------------------------+
        | Name (Value) | Description                                          |
        +==============+======================================================+
        | False (0)    | Disables the acquisition of the frequency range.     |
        +--------------+------------------------------------------------------+
        | True (1)     | Enables measurement of Spurs in the frequency range. |
        +--------------+------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurRangeEnabled, int):
                Specifies whether to measure the spurious emissions (Spur) in the frequency range.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpurRangeEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_start_frequency(self, selector_string):
        r"""Gets the start of the frequency range for the measurement. This value is expressed in Hz.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 500 MHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start of the frequency range for the measurement. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_START_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_start_frequency(self, selector_string, value):
        r"""Sets the start of the frequency range for the measurement. This value is expressed in Hz.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 500 MHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start of the frequency range for the measurement. This value is expressed in Hz.

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
                attributes.AttributeID.SPUR_RANGE_START_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_stop_frequency(self, selector_string):
        r"""Gets the stop of the frequency range for the measurement. This value is expressed in Hz.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1.5 GHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the stop of the frequency range for the measurement. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_STOP_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_stop_frequency(self, selector_string, value):
        r"""Sets the stop of the frequency range for the measurement. This value is expressed in Hz.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1.5 GHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the stop of the frequency range for the measurement. This value is expressed in Hz.

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
                attributes.AttributeID.SPUR_RANGE_STOP_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_rbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the measurement computes the resolution bandwidth (RBW).

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                    |
        +==============+================================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the Spur Range RBW attribute. |
        +--------------+--------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                              |
        +--------------+--------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurRbwAutoBandwidth):
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
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_AUTO_BANDWIDTH.value,
            )
            attr_val = enums.SpurRbwAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_rbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the measurement computes the resolution bandwidth (RBW).

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                    |
        +==============+================================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the Spur Range RBW attribute. |
        +--------------+--------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                              |
        +--------------+--------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurRbwAutoBandwidth, int):
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
            value = value.value if type(value) is enums.SpurRbwAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False.**

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10 kHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False.**

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
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False.**

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10 kHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired signal, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False.**

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
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_rbw_filter_type(self, selector_string):
        r"""Gets the shape of the digital resolution bandwidth (RBW) filter.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Gaussian**.

        **Supported devices**: PXIe-5665/5668

        +---------------+----------------------------------------------------+
        | Name (Value)  | Description                                        |
        +===============+====================================================+
        | FFT Based (0) | No RBW filtering is performed.                     |
        +---------------+----------------------------------------------------+
        | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
        +---------------+----------------------------------------------------+
        | Flat (2)      | An RBW filter with a flat response is applied.     |
        +---------------+----------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurRbwFilterType):
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
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_RBW_FILTER_TYPE.value
            )
            attr_val = enums.SpurRbwFilterType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_rbw_filter_type(self, selector_string, value):
        r"""Sets the shape of the digital resolution bandwidth (RBW) filter.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Gaussian**.

        **Supported devices**: PXIe-5665/5668

        +---------------+----------------------------------------------------+
        | Name (Value)  | Description                                        |
        +===============+====================================================+
        | FFT Based (0) | No RBW filtering is performed.                     |
        +---------------+----------------------------------------------------+
        | Gaussian (1)  | An RBW filter with a Gaussian response is applied. |
        +---------------+----------------------------------------------------+
        | Flat (2)      | An RBW filter with a flat response is applied.     |
        +---------------+----------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurRbwFilterType, int):
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
            value = value.value if type(value) is enums.SpurRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_rbw_filter_bandwidth_definition(self, selector_string):
        r"""Gets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the Spur Range RBW Filter Type attribute   |
        |               | to FFT Based, RBW is the 3dB bandwidth of the window specified by the Spur FFT Window attribute.                         |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spur Range RBW Filter Type        |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | ENBW (3)      | Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spur                                  |
        |               | RBW Filter Type attribute to FFT Based, RBW is the ENBW                                                                  |
        |               | bandwidth of the window specified by the Spur FFT Window attribute.                                                      |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurRbwFilterBandwidthDefinition):
                Specifies the bandwidth definition which you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute.

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
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_BANDWIDTH_DEFINITION.value,
            )
            attr_val = enums.SpurRbwFilterBandwidthDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_rbw_filter_bandwidth_definition(self, selector_string, value):
        r"""Sets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the Spur Range RBW Filter Type attribute   |
        |               | to FFT Based, RBW is the 3dB bandwidth of the window specified by the Spur FFT Window attribute.                         |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the Spur Range RBW Filter Type        |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | ENBW (3)      | Defines the RBW in terms of the ENBW bandwidth of the RBW filter. When you set the Spur                                  |
        |               | RBW Filter Type attribute to FFT Based, RBW is the ENBW                                                                  |
        |               | bandwidth of the window specified by the Spur FFT Window attribute.                                                      |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurRbwFilterBandwidthDefinition, int):
                Specifies the bandwidth definition which you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_RBW_FILTER_BANDWIDTH` attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpurRbwFilterBandwidthDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_RBW_FILTER_BANDWIDTH_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_vbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Specify the video bandwidth in the                                                                                       |
        |              | Spur Range VBW                                                                                                           |
        |              | attribute. The Spur VBW to RBW Ratio attribute is disregarded in this mode.                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
        |              | the Spur Range VBW to RBW Ratio attribute and the Spur Range RBW attribute. The value of the Spur Range VBW attribute    |
        |              | is disregarded in this mode.                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurRangeVbwFilterAutoBandwidth):
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
                attributes.AttributeID.SPUR_RANGE_VBW_FILTER_AUTO_BANDWIDTH.value,
            )
            attr_val = enums.SpurRangeVbwFilterAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_vbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the video bandwidth (VBW) is expressed directly or computed based on the VBW to RBW ratio.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Specify the video bandwidth in the                                                                                       |
        |              | Spur Range VBW                                                                                                           |
        |              | attribute. The Spur VBW to RBW Ratio attribute is disregarded in this mode.                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
        |              | the Spur Range VBW to RBW Ratio attribute and the Spur Range RBW attribute. The value of the Spur Range VBW attribute    |
        |              | is disregarded in this mode.                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurRangeVbwFilterAutoBandwidth, int):
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
            value = value.value if type(value) is enums.SpurRangeVbwFilterAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_VBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_vbw_filter_bandwidth(self, selector_string):
        r"""Gets the video bandwidth (VBW) in Hz when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 30000.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the video bandwidth (VBW) in Hz when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

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
                attributes.AttributeID.SPUR_RANGE_VBW_FILTER_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_vbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the video bandwidth (VBW) in Hz when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 30000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the video bandwidth (VBW) in Hz when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

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
                attributes.AttributeID.SPUR_RANGE_VBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_vbw_filter_vbw_to_rbw_ratio(self, selector_string):
        r"""Gets the VBW to RBW Ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the VBW to RBW Ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

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
                attributes.AttributeID.SPUR_RANGE_VBW_FILTER_VBW_TO_RBW_RATIO.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_vbw_filter_vbw_to_rbw_ratio(self, selector_string, value):
        r"""Sets the VBW to RBW Ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the VBW to RBW Ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

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
                attributes.AttributeID.SPUR_RANGE_VBW_FILTER_VBW_TO_RBW_RATIO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_sweep_time_auto(self, selector_string):
        r"""Gets whether the measurement computes the sweep time.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+-----------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                   |
        +==============+===============================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the Spur Range Sweep Time attribute.  |
        +--------------+-----------------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the Spur Range RBW attribute. |
        +--------------+-----------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurSweepTimeAuto):
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
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_SWEEP_TIME_AUTO.value
            )
            attr_val = enums.SpurSweepTimeAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_sweep_time_auto(self, selector_string, value):
        r"""Sets whether the measurement computes the sweep time.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+-----------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                   |
        +==============+===============================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the Spur Range Sweep Time attribute.  |
        +--------------+-----------------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the Spur Range RBW attribute. |
        +--------------+-----------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurSweepTimeAuto, int):
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
            value = value.value if type(value) is enums.SpurSweepTimeAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_SWEEP_TIME_AUTO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_sweep_time_interval(self, selector_string):
        r"""Gets the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SWEEP_TIME_AUTO`
        attribute to **False**. This value is expressed in seconds.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.001.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SWEEP_TIME_AUTO`
                attribute to **False**. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_SWEEP_TIME_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_sweep_time_interval(self, selector_string, value):
        r"""Sets the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SWEEP_TIME_AUTO`
        attribute to **False**. This value is expressed in seconds.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.001.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the sweep time when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_SWEEP_TIME_AUTO`
                attribute to **False**. This value is expressed in seconds.

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
                attributes.AttributeID.SPUR_RANGE_SWEEP_TIME_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_detector_type(self, selector_string):
        r"""Gets the type of detector to be used.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        Refer to `Spectral Measurements Concepts
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
        detector types.

        The default value is **None**.

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

            attr_val (enums.SpurRangeDetectorType):
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
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_DETECTOR_TYPE.value
            )
            attr_val = enums.SpurRangeDetectorType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_detector_type(self, selector_string, value):
        r"""Sets the type of detector to be used.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        Refer to `Spectral Measurements Concepts
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
        detector types.

        The default value is **None**.

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

            value (enums.SpurRangeDetectorType, int):
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
            value = value.value if type(value) is enums.SpurRangeDetectorType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_DETECTOR_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_detector_points(self, selector_string):
        r"""Gets the number of range points after the detector is applied.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1001.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of range points after the detector is applied.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_DETECTOR_POINTS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_detector_points(self, selector_string, value):
        r"""Sets the number of range points after the detector is applied.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of range points after the detector is applied.

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
                attributes.AttributeID.SPUR_RANGE_DETECTOR_POINTS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_absolute_limit_mode(self, selector_string):
        r"""Gets whether the absolute limit threshold is a flat line or a line with a slope.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Couple**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | The line specified by the Spur Range Abs Limit Start and Spur Range Abs Limit Stop attribute                             |
        |              | values as the two ends is considered as the threshold.                                                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Couple (1)   | The two ends of the line are coupled to the value of the Spur Range Abs Limit Start attribute.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurAbsoluteLimitMode):
                Specifies whether the absolute limit threshold is a flat line or a line with a slope.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_ABSOLUTE_LIMIT_MODE.value
            )
            attr_val = enums.SpurAbsoluteLimitMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_absolute_limit_mode(self, selector_string, value):
        r"""Sets whether the absolute limit threshold is a flat line or a line with a slope.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Couple**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | The line specified by the Spur Range Abs Limit Start and Spur Range Abs Limit Stop attribute                             |
        |              | values as the two ends is considered as the threshold.                                                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Couple (1)   | The two ends of the line are coupled to the value of the Spur Range Abs Limit Start attribute.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurAbsoluteLimitMode, int):
                Specifies whether the absolute limit threshold is a flat line or a line with a slope.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpurAbsoluteLimitMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_RANGE_ABSOLUTE_LIMIT_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_absolute_limit_start(self, selector_string):
        r"""Gets the absolute power limit corresponding to the beginning of the frequency range. This value is expressed in
        dBm. This power limit is also set as the absolute power limit for the range when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the absolute power limit corresponding to the beginning of the frequency range. This value is expressed in
                dBm. This power limit is also set as the absolute power limit for the range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SPUR_RANGE_ABSOLUTE_LIMIT_START.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_absolute_limit_start(self, selector_string, value):
        r"""Sets the absolute power limit corresponding to the beginning of the frequency range. This value is expressed in
        dBm. This power limit is also set as the absolute power limit for the range when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the absolute power limit corresponding to the beginning of the frequency range. This value is expressed in
                dBm. This power limit is also set as the absolute power limit for the range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SPUR_RANGE_ABSOLUTE_LIMIT_START.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_absolute_limit_stop(self, selector_string):
        r"""Gets the absolute power limit corresponding to the end of the frequency range. This value is expressed in dBm. The
        measurement ignores this attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the absolute power limit corresponding to the end of the frequency range. This value is expressed in dBm. The
                measurement ignores this attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_ABSOLUTE_LIMIT_STOP.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_absolute_limit_stop(self, selector_string, value):
        r"""Sets the absolute power limit corresponding to the end of the frequency range. This value is expressed in dBm. The
        measurement ignores this attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the absolute power limit corresponding to the end of the frequency range. This value is expressed in dBm. The
                measurement ignores this attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SPUR_RANGE_ABSOLUTE_LIMIT_STOP.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_relative_attenuation(self, selector_string):
        r"""Gets the attenuation relative to the external attenuation specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
        Spur Range Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
        wide in frequency.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the attenuation relative to the external attenuation specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
                Spur Range Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
                wide in frequency.

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
                attributes.AttributeID.SPUR_RANGE_RELATIVE_ATTENUATION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_relative_attenuation(self, selector_string, value):
        r"""Sets the attenuation relative to the external attenuation specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
        Spur Range Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
        wide in frequency.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the attenuation relative to the external attenuation specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
                Spur Range Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
                wide in frequency.

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
                attributes.AttributeID.SPUR_RANGE_RELATIVE_ATTENUATION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_peak_threshold(self, selector_string):
        r"""Gets the threshold level above which the measurement detects spurs in the range that you specify using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attributes. This value is expressed in dBm.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -200.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the threshold level above which the measurement detects spurs in the range that you specify using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attributes. This value is expressed in dBm.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_PEAK_THRESHOLD.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_peak_threshold(self, selector_string, value):
        r"""Sets the threshold level above which the measurement detects spurs in the range that you specify using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attributes. This value is expressed in dBm.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -200.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the threshold level above which the measurement detects spurs in the range that you specify using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_STOP_FREQUENCY` attributes. This value is expressed in dBm.

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
                attributes.AttributeID.SPUR_RANGE_PEAK_THRESHOLD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_peak_excursion(self, selector_string):
        r"""Gets the peak excursion value used to find the spurs in the spectrum. This value is expressed in dB. The signal
        should rise and fall by at least the peak excursion value, above the threshold, to be considered a spur.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the peak excursion value used to find the spurs in the spectrum. This value is expressed in dB. The signal
                should rise and fall by at least the peak excursion value, above the threshold, to be considered a spur.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SPUR_RANGE_PEAK_EXCURSION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_peak_excursion(self, selector_string, value):
        r"""Sets the peak excursion value used to find the spurs in the spectrum. This value is expressed in dB. The signal
        should rise and fall by at least the peak excursion value, above the threshold, to be considered a spur.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the peak excursion value used to find the spurs in the spectrum. This value is expressed in dB. The signal
                should rise and fall by at least the peak excursion value, above the threshold, to be considered a spur.

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
                attributes.AttributeID.SPUR_RANGE_PEAK_EXCURSION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_number_of_spurs_to_report(self, selector_string):
        r"""Gets the number of spurious emissions (Spur) that the measurement should report in the frequency range.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of spurious emissions (Spur) that the measurement should report in the frequency range.

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
                attributes.AttributeID.SPUR_RANGE_NUMBER_OF_SPURS_TO_REPORT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_number_of_spurs_to_report(self, selector_string, value):
        r"""Sets the number of spurious emissions (Spur) that the measurement should report in the frequency range.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of spurious emissions (Spur) that the measurement should report in the frequency range.

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
                attributes.AttributeID.SPUR_RANGE_NUMBER_OF_SPURS_TO_REPORT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the spurious emission (Spur) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The Spur measurement uses the Spur Averaging Count attribute as the number of acquisitions over which the Spur           |
        |              | measurement is averaged.                                                                                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SpurAveragingEnabled):
                Specifies whether to enable averaging for the spurious emission (Spur) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_AVERAGING_ENABLED.value
            )
            attr_val = enums.SpurAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the spurious emission (Spur) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The Spur measurement uses the Spur Averaging Count attribute as the number of acquisitions over which the Spur           |
        |              | measurement is averaged.                                                                                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurAveragingEnabled, int):
                Specifies whether to enable averaging for the spurious emission (Spur) measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpurAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_AVERAGING_ENABLED.value, value
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

        **Supported devices**: PXIe-5665/5668

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
                updated_selector_string, attributes.AttributeID.SPUR_AVERAGING_COUNT.value
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

        **Supported devices**: PXIe-5665/5668

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
                updated_selector_string, attributes.AttributeID.SPUR_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spurious
        emission (Spur) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        **Supported devices**: PXIe-5665/5668

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

            attr_val (enums.SpurAveragingType):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spurious
                emission (Spur) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_AVERAGING_TYPE.value
            )
            attr_val = enums.SpurAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spurious
        emission (Spur) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        **Supported devices**: PXIe-5665/5668

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

            value (enums.SpurAveragingType, int):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for spurious
                emission (Spur) measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SpurAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_AVERAGING_TYPE.value, value
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

        **Supported devices**: PXIe-5665/5668

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

            attr_val (enums.SpurFftWindow):
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
                updated_selector_string, attributes.AttributeID.SPUR_FFT_WINDOW.value
            )
            attr_val = enums.SpurFftWindow(attr_val)
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

        **Supported devices**: PXIe-5665/5668

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
        | Blackman-Harris (6) | Useful as a good general purpose window, having side lobe rejection greater than 90 dB and having a moderately wide      |
        |                     | main lobe.                                                                                                               |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
        +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SpurFftWindow, int):
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
            value = value.value if type(value) is enums.SpurFftWindow else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_FFT_WINDOW.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trace_range_index(self, selector_string):
        r"""Gets the index of the range used to store and retrieve spurious emission (Spur) traces. This attribute is not used
        if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.ALL_TRACES_ENABLED` to FALSE. When you set this attribute
        to -1, the measurement stores and retrieves traces for all enabled ranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the index of the range used to store and retrieve spurious emission (Spur) traces. This attribute is not used
                if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.ALL_TRACES_ENABLED` to FALSE. When you set this attribute
                to -1, the measurement stores and retrieves traces for all enabled ranges.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_TRACE_RANGE_INDEX.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_trace_range_index(self, selector_string, value):
        r"""Sets the index of the range used to store and retrieve spurious emission (Spur) traces. This attribute is not used
        if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.ALL_TRACES_ENABLED` to FALSE. When you set this attribute
        to -1, the measurement stores and retrieves traces for all enabled ranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the index of the range used to store and retrieve spurious emission (Spur) traces. This attribute is not used
                if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.ALL_TRACES_ENABLED` to FALSE. When you set this attribute
                to -1, the measurement stores and retrieves traces for all enabled ranges.

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
                updated_selector_string, attributes.AttributeID.SPUR_TRACE_RANGE_INDEX.value, value
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

            attr_val (enums.SpurAmplitudeCorrectionType):
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
                updated_selector_string, attributes.AttributeID.SPUR_AMPLITUDE_CORRECTION_TYPE.value
            )
            attr_val = enums.SpurAmplitudeCorrectionType(attr_val)
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

            value (enums.SpurAmplitudeCorrectionType, int):
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
            value = value.value if type(value) is enums.SpurAmplitudeCorrectionType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SPUR_AMPLITUDE_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the spurious emissions (Spur)
        measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the spurious emissions (Spur)
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
                updated_selector_string, attributes.AttributeID.SPUR_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the spurious emissions (Spur)
        measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the spurious emissions (Spur)
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
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SPUR_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for spurious emission (Spur) measurement.

        The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
        be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum number of threads used for parallelism for spurious emission (Spur) measurement.

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
                attributes.AttributeID.SPUR_NUMBER_OF_ANALYSIS_THREADS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for spurious emission (Spur) measurement.

        The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
        be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of threads used for parallelism for spurious emission (Spur) measurement.

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
                attributes.AttributeID.SPUR_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the spurious emission (Spur) measurement.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.SpurAveragingEnabled, int):
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

            averaging_type (enums.SpurAveragingType, int):
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
                if type(averaging_enabled) is enums.SpurAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.SpurAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fft_window_type(self, selector_string, fft_window):
        r"""Configures the FFT window to obtain a spectrum for the spurious emission (Spur) measurement.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            fft_window (enums.SpurFftWindow, int):
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
                | Blackman (5)        | Analyzes single tone because it has a low maximum side lobe level and a high side lobe roll-off rate.                    |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Blackman-Harris (6) | Useful as a general purpose window, having side lobe rejection greater than 90dB and having a moderately wide main       |
                |                     | lobe.                                                                                                                    |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Kaiser-Bessel (7)   | Separates two tones with frequencies close to each other but with widely-differing amplitudes.                           |
                +---------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            fft_window = fft_window.value if type(fft_window) is enums.SpurFftWindow else fft_window
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_fft_window_type(
                updated_selector_string, fft_window
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_ranges(self, selector_string, number_of_ranges):
        r"""Configures the number of ranges.

        **
        Supported devices:
        **
        PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_ranges (int):
                This parameter specifies the number of ranges. The default value is 1.

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
            error_code = self._interpreter.spur_configure_number_of_ranges(
                updated_selector_string, number_of_ranges
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_absolute_limit_array(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        r"""Configures the absolute power limits corresponding to the beginning and end of the frequency range and specifies
        whether the absolute limit threshold is a flat line or a line with a slope.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            absolute_limit_mode (enums.SpurAbsoluteLimitMode, int):
                This parameter specifies whether the absolute limit threshold is a flat line or a line with a slope. The default value
                is **Couple**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | The line specified by the Spur Range Abs Limit Start and Spur Range Abs Limit Stop attribute values as the two ends is   |
                |              | considered as the mask.                                                                                                  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Couple (1)   | The two ends of the line are coupled to the value of the Spur Range Abs Limit Start attribute.                           |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            absolute_limit_start (float):
                This parameter specifies the array of absolute power limits, in dBm, corresponding to the beginning of the frequency
                range. The value of this parameter is also set as the absolute power limit for the range when you set the **Absolute
                Limit Mode** parameter to **Couple**. The default value is -10.

            absolute_limit_stop (float):
                This parameter specifies the array of absolute power limits, in dBm, corresponding to the end of the frequency range.
                This parameter is ignored when you set the **Absolute Limit Mode** parameter to **Couple**. The default value is -10.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            absolute_limit_mode = (
                [v.value for v in absolute_limit_mode]
                if (
                    isinstance(absolute_limit_mode, list)
                    and all(isinstance(v, enums.SpurAbsoluteLimitMode) for v in absolute_limit_mode)
                )
                else absolute_limit_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_absolute_limit_array(
                updated_selector_string,
                absolute_limit_mode,
                absolute_limit_start,
                absolute_limit_stop,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_absolute_limit(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        r"""Configures the absolute power limits corresponding to the beginning and end of the frequency range.
        Use "range<*n*>" as the selector string to configure this method.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            absolute_limit_mode (enums.SpurAbsoluteLimitMode, int):
                This parameter specifies whether the absolute limit threshold is a flat line or a line with a slope. The default value
                is **Couple**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | The line specified by the Spur Range Abs Limit Start and Spur Range Abs Limit Stop attribute values as the two ends is   |
                |              | considered as the mask.                                                                                                  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Couple (1)   | The two ends of the line are coupled to the value of the Spur Range Abs Limit Start attribute.                           |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            absolute_limit_start (float):
                This parameter specifies the absolute power limit, in dBm, corresponding to the beginning of the frequency range. The
                value of this parameter is also set as the absolute power limit for the range when you set the **Absolute Limit Mode**
                parameter to **Couple**. The default value is -10.

            absolute_limit_stop (float):
                This parameter specifies the absolute power limit, in dBm, corresponding to the end of the frequency range. This
                parameter is ignored when you set the **Absolute Limit Mode** parameter to **Couple**. The default value is -10.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            absolute_limit_mode = (
                absolute_limit_mode.value
                if type(absolute_limit_mode) is enums.SpurAbsoluteLimitMode
                else absolute_limit_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_absolute_limit(
                updated_selector_string,
                absolute_limit_mode,
                absolute_limit_start,
                absolute_limit_stop,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_detector_array(self, selector_string, detector_type, detector_points):
        r"""Configures an array of the detector settings including detector type and the number of points to be detected.

        Refer to `Spectral Measurements Concepts
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectral-measurements-concepts.html>`_ topic for more information on
        detector types.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            detector_type (enums.SpurRangeDetectorType, int):
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
                This parameter specifies an array of the number of points after the detector is applied.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            detector_type = (
                [v.value for v in detector_type]
                if (
                    isinstance(detector_type, list)
                    and all(isinstance(v, enums.SpurRangeDetectorType) for v in detector_type)
                )
                else detector_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_detector_array(
                updated_selector_string, detector_type, detector_points
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_detector(self, selector_string, detector_type, detector_points):
        r"""Configures the detector settings including detector type and the number of points to be detected.
        Use "range<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            detector_type (enums.SpurRangeDetectorType, int):
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
                if type(detector_type) is enums.SpurRangeDetectorType
                else detector_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_detector(
                updated_selector_string, detector_type, detector_points
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_frequency_array(
        self, selector_string, start_frequency, stop_frequency, range_enabled
    ):
        r"""Configures the frequency start and stop values and specifies whether to enable measurement of the spurious emissions
        (Spur) in the frequency range.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            start_frequency (float):
                This parameter specifies the array of start frequencies of the frequency range, in Hz, for the measurement. The default
                value is 500 MHz.

            stop_frequency (float):
                This parameter specifies the array of stop frequencies of the frequency range, in Hz, for the measurement. The default
                value is 1.5 GHz.

            range_enabled (enums.SpurRangeEnabled, int):
                This parameter specifies whether to measure the Spur in the frequency range. The default value is **True**.

                +--------------+------------------------------------------------------+
                | Name (Value) | Description                                          |
                +==============+======================================================+
                | False (0)    | Disables the acquisition of the frequency range.     |
                +--------------+------------------------------------------------------+
                | True (1)     | Enables measurement of Spurs in the frequency range. |
                +--------------+------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            range_enabled = (
                [v.value for v in range_enabled]
                if (
                    isinstance(range_enabled, list)
                    and all(isinstance(v, enums.SpurRangeEnabled) for v in range_enabled)
                )
                else range_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_frequency_array(
                updated_selector_string, start_frequency, stop_frequency, range_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_frequency(
        self, selector_string, start_frequency, stop_frequency, range_enabled
    ):
        r"""Configures the frequency start and stop values of the range.
        Use "range<*n*>" as the selector string to configure this method.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            start_frequency (float):
                This parameter specifies the start of the frequency range, in Hz, for the measurement. The default value is 500 MHz.

            stop_frequency (float):
                This parameter specifies the stop of the frequency range, in Hz, for the measurement. The default value is 1.5 GHz.

            range_enabled (enums.SpurRangeEnabled, int):
                This parameter specifies whether to measure the Spurs in the frequency range. The default value is **True**.

                +--------------+------------------------------------------------------+
                | Name (Value) | Description                                          |
                +==============+======================================================+
                | False (0)    | Disables the acquisition of the frequency range.     |
                +--------------+------------------------------------------------------+
                | True (1)     | Enables measurement of Spurs in the frequency range. |
                +--------------+------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            range_enabled = (
                range_enabled.value
                if type(range_enabled) is enums.SpurRangeEnabled
                else range_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_frequency(
                updated_selector_string, start_frequency, stop_frequency, range_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_number_of_spurs_to_report_array(
        self, selector_string, number_of_spurs_to_report
    ):
        r"""Specifies the number of Spurs that the measurement should report in the frequency range.

        **
        Supported devices:
        **
        PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_spurs_to_report (int):
                This parameter specifies the array of number of Spurs that the measurement should report in the frequency range. The
                default value is 10.

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
            error_code = self._interpreter.spur_configure_range_number_of_spurs_to_report_array(
                updated_selector_string, number_of_spurs_to_report
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_number_of_spurs_to_report(self, selector_string, number_of_spurs_to_report):
        r"""Specifies the number of Spurs that the measurement should report in the frequency range.

        Use "range<
        *
        n
        *
        >" as the selector string to configure this method.

        **
        Supported devices:
        **
        PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            number_of_spurs_to_report (int):
                This parameter specifies the number of Spurs that the measurement should report in the frequency range. The default
                value is 10.

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
            error_code = self._interpreter.spur_configure_range_number_of_spurs_to_report(
                updated_selector_string, number_of_spurs_to_report
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_peak_criteria_array(self, selector_string, threshold, excursion):
        r"""Configures arrays of peak threshold and peak excursion criteria which a peak should meet to be classified as a spurious
        emission (Spur).

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            threshold (float):
                This parameter specifies the array of threshold levels, in dBm, above which the measurement detects spurs in the range.
                The default value is -200.

            excursion (float):
                This parameter specifies  the array of peak excursion values, in dB, used to find the spurs in the spectrum. The signal
                should rise and fall by at least the peak excursion value, above the threshold, to be considered as a spur. The default
                value is 0.

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
            error_code = self._interpreter.spur_configure_range_peak_criteria_array(
                updated_selector_string, threshold, excursion
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_peak_criteria(self, selector_string, threshold, excursion):
        r"""Configures the peak threshold and peak excursion criteria which a peak should meet to be classified as a spurious
        emission (Spur).

        Use "range<
        *
        n
        *
        >" as the selector string to configure this method.

        **
        Supported devices:
        **
        PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            threshold (float):
                This parameter specifies the threshold level, in dBm, above which the measurement detects spurs in the range. The
                default value is -200.

            excursion (float):
                This parameter specifies  the peak excursion to be used when spur detection is performed. The default value is 6.

                Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
                information on spur removal.

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
            error_code = self._interpreter.spur_configure_range_peak_criteria(
                updated_selector_string, threshold, excursion
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_rbw_array(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the resolution bandwidth (RBW) filter.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw_auto (enums.SpurRbwAutoBandwidth, int):
                This parameter specifies whether the measurement computes the RBW. Refer to the `Spectrum
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectrum.html>`_ topic for details on RBW and sweep time. The default
                value is **True**.

                +--------------+---------------------------------------------------------------------+
                | Name (Value) | Description                                                         |
                +==============+=====================================================================+
                | False (0)    | The measurement uses the RBW that you specify in the RBW parameter. |
                +--------------+---------------------------------------------------------------------+
                | True (1)     | The measurement computes the RBW.                                   |
                +--------------+---------------------------------------------------------------------+

            rbw (float):
                This parameter specifies the array of bandwidths, in Hz, of the RBW filter used to sweep the acquired range, when you
                set the **RBW Auto** parameter to **False**. The default value is 10 kHz.

            rbw_filter_type (enums.SpurRbwFilterType, int):
                This parameter specifies the shape of the digital RBW filter. The default value is **Gaussian**.

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
                [v.value for v in rbw_auto]
                if (
                    isinstance(rbw_auto, list)
                    and all(isinstance(v, enums.SpurRbwAutoBandwidth) for v in rbw_auto)
                )
                else rbw_auto
            )
            rbw_filter_type = (
                [v.value for v in rbw_filter_type]
                if (
                    isinstance(rbw_filter_type, list)
                    and all(isinstance(v, enums.SpurRbwFilterType) for v in rbw_filter_type)
                )
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_rbw_array(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the resolution bandwidth (RBW) filter.
        Use "range<*n*>" as the selector string to configure this method.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            rbw_auto (enums.SpurRbwAutoBandwidth, int):
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
                This parameter specifies the bandwidth, in Hz, of the RBW filter used to sweep the acquired offset segment, when you
                set the **RBW Auto** parameter to **False**. The default value is 10 kHz.

            rbw_filter_type (enums.SpurRbwFilterType, int):
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
            rbw_auto = rbw_auto.value if type(rbw_auto) is enums.SpurRbwAutoBandwidth else rbw_auto
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.SpurRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_rbw_filter(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_relative_attenuation_array(self, selector_string, relative_attenuation):
        r"""Specifies the attenuation, in dB, relative to the external attenuation.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            relative_attenuation (float):
                This parameter specifies an array of attenuation values, in dB, relative to the external attenuation. Use this
                parameter to compensate for the variations in external attenuation when offset channels are spread wide in frequency.
                The default value is 0.

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
            error_code = self._interpreter.spur_configure_range_relative_attenuation_array(
                updated_selector_string, relative_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_relative_attenuation(self, selector_string, relative_attenuation):
        r"""Specifies the attenuation, in dB, relative to the external attenuation.
        Use "range<*n*>" as the selector string to configure this method.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            relative_attenuation (float):
                This parameter specifies the attenuation, in dB, relative to the external attenuation. Use this parameter to compensate
                for variations in external attenuation when the offset channels are spread wide in frequency. The default value is 0.

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
            error_code = self._interpreter.spur_configure_range_relative_attenuation(
                updated_selector_string, relative_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_sweep_time_array(
        self, selector_string, sweep_time_auto, sweep_time_interval
    ):
        r"""Configures the sweep time.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            sweep_time_auto (enums.SpurSweepTimeAuto, int):
                This parameter specifies whether the measurement computes the sweep time. The default value is **True**.

                +--------------+-----------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                   |
                +==============+===============================================================================================+
                | False (0)    | The measurement uses the sweep time that you specify in the Spur Range Sweep Time attribute.  |
                +--------------+-----------------------------------------------------------------------------------------------+
                | True (1)     | The measurement calculates the sweep time based on the value of the Spur Range RBW attribute. |
                +--------------+-----------------------------------------------------------------------------------------------+

            sweep_time_interval (float):
                This parameter specifies the array of sweep times, in seconds, when you set the **Sweep Time Auto** parameter to
                **False**. The default value is 1 ms.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            sweep_time_auto = (
                [v.value for v in sweep_time_auto]
                if (
                    isinstance(sweep_time_auto, list)
                    and all(isinstance(v, enums.SpurSweepTimeAuto) for v in sweep_time_auto)
                )
                else sweep_time_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_sweep_time_array(
                updated_selector_string, sweep_time_auto, sweep_time_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        r"""Configures the sweep time.
        Use "range<*n*>" as the selector string to configure this method.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            sweep_time_auto (enums.SpurSweepTimeAuto, int):
                This parameter specifies whether the measurement computes the sweep time. The default value is **True**.

                +--------------+-----------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                   |
                +==============+===============================================================================================+
                | False (0)    | The measurement uses the sweep time that you specify in the Spur Range Sweep Time attribute.  |
                +--------------+-----------------------------------------------------------------------------------------------+
                | True (1)     | The measurement calculates the sweep time based on the value of the Spur Range RBW attribute. |
                +--------------+-----------------------------------------------------------------------------------------------+

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
                if type(sweep_time_auto) is enums.SpurSweepTimeAuto
                else sweep_time_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_sweep_time(
                updated_selector_string, sweep_time_auto, sweep_time_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_vbw_filter_array(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        r"""Configures an array of the VBW settings, including VBW Auto, VBW, and VBW to RBW ratio for the specified range.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            vbw_auto (enums.SpurRangeVbwFilterAutoBandwidth, int):
                This parameter specifies whether the VBW is expressed directly or computed based on VBW to RBW ratio. The default value
                is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Specify the video bandwidth in the VBW parameter. The VBW to RBW Ratio parameter is disregarded in this mode.            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
                |              | the Spur VBW to RBW Ratio attribute and the Spur Range RBW attribute. The value of the VBW parameter is disregarded in   |
                |              | this mode.                                                                                                               |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            vbw (float):
                This parameter specifies the video bandwidth when you set the **VBW Auto** parameter to **False**. This value is
                expressed in Hz. The default value is 30KHz.

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
                [v.value for v in vbw_auto]
                if (
                    isinstance(vbw_auto, list)
                    and all(isinstance(v, enums.SpurRangeVbwFilterAutoBandwidth) for v in vbw_auto)
                )
                else vbw_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_vbw_filter_array(
                updated_selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_vbw_filter(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        r"""Configures the video bandwidth (VBW) settings including VBW Auto, VBW, and VBW to RBW ratio for the specified range.
        Use "range<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of range
                number.

                Example:

                "range0"

                You can use the :py:meth:`build_range_string` method to build the selector string.

            vbw_auto (enums.SpurRangeVbwFilterAutoBandwidth, int):
                This parameter specifies whether the VBW is expressed directly or computed based on VBW to RBW ratio. The default value
                is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Specify the video bandwidth in the VBW parameter. The VBW to RBW Ratio parameter is disregarded in this mode.            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
                |              | the Spur VBW to RBW Ratio attribute and the Spur Range RBW attribute. The value of the VBW parameter is disregarded in   |
                |              | this mode.                                                                                                               |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            vbw (float):
                This parameter specifies the video bandwidth when you set the **VBW Auto** parameter to **False**. This value is
                expressed in Hz. The default value is 30KHz.

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
                if type(vbw_auto) is enums.SpurRangeVbwFilterAutoBandwidth
                else vbw_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.spur_configure_range_vbw_filter(
                updated_selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_trace_range_index(self, selector_string, trace_range_index):
        r"""Specifies the index of the range used to store and retrieve the spurious emission (Spur) trace.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            trace_range_index (int):
                This parameter specifies the index of the range used to store and retrieve Spur traces. This parameter is not used if
                you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.ALL_TRACES_ENABLED` to FALSE. When you set this parameter to
                -1, the measurement stores and retrieves traces for all enabled ranges. The default value is -1.

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
            error_code = self._interpreter.spur_configure_trace_range_index(
                updated_selector_string, trace_range_index
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
