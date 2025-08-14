"""Provides methods to configure the Sem measurement."""

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


class SemConfiguration(object):
    """Provides methods to configure the Sem measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Sem measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the SEM measurement.

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
                Specifies whether to enable the SEM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the SEM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the SEM measurement.

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
                updated_selector_string, attributes.AttributeID.SEM_MEASUREMENT_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.SEM_NUMBER_OF_CARRIERS.value
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
                updated_selector_string, attributes.AttributeID.SEM_NUMBER_OF_CARRIERS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_enabled(self, selector_string):
        r"""Gets whether to consider the carrier power as part of the total carrier power measurement.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+-------------------------------------------------------------------------+
        | Name (Value) | Description                                                             |
        +==============+=========================================================================+
        | False (0)    | The carrier power is not considered as part of the total carrier power. |
        +--------------+-------------------------------------------------------------------------+
        | True (1)     | The carrier power is considered as part of the total carrier power.     |
        +--------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemCarrierEnabled):
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
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_ENABLED.value
            )
            attr_val = enums.SemCarrierEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_enabled(self, selector_string, value):
        r"""Sets whether to consider the carrier power as part of the total carrier power measurement.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+-------------------------------------------------------------------------+
        | Name (Value) | Description                                                             |
        +==============+=========================================================================+
        | False (0)    | The carrier power is not considered as part of the total carrier power. |
        +--------------+-------------------------------------------------------------------------+
        | True (1)     | The carrier power is considered as part of the total carrier power.     |
        +--------------+-------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemCarrierEnabled, int):
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
            value = value.value if type(value) is enums.SemCarrierEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_FREQUENCY.value
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
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_integration_bandwidth(self, selector_string):
        r"""Gets the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 2 MHz.

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
                attributes.AttributeID.SEM_CARRIER_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_integration_bandwidth(self, selector_string, value):
        r"""Sets the frequency range over which the measurement integrates the carrier power. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 2 MHz.

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
                attributes.AttributeID.SEM_CARRIER_INTEGRATION_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_channel_bandwidth(self, selector_string):
        r"""Gets the channel bandwidth of the carrier. This parameter is used to calculate the values of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_START_FREQUENCY` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_STOP_FREQUENCY` attributes when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute to **Carrier Edge to Meas BW
        Center** or **Carrier Edge to Meas BW Edge**.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 2 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the channel bandwidth of the carrier. This parameter is used to calculate the values of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_START_FREQUENCY` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_STOP_FREQUENCY` attributes when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute to **Carrier Edge to Meas BW
                Center** or **Carrier Edge to Meas BW Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_CHANNEL_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_channel_bandwidth(self, selector_string, value):
        r"""Sets the channel bandwidth of the carrier. This parameter is used to calculate the values of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_START_FREQUENCY` and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_STOP_FREQUENCY` attributes when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute to **Carrier Edge to Meas BW
        Center** or **Carrier Edge to Meas BW Edge**.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 2 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the channel bandwidth of the carrier. This parameter is used to calculate the values of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_START_FREQUENCY` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_STOP_FREQUENCY` attributes when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute to **Carrier Edge to Meas BW
                Center** or **Carrier Edge to Meas BW Edge**.

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
                attributes.AttributeID.SEM_CARRIER_CHANNEL_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the measurement computes the resolution bandwidth (RBW) of the carrier.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+---------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                     |
        +==============+=================================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the SEM Carrier RBW attribute. |
        +--------------+---------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                               |
        +--------------+---------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemCarrierRbwAutoBandwidth):
                Specifies whether the measurement computes the resolution bandwidth (RBW) of the carrier.

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
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_AUTO_BANDWIDTH.value,
            )
            attr_val = enums.SemCarrierRbwAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the measurement computes the resolution bandwidth (RBW) of the carrier.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+---------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                     |
        +==============+=================================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the SEM Carrier RBW attribute. |
        +--------------+---------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                               |
        +--------------+---------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemCarrierRbwAutoBandwidth, int):
                Specifies whether the measurement computes the resolution bandwidth (RBW) of the carrier.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemCarrierRbwAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired carrier signal, when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
        value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired carrier signal, when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
                value is expressed in Hz.

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
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired carrier signal, when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
        value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired carrier signal, when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
                value is expressed in Hz.

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
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rbw_filter_type(self, selector_string):
        r"""Gets the shape of the digital resolution bandwidth (RBW) filter.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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

            attr_val (enums.SemCarrierRbwFilterType):
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
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_RBW_FILTER_TYPE.value
            )
            attr_val = enums.SemCarrierRbwFilterType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rbw_filter_type(self, selector_string, value):
        r"""Sets the shape of the digital resolution bandwidth (RBW) filter.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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

            value (enums.SemCarrierRbwFilterType, int):
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
            value = value.value if type(value) is enums.SemCarrierRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rbw_filter_bandwidth_definition(self, selector_string):
        r"""Gets the bandwidth definition that you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attribute.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the SEM Carrier RBW Filter Type           |
        |               | attribute to FFT Based, RBW is the 3 dB bandwidth of the window specified by the SEM FFT Window attribute.               |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the SEM Carrier RBW Filter Type    |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemCarrierRbwFilterBandwidthDefinition):
                Specifies the bandwidth definition that you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attribute.

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
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_BANDWIDTH_DEFINITION.value,
            )
            attr_val = enums.SemCarrierRbwFilterBandwidthDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rbw_filter_bandwidth_definition(self, selector_string, value):
        r"""Sets the bandwidth definition that you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attribute.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3 dB bandwidth of the RBW filter. When you set the SEM Carrier RBW Filter Type           |
        |               | attribute to FFT Based, RBW is the 3 dB bandwidth of the window specified by the SEM FFT Window attribute.               |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using an FFT when you set the SEM Carrier RBW Filter Type    |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemCarrierRbwFilterBandwidthDefinition, int):
                Specifies the bandwidth definition that you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CARRIER_RBW_FILTER_BANDWIDTH` attribute.

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
                if type(value) is enums.SemCarrierRbwFilterBandwidthDefinition
                else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_CARRIER_RBW_FILTER_BANDWIDTH_DEFINITION.value,
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

            attr_val (enums.SemCarrierRrcFilterEnabled):
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
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_RRC_FILTER_ENABLED.value
            )
            attr_val = enums.SemCarrierRrcFilterEnabled(attr_val)
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

            value (enums.SemCarrierRrcFilterEnabled, int):
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
            value = value.value if type(value) is enums.SemCarrierRrcFilterEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_CARRIER_RRC_FILTER_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_rrc_filter_alpha(self, selector_string):
        r"""Gets the roll-off factor for the root-raised-cosine (RRC) filter to apply on the acquired carrier channel before
        measuring the carrier channel power.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the roll-off factor for the root-raised-cosine (RRC) filter to apply on the acquired carrier channel before
                measuring the carrier channel power.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_CARRIER_RRC_FILTER_ALPHA.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_rrc_filter_alpha(self, selector_string, value):
        r"""Sets the roll-off factor for the root-raised-cosine (RRC) filter to apply on the acquired carrier channel before
        measuring the carrier channel power.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the roll-off factor for the root-raised-cosine (RRC) filter to apply on the acquired carrier channel before
                measuring the carrier channel power.

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
                attributes.AttributeID.SEM_CARRIER_RRC_FILTER_ALPHA.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_offsets(self, selector_string):
        r"""Gets the number of offset segments.

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
                Specifies the number of offset segments.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_NUMBER_OF_OFFSETS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_offsets(self, selector_string, value):
        r"""Sets the number of offset segments.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of offset segments.

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
                updated_selector_string, attributes.AttributeID.SEM_NUMBER_OF_OFFSETS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_enabled(self, selector_string):
        r"""Gets whether to enable the offset segment for SEM measurement.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+------------------------------------------------------+
        | Name (Value) | Description                                          |
        +==============+======================================================+
        | False (0)    | Disables the offset segment for the SEM measurement. |
        +--------------+------------------------------------------------------+
        | True (1)     | Enables the offset segment for the SEM measurement.  |
        +--------------+------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetEnabled):
                Specifies whether to enable the offset segment for SEM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_ENABLED.value
            )
            attr_val = enums.SemOffsetEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_enabled(self, selector_string, value):
        r"""Sets whether to enable the offset segment for SEM measurement.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+------------------------------------------------------+
        | Name (Value) | Description                                          |
        +==============+======================================================+
        | False (0)    | Disables the offset segment for the SEM measurement. |
        +--------------+------------------------------------------------------+
        | True (1)     | Enables the offset segment for the SEM measurement.  |
        +--------------+------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetEnabled, int):
                Specifies whether to enable the offset segment for SEM measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemOffsetEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_start_frequency(self, selector_string):
        r"""Gets the start frequency of the offset segment relative to the closest configured carrier channel bandwidth center
        or carrier channel bandwidth edge based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the start frequency of the offset segment relative to the closest configured carrier channel bandwidth center
                or carrier channel bandwidth edge based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_START_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_start_frequency(self, selector_string, value):
        r"""Sets the start frequency of the offset segment relative to the closest configured carrier channel bandwidth center
        or carrier channel bandwidth edge based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the start frequency of the offset segment relative to the closest configured carrier channel bandwidth center
                or carrier channel bandwidth edge based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_OFFSET_START_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_stop_frequency(self, selector_string):
        r"""Gets the stop frequency of the offset segment relative to the closest configured carrier  channel bandwidth center
        or carrier channel bandwidth edge based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 2 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the stop frequency of the offset segment relative to the closest configured carrier  channel bandwidth center
                or carrier channel bandwidth edge based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_STOP_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_stop_frequency(self, selector_string, value):
        r"""Sets the stop frequency of the offset segment relative to the closest configured carrier  channel bandwidth center
        or carrier channel bandwidth edge based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 2 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the stop frequency of the offset segment relative to the closest configured carrier  channel bandwidth center
                or carrier channel bandwidth edge based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_OFFSET_STOP_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_sideband(self, selector_string):
        r"""Gets whether the offset segment is present on one side, or on both sides of the carrier.

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

            attr_val (enums.SemOffsetSideband):
                Specifies whether the offset segment is present on one side, or on both sides of the carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_SIDEBAND.value
            )
            attr_val = enums.SemOffsetSideband(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_sideband(self, selector_string, value):
        r"""Sets whether the offset segment is present on one side, or on both sides of the carrier.

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

            value (enums.SemOffsetSideband, int):
                Specifies whether the offset segment is present on one side, or on both sides of the carrier.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemOffsetSideband else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_SIDEBAND.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_rbw_filter_auto_bandwidth(self, selector_string):
        r"""Gets whether the measurement computes the resolution bandwidth (RBW).

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                    |
        +==============+================================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the SEM Offset RBW attribute. |
        +--------------+--------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                              |
        +--------------+--------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetRbwAutoBandwidth):
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
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_AUTO_BANDWIDTH.value,
            )
            attr_val = enums.SemOffsetRbwAutoBandwidth(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_rbw_filter_auto_bandwidth(self, selector_string, value):
        r"""Sets whether the measurement computes the resolution bandwidth (RBW).

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        +--------------+--------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                    |
        +==============+================================================================================+
        | False (0)    | The measurement uses the RBW that you specify in the SEM Offset RBW attribute. |
        +--------------+--------------------------------------------------------------------------------+
        | True (1)     | The measurement computes the RBW.                                              |
        +--------------+--------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetRbwAutoBandwidth, int):
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
            value = value.value if type(value) is enums.SemOffsetRbwAutoBandwidth else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_AUTO_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired offset segment, when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
        value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired offset segment, when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
                value is expressed in Hz.

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
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired offset segment, when you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
        value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 10 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to sweep the acquired offset segment, when you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_AUTO_BANDWIDTH` attribute to **False**. This
                value is expressed in Hz.

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
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_rbw_filter_type(self, selector_string):
        r"""Gets the shape of the digital resolution bandwidth (RBW) filter.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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

            attr_val (enums.SemOffsetRbwFilterType):
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
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_RBW_FILTER_TYPE.value
            )
            attr_val = enums.SemOffsetRbwFilterType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_rbw_filter_type(self, selector_string, value):
        r"""Sets the shape of the digital resolution bandwidth (RBW) filter.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

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

            value (enums.SemOffsetRbwFilterType, int):
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
            value = value.value if type(value) is enums.SemOffsetRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_rbw_filter_bandwidth_definition(self, selector_string):
        r"""Gets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` attribute.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the SEM Offset RBW Filter Type attribute   |
        |               | to FFT Based, RBW is the 3dB bandwidth of the window specified by the SEM FFT Window attribute.                          |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the SEM Offset RBW Filter Type        |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetRbwFilterBandwidthDefinition):
                Specifies the bandwidth definition which you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` attribute.

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
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_BANDWIDTH_DEFINITION.value,
            )
            attr_val = enums.SemOffsetRbwFilterBandwidthDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_rbw_filter_bandwidth_definition(self, selector_string, value):
        r"""Sets the bandwidth definition which you use to specify the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` attribute.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **3dB**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | 3dB (0)       | Defines the RBW in terms of the 3dB bandwidth of the RBW filter. When you set the SEM Offset RBW Filter Type attribute   |
        |               | to FFT Based, RBW is the 3dB bandwidth of the window specified by the SEM FFT Window attribute.                          |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Bin Width (2) | Defines the RBW in terms of the spectrum bin width computed using FFT when you set the SEM Offset RBW Filter Type        |
        |               | attribute to FFT Based.                                                                                                  |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetRbwFilterBandwidthDefinition, int):
                Specifies the bandwidth definition which you use to specify the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RBW_FILTER_BANDWIDTH` attribute.

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
                value.value if type(value) is enums.SemOffsetRbwFilterBandwidthDefinition else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_RBW_FILTER_BANDWIDTH_DEFINITION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_bandwidth_integral(self, selector_string):
        r"""Gets the resolution of the spectrum to compare with spectral mask limits as an integer multiple of the resolution
        bandwidth (RBW).

        If you set this attribute to a value greater than 1, the measurement acquires the spectrum with a narrow
        resolution and then processes it digitally to get a wider resolution that is equal to the product of the bandwidth
        integral and the RBW.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the resolution of the spectrum to compare with spectral mask limits as an integer multiple of the resolution
                bandwidth (RBW).

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_BANDWIDTH_INTEGRAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_bandwidth_integral(self, selector_string, value):
        r"""Sets the resolution of the spectrum to compare with spectral mask limits as an integer multiple of the resolution
        bandwidth (RBW).

        If you set this attribute to a value greater than 1, the measurement acquires the spectrum with a narrow
        resolution and then processes it digitally to get a wider resolution that is equal to the product of the bandwidth
        integral and the RBW.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the resolution of the spectrum to compare with spectral mask limits as an integer multiple of the resolution
                bandwidth (RBW).

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
                attributes.AttributeID.SEM_OFFSET_BANDWIDTH_INTEGRAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_relative_attenuation(self, selector_string):
        r"""Gets the attenuation relative to the external attenuation specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
        SEM Offset Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
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
                SEM Offset Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
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
                attributes.AttributeID.SEM_OFFSET_RELATIVE_ATTENUATION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_relative_attenuation(self, selector_string, value):
        r"""Sets the attenuation relative to the external attenuation specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_ATTENUATION` attribute. This value is expressed in dB. Use the
        SEM Offset Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
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
                SEM Offset Rel Attn attribute to compensate for the variations in external attenuation when offset segments are spread
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
                attributes.AttributeID.SEM_OFFSET_RELATIVE_ATTENUATION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_limit_fail_mask(self, selector_string):
        r"""Gets the criteria to determine the measurement fail status.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Absolute**.

        +-----------------+-------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                     |
        +=================+=================================================================================================+
        | Abs AND Rel (0) | The measurement fails if the power in the segment exceeds both the absolute and relative masks. |
        +-----------------+-------------------------------------------------------------------------------------------------+
        | Abs OR Rel (1)  | The measurement fails if the power in the segment exceeds either the absolute or relative mask. |
        +-----------------+-------------------------------------------------------------------------------------------------+
        | Absolute (2)    | The measurement fails if the power in the segment exceeds the absolute mask.                    |
        +-----------------+-------------------------------------------------------------------------------------------------+
        | Relative (3)    | The measurement fails if the power in the segment exceeds the relative mask.                    |
        +-----------------+-------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetLimitFailMask):
                Specifies the criteria to determine the measurement fail status.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_LIMIT_FAIL_MASK.value
            )
            attr_val = enums.SemOffsetLimitFailMask(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_limit_fail_mask(self, selector_string, value):
        r"""Sets the criteria to determine the measurement fail status.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Absolute**.

        +-----------------+-------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                     |
        +=================+=================================================================================================+
        | Abs AND Rel (0) | The measurement fails if the power in the segment exceeds both the absolute and relative masks. |
        +-----------------+-------------------------------------------------------------------------------------------------+
        | Abs OR Rel (1)  | The measurement fails if the power in the segment exceeds either the absolute or relative mask. |
        +-----------------+-------------------------------------------------------------------------------------------------+
        | Absolute (2)    | The measurement fails if the power in the segment exceeds the absolute mask.                    |
        +-----------------+-------------------------------------------------------------------------------------------------+
        | Relative (3)    | The measurement fails if the power in the segment exceeds the relative mask.                    |
        +-----------------+-------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetLimitFailMask, int):
                Specifies the criteria to determine the measurement fail status.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemOffsetLimitFailMask else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_LIMIT_FAIL_MASK.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_absolute_limit_mode(self, selector_string):
        r"""Gets whether the absolute limit mask is a flat line or a line with a slope.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Couple**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | The line specified by the SEM Offset Abs Limit Start and SEM Offset Abs Limit Stop attribute values as the two ends is   |
        |              | considered as the mask.                                                                                                  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Abs Limit Start attribute.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetAbsoluteLimitMode):
                Specifies whether the absolute limit mask is a flat line or a line with a slope.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_ABSOLUTE_LIMIT_MODE.value
            )
            attr_val = enums.SemOffsetAbsoluteLimitMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_absolute_limit_mode(self, selector_string, value):
        r"""Sets whether the absolute limit mask is a flat line or a line with a slope.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Couple**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | The line specified by the SEM Offset Abs Limit Start and SEM Offset Abs Limit Stop attribute values as the two ends is   |
        |              | considered as the mask.                                                                                                  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Abs Limit Start attribute.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetAbsoluteLimitMode, int):
                Specifies whether the absolute limit mask is a flat line or a line with a slope.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemOffsetAbsoluteLimitMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_ABSOLUTE_LIMIT_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_absolute_limit_start(self, selector_string):
        r"""Gets the absolute power limit corresponding to the beginning of the offset segment. This value is expressed in
        dBm. This power limit is also set as the stop limit for the offset segment when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the absolute power limit corresponding to the beginning of the offset segment. This value is expressed in
                dBm. This power limit is also set as the stop limit for the offset segment when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SEM_OFFSET_ABSOLUTE_LIMIT_START.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_absolute_limit_start(self, selector_string, value):
        r"""Sets the absolute power limit corresponding to the beginning of the offset segment. This value is expressed in
        dBm. This power limit is also set as the stop limit for the offset segment when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the absolute power limit corresponding to the beginning of the offset segment. This value is expressed in
                dBm. This power limit is also set as the stop limit for the offset segment when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SEM_OFFSET_ABSOLUTE_LIMIT_START.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_absolute_limit_stop(self, selector_string):
        r"""Gets the absolute power limit corresponding to the end of the offset segment. This value is expressed in dBm. The
        measurement ignores this attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the absolute power limit corresponding to the end of the offset segment. This value is expressed in dBm. The
                measurement ignores this attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_ABSOLUTE_LIMIT_STOP.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_absolute_limit_stop(self, selector_string, value):
        r"""Sets the absolute power limit corresponding to the end of the offset segment. This value is expressed in dBm. The
        measurement ignores this attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the absolute power limit corresponding to the end of the offset segment. This value is expressed in dBm. The
                measurement ignores this attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_ABSOLUTE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SEM_OFFSET_ABSOLUTE_LIMIT_STOP.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_relative_limit_mode(self, selector_string):
        r"""Gets whether the relative limit mask is a flat line or a line with a slope.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Manual**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | The line specified by the SEM Offset Rel Limit Start and SEM Offset Rel Limit Stop attribute values as the two ends is   |
        |              | considered as the mask.                                                                                                  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Rel Limit Start attribute.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetRelativeLimitMode):
                Specifies whether the relative limit mask is a flat line or a line with a slope.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_RELATIVE_LIMIT_MODE.value
            )
            attr_val = enums.SemOffsetRelativeLimitMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_relative_limit_mode(self, selector_string, value):
        r"""Sets whether the relative limit mask is a flat line or a line with a slope.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Manual**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Manual (0)   | The line specified by the SEM Offset Rel Limit Start and SEM Offset Rel Limit Stop attribute values as the two ends is   |
        |              | considered as the mask.                                                                                                  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Rel Limit Start attribute.                           |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetRelativeLimitMode, int):
                Specifies whether the relative limit mask is a flat line or a line with a slope.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemOffsetRelativeLimitMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_RELATIVE_LIMIT_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_relative_limit_start(self, selector_string):
        r"""Gets the relative power limit corresponding to the beginning of the offset segment. This value is expressed in dB.
        This power limit is also set as the stop limit for the offset segment when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the relative power limit corresponding to the beginning of the offset segment. This value is expressed in dB.
                This power limit is also set as the stop limit for the offset segment when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SEM_OFFSET_RELATIVE_LIMIT_START.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_relative_limit_start(self, selector_string, value):
        r"""Sets the relative power limit corresponding to the beginning of the offset segment. This value is expressed in dB.
        This power limit is also set as the stop limit for the offset segment when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -20.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the relative power limit corresponding to the beginning of the offset segment. This value is expressed in dB.
                This power limit is also set as the stop limit for the offset segment when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SEM_OFFSET_RELATIVE_LIMIT_START.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_relative_limit_stop(self, selector_string):
        r"""Gets the relative power limit corresponding to the end of the offset segment. This value is expressed in dB. The
        measurement ignores this attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -30.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the relative power limit corresponding to the end of the offset segment. This value is expressed in dB. The
                measurement ignores this attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_OFFSET_RELATIVE_LIMIT_STOP.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_relative_limit_stop(self, selector_string, value):
        r"""Sets the relative power limit corresponding to the end of the offset segment. This value is expressed in dB. The
        measurement ignores this attribute when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is -30.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the relative power limit corresponding to the end of the offset segment. This value is expressed in dB. The
                measurement ignores this attribute when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_RELATIVE_LIMIT_MODE` attribute to **Couple**.

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
                attributes.AttributeID.SEM_OFFSET_RELATIVE_LIMIT_STOP.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_offset_frequency_definition(self, selector_string):
        r"""Gets the definition of  the start frequency and stop frequency of the offset segments from the nearest carrier
        channels.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Carrier Center to Meas BW Center**.

        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                         | Description                                                                                                              |
        +======================================+==========================================================================================================================+
        | Carrier Center to Meas BW Center (0) | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
        |                                      | center of the offset segment measurement bandwidth.                                                                      |
        |                                      | Measurement Bandwidth = Resolution Bandwidth * Bandwidth Integral.                                                       |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Carrier Center to Meas BW Edge (1)   | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
        |                                      | nearest edge of the offset segment measurement bandwidth.                                                                |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Carrier Edge to Meas BW Center (2)   | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
        |                                      | the center of the nearest offset segment measurement bandwidth.                                                          |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Carrier Edge to Meas BW Edge (3)     | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
        |                                      | the edge of the nearest offset segment measurement bandwidth.                                                            |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemOffsetFrequencyDefinition):
                Specifies the definition of  the start frequency and stop frequency of the offset segments from the nearest carrier
                channels.

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
                attributes.AttributeID.SEM_OFFSET_FREQUENCY_DEFINITION.value,
            )
            attr_val = enums.SemOffsetFrequencyDefinition(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_offset_frequency_definition(self, selector_string, value):
        r"""Sets the definition of  the start frequency and stop frequency of the offset segments from the nearest carrier
        channels.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **Carrier Center to Meas BW Center**.

        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                         | Description                                                                                                              |
        +======================================+==========================================================================================================================+
        | Carrier Center to Meas BW Center (0) | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
        |                                      | center of the offset segment measurement bandwidth.                                                                      |
        |                                      | Measurement Bandwidth = Resolution Bandwidth * Bandwidth Integral.                                                       |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Carrier Center to Meas BW Edge (1)   | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
        |                                      | nearest edge of the offset segment measurement bandwidth.                                                                |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Carrier Edge to Meas BW Center (2)   | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
        |                                      | the center of the nearest offset segment measurement bandwidth.                                                          |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Carrier Edge to Meas BW Edge (3)     | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
        |                                      | the edge of the nearest offset segment measurement bandwidth.                                                            |
        +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemOffsetFrequencyDefinition, int):
                Specifies the definition of  the start frequency and stop frequency of the offset segments from the nearest carrier
                channels.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemOffsetFrequencyDefinition else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_OFFSET_FREQUENCY_DEFINITION.value,
                value,
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

            attr_val (enums.SemPowerUnits):
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
                updated_selector_string, attributes.AttributeID.SEM_POWER_UNITS.value
            )
            attr_val = enums.SemPowerUnits(attr_val)
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

            value (enums.SemPowerUnits, int):
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
            value = value.value if type(value) is enums.SemPowerUnits else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_POWER_UNITS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_reference_type(self, selector_string):
        r"""Gets whether the power reference is the integrated power or the peak power in the closest carrier channel.
        The leftmost carrier is the carrier closest to all the lower (negative) offset segments. The rightmost carrier
        is the carrier closest to all the upper (positive) offset segments.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Integration**.

        +-----------------+---------------------------------------------------------------------+
        | Name (Value)    | Description                                                         |
        +=================+=====================================================================+
        | Integration (0) | The power reference is the integrated power of the closest carrier. |
        +-----------------+---------------------------------------------------------------------+
        | Peak (1)        | The power reference is the peak power of the closest carrier.       |
        +-----------------+---------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemReferenceType):
                Specifies whether the power reference is the integrated power or the peak power in the closest carrier channel.
                The leftmost carrier is the carrier closest to all the lower (negative) offset segments. The rightmost carrier
                is the carrier closest to all the upper (positive) offset segments.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_REFERENCE_TYPE.value
            )
            attr_val = enums.SemReferenceType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_reference_type(self, selector_string, value):
        r"""Sets whether the power reference is the integrated power or the peak power in the closest carrier channel.
        The leftmost carrier is the carrier closest to all the lower (negative) offset segments. The rightmost carrier
        is the carrier closest to all the upper (positive) offset segments.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Integration**.

        +-----------------+---------------------------------------------------------------------+
        | Name (Value)    | Description                                                         |
        +=================+=====================================================================+
        | Integration (0) | The power reference is the integrated power of the closest carrier. |
        +-----------------+---------------------------------------------------------------------+
        | Peak (1)        | The power reference is the peak power of the closest carrier.       |
        +-----------------+---------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemReferenceType, int):
                Specifies whether the power reference is the integrated power or the peak power in the closest carrier channel.
                The leftmost carrier is the carrier closest to all the lower (negative) offset segments. The rightmost carrier
                is the carrier closest to all the upper (positive) offset segments.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemReferenceType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_REFERENCE_TYPE.value, value
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

        +--------------+---------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                         |
        +==============+=====================================================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the SEM Sweep Time attribute.                               |
        +--------------+---------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the SEM Offset RBW and                              |
        |              | SEM Carrier RBW attributes.                                                                                         |
        +--------------+---------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemSweepTimeAuto):
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
                updated_selector_string, attributes.AttributeID.SEM_SWEEP_TIME_AUTO.value
            )
            attr_val = enums.SemSweepTimeAuto(attr_val)
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

        +--------------+---------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                         |
        +==============+=====================================================================================================================+
        | False (0)    | The measurement uses the sweep time that you specify in the SEM Sweep Time attribute.                               |
        +--------------+---------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement calculates the sweep time based on the value of the SEM Offset RBW and                              |
        |              | SEM Carrier RBW attributes.                                                                                         |
        +--------------+---------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemSweepTimeAuto, int):
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
            value = value.value if type(value) is enums.SemSweepTimeAuto else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_SWEEP_TIME_AUTO.value, value
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
                updated_selector_string, attributes.AttributeID.SEM_SWEEP_TIME_INTERVAL.value
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
                updated_selector_string, attributes.AttributeID.SEM_SWEEP_TIME_INTERVAL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the SEM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The SEM measurement uses the SEM Averaging Count attribute as the number of acquisitions over which the SEM measurement  |
        |              | is averaged.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemAveragingEnabled):
                Specifies whether to enable averaging for the SEM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_AVERAGING_ENABLED.value
            )
            attr_val = enums.SemAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the SEM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The SEM measurement uses the SEM Averaging Count attribute as the number of acquisitions over which the SEM measurement  |
        |              | is averaged.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.SemAveragingEnabled, int):
                Specifies whether to enable averaging for the SEM measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.SemAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.SEM_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.SEM_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for SEM
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

            attr_val (enums.SemAveragingType):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for SEM
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
                updated_selector_string, attributes.AttributeID.SEM_AVERAGING_TYPE.value
            )
            attr_val = enums.SemAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for SEM
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

            value (enums.SemAveragingType, int):
                Specifies the averaging type for averaging multiple spectrum acquisitions. The averaged spectrum is used for SEM
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
            value = value.value if type(value) is enums.SemAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_AVERAGING_TYPE.value, value
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

            attr_val (enums.SemFftWindow):
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
                updated_selector_string, attributes.AttributeID.SEM_FFT_WINDOW.value
            )
            attr_val = enums.SemFftWindow(attr_val)
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

            value (enums.SemFftWindow, int):
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
            value = value.value if type(value) is enums.SemFftWindow else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_FFT_WINDOW.value, value
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
                updated_selector_string, attributes.AttributeID.SEM_FFT_PADDING.value
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
                updated_selector_string, attributes.AttributeID.SEM_FFT_PADDING.value, value
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

            attr_val (enums.SemAmplitudeCorrectionType):
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
                updated_selector_string, attributes.AttributeID.SEM_AMPLITUDE_CORRECTION_TYPE.value
            )
            attr_val = enums.SemAmplitudeCorrectionType(attr_val)
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

            value (enums.SemAmplitudeCorrectionType, int):
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
            value = value.value if type(value) is enums.SemAmplitudeCorrectionType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.SEM_AMPLITUDE_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the SEM measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the SEM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the SEM measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the SEM measurement.

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
                updated_selector_string, attributes.AttributeID.SEM_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for SEM measurement.

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
                Specifies the maximum number of threads used for parallelism for SEM measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.SEM_NUMBER_OF_ANALYSIS_THREADS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for SEM measurement.

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
                Specifies the maximum number of threads used for parallelism for SEM measurement.

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
                attributes.AttributeID.SEM_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the spectral emission mask (SEM) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.SemAveragingEnabled, int):
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

            averaging_type (enums.SemAveragingType, int):
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
                if type(averaging_enabled) is enums.SemAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.SemAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_channel_bandwidth(self, selector_string, carrier_channel_bandwidth):
        r"""Configures the channel bandwidth of the carrier.

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

            carrier_channel_bandwidth (float):
                This parameter specifies the channel bandwidth of the carrier. This parameter is used to calculate the values of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_START_FREQUENCY` and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_STOP_FREQUENCY` attributes when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute to **Carrier Edge to Meas BW
                Center** or **Carrier Edge to Meas BW Edge**. The default value is 2 MHz.

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
            error_code = self._interpreter.sem_configure_carrier_channel_bandwidth(
                updated_selector_string, carrier_channel_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_enabled(self, selector_string, carrier_enabled):
        r"""Configures whether to consider the carrier power as part of total carrier power measurement.
        Use "carrier<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

            carrier_enabled (enums.SemCarrierEnabled, int):
                This parameter specifies whether to consider the carrier power as part of total carrier power measurement. The default
                value is **True**.

                +--------------+-------------------------------------------------------------------------+
                | Name (Value) | Description                                                             |
                +==============+=========================================================================+
                | False (0)    | The carrier power is not considered as part of the total carrier power. |
                +--------------+-------------------------------------------------------------------------+
                | True (1)     | The carrier power is considered as part of the total carrier power.     |
                +--------------+-------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            carrier_enabled = (
                carrier_enabled.value
                if type(carrier_enabled) is enums.SemCarrierEnabled
                else carrier_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_carrier_enabled(
                updated_selector_string, carrier_enabled
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
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

            integration_bandwidth (float):
                This parameter specifies the frequency range, in Hz, over which the measurement integrates the carrier channel power.
                The default value is 2 MHz.

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
            error_code = self._interpreter.sem_configure_carrier_integration_bandwidth(
                updated_selector_string, integration_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_frequency(self, selector_string, carrier_frequency):
        r"""Configures the center frequency, in Hz, of the carrier, relative to the RF center frequency.

        Use "carrier<
        *
        n
        *
        >" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

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
            error_code = self._interpreter.sem_configure_carrier_frequency(
                updated_selector_string, carrier_frequency
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the resolution bandwidth (RBW) filter of the carrier signal.
        Use "carrier<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

            rbw_auto (enums.SemCarrierRbwAutoBandwidth, int):
                This parameter specifies whether the measurement computes the resolution bandwidth (RBW) of the carrier. Refer to the
                `SEM <www.ni.com/docs/en-US/bundle/rfmx-specan/page/sem.html>`_ topic for more details on RBW. The default value is
                **True**.

                +--------------+-----------------------------------------------------------------------+
                | Name (Value) | Description                                                           |
                +==============+=======================================================================+
                | False (0)    | The measurement uses the RBW that you specify in the                  |
                |              | RBW                                                                   |
                |              | parameter.                                                            |
                +--------------+-----------------------------------------------------------------------+
                | True (1)     | The measurement computes the RBW.                                     |
                +--------------+-----------------------------------------------------------------------+

            rbw (float):
                This parameter specifies the bandwidth, in Hz, of the resolution bandwidth (RBW) filter used to sweep the acquired
                carrier signal, when you set the **RBW Auto** parameter to **False**. The default value is 10 kHz.

            rbw_filter_type (enums.SemCarrierRbwFilterType, int):
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
                rbw_auto.value if type(rbw_auto) is enums.SemCarrierRbwAutoBandwidth else rbw_auto
            )
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.SemCarrierRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_carrier_rbw_filter(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_carrier_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        r"""Configures the root raised cosine (RRC) channel filter to apply on the acquired carrier channel before measuring the
        channel power. RRC alpha is the filter roll off.
        Use "carrier<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of carrier
                number.

                Example:

                "carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

            rrc_filter_enabled (enums.SemCarrierRrcFilterEnabled, int):
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
                if type(rrc_filter_enabled) is enums.SemCarrierRrcFilterEnabled
                else rrc_filter_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_carrier_rrc_filter(
                updated_selector_string, rrc_filter_enabled, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fft(self, selector_string, fft_window, fft_padding):
        r"""Configures window and FFT to obtain a spectrum for the spectral emission mask (SEM) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            fft_window (enums.SemFftWindow, int):
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
            fft_window = fft_window.value if type(fft_window) is enums.SemFftWindow else fft_window
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_fft(
                updated_selector_string, fft_window, fft_padding
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_carriers(self, selector_string, number_of_carriers):
        r"""Configures the number of carriers for the spectral emission mask (SEM) measurement.

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
            error_code = self._interpreter.sem_configure_number_of_carriers(
                updated_selector_string, number_of_carriers
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_offsets(self, selector_string, number_of_offsets):
        r"""Configures the number of offset segments for the spectral emission mask (SEM) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_offsets (int):
                This parameter specifies the number of offset segments. The default value is 1.

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
            error_code = self._interpreter.sem_configure_number_of_offsets(
                updated_selector_string, number_of_offsets
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_absolute_limit_array(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        r"""Configures the absolute limit mode and specifies the absolute power limits corresponding to the beginning and end of
        the offset segment.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            absolute_limit_mode (enums.SemOffsetAbsoluteLimitMode, int):
                This parameter specifies whether the absolute limit mask is a flat line or a line with a slope. The default value is
                **Couple**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | The line specified by the SEM Offset Abs Limit Start and SEM Offset Abs Limit Stop                                       |
                |              | attribute values as the two ends is considered as the mask.                                                              |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Abs Limit Start attribute.                           |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            absolute_limit_start (float):
                This parameter specifies the array of absolute power limits, in dBm, corresponding to the beginning of the offset
                segment. The value of this parameter is also set as the stop limit for the offset segment when you set the **Absolute
                Limit Mode** parameter to **Couple**. The default value is -10.

            absolute_limit_stop (float):
                This parameter specifies the array of absolute power limits, in dBm, corresponding to the end of the offset segment.
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
                    and all(
                        isinstance(v, enums.SemOffsetAbsoluteLimitMode) for v in absolute_limit_mode
                    )
                )
                else absolute_limit_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_absolute_limit_array(
                updated_selector_string,
                absolute_limit_mode,
                absolute_limit_start,
                absolute_limit_stop,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_absolute_limit(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        r"""Configures the absolute limit mode and specifies the absolute power limits corresponding to the beginning and end of
        the offset segment.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            absolute_limit_mode (enums.SemOffsetAbsoluteLimitMode, int):
                This parameter specifies whether the absolute limit mask is a flat line or a line with a slope. The default value is
                **Couple**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | The line specified by the SEM Offset Abs Limit Start and SEM Offset Abs Limit Stop                                       |
                |              | attribute values as the two ends is considered as the mask.                                                              |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Abs Limit Start attribute.                           |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            absolute_limit_start (float):
                This parameter specifies the absolute power limit, in dBm, corresponding to the beginning of the offset segment. The
                value of this parameter is also set as the stop limit for the offset segment when you set the **Absolute Limit Mode**
                parameter to **Couple**. The default value is -10.

            absolute_limit_stop (float):
                This parameter specifies the absolute power limit, in dBm, corresponding to the end of the offset segment. This
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
                if type(absolute_limit_mode) is enums.SemOffsetAbsoluteLimitMode
                else absolute_limit_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_absolute_limit(
                updated_selector_string,
                absolute_limit_mode,
                absolute_limit_start,
                absolute_limit_stop,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_bandwidth_integral(self, selector_string, bandwidth_integral):
        r"""Configures the resolution of the spectrum to compare with spectral mask limits as an integer multiple of the resolution
        bandwidth (RBW).
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            bandwidth_integral (int):
                This parameter specifies the resolution of the spectrum to compare with spectral mask limits as an integer multiple of
                the RBW. If you set this parameter to a value greater than 1, the measurement acquires the spectrum with a narrow
                resolution and then processes it digitally to get a wider resolution that is equal to the product of the bandwidth
                integral and the RBW. The default value is 1.

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
            error_code = self._interpreter.sem_configure_offset_bandwidth_integral(
                updated_selector_string, bandwidth_integral
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_frequency_array(
        self,
        selector_string,
        offset_start_frequency,
        offset_stop_frequency,
        offset_enabled,
        offset_sideband,
    ):
        r"""Configures the offset frequency start and stop values and specifies whether the offset segment is present on one side,
        or on both sides of the carriers.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            offset_start_frequency (float):
                This parameter specifies the array of start frequencies, in Hz, of each offset segment relative to the closest
                configured carrier channel bandwidth center or carrier channel bandwidth edge based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. The default value is 1 MHz.

            offset_stop_frequency (float):
                This parameter specifies the array of stop frequencies, in Hz, of each offset segment relative to the closest
                configured carrier channel bandwidth center or carrier channel bandwidth edge based on the value of the SEM Offset Freq
                Definition attribute. The default value is 2 MHz.

            offset_enabled (enums.SemOffsetEnabled, int):
                This parameter specifies whether to enable the offset segment for the SEM measurement. The default value is **True**.

                +--------------+------------------------------------------------------+
                | Name (Value) | Description                                          |
                +==============+======================================================+
                | False (0)    | Disables the offset segment for the SEM measurement. |
                +--------------+------------------------------------------------------+
                | True (1)     | Enables the offset segment for the SEM measurement.  |
                +--------------+------------------------------------------------------+

            offset_sideband (enums.SemOffsetSideband, int):
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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_enabled = (
                [v.value for v in offset_enabled]
                if (
                    isinstance(offset_enabled, list)
                    and all(isinstance(v, enums.SemOffsetEnabled) for v in offset_enabled)
                )
                else offset_enabled
            )
            offset_sideband = (
                [v.value for v in offset_sideband]
                if (
                    isinstance(offset_sideband, list)
                    and all(isinstance(v, enums.SemOffsetSideband) for v in offset_sideband)
                )
                else offset_sideband
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_frequency_array(
                updated_selector_string,
                offset_start_frequency,
                offset_stop_frequency,
                offset_enabled,
                offset_sideband,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_frequency_definition(self, selector_string, offset_frequency_definition):
        r"""Configures the offset frequency definition for the SEM measurement.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter specifies the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method to build the selector string.

            offset_frequency_definition (enums.SemOffsetFrequencyDefinition, int):
                This parameter specifies the definition of  the start frequency and stop frequency of the offset segments from the
                nearest carrier channels. The default value is **Carrier Center to Meas BW Center**.

                +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)                         | Description                                                                                                              |
                +======================================+==========================================================================================================================+
                | Carrier Center to Meas BW Center (0) | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
                |                                      | center of the offset segment measurement bandwidth.                                                                      |
                |                                      | Measurement Bandwidth = Resolution Bandwidth * Bandwidth Integral.                                                       |
                +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Carrier Center to Meas BW Edge (1)   | The start frequency and stop frequency are defined from the center of the closest carrier channel bandwidth to the       |
                |                                      | nearest edge of the offset segment measurement bandwidth.                                                                |
                +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Carrier Edge to Meas BW Center (2)   | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
                |                                      | the center of the nearest offset segment measurement bandwidth.                                                          |
                +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
                | Carrier Edge to Meas BW Edge (3)     | The start frequency and stop frequency are defined from the nearest edge of the closest carrier channel bandwidth to     |
                |                                      | the edge of the nearest offset segment measurement bandwidth.                                                            |
                +--------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_frequency_definition = (
                offset_frequency_definition.value
                if type(offset_frequency_definition) is enums.SemOffsetFrequencyDefinition
                else offset_frequency_definition
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_frequency_definition(
                updated_selector_string, offset_frequency_definition
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_frequency(
        self,
        selector_string,
        offset_start_frequency,
        offset_stop_frequency,
        offset_enabled,
        offset_sideband,
    ):
        r"""Configures the offset frequency start and stop values and specifies whether the offset segment is present on one side,
        or on both sides of the carriers.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            offset_start_frequency (float):
                This parameter specifies the start frequency, in Hz, of the offset segment relative to the closest configured carrier
                channel bandwidth center or carrier channel bandwidth edge based on the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_FREQUENCY_DEFINITION` attribute. The default value is 1 MHz.

            offset_stop_frequency (float):
                This parameter specifies the stop frequency, in Hz, of the offset segment relative to the closest configured carrier
                channel bandwidth center or carrier channel bandwidth edge based on the value of the SEM Offset Freq Definition
                attribute. The default value is 2 MHz.

            offset_enabled (enums.SemOffsetEnabled, int):
                This parameter specifies whether to enable the offset segment for the SEM measurement. The default value is **True**.

                +--------------+------------------------------------------------------+
                | Name (Value) | Description                                          |
                +==============+======================================================+
                | False (0)    | Disables the offset segment for the SEM measurement. |
                +--------------+------------------------------------------------------+
                | True (1)     | Enables the offset segment for the SEM measurement.  |
                +--------------+------------------------------------------------------+

            offset_sideband (enums.SemOffsetSideband, int):
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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            offset_enabled = (
                offset_enabled.value
                if type(offset_enabled) is enums.SemOffsetEnabled
                else offset_enabled
            )
            offset_sideband = (
                offset_sideband.value
                if type(offset_sideband) is enums.SemOffsetSideband
                else offset_sideband
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_frequency(
                updated_selector_string,
                offset_start_frequency,
                offset_stop_frequency,
                offset_enabled,
                offset_sideband,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_limit_fail_mask(self, selector_string, limit_fail_mask):
        r"""Specifies the criteria to determine the measurement fail status.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            limit_fail_mask (enums.SemOffsetLimitFailMask, int):
                This parameter specifies the criteria to determine the measurement fail status. The default value is **Absolute**.

                +-----------------+-------------------------------------------------------------------------------------------------+
                | Name (Value)    | Description                                                                                     |
                +=================+=================================================================================================+
                | Abs AND Rel (0) | The measurement fails if the power in the segment exceeds both the absolute and relative masks. |
                +-----------------+-------------------------------------------------------------------------------------------------+
                | Abs OR Rel (1)  | The measurement fails if the power in the segment exceeds either the absolute or relative mask. |
                +-----------------+-------------------------------------------------------------------------------------------------+
                | Absolute (2)    | The measurement fails if the power in the segment exceeds the absolute mask.                    |
                +-----------------+-------------------------------------------------------------------------------------------------+
                | Relative (3)    | The measurement fails if the power in the segment exceeds the relative mask.                    |
                +-----------------+-------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            limit_fail_mask = (
                limit_fail_mask.value
                if type(limit_fail_mask) is enums.SemOffsetLimitFailMask
                else limit_fail_mask
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_limit_fail_mask(
                updated_selector_string, limit_fail_mask
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_rbw_filter_array(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the resolution bandwidth (RBW) filter of the offset segment.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw_auto (enums.SemOffsetRbwAutoBandwidth, int):
                This parameter specifies whether the measurement computes the RBW. Refer to the `SEM
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/sem.html>`_ topic for details on RBW and sweep time. The default value
                is **True**.

                +--------------+---------------------------------------------------------------------+
                | Name (Value) | Description                                                         |
                +==============+=====================================================================+
                | False (0)    | The measurement uses the RBW that you specify in the RBW parameter. |
                +--------------+---------------------------------------------------------------------+
                | True (1)     | The measurement computes the RBW.                                   |
                +--------------+---------------------------------------------------------------------+

            rbw (float):
                This parameter specifies the array of bandwidths, in Hz, of the resolution bandwidth (RBW) filter used to sweep the
                acquired offset segment, when you set the **RBW Auto** parameter to **False**. The default value is 10 kHz.

            rbw_filter_type (enums.SemOffsetRbwFilterType, int):
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
                    and all(isinstance(v, enums.SemOffsetRbwAutoBandwidth) for v in rbw_auto)
                )
                else rbw_auto
            )
            rbw_filter_type = (
                [v.value for v in rbw_filter_type]
                if (
                    isinstance(rbw_filter_type, list)
                    and all(isinstance(v, enums.SemOffsetRbwFilterType) for v in rbw_filter_type)
                )
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_rbw_filter_array(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        r"""Configures the resolution bandwidth (RBW) filter of the offset segment.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            rbw_auto (enums.SemOffsetRbwAutoBandwidth, int):
                This parameter specifies whether the measurement computes the RBW. Refer to the RBW and Sweep Time section in the `SEM
                <www.ni.com/docs/en-US/bundle/rfmx-specan/page/sem.html>`_ topic for more details on RBW and sweep time. The default
                value is **True**.

                +--------------+---------------------------------------------------------------------+
                | Name (Value) | Description                                                         |
                +==============+=====================================================================+
                | False (0)    | The measurement uses the RBW that you specify in the RBW parameter. |
                +--------------+---------------------------------------------------------------------+
                | True (1)     | The measurement computes the RBW.                                   |
                +--------------+---------------------------------------------------------------------+

            rbw (float):
                This parameter specifies the bandwidth, in Hz, of the resolution bandwidth (RBW) filter used to sweep the acquired
                offset segment, when you set the **RBW Auto** parameter to **False**. The default value is 10 kHz.

            rbw_filter_type (enums.SemOffsetRbwFilterType, int):
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
                rbw_auto.value if type(rbw_auto) is enums.SemOffsetRbwAutoBandwidth else rbw_auto
            )
            rbw_filter_type = (
                rbw_filter_type.value
                if type(rbw_filter_type) is enums.SemOffsetRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_rbw_filter(
                updated_selector_string, rbw_auto, rbw, rbw_filter_type
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
            error_code = self._interpreter.sem_configure_offset_relative_attenuation_array(
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
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

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
            error_code = self._interpreter.sem_configure_offset_relative_attenuation(
                updated_selector_string, relative_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_relative_limit_array(
        self, selector_string, relative_limit_mode, relative_limit_start, relative_limit_stop
    ):
        r"""Configures the relative limit mode and specifies the relative power limits corresponding to the beginning and end of
        the offset segment.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            relative_limit_mode (enums.SemOffsetRelativeLimitMode, int):
                This parameter specifies whether the relative limit mask is a flat line or a line with a slope. The default value is
                **Manual**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | The line specified by the SEM Offset Rel Limit Start and SEM Offset Rel Limit Stop attribute values as the two ends is   |
                |              | considered as the mask.                                                                                                  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Rel Limit Start attribute.                           |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            relative_limit_start (float):
                This parameter specifies the array of relative power limits, in dB, corresponding to the beginning of the offset
                segment. The value of this parameter is also set as the stop limit for the offset segment when you set the **Relative
                Limit Mode** parameter to **Couple**. The default value is -20.

            relative_limit_stop (float):
                This parameter specifies the array of relative power limits, in dB, corresponding to the end of the offset segment.
                This parameter is ignored if you set the **Relative Limit Mode** parameter to **Couple**. The default value is -30.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            relative_limit_mode = (
                [v.value for v in relative_limit_mode]
                if (
                    isinstance(relative_limit_mode, list)
                    and all(
                        isinstance(v, enums.SemOffsetRelativeLimitMode) for v in relative_limit_mode
                    )
                )
                else relative_limit_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_relative_limit_array(
                updated_selector_string,
                relative_limit_mode,
                relative_limit_start,
                relative_limit_stop,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_offset_relative_limit(
        self, selector_string, relative_limit_mode, relative_limit_start, relative_limit_stop
    ):
        r"""Configures the relative limit mode and specifies the relative power limits corresponding to the beginning and end of
        the offset segment.
        Use "offset<*n*>" as the selector string to configure this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of offset
                number.

                Example:

                "offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            relative_limit_mode (enums.SemOffsetRelativeLimitMode, int):
                This parameter specifies whether the relative limit mask is a flat line or a line with a slope. The default value is
                **Manual**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Manual (0)   | The line specified by the SEM Offset Rel Limit Start and SEM Offset Rel Limit Stop attribute values as the two ends is   |
                |              | considered as the mask.                                                                                                  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Couple (1)   | The two ends of the line are coupled to the value of the SEM Offset Rel Limit Start attribute.                           |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

            relative_limit_start (float):
                This parameter specifies the relative power limit, in dB, corresponding to the beginning of the offset segment. The
                value of this parameter is also set as the stop limit for the offset segment when you set the **Relative Limit Mode**
                parameter to **Couple**. The default value is -20.

            relative_limit_stop (float):
                This parameter specifies the relative power limit, in dB, corresponding to the end of the offset segment. This
                parameter is ignored if you set the **Relative Limit Mode** parameter to **Couple**. The default value is -30.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            relative_limit_mode = (
                relative_limit_mode.value
                if type(relative_limit_mode) is enums.SemOffsetRelativeLimitMode
                else relative_limit_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_offset_relative_limit(
                updated_selector_string,
                relative_limit_mode,
                relative_limit_start,
                relative_limit_stop,
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

            power_units (enums.SemPowerUnits, int):
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
                power_units.value if type(power_units) is enums.SemPowerUnits else power_units
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_power_units(
                updated_selector_string, power_units
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_type(self, selector_string, reference_type):
        r"""Configures whether the power reference is the integrated power or the peak power in the closest carrier channel.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            reference_type (enums.SemReferenceType, int):
                This parameter specifies whether the power reference is the integrated power or the peak power in the closest carrier
                channel. The leftmost carrier is the carrier closest to all the lower (negative) offset segments. The rightmost carrier
                offset is the carrier closest to all the upper (positive) offset segments. The default value is **Integration**.

                +-----------------+---------------------------------------------------------------------+
                | Name (Value)    | Description                                                         |
                +=================+=====================================================================+
                | Integration (0) | The power reference is the integrated power of the closest carrier. |
                +-----------------+---------------------------------------------------------------------+
                | Peak (1)        | The power reference is the peak power of the closest carrier.       |
                +-----------------+---------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            reference_type = (
                reference_type.value
                if type(reference_type) is enums.SemReferenceType
                else reference_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_reference_type(
                updated_selector_string, reference_type
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

            sweep_time_auto (enums.SemSweepTimeAuto, int):
                This parameter specifies whether the measurement computes the sweep time. The default value is **True**.

                +--------------+-------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                       |
                +==============+===================================================================================================================+
                | False (0)    | The measurement uses the sweep time that you specify in the Sweep Time Interval parameter.                        |
                +--------------+-------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement calculates the sweep time based on the value of the SEM Offset RBW and SEM Carrier RBW attribute. |
                +--------------+-------------------------------------------------------------------------------------------------------------------+

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
                if type(sweep_time_auto) is enums.SemSweepTimeAuto
                else sweep_time_auto
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.sem_configure_sweep_time(
                updated_selector_string, sweep_time_auto, sweep_time_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
