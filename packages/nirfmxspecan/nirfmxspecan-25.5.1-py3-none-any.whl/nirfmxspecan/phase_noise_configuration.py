"""Provides methods to configure the PhaseNoise measurement."""

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


class PhaseNoiseConfiguration(object):
    """Provides methods to configure the PhaseNoise measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the PhaseNoise measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the phase noise measurement.

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
                Specifies whether to enable the phase noise measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the phase noise measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the phase noise measurement.

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
                attributes.AttributeID.PHASENOISE_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_definition(self, selector_string):
        r"""Gets how the measurement computes offset subranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Auto**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | Specify the offset sub-ranges used for the measurement. Use the PhaseNoise Range Start Freq attribute and the            |
        |              | PhaseNoise Range Stop Freq attribute to configure single or multiple range start and range stop frequencies.             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Auto (1)     | Measurement computes offset sub-ranges by dividing the user configured offset range into multiple decade sub-ranges.     |
        |              | The range is specified by the PhaseNoise Start Freq and the PhaseNoise Stop Freq attributes.                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PhaseNoiseRangeDefinition):
                Specifies how the measurement computes offset subranges.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_RANGE_DEFINITION.value
            )
            attr_val = enums.PhaseNoiseRangeDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_definition(self, selector_string, value):
        r"""Sets how the measurement computes offset subranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Auto**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | Specify the offset sub-ranges used for the measurement. Use the PhaseNoise Range Start Freq attribute and the            |
        |              | PhaseNoise Range Stop Freq attribute to configure single or multiple range start and range stop frequencies.             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Auto (1)     | Measurement computes offset sub-ranges by dividing the user configured offset range into multiple decade sub-ranges.     |
        |              | The range is specified by the PhaseNoise Start Freq and the PhaseNoise Stop Freq attributes.                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PhaseNoiseRangeDefinition, int):
                Specifies how the measurement computes offset subranges.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PhaseNoiseRangeDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_RANGE_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_start_frequency(self, selector_string):
        r"""Gets the start frequency of the offset frequency range when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1000.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start frequency of the offset frequency range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PHASENOISE_START_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_start_frequency(self, selector_string, value):
        r"""Sets the start frequency of the offset frequency range when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start frequency of the offset frequency range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

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
                attributes.AttributeID.PHASENOISE_START_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_stop_frequency(self, selector_string):
        r"""Gets the stop frequency of the offset frequency range when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1E+06.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the stop frequency of the offset frequency range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PHASENOISE_STOP_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_stop_frequency(self, selector_string, value):
        r"""Sets the stop frequency of the offset frequency range when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1E+06.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the stop frequency of the offset frequency range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

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
                attributes.AttributeID.PHASENOISE_STOP_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_percentage(self, selector_string):
        r"""Gets the RBW as a percentage of the start frequency of each subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the RBW as a percentage of the start frequency of each subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.PHASENOISE_RBW_PERCENTAGE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_percentage(self, selector_string, value):
        r"""Sets the RBW as a percentage of the start frequency of each subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the RBW as a percentage of the start frequency of each subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

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
                attributes.AttributeID.PHASENOISE_RBW_PERCENTAGE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_ranges(self, selector_string):
        r"""Gets the number of manual ranges.

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
                Specifies the number of manual ranges.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_NUMBER_OF_RANGES.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_ranges(self, selector_string, value):
        r"""Sets the number of manual ranges.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of manual ranges.

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
                attributes.AttributeID.PHASENOISE_NUMBER_OF_RANGES.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_start_frequency(self, selector_string):
        r"""Gets the start frequency for the specified subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1000.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start frequency for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_START_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_start_frequency(self, selector_string, value):
        r"""Sets the start frequency for the specified subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1000.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start frequency for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_START_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_stop_frequency(self, selector_string):
        r"""Gets the stop frequency for the specified subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1E+06.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the stop frequency for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_STOP_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_stop_frequency(self, selector_string, value):
        r"""Sets the stop frequency for the specified subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1E+06.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the stop frequency for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_STOP_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_rbw_percentage(self, selector_string):
        r"""Gets the RBW as a percentage of the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY`
        attribute of the specified subrange when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION`
        attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the RBW as a percentage of the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY`
                attribute of the specified subrange when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION`
                attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_RBW_PERCENTAGE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_rbw_percentage(self, selector_string, value):
        r"""Sets the RBW as a percentage of the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY`
        attribute of the specified subrange when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION`
        attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the RBW as a percentage of the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_START_FREQUENCY`
                attribute of the specified subrange when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION`
                attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_RBW_PERCENTAGE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_range_averaging_count(self, selector_string):
        r"""Gets the averaging count for the specified subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the averaging count for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_AVERAGING_COUNT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_range_averaging_count(self, selector_string, value):
        r"""Sets the averaging count for the specified subrange when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Use "range<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the averaging count for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

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
                attributes.AttributeID.PHASENOISE_RANGE_AVERAGING_COUNT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_multiplier(self, selector_string):
        r"""Gets the factor by which you increase the averaging count for each range. This setting applies to both **Auto**
        and **Manual** range definitions.

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
                Specifies the factor by which you increase the averaging count for each range. This setting applies to both **Auto**
                and **Manual** range definitions.

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
                attributes.AttributeID.PHASENOISE_AVERAGING_MULTIPLIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_multiplier(self, selector_string, value):
        r"""Sets the factor by which you increase the averaging count for each range. This setting applies to both **Auto**
        and **Manual** range definitions.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the factor by which you increase the averaging count for each range. This setting applies to both **Auto**
                and **Manual** range definitions.

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
                attributes.AttributeID.PHASENOISE_AVERAGING_MULTIPLIER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_window(self, selector_string):
        r"""Gets the FFT window to use.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Hamming**.

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

            attr_val (enums.PhaseNoiseFftWindow):
                Specifies the FFT window to use.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_FFT_WINDOW.value
            )
            attr_val = enums.PhaseNoiseFftWindow(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_window(self, selector_string, value):
        r"""Sets the FFT window to use.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Hamming**.

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

            value (enums.PhaseNoiseFftWindow, int):
                Specifies the FFT window to use.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PhaseNoiseFftWindow else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_FFT_WINDOW.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_smoothing_type(self, selector_string):
        r"""Gets the smoothing type used to smoothen the measured log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Logarithmic**.

        +-----------------+-------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                               |
        +=================+===========================================================================================+
        | None (0)        | Smoothing is disabled.                                                                    |
        +-----------------+-------------------------------------------------------------------------------------------+
        | Linear (1)      | Performs linear moving average filtering on the measured phase noise log plot trace.      |
        +-----------------+-------------------------------------------------------------------------------------------+
        | Logarithmic (2) | Performs logarithmic moving average filtering on the measured phase noise log plot trace. |
        +-----------------+-------------------------------------------------------------------------------------------+
        | Median (3)      | Performs moving median filtering on the measured phase noise log plot trace.              |
        +-----------------+-------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PhaseNoiseSmoothingType):
                Specifies the smoothing type used to smoothen the measured log plot trace.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_SMOOTHING_TYPE.value
            )
            attr_val = enums.PhaseNoiseSmoothingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_smoothing_type(self, selector_string, value):
        r"""Sets the smoothing type used to smoothen the measured log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Logarithmic**.

        +-----------------+-------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                               |
        +=================+===========================================================================================+
        | None (0)        | Smoothing is disabled.                                                                    |
        +-----------------+-------------------------------------------------------------------------------------------+
        | Linear (1)      | Performs linear moving average filtering on the measured phase noise log plot trace.      |
        +-----------------+-------------------------------------------------------------------------------------------+
        | Logarithmic (2) | Performs logarithmic moving average filtering on the measured phase noise log plot trace. |
        +-----------------+-------------------------------------------------------------------------------------------+
        | Median (3)      | Performs moving median filtering on the measured phase noise log plot trace.              |
        +-----------------+-------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PhaseNoiseSmoothingType, int):
                Specifies the smoothing type used to smoothen the measured log plot trace.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PhaseNoiseSmoothingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_SMOOTHING_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_smoothing_percentage(self, selector_string):
        r"""Gets the number of trace points to use in the moving average filter as a percentage of total number of points in
        the log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 2.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the number of trace points to use in the moving average filter as a percentage of total number of points in
                the log plot trace.

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
                attributes.AttributeID.PHASENOISE_SMOOTHING_PERCENTAGE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_smoothing_percentage(self, selector_string, value):
        r"""Sets the number of trace points to use in the moving average filter as a percentage of total number of points in
        the log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 2.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the number of trace points to use in the moving average filter as a percentage of total number of points in
                the log plot trace.

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
                attributes.AttributeID.PHASENOISE_SMOOTHING_PERCENTAGE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_spot_noise_frequency_list(self, selector_string):
        r"""Gets an array of offset frequencies at which the phase noise is measured using the smoothed log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of offset frequencies at which the phase noise is measured using the smoothed log plot trace.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_SPOT_NOISE_FREQUENCY_LIST.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_spot_noise_frequency_list(self, selector_string, value):
        r"""Sets an array of offset frequencies at which the phase noise is measured using the smoothed log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of offset frequencies at which the phase noise is measured using the smoothed log plot trace.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_SPOT_NOISE_FREQUENCY_LIST.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_integrated_noise_range_definition(self, selector_string):
        r"""Gets the frequency range for integrated noise measurements.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is ** Measurement**.

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                                              |
        +=================+==========================================================================================================================+
        | None (0)        | Integrated noise measurement is not computed.                                                                            |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Measurement (1) | The complete log plot frequency range, considered as a single range, is used for computing integrated measurements.      |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Custom (2)      | The measurement range(s) specified by                                                                                    |
        |                 | PhaseNoise Integrated Noise Start Freq attribute and the PhaseNoise Integrated Noise Stop Freq attribute is used for     |
        |                 | computing integrated measurements.                                                                                       |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PhaseNoiseIntegratedNoiseRangeDefinition):
                Specifies the frequency range for integrated noise measurements.

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
                attributes.AttributeID.PHASENOISE_INTEGRATED_NOISE_RANGE_DEFINITION.value,
            )
            attr_val = enums.PhaseNoiseIntegratedNoiseRangeDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_integrated_noise_range_definition(self, selector_string, value):
        r"""Sets the frequency range for integrated noise measurements.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is ** Measurement**.

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                                              |
        +=================+==========================================================================================================================+
        | None (0)        | Integrated noise measurement is not computed.                                                                            |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Measurement (1) | The complete log plot frequency range, considered as a single range, is used for computing integrated measurements.      |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Custom (2)      | The measurement range(s) specified by                                                                                    |
        |                 | PhaseNoise Integrated Noise Start Freq attribute and the PhaseNoise Integrated Noise Stop Freq attribute is used for     |
        |                 | computing integrated measurements.                                                                                       |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PhaseNoiseIntegratedNoiseRangeDefinition, int):
                Specifies the frequency range for integrated noise measurements.

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
                value.value
                if type(value) is enums.PhaseNoiseIntegratedNoiseRangeDefinition
                else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_INTEGRATED_NOISE_RANGE_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_integrated_noise_start_frequency(self, selector_string):
        r"""Gets an array of the start frequencies for integrated noise measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the start frequencies for integrated noise measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_INTEGRATED_NOISE_START_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_integrated_noise_start_frequency(self, selector_string, value):
        r"""Sets an array of the start frequencies for integrated noise measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the start frequencies for integrated noise measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_INTEGRATED_NOISE_START_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_integrated_noise_stop_frequency(self, selector_string):
        r"""Gets an array of the stop frequencies for integrated noise measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the stop frequencies for integrated noise measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_INTEGRATED_NOISE_STOP_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_integrated_noise_stop_frequency(self, selector_string, value):
        r"""Sets an array of the stop frequencies for integrated noise measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the stop frequencies for integrated noise measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.INTEGRATED_NOISE_RANGE_DEFINITION` attribute to **Custom**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_INTEGRATED_NOISE_STOP_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_spur_removal_enabled(self, selector_string):
        r"""Gets whether to remove spurs from the log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+----------------------------------------------+
        | Name (Value) | Description                                  |
        +==============+==============================================+
        | False (0)    | Disables spur removal on the log plot trace. |
        +--------------+----------------------------------------------+
        | True (1)     | Enables spur removal on the log plot trace.  |
        +--------------+----------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PhaseNoiseSpurRemovalEnabled):
                Specifies whether to remove spurs from the log plot trace.

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
                attributes.AttributeID.PHASENOISE_SPUR_REMOVAL_ENABLED.value,
            )
            attr_val = enums.PhaseNoiseSpurRemovalEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_spur_removal_enabled(self, selector_string, value):
        r"""Sets whether to remove spurs from the log plot trace.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+----------------------------------------------+
        | Name (Value) | Description                                  |
        +==============+==============================================+
        | False (0)    | Disables spur removal on the log plot trace. |
        +--------------+----------------------------------------------+
        | True (1)     | Enables spur removal on the log plot trace.  |
        +--------------+----------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PhaseNoiseSpurRemovalEnabled, int):
                Specifies whether to remove spurs from the log plot trace.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PhaseNoiseSpurRemovalEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_SPUR_REMOVAL_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_spur_removal_peak_excursion(self, selector_string):
        r"""Gets the peak excursion to be used when spur detection is performed.

        Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
        information on spur removal.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 6.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the peak excursion to be used when spur detection is performed.

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
                attributes.AttributeID.PHASENOISE_SPUR_REMOVAL_PEAK_EXCURSION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_spur_removal_peak_excursion(self, selector_string, value):
        r"""Sets the peak excursion to be used when spur detection is performed.

        Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
        information on spur removal.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 6.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the peak excursion to be used when spur detection is performed.

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
                attributes.AttributeID.PHASENOISE_SPUR_REMOVAL_PEAK_EXCURSION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cancellation_enabled(self, selector_string):
        r"""Gets whether to enable or disable the phase noise cancellation.

        Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
        information on phase noise cancellation.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+------------------------------------+
        | Name (Value) | Description                        |
        +==============+====================================+
        | False (0)    | Disables phase noise cancellation. |
        +--------------+------------------------------------+
        | True (1)     | Enables phase noise cancellation.  |
        +--------------+------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.PhaseNoiseCancellationEnabled):
                Specifies whether to enable or disable the phase noise cancellation.

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
                attributes.AttributeID.PHASENOISE_CANCELLATION_ENABLED.value,
            )
            attr_val = enums.PhaseNoiseCancellationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cancellation_enabled(self, selector_string, value):
        r"""Sets whether to enable or disable the phase noise cancellation.

        Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
        information on phase noise cancellation.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+------------------------------------+
        | Name (Value) | Description                        |
        +==============+====================================+
        | False (0)    | Disables phase noise cancellation. |
        +--------------+------------------------------------+
        | True (1)     | Enables phase noise cancellation.  |
        +--------------+------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.PhaseNoiseCancellationEnabled, int):
                Specifies whether to enable or disable the phase noise cancellation.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.PhaseNoiseCancellationEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_CANCELLATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cancellation_threshold(self, selector_string):
        r"""Gets the minimum difference between the reference and pre-cancellation traces that must exist before cancellation
        is performed.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.01.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the minimum difference between the reference and pre-cancellation traces that must exist before cancellation
                is performed.

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
                attributes.AttributeID.PHASENOISE_CANCELLATION_THRESHOLD.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cancellation_threshold(self, selector_string, value):
        r"""Sets the minimum difference between the reference and pre-cancellation traces that must exist before cancellation
        is performed.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.01.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the minimum difference between the reference and pre-cancellation traces that must exist before cancellation
                is performed.

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
                attributes.AttributeID.PHASENOISE_CANCELLATION_THRESHOLD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cancellation_frequency(self, selector_string):
        r"""Gets an array of frequencies where the reference phase noise has been measured.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of frequencies where the reference phase noise has been measured.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f32_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_CANCELLATION_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cancellation_frequency(self, selector_string, value):
        r"""Sets an array of frequencies where the reference phase noise has been measured.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of frequencies where the reference phase noise has been measured.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f32_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_CANCELLATION_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cancellation_reference_phase_noise(self, selector_string):
        r"""Gets an array of reference phase noise at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CANCELLATION_FREQUENCY` attribute .

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of reference phase noise at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CANCELLATION_FREQUENCY` attribute .

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f32_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_CANCELLATION_REFERENCE_PHASE_NOISE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cancellation_reference_phase_noise(self, selector_string, value):
        r"""Sets an array of reference phase noise at the frequencies specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CANCELLATION_FREQUENCY` attribute .

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of reference phase noise at the frequencies specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CANCELLATION_FREQUENCY` attribute .

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.set_attribute_f32_array(
                updated_selector_string,
                attributes.AttributeID.PHASENOISE_CANCELLATION_REFERENCE_PHASE_NOISE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the Phase Noise measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the Phase Noise measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.PHASENOISE_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the Phase Noise measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the Phase Noise measurement.

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
                attributes.AttributeID.PHASENOISE_ALL_TRACES_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_auto_range(
        self, selector_string, start_frequency, stop_frequency, rbw_percentage
    ):
        r"""Configures the offset range and the RBW percentage when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            start_frequency (float):
                This parameter specifies the start frequency of the offset frequency range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**. This value is expressed in Hz.
                The default value is 1000.

            stop_frequency (float):
                This parameter specifies the stop frequency of the offset frequency range when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**. This value is expressed in Hz.
                The default value is 1000000.

            rbw_percentage (float):
                This parameter specifies the RBW as a percentage of the start frequency of each subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**. This value is expressed as a
                percentage. The default value is 10.

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
            error_code = self._interpreter.phasenoise_configure_auto_range(
                updated_selector_string, start_frequency, stop_frequency, rbw_percentage
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging_multiplier(self, selector_string, averaging_multiplier):
        r"""Configures the averaging multiplier.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_multiplier (int):
                This parameter specifies the factor by which you increase the averaging count for each range. This setting applies to
                both **Auto** and **Manual** range definitions. The default value is 1.

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
            error_code = self._interpreter.phasenoise_configure_averaging_multiplier(
                updated_selector_string, averaging_multiplier
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_cancellation(
        self,
        selector_string,
        cancellation_enabled,
        cancellation_threshold,
        frequency,
        reference_phase_noise,
    ):
        r"""Configures phase noise cancellation for the measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            cancellation_enabled (enums.PhaseNoiseCancellationEnabled, int):
                This parameter specifies whether to enable or disable the phase noise cancellation.

                Refer to the `Phase Noise <www.ni.com/docs/en-US/bundle/rfmx-specan/page/phase-noise.html>`_ topic for more
                information on phase noise cancellation.

                +--------------+------------------------------------+
                | Name (Value) | Description                        |
                +==============+====================================+
                | False (0)    | Disables phase noise cancellation. |
                +--------------+------------------------------------+
                | True (1)     | Enables phase noise cancellation.  |
                +--------------+------------------------------------+

            cancellation_threshold (float):
                This parameter specifies the minimum difference between the reference and pre-cancellation traces that must exist
                before cancellation is performed. This value is expressed in dB.

            frequency (float):
                This parameter specifies an array of frequencies where the reference phase noise has been measured. This value is
                expressed in Hz.

            reference_phase_noise (float):
                This parameter specifies an array of the reference phase noise at the frequencies specified by the phase noise
                cancellation frequency parameter. This value is expressed in dBc/Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            cancellation_enabled = (
                cancellation_enabled.value
                if type(cancellation_enabled) is enums.PhaseNoiseCancellationEnabled
                else cancellation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.phasenoise_configure_cancellation(
                updated_selector_string,
                cancellation_enabled,
                cancellation_threshold,
                frequency,
                reference_phase_noise,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_integrated_noise(
        self,
        selector_string,
        integrated_noise_range_definition,
        integrated_noise_start_frequency,
        integrated_noise_stop_frequency,
    ):
        r"""Configures the integrated noise ranges. The smoothed log plot trace is used when computing integrated measurements.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            integrated_noise_range_definition (enums.PhaseNoiseIntegratedNoiseRangeDefinition, int):
                This parameter specifies the frequency range for the integrated noise measurements.

            integrated_noise_start_frequency (float):
                This parameter specifies an array of the start frequencies when you set the **Integrated Noise Range Definition**
                parameter to **Custom**. This value is expressed in Hz.

            integrated_noise_stop_frequency (float):
                This parameter specifies an array of the stop frequencies when you set the **Integrated Noise Range Definition**
                parameter to **Custom**. This value is expressed in Hz.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            integrated_noise_range_definition = (
                integrated_noise_range_definition.value
                if type(integrated_noise_range_definition)
                is enums.PhaseNoiseIntegratedNoiseRangeDefinition
                else integrated_noise_range_definition
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.phasenoise_configure_integrated_noise(
                updated_selector_string,
                integrated_noise_range_definition,
                integrated_noise_start_frequency,
                integrated_noise_stop_frequency,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_ranges(self, selector_string, number_of_ranges):
        r"""Configures the number of offset ranges when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to ** Manual**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_ranges (int):
                This parameter specifies the number of manual ranges. The default value is 1.

                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)    | Description                                                                                                              |
                +=================+==========================================================================================================================+
                | None (0)        | Integrated noise measurement is not computed.                                                                            |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | Measurement (1) | The complete log plot frequency range, considered as a single range, is used for computing integrated measurements.      |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | Custom (2)      | The measurement range(s) specified by                                                                                    |
                |                 | PhaseNoise Integrated Noise Start Freq attribute and the PhaseNoise Integrated Noise Stop Freq attribute is used for     |
                |                 | computing integrated measurements.                                                                                       |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+

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
            error_code = self._interpreter.phasenoise_configure_number_of_ranges(
                updated_selector_string, number_of_ranges
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_array(
        self,
        selector_string,
        range_start_frequency,
        range_stop_frequency,
        range_rbw_percentage,
        range_averaging_count,
    ):
        r"""Configures an array of the offset range, RBW percentage and averaging count when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            range_start_frequency (float):
                This parameter specifies the start frequency of the offset frequency for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Auto**. This value is expressed in Hz.
                The default value is 1000..

            range_stop_frequency (float):
                This parameter Specifies the stop offset frequency for the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**. This value is expressed in
                Hz. The default value is 1000000.

            range_rbw_percentage (float):
                This parameter specifies the RBW as a percentage of the start frequency of the specified subrange when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.RANGE_DEFINITION` attribute to **Manual**. This value is expressed as a
                percentage. The default value is 10.

            range_averaging_count (int):
                This parameter specifies the averaging count for the specified range. The default value is 10.

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
            error_code = self._interpreter.phasenoise_configure_range_array(
                updated_selector_string,
                range_start_frequency,
                range_stop_frequency,
                range_rbw_percentage,
                range_averaging_count,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_range_definition(self, selector_string, range_definition):
        r"""Specifies how the measurement computes offset subranges.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            range_definition (enums.PhaseNoiseRangeDefinition, int):
                This parameter specifies how the measurement computes offset subranges.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | Specify the offset sub-ranges used for the measurement. Use the PhaseNoise Range Start Freq attribute and the            |
                |              | PhaseNoise Range Stop Freq attribute to configure single or multiple range start and range stop frequencies.             |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Auto (1)     | Measurement computes offset sub-ranges by dividing the user configured offset range into multiple decade sub-ranges.     |
                |              | The range is specified by the PhaseNoise Start Freq and the PhaseNoise Stop Freq attributes.                             |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            range_definition = (
                range_definition.value
                if type(range_definition) is enums.PhaseNoiseRangeDefinition
                else range_definition
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.phasenoise_configure_range_definition(
                updated_selector_string, range_definition
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_smoothing(self, selector_string, smoothing_type, smoothing_percentage):
        r"""Configures the smoothing type and smoothing percentage used to smoothen the measured log plot trace.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            smoothing_type (enums.PhaseNoiseSmoothingType, int):
                This parameter specifies the smoothing type used to smoothen the measured log plot trace. The default value is
                Logarithmic.

                +-----------------+-------------------------------------------------------------------------------------------+
                | Name (Value)    | Description                                                                               |
                +=================+===========================================================================================+
                | None (0)        | Smoothing is disabled.                                                                    |
                +-----------------+-------------------------------------------------------------------------------------------+
                | Linear (1)      | Performs linear moving average filtering on the measured phase noise log plot trace.      |
                +-----------------+-------------------------------------------------------------------------------------------+
                | Logarithmic (2) | Performs logarithmic moving average filtering on the measured phase noise log plot trace. |
                +-----------------+-------------------------------------------------------------------------------------------+
                | Median (3)      | Performs moving median filtering on the measured phase noise log plot trace.              |
                +-----------------+-------------------------------------------------------------------------------------------+

            smoothing_percentage (float):
                This parameter specifies the number of points to use in the moving average filter as a percentage of total number of
                points in the log plot trace. This value is expressed as a percentage. The default value is 2.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            smoothing_type = (
                smoothing_type.value
                if type(smoothing_type) is enums.PhaseNoiseSmoothingType
                else smoothing_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.phasenoise_configure_smoothing(
                updated_selector_string, smoothing_type, smoothing_percentage
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_spot_noise_frequency_list(self, selector_string, frequency_list):
        r"""Configures a list of frequencies at which the phase noise values are to be read using the smoothed log plot trace.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            frequency_list (float):
                This parameter specifies an array of offset frequencies at which the corresponding phase noise is measured using the
                smoothed log plot trace. This value is expressed in Hz. The default value is an empty array.

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
            error_code = self._interpreter.phasenoise_configure_spot_noise_frequency_list(
                updated_selector_string, frequency_list
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_spur_removal(self, selector_string, spur_removal_enabled, peak_excursion):
        r"""Configures enabling or disabling of the spur removal and the peak excursion to use when spur removal is enabled.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            spur_removal_enabled (enums.PhaseNoiseSpurRemovalEnabled, int):
                This parameter specifies whether the spur removal is enabled or disabled.

                +--------------+----------------------------------------------+
                | Name (Value) | Description                                  |
                +==============+==============================================+
                | False (0)    | Disables spur removal on the log plot trace. |
                +--------------+----------------------------------------------+
                | True (1)     | Enables spur removal on the log plot trace.  |
                +--------------+----------------------------------------------+

            peak_excursion (float):
                This parameter specifies the peak excursion to be used when spur detection is performed.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            spur_removal_enabled = (
                spur_removal_enabled.value
                if type(spur_removal_enabled) is enums.PhaseNoiseSpurRemovalEnabled
                else spur_removal_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.phasenoise_configure_spur_removal(
                updated_selector_string, spur_removal_enabled, peak_excursion
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
