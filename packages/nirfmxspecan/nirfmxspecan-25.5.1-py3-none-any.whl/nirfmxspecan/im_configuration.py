"""Provides methods to configure the IM measurement."""

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


class IMConfiguration(object):
    """Provides methods to configure the IM measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the IM measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the IM measurement.

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
                Specifies whether to enable the IM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the IM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the IM measurement.

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
                updated_selector_string, attributes.AttributeID.IM_MEASUREMENT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_definition(self, selector_string):
        r"""Gets whether the tones and intermod frequencies are relative to the RF
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`, or are absolute frequencies.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Relative**.

        +--------------+--------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                  |
        +==============+==============================================================================================================+
        | Relative (0) | The tone and intermod frequencies are relative to the RF center frequency.                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------+
        | Absolute (1) | The tone and intermod frequencies are absolute frequencies. The measurement ignores the RF center frequency. |
        +--------------+--------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMFrequencyDefinition):
                Specifies whether the tones and intermod frequencies are relative to the RF
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`, or are absolute frequencies.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_FREQUENCY_DEFINITION.value
            )
            attr_val = enums.IMFrequencyDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_definition(self, selector_string, value):
        r"""Sets whether the tones and intermod frequencies are relative to the RF
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`, or are absolute frequencies.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Relative**.

        +--------------+--------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                  |
        +==============+==============================================================================================================+
        | Relative (0) | The tone and intermod frequencies are relative to the RF center frequency.                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------+
        | Absolute (1) | The tone and intermod frequencies are absolute frequencies. The measurement ignores the RF center frequency. |
        +--------------+--------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMFrequencyDefinition, int):
                Specifies whether the tones and intermod frequencies are relative to the RF
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`, or are absolute frequencies.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMFrequencyDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_FREQUENCY_DEFINITION.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fundamental_lower_tone_frequency(self, selector_string):
        r"""Gets the frequency of the tone that has a lower frequency among the two tones in the input signal. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequency of the tone that has a lower frequency among the two tones in the input signal. This value is
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
                updated_selector_string,
                attributes.AttributeID.IM_FUNDAMENTAL_LOWER_TONE_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fundamental_lower_tone_frequency(self, selector_string, value):
        r"""Sets the frequency of the tone that has a lower frequency among the two tones in the input signal. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency of the tone that has a lower frequency among the two tones in the input signal. This value is
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
                attributes.AttributeID.IM_FUNDAMENTAL_LOWER_TONE_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fundamental_upper_tone_frequency(self, selector_string):
        r"""Gets the frequency of the tone that has a higher frequency among the two tones in the input signal. This value is
        expressed in Hz.

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
                Specifies the frequency of the tone that has a higher frequency among the two tones in the input signal. This value is
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
                updated_selector_string,
                attributes.AttributeID.IM_FUNDAMENTAL_UPPER_TONE_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fundamental_upper_tone_frequency(self, selector_string, value):
        r"""Sets the frequency of the tone that has a higher frequency among the two tones in the input signal. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency of the tone that has a higher frequency among the two tones in the input signal. This value is
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
                attributes.AttributeID.IM_FUNDAMENTAL_UPPER_TONE_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_auto_intermods_setup_enabled(self, selector_string):
        r"""Gets whether the measurement computes the intermod frequencies or uses user-specified frequencies.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement uses the values that you specify for the IM Lower Intermod Freq and IM Upper Intermod Freq attributes.   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the intermod frequencies. The maximum number of intermods that you can measure is based on the  |
        |              | value of the IM Max Intermod Order attribute.                                                                            |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMAutoIntermodsSetupEnabled):
                Specifies whether the measurement computes the intermod frequencies or uses user-specified frequencies.

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
                attributes.AttributeID.IM_AUTO_INTERMODS_SETUP_ENABLED.value,
            )
            attr_val = enums.IMAutoIntermodsSetupEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_auto_intermods_setup_enabled(self, selector_string, value):
        r"""Sets whether the measurement computes the intermod frequencies or uses user-specified frequencies.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement uses the values that you specify for the IM Lower Intermod Freq and IM Upper Intermod Freq attributes.   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the intermod frequencies. The maximum number of intermods that you can measure is based on the  |
        |              | value of the IM Max Intermod Order attribute.                                                                            |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMAutoIntermodsSetupEnabled, int):
                Specifies whether the measurement computes the intermod frequencies or uses user-specified frequencies.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMAutoIntermodsSetupEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IM_AUTO_INTERMODS_SETUP_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_maximum_intermod_order(self, selector_string):
        r"""Gets the order up to which the RFmx driver measures odd order intermodulation products when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**. The lower and upper
        intermodulation products are measured for each order.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **3**.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the order up to which the RFmx driver measures odd order intermodulation products when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**. The lower and upper
                intermodulation products are measured for each order.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_MAXIMUM_INTERMOD_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_maximum_intermod_order(self, selector_string, value):
        r"""Sets the order up to which the RFmx driver measures odd order intermodulation products when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**. The lower and upper
        intermodulation products are measured for each order.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **3**.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the order up to which the RFmx driver measures odd order intermodulation products when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**. The lower and upper
                intermodulation products are measured for each order.

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
                attributes.AttributeID.IM_MAXIMUM_INTERMOD_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_intermods(self, selector_string):
        r"""Gets the number of intermods to measure when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

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
                Specifies the number of intermods to measure when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_NUMBER_OF_INTERMODS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_intermods(self, selector_string, value):
        r"""Sets the number of intermods to measure when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of intermods to measure when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

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
                updated_selector_string, attributes.AttributeID.IM_NUMBER_OF_INTERMODS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_intermod_enabled(self, selector_string):
        r"""Gets whether to enable an intermod for the IM measurement. This attribute is not used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+-----------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                               |
        +==============+===========================================================================================================+
        | False (0)    | Disables an intermod for the IM measurement. The results for the disabled intermods are displayed as NaN. |
        +--------------+-----------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables an intermod for the IM measurement.                                                               |
        +--------------+-----------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMIntermodEnabled):
                Specifies whether to enable an intermod for the IM measurement. This attribute is not used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_INTERMOD_ENABLED.value
            )
            attr_val = enums.IMIntermodEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_intermod_enabled(self, selector_string, value):
        r"""Sets whether to enable an intermod for the IM measurement. This attribute is not used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+-----------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                               |
        +==============+===========================================================================================================+
        | False (0)    | Disables an intermod for the IM measurement. The results for the disabled intermods are displayed as NaN. |
        +--------------+-----------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables an intermod for the IM measurement.                                                               |
        +--------------+-----------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMIntermodEnabled, int):
                Specifies whether to enable an intermod for the IM measurement. This attribute is not used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMIntermodEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_INTERMOD_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_intermod_order(self, selector_string):
        r"""Gets the order of the intermod. This attribute is not used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the order of the intermod. This attribute is not used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_INTERMOD_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_intermod_order(self, selector_string, value):
        r"""Sets the order of the intermod. This attribute is not used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the order of the intermod. This attribute is not used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

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
                updated_selector_string, attributes.AttributeID.IM_INTERMOD_ORDER.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_intermod_side(self, selector_string):
        r"""Gets whether to measure intermodulation products corresponding to both lower and upper intermod frequencies or
        either one of them. This attribute is not used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Both**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Lower (0)    | Measures the intermodulation product corresponding to the IM Lower Intermod Freq attribute.                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Upper (1)    | Measures the intermodulation product corresponding to the IM Upper Intermod Freq attribute.                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Both (2)     | Measures the intermodulation product corresponding to both IM Lower Intermod Freq and IM Upper Intermod Freq             |
        |              | attributes.                                                                                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMIntermodSide):
                Specifies whether to measure intermodulation products corresponding to both lower and upper intermod frequencies or
                either one of them. This attribute is not used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_INTERMOD_SIDE.value
            )
            attr_val = enums.IMIntermodSide(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_intermod_side(self, selector_string, value):
        r"""Sets whether to measure intermodulation products corresponding to both lower and upper intermod frequencies or
        either one of them. This attribute is not used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Both**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Lower (0)    | Measures the intermodulation product corresponding to the IM Lower Intermod Freq attribute.                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Upper (1)    | Measures the intermodulation product corresponding to the IM Upper Intermod Freq attribute.                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Both (2)     | Measures the intermodulation product corresponding to both IM Lower Intermod Freq and IM Upper Intermod Freq             |
        |              | attributes.                                                                                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMIntermodSide, int):
                Specifies whether to measure intermodulation products corresponding to both lower and upper intermod frequencies or
                either one of them. This attribute is not used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMIntermodSide else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_INTERMOD_SIDE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lower_intermod_frequency(self, selector_string):
        r"""Gets the frequency of the lower intermodulation product. This value is expressed in Hz. This attribute is not used
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -3 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequency of the lower intermodulation product. This value is expressed in Hz. This attribute is not used
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IM_LOWER_INTERMOD_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lower_intermod_frequency(self, selector_string, value):
        r"""Sets the frequency of the lower intermodulation product. This value is expressed in Hz. This attribute is not used
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -3 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency of the lower intermodulation product. This value is expressed in Hz. This attribute is not used
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

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
                attributes.AttributeID.IM_LOWER_INTERMOD_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_upper_intermod_frequency(self, selector_string):
        r"""Gets the frequency of the upper intermodulation product. This value is expressed in Hz. This attribute is not used
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 3 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequency of the upper intermodulation product. This value is expressed in Hz. This attribute is not used
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IM_UPPER_INTERMOD_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_upper_intermod_frequency(self, selector_string, value):
        r"""Sets the frequency of the upper intermodulation product. This value is expressed in Hz. This attribute is not used
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

        Use "intermod<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 3 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency of the upper intermodulation product. This value is expressed in Hz. This attribute is not used
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **True**.

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
                attributes.AttributeID.IM_UPPER_INTERMOD_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_method(self, selector_string):
        r"""Gets the method used to perform the IM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Normal**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | Normal (0)        | The IM measurement acquires the spectrum using the same signal analyzer settings across frequency bands. Use this        |
        |                   | method when the fundamental tone separation is not large.                                                                |
        |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668.                          |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Dynamic Range (1) | The IM measurement acquires a segmented spectrum using the signal analyzer specific optimizations for different          |
        |                   | frequency bands. The spectrum is acquired in segments, one per tone or intermod frequency to be measured. The span of    |
        |                   | each acquired spectral segment is equal to the frequency separation between the two input tones, or 1 MHz, whichever is  |
        |                   | smaller.                                                                                                                 |
        |                   | Use this method to configure the IM measurement and the signal analyzer for maximum dynamic range instead of             |
        |                   | measurement speed.                                                                                                       |
        |                   | Supported devices: PXIe-5665/5668.                                                                                       |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Segmented (2)     | Similar to the Dynamic Range method, this method also acquires a segmented spectrum, except that signal analyzer is not  |
        |                   | explicitly configured to provide maximum dynamic range. Use this method when the frequency separation of the two input   |
        |                   | tones is large and the measurement accuracy can be traded off for measurement speed.                                     |
        |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668.                          |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMMeasurementMethod):
                Specifies the method used to perform the IM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_MEASUREMENT_METHOD.value
            )
            attr_val = enums.IMMeasurementMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_method(self, selector_string, value):
        r"""Sets the method used to perform the IM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Normal**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | Normal (0)        | The IM measurement acquires the spectrum using the same signal analyzer settings across frequency bands. Use this        |
        |                   | method when the fundamental tone separation is not large.                                                                |
        |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668.                          |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Dynamic Range (1) | The IM measurement acquires a segmented spectrum using the signal analyzer specific optimizations for different          |
        |                   | frequency bands. The spectrum is acquired in segments, one per tone or intermod frequency to be measured. The span of    |
        |                   | each acquired spectral segment is equal to the frequency separation between the two input tones, or 1 MHz, whichever is  |
        |                   | smaller.                                                                                                                 |
        |                   | Use this method to configure the IM measurement and the signal analyzer for maximum dynamic range instead of             |
        |                   | measurement speed.                                                                                                       |
        |                   | Supported devices: PXIe-5665/5668.                                                                                       |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Segmented (2)     | Similar to the Dynamic Range method, this method also acquires a segmented spectrum, except that signal analyzer is not  |
        |                   | explicitly configured to provide maximum dynamic range. Use this method when the frequency separation of the two input   |
        |                   | tones is large and the measurement accuracy can be traded off for measurement speed.                                     |
        |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5860/5830/5831/5832, PXIe-5663/5665/5668.                          |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMMeasurementMethod, int):
                Specifies the method used to perform the IM measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMMeasurementMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_MEASUREMENT_METHOD.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_local_peak_search_enabled(self, selector_string):
        r"""Gets whether to enable a local peak search around the tone or intermod frequencies to account for small frequency
        offsets.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+-----------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                     |
        +==============+=================================================================================================================+
        | False (0)    | The measurement returns the power at the tone and intermod frequencies.                                         |
        +--------------+-----------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement performs a local peak search around the tone and intermod frequencies to return the peak power. |
        +--------------+-----------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMLocalPeakSearchEnabled):
                Specifies whether to enable a local peak search around the tone or intermod frequencies to account for small frequency
                offsets.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_LOCAL_PEAK_SEARCH_ENABLED.value
            )
            attr_val = enums.IMLocalPeakSearchEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_local_peak_search_enabled(self, selector_string, value):
        r"""Sets whether to enable a local peak search around the tone or intermod frequencies to account for small frequency
        offsets.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+-----------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                     |
        +==============+=================================================================================================================+
        | False (0)    | The measurement returns the power at the tone and intermod frequencies.                                         |
        +--------------+-----------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement performs a local peak search around the tone and intermod frequencies to return the peak power. |
        +--------------+-----------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMLocalPeakSearchEnabled, int):
                Specifies whether to enable a local peak search around the tone or intermod frequencies to account for small frequency
                offsets.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMLocalPeakSearchEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IM_LOCAL_PEAK_SEARCH_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the measurement computes the RBW.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+------------------------------------------------------------------------+
        | Name (Value) | Description                                                            |
        +==============+========================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the IM RBW attribute. |
        +--------------+------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                      |
        +--------------+------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMRbwFilterAutoBandwidth):
                Specifies whether the measurement computes the RBW.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_RBW_FILTER_AUTO_BANDWIDTH.value
            )
            attr_val = enums.IMRbwFilterAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the measurement computes the RBW.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+------------------------------------------------------------------------+
        | Name (Value) | Description                                                            |
        +==============+========================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the IM RBW attribute. |
        +--------------+------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                      |
        +--------------+------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMRbwFilterAutoBandwidth, int):
                Specifies whether the measurement computes the RBW.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMRbwFilterAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IM_RBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the RBW filter used to sweep the acquired signal, when you set the
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
                Specifies the bandwidth of the RBW filter used to sweep the acquired signal, when you set the
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
                updated_selector_string, attributes.AttributeID.IM_RBW_FILTER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the RBW filter used to sweep the acquired signal, when you set the
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
                Specifies the bandwidth of the RBW filter used to sweep the acquired signal, when you set the
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
                updated_selector_string, attributes.AttributeID.IM_RBW_FILTER_BANDWIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_type(self, selector_string):
        r"""Gets the response of the digital RBW filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Gaussian**.

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

            attr_val (enums.IMRbwFilterType):
                Specifies the response of the digital RBW filter.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_RBW_FILTER_TYPE.value
            )
            attr_val = enums.IMRbwFilterType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_type(self, selector_string, value):
        r"""Sets the response of the digital RBW filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Gaussian**.

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

            value (enums.IMRbwFilterType, int):
                Specifies the response of the digital RBW filter.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_RBW_FILTER_TYPE.value, value
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

        +--------------+--------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                          |
        +==============+======================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the IM Sweep Time attribute. |
        +--------------+--------------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the sweep time based on the value of the IM RBW attribute.  |
        +--------------+--------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMSweepTimeAuto):
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
                updated_selector_string, attributes.AttributeID.IM_SWEEP_TIME_AUTO.value
            )
            attr_val = enums.IMSweepTimeAuto(attr_val)
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

        +--------------+--------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                          |
        +==============+======================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the IM Sweep Time attribute. |
        +--------------+--------------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the sweep time based on the value of the IM RBW attribute.  |
        +--------------+--------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMSweepTimeAuto, int):
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
            value = value.value if type(value) is enums.IMSweepTimeAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_SWEEP_TIME_AUTO.value, value
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
                updated_selector_string, attributes.AttributeID.IM_SWEEP_TIME_INTERVAL.value
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
                updated_selector_string, attributes.AttributeID.IM_SWEEP_TIME_INTERVAL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the IM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The IM measurement uses the IM Averaging Count attribute as the number of acquisitions over which the IM measurement is  |
        |              | averaged.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMAveragingEnabled):
                Specifies whether to enable averaging for the IM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_AVERAGING_ENABLED.value
            )
            attr_val = enums.IMAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the IM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The IM measurement uses the IM Averaging Count attribute as the number of acquisitions over which the IM measurement is  |
        |              | averaged.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMAveragingEnabled, int):
                Specifies whether to enable averaging for the IM measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.IM_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.IM_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for the IM
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

            attr_val (enums.IMAveragingType):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for the IM
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
                updated_selector_string, attributes.AttributeID.IM_AVERAGING_TYPE.value
            )
            attr_val = enums.IMAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for the IM
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

            value (enums.IMAveragingType, int):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for the IM
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
            value = value.value if type(value) is enums.IMAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_AVERAGING_TYPE.value, value
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
        | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful   |
        |                     | for time-frequency analysis.                                                                                             |
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

            attr_val (enums.IMFftWindow):
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
                updated_selector_string, attributes.AttributeID.IM_FFT_WINDOW.value
            )
            attr_val = enums.IMFftWindow(attr_val)
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
        | Gaussian (4)        | Provides a good balance of spectral leakage, frequency resolution, and amplitude attenuation. This windowing is useful   |
        |                     | for time-frequency analysis.                                                                                             |
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

            value (enums.IMFftWindow, int):
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
            value = value.value if type(value) is enums.IMFftWindow else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_FFT_WINDOW.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_padding(self, selector_string):
        r"""Gets the factor by which the time-domain waveform is zero-padded before an FFT. The FFT size is given by the
        following formula:

        *FFT size* = *waveform size* * *padding*

        This attribute is used only when the acquisition span is less than the device instantaneous bandwidth.

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
                Specifies the factor by which the time-domain waveform is zero-padded before an FFT. The FFT size is given by the
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
                updated_selector_string, attributes.AttributeID.IM_FFT_PADDING.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_padding(self, selector_string, value):
        r"""Sets the factor by which the time-domain waveform is zero-padded before an FFT. The FFT size is given by the
        following formula:

        *FFT size* = *waveform size* * *padding*

        This attribute is used only when the acquisition span is less than the device instantaneous bandwidth.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the factor by which the time-domain waveform is zero-padded before an FFT. The FFT size is given by the
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
                updated_selector_string, attributes.AttributeID.IM_FFT_PADDING.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_if_output_power_offset_auto(self, selector_string):
        r"""Gets whether the measurement computes an IF output power level offset for the intermods to maximize the dynamic
        range of the signal analyzer. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement sets the IF output power level offset using the values of the IM Near IF Output Power Offset and IM Far  |
        |              | IF Output Power Offset attributes.                                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement computes an IF output power level offset for the intermods to improve the dynamic range of the IM        |
        |              | measurement.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMIFOutputPowerOffsetAuto):
                Specifies whether the measurement computes an IF output power level offset for the intermods to maximize the dynamic
                range of the signal analyzer. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_IF_OUTPUT_POWER_OFFSET_AUTO.value
            )
            attr_val = enums.IMIFOutputPowerOffsetAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_if_output_power_offset_auto(self, selector_string, value):
        r"""Sets whether the measurement computes an IF output power level offset for the intermods to maximize the dynamic
        range of the signal analyzer. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement sets the IF output power level offset using the values of the IM Near IF Output Power Offset and IM Far  |
        |              | IF Output Power Offset attributes.                                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement computes an IF output power level offset for the intermods to improve the dynamic range of the IM        |
        |              | measurement.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMIFOutputPowerOffsetAuto, int):
                Specifies whether the measurement computes an IF output power level offset for the intermods to maximize the dynamic
                range of the signal analyzer. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.IMIFOutputPowerOffsetAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IM_IF_OUTPUT_POWER_OFFSET_AUTO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_near_if_output_power_offset(self, selector_string):
        r"""Gets the offset by which to adjust the IF output power level for the intermods near the carrier channel to improve
        the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 dB.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the offset by which to adjust the IF output power level for the intermods near the carrier channel to improve
                the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IM_NEAR_IF_OUTPUT_POWER_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_near_if_output_power_offset(self, selector_string, value):
        r"""Sets the offset by which to adjust the IF output power level for the intermods near the carrier channel to improve
        the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the offset by which to adjust the IF output power level for the intermods near the carrier channel to improve
                the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

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
                attributes.AttributeID.IM_NEAR_IF_OUTPUT_POWER_OFFSET.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_far_if_output_power_offset(self, selector_string):
        r"""Gets the offset by which to adjust the IF output power level for the intermods that are far from the carrier
        channel to improve the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only
        if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 20 dB.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the offset by which to adjust the IF output power level for the intermods that are far from the carrier
                channel to improve the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only
                if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.IM_FAR_IF_OUTPUT_POWER_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_far_if_output_power_offset(self, selector_string, value):
        r"""Sets the offset by which to adjust the IF output power level for the intermods that are far from the carrier
        channel to improve the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only
        if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 20 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the offset by which to adjust the IF output power level for the intermods that are far from the carrier
                channel to improve the dynamic range of the signal analyzer. This value is expressed in dB. This attribute is used only
                if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

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
                attributes.AttributeID.IM_FAR_IF_OUTPUT_POWER_OFFSET.value,
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
        | Spectrum Frequency Bin (1) | An Individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
        |                            | frequency.                                                                                                               |
        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IMAmplitudeCorrectionType):
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
                updated_selector_string, attributes.AttributeID.IM_AMPLITUDE_CORRECTION_TYPE.value
            )
            attr_val = enums.IMAmplitudeCorrectionType(attr_val)
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
        | Spectrum Frequency Bin (1) | An Individual frequency bin in the spectrum is compensated with the external attenuation value corresponding to that     |
        |                            | frequency.                                                                                                               |
        +----------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IMAmplitudeCorrectionType, int):
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
            value = value.value if type(value) is enums.IMAmplitudeCorrectionType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.IM_AMPLITUDE_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the IM measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the IM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the IM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the IM measurement.

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
                updated_selector_string, attributes.AttributeID.IM_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for the IM measurement.

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
                Specifies the maximum number of threads used for parallelism for the IM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.IM_NUMBER_OF_ANALYSIS_THREADS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for the IM measurement.

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
                Specifies the maximum number of threads used for parallelism for the IM measurement.

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
                attributes.AttributeID.IM_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_auto_intermods_setup(
        self, selector_string, auto_intermods_setup_enabled, maximum_intermod_order
    ):
        r"""Configures whether the measurement computes the intermod frequencies or uses manually specified frequencies.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            auto_intermods_setup_enabled (enums.IMAutoIntermodsSetupEnabled, int):
                This parameter specifies whether the measurement computes the intermod frequencies or uses manually specified
                frequencies. The default value is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | The measurement uses the values that you specify for the IM Lower Intermod Freq and IM Upper Intermod Freq attributes.   |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement computes intermod frequencies. The number of intermods to measure is based on the value of the Maximum   |
                |              | Intermod Order parameter.                                                                                                |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            maximum_intermod_order (int):
                This parameter specifies the order up to which the RFmx driver measures odd order intermodulation products when you set
                the **Auto Intermods Setup Enabled** parameter to **True**. The lower and upper intermodulation products are measured
                for each order. The default value is **3**.

                +--------------+-------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                               |
                +==============+===========================================================================================+
                | 3 (3)        | The RFmx driver measures third order intermodulation products.                            |
                +--------------+-------------------------------------------------------------------------------------------+
                | 5 (5)        | The RFmx driver measures third and fifth order intermodulation products.                  |
                +--------------+-------------------------------------------------------------------------------------------+
                | 7 (7)        | The RFmx driver measures third, fifth, and seventh order intermodulation products.        |
                +--------------+-------------------------------------------------------------------------------------------+
                | 9 (9)        | The RFmx driver measures third, fifth, seventh, and ninth order intermodulation products. |
                +--------------+-------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            auto_intermods_setup_enabled = (
                auto_intermods_setup_enabled.value
                if type(auto_intermods_setup_enabled) is enums.IMAutoIntermodsSetupEnabled
                else auto_intermods_setup_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_auto_intermods_setup(
                updated_selector_string, auto_intermods_setup_enabled, maximum_intermod_order
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the IM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.IMAveragingEnabled, int):
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

            averaging_type (enums.IMAveragingType, int):
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
                if type(averaging_enabled) is enums.IMAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.IMAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fft(self, selector_string, fft_window, fft_padding):
        r"""Configures the window and FFT to obtain a spectrum for the IM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            fft_window (enums.IMFftWindow, int):
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
            fft_window = fft_window.value if type(fft_window) is enums.IMFftWindow else fft_window
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_fft(
                updated_selector_string, fft_window, fft_padding
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency_definition(self, selector_string, frequency_definition):
        r"""Configures whether you can specify the tones and intermod frequencies as either relative to the RF center frequency or
        as absolute frequencies.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            frequency_definition (enums.IMFrequencyDefinition, int):
                This parameter specifies whether you can specify the tones and intermod frequencies as either relative to the RF
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` or as absolute frequencies. The default value is
                **Relative**.

                +--------------+--------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                  |
                +==============+==============================================================================================================+
                | Relative (0) | The tone and intermod frequencies are relative to the RF center frequency.                                   |
                +--------------+--------------------------------------------------------------------------------------------------------------+
                | Absolute (1) | The tone and intermod frequencies are absolute frequencies. The measurement ignores the RF center frequency. |
                +--------------+--------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            frequency_definition = (
                frequency_definition.value
                if type(frequency_definition) is enums.IMFrequencyDefinition
                else frequency_definition
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_frequency_definition(
                updated_selector_string, frequency_definition
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fundamental_tones(
        self, selector_string, lower_tone_frequency, upper_tone_frequency
    ):
        r"""Configures the upper and lower frequencies in a two-tone input signal.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            lower_tone_frequency (float):
                This parameter specifies the frequency of the tone that has a lower frequency among the two tones in the input signal.
                This value is expressed in Hz. The default value is -1 MHz.

            upper_tone_frequency (float):
                This parameter specifies the frequency of the tone that has a higher frequency among the two tones in the input signal.
                This value is expressed in Hz. The default value is 1 MHz.

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
            error_code = self._interpreter.im_configure_fundamental_tones(
                updated_selector_string, lower_tone_frequency, upper_tone_frequency
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_intermod_array(
        self,
        selector_string,
        intermod_order,
        lower_intermod_frequency,
        upper_intermod_frequency,
        intermod_side,
        intermod_enabled,
    ):
        r"""Configures the intermod order, intermod side, lower intermod frequency, and upper intermod frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            intermod_order (int):
                This parameter specifies array of orders of the intermod. The default value is 3.

            lower_intermod_frequency (float):
                This parameter specifies an array of the frequencies of the lower intermodulation products. This value is expressed in
                Hz. The default value is -3 MHz.

            upper_intermod_frequency (float):
                This parameter specifies an array of frequencies of the upper intermodulation products. This value is expressed in Hz.
                The default value is 3 MHz.

            intermod_side (enums.IMIntermodSide, int):
                This parameter specifies whether to measure intermodulation products corresponding to both lower and upper intermod
                frequencies or either one of them. The default value is **Both**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Lower (0)    | Measures the intermodulation product corresponding to the Lower Intermod Frequency parameter.                            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Upper (1)    | Measures the intermodulation product corresponding to the Upper Intermod Frequency parameter.                            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Both (2)     | Measures the intermodulation product corresponding to the Lower Intermod Frequency and Upper Intermod Frequency          |
                |              | parameters.                                                                                                              |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            intermod_enabled (enums.IMIntermodEnabled, int):
                This parameter specifies whether to enable an intermod for the IM measurement. The default value is **True**.

                +--------------+------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                |
                +==============+============================================================================================================+
                | False (0)    | Disables the intermod for the IM measurement. The results for the disabled intermods are displayed as NaN. |
                +--------------+------------------------------------------------------------------------------------------------------------+
                | True (1)     | Enables the intermod for the IM measurement.                                                               |
                +--------------+------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            intermod_side = (
                [v.value for v in intermod_side]
                if (
                    isinstance(intermod_side, list)
                    and all(isinstance(v, enums.IMIntermodSide) for v in intermod_side)
                )
                else intermod_side
            )
            intermod_enabled = (
                [v.value for v in intermod_enabled]
                if (
                    isinstance(intermod_enabled, list)
                    and all(isinstance(v, enums.IMIntermodEnabled) for v in intermod_enabled)
                )
                else intermod_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_intermod_array(
                updated_selector_string,
                intermod_order,
                lower_intermod_frequency,
                upper_intermod_frequency,
                intermod_side,
                intermod_enabled,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_intermod(
        self,
        selector_string,
        intermod_order,
        lower_intermod_frequency,
        upper_intermod_frequency,
        intermod_side,
        intermod_enabled,
    ):
        r"""Configures the intermod order, intermod side, lower intermod frequency, and upper intermod frequency when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

        Use "intermod<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of intermod
                number.

                Example:

                "intermod0"

                You can use the :py:meth:`build_intermod_string` method  to build the selector string.

            intermod_order (int):
                This parameter specifies the order of the intermod. The default value is 3.

            lower_intermod_frequency (float):
                This parameter specifies the frequency of the lower intermodulation product. This value is expressed in Hz. The default
                value is -3 MHz.

            upper_intermod_frequency (float):
                This parameter specifies the frequency of the upper intermodulation product. This value is expressed in Hz. The default
                value is 3 MHz.

            intermod_side (enums.IMIntermodSide, int):
                This parameter specifies whether to measure intermodulation products corresponding to both lower and upper intermod
                frequencies or either one of them. The default value is **Both**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Lower (0)    | Measures the intermodulation product corresponding to the Lower Intermod Frequency parameter.                            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Upper (1)    | Measures the intermodulation product corresponding to the Upper Intermod Frequency parameter.                            |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Both (2)     | Measures the intermodulation product corresponding to both Lower Intermod Frequency and Upper Intermod Frequency         |
                |              | parameters.                                                                                                              |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            intermod_enabled (enums.IMIntermodEnabled, int):
                This parameter specifies whether to enable an intermod for the IM measurement. The default value is **True**.

                +--------------+-----------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                               |
                +==============+===========================================================================================================+
                | False (0)    | Disables an intermod for the IM measurement. The results for the disabled intermods are displayed as NaN. |
                +--------------+-----------------------------------------------------------------------------------------------------------+
                | True (1)     | Enables an intermod for the IM measurement.                                                               |
                +--------------+-----------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            intermod_side = (
                intermod_side.value
                if type(intermod_side) is enums.IMIntermodSide
                else intermod_side
            )
            intermod_enabled = (
                intermod_enabled.value
                if type(intermod_enabled) is enums.IMIntermodEnabled
                else intermod_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_intermod(
                updated_selector_string,
                intermod_order,
                lower_intermod_frequency,
                upper_intermod_frequency,
                intermod_side,
                intermod_enabled,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_method(self, selector_string, measurement_method):
        r"""Configures the method for performing the IM measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_method (enums.IMMeasurementMethod, int):
                This parameter specifies the method for performing the IM measurement. The default value is **Normal**.

                +-------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)      | Description                                                                                                              |
                +===================+==========================================================================================================================+
                | Normal (0)        | The IM measurement acquires the spectrum using the same signal analyzer settings across frequency bands. Use this        |
                |                   | method when the fundamental tone separation is not large.                                                                |
                |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5830/5831/5832/5860, PXIe-5663/5665/5668.                          |
                +-------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Dynamic Range (1) | The IM measurement acquires a segmented spectrum using the signal analyzer specific optimizations for different          |
                |                   | frequency bands. The spectrum is acquired in segments, one per tone or intermod frequency to be measured. The span of    |
                |                   | each acquired spectral segment is equal to the frequency separation between the two input tones, or 1 MHz, whichever is  |
                |                   | smaller.                                                                                                                 |
                |                   | Use this method to configure the IM measurement and the signal analyzer for maximum dynamic range instead of             |
                |                   | measurement speed.                                                                                                       |
                |                   | Supported devices: PXIe-5665/5668                                                                                        |
                +-------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Segmented (2)     | Similar to the Dynamic Range method, this method also acquires a segmented spectrum, except that signal analyzer is not  |
                |                   | explicitly configured to provide maximum dynamic range. Use this method when the frequency separation of the two input   |
                |                   | tones is large and the measurement accuracy can be traded off for measurement speed.                                     |
                |                   | Supported devices: PXIe-5644/5645/5646/5840/5841/5842/5830/5831/5832, PXIe-5663/5665/5668                                |
                +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            measurement_method = (
                measurement_method.value
                if type(measurement_method) is enums.IMMeasurementMethod
                else measurement_method
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_measurement_method(
                updated_selector_string, measurement_method
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_intermods(self, selector_string, number_of_intermods):
        r"""Configures the number of intermods to measure when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_INTERMODS_SETUP_ENABLED` attribute to **False**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_intermods (int):
                This parameter specifies the number of intermods to measure when you set the IM Auto Intermods Setup Enabled attribute
                to **False**. The default value is 1.

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
            error_code = self._interpreter.im_configure_number_of_intermods(
                updated_selector_string, number_of_intermods
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the RBW filter.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw_auto (enums.IMRbwFilterAutoBandwidth, int):
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

            rbw_filter_type (enums.IMRbwFilterType, int):
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
                rbw_auto.value if type(rbw_auto) is enums.IMRbwFilterAutoBandwidth else rbw_auto
            )
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.IMRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_rbw_filter(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
            )
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

            sweep_time_auto (enums.IMSweepTimeAuto, int):
                This parameter specifies whether the measurement computes the sweep time. The default value is **True**.

                +--------------+--------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                |
                +==============+============================================================================================+
                | False (0)    | The measurement uses the sweep time that you specify in the Sweep Time Interval parameter. |
                +--------------+--------------------------------------------------------------------------------------------+
                | True (1)     | The measurement computes the sweep time based on the value of the IM RBW attribute.        |
                +--------------+--------------------------------------------------------------------------------------------+

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
                if type(sweep_time_auto) is enums.IMSweepTimeAuto
                else sweep_time_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.im_configure_sweep_time(
                updated_selector_string, sweep_time_auto, sweep_time_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
