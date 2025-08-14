"""Provides methods to configure the Acp measurement."""

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


class AcpConfiguration(object):
    """Provides methods to configure the Acp measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Acp measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the ACP measurement.

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
                Specifies whether to enable the ACP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the ACP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the ACP measurement.

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
                updated_selector_string, attributes.AttributeID.ACP_MEASUREMENT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_carriers(self, selector_string):
        r"""Gets the number of carriers.

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
                Specifies the number of carriers.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_NUMBER_OF_CARRIERS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_carriers(self, selector_string, value):
        r"""Sets the number of carriers.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of carriers.

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
                updated_selector_string, attributes.AttributeID.ACP_NUMBER_OF_CARRIERS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_mode(self, selector_string):
        r"""Gets whether to consider the carrier power as part of the total carrier power measurement.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Active**.

        +--------------+-------------------------------------------------------------------------+
        | Name (Value) | Description                                                             |
        +==============+=========================================================================+
        | Passive (0)  | The carrier power is not considered as part of the total carrier power. |
        +--------------+-------------------------------------------------------------------------+
        | Active (1)   | The carrier power is considered as part of the total carrier power.     |
        +--------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpCarrierMode):
                Specifies whether to consider the carrier power as part of the total carrier power measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_CARRIER_MODE.value
            )
            attr_val = enums.AcpCarrierMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_mode(self, selector_string, value):
        r"""Sets whether to consider the carrier power as part of the total carrier power measurement.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Active**.

        +--------------+-------------------------------------------------------------------------+
        | Name (Value) | Description                                                             |
        +==============+=========================================================================+
        | Passive (0)  | The carrier power is not considered as part of the total carrier power. |
        +--------------+-------------------------------------------------------------------------+
        | Active (1)   | The carrier power is considered as part of the total carrier power.     |
        +--------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpCarrierMode, int):
                Specifies whether to consider the carrier power as part of the total carrier power measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpCarrierMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_CARRIER_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_frequency(self, selector_string):
        r"""Gets the center frequency of the carrier, relative to the RF
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the center frequency of the carrier, relative to the RF
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.ACP_CARRIER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_frequency(self, selector_string, value):
        r"""Sets the center frequency of the carrier, relative to the RF
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the center frequency of the carrier, relative to the RF
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. This value is expressed in Hz.

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
                updated_selector_string, attributes.AttributeID.ACP_CARRIER_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_integration_bandwidth(self, selector_string):
        r"""Gets the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.

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
                attributes.AttributeID.ACP_CARRIER_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_integration_bandwidth(self, selector_string, value):
        r"""Sets the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.

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
                attributes.AttributeID.ACP_CARRIER_INTEGRATION_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rrc_filter_enabled(self, selector_string):
        r"""Gets whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before measuring the
        carrier channel power.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                        |
        +==============+====================================================================================================================+
        | False (0)    | The channel power of the acquired carrier channel is measured directly.                                            |
        +--------------+--------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement applies the RRC filter on the acquired carrier channel before measuring the carrier channel power. |
        +--------------+--------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpCarrierRrcFilterEnabled):
                Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before measuring the
                carrier channel power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_CARRIER_RRC_FILTER_ENABLED.value
            )
            attr_val = enums.AcpCarrierRrcFilterEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rrc_filter_enabled(self, selector_string, value):
        r"""Sets whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before measuring the
        carrier channel power.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                        |
        +==============+====================================================================================================================+
        | False (0)    | The channel power of the acquired carrier channel is measured directly.                                            |
        +--------------+--------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement applies the RRC filter on the acquired carrier channel before measuring the carrier channel power. |
        +--------------+--------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpCarrierRrcFilterEnabled, int):
                Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before measuring the
                carrier channel power.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpCarrierRrcFilterEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_CARRIER_RRC_FILTER_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rrc_filter_alpha(self, selector_string):
        r"""Gets the roll-off factor for the root-raised-cosine (RRC) filter.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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
                updated_selector_string, attributes.AttributeID.ACP_CARRIER_RRC_FILTER_ALPHA.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rrc_filter_alpha(self, selector_string, value):
        r"""Sets the roll-off factor for the root-raised-cosine (RRC) filter.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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
                updated_selector_string,
                attributes.AttributeID.ACP_CARRIER_RRC_FILTER_ALPHA.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_offsets(self, selector_string):
        r"""Gets the number of offset channels.

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
                Specifies the number of offset channels.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_NUMBER_OF_OFFSETS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_offsets(self, selector_string, value):
        r"""Sets the number of offset channels.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of offset channels.

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
                updated_selector_string, attributes.AttributeID.ACP_NUMBER_OF_OFFSETS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_enabled(self, selector_string):
        r"""Gets whether to enable the offset channel for ACP measurement.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+--------------------------------------------------+
        | Name (Value) | Description                                      |
        +==============+==================================================+
        | False (0)    | Disables the offset channel for ACP measurement. |
        +--------------+--------------------------------------------------+
        | True (1)     | Enables the offset channel for ACP measurement.  |
        +--------------+--------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpOffsetEnabled):
                Specifies whether to enable the offset channel for ACP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_ENABLED.value
            )
            attr_val = enums.AcpOffsetEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_enabled(self, selector_string, value):
        r"""Sets whether to enable the offset channel for ACP measurement.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+--------------------------------------------------+
        | Name (Value) | Description                                      |
        +==============+==================================================+
        | False (0)    | Disables the offset channel for ACP measurement. |
        +--------------+--------------------------------------------------+
        | True (1)     | Enables the offset channel for ACP measurement.  |
        +--------------+--------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpOffsetEnabled, int):
                Specifies whether to enable the offset channel for ACP measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpOffsetEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_frequency(self, selector_string):
        r"""Gets the center or edge frequency of the offset channel, relative to the center frequency of the closest carrier
        as determined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value
        is expressed in Hz. The sign of offset frequency is ignored and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_SIDEBAND` attribute determines whether the upper, lower, or both
        offsets are measured.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the center or edge frequency of the offset channel, relative to the center frequency of the closest carrier
                as determined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value
                is expressed in Hz. The sign of offset frequency is ignored and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_SIDEBAND` attribute determines whether the upper, lower, or both
                offsets are measured.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_frequency(self, selector_string, value):
        r"""Sets the center or edge frequency of the offset channel, relative to the center frequency of the closest carrier
        as determined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value
        is expressed in Hz. The sign of offset frequency is ignored and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_SIDEBAND` attribute determines whether the upper, lower, or both
        offsets are measured.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the center or edge frequency of the offset channel, relative to the center frequency of the closest carrier
                as determined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value
                is expressed in Hz. The sign of offset frequency is ignored and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_SIDEBAND` attribute determines whether the upper, lower, or both
                offsets are measured.

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
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_sideband(self, selector_string):
        r"""Gets whether the offset channel is present on one side, or on both sides of the carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Both**.

        +--------------+---------------------------------------------------------------------------+
        | Name (Value) | Description                                                               |
        +==============+===========================================================================+
        | Neg (0)      | Configures a lower offset segment to the left of the leftmost carrier.    |
        +--------------+---------------------------------------------------------------------------+
        | Pos (1)      | Configures an upper offset segment to the right of the rightmost carrier. |
        +--------------+---------------------------------------------------------------------------+
        | Both (2)     | Configures both negative and positive offset segments.                    |
        +--------------+---------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpOffsetSideband):
                Specifies whether the offset channel is present on one side, or on both sides of the carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_SIDEBAND.value
            )
            attr_val = enums.AcpOffsetSideband(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_sideband(self, selector_string, value):
        r"""Sets whether the offset channel is present on one side, or on both sides of the carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Both**.

        +--------------+---------------------------------------------------------------------------+
        | Name (Value) | Description                                                               |
        +==============+===========================================================================+
        | Neg (0)      | Configures a lower offset segment to the left of the leftmost carrier.    |
        +--------------+---------------------------------------------------------------------------+
        | Pos (1)      | Configures an upper offset segment to the right of the rightmost carrier. |
        +--------------+---------------------------------------------------------------------------+
        | Both (2)     | Configures both negative and positive offset segments.                    |
        +--------------+---------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpOffsetSideband, int):
                Specifies whether the offset channel is present on one side, or on both sides of the carrier.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpOffsetSideband else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_SIDEBAND.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_power_reference_carrier(self, selector_string):
        r"""Gets the carrier to be used as power reference to measure the offset channel relative power. The offset channel
        power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute of the
        reference carrier to **Active**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Closest**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Closest (0)   | The measurement uses the power measured in the carrier closest to the offset channel center frequency, as the power      |
        |               | reference.                                                                                                               |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Highest (1)   | The measurement uses the highest power measured among all the active carriers as the power reference.                    |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Composite (2) | The measurement uses the sum of powers measured in all the active carriers as the power reference.                       |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Specific (3)  | The measurement uses the power measured in the carrier that has an index specified by the ACP Offset Pwr Ref Specific    |
        |               | attribute, as the power reference.                                                                                       |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpOffsetPowerReferenceCarrier):
                Specifies the carrier to be used as power reference to measure the offset channel relative power. The offset channel
                power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute of the
                reference carrier to **Active**.

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
                attributes.AttributeID.ACP_OFFSET_POWER_REFERENCE_CARRIER.value,
            )
            attr_val = enums.AcpOffsetPowerReferenceCarrier(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_power_reference_carrier(self, selector_string, value):
        r"""Sets the carrier to be used as power reference to measure the offset channel relative power. The offset channel
        power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute of the
        reference carrier to **Active**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Closest**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Closest (0)   | The measurement uses the power measured in the carrier closest to the offset channel center frequency, as the power      |
        |               | reference.                                                                                                               |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Highest (1)   | The measurement uses the highest power measured among all the active carriers as the power reference.                    |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Composite (2) | The measurement uses the sum of powers measured in all the active carriers as the power reference.                       |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Specific (3)  | The measurement uses the power measured in the carrier that has an index specified by the ACP Offset Pwr Ref Specific    |
        |               | attribute, as the power reference.                                                                                       |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpOffsetPowerReferenceCarrier, int):
                Specifies the carrier to be used as power reference to measure the offset channel relative power. The offset channel
                power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute of the
                reference carrier to **Active**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpOffsetPowerReferenceCarrier else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_OFFSET_POWER_REFERENCE_CARRIER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_power_reference_specific(self, selector_string):
        r"""Gets the index of the carrier to be used as the reference carrier. The power measured in this carrier is used as
        the power reference for measuring the offset channel relative power, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to **Specific**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the index of the carrier to be used as the reference carrier. The power measured in this carrier is used as
                the power reference for measuring the offset channel relative power, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to **Specific**.

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
                attributes.AttributeID.ACP_OFFSET_POWER_REFERENCE_SPECIFIC.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_power_reference_specific(self, selector_string, value):
        r"""Sets the index of the carrier to be used as the reference carrier. The power measured in this carrier is used as
        the power reference for measuring the offset channel relative power, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to **Specific**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the index of the carrier to be used as the reference carrier. The power measured in this carrier is used as
                the power reference for measuring the offset channel relative power, when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_POWER_REFERENCE_CARRIER` attribute to **Specific**.

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
                attributes.AttributeID.ACP_OFFSET_POWER_REFERENCE_SPECIFIC.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_integration_bandwidth(self, selector_string):
        r"""Gets the frequency range, over which the measurement integrates the offset channel power. This value is expressed
        in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequency range, over which the measurement integrates the offset channel power. This value is expressed
                in Hz.

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
                attributes.AttributeID.ACP_OFFSET_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_integration_bandwidth(self, selector_string, value):
        r"""Sets the frequency range, over which the measurement integrates the offset channel power. This value is expressed
        in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequency range, over which the measurement integrates the offset channel power. This value is expressed
                in Hz.

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
                attributes.AttributeID.ACP_OFFSET_INTEGRATION_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_relative_attenuation(self, selector_string):
        r"""Gets the attenuation relative to the external attenuation specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
        ACP Offset Rel Attn attribute to compensate for variations in external attenuation when the offset channels are spread
        wide in frequency.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the attenuation relative to the external attenuation specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
                ACP Offset Rel Attn attribute to compensate for variations in external attenuation when the offset channels are spread
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
                attributes.AttributeID.ACP_OFFSET_RELATIVE_ATTENUATION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_relative_attenuation(self, selector_string, value):
        r"""Sets the attenuation relative to the external attenuation specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
        ACP Offset Rel Attn attribute to compensate for variations in external attenuation when the offset channels are spread
        wide in frequency.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the attenuation relative to the external attenuation specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
                ACP Offset Rel Attn attribute to compensate for variations in external attenuation when the offset channels are spread
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
                attributes.AttributeID.ACP_OFFSET_RELATIVE_ATTENUATION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_rrc_filter_enabled(self, selector_string):
        r"""Gets whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before measuring the
        offset channel power.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **False**.

        +--------------+------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                      |
        +==============+==================================================================================================================+
        | False (0)    | The channel power of the acquired offset channel is measured directly.                                           |
        +--------------+------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement applies the RRC filter on the acquired offset channel before measuring the offset channel power. |
        +--------------+------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpOffsetRrcFilterEnabled):
                Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before measuring the
                offset channel power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_RRC_FILTER_ENABLED.value
            )
            attr_val = enums.AcpOffsetRrcFilterEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_rrc_filter_enabled(self, selector_string, value):
        r"""Sets whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before measuring the
        offset channel power.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **False**.

        +--------------+------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                      |
        +==============+==================================================================================================================+
        | False (0)    | The channel power of the acquired offset channel is measured directly.                                           |
        +--------------+------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement applies the RRC filter on the acquired offset channel before measuring the offset channel power. |
        +--------------+------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpOffsetRrcFilterEnabled, int):
                Specifies whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before measuring the
                offset channel power.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpOffsetRrcFilterEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_OFFSET_RRC_FILTER_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_rrc_filter_alpha(self, selector_string):
        r"""Gets the roll-off factor for the root-raised-cosine (RRC) filter.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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
                updated_selector_string, attributes.AttributeID.ACP_OFFSET_RRC_FILTER_ALPHA.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_rrc_filter_alpha(self, selector_string, value):
        r"""Sets the roll-off factor for the root-raised-cosine (RRC) filter.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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
                updated_selector_string,
                attributes.AttributeID.ACP_OFFSET_RRC_FILTER_ALPHA.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_frequency_definition(self, selector_string):
        r"""Gets the offset frequency definition used to specify the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY` attribute.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Carrier Center to Offset Center**.

        +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                        | Description                                                                                                       |
        +=====================================+===================================================================================================================+
        | Carrier Center to Offset Center (0) | The offset frequency is defined from the center of the closest carrier to the center of the offset channel.       |
        +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
        | Carrier Center to Offset Edge (1)   | The offset frequency is defined from the center of the closest carrier to the nearest edge of the offset channel. |
        +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpOffsetFrequencyDefinition):
                Specifies the offset frequency definition used to specify the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY` attribute.

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
                attributes.AttributeID.ACP_OFFSET_FREQUENCY_DEFINITION.value,
            )
            attr_val = enums.AcpOffsetFrequencyDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_frequency_definition(self, selector_string, value):
        r"""Sets the offset frequency definition used to specify the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY` attribute.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Carrier Center to Offset Center**.

        +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                        | Description                                                                                                       |
        +=====================================+===================================================================================================================+
        | Carrier Center to Offset Center (0) | The offset frequency is defined from the center of the closest carrier to the center of the offset channel.       |
        +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
        | Carrier Center to Offset Edge (1)   | The offset frequency is defined from the center of the closest carrier to the nearest edge of the offset channel. |
        +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpOffsetFrequencyDefinition, int):
                Specifies the offset frequency definition used to specify the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY` attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpOffsetFrequencyDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_OFFSET_FREQUENCY_DEFINITION.value,
                value,
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

        +--------------+-------------------------------------------------------------------------+
        | Name (Value) | Description                                                             |
        +==============+=========================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the ACP RBW attribute. |
        +--------------+-------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                       |
        +--------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpRbwAutoBandwidth):
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
                updated_selector_string, attributes.AttributeID.ACP_RBW_FILTER_AUTO_BANDWIDTH.value
            )
            attr_val = enums.AcpRbwAutoBandwidth(attr_val)
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

        +--------------+-------------------------------------------------------------------------+
        | Name (Value) | Description                                                             |
        +==============+=========================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the ACP RBW attribute. |
        +--------------+-------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                       |
        +--------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpRbwAutoBandwidth, int):
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
            value = value.value if type(value) is enums.AcpRbwAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_RBW_FILTER_AUTO_BANDWIDTH.value,
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
                updated_selector_string, attributes.AttributeID.ACP_RBW_FILTER_BANDWIDTH.value
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
                attributes.AttributeID.ACP_RBW_FILTER_BANDWIDTH.value,
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

            attr_val (enums.AcpRbwFilterType):
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
                updated_selector_string, attributes.AttributeID.ACP_RBW_FILTER_TYPE.value
            )
            attr_val = enums.AcpRbwFilterType(attr_val)
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

            value (enums.AcpRbwFilterType, int):
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
            value = value.value if type(value) is enums.AcpRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_RBW_FILTER_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_bandwidth_definition(self, selector_string):
        r"""Gets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the ACP RBW Filter Type attribute to FFT   |
        |               | Based, RBW is the 3dB bandwidth of the window specified by the ACP FFT Window attribute.                                 |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the bin width of the spectrum computed using FFT when you set the ACP RBW Filter Type        |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpRbwFilterBandwidthDefinition):
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
                attributes.AttributeID.ACP_RBW_FILTER_BANDWIDTH_DEFINITION.value,
            )
            attr_val = enums.AcpRbwFilterBandwidthDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_bandwidth_definition(self, selector_string, value):
        r"""Sets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.RBW_FILTER_BANDWIDTH` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the ACP RBW Filter Type attribute to FFT   |
        |               | Based, RBW is the 3dB bandwidth of the window specified by the ACP FFT Window attribute.                                 |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the bin width of the spectrum computed using FFT when you set the ACP RBW Filter Type        |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpRbwFilterBandwidthDefinition, int):
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
            value = value.value if type(value) is enums.AcpRbwFilterBandwidthDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_RBW_FILTER_BANDWIDTH_DEFINITION.value,
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

        +--------------+----------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                            |
        +==============+========================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the ACP Sweep Time attribute.  |
        +--------------+----------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the ACP RBW attribute. |
        +--------------+----------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpSweepTimeAuto):
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
                updated_selector_string, attributes.AttributeID.ACP_SWEEP_TIME_AUTO.value
            )
            attr_val = enums.AcpSweepTimeAuto(attr_val)
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

        +--------------+----------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                            |
        +==============+========================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the ACP Sweep Time attribute.  |
        +--------------+----------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the ACP RBW attribute. |
        +--------------+----------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpSweepTimeAuto, int):
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
            value = value.value if type(value) is enums.AcpSweepTimeAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_SWEEP_TIME_AUTO.value, value
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
                updated_selector_string, attributes.AttributeID.ACP_SWEEP_TIME_INTERVAL.value
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
                updated_selector_string, attributes.AttributeID.ACP_SWEEP_TIME_INTERVAL.value, value
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

            attr_val (enums.AcpDetectorType):
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
                updated_selector_string, attributes.AttributeID.ACP_DETECTOR_TYPE.value
            )
            attr_val = enums.AcpDetectorType(attr_val)
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

            value (enums.AcpDetectorType, int):
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
            value = value.value if type(value) is enums.AcpDetectorType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_DETECTOR_TYPE.value, value
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
                updated_selector_string, attributes.AttributeID.ACP_DETECTOR_POINTS.value
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
                updated_selector_string, attributes.AttributeID.ACP_DETECTOR_POINTS.value, value
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

        +--------------+---------------------------------------------+
        | Name (Value) | Description                                 |
        +==============+=============================================+
        | dBm (0)      | The absolute powers are reported in dBm.    |
        +--------------+---------------------------------------------+
        | dBm/Hz (1)   | The absolute powers are reported in dBm/Hz. |
        +--------------+---------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpPowerUnits):
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
                updated_selector_string, attributes.AttributeID.ACP_POWER_UNITS.value
            )
            attr_val = enums.AcpPowerUnits(attr_val)
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

        +--------------+---------------------------------------------+
        | Name (Value) | Description                                 |
        +==============+=============================================+
        | dBm (0)      | The absolute powers are reported in dBm.    |
        +--------------+---------------------------------------------+
        | dBm/Hz (1)   | The absolute powers are reported in dBm/Hz. |
        +--------------+---------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpPowerUnits, int):
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
            value = value.value if type(value) is enums.AcpPowerUnits else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_POWER_UNITS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_method(self, selector_string):
        r"""Gets the method for performing the ACP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Normal**.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | Normal (0)         | The ACP measurement acquires the spectrum using the same signal analyzer setting across frequency bands. Use this        |
        |                    | method when measurement speed is desirable over higher dynamic range.                                                    |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Dynamic Range (1)  | The ACP measurement acquires the spectrum using the hardware-specific optimizations for different frequency bands. Use   |
        |                    | this method to get the best dynamic range.                                                                               |
        |                    | Supported devices: PXIe-5665/5668                                                                                        |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sequential FFT (2) | The ACP measurement acquires I/Q samples for a duration specified by the ACP Sweep Time attribute. These samples are     |
        |                    | divided into smaller chunks. The size of each chunk is defined by the ACP Sequential FFT Size attribute. The overlap     |
        |                    | between the chunks is defined by the ACP FFT Overlap Mode                                                                |
        |                    | attribute. FFT is computed on each of these chunks. The resultant FFTs are averaged to get the spectrum and is used to   |
        |                    | compute ACP.                                                                                                             |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpMeasurementMethod):
                Specifies the method for performing the ACP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_MEASUREMENT_METHOD.value
            )
            attr_val = enums.AcpMeasurementMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_method(self, selector_string, value):
        r"""Sets the method for performing the ACP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Normal**.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | Normal (0)         | The ACP measurement acquires the spectrum using the same signal analyzer setting across frequency bands. Use this        |
        |                    | method when measurement speed is desirable over higher dynamic range.                                                    |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Dynamic Range (1)  | The ACP measurement acquires the spectrum using the hardware-specific optimizations for different frequency bands. Use   |
        |                    | this method to get the best dynamic range.                                                                               |
        |                    | Supported devices: PXIe-5665/5668                                                                                        |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sequential FFT (2) | The ACP measurement acquires I/Q samples for a duration specified by the ACP Sweep Time attribute. These samples are     |
        |                    | divided into smaller chunks. The size of each chunk is defined by the ACP Sequential FFT Size attribute. The overlap     |
        |                    | between the chunks is defined by the ACP FFT Overlap Mode                                                                |
        |                    | attribute. FFT is computed on each of these chunks. The resultant FFTs are averaged to get the spectrum and is used to   |
        |                    | compute ACP.                                                                                                             |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpMeasurementMethod, int):
                Specifies the method for performing the ACP measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpMeasurementMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_MEASUREMENT_METHOD.value, value
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
        | Manual (0)   | When you set the ACP Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration for     |
        |              | the ACP measurement manually. When you set the ACP Meas Mode attribute to Measure, you can initiate the ACP measurement  |
        |              | manually.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Auto (1)     | When you set the ACP Noise Comp Enabled to True, RFmx sets the Input Isolation Enabled attribute to Enabled and          |
        |              | calibrates the instrument noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled     |
        |              | attribute and performs the ACP measurement, including compensation for noise of the instrument. RFmx skips noise         |
        |              | calibration in this mode if valid noise calibration data is already cached. When you set the ACP Noise Comp Enabled      |
        |              | attribute to False, RFmx does not calibrate instrument noise and only performs the ACP measurement without compensating  |
        |              | for noise of the instrument.                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpNoiseCalibrationMode):
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
                updated_selector_string, attributes.AttributeID.ACP_NOISE_CALIBRATION_MODE.value
            )
            attr_val = enums.AcpNoiseCalibrationMode(attr_val)
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
        | Manual (0)   | When you set the ACP Meas Mode attribute to Calibrate Noise Floor, you can initiate instrument noise calibration for     |
        |              | the ACP measurement manually. When you set the ACP Meas Mode attribute to Measure, you can initiate the ACP measurement  |
        |              | manually.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Auto (1)     | When you set the ACP Noise Comp Enabled to True, RFmx sets the Input Isolation Enabled attribute to Enabled and          |
        |              | calibrates the instrument noise in the current state of the instrument. RFmx then resets the Input Isolation Enabled     |
        |              | attribute and performs the ACP measurement, including compensation for noise of the instrument. RFmx skips noise         |
        |              | calibration in this mode if valid noise calibration data is already cached. When you set the ACP Noise Comp Enabled      |
        |              | attribute to False, RFmx does not calibrate instrument noise and only performs the ACP measurement without compensating  |
        |              | for noise of the instrument.                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpNoiseCalibrationMode, int):
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
            value = value.value if type(value) is enums.AcpNoiseCalibrationMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_NOISE_CALIBRATION_MODE.value,
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

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | RFmx uses the averages that you set for the ACP Noise Cal Averaging Count attribute.                                     |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | When you set the ACP Meas Method attribute to Normal or Sequential FFT, RFmx uses a noise calibration averaging count    |
        |              | of 32. When you set the ACP Meas Method attribute to Dynamic Range and the sweep time is less than 5 ms, RFmx uses a     |
        |              | noise calibration averaging count of 15. When you set the ACP Meas Method attribute to Dynamic Range and the sweep time  |
        |              | is greater than or equal to 5 ms, RFmx uses a noise calibration averaging count of 5.                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpNoiseCalibrationAveragingAuto):
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
                attributes.AttributeID.ACP_NOISE_CALIBRATION_AVERAGING_AUTO.value,
            )
            attr_val = enums.AcpNoiseCalibrationAveragingAuto(attr_val)
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

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | RFmx uses the averages that you set for the ACP Noise Cal Averaging Count attribute.                                     |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | When you set the ACP Meas Method attribute to Normal or Sequential FFT, RFmx uses a noise calibration averaging count    |
        |              | of 32. When you set the ACP Meas Method attribute to Dynamic Range and the sweep time is less than 5 ms, RFmx uses a     |
        |              | noise calibration averaging count of 15. When you set the ACP Meas Method attribute to Dynamic Range and the sweep time  |
        |              | is greater than or equal to 5 ms, RFmx uses a noise calibration averaging count of 5.                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpNoiseCalibrationAveragingAuto, int):
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
            value = value.value if type(value) is enums.AcpNoiseCalibrationAveragingAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_NOISE_CALIBRATION_AVERAGING_AUTO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_calibration_averaging_count(self, selector_string):
        r"""Gets the averaging count used for noise calibration when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO` attribute to **False**.

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
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO` attribute to **False**.

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
                attributes.AttributeID.ACP_NOISE_CALIBRATION_AVERAGING_COUNT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_calibration_averaging_count(self, selector_string, value):
        r"""Sets the averaging count used for noise calibration when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 32.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the averaging count used for noise calibration when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_AVERAGING_AUTO` attribute to **False**.

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
                attributes.AttributeID.ACP_NOISE_CALIBRATION_AVERAGING_COUNT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_compensation_enabled(self, selector_string):
        r"""Gets whether RFmx compensates for the instrument noise while performing the measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the ACP
        Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
        **Measure**. Refer to the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+------------------------------+
        | Name (Value) | Description                  |
        +==============+==============================+
        | False (0)    | Disables noise compensation. |
        +--------------+------------------------------+
        | True (1)     | Enables noise compensation.  |
        +--------------+------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpNoiseCompensationEnabled):
                Specifies whether RFmx compensates for the instrument noise while performing the measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the ACP
                Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
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
                updated_selector_string, attributes.AttributeID.ACP_NOISE_COMPENSATION_ENABLED.value
            )
            attr_val = enums.AcpNoiseCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_compensation_enabled(self, selector_string, value):
        r"""Sets whether RFmx compensates for the instrument noise while performing the measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the ACP
        Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
        **Measure**. Refer to the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+------------------------------+
        | Name (Value) | Description                  |
        +==============+==============================+
        | False (0)    | Disables noise compensation. |
        +--------------+------------------------------+
        | True (1)     | Enables noise compensation.  |
        +--------------+------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpNoiseCompensationEnabled, int):
                Specifies whether RFmx compensates for the instrument noise while performing the measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.NOISE_CALIBRATION_MODE` attribute to **Auto**, or when you set the ACP
                Noise Cal Mode attribute to **Manual** and :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_MODE` to
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
            value = value.value if type(value) is enums.AcpNoiseCompensationEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_NOISE_COMPENSATION_ENABLED.value,
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
        | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50-ohm termination. The measured power values are in excess of the       |
        |                              | thermal noise floor.                                                                                                     |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpNoiseCompensationType):
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
                updated_selector_string, attributes.AttributeID.ACP_NOISE_COMPENSATION_TYPE.value
            )
            attr_val = enums.AcpNoiseCompensationType(attr_val)
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
        | Analyzer and Termination (0) | Compensates for noise from the analyzer and the 50-ohm termination. The measured power values are in excess of the       |
        |                              | thermal noise floor.                                                                                                     |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Analyzer Only (1)            | Compensates for the analyzer noise only.                                                                                 |
        +------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpNoiseCompensationType, int):
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
            value = value.value if type(value) is enums.AcpNoiseCompensationType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_NOISE_COMPENSATION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the ACP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The ACP measurement uses the ACP Averaging Count attribute as the number of acquisitions over which the ACP measurement  |
        |              | is averaged.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpAveragingEnabled):
                Specifies whether to enable averaging for the ACP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_AVERAGING_ENABLED.value
            )
            attr_val = enums.AcpAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the ACP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The ACP measurement uses the ACP Averaging Count attribute as the number of acquisitions over which the ACP measurement  |
        |              | is averaged.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpAveragingEnabled, int):
                Specifies whether to enable averaging for the ACP measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.AcpAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.ACP_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.ACP_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for ACP
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

            attr_val (enums.AcpAveragingType):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for ACP
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
                updated_selector_string, attributes.AttributeID.ACP_AVERAGING_TYPE.value
            )
            attr_val = enums.AcpAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for ACP
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

            value (enums.AcpAveragingType, int):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for ACP
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
            value = value.value if type(value) is enums.AcpAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_AVERAGING_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_mode(self, selector_string):
        r"""Gets whether the measurement calibrates the noise floor of analyzer or performs the ACP measurement. Refer to the
        measurement guidelines section in the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------------------+---------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                           |
        +===========================+=======================================================================================+
        | Measure (0)               | ACP measurement is performed on the acquired signal.                                  |
        +---------------------------+---------------------------------------------------------------------------------------+
        | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the ACP measurement. |
        +---------------------------+---------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpMeasurementMode):
                Specifies whether the measurement calibrates the noise floor of analyzer or performs the ACP measurement. Refer to the
                measurement guidelines section in the `Noise Compensation Algorithm
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
                updated_selector_string, attributes.AttributeID.ACP_MEASUREMENT_MODE.value
            )
            attr_val = enums.AcpMeasurementMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_mode(self, selector_string, value):
        r"""Sets whether the measurement calibrates the noise floor of analyzer or performs the ACP measurement. Refer to the
        measurement guidelines section in the `Noise Compensation Algorithm
        <www.ni.com/docs/en-US/bundle/rfmx-specan/page/noise-compensation-algorithm.html>`_ topic for more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------------------+---------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                           |
        +===========================+=======================================================================================+
        | Measure (0)               | ACP measurement is performed on the acquired signal.                                  |
        +---------------------------+---------------------------------------------------------------------------------------+
        | Calibrate Noise Floor (1) | Manual noise calibration of the signal analyzer is performed for the ACP measurement. |
        +---------------------------+---------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpMeasurementMode, int):
                Specifies whether the measurement calibrates the noise floor of analyzer or performs the ACP measurement. Refer to the
                measurement guidelines section in the `Noise Compensation Algorithm
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
            value = value.value if type(value) is enums.AcpMeasurementMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_MEASUREMENT_MODE.value, value
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

            attr_val (enums.AcpFftWindow):
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
                updated_selector_string, attributes.AttributeID.ACP_FFT_WINDOW.value
            )
            attr_val = enums.AcpFftWindow(attr_val)
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

            value (enums.AcpFftWindow, int):
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
            value = value.value if type(value) is enums.AcpFftWindow else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_FFT_WINDOW.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fft_padding(self, selector_string):
        r"""Gets the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
        is given by the following formula:

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
                Specifies the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
                is given by the following formula:

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.ACP_FFT_PADDING.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fft_padding(self, selector_string, value):
        r"""Sets the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
        is given by the following formula:

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
                Specifies the factor by which the time-domain waveform is zero-padded before fast Fourier transform (FFT). The FFT size
                is given by the following formula:

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
                updated_selector_string, attributes.AttributeID.ACP_FFT_PADDING.value, value
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
        | Automatic (1)    | Measurement sets the overlap based on the value you have set for the ACP FFT Window attribute. When you set the ACP FFT  |
        |                  | Window attribute to any value other than None, the number of overlapped samples between consecutive chunks is set to     |
        |                  | 50% of the value of the ACP Sequential FFT Size attribute. When you set the ACP FFT Window attribute to None, the        |
        |                  | chunks are not overlapped and the overlap is set to 0%.                                                                  |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | User Defined (2) | Measurement uses the overlap that you specify in the ACP FFT Overlap attribute.                                          |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpFftOverlapMode):
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
                updated_selector_string, attributes.AttributeID.ACP_FFT_OVERLAP_MODE.value
            )
            attr_val = enums.AcpFftOverlapMode(attr_val)
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
        | Automatic (1)    | Measurement sets the overlap based on the value you have set for the ACP FFT Window attribute. When you set the ACP FFT  |
        |                  | Window attribute to any value other than None, the number of overlapped samples between consecutive chunks is set to     |
        |                  | 50% of the value of the ACP Sequential FFT Size attribute. When you set the ACP FFT Window attribute to None, the        |
        |                  | chunks are not overlapped and the overlap is set to 0%.                                                                  |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+
        | User Defined (2) | Measurement uses the overlap that you specify in the ACP FFT Overlap attribute.                                          |
        +------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpFftOverlapMode, int):
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
            value = value.value if type(value) is enums.AcpFftOverlapMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_FFT_OVERLAP_MODE.value, value
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
                updated_selector_string, attributes.AttributeID.ACP_FFT_OVERLAP.value
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
                updated_selector_string, attributes.AttributeID.ACP_FFT_OVERLAP.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_if_output_power_offset_auto(self, selector_string):
        r"""Gets whether the measurement computes an IF output power level offset for the offset channels to improve the
        dynamic range of the ACP measurement. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement sets the IF output power level offset using the values of the ACP Near IF Output Power Offset and ACP    |
        |              | Far IF Output Power Offset attributes.                                                                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement automatically computes an IF output power level offset for the offset channels to improve the dynamic    |
        |              | range of the ACP measurement.                                                                                            |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.AcpIFOutputPowerOffsetAuto):
                Specifies whether the measurement computes an IF output power level offset for the offset channels to improve the
                dynamic range of the ACP measurement. This attribute is used only if you set the
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
                updated_selector_string,
                attributes.AttributeID.ACP_IF_OUTPUT_POWER_OFFSET_AUTO.value,
            )
            attr_val = enums.AcpIFOutputPowerOffsetAuto(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_if_output_power_offset_auto(self, selector_string, value):
        r"""Sets whether the measurement computes an IF output power level offset for the offset channels to improve the
        dynamic range of the ACP measurement. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement sets the IF output power level offset using the values of the ACP Near IF Output Power Offset and ACP    |
        |              | Far IF Output Power Offset attributes.                                                                                   |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement automatically computes an IF output power level offset for the offset channels to improve the dynamic    |
        |              | range of the ACP measurement.                                                                                            |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.AcpIFOutputPowerOffsetAuto, int):
                Specifies whether the measurement computes an IF output power level offset for the offset channels to improve the
                dynamic range of the ACP measurement. This attribute is used only if you set the
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
            value = value.value if type(value) is enums.AcpIFOutputPowerOffsetAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_IF_OUTPUT_POWER_OFFSET_AUTO.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_near_if_output_power_offset(self, selector_string):
        r"""Gets the offset by which to adjust the IF output power level for offset channels that are near to the carrier
        channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
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
                Specifies the offset by which to adjust the IF output power level for offset channels that are near to the carrier
                channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
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
                updated_selector_string,
                attributes.AttributeID.ACP_NEAR_IF_OUTPUT_POWER_OFFSET.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_near_if_output_power_offset(self, selector_string, value):
        r"""Sets the offset by which to adjust the IF output power level for offset channels that are near to the carrier
        channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the offset by which to adjust the IF output power level for offset channels that are near to the carrier
                channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
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
                attributes.AttributeID.ACP_NEAR_IF_OUTPUT_POWER_OFFSET.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_far_if_output_power_offset(self, selector_string):
        r"""Gets the offset by which to adjust the IF output power level for offset channels that are far from the carrier
        channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

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
                Specifies the offset by which to adjust the IF output power level for offset channels that are far from the carrier
                channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
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
                updated_selector_string, attributes.AttributeID.ACP_FAR_IF_OUTPUT_POWER_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_far_if_output_power_offset(self, selector_string, value):
        r"""Sets the offset by which to adjust the IF output power level for offset channels that are far from the carrier
        channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IF_OUTPUT_POWER_OFFSET_AUTO` attribute to **False**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 20 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the offset by which to adjust the IF output power level for offset channels that are far from the carrier
                channel to improve the dynamic range. This value is expressed in dB. This attribute is used only if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Dynamic Range** and set the
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
                attributes.AttributeID.ACP_FAR_IF_OUTPUT_POWER_OFFSET.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_sequential_fft_size(self, selector_string):
        r"""Gets the FFT size when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**.

        The default value is 512.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the FFT size when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_SEQUENTIAL_FFT_SIZE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_sequential_fft_size(self, selector_string, value):
        r"""Sets the FFT size when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**.

        The default value is 512.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the FFT size when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Sequential FFT**.

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
                updated_selector_string, attributes.AttributeID.ACP_SEQUENTIAL_FFT_SIZE.value, value
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

            attr_val (enums.AcpAmplitudeCorrectionType):
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
                updated_selector_string, attributes.AttributeID.ACP_AMPLITUDE_CORRECTION_TYPE.value
            )
            attr_val = enums.AcpAmplitudeCorrectionType(attr_val)
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

            value (enums.AcpAmplitudeCorrectionType, int):
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
            value = value.value if type(value) is enums.AcpAmplitudeCorrectionType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.ACP_AMPLITUDE_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the ACP measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the ACP measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the ACP measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the ACP measurement.

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
                updated_selector_string, attributes.AttributeID.ACP_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for adjacent channel power  (ACP) measurement.

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
                Specifies the maximum number of threads used for parallelism for adjacent channel power  (ACP) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.ACP_NUMBER_OF_ANALYSIS_THREADS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for adjacent channel power  (ACP) measurement.

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
                Specifies the maximum number of threads used for parallelism for adjacent channel power  (ACP) measurement.

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
                attributes.AttributeID.ACP_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.AcpAveragingEnabled, int):
                This parameter specifies whether to enable averaging of the spectrum for the measurement. The default value is
                **False**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | The measurement is performed on a single acquisition.                                                                    |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement uses the Averaging Count parameter to calculate the number of acquisitions over which the spectrum is    |
                |              | averaged.                                                                                                                |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            averaging_count (int):
                This parameter specifies the number of acquisitions used for averaging when you set the **Averaging Enabled** parameter
                to **True**. The default value is 10.

            averaging_type (enums.AcpAveragingType, int):
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
                if type(averaging_enabled) is enums.AcpAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.AcpAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_and_offsets(
        self, selector_string, integration_bandwidth, number_of_offsets, channel_spacing
    ):
        r"""Configures a carrier channel with offset channels on both sides of the carrier as specified by the number of offsets.
        The offset channels are separated by +/- n * channel spacing from the center of the carrier. Power is measured over the
        integration bandwidth for each channel.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            integration_bandwidth (float):
                This parameter specifies the frequency range, in Hz, over which the measurement integrates the carrier channel power.
                The default value is 1 MHz.

            number_of_offsets (int):
                This parameter specifies the number of offset channels. The default value is 1.

            channel_spacing (float):
                This parameter specifies the spacing between offset channels. The default value is 1 MHz.

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
            error_code = self._interpreter.acp_configure_carrier_and_offsets(
                updated_selector_string, integration_bandwidth, number_of_offsets, channel_spacing
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_integration_bandwidth(self, selector_string, integration_bandwidth):
        r"""Configures the frequency range, in Hz, over which the measurement integrates the carrier power.
        Use "carrier<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method to build the selector string.

            integration_bandwidth (float):
                This parameter specifies the frequency range, in Hz, over which the measurement integrates the carrier channel power.
                The default value is 1 MHz.

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
            error_code = self._interpreter.acp_configure_carrier_integration_bandwidth(
                updated_selector_string, integration_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_mode(self, selector_string, carrier_mode):
        r"""Configures whether to consider the carrier power as part of total carrier power measurement.
        Use "carrier<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method to build the selector string.

            carrier_mode (enums.AcpCarrierMode, int):
                This parameter specifies whether to consider the carrier power as part of total carrier power measurement. The default
                value is **Active**.

                +--------------+---------------------------------------------------------------------+
                | Name (Value) | Description                                                         |
                +==============+=====================================================================+
                | Passive (0)  | The carrier power is not considered as part of total carrier power. |
                +--------------+---------------------------------------------------------------------+
                | Active (1)   | The carrier power is considered as part of total carrier power.     |
                +--------------+---------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            carrier_mode = (
                carrier_mode.value if type(carrier_mode) is enums.AcpCarrierMode else carrier_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_carrier_mode(
                updated_selector_string, carrier_mode
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_frequency(self, selector_string, carrier_frequency):
        r"""Configures the center frequency of the carrier, relative to the RF center frequency.

        Use "carrier<
        *
        n
        *
        >" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method to build the selector string.

            carrier_frequency (float):
                This parameter specifies the center frequency, in Hz, of the carrier, relative to the RF
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY`. The default value is 0.

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
            error_code = self._interpreter.acp_configure_carrier_frequency(
                updated_selector_string, carrier_frequency
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        r"""Configures the root-raised-cosine (RRC) filter to apply on the carrier channel before measuring the carrier channel
        power.
        Use "carrier<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method to build the selector string.

            rrc_filter_enabled (enums.AcpCarrierRrcFilterEnabled, int):
                This parameter specifies whether to apply the root-raised-cosine (RRC) filter on the acquired carrier channel before
                measuring the carrier channel power. The default value is **False**.

                +--------------+-------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                           |
                +==============+=======================================================================================================+
                | False (0)    | The channel power of the acquired carrier channel is measured directly.                               |
                +--------------+-------------------------------------------------------------------------------------------------------+
                | True (1)     | The RRC filter on the acquired carrier channel is applied before measuring the carrier channel power. |
                +--------------+-------------------------------------------------------------------------------------------------------+

            rrc_alpha (float):
                This parameter specifies the roll-off factor for the root-raised-cosine (RRC) filter. The default value is 0.1.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            rrc_filter_enabled = (
                rrc_filter_enabled.value
                if type(rrc_filter_enabled) is enums.AcpCarrierRrcFilterEnabled
                else rrc_filter_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_carrier_rrc_filter(
                updated_selector_string, rrc_filter_enabled, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fft(self, selector_string, fft_window, fft_padding):
        r"""Configures window and FFT to obtain a spectrum for the adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            fft_window (enums.AcpFftWindow, int):
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
            fft_window = fft_window.value if type(fft_window) is enums.AcpFftWindow else fft_window
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_fft(
                updated_selector_string, fft_window, fft_padding
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_method(self, selector_string, measurement_method):
        r"""Configures the method for performing the adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_method (enums.AcpMeasurementMethod, int):
                This parameter specifies the method for performing the ACP measurement. The default value is **Normal**.

                +--------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)       | Description                                                                                                              |
                +====================+==========================================================================================================================+
                | Normal (0)         | The ACP measurement acquires the spectrum with the same signal analyzer setting across frequency bands. Use this method  |
                |                    | when measurement speed is desirable over higher dynamic range.                                                           |
                +--------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Dynamic Range (1)  | The ACP measurement acquires the spectrum using the hardware-specific optimizations for different frequency bands. Use   |
                |                    | this method to get the best dynamic range.                                                                               |
                |                    | Supported devices: PXIe-5665/5668                                                                                        |
                +--------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Sequential FFT (2) | The ACP measurement acquires I/Q samples for a duration specified by the ACP Sweep Time attribute. These samples are     |
                |                    | divided into smaller chunks. The size of each chunk is defined by the ACP Sequential FFT Size attribute. The overlap     |
                |                    | between the chunks is defined by the ACP FFT Overlap Mode attribute. FFT is computed on each of these chunks. The        |
                |                    | resultant FFTs are averaged to get the spectrum and is used to compute ACP.                                              |
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
                if type(measurement_method) is enums.AcpMeasurementMethod
                else measurement_method
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_measurement_method(
                updated_selector_string, measurement_method
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_noise_compensation_enabled(self, selector_string, noise_compensation_enabled):
        r"""Configures compensation of the channel powers for the inherent noise floor of the signal analyzer.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            noise_compensation_enabled (enums.AcpNoiseCompensationEnabled, int):
                This parameter specifies whether to enable compensation of the channel powers for the inherent noise floor of the
                signal analyzer. The default value is **False**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Disables compensation of the channel powers for the noise floor of the signal analyzer.                                  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Enables compensation of the channel powers for the noise floor of the signal analyzer. The noise floor of the signal     |
                |              | analyzer is measured for the RF path used by the ACP measurement and cached for future use. If signal analyzer or        |
                |              | measurement parameters change, noise floors are measured again.                                                          |
                |              | Supported Devices: PXIe-5663/5665/5668, PXIe-5830/5831/5832/5842/5860                                                    |
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
                if type(noise_compensation_enabled) is enums.AcpNoiseCompensationEnabled
                else noise_compensation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_noise_compensation_enabled(
                updated_selector_string, noise_compensation_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_carriers(self, selector_string, number_of_carriers):
        r"""Configures the number of carriers for the adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_carriers (int):
                This parameter specifies the number of carriers. The default value is 1.

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
            error_code = self._interpreter.acp_configure_number_of_carriers(
                updated_selector_string, number_of_carriers
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_offsets(self, selector_string, number_of_offsets):
        r"""Configures the number of offsets for the adjacent channel power (ACP) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_offsets (int):
                This parameter specifies the number of offset channels. The default value is 1.

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
            error_code = self._interpreter.acp_configure_number_of_offsets(
                updated_selector_string, number_of_offsets
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_array(
        self, selector_string, offset_frequency, offset_sideband, offset_enabled
    ):
        r"""Configures an offset channel on one or both sides of carrier with center to center spacing as specified by the offset
        frequency and offset frequency definition. In case of multiple carriers, offset frequency is relative to the closest
        carrier.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            offset_frequency (float):
                This parameter specifies an array of center or edge frequencies, in Hz, of the offset channel, relative to the center
                frequency of the closest carrier as determined by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. The sign of offset frequency is
                ignored and the **Offset Sideband** parameter determines whether the upper, lower, or both offsets are measured. The
                default value is 1 MHz.

            offset_sideband (enums.AcpOffsetSideband, int):
                This parameter specifies whether the offset segment is present on one side, or on both sides of the carriers. The
                default value is **Both**.

                +--------------+---------------------------------------------------------------------------+
                | Name (Value) | Description                                                               |
                +==============+===========================================================================+
                | Neg (0)      | Configures a lower offset segment to the left of the leftmost carrier.    |
                +--------------+---------------------------------------------------------------------------+
                | Pos (1)      | Configures an upper offset segment to the right of the rightmost carrier. |
                +--------------+---------------------------------------------------------------------------+
                | Both (2)     | Configures both negative and positive offset segments.                    |
                +--------------+---------------------------------------------------------------------------+

            offset_enabled (enums.AcpOffsetEnabled, int):
                This parameter specifies whether to enable the offset channel for ACP measurement. The default value is **True**.

                +--------------+--------------------------------------------------+
                | Name (Value) | Description                                      |
                +==============+==================================================+
                | False (0)    | Disables the offset channel for ACP measurement. |
                +--------------+--------------------------------------------------+
                | True (1)     | Enables the offset channel for ACP measurement.  |
                +--------------+--------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_sideband = (
                [v.value for v in offset_sideband]
                if (
                    isinstance(offset_sideband, list)
                    and all(isinstance(v, enums.AcpOffsetSideband) for v in offset_sideband)
                )
                else offset_sideband
            )
            offset_enabled = (
                [v.value for v in offset_enabled]
                if (
                    isinstance(offset_enabled, list)
                    and all(isinstance(v, enums.AcpOffsetEnabled) for v in offset_enabled)
                )
                else offset_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset_array(
                updated_selector_string, offset_frequency, offset_sideband, offset_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_frequency_definition(self, selector_string, offset_frequency_definition):
        r"""Configures the offset frequency definition for the ACP measurement.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

            offset_frequency_definition (enums.AcpOffsetFrequencyDefinition, int):
                This parameter specifies the offset frequency definition. The default value is **Carrier Center to Offset Center**.

                +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
                | Name (Value)                        | Description                                                                                                       |
                +=====================================+===================================================================================================================+
                | Carrier Center to Offset Center (0) | The offset frequency is defined from the center of the closest carrier to the center of the offset channel.       |
                +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+
                | Carrier Center to Offset Edge (1)   | The offset frequency is defined from the center of the closest carrier to the nearest edge of the offset channel. |
                +-------------------------------------+-------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_frequency_definition = (
                offset_frequency_definition.value
                if type(offset_frequency_definition) is enums.AcpOffsetFrequencyDefinition
                else offset_frequency_definition
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset_frequency_definition(
                updated_selector_string, offset_frequency_definition
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_integration_bandwidth_array(self, selector_string, integration_bandwidth):
        r"""Configures the frequency range, in Hz, over which the measurement integrates the offset channel power.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            integration_bandwidth (float):
                This parameter specifies an array of frequency ranges, in Hz, over which the measurement integrates the offset channel
                power. The default value is 1 MHz.

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
            error_code = self._interpreter.acp_configure_offset_integration_bandwidth_array(
                updated_selector_string, integration_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_integration_bandwidth(self, selector_string, integration_bandwidth):
        r"""Configures the frequency range, in Hz, over which the measurement integrates the offset channel power.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

            integration_bandwidth (float):
                This parameter specifies the frequency range, in Hz, over which the measurement integrates the offset channel power.
                The default value is 1 MHz.

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
            error_code = self._interpreter.acp_configure_offset_integration_bandwidth(
                updated_selector_string, integration_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_power_reference_array(
        self, selector_string, offset_power_reference_carrier, offset_power_reference_specific
    ):
        r"""Configures the power reference to use for measuring the relative power of the offset channel.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            offset_power_reference_carrier (enums.AcpOffsetPowerReferenceCarrier, int):
                This parameter specifies the array of carriers to be used as power reference to measure offset channel relative power.
                The offset channel power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE`
                attribute of the reference carrier to **Active**. The default value is **Closest**.

                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)  | Description                                                                                                              |
                +===============+==========================================================================================================================+
                | Closest (0)   | The measurement uses the power measured in the carrier closest to the offset channel center frequency, as the power      |
                |               | reference.                                                                                                               |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Highest (1)   | The measurement uses the highest power measured among all the active carriers as the power reference.                    |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Composite (2) | The measurement uses the sum of powers measured in all the active carriers as the power reference.                       |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Specific (3)  | The measurement uses the power measured in the carrier that has an index specified by the ACP Offset Pwr Ref Specific    |
                |               | attribute, as the power reference.                                                                                       |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+

            offset_power_reference_specific (int):
                This parameter specifies the array of carrier indices to use as the reference carrier for each offset channel. The
                power measured in this carrier is used as the power reference for measuring the offset channel relative power, when you
                set the **Offset Power Reference Carrier** parameter to **Specific**. The default value is 0.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_power_reference_carrier = (
                [v.value for v in offset_power_reference_carrier]
                if (
                    isinstance(offset_power_reference_carrier, list)
                    and all(
                        isinstance(v, enums.AcpOffsetPowerReferenceCarrier)
                        for v in offset_power_reference_carrier
                    )
                )
                else offset_power_reference_carrier
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset_power_reference_array(
                updated_selector_string,
                offset_power_reference_carrier,
                offset_power_reference_specific,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_power_reference(
        self, selector_string, offset_reference_carrier, offset_reference_specific
    ):
        r"""Configures the power reference to use for measuring the relative power of the offset channel.

        Use "offset<
        *
        n
        *
        >" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

            offset_reference_carrier (enums.AcpOffsetPowerReferenceCarrier, int):
                This parameter specifies the carrier to be used as power reference to measure offset channel relative power. The offset
                channel power is measured only if you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_MODE` attribute of
                the reference carrier to **Active**. The default value is **Closest**.

                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)  | Description                                                                                                              |
                +===============+==========================================================================================================================+
                | Closest (0)   | The measurement uses the power measured in the carrier closest to the offset channel center frequency, as the power      |
                |               | reference.                                                                                                               |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Highest (1)   | The measurement uses the highest power measured among all the active carriers as the power reference.                    |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Composite (2) | The measurement uses the sum of powers measured in all the active carriers as the power reference.                       |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+
                | Specific (3)  | The measurement uses the power measured in the carrier that has an index specified by the ACP Offset Pwr Ref Specific    |
                |               | attribute, as the power reference.                                                                                       |
                +---------------+--------------------------------------------------------------------------------------------------------------------------+

            offset_reference_specific (int):
                This parameter specifies the index of the carrier to be used as the reference carrier. The power measured in this
                carrier is used as the power reference for measuring the offset channel relative power, when you set the **Offset Power
                Reference Carrier** parameter to **Specific**. The default value is 0.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_reference_carrier = (
                offset_reference_carrier.value
                if type(offset_reference_carrier) is enums.AcpOffsetPowerReferenceCarrier
                else offset_reference_carrier
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset_power_reference(
                updated_selector_string, offset_reference_carrier, offset_reference_specific
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_relative_attenuation_array(self, selector_string, relative_attenuation):
        r"""Configures the attenuation, in dB, relative to the external attenuation.

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
            error_code = self._interpreter.acp_configure_offset_relative_attenuation_array(
                updated_selector_string, relative_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_relative_attenuation(self, selector_string, relative_attenuation):
        r"""Configures the attenuation, in dB, relative to the external attenuation.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

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
            error_code = self._interpreter.acp_configure_offset_relative_attenuation(
                updated_selector_string, relative_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_rrc_filter_array(self, selector_string, rrc_filter_enabled, rrc_alpha):
        r"""Configures the root raised cosine (RRC) channel filter to be applied on the offset channel before measuring channel
        power.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rrc_filter_enabled (enums.AcpOffsetRrcFilterEnabled, int):
                This parameter specifies whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before
                measuring the offset channel power. The default value is **False**.

                +--------------+------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                      |
                +==============+==================================================================================================================+
                | False (0)    | The channel power of the acquired offset channel is measured directly.                                           |
                +--------------+------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement applies the RRC filter on the acquired offset channel before measuring the offset channel power. |
                +--------------+------------------------------------------------------------------------------------------------------------------+

            rrc_alpha (float):
                This parameter specifies an array of roll-off factors of the root-raised-cosine (RRC) filter to apply on the acquired
                offset channel before measuring the offset channel power. The default value is 0.1.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            rrc_filter_enabled = (
                [v.value for v in rrc_filter_enabled]
                if (
                    isinstance(rrc_filter_enabled, list)
                    and all(
                        isinstance(v, enums.AcpOffsetRrcFilterEnabled) for v in rrc_filter_enabled
                    )
                )
                else rrc_filter_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset_rrc_filter_array(
                updated_selector_string, rrc_filter_enabled, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        r"""Configures the root raised cosine (RRC) channel filter to be applied on the offset channel before measuring channel
        power.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

            rrc_filter_enabled (enums.AcpOffsetRrcFilterEnabled, int):
                This parameter specifies whether to apply the root-raised-cosine (RRC) filter on the acquired offset channel before
                measuring the offset channel power. The default value is **False**.

                +--------------+------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                      |
                +==============+==================================================================================================================+
                | False (0)    | The channel power of the acquired offset channel is measured directly.                                           |
                +--------------+------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement applies the RRC filter on the acquired offset channel before measuring the offset channel power. |
                +--------------+------------------------------------------------------------------------------------------------------------------+

            rrc_alpha (float):
                This parameter specifies the roll-off factor for the root-raised-cosine (RRC) filter. The default value is 0.1.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            rrc_filter_enabled = (
                rrc_filter_enabled.value
                if type(rrc_filter_enabled) is enums.AcpOffsetRrcFilterEnabled
                else rrc_filter_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset_rrc_filter(
                updated_selector_string, rrc_filter_enabled, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset(self, selector_string, offset_frequency, offset_sideband, offset_enabled):
        r"""Configures an offset channel on one or both sides of carrier with center to center spacing as specified by the offset
        frequency and offset frequency definition. In case of multiple carriers, offset frequency is relative to the closest
        carrier.

        Use "offset<
        *
        n
        *
        >" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

            offset_frequency (float):
                This parameter specifies the center or edge frequency, in Hz, of the offset channel, relative to the center frequency
                of the closest carrier as determined by the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION`
                attribute. The sign of offset frequency is ignored and the **Offset Sideband** parameter determines whether the upper,
                lower, or both offsets are measured. The default value is 1 MHz.

            offset_sideband (enums.AcpOffsetSideband, int):
                This parameter specifies whether the offset segment is present on one side, or on both sides of the carriers. The
                default value is **Both**.

                +--------------+---------------------------------------------------------------------------+
                | Name (Value) | Description                                                               |
                +==============+===========================================================================+
                | Neg (0)      | Configures a lower offset segment to the left of the leftmost carrier.    |
                +--------------+---------------------------------------------------------------------------+
                | Pos (1)      | Configures an upper offset segment to the right of the rightmost carrier. |
                +--------------+---------------------------------------------------------------------------+
                | Both (2)     | Configures both negative and positive offset segments.                    |
                +--------------+---------------------------------------------------------------------------+

            offset_enabled (enums.AcpOffsetEnabled, int):
                This parameter specifies whether to enable the offset channel for ACP measurement. The default value is **True**.

                +--------------+--------------------------------------------------+
                | Name (Value) | Description                                      |
                +==============+==================================================+
                | False (0)    | Disables the offset channel for ACP measurement. |
                +--------------+--------------------------------------------------+
                | True (1)     | Enables the offset channel for ACP measurement.  |
                +--------------+--------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_sideband = (
                offset_sideband.value
                if type(offset_sideband) is enums.AcpOffsetSideband
                else offset_sideband
            )
            offset_enabled = (
                offset_enabled.value
                if type(offset_enabled) is enums.AcpOffsetEnabled
                else offset_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_offset(
                updated_selector_string, offset_frequency, offset_sideband, offset_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_power_units(self, selector_string, power_units):
        r"""Configures the units for the absolute power.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            power_units (enums.AcpPowerUnits, int):
                This parameter specifies the units for the absolute power. The default value is **dBm**.

                +--------------+---------------------------------------------+
                | Name (Value) | Description                                 |
                +==============+=============================================+
                | dBm (0)      | The absolute powers are reported in dBm.    |
                +--------------+---------------------------------------------+
                | dBm/Hz (1)   | The absolute powers are reported in dBm/Hz. |
                +--------------+---------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            power_units = (
                power_units.value if type(power_units) is enums.AcpPowerUnits else power_units
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_power_units(
                updated_selector_string, power_units
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

            rbw_auto (enums.AcpRbwAutoBandwidth, int):
                This parameter specifies whether the measurement computes the RBW. Refer to the RBW and Sweep Time section in the `ACP
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/acp.html>`_ topic for more details on RBW and sweep time. The default
                value is **True**.

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

            rbw_filter_type (enums.AcpRbwFilterType, int):
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
            rbw_auto = rbw_auto.value if type(rbw_auto) is enums.AcpRbwAutoBandwidth else rbw_auto
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.AcpRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_rbw_filter(
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

            sweep_time_auto (enums.AcpSweepTimeAuto, int):
                This parameter specifies whether the measurement computes the sweep time. The default value is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | The measurement uses the sweep time that you specify in the Sweep Time Interval parameter.                               |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement calculates the sweep time based on the value of the ACP RBW attribute. Refer to the ACP topic for more   |
                |              | information about RBW.                                                                                                   |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

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
                if type(sweep_time_auto) is enums.AcpSweepTimeAuto
                else sweep_time_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_sweep_time(
                updated_selector_string, sweep_time_auto, sweep_time_interval
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

            detector_type (enums.AcpDetectorType, int):
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
                if type(detector_type) is enums.AcpDetectorType
                else detector_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.acp_configure_detector(
                updated_selector_string, detector_type, detector_points
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

            noise_calibration_data_valid (enums.AcpNoiseCalibrationDataValid):
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
                self._interpreter.acp_validate_noise_calibration_data(updated_selector_string)
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return noise_calibration_data_valid, error_code
