"""Provides methods to configure the Txp measurement."""

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


class TxpConfiguration(object):
    """Provides methods to configure the Txp measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Txp measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the TXP measurement.

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
                Specifies whether to enable the TXP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the TXP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the TXP measurement.

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
                updated_selector_string, attributes.AttributeID.TXP_MEASUREMENT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_interval(self, selector_string):
        r"""Gets the acquisition time for the TXP measurement. This value is expressed in seconds.

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
                Specifies the acquisition time for the TXP measurement. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.TXP_MEASUREMENT_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_interval(self, selector_string, value):
        r"""Sets the acquisition time for the TXP measurement. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition time for the TXP measurement. This value is expressed in seconds.

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
                attributes.AttributeID.TXP_MEASUREMENT_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
        Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
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
                updated_selector_string, attributes.AttributeID.TXP_RBW_FILTER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
        Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the signal. This value is expressed in
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
                updated_selector_string,
                attributes.AttributeID.TXP_RBW_FILTER_BANDWIDTH.value,
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

        +--------------+----------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                              |
        +==============+==========================================================================================================+
        | Gaussian (1) | The RBW filter has a Gaussian response.                                                                  |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Flat (2)     | The RBW filter has a flat response.                                                                      |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | None (5)     | The measurement does not use any RBW filtering.                                                          |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | RRC (6)      | The RRC filter with the roll-off specified by the TXP RBW RRC Alpha attribute is used as the RBW filter. |
        +--------------+----------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TxpRbwFilterType):
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
                updated_selector_string, attributes.AttributeID.TXP_RBW_FILTER_TYPE.value
            )
            attr_val = enums.TxpRbwFilterType(attr_val)
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

        +--------------+----------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                              |
        +==============+==========================================================================================================+
        | Gaussian (1) | The RBW filter has a Gaussian response.                                                                  |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Flat (2)     | The RBW filter has a flat response.                                                                      |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | None (5)     | The measurement does not use any RBW filtering.                                                          |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | RRC (6)      | The RRC filter with the roll-off specified by the TXP RBW RRC Alpha attribute is used as the RBW filter. |
        +--------------+----------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TxpRbwFilterType, int):
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
            value = value.value if type(value) is enums.TxpRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_RBW_FILTER_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_alpha(self, selector_string):
        r"""Gets the roll-off factor for the root-raised-cosine (RRC) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the roll-off factor for the root-raised-cosine (RRC) filter.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.TXP_RBW_FILTER_ALPHA.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_alpha(self, selector_string, value):
        r"""Sets the roll-off factor for the root-raised-cosine (RRC) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the roll-off factor for the root-raised-cosine (RRC) filter.

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
                updated_selector_string, attributes.AttributeID.TXP_RBW_FILTER_ALPHA.value, value
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
        | False (0)    | Specify the video bandwidth in the TXP VBW                                                                               |
        |              | attribute. The TXP VBW to RBW Ratio attribute is disregarded in this mode.                                               |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
        |              | the TXP VBW to RBW Ratio attribute and the TXP RBW attribute. The value of the TXP VBW                                   |
        |              | attribute is disregarded in this mode.                                                                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TxpVbwFilterAutoBandwidth):
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
                updated_selector_string, attributes.AttributeID.TXP_VBW_FILTER_AUTO_BANDWIDTH.value
            )
            attr_val = enums.TxpVbwFilterAutoBandwidth(attr_val)
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
        | False (0)    | Specify the video bandwidth in the TXP VBW                                                                               |
        |              | attribute. The TXP VBW to RBW Ratio attribute is disregarded in this mode.                                               |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
        |              | the TXP VBW to RBW Ratio attribute and the TXP RBW attribute. The value of the TXP VBW                                   |
        |              | attribute is disregarded in this mode.                                                                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TxpVbwFilterAutoBandwidth, int):
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
            value = value.value if type(value) is enums.TxpVbwFilterAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.TXP_VBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_vbw_filter_bandwidth(self, selector_string):
        r"""Gets the video bandwidth when you set the
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
                Specifies the video bandwidth when you set the
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
                updated_selector_string, attributes.AttributeID.TXP_VBW_FILTER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_vbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the video bandwidth when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 30000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the video bandwidth when you set the
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
                attributes.AttributeID.TXP_VBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_vbw_filter_vbw_to_rbw_ratio(self, selector_string):
        r"""Gets the VBW to RBW Ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

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
                :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

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
                attributes.AttributeID.TXP_VBW_FILTER_VBW_TO_RBW_RATIO.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_vbw_filter_vbw_to_rbw_ratio(self, selector_string, value):
        r"""Sets the VBW to RBW Ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the VBW to RBW Ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.VBW_FILTER_AUTO_BANDWIDTH` attribute to **True**.

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
                attributes.AttributeID.TXP_VBW_FILTER_VBW_TO_RBW_RATIO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_enabled(self, selector_string):
        r"""Gets whether to enable thresholding of the acquired samples to be used for the TXP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | All the acquired samples are considered for the TXP measurement.                                                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The samples above the threshold level specified in the TXP Threshold Level attribute are considered for the TXP          |
        |              | measurement.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TxpThresholdEnabled):
                Specifies whether to enable thresholding of the acquired samples to be used for the TXP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_THRESHOLD_ENABLED.value
            )
            attr_val = enums.TxpThresholdEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_enabled(self, selector_string, value):
        r"""Sets whether to enable thresholding of the acquired samples to be used for the TXP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | All the acquired samples are considered for the TXP measurement.                                                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The samples above the threshold level specified in the TXP Threshold Level attribute are considered for the TXP          |
        |              | measurement.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TxpThresholdEnabled, int):
                Specifies whether to enable thresholding of the acquired samples to be used for the TXP measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.TxpThresholdEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_THRESHOLD_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_type(self, selector_string):
        r"""Gets the reference for the power level used for thresholding.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Relative**.

        +--------------+----------------------------------------------------------------------+
        | Name (Value) | Description                                                          |
        +==============+======================================================================+
        | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
        +--------------+----------------------------------------------------------------------+
        | Absolute (1) | The threshold is the absolute power, in dBm.                         |
        +--------------+----------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TxpThresholdType):
                Specifies the reference for the power level used for thresholding.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_THRESHOLD_TYPE.value
            )
            attr_val = enums.TxpThresholdType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_type(self, selector_string, value):
        r"""Sets the reference for the power level used for thresholding.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Relative**.

        +--------------+----------------------------------------------------------------------+
        | Name (Value) | Description                                                          |
        +==============+======================================================================+
        | Relative (0) | The threshold is relative to the peak power of the acquired samples. |
        +--------------+----------------------------------------------------------------------+
        | Absolute (1) | The threshold is the absolute power, in dBm.                         |
        +--------------+----------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TxpThresholdType, int):
                Specifies the reference for the power level used for thresholding.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.TxpThresholdType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_THRESHOLD_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_level(self, selector_string):
        r"""Gets either the relative or absolute threshold power level based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies either the relative or absolute threshold power level based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.TXP_THRESHOLD_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_level(self, selector_string, value):
        r"""Sets either the relative or absolute threshold power level based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies either the relative or absolute threshold power level based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

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
                updated_selector_string, attributes.AttributeID.TXP_THRESHOLD_LEVEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the TXP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The TXP measurement uses the TXP Averaging Count attribute as the number of acquisitions over which the TXP measurement  |
        |              | is averaged.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TxpAveragingEnabled):
                Specifies whether to enable averaging for the TXP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_AVERAGING_ENABLED.value
            )
            attr_val = enums.TxpAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the TXP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The TXP measurement uses the TXP Averaging Count attribute as the number of acquisitions over which the TXP measurement  |
        |              | is averaged.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TxpAveragingEnabled, int):
                Specifies whether to enable averaging for the TXP measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.TxpAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.TXP_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.TXP_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for the TXP measurement. The averaged power trace is used for the measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        +--------------+--------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                      |
        +==============+==================================================================================================+
        | RMS (0)      | The power trace is linearly averaged.                                                            |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Log (1)      | The power trace is averaged in a logarithmic scale.                                              |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Scalar (2)   | The square root of the power trace is averaged.                                                  |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Max (3)      | The maximum instantaneous power in the power trace is retained from one acquisition to the next. |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Min (4)      | The minimum instantaneous power in the power trace is retained from one acquisition to the next. |
        +--------------+--------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TxpAveragingType):
                Specifies the averaging type for the TXP measurement. The averaged power trace is used for the measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_AVERAGING_TYPE.value
            )
            attr_val = enums.TxpAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for the TXP measurement. The averaged power trace is used for the measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        +--------------+--------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                      |
        +==============+==================================================================================================+
        | RMS (0)      | The power trace is linearly averaged.                                                            |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Log (1)      | The power trace is averaged in a logarithmic scale.                                              |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Scalar (2)   | The square root of the power trace is averaged.                                                  |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Max (3)      | The maximum instantaneous power in the power trace is retained from one acquisition to the next. |
        +--------------+--------------------------------------------------------------------------------------------------+
        | Min (4)      | The minimum instantaneous power in the power trace is retained from one acquisition to the next. |
        +--------------+--------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TxpAveragingType, int):
                Specifies the averaging type for the TXP measurement. The averaged power trace is used for the measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.TxpAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_AVERAGING_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the TXP measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the TXP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the TXP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the TXP measurement.

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
                updated_selector_string, attributes.AttributeID.TXP_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for TXP measurement.

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
                Specifies the maximum number of threads used for parallelism for TXP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.TXP_NUMBER_OF_ANALYSIS_THREADS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for TXP measurement.

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
                Specifies the maximum number of threads used for parallelism for TXP measurement.

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
                attributes.AttributeID.TXP_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the transmit power (TXP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.TxpAveragingEnabled, int):
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

            averaging_type (enums.TxpAveragingType, int):
                This parameter specifies the averaging type for averaging the power over multiple acquisitions. The averaged power
                trace is used for the measurement. Refer to the Averaging section of the `Spectrum
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/spectrum.html>`_ topic for more information about averaging types. The
                default value is **RMS**.

                +--------------+----------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                              |
                +==============+==========================================================================================================+
                | RMS (0)      | The power trace is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
                +--------------+----------------------------------------------------------------------------------------------------------+
                | Log (1)      | The power trace is averaged in a logarithmic scale.                                                      |
                +--------------+----------------------------------------------------------------------------------------------------------+
                | Scalar (2)   | The square root of the power trace is averaged.                                                          |
                +--------------+----------------------------------------------------------------------------------------------------------+
                | Max (3)      | The peak power in the power trace at each sample instance is retained from one acquisition to the next.  |
                +--------------+----------------------------------------------------------------------------------------------------------+
                | Min (4)      | The least power in the power trace at each sample instance is retained from one acquisition to the next. |
                +--------------+----------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            averaging_enabled = (
                averaging_enabled.value
                if type(averaging_enabled) is enums.TxpAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.TxpAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.txp_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval(self, selector_string, measurement_interval):
        r"""Specifies the acquisition time, in seconds, for the transmit power (TXP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_interval (float):
                This parameter specifies the acquisition time, in seconds, for the measurement. The default value is 1 ms.

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
            error_code = self._interpreter.txp_configure_measurement_interval(
                updated_selector_string, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rbw_filter(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        r"""Configures the resolution bandwidth (RBW) filter to measure the power of the signal as seen through this filter.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw (float):
                This parameter specifies the bandwidth, in Hz, of the resolution bandwidth (RBW) filter used to measure the signal. The
                default value is 100 kHz.

            rbw_filter_type (enums.TxpRbwFilterType, int):
                This parameter specifies the shape of the digital RBW filter. The default value is **Gaussian**.

                +--------------+----------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                  |
                +==============+==============================================================================================+
                | None (1)     | The measurement does not use any RBW filtering.                                              |
                +--------------+----------------------------------------------------------------------------------------------+
                | Gaussian (2) | The RBW filter has a Gaussian response.                                                      |
                +--------------+----------------------------------------------------------------------------------------------+
                | Flat (3)     | The RBW filter has a flat response.                                                          |
                +--------------+----------------------------------------------------------------------------------------------+
                | RRC (4)      | The RRC filter with the roll-off specified by RRC Alpha parameter is used as the RBW filter. |
                +--------------+----------------------------------------------------------------------------------------------+

            rrc_alpha (float):
                This parameter specifies the roll-off factor for the root-raised-cosine (RRC) filter. The default value is 0.1.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.TxpRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.txp_configure_rbw_filter(
                updated_selector_string, rbw, rbw_filter_type, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        r"""Configures the threshold level for the samples that need to be considered for the transmit power (TXP) measurement.
        Enable the threshold when analyzing burst signals or signals with dead time.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            threshold_enabled (enums.TxpThresholdEnabled, int):
                This parameter specifies whether to enable thresholding of the acquired samples to be used for the measurement. The
                default value is **False**.

                +--------------+----------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                          |
                +==============+======================================================================================================================+
                | False (0)    | All samples are considered for the measurement.                                                                      |
                +--------------+----------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The samples above the threshold level specified in the Threshold Level parameter are considered for the measurement. |
                +--------------+----------------------------------------------------------------------------------------------------------------------+

            threshold_level (float):
                This parameter specifies either the relative or absolute threshold power level based on the value of the **Threshold
                Type** parameter. The default value is -20 dB.

            threshold_type (enums.TxpThresholdType, int):
                This parameter specifies the reference for the power level used for thresholding. The default value is **Relative**.

                +--------------+------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                  |
                +==============+==============================================================================+
                | Relative (0) | The threshold is relative to the peak power, in dB, of the acquired samples. |
                +--------------+------------------------------------------------------------------------------+
                | Absolute (1) | The threshold is the absolute power, in dBm.                                 |
                +--------------+------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            threshold_enabled = (
                threshold_enabled.value
                if type(threshold_enabled) is enums.TxpThresholdEnabled
                else threshold_enabled
            )
            threshold_type = (
                threshold_type.value
                if type(threshold_type) is enums.TxpThresholdType
                else threshold_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.txp_configure_threshold(
                updated_selector_string, threshold_enabled, threshold_level, threshold_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_vbw_filter(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        r"""Configures VBW settings including the VBW mode, video bandwidth (VBW), and the VBW to RBW ratio.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            vbw_auto (enums.TxpVbwFilterAutoBandwidth, int):
                This parameter specifies whether the VBW is expressed directly or computed based on VBW to RBW ratio. The default value
                is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Specify the video bandwidth in the VBW parameter. The VBW to RBW Ratio parameter is disregarded in this mode.            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Specify video bandwidth in terms of the VBW to RBW ratio. The value of the video bandwidth is then computed by using     |
                |              | the TXP VBW to RBW Ratio attribute and the TXP RBW attribute. The value of the VBW parameter is disregarded in this      |
                |              | mode.                                                                                                                    |
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
                vbw_auto.value if type(vbw_auto) is enums.TxpVbwFilterAutoBandwidth else vbw_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.txp_configure_vbw_filter(
                updated_selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
