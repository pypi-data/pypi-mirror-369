"""Provides methods to configure the Harm measurement."""

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


class HarmConfiguration(object):
    """Provides methods to configure the Harm measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Harm measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the Harmonics measurement.

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
                Specifies whether to enable the Harmonics measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the Harmonics measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the Harmonics measurement.

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
                attributes.AttributeID.HARM_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fundamental_rbw_filter_bandwidth(self, selector_string):
        r"""Gets the bandwidth of the resolution bandwidth (RBW) filter used to measure the fundamental signal. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100 kHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the fundamental signal. This value is
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
                attributes.AttributeID.HARM_FUNDAMENTAL_RBW_FILTER_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fundamental_rbw_filter_bandwidth(self, selector_string, value):
        r"""Sets the bandwidth of the resolution bandwidth (RBW) filter used to measure the fundamental signal. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 100 kHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the bandwidth of the resolution bandwidth (RBW) filter used to measure the fundamental signal. This value is
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
                attributes.AttributeID.HARM_FUNDAMENTAL_RBW_FILTER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fundamental_rbw_filter_type(self, selector_string):
        r"""Gets the shape of the digital resolution bandwidth (RBW) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Gaussian**.

        **Supported devices**: PXIe-5665/5668

        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                           |
        +==============+=======================================================================================================================+
        | None (5)     | The measurement does not use any RBW filtering.                                                                       |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | Gaussian (1) | The RBW filter has a Gaussian response.                                                                               |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | Flat (2)     | The RBW filter                                                                                                        |
        |              | has a flat response.                                                                                                  |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | RRC (6)      | The RRC filter with the roll-off specified by the Harm Fundamental RBW RRC Alpha attribute is used as the RBW filter. |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmRbwFilterType):
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
                updated_selector_string,
                attributes.AttributeID.HARM_FUNDAMENTAL_RBW_FILTER_TYPE.value,
            )
            attr_val = enums.HarmRbwFilterType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fundamental_rbw_filter_type(self, selector_string, value):
        r"""Sets the shape of the digital resolution bandwidth (RBW) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Gaussian**.

        **Supported devices**: PXIe-5665/5668

        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                           |
        +==============+=======================================================================================================================+
        | None (5)     | The measurement does not use any RBW filtering.                                                                       |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | Gaussian (1) | The RBW filter has a Gaussian response.                                                                               |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | Flat (2)     | The RBW filter                                                                                                        |
        |              | has a flat response.                                                                                                  |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+
        | RRC (6)      | The RRC filter with the roll-off specified by the Harm Fundamental RBW RRC Alpha attribute is used as the RBW filter. |
        +--------------+-----------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmRbwFilterType, int):
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
            value = value.value if type(value) is enums.HarmRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.HARM_FUNDAMENTAL_RBW_FILTER_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fundamental_rbw_filter_alpha(self, selector_string):
        r"""Gets the roll-off factor for the root-raised-cosine (RRC) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1.

        **Supported devices**: PXIe-5665/5668

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
                updated_selector_string,
                attributes.AttributeID.HARM_FUNDAMENTAL_RBW_FILTER_ALPHA.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fundamental_rbw_filter_alpha(self, selector_string, value):
        r"""Sets the roll-off factor for the root-raised-cosine (RRC) filter.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.1.

        **Supported devices**: PXIe-5665/5668

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
                attributes.AttributeID.HARM_FUNDAMENTAL_RBW_FILTER_ALPHA.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_fundamental_measurement_interval(self, selector_string):
        r"""Gets the acquisition time for the Harmonics measurement of the fundamental signal. This value is expressed in
        seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition time for the Harmonics measurement of the fundamental signal. This value is expressed in
                seconds.

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
                attributes.AttributeID.HARM_FUNDAMENTAL_MEASUREMENT_INTERVAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_fundamental_measurement_interval(self, selector_string, value):
        r"""Sets the acquisition time for the Harmonics measurement of the fundamental signal. This value is expressed in
        seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition time for the Harmonics measurement of the fundamental signal. This value is expressed in
                seconds.

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
                attributes.AttributeID.HARM_FUNDAMENTAL_MEASUREMENT_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_harmonics(self, selector_string):
        r"""Gets the number of harmonics, including fundamental, to measure.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of harmonics, including fundamental, to measure.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_NUMBER_OF_HARMONICS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_harmonics(self, selector_string, value):
        r"""Sets the number of harmonics, including fundamental, to measure.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of harmonics, including fundamental, to measure.

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
                attributes.AttributeID.HARM_NUMBER_OF_HARMONICS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_auto_setup_enabled(self, selector_string):
        r"""Gets whether to enable auto configuration of successive harmonics.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement uses manual configuration for the harmonic order, harmonic bandwidth, and harmonic measurement           |
        |              | interval.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement uses the Harm Num Harmonics attribute and configuration of the fundamental to configure successive       |
        |              | harmonics.                                                                                                               |
        |              | Bandwidth of Nth order harmonic = N * (Bandwidth of fundamental).                                                        |
        |              | Measurement interval of Nth order harmonics = (Measurement interval of fundamental)/N                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmAutoHarmonicsSetupEnabled):
                Specifies whether to enable auto configuration of successive harmonics.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AUTO_SETUP_ENABLED.value
            )
            attr_val = enums.HarmAutoHarmonicsSetupEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_auto_setup_enabled(self, selector_string, value):
        r"""Sets whether to enable auto configuration of successive harmonics.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement uses manual configuration for the harmonic order, harmonic bandwidth, and harmonic measurement           |
        |              | interval.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The measurement uses the Harm Num Harmonics attribute and configuration of the fundamental to configure successive       |
        |              | harmonics.                                                                                                               |
        |              | Bandwidth of Nth order harmonic = N * (Bandwidth of fundamental).                                                        |
        |              | Measurement interval of Nth order harmonics = (Measurement interval of fundamental)/N                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmAutoHarmonicsSetupEnabled, int):
                Specifies whether to enable auto configuration of successive harmonics.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.HarmAutoHarmonicsSetupEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AUTO_SETUP_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_harmonic_enabled(self, selector_string):
        r"""Gets whether to enable a particular harmonic for measurement. Only the enabled harmonics are used to measure the
        total harmonic distortion (THD). This attribute is not used if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+----------------------------------------+
        | Name (Value) | Description                            |
        +==============+========================================+
        | False (0)    | Disables the harmonic for measurement. |
        +--------------+----------------------------------------+
        | True (1)     | Enables the harmonic for measurement.  |
        +--------------+----------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmHarmonicEnabled):
                Specifies whether to enable a particular harmonic for measurement. Only the enabled harmonics are used to measure the
                total harmonic distortion (THD). This attribute is not used if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_HARMONIC_ENABLED.value
            )
            attr_val = enums.HarmHarmonicEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_harmonic_enabled(self, selector_string, value):
        r"""Sets whether to enable a particular harmonic for measurement. Only the enabled harmonics are used to measure the
        total harmonic distortion (THD). This attribute is not used if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is **True**.

        **Supported devices**: PXIe-5665/5668

        +--------------+----------------------------------------+
        | Name (Value) | Description                            |
        +==============+========================================+
        | False (0)    | Disables the harmonic for measurement. |
        +--------------+----------------------------------------+
        | True (1)     | Enables the harmonic for measurement.  |
        +--------------+----------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmHarmonicEnabled, int):
                Specifies whether to enable a particular harmonic for measurement. Only the enabled harmonics are used to measure the
                total harmonic distortion (THD). This attribute is not used if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.HarmHarmonicEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_HARMONIC_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_harmonic_order(self, selector_string):
        r"""Gets the order of the harmonic. This attribute is not used if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Frequency of Nth order harmonic = N * (Frequency of fundamental)

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the order of the harmonic. This attribute is not used if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_HARMONIC_ORDER.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_harmonic_order(self, selector_string, value):
        r"""Sets the order of the harmonic. This attribute is not used if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Frequency of Nth order harmonic = N * (Frequency of fundamental)

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the order of the harmonic. This attribute is not used if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

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
                updated_selector_string, attributes.AttributeID.HARM_HARMONIC_ORDER.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_harmonic_bandwidth(self, selector_string):
        r"""Gets the resolution bandwidth for the harmonic. This attribute is not used if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**. This value is expressed in Hz.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 100 kHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the resolution bandwidth for the harmonic. This attribute is not used if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.HARM_HARMONIC_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_harmonic_bandwidth(self, selector_string, value):
        r"""Sets the resolution bandwidth for the harmonic. This attribute is not used if you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**. This value is expressed in Hz.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 100 kHz.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the resolution bandwidth for the harmonic. This attribute is not used if you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**. This value is expressed in Hz.

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
                updated_selector_string, attributes.AttributeID.HARM_HARMONIC_BANDWIDTH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_harmonic_measurement_interval(self, selector_string):
        r"""Gets the acquisition time for the harmonic. This value is expressed in seconds. This attribute is not used if you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 ms.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition time for the harmonic. This value is expressed in seconds. This attribute is not used if you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

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
                attributes.AttributeID.HARM_HARMONIC_MEASUREMENT_INTERVAL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_harmonic_measurement_interval(self, selector_string, value):
        r"""Sets the acquisition time for the harmonic. This value is expressed in seconds. This attribute is not used if you
        set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

        Use "harmonic<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 1 ms.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition time for the harmonic. This value is expressed in seconds. This attribute is not used if you
                set the :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` to **True**.

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
                attributes.AttributeID.HARM_HARMONIC_MEASUREMENT_INTERVAL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_method(self, selector_string):
        r"""Gets the method used to perform the harmonics measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Time Domain**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | Time Domain (0)   | The harmonics measurement acquires the signal using the same signal analyzer setting across frequency bands. Use this    |
        |                   | method when the measurement speed is desirable over higher dynamic range.                                                |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Dynamic Range (2) | The harmonics measurement acquires the signal using the hardware-specific features, such as the IF filter and IF gain,   |
        |                   | for different frequency bands. Use this method to get the best dynamic range.                                            |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmMeasurementMethod):
                Specifies the method used to perform the harmonics measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_MEASUREMENT_METHOD.value
            )
            attr_val = enums.HarmMeasurementMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_method(self, selector_string, value):
        r"""Sets the method used to perform the harmonics measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Time Domain**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | Time Domain (0)   | The harmonics measurement acquires the signal using the same signal analyzer setting across frequency bands. Use this    |
        |                   | method when the measurement speed is desirable over higher dynamic range.                                                |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Dynamic Range (2) | The harmonics measurement acquires the signal using the hardware-specific features, such as the IF filter and IF gain,   |
        |                   | for different frequency bands. Use this method to get the best dynamic range.                                            |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmMeasurementMethod, int):
                Specifies the method used to perform the harmonics measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.HarmMeasurementMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_MEASUREMENT_METHOD.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_noise_compensation_enabled(self, selector_string):
        r"""Gets whether to enable compensation of the average harmonic powers for inherent noise floor of the signal
        analyzer.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables compensation of the average harmonic powers for the noise floor of the signal analyzer.                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables compensation of the average harmonic powers for the noise floor of the signal analyzer. The noise floor of the   |
        |              | signal analyzer is measured for the RF path used by the harmonics measurement and cached for future use. If the signal   |
        |              | analyzer or measurement parameters change, noise floors are measured again.                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmNoiseCompensationEnabled):
                Specifies whether to enable compensation of the average harmonic powers for inherent noise floor of the signal
                analyzer.

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
                attributes.AttributeID.HARM_NOISE_COMPENSATION_ENABLED.value,
            )
            attr_val = enums.HarmNoiseCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_noise_compensation_enabled(self, selector_string, value):
        r"""Sets whether to enable compensation of the average harmonic powers for inherent noise floor of the signal
        analyzer.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables compensation of the average harmonic powers for the noise floor of the signal analyzer.                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables compensation of the average harmonic powers for the noise floor of the signal analyzer. The noise floor of the   |
        |              | signal analyzer is measured for the RF path used by the harmonics measurement and cached for future use. If the signal   |
        |              | analyzer or measurement parameters change, noise floors are measured again.                                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmNoiseCompensationEnabled, int):
                Specifies whether to enable compensation of the average harmonic powers for inherent noise floor of the signal
                analyzer.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.HarmNoiseCompensationEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.HARM_NOISE_COMPENSATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the Harmonics measurement.

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
        | True (1)     | The Harmonics measurement uses the Harm Averaging Count attribute as the number of acquisitions over which the           |
        |              | Harmonics measurement is averaged.                                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmAveragingEnabled):
                Specifies whether to enable averaging for the Harmonics measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AVERAGING_ENABLED.value
            )
            attr_val = enums.HarmAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the Harmonics measurement.

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
        | True (1)     | The Harmonics measurement uses the Harm Averaging Count attribute as the number of acquisitions over which the           |
        |              | Harmonics measurement is averaged.                                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmAveragingEnabled, int):
                Specifies whether to enable averaging for the Harmonics measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.HarmAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AVERAGING_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_count(self, selector_string):
        r"""Gets the number of acquisitions used for averaging when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the number of acquisitions used for averaging when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AVERAGING_COUNT.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_count(self, selector_string, value):
        r"""Sets the number of acquisitions used for averaging when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of acquisitions used for averaging when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.AVERAGING_COUNT` attribute to **True**.

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
                updated_selector_string, attributes.AttributeID.HARM_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for the Harmonics measurement. The averaged power trace is used for the measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668

        +--------------+----------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                              |
        +==============+==========================================================================================================+
        | RMS (0)      | The power trace is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Log (1)      | The power trace is averaged in a logarithmic scale.                                                      |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Scalar (2)   | The square root of the power trace is averaged.                                                          |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Max (3)      | The maximum instantaneous power in the power trace is retained from one acquisition to the next.         |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Min (4)      | The minimum instantaneous power in the power trace is retained from one acquisition to the next.         |
        +--------------+----------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.HarmAveragingType):
                Specifies the averaging type for the Harmonics measurement. The averaged power trace is used for the measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AVERAGING_TYPE.value
            )
            attr_val = enums.HarmAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for the Harmonics measurement. The averaged power trace is used for the measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RMS**.

        **Supported devices**: PXIe-5644/5645/5646, PXIe-5663/5663E/5665/5668

        +--------------+----------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                              |
        +==============+==========================================================================================================+
        | RMS (0)      | The power trace is linearly averaged. RMS averaging reduces signal fluctuations but not the noise floor. |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Log (1)      | The power trace is averaged in a logarithmic scale.                                                      |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Scalar (2)   | The square root of the power trace is averaged.                                                          |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Max (3)      | The maximum instantaneous power in the power trace is retained from one acquisition to the next.         |
        +--------------+----------------------------------------------------------------------------------------------------------+
        | Min (4)      | The minimum instantaneous power in the power trace is retained from one acquisition to the next.         |
        +--------------+----------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.HarmAveragingType, int):
                Specifies the averaging type for the Harmonics measurement. The averaged power trace is used for the measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.HarmAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_AVERAGING_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the Harmonics measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the Harmonics measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.HARM_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the Harmonics measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        **Supported devices**: PXIe-5665/5668

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the Harmonics measurement.

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
                updated_selector_string, attributes.AttributeID.HARM_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for Harmonics measurement.

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
                Specifies the maximum number of threads used for parallelism for Harmonics measurement.

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
                attributes.AttributeID.HARM_NUMBER_OF_ANALYSIS_THREADS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for Harmonics measurement.

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
                Specifies the maximum number of threads used for parallelism for Harmonics measurement.

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
                attributes.AttributeID.HARM_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_auto_harmonics(self, selector_string, auto_harmonics_setup_enabled):
        r"""Configures auto configuration of successive harmonics.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            auto_harmonics_setup_enabled (enums.HarmAutoHarmonicsSetupEnabled, int):
                This parameter specifies whether to enable auto configuration of successive harmonics. The default value is **True**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | The measurement uses manual configuration for the harmonic order, harmonic bandwidth, and harmonic measurement           |
                |              | interval.                                                                                                                |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | The measurement uses the Harm Num Harmonics attribute and configuration of the fundamental to configure successive       |
                |              | harmonics.                                                                                                               |
                |              | Bandwidth of Nth order harmonic = N * (Bandwidth of fundamental).                                                        |
                |              | Measurement interval of Nth order harmonics = (Measurement interval of fundamental)/N                                    |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            auto_harmonics_setup_enabled = (
                auto_harmonics_setup_enabled.value
                if type(auto_harmonics_setup_enabled) is enums.HarmAutoHarmonicsSetupEnabled
                else auto_harmonics_setup_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.harm_configure_auto_harmonics(
                updated_selector_string, auto_harmonics_setup_enabled
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the harmonics measurement.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.HarmAveragingEnabled, int):
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

            averaging_type (enums.HarmAveragingType, int):
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
                if type(averaging_enabled) is enums.HarmAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.HarmAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.harm_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fundamental_measurement_interval(self, selector_string, measurement_interval):
        r"""Configures the acquisition time, in seconds, for acquiring the fundamental signal.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_interval (float):
                This parameter specifies the acquisition time, in seconds, for the Harmonics measurement of the fundamental signal. The
                default value is 1 ms.

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
            error_code = self._interpreter.harm_configure_fundamental_measurement_interval(
                updated_selector_string, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_fundamental_rbw(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        r"""Configures the resolution bandwidth (RBW) filter to be applied on the acquired signal. The bandwidth of the filter
        specified is applicable for fundamental signal.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw (float):
                This parameter specifies the bandwidth, in Hz, of the resolution bandwidth (RBW) filter used to acquire the fundamental
                signal. The default value is 100 kHz.

            rbw_filter_type (enums.HarmRbwFilterType, int):
                This parameter specifies the shape of the digital RBW filter. The default value is **Gaussian**.

                +--------------+----------------------------------------------------------+
                | Name (Value) | Description                                              |
                +==============+==========================================================+
                | None (1)     | The measurement does not use any RBW filtering.          |
                +--------------+----------------------------------------------------------+
                | Gaussian (2) | An RBW filter with a Gaussian response is applied.       |
                +--------------+----------------------------------------------------------+
                | Flat (3)     | An RBW filter with a flat response is applied.           |
                +--------------+----------------------------------------------------------+
                | RRC (4)      | The measurement uses RRC FIR coefficients for filtering. |
                +--------------+----------------------------------------------------------+

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
                if type(rbw_filter_type) is enums.HarmRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.harm_configure_fundamental_rbw(
                updated_selector_string, rbw, rbw_filter_type, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_harmonic_array(
        self,
        selector_string,
        harmonic_order,
        harmonic_bandwidth,
        harmonic_enabled,
        harmonic_measurement_interval,
    ):
        r"""Configures the harmonic frequency, acquisition bandwidth, and acquisition time for the harmonic, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` attribute to **False**.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            harmonic_order (int):
                This parameter specifies the array of the orders of the harmonics. The default value is 1.

                Frequency of Nth order harmonic = N * (Frequency of fundamental)

            harmonic_bandwidth (float):
                This parameter specifies the array of resolution bandwidths, in Hz, for the harmonic. The default value is 100 kHz.

            harmonic_enabled (enums.HarmHarmonicEnabled, int):
                This parameter specifies whether to enable a particular harmonic for measurement. Only the enabled harmonics are used
                to measure the total harmonic distortion (THD). The default value is **True**.

                +--------------+----------------------------------------+
                | Name (Value) | Description                            |
                +==============+========================================+
                | False (0)    | Disables the harmonic for measurement. |
                +--------------+----------------------------------------+
                | True (1)     | Enables the harmonic for measurement.  |
                +--------------+----------------------------------------+

            harmonic_measurement_interval (float):
                This parameter specifies the array of acquisition times, in seconds, for the harmonic. The default value is 1 ms.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            harmonic_enabled = (
                [v.value for v in harmonic_enabled]
                if (
                    isinstance(harmonic_enabled, list)
                    and all(isinstance(v, enums.HarmHarmonicEnabled) for v in harmonic_enabled)
                )
                else harmonic_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.harm_configure_harmonic_array(
                updated_selector_string,
                harmonic_order,
                harmonic_bandwidth,
                harmonic_enabled,
                harmonic_measurement_interval,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_harmonic(
        self,
        selector_string,
        harmonic_order,
        harmonic_bandwidth,
        harmonic_enabled,
        harmonic_measurement_interval,
    ):
        r"""Configures the harmonic frequency, acquisition bandwidth, and acquisition time for the harmonic, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_SETUP_ENABLED` attribute to **False**.
        Use "harmonic<*n*>" as the selector string to configure this method.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of harmonic
                number.

                Example:

                "harmonic0"

                You can use the :py:meth:`build_harmonic_string` method  to build the selector string.

            harmonic_order (int):
                This parameter specifies the order of the harmonic. The default value is 1.

                Frequency of Nth order harmonic = N * (Frequency of fundamental)

            harmonic_bandwidth (float):
                This parameter specifies the resolution bandwidth, in Hz, for the harmonic. The default value is 100 kHz.

            harmonic_enabled (enums.HarmHarmonicEnabled, int):
                This parameter specifies whether to enable a particular harmonic for measurement. Only the enabled harmonics are used
                to measure the total harmonic distortion (THD). The default value is **True**.

                +--------------+----------------------------------------+
                | Name (Value) | Description                            |
                +==============+========================================+
                | False (0)    | Disables the harmonic for measurement. |
                +--------------+----------------------------------------+
                | True (1)     | Enables the harmonic for measurement.  |
                +--------------+----------------------------------------+

            harmonic_measurement_interval (float):
                This parameter specifies the acquisition time, in seconds, for the harmonic. The default value is 1 ms.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            harmonic_enabled = (
                harmonic_enabled.value
                if type(harmonic_enabled) is enums.HarmHarmonicEnabled
                else harmonic_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.harm_configure_harmonic(
                updated_selector_string,
                harmonic_order,
                harmonic_bandwidth,
                harmonic_enabled,
                harmonic_measurement_interval,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_number_of_harmonics(self, selector_string, number_of_harmonics):
        r"""Configures the  number of harmonics, including fundamental, to measure.
        **Supported devices:** PXIe-5665, PXIe-5668

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            number_of_harmonics (int):
                This parameter specifies the number of harmonics, including fundamental, to measure. The default value is 3.

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
            error_code = self._interpreter.harm_configure_number_of_harmonics(
                updated_selector_string, number_of_harmonics
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
