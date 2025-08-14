"""Provides methods to configure the NF measurement."""

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


class NFConfiguration(object):
    """Provides methods to configure the NF measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the NF measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Enables the noise figure (NF) measurement.

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
                Enables the noise figure (NF) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Enables the noise figure (NF) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Enables the noise figure (NF) measurement.

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
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_type(self, selector_string):
        r"""Gets the type of DUT.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Amplifier**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | Amplifier (0)     | Specifies that the DUT only amplifies or attenuates the signal, and does not change the frequency.                       |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Downconverter (1) | Specifies that the DUT is a downconverter, that is, the IF frequency is the difference between the LO and RF             |
        |                   | frequencies.                                                                                                             |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Upconverter (2)   | Specifies that the DUT is an upconverter, that is, the IF frequency is the sum of LO and RF frequencies.                 |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFDutType):
                Specifies the type of DUT.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_DUT_TYPE.value
            )
            attr_val = enums.NFDutType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_type(self, selector_string, value):
        r"""Sets the type of DUT.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Amplifier**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | Amplifier (0)     | Specifies that the DUT only amplifies or attenuates the signal, and does not change the frequency.                       |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Downconverter (1) | Specifies that the DUT is a downconverter, that is, the IF frequency is the difference between the LO and RF             |
        |                   | frequencies.                                                                                                             |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Upconverter (2)   | Specifies that the DUT is an upconverter, that is, the IF frequency is the sum of LO and RF frequencies.                 |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFDutType, int):
                Specifies the type of DUT.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFDutType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_DUT_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_converter_lo_frequency(self, selector_string):
        r"""Gets the fixed LO frequency of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE`
        attribute to either **Downconverter** or **Upconverter**. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the fixed LO frequency of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE`
                attribute to either **Downconverter** or **Upconverter**. This value is expressed in Hz.

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
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_LO_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_converter_lo_frequency(self, selector_string, value):
        r"""Sets the fixed LO frequency of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE`
        attribute to either **Downconverter** or **Upconverter**. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the fixed LO frequency of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE`
                attribute to either **Downconverter** or **Upconverter**. This value is expressed in Hz.

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
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_LO_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_converter_frequency_context(self, selector_string):
        r"""Gets the context of the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RF**.

        +--------------+---------------------------------------------+
        | Name (Value) | Description                                 |
        +==============+=============================================+
        | RF (0)       | Specifies that the frequency context is RF. |
        +--------------+---------------------------------------------+
        | IF (1)       | Specifies that the frequency context is IF. |
        +--------------+---------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFFrequencyConverterFrequencyContext):
                Specifies the context of the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute.

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
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_FREQUENCY_CONTEXT.value,
            )
            attr_val = enums.NFFrequencyConverterFrequencyContext(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_converter_frequency_context(self, selector_string, value):
        r"""Sets the context of the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **RF**.

        +--------------+---------------------------------------------+
        | Name (Value) | Description                                 |
        +==============+=============================================+
        | RF (0)       | Specifies that the frequency context is RF. |
        +--------------+---------------------------------------------+
        | IF (1)       | Specifies that the frequency context is IF. |
        +--------------+---------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFFrequencyConverterFrequencyContext, int):
                Specifies the context of the :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute.

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
                value.value if type(value) is enums.NFFrequencyConverterFrequencyContext else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_FREQUENCY_CONTEXT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_converter_sideband(self, selector_string):
        r"""Gets the sideband when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE` attribute to either
        **Downconverter** or **Upconverter**, and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_CONVERTER_FREQUENCY_CONTEXT` attribute to **IF**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **LSB**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | LSB (0)      | When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is     |
        |              | treated as the RF (signal) frequency while the higher is treated as the image frequency.                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | USB (1)      | When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is     |
        |              | treated as the image frequency while the higher is treated as the RF (signal) frequency.                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFFrequencyConverterSideband):
                Specifies the sideband when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE` attribute to either
                **Downconverter** or **Upconverter**, and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_CONVERTER_FREQUENCY_CONTEXT` attribute to **IF**.

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
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_SIDEBAND.value,
            )
            attr_val = enums.NFFrequencyConverterSideband(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_converter_sideband(self, selector_string, value):
        r"""Sets the sideband when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE` attribute to either
        **Downconverter** or **Upconverter**, and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_CONVERTER_FREQUENCY_CONTEXT` attribute to **IF**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **LSB**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | LSB (0)      | When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is     |
        |              | treated as the RF (signal) frequency while the higher is treated as the image frequency.                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | USB (1)      | When the frequency context is IF, out of the two possible input frequencies that gets translated to IF, the lower is     |
        |              | treated as the image frequency while the higher is treated as the RF (signal) frequency.                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFFrequencyConverterSideband, int):
                Specifies the sideband when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_TYPE` attribute to either
                **Downconverter** or **Upconverter**, and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_CONVERTER_FREQUENCY_CONTEXT` attribute to **IF**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFFrequencyConverterSideband else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_SIDEBAND.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_converter_image_rejection(self, selector_string):
        r"""Gets the gain ratio of the DUT at the image frequency to that at the RF frequency. This value is expressed in dB.
        Refer to NF concept help for more details.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 999.99 dB.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the gain ratio of the DUT at the image frequency to that at the RF frequency. This value is expressed in dB.
                Refer to NF concept help for more details.

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
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_IMAGE_REJECTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_converter_image_rejection(self, selector_string, value):
        r"""Sets the gain ratio of the DUT at the image frequency to that at the RF frequency. This value is expressed in dB.
        Refer to NF concept help for more details.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 999.99 dB.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the gain ratio of the DUT at the image frequency to that at the RF frequency. This value is expressed in dB.
                Refer to NF concept help for more details.

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
                attributes.AttributeID.NF_FREQUENCY_CONVERTER_IMAGE_REJECTION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_frequency_list(self, selector_string):
        r"""Gets the list of frequencies at which the noise figure (NF) of the DUT is computed. This value is expressed in Hz.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the list of frequencies at which the noise figure (NF) of the DUT is computed. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_FREQUENCY_LIST.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_frequency_list(self, selector_string, value):
        r"""Sets the list of frequencies at which the noise figure (NF) of the DUT is computed. This value is expressed in Hz.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the list of frequencies at which the noise figure (NF) of the DUT is computed. This value is expressed in Hz.

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
                updated_selector_string, attributes.AttributeID.NF_FREQUENCY_LIST.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_bandwidth(self, selector_string):
        r"""Gets the effective noise-bandwidth in which power measurements are performed for the noise figure (NF)
        measurement. This value is expressed in Hz.

        The default value is 100 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the effective noise-bandwidth in which power measurements are performed for the noise figure (NF)
                measurement. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_bandwidth(self, selector_string, value):
        r"""Sets the effective noise-bandwidth in which power measurements are performed for the noise figure (NF)
        measurement. This value is expressed in Hz.

        The default value is 100 kHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the effective noise-bandwidth in which power measurements are performed for the noise figure (NF)
                measurement. This value is expressed in Hz.

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
                attributes.AttributeID.NF_MEASUREMENT_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_interval(self, selector_string):
        r"""Gets the duration for which the signals are acquired at each frequency which you specify in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 ms.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the duration for which the signals are acquired at each frequency which you specify in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_interval(self, selector_string, value):
        r"""Sets the duration for which the signals are acquired at each frequency which you specify in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1 ms.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the duration for which the signals are acquired at each frequency which you specify in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in seconds.

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
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_INTERVAL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the noise figure (NF) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The NF measurement uses the value of the NF Averaging Count attribute as the number of acquisitions for each frequency   |
        |              | which you specify in the NF Freq List attribute, over which the NF measurement is averaged.                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFAveragingEnabled):
                Specifies whether to enable averaging for the noise figure (NF) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_AVERAGING_ENABLED.value
            )
            attr_val = enums.NFAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the noise figure (NF) measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The NF measurement uses the value of the NF Averaging Count attribute as the number of acquisitions for each frequency   |
        |              | which you specify in the NF Freq List attribute, over which the NF measurement is averaged.                              |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFAveragingEnabled, int):
                Specifies whether to enable averaging for the noise figure (NF) measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.NF_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.NF_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_calibration_setup_id(self, selector_string):
        r"""Associates a unique string identifier with the hardware setup used to perform calibration for the NF measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty string.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Associates a unique string identifier with the hardware setup used to perform calibration for the NF measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_string(
                updated_selector_string, attributes.AttributeID.NF_CALIBRATION_SETUP_ID.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_calibration_setup_id(self, selector_string, value):
        r"""Associates a unique string identifier with the hardware setup used to perform calibration for the NF measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty string.

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Associates a unique string identifier with the hardware setup used to perform calibration for the NF measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(
                updated_selector_string, attributes.AttributeID.NF_CALIBRATION_SETUP_ID.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_external_preamp_present(self, selector_string):
        r"""Gets if an external preamplifier is present in the signal path.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+------------------------------------------------------+
        | Name (Value) | Description                                          |
        +==============+======================================================+
        | False (0)    | No external preamplifier present in the signal path. |
        +--------------+------------------------------------------------------+
        | True (1)     | An external preamplifier present in the signal path. |
        +--------------+------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFExternalPreampPresent):
                Specifies if an external preamplifier is present in the signal path.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_EXTERNAL_PREAMP_PRESENT.value
            )
            attr_val = enums.NFExternalPreampPresent(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_external_preamp_present(self, selector_string, value):
        r"""Sets if an external preamplifier is present in the signal path.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+------------------------------------------------------+
        | Name (Value) | Description                                          |
        +==============+======================================================+
        | False (0)    | No external preamplifier present in the signal path. |
        +--------------+------------------------------------------------------+
        | True (1)     | An external preamplifier present in the signal path. |
        +--------------+------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFExternalPreampPresent, int):
                Specifies if an external preamplifier is present in the signal path.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFExternalPreampPresent else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_EXTERNAL_PREAMP_PRESENT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_external_preamp_frequency(self, selector_string):
        r"""Gets the array of frequencies corresponding to the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_GAIN` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_GAIN` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_EXTERNAL_PREAMP_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_external_preamp_frequency(self, selector_string, value):
        r"""Sets the array of frequencies corresponding to the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_GAIN` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_GAIN` attribute.

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
                attributes.AttributeID.NF_EXTERNAL_PREAMP_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_external_preamp_gain(self, selector_string):
        r"""Gets the gain of the external preamp as a function of frequency. The value is expressed in dB.

        Specify the frequencies at which gain values were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_FREQUENCY` attribute.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the gain of the external preamp as a function of frequency. The value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_EXTERNAL_PREAMP_GAIN.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_external_preamp_gain(self, selector_string, value):
        r"""Sets the gain of the external preamp as a function of frequency. The value is expressed in dB.

        Specify the frequencies at which gain values were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.EXTERNAL_PREAMP_FREQUENCY` attribute.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the gain of the external preamp as a function of frequency. The value is expressed in dB.

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
                updated_selector_string, attributes.AttributeID.NF_EXTERNAL_PREAMP_GAIN.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_input_loss_compensation_enabled(self, selector_string):
        r"""Gets whether the noise figure (NF) measurement accounts for ohmic losses between the noise source and the input
        port of the DUT, excluding the losses that are common to calibration and the measurement steps for the Y-Factor method,
        which are specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------+
        | Name (Value) | Description                                       |
        +==============+===================================================+
        | False (0)    | The NF measurement ignores the ohmic losses.      |
        +--------------+---------------------------------------------------+
        | True (1)     | The NF measurement accounts for the ohmic losses. |
        +--------------+---------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFDutInputLossCompensationEnabled):
                Specifies whether the noise figure (NF) measurement accounts for ohmic losses between the noise source and the input
                port of the DUT, excluding the losses that are common to calibration and the measurement steps for the Y-Factor method,
                which are specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

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
                attributes.AttributeID.NF_DUT_INPUT_LOSS_COMPENSATION_ENABLED.value,
            )
            attr_val = enums.NFDutInputLossCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_input_loss_compensation_enabled(self, selector_string, value):
        r"""Sets whether the noise figure (NF) measurement accounts for ohmic losses between the noise source and the input
        port of the DUT, excluding the losses that are common to calibration and the measurement steps for the Y-Factor method,
        which are specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------+
        | Name (Value) | Description                                       |
        +==============+===================================================+
        | False (0)    | The NF measurement ignores the ohmic losses.      |
        +--------------+---------------------------------------------------+
        | True (1)     | The NF measurement accounts for the ohmic losses. |
        +--------------+---------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFDutInputLossCompensationEnabled, int):
                Specifies whether the noise figure (NF) measurement accounts for ohmic losses between the noise source and the input
                port of the DUT, excluding the losses that are common to calibration and the measurement steps for the Y-Factor method,
                which are specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFDutInputLossCompensationEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_DUT_INPUT_LOSS_COMPENSATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_input_loss_frequency(self, selector_string):
        r"""Gets an array of frequencies corresponding to the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_DUT_INPUT_LOSS_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_input_loss_frequency(self, selector_string, value):
        r"""Sets an array of frequencies corresponding to the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in Hz.

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
                attributes.AttributeID.NF_DUT_INPUT_LOSS_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_input_loss(self, selector_string):
        r"""Gets an array of the ohmic losses between the noise source and the input port of the DUT, as a function of the
        frequency. This value is expressed in dB. This loss is accounted for by the NF measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_COMPENSATION_ENABLED` attribute to **True**. You must
        exclude any loss which is inherent to the noise source and is common between the calibration and measurement steps, and
        configure the loss using the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        Specify the frequencies at which the losses were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the ohmic losses between the noise source and the input port of the DUT, as a function of the
                frequency. This value is expressed in dB. This loss is accounted for by the NF measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_COMPENSATION_ENABLED` attribute to **True**. You must
                exclude any loss which is inherent to the noise source and is common between the calibration and measurement steps, and
                configure the loss using the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_DUT_INPUT_LOSS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_input_loss(self, selector_string, value):
        r"""Sets an array of the ohmic losses between the noise source and the input port of the DUT, as a function of the
        frequency. This value is expressed in dB. This loss is accounted for by the NF measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_COMPENSATION_ENABLED` attribute to **True**. You must
        exclude any loss which is inherent to the noise source and is common between the calibration and measurement steps, and
        configure the loss using the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        Specify the frequencies at which the losses were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the ohmic losses between the noise source and the input port of the DUT, as a function of the
                frequency. This value is expressed in dB. This loss is accounted for by the NF measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS_COMPENSATION_ENABLED` attribute to **True**. You must
                exclude any loss which is inherent to the noise source and is common between the calibration and measurement steps, and
                configure the loss using the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

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
                updated_selector_string, attributes.AttributeID.NF_DUT_INPUT_LOSS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_input_loss_temperature(self, selector_string):
        r"""Gets the physical temperature of the ohmic loss elements considered in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the physical temperature of the ohmic loss elements considered in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in kelvin.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.NF_DUT_INPUT_LOSS_TEMPERATURE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_input_loss_temperature(self, selector_string, value):
        r"""Sets the physical temperature of the ohmic loss elements considered in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the physical temperature of the ohmic loss elements considered in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_INPUT_LOSS` attribute. This value is expressed in kelvin.

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
                attributes.AttributeID.NF_DUT_INPUT_LOSS_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_output_loss_compensation_enabled(self, selector_string):
        r"""Gets whether the noise figure (NF) measurement accounts for ohmic losses between the output port of the DUT and
        the input port of the analyzer.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------+
        | Name (Value) | Description                                       |
        +==============+===================================================+
        | False (0)    | The NF measurement ignores ohmic losses.          |
        +--------------+---------------------------------------------------+
        | True (1)     | The NF measurement accounts for the ohmic losses. |
        +--------------+---------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFDutOutputLossCompensationEnabled):
                Specifies whether the noise figure (NF) measurement accounts for ohmic losses between the output port of the DUT and
                the input port of the analyzer.

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
                attributes.AttributeID.NF_DUT_OUTPUT_LOSS_COMPENSATION_ENABLED.value,
            )
            attr_val = enums.NFDutOutputLossCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_output_loss_compensation_enabled(self, selector_string, value):
        r"""Sets whether the noise figure (NF) measurement accounts for ohmic losses between the output port of the DUT and
        the input port of the analyzer.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------+
        | Name (Value) | Description                                       |
        +==============+===================================================+
        | False (0)    | The NF measurement ignores ohmic losses.          |
        +--------------+---------------------------------------------------+
        | True (1)     | The NF measurement accounts for the ohmic losses. |
        +--------------+---------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFDutOutputLossCompensationEnabled, int):
                Specifies whether the noise figure (NF) measurement accounts for ohmic losses between the output port of the DUT and
                the input port of the analyzer.

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
                value.value if type(value) is enums.NFDutOutputLossCompensationEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_DUT_OUTPUT_LOSS_COMPENSATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_output_loss_frequency(self, selector_string):
        r"""Gets the array of frequencies corresponding to the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS`  attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS`  attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_DUT_OUTPUT_LOSS_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_output_loss_frequency(self, selector_string, value):
        r"""Sets the array of frequencies corresponding to the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS`  attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS`  attribute. This value is expressed in Hz.

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
                attributes.AttributeID.NF_DUT_OUTPUT_LOSS_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_output_loss(self, selector_string):
        r"""Gets the array of ohmic losses between the output port of the DUT and the input port of the analyzer, as a
        function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_COMPENSATION_ENABLED` attribute to
        **True**.

        Specify the array of frequencies at which the losses were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the array of ohmic losses between the output port of the DUT and the input port of the analyzer, as a
                function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_COMPENSATION_ENABLED` attribute to
                **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_DUT_OUTPUT_LOSS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_output_loss(self, selector_string, value):
        r"""Sets the array of ohmic losses between the output port of the DUT and the input port of the analyzer, as a
        function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_COMPENSATION_ENABLED` attribute to
        **True**.

        Specify the array of frequencies at which the losses were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the array of ohmic losses between the output port of the DUT and the input port of the analyzer, as a
                function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS_COMPENSATION_ENABLED` attribute to
                **True**.

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
                updated_selector_string, attributes.AttributeID.NF_DUT_OUTPUT_LOSS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_dut_output_loss_temperature(self, selector_string):
        r"""Gets the physical temperature of the ohmic loss elements specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.NF_DUT_OUTPUT_LOSS_TEMPERATURE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_dut_output_loss_temperature(self, selector_string, value):
        r"""Sets the physical temperature of the ohmic loss elements specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin.

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
                attributes.AttributeID.NF_DUT_OUTPUT_LOSS_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_calibration_loss_compensation_enabled(self, selector_string):
        r"""Gets whether the noise figure (NF) measurement accounts for the ohmic losses between the noise source and input
        port of the analyzer during the calibration step, excluding any losses which you have specified using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------+
        | Name (Value) | Description                                       |
        +==============+===================================================+
        | False (0)    | The NF measurement ignores the ohmic losses.      |
        +--------------+---------------------------------------------------+
        | True (1)     | The NF measurement accounts for the ohmic losses. |
        +--------------+---------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFCalibrationLossCompensationEnabled):
                Specifies whether the noise figure (NF) measurement accounts for the ohmic losses between the noise source and input
                port of the analyzer during the calibration step, excluding any losses which you have specified using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

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
                attributes.AttributeID.NF_CALIBRATION_LOSS_COMPENSATION_ENABLED.value,
            )
            attr_val = enums.NFCalibrationLossCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_calibration_loss_compensation_enabled(self, selector_string, value):
        r"""Sets whether the noise figure (NF) measurement accounts for the ohmic losses between the noise source and input
        port of the analyzer during the calibration step, excluding any losses which you have specified using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------+
        | Name (Value) | Description                                       |
        +==============+===================================================+
        | False (0)    | The NF measurement ignores the ohmic losses.      |
        +--------------+---------------------------------------------------+
        | True (1)     | The NF measurement accounts for the ohmic losses. |
        +--------------+---------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFCalibrationLossCompensationEnabled, int):
                Specifies whether the noise figure (NF) measurement accounts for the ohmic losses between the noise source and input
                port of the analyzer during the calibration step, excluding any losses which you have specified using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

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
                value.value if type(value) is enums.NFCalibrationLossCompensationEnabled else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_CALIBRATION_LOSS_COMPENSATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_calibration_loss_frequency(self, selector_string):
        r"""Gets an array of frequencies corresponding to the ohmic losses between the source and the input port of the
        analyzer. This value is expressed in Hz. This attribute is applicable only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_MODE` attribute to **Calibrate** and set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**, or when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_MODE` attribute to **Calibrate** and set the NF Meas Method
        attribute to **Cold Source**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of frequencies corresponding to the ohmic losses between the source and the input port of the
                analyzer. This value is expressed in Hz. This attribute is applicable only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_MODE` attribute to **Calibrate** and set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**, or when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_MODE` attribute to **Calibrate** and set the NF Meas Method
                attribute to **Cold Source**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_CALIBRATION_LOSS_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_calibration_loss_frequency(self, selector_string, value):
        r"""Sets an array of frequencies corresponding to the ohmic losses between the source and the input port of the
        analyzer. This value is expressed in Hz. This attribute is applicable only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_MODE` attribute to **Calibrate** and set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**, or when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_MODE` attribute to **Calibrate** and set the NF Meas Method
        attribute to **Cold Source**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of frequencies corresponding to the ohmic losses between the source and the input port of the
                analyzer. This value is expressed in Hz. This attribute is applicable only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_MODE` attribute to **Calibrate** and set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**, or when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_MODE` attribute to **Calibrate** and set the NF Meas Method
                attribute to **Cold Source**.

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
                attributes.AttributeID.NF_CALIBRATION_LOSS_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_calibration_loss(self, selector_string):
        r"""Gets the array of ohmic losses between the noise source and input port of the analyzer during calibration, as a
        function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_COMPENSATION_ENABLED` attribute to
        **True**. You must exclude any loss specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        This attribute specifies the frequencies at which the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_FREQUENCY` attribute measures the losses.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the array of ohmic losses between the noise source and input port of the analyzer during calibration, as a
                function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_COMPENSATION_ENABLED` attribute to
                **True**. You must exclude any loss specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_CALIBRATION_LOSS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_calibration_loss(self, selector_string, value):
        r"""Sets the array of ohmic losses between the noise source and input port of the analyzer during calibration, as a
        function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
        when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_COMPENSATION_ENABLED` attribute to
        **True**. You must exclude any loss specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

        This attribute specifies the frequencies at which the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_FREQUENCY` attribute measures the losses.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the array of ohmic losses between the noise source and input port of the analyzer during calibration, as a
                function of frequency. This value is expressed in dB. This loss is accounted for by the noise figure (NF) measurement
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS_COMPENSATION_ENABLED` attribute to
                **True**. You must exclude any loss specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.

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
                updated_selector_string, attributes.AttributeID.NF_CALIBRATION_LOSS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_calibration_loss_temperature(self, selector_string):
        r"""Gets the physical temperature of the ohmic loss elements specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.

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
                attributes.AttributeID.NF_CALIBRATION_LOSS_TEMPERATURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_calibration_loss_temperature(self, selector_string, value):
        r"""Sets the physical temperature of the ohmic loss elements specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.

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
                attributes.AttributeID.NF_CALIBRATION_LOSS_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_method(self, selector_string):
        r"""Gets the measurement method used to perform the noise figure (NF) measurement. Refer to the NF concept topic for
        more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Y-Factor**.

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                                              |
        +=================+==========================================================================================================================+
        | Y-Factor (0)    | The NF measurement computes the noise figure of the DUT using a noise source with a calibrated excess-noise ratio        |
        |                 | (ENR).                                                                                                                   |
        |                 | Refer to the NF Y-Factor NS Type attribute for information about supported devices and their corresponding noise source  |
        |                 | type.                                                                                                                    |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Cold Source (1) | The NF measurement computes the noise figure of the DUT using a 50 ohm microwave termination as the noise source.        |
        |                 | Supported Devices: PXIe-5644/5645/5646/5840/5841/5842/5860, PXIe-5830/5831/5832                                          |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFMeasurementMethod):
                Specifies the measurement method used to perform the noise figure (NF) measurement. Refer to the NF concept topic for
                more information.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_METHOD.value
            )
            attr_val = enums.NFMeasurementMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_method(self, selector_string, value):
        r"""Sets the measurement method used to perform the noise figure (NF) measurement. Refer to the NF concept topic for
        more information.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Y-Factor**.

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                                              |
        +=================+==========================================================================================================================+
        | Y-Factor (0)    | The NF measurement computes the noise figure of the DUT using a noise source with a calibrated excess-noise ratio        |
        |                 | (ENR).                                                                                                                   |
        |                 | Refer to the NF Y-Factor NS Type attribute for information about supported devices and their corresponding noise source  |
        |                 | type.                                                                                                                    |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Cold Source (1) | The NF measurement computes the noise figure of the DUT using a 50 ohm microwave termination as the noise source.        |
        |                 | Supported Devices: PXIe-5644/5645/5646/5840/5841/5842/5860, PXIe-5830/5831/5832                                          |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFMeasurementMethod, int):
                Specifies the measurement method used to perform the noise figure (NF) measurement. Refer to the NF concept topic for
                more information.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFMeasurementMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_MEASUREMENT_METHOD.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_mode(self, selector_string):
        r"""Gets whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
        characteristics of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        attribute to **Y-Factor**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Measure (0)   | The noise figure (NF) measurement computes the noise characteristics of the DUT, compensating for the noise figure of    |
        |               | the analyzer.                                                                                                            |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                                   |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFYFactorMode):
                Specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
                characteristics of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_Y_FACTOR_MODE.value
            )
            attr_val = enums.NFYFactorMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_mode(self, selector_string, value):
        r"""Sets whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
        characteristics of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
        attribute to **Y-Factor**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Measure (0)   | The noise figure (NF) measurement computes the noise characteristics of the DUT, compensating for the noise figure of    |
        |               | the analyzer.                                                                                                            |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                                   |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFYFactorMode, int):
                Specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
                characteristics of the DUT when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD`
                attribute to **Y-Factor**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFYFactorMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_Y_FACTOR_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_type(self, selector_string):
        r"""Gets the noise source type for performing the noise figure (NF) measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **External Noise Source**.

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | External Noise Source (0) | The NF measurement generates noise using an external noise source, that is controlled either by an internal noise        |
        |                           | source power supply or an NI Source Measure Unit (SMU).                                                                  |
        |                           | Supported Devices: PXIe-5665 (3.6 GHz), PXIe-5668, PXIe-5644/5645/5646*, PXIe-5840*/5841*/5842*/5860*, PXIe              |
        |                           | 5830/5831*/5832*                                                                                                         |
        |                           | *Use an external NI Source Measure Unit (SMU) as the noise source power supply for the Noise Figure measurement.         |
        |                           | During initialization, specify the SMU resource name using "NoiseSourcePowerSupply" as the specifier within the          |
        |                           | RFmxSetup string. For example, "RFmxSetup= NoiseSourcePowerSupply:myDCPower[0]" configures RFmx to use channel 0 on      |
        |                           | myDCPower SMU device for powering the noise source. You should allocate a dedicated SMU channel for RFmx.                |
        |                           | RFmx supports PXIe-4138, PXIe-4139, and PXIe-4139 (40 W) SMUs.                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RF Signal Generator (1)   | When you measure Y-Factor based NF using a supported NI vector signal transceiver (VST) instrument, RFmx generates       |
        |                           | noise using the vector signal generator (VSG) integrated into the same VST.                                              |
        |                           | RFmx automatically configures the vector signal generator (VSG) to generate noise at the specified bandwidth and ENR     |
        |                           | levels that you set using the NF Y-Factor NS ENR Freq and NF Y-Factor NS ENR attributes.                                 |
        |                           | Supported Devices: PXIe-5842/5860                                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFYFactorNoiseSourceType):
                Specifies the noise source type for performing the noise figure (NF) measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_TYPE.value
            )
            attr_val = enums.NFYFactorNoiseSourceType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_type(self, selector_string, value):
        r"""Sets the noise source type for performing the noise figure (NF) measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **External Noise Source**.

        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)              | Description                                                                                                              |
        +===========================+==========================================================================================================================+
        | External Noise Source (0) | The NF measurement generates noise using an external noise source, that is controlled either by an internal noise        |
        |                           | source power supply or an NI Source Measure Unit (SMU).                                                                  |
        |                           | Supported Devices: PXIe-5665 (3.6 GHz), PXIe-5668, PXIe-5644/5645/5646*, PXIe-5840*/5841*/5842*/5860*, PXIe              |
        |                           | 5830/5831*/5832*                                                                                                         |
        |                           | *Use an external NI Source Measure Unit (SMU) as the noise source power supply for the Noise Figure measurement.         |
        |                           | During initialization, specify the SMU resource name using "NoiseSourcePowerSupply" as the specifier within the          |
        |                           | RFmxSetup string. For example, "RFmxSetup= NoiseSourcePowerSupply:myDCPower[0]" configures RFmx to use channel 0 on      |
        |                           | myDCPower SMU device for powering the noise source. You should allocate a dedicated SMU channel for RFmx.                |
        |                           | RFmx supports PXIe-4138, PXIe-4139, and PXIe-4139 (40 W) SMUs.                                                           |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | RF Signal Generator (1)   | When you measure Y-Factor based NF using a supported NI vector signal transceiver (VST) instrument, RFmx generates       |
        |                           | noise using the vector signal generator (VSG) integrated into the same VST.                                              |
        |                           | RFmx automatically configures the vector signal generator (VSG) to generate noise at the specified bandwidth and ENR     |
        |                           | levels that you set using the NF Y-Factor NS ENR Freq and NF Y-Factor NS ENR attributes.                                 |
        |                           | Supported Devices: PXIe-5842/5860                                                                                        |
        +---------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFYFactorNoiseSourceType, int):
                Specifies the noise source type for performing the noise figure (NF) measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFYFactorNoiseSourceType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_rf_signal_generator_port(self, selector_string):
        r"""Gets the vector signal generator port to be configured to generate a noise signal when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **RF Signal Generator**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is "" (empty string).

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the vector signal generator port to be configured to generate a noise signal when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **RF Signal Generator**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_string(
                updated_selector_string,
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_RF_SIGNAL_GENERATOR_PORT.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_rf_signal_generator_port(self, selector_string, value):
        r"""Sets the vector signal generator port to be configured to generate a noise signal when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **RF Signal Generator**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is "" (empty string).

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the vector signal generator port to be configured to generate a noise signal when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **RF Signal Generator**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(
                updated_selector_string,
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_RF_SIGNAL_GENERATOR_PORT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_enr_frequency(self, selector_string):
        r"""Gets an array of frequencies corresponding to the effective noise ratio (ENR) values specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR` attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of frequencies corresponding to the effective noise ratio (ENR) values specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR` attribute. This value is expressed in Hz.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_enr_frequency(self, selector_string, value):
        r"""Sets an array of frequencies corresponding to the effective noise ratio (ENR) values specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR` attribute. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of frequencies corresponding to the effective noise ratio (ENR) values specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR` attribute. This value is expressed in Hz.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_enr(self, selector_string):
        r"""Gets the array of effective noise ratio (ENR) values of the noise source as a function of the frequency. This
        value is expressed in dB. The corresponding frequencies are specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY` attribute. This attribute is used
        only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the array of effective noise ratio (ENR) values of the noise source as a function of the frequency. This
                value is expressed in dB. The corresponding frequencies are specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY` attribute. This attribute is used
                only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_ENR.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_enr(self, selector_string, value):
        r"""Sets the array of effective noise ratio (ENR) values of the noise source as a function of the frequency. This
        value is expressed in dB. The corresponding frequencies are specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY` attribute. This attribute is used
        only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the array of effective noise ratio (ENR) values of the noise source as a function of the frequency. This
                value is expressed in dB. The corresponding frequencies are specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_ENR_FREQUENCY` attribute. This attribute is used
                only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_ENR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_cold_temperature(self, selector_string):
        r"""Gets the calibrated cold noise temperature of the noise source used in the Y-Factor method. This value is
        expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 302.8.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the calibrated cold noise temperature of the noise source used in the Y-Factor method. This value is
                expressed in kelvin.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_COLD_TEMPERATURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_cold_temperature(self, selector_string, value):
        r"""Sets the calibrated cold noise temperature of the noise source used in the Y-Factor method. This value is
        expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 302.8.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the calibrated cold noise temperature of the noise source used in the Y-Factor method. This value is
                expressed in kelvin.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_COLD_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_off_temperature(self, selector_string):
        r"""Gets the physical temperature of the noise source used in the Y-Factor method when the noise source is turned off.
        This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the physical temperature of the noise source used in the Y-Factor method when the noise source is turned off.
                This value is expressed in kelvin.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_OFF_TEMPERATURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_off_temperature(self, selector_string, value):
        r"""Sets the physical temperature of the noise source used in the Y-Factor method when the noise source is turned off.
        This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the physical temperature of the noise source used in the Y-Factor method when the noise source is turned off.
                This value is expressed in kelvin.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_OFF_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_settling_time(self, selector_string):
        r"""Gets the time to wait till the noise source used in the Y-Factor method settles to either hot or cold state when
        the noise source is turned on or off. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **External Noise Source**. This
        value is expressed in seconds.

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
                Specifies the time to wait till the noise source used in the Y-Factor method settles to either hot or cold state when
                the noise source is turned on or off. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **External Noise Source**. This
                value is expressed in seconds.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_SETTLING_TIME.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_settling_time(self, selector_string, value):
        r"""Sets the time to wait till the noise source used in the Y-Factor method settles to either hot or cold state when
        the noise source is turned on or off. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **External Noise Source**. This
        value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the time to wait till the noise source used in the Y-Factor method settles to either hot or cold state when
                the noise source is turned on or off. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **External Noise Source**. This
                value is expressed in seconds.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_SETTLING_TIME.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_loss_compensation_enabled(self, selector_string):
        r"""Gets whether the noise figure (NF) measurement should account for ohmic losses inherent to the noise source used
        in the Y-Factor method common to the calibration and measurement steps.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+-------------------------------------------------------+
        | Name (Value) | Description                                           |
        +==============+=======================================================+
        | False (0)    | Ohmic losses are ignored.                             |
        +--------------+-------------------------------------------------------+
        | True (1)     | Ohmic losses are accounted for in the NF measurement. |
        +--------------+-------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFYFactorNoiseSourceLossCompensationEnabled):
                Specifies whether the noise figure (NF) measurement should account for ohmic losses inherent to the noise source used
                in the Y-Factor method common to the calibration and measurement steps.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED.value,
            )
            attr_val = enums.NFYFactorNoiseSourceLossCompensationEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_loss_compensation_enabled(self, selector_string, value):
        r"""Sets whether the noise figure (NF) measurement should account for ohmic losses inherent to the noise source used
        in the Y-Factor method common to the calibration and measurement steps.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+-------------------------------------------------------+
        | Name (Value) | Description                                           |
        +==============+=======================================================+
        | False (0)    | Ohmic losses are ignored.                             |
        +--------------+-------------------------------------------------------+
        | True (1)     | Ohmic losses are accounted for in the NF measurement. |
        +--------------+-------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFYFactorNoiseSourceLossCompensationEnabled, int):
                Specifies whether the noise figure (NF) measurement should account for ohmic losses inherent to the noise source used
                in the Y-Factor method common to the calibration and measurement steps.

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
                if type(value) is enums.NFYFactorNoiseSourceLossCompensationEnabled
                else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_loss_frequency(self, selector_string):
        r"""Gets the frequencies corresponding to the ohmic loss inherent to the noise source used in the Y-Factor method
        specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the frequencies corresponding to the ohmic loss inherent to the noise source used in the Y-Factor method
                specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is
                expressed in Hz.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_loss_frequency(self, selector_string, value):
        r"""Sets the frequencies corresponding to the ohmic loss inherent to the noise source used in the Y-Factor method
        specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is
        expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the frequencies corresponding to the ohmic loss inherent to the noise source used in the Y-Factor method
                specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is
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
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_loss(self, selector_string):
        r"""Gets an array of the ohmic losses inherent to the noise source used in the Y-Factor method. This value is
        expressed in dB. This loss is accounted for by the NF measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED` attribute to **True**.

        You must specify the frequencies at which the losses were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the ohmic losses inherent to the noise source used in the Y-Factor method. This value is
                expressed in dB. This loss is accounted for by the NF measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_loss(self, selector_string, value):
        r"""Sets an array of the ohmic losses inherent to the noise source used in the Y-Factor method. This value is
        expressed in dB. This loss is accounted for by the NF measurement when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED` attribute to **True**.

        You must specify the frequencies at which the losses were measured using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the ohmic losses inherent to the noise source used in the Y-Factor method. This value is
                expressed in dB. This loss is accounted for by the NF measurement when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS_COMPENSATION_ENABLED` attribute to **True**.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_y_factor_noise_source_loss_temperature(self, selector_string):
        r"""Gets the physical temperature of the ohmic loss elements specified in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is expressed in
        kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the physical temperature of the ohmic loss elements specified in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is expressed in
                kelvin.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS_TEMPERATURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_y_factor_noise_source_loss_temperature(self, selector_string, value):
        r"""Sets the physical temperature of the ohmic loss elements specified in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is expressed in
        kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the physical temperature of the ohmic loss elements specified in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This value is expressed in
                kelvin.

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
                attributes.AttributeID.NF_Y_FACTOR_NOISE_SOURCE_LOSS_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_mode(self, selector_string):
        r"""Gets whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
        characteristics of the DUT for the cold source method.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Measure (0)   | The noise figure (NF) measurement computes the noise characteristics of the DUT and compensates for the noise figure of  |
        |               | the analyzer.                                                                                                            |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                                   |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.NFColdSourceMode):
                Specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
                characteristics of the DUT for the cold source method.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_MODE.value
            )
            attr_val = enums.NFColdSourceMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_mode(self, selector_string, value):
        r"""Sets whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
        characteristics of the DUT for the cold source method.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measure**.

        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)  | Description                                                                                                              |
        +===============+==========================================================================================================================+
        | Measure (0)   | The noise figure (NF) measurement computes the noise characteristics of the DUT and compensates for the noise figure of  |
        |               | the analyzer.                                                                                                            |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+
        | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                                   |
        +---------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.NFColdSourceMode, int):
                Specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute the noise
                characteristics of the DUT for the cold source method.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.NFColdSourceMode else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_MODE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_input_termination_vswr(self, selector_string):
        r"""Gets an array of voltage standing wave ratios (VSWR) as a function of frequency of the microwave termination used
        as the noise source in cold source method. The corresponding array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY` attribute.

        In most cases, the exact VSWR of the microwave termination may not be known. Hence, NI recommends that you set
        this attribute to an empty array, in which case the noise figure (NF) measurement assumes that the VSWR of the
        microwave termination is unity for all frequencies.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of voltage standing wave ratios (VSWR) as a function of frequency of the microwave termination used
                as the noise source in cold source method. The corresponding array of frequencies is specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY` attribute.

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
                attributes.AttributeID.NF_COLD_SOURCE_INPUT_TERMINATION_VSWR.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_input_termination_vswr(self, selector_string, value):
        r"""Sets an array of voltage standing wave ratios (VSWR) as a function of frequency of the microwave termination used
        as the noise source in cold source method. The corresponding array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY` attribute.

        In most cases, the exact VSWR of the microwave termination may not be known. Hence, NI recommends that you set
        this attribute to an empty array, in which case the noise figure (NF) measurement assumes that the VSWR of the
        microwave termination is unity for all frequencies.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of voltage standing wave ratios (VSWR) as a function of frequency of the microwave termination used
                as the noise source in cold source method. The corresponding array of frequencies is specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY` attribute.

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
                attributes.AttributeID.NF_COLD_SOURCE_INPUT_TERMINATION_VSWR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_input_termination_vswr_frequency(self, selector_string):
        r"""Gets an array of  frequencies corresponding to the voltage standing wave ratios (VSWR) of the microwave
        termination used in the cold source method as specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR` attribute. This value is expressed
        in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of  frequencies corresponding to the voltage standing wave ratios (VSWR) of the microwave
                termination used in the cold source method as specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR` attribute. This value is expressed
                in Hz.

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
                attributes.AttributeID.NF_COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_input_termination_vswr_frequency(self, selector_string, value):
        r"""Sets an array of  frequencies corresponding to the voltage standing wave ratios (VSWR) of the microwave
        termination used in the cold source method as specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR` attribute. This value is expressed
        in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of  frequencies corresponding to the voltage standing wave ratios (VSWR) of the microwave
                termination used in the cold source method as specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_INPUT_TERMINATION_VSWR` attribute. This value is expressed
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
            error_code = self._interpreter.set_attribute_f64_array(
                updated_selector_string,
                attributes.AttributeID.NF_COLD_SOURCE_INPUT_TERMINATION_VSWR_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_input_termination_temperature(self, selector_string):
        r"""Gets the physical temperature of the microwave termination used as the noise source in the cold source method.
        This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the physical temperature of the microwave termination used as the noise source in the cold source method.
                This value is expressed in kelvin.

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
                attributes.AttributeID.NF_COLD_SOURCE_INPUT_TERMINATION_TEMPERATURE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_input_termination_temperature(self, selector_string, value):
        r"""Sets the physical temperature of the microwave termination used as the noise source in the cold source method.
        This value is expressed in kelvin.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 297.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the physical temperature of the microwave termination used as the noise source in the cold source method.
                This value is expressed in kelvin.

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
                attributes.AttributeID.NF_COLD_SOURCE_INPUT_TERMINATION_TEMPERATURE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_dut_s_parameters_frequency(self, selector_string):
        r"""Gets an array of frequencies corresponding to the s-parameters of the DUT specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S21`,
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S12`,
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S11`, and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S22` attributes. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of frequencies corresponding to the s-parameters of the DUT specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S21`,
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S12`,
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S11`, and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S22` attributes. This value is expressed in Hz.

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
                attributes.AttributeID.NF_COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_dut_s_parameters_frequency(self, selector_string, value):
        r"""Sets an array of frequencies corresponding to the s-parameters of the DUT specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S21`,
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S12`,
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S11`, and
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S22` attributes. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of frequencies corresponding to the s-parameters of the DUT specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S21`,
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S12`,
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S11`, and
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S22` attributes. This value is expressed in Hz.

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
                attributes.AttributeID.NF_COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_dut_s21(self, selector_string):
        r"""Gets an array of the gains of the DUT as a function of frequency, when the output port of the DUT is terminated
        with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding array of
        frequencies is specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY`
        attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the gains of the DUT as a function of frequency, when the output port of the DUT is terminated
                with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding array of
                frequencies is specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY`
                attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S21.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_dut_s21(self, selector_string, value):
        r"""Sets an array of the gains of the DUT as a function of frequency, when the output port of the DUT is terminated
        with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding array of
        frequencies is specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY`
        attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the gains of the DUT as a function of frequency, when the output port of the DUT is terminated
                with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding array of
                frequencies is specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY`
                attribute.

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
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S21.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_dut_s12(self, selector_string):
        r"""Gets an array of the input-isolations of the DUT as a function of frequency, when the input port of the DUT is
        terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
        array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the input-isolations of the DUT as a function of frequency, when the input port of the DUT is
                terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
                array of frequencies is specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S12.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_dut_s12(self, selector_string, value):
        r"""Sets an array of the input-isolations of the DUT as a function of frequency, when the input port of the DUT is
        terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
        array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the input-isolations of the DUT as a function of frequency, when the input port of the DUT is
                terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
                array of frequencies is specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

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
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S12.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_dut_s11(self, selector_string):
        r"""Gets an array of the input-reflections of the DUT as a function of frequency, when the output port of the DUT is
        terminated with an impedance equal to the characteristic impedance. This value is expressed in dB.

        The corresponding array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the input-reflections of the DUT as a function of frequency, when the output port of the DUT is
                terminated with an impedance equal to the characteristic impedance. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S11.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_dut_s11(self, selector_string, value):
        r"""Sets an array of the input-reflections of the DUT as a function of frequency, when the output port of the DUT is
        terminated with an impedance equal to the characteristic impedance. This value is expressed in dB.

        The corresponding array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the input-reflections of the DUT as a function of frequency, when the output port of the DUT is
                terminated with an impedance equal to the characteristic impedance. This value is expressed in dB.

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
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S11.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cold_source_dut_s22(self, selector_string):
        r"""Gets an array of the output-reflections of the DUT as a function of frequency, when the input port of the DUT is
        terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
        array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies an array of the output-reflections of the DUT as a function of frequency, when the input port of the DUT is
                terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
                array of frequencies is specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64_array(
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S22.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cold_source_dut_s22(self, selector_string, value):
        r"""Sets an array of the output-reflections of the DUT as a function of frequency, when the input port of the DUT is
        terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
        array of frequencies is specified by the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is an empty array.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies an array of the output-reflections of the DUT as a function of frequency, when the input port of the DUT is
                terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
                array of frequencies is specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_DUT_S_PARAMETERS_FREQUENCY` attribute.

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
                updated_selector_string, attributes.AttributeID.NF_COLD_SOURCE_DUT_S22.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_device_temperature_tolerance(self, selector_string):
        r"""Gets the tolerance for device temperature beyond which the calibration data is considered invalid. This value  is
        expressed in Celsius.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 5.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the tolerance for device temperature beyond which the calibration data is considered invalid. This value  is
                expressed in Celsius.

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
                attributes.AttributeID.NF_DEVICE_TEMPERATURE_TOLERANCE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_device_temperature_tolerance(self, selector_string, value):
        r"""Sets the tolerance for device temperature beyond which the calibration data is considered invalid. This value  is
        expressed in Celsius.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 5.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the tolerance for device temperature beyond which the calibration data is considered invalid. This value  is
                expressed in Celsius.

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
                attributes.AttributeID.NF_DEVICE_TEMPERATURE_TOLERANCE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for the noise figure (NF) measurement.

        The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
        be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum number of threads used for parallelism for the noise figure (NF) measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.NF_NUMBER_OF_ANALYSIS_THREADS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for the noise figure (NF) measurement.

        The number of threads can range from 1 to the number of physical cores. The number of threads you set may not
        be used in calculations. The actual number of threads used depends on the problem size, system resources, data
        availability, and other considerations.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of threads used for parallelism for the noise figure (NF) measurement.

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
                attributes.AttributeID.NF_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def clear_calibration_database(self, calibration_setup_id):
        r"""Clear the noise figure calibration data for Cold Source and Y-Factor method. Calibration data associated with the
        selected VSA is cleared for the Cold Source method while calibration data associated with the noise source name and the
        VSA is cleared for the Y-Factor method.

        Args:
            calibration_setup_id (string):
                This parameter associates a unique string identifier with the hardware setup used to perform calibration for the NF
                measurement. The default value is an empty string.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(calibration_setup_id, "calibration_setup_id")
            error_code = self._interpreter.nf_clear_calibration_database(calibration_setup_id)
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(self, selector_string, averaging_enabled, averaging_count):
        r"""Configures averaging for the noise figure (NF) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.NFAveragingEnabled, int):
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

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            averaging_enabled = (
                averaging_enabled.value
                if type(averaging_enabled) is enums.NFAveragingEnabled
                else averaging_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_calibration_loss(
        self,
        selector_string,
        calibration_loss_compensation_enabled,
        calibration_loss_frequency,
        calibration_loss,
        calibration_loss_temperature,
    ):
        r"""Configures the ohmic loss, as a function of frequency, of the loss elements between the noise source and the input port
        of the analyzer during the calibration step, excluding the loss specified as the noise source loss.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            calibration_loss_compensation_enabled (enums.NFCalibrationLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement accounts for the ohmic losses between the noise
                source and input port of the analyzer during the calibration step, excluding any losses which you have specified using
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. The default value is
                **False**.

                +--------------+---------------------------------------------------+
                | Name (Value) | Description                                       |
                +==============+===================================================+
                | False (0)    | The NF measurement ignores the ohmic losses.      |
                +--------------+---------------------------------------------------+
                | True (1)     | The NF measurement accounts for the ohmic losses. |
                +--------------+---------------------------------------------------+

            calibration_loss_frequency (float):
                This parameter specifies an array of frequencies corresponding to the ohmic losses between the source and the input
                port of the analyzer. This value is expressed in Hz. This parameter is applicable only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_MODE` attribute to **Calibrate** and set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**, or when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.COLD_SOURCE_MODE` attribute to **Calibrate** and set the NF Meas Method
                attribute to **Cold Source**. The default value is an empty array.

            calibration_loss (float):
                This parameter specifies the array of ohmic losses between the noise source and input port of the analyzer during
                calibration, as a function of frequency. You must exclude any loss specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute.  This loss is accounted for by
                the NF measurement when you set the **Calibration Loss Compensation Enabled** parameter to **True**. The default value
                is empty array.

                This parameter specifies the frequencies at which the **Calibration Loss Frequency** parameter measures the
                losses.

            calibration_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            calibration_loss_compensation_enabled = (
                calibration_loss_compensation_enabled.value
                if type(calibration_loss_compensation_enabled)
                is enums.NFCalibrationLossCompensationEnabled
                else calibration_loss_compensation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_calibration_loss(
                updated_selector_string,
                calibration_loss_compensation_enabled,
                calibration_loss_frequency,
                calibration_loss,
                calibration_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_cold_source_dut_s_parameters(
        self, selector_string, dut_s_parameters_frequency, dut_s21, dut_s12, dut_s11, dut_s22
    ):
        r"""Configures the scattering parameters of the DUT as a function of the frequency, for use in the cold source measurement
        method.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_s_parameters_frequency (float):
                This parameter specifies the array of frequencies corresponding to the s-parameters of the DUT specified by the  **DUT
                S21**, **DUT S12**, **DUT S11**, and **DUT S22** parameters. This value is expressed in Hz. The default value is an
                empty array.

            dut_s21 (float):
                This parameter specifies an array of the gains of the DUT as a function of frequency, when the output port of the DUT
                is terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The corresponding
                array of frequencies is specified by the **DUT S-Parameters Frequency** parameter.  The default value is an empty
                array.

            dut_s12 (float):
                This parameter specifies an array of the input-isolations of the DUT as a function of frequency, when the input port of
                the DUT is terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The
                corresponding array of frequencies is specified by the **DUT S-Parameters Frequency** parameter. The default value is
                an empty array.

            dut_s11 (float):
                This parameter specifies an array of the input-reflections of the DUT as a function of frequency, when the output port
                of the DUT is terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The
                corresponding array of frequencies is specified by the **DUT S-Parameters Frequency** parameter. The default value is
                an empty array.

            dut_s22 (float):
                This parameter specifies an array of the output-reflections of the DUT as a function of frequency, when the input port
                of the DUT is terminated with an impedance equal to the characteristic impedance. This value is expressed in dB. The
                corresponding array of frequencies is specified by the **DUT S-Parameters Frequency** parameter. The default value is
                an empty array.

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
            error_code = self._interpreter.nf_configure_cold_source_dut_s_parameters(
                updated_selector_string,
                dut_s_parameters_frequency,
                dut_s21,
                dut_s12,
                dut_s11,
                dut_s22,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_cold_source_input_termination(
        self, selector_string, termination_vswr, termination_vswr_frequency, termination_temperature
    ):
        r"""Configures the characteristics of the microwave termination used as a noise source in the cold source method.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            termination_vswr (float):
                This parameter specifies an array of voltage standing wave ratios (VSWR) as a function of frequency of the microwave
                termination used as the noise source in cold source method. The corresponding array of frequencies is specified by the
                **Termination VSWR Frequency** parameter.

                In most cases, the exact VSWR of the microwave termination may not be known. Hence, NI recommends that you set
                this parameter to an empty array, in which case the noise figure (NF) measurement assumes that the VSWR of the
                microwave termination is unity for all frequencies.

                The default value is an empty array.

            termination_vswr_frequency (float):
                This parameter specifies an array of  frequencies corresponding to the VSWRs of the microwave termination used in the
                cold source method as specified by the **Termination VSWR** parameter. This value is expressed in Hz. The default value
                is an empty array.

            termination_temperature (float):
                This parameter specifies the physical temperature of the microwave termination used as the noise source in the cold
                source method. This value is expressed in kelvin. The default value is 297.

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
            error_code = self._interpreter.nf_configure_cold_source_input_termination(
                updated_selector_string,
                termination_vswr,
                termination_vswr_frequency,
                termination_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_cold_source_mode(self, selector_string, cold_source_mode):
        r"""Configures the cold source based noise figure (NF) measurement to perform the calibration step or the measurement step.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            cold_source_mode (enums.NFColdSourceMode, int):
                This parameter specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute
                the noise characteristics of the DUT for the cold source method. The default value is **Measure**.

                +---------------+--------------------------------------------------------------------------------------------------------------------+
                | Name (Value)  | Description                                                                                                        |
                +===============+====================================================================================================================+
                | Measure (0)   | NF measurement computes the noise characteristics of the DUT and compensates for the noise figure of the analyzer. |
                +---------------+--------------------------------------------------------------------------------------------------------------------+
                | Calibrate (1) | NF measurement computes the noise characteristics of the analyzer.                                                 |
                +---------------+--------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            cold_source_mode = (
                cold_source_mode.value
                if type(cold_source_mode) is enums.NFColdSourceMode
                else cold_source_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_cold_source_mode(
                updated_selector_string, cold_source_mode
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_dut_input_loss(
        self,
        selector_string,
        dut_input_loss_compensation_enabled,
        dut_input_loss_frequency,
        dut_input_loss,
        dut_input_loss_temperature,
    ):
        r"""Configures the ohmic loss, as a function of frequency, of the loss elements between the noise source and the input port
        of the DUT, excluding the losses that are common to the calibration step and the measurement step.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_input_loss_compensation_enabled (enums.NFDutInputLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement accounts for ohmic losses between the noise source
                and the input port of the DUT, excluding the losses that are common to calibration and the measurement steps, which are
                specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. The default
                value is **False**.

                +--------------+---------------------------------------------------+
                | Name (Value) | Description                                       |
                +==============+===================================================+
                | False (0)    | The NF measurement ignores the ohmic losses.      |
                +--------------+---------------------------------------------------+
                | True (1)     | The NF measurement accounts for the ohmic losses. |
                +--------------+---------------------------------------------------+

            dut_input_loss_frequency (float):
                This parameter specifies the array of frequencies corresponding to the value of the **DUT Input Loss** parameter. This
                value is expressed in Hz.  The default value is an empty array.

            dut_input_loss (float):
                This parameter specifies the array of ohmic losses between the noise source and the input port of the DUT, as a
                function of the frequency. This value is expressed in dB. You must exclude any loss which is inherent to the noise
                source and is common between the calibration and measurement steps, and configure it using the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. This loss is accounted for by the
                NF measurement when you set the **DUT Input Loss Compensation Enabled** parameter to **True**. The default value is an
                empty array.

                Specify the frequencies at which the losses were measured using the **DUT Input Loss Frequency** parameter.

            dut_input_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements considered in the **DUT Input Loss**
                parameter. This value is expressed in kelvin. The default value is 297.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            dut_input_loss_compensation_enabled = (
                dut_input_loss_compensation_enabled.value
                if type(dut_input_loss_compensation_enabled)
                is enums.NFDutInputLossCompensationEnabled
                else dut_input_loss_compensation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_dut_input_loss(
                updated_selector_string,
                dut_input_loss_compensation_enabled,
                dut_input_loss_frequency,
                dut_input_loss,
                dut_input_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_dut_output_loss(
        self,
        selector_string,
        dut_output_loss_compensation_enabled,
        dut_output_loss_frequency,
        dut_output_loss,
        dut_output_loss_temperature,
    ):
        r"""Configures the ohmic loss, as a function of frequency, of the loss elements between the output port of the DUT and the
        input port of the analyzer.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_output_loss_compensation_enabled (enums.NFDutOutputLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement accounts for ohmic losses between the output port of
                the DUT and the input port of the analyzer. The default value is **False**.

                +--------------+------------------------------------------------+
                | Name (Value) | Description                                    |
                +==============+================================================+
                | False (0)    | The measurement ignores ohmic losses.          |
                +--------------+------------------------------------------------+
                | True (1)     | The measurement accounts for the ohmic losses. |
                +--------------+------------------------------------------------+

            dut_output_loss_frequency (float):
                This parameter specifies the array of frequencies corresponding to the value of the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS`  attribute. This value is expressed in Hz. The default
                value is an empty array.

            dut_output_loss (float):
                This parameter specifies the array of ohmic losses between the output port of the DUT and the input port of the
                analyzer, as a function of frequency. This value is expressed in dB. This loss is accounted for by the NF measurement
                when you set the **DUT Output Loss Compensation Enabled** parameter to **True**. The default value is an empty array.

                Specify the array of frequencies at which the losses were measured using the **DUT Output Loss Frequency**
                parameter.

            dut_output_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin. The
                default value is 297.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            dut_output_loss_compensation_enabled = (
                dut_output_loss_compensation_enabled.value
                if type(dut_output_loss_compensation_enabled)
                is enums.NFDutOutputLossCompensationEnabled
                else dut_output_loss_compensation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_dut_output_loss(
                updated_selector_string,
                dut_output_loss_compensation_enabled,
                dut_output_loss_frequency,
                dut_output_loss,
                dut_output_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency_list(self, selector_string, frequency_list):
        r"""Configures the list of frequencies at which to perform the noise figure (NF) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            frequency_list (float):
                This parameter specifies the list of frequencies at which the NF of the DUT is computed. This value is expressed in Hz.
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
            error_code = self._interpreter.nf_configure_frequency_list(
                updated_selector_string, frequency_list
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency_list_start_stop_points(
        self, selector_string, start_frequency, stop_frequency, number_of_points
    ):
        r"""Configures the list of frequencies at which the noise figure (NF) measurement has to be performed. The start frequency
        and stop frequency points are inclusive in the frequency list.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            start_frequency (float):
                This parameter specifies the lowest frequency at which to perform the NF measurement. This value is expressed in Hz.

            stop_frequency (float):
                This parameter specifies the highest frequency at which to perform the NF measurement. This value is expressed in Hz.

            number_of_points (int):
                This parameter specifies the number of frequency points in the list of frequencies at which to perform the NF
                measurement. This value is expressed in Hz.

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
            error_code = self._interpreter.nf_configure_frequency_list_start_stop_points(
                updated_selector_string, start_frequency, stop_frequency, number_of_points
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency_list_start_stop_step(
        self, selector_string, start_frequency, stop_frequency, step_size
    ):
        r"""Configures the list of frequencies at which to perform the noise figure (NF) measurement. The start frequency and stop
        frequency points are inclusive in the frequency list.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            start_frequency (float):
                This parameter specifies the lowest frequency at which to perform the NF measurement. This value is expressed in Hz.

            stop_frequency (float):
                This parameter specifies the highest frequency at which to perform the NF measurement. This value is expressed in Hz.

            step_size (float):
                This parameter specifies the spacing between adjacent frequency points in the list of frequencies at which to perform
                the NF measurement. This value is expressed in Hz.

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
            error_code = self._interpreter.nf_configure_frequency_list_start_stop_step(
                updated_selector_string, start_frequency, stop_frequency, step_size
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_bandwidth(self, selector_string, measurement_bandwidth):
        r"""Configures the effective noise-bandwidth in which power measurements are performed in the noise figure (NF)
        measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_bandwidth (float):
                This parameter specifies the effective noise-bandwidth in which power measurements are performed for the NF
                measurement. This value is expressed in Hz. The default value is 100 kHz.

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
            error_code = self._interpreter.nf_configure_measurement_bandwidth(
                updated_selector_string, measurement_bandwidth
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval(self, selector_string, measurement_interval):
        r"""Configures the duration for which the signals are acquired at each frequency to perform the noise figure (NF)
        measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_interval (float):
                This parameter specifies the duration for which signals are acquired at each frequency which you specify in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.FREQUENCY_LIST` attribute. This value is expressed in seconds. The
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
            error_code = self._interpreter.nf_configure_measurement_interval(
                updated_selector_string, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_method(self, selector_string, measurement_method):
        r"""Configures the noise figure (NF) measurement to use either the Y-factor or the cold source method.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurement_method (enums.NFMeasurementMethod, int):
                This parameter specifies the measurement method used to perform the NF measurement. Refer to the NF concept topic for
                more information. The default value is **Y-Factor**.

                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)    | Description                                                                                                              |
                +=================+==========================================================================================================================+
                | Y-Factor (0)    | The NF measurement computes the noise figure of the DUT using a noise source with a calibrated excess-noise ratio        |
                |                 | (ENR).                                                                                                                   |
                |                 | Refer to NF Y-Factor NS Type for information about the supported devices and their corresponding noise source type.      |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | Cold Source (1) | The NF measurement computes the noise figure of the DUT using a 50 ohm microwave termination as the noise source.        |
                |                 | Supported Devices: PXIe-5644/5645/5646/5840/5841/5842/5860, PXIe-5830/5831/5832                                          |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            measurement_method = (
                measurement_method.value
                if type(measurement_method) is enums.NFMeasurementMethod
                else measurement_method
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_measurement_method(
                updated_selector_string, measurement_method
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_y_factor_mode(self, selector_string, y_factor_mode):
        r"""Configures the Y-Factor based noise figure (NF) measurement to perform the calibration step or the measurement step.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            y_factor_mode (enums.NFYFactorMode, int):
                This parameter specifies whether the measurement should calibrate the noise characteristics of the analyzer or compute
                the noise characteristics of the DUT when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**.

                +---------------+----------------------------------------------------------------------------------------------------------------------+
                | Name (Value)  | Description                                                                                                          |
                +===============+======================================================================================================================+
                | Measure (0)   | The NF measurement computes the noise characteristics of the DUT, compensating for the noise figure of the analyzer. |
                +---------------+----------------------------------------------------------------------------------------------------------------------+
                | Calibrate (1) | The NF measurement computes the noise characteristics of the analyzer.                                               |
                +---------------+----------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            y_factor_mode = (
                y_factor_mode.value if type(y_factor_mode) is enums.NFYFactorMode else y_factor_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_y_factor_mode(
                updated_selector_string, y_factor_mode
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_y_factor_noise_source_enr(
        self, selector_string, enr_frequency, enr, cold_temperature, off_temperature
    ):
        r"""Configures excess noise ratio (ENR) and temperature of the noise source used by the Y-factor method.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            enr_frequency (float):
                This parameter specifies an array of frequencies corresponding to the effective noise ratio (ENR) values specified by
                the **ENR** parameter. This value is expressed in Hz. The default value is an empty array.

            enr (float):
                This parameter specifies the array of ENR values of the noise source as a function of the frequency. This value is
                expressed in dB. The corresponding frequencies are specified by the **ENR Freq** parameter. This attribute is used only
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MEASUREMENT_METHOD` attribute to **Y-Factor**. This
                value is expressed in dB. The default value is an empty array.

            cold_temperature (float):
                This parameter specifies the calibrated cold noise temperature of the noise source used in the Y-Factor method. This
                value is expressed in kelvin. The default value is 302.8.

            off_temperature (float):
                This parameter specifies the physical temperature of the noise source used in the Y-Factor method when the noise source
                is turned off. This value is expressed in kelvin. The default value is 297.

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
            error_code = self._interpreter.nf_configure_y_factor_noise_source_enr(
                updated_selector_string, enr_frequency, enr, cold_temperature, off_temperature
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_y_factor_noise_source_loss(
        self,
        selector_string,
        noise_source_loss_compensation_enabled,
        noise_source_loss_frequency,
        noise_source_loss,
        noise_source_loss_temperature,
    ):
        r"""Configures the ohmic loss inherent to the noise source used in the Y-Factor method that is common to the calibration
        and the measurement steps.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            noise_source_loss_compensation_enabled (enums.NFYFactorNoiseSourceLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement should account for ohmic losses inherent to the
                noise source used in the Y-Factor method common to the calibration and measurement steps. The default value is
                **False**.

                +--------------+-------------------------------------------------------+
                | Name (Value) | Description                                           |
                +==============+=======================================================+
                | False (0)    | Ohmic losses are ignored.                             |
                +--------------+-------------------------------------------------------+
                | True (1)     | Ohmic losses are accounted for in the NF measurement. |
                +--------------+-------------------------------------------------------+

            noise_source_loss_frequency (float):
                This parameter specifies the array of the frequencies corresponding to the ohmic loss inherent to the noise source used
                in the Y-Factor method specified by the **Noise Source Loss** parameter. This value is expressed in Hz. The default
                value is an empty array.

            noise_source_loss (float):
                This parameter specifies an array of the ohmic losses inherent to the noise source used in the Y-Factor method. This
                value is expressed in dB. This loss is accounted for by the NF measurement when you set the **Noise Source Loss
                Compensation Enabled** parameter to **True**. The default value is an empty array.

                You must specify the frequencies at which the losses were measured using the **Noise Source Loss Frequency**
                parameter.

            noise_source_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements specified in the **Noise Source Loss**
                parameter. This value is expressed in kelvin. The default value is 297.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            noise_source_loss_compensation_enabled = (
                noise_source_loss_compensation_enabled.value
                if type(noise_source_loss_compensation_enabled)
                is enums.NFYFactorNoiseSourceLossCompensationEnabled
                else noise_source_loss_compensation_enabled
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_configure_y_factor_noise_source_loss(
                updated_selector_string,
                noise_source_loss_compensation_enabled,
                noise_source_loss_frequency,
                noise_source_loss,
                noise_source_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_y_factor_noise_source_settling_time(self, selector_string, settling_time):
        r"""Configures the time required for the acquisition to wait till the noise source used in the Y-Factor method settles to
        hot or cold state when the noise source is powered on or off.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            settling_time (float):
                This parameter specifies the time to wait till the noise source used in the Y-Factor method settles to either hot or
                cold state when the noise source is enabled or disabled. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_TYPE` attribute to **External Noise Source**. This
                value is expressed in seconds. The default value is 0.

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
            error_code = self._interpreter.nf_configure_y_factor_noise_source_settling_time(
                updated_selector_string, settling_time
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def recommend_reference_level(self, selector_string, dut_max_gain, dut_max_noise_figure):
        r"""Computes and sets an appropriate reference level based on the expected maximum DUT gain, maximum DUT noise figure, and
        other measurement and analyzer attributes. You must not set :py:attr:`~nirfmxinstr.attribute.AttributeID.MIXER_LEVEL`,
        :py:attr:`~nirfmxinstr.attribute.AttributeID.MIXER_LEVEL_OFFSET`,
        :py:attr:`~nirfmxinstr.attribute.AttributeID.IF_OUTPUT_POWER_LEVEL_OFFSET`, and
        :py:attr:`~nirfmxinstr.attribute.AttributeID.IF_FILTER_BANDWIDTH` attributes in order to obtain an appropriate
        recommended reference level.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            dut_max_gain (float):
                This parameter returns the expected maximum gain from the DUT. This value is expressed in dB.

            dut_max_noise_figure (float):
                This parameter returns the expected maximum noise figure of the DUT. This value is expressed in dB.

        Returns:
            Tuple (reference_level, error_code):

            reference_level (float):
                This parameter returns the recommended reference level for the NF measurement. This value is expressed in dBm for RF
                devices and as V\ :sub:`pk-pk`\ for baseband devices.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            reference_level, error_code = self._interpreter.nf_recommend_reference_level(
                updated_selector_string, dut_max_gain, dut_max_noise_figure
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return reference_level, error_code

    @_raise_if_disposed
    def validate_calibration_data(self, selector_string):
        r"""Indicates whether the calibration data is valid for the configuration specified by the signal name in the **Selector
        string** parameter.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            Tuple (calibration_data_valid, error_code):

            calibration_data_valid (enums.NFCalibrationDataValid):
                This parameter returns whether the calibration data is valid.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | False (0)    | Returns false if the calibration data is not present for one or more frequency points in the list or if the difference   |
                |              | between the current device temperature and the calibration temperature exceeds the tolerance specified by the NF Device  |
                |              | Temperature Tolerance attribute.                                                                                         |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | True (1)     | Returns true if the calibration data is present for all of the frequencies in the list.                                  |
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
            calibration_data_valid, error_code = self._interpreter.nf_validate_calibration_data(
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return calibration_data_valid, error_code

    @_raise_if_disposed
    def load_dut_input_loss_from_s2p(
        self,
        selector_string,
        dut_input_loss_compensation_enabled,
        dut_input_loss_s2p_file_path,
        dut_input_loss_s_parameter_orientation,
        dut_input_loss_temperature,
    ):
        r"""Loads the ohmic Input loss data from an S2P file and configures the loss elements between the noise source and the
        input port of DUT, excluding the losses that are common to the calibration step and the measurement step.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_input_loss_compensation_enabled (enums.NFDutInputLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement accounts for ohmic losses between the noise source
                and the input port of the DUT, excluding the losses that are common to calibration and the measurement steps, which are
                specified by the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. The default
                value is **False**.

                +--------------+---------------------------------------------------+
                | Name (Value) | Description                                       |
                +==============+===================================================+
                | False (0)    | The NF measurement ignores the ohmic losses.      |
                +--------------+---------------------------------------------------+
                | True (1)     | The NF measurement accounts for the ohmic losses. |
                +--------------+---------------------------------------------------+

            dut_input_loss_s2p_file_path (string):
                This parameterspecifies the path to the S2P file that contains DUT Input Loss for the specified port.

            dut_input_loss_s_parameter_orientation (enums.NFDutInputLossS2pSParameterOrientation, int):
                This parameter specifies the orientation of the data in the S-parameter table relative to the port you specify. The
                default value is **Port1 Towards DUT**.

                +-----------------------+------------------------------------------------+
                | Name (Value)          | Description                                    |
                +=======================+================================================+
                | Port1 Towards DUT (0) | Port 1 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+
                | Port2 Towards DUT (1) | Port 2 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+

            dut_input_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements considered in the **DUT Input Loss**
                parameter. This value is expressed in kelvin. The default value is 297.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            dut_input_loss_compensation_enabled = (
                dut_input_loss_compensation_enabled.value
                if type(dut_input_loss_compensation_enabled)
                is enums.NFDutInputLossCompensationEnabled
                else dut_input_loss_compensation_enabled
            )
            _helper.validate_not_none(dut_input_loss_s2p_file_path, "dut_input_loss_s2p_file_path")
            dut_input_loss_s_parameter_orientation = (
                dut_input_loss_s_parameter_orientation.value
                if type(dut_input_loss_s_parameter_orientation)
                is enums.NFDutInputLossS2pSParameterOrientation
                else dut_input_loss_s_parameter_orientation
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_dut_input_loss_from_s2p(
                updated_selector_string,
                dut_input_loss_compensation_enabled,
                dut_input_loss_s2p_file_path,
                dut_input_loss_s_parameter_orientation,
                dut_input_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_dut_output_loss_from_s2p(
        self,
        selector_string,
        dut_output_loss_compensation_enabled,
        dut_output_loss_s2p_file_path,
        dut_output_loss_s_parameter_orientation,
        dut_output_loss_temperature,
    ):
        r"""Loads the ohmic Output loss data from an S2P file and configures the loss elements between the output port of the DUT
        and the input port of the analyzer.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_output_loss_compensation_enabled (enums.NFDutOutputLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement accounts for ohmic losses between the output port of
                the DUT and the input port of the analyzer. The default value is **False**.

                +--------------+------------------------------------------------+
                | Name (Value) | Description                                    |
                +==============+================================================+
                | False (0)    | The measurement ignores ohmic losses.          |
                +--------------+------------------------------------------------+
                | True (1)     | The measurement accounts for the ohmic losses. |
                +--------------+------------------------------------------------+

            dut_output_loss_s2p_file_path (string):
                This parameterspecifies the path to the S2P file that contains DUT Output Loss for the specified port.

            dut_output_loss_s_parameter_orientation (enums.NFDutOutputLossS2pSParameterOrientation, int):
                This parameter specifies the orientation of the data in the S-parameter table relative to the port you specify. The
                default value is **Port1 Towards DUT**.

                +-----------------------+------------------------------------------------+
                | Name (Value)          | Description                                    |
                +=======================+================================================+
                | Port1 Towards DUT (0) | Port 1 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+
                | Port2 Towards DUT (1) | Port 2 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+

            dut_output_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DUT_OUTPUT_LOSS` attribute. This value is expressed in kelvin. The
                default value is 297.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            dut_output_loss_compensation_enabled = (
                dut_output_loss_compensation_enabled.value
                if type(dut_output_loss_compensation_enabled)
                is enums.NFDutOutputLossCompensationEnabled
                else dut_output_loss_compensation_enabled
            )
            _helper.validate_not_none(
                dut_output_loss_s2p_file_path, "dut_output_loss_s2p_file_path"
            )
            dut_output_loss_s_parameter_orientation = (
                dut_output_loss_s_parameter_orientation.value
                if type(dut_output_loss_s_parameter_orientation)
                is enums.NFDutOutputLossS2pSParameterOrientation
                else dut_output_loss_s_parameter_orientation
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_dut_output_loss_from_s2p(
                updated_selector_string,
                dut_output_loss_compensation_enabled,
                dut_output_loss_s2p_file_path,
                dut_output_loss_s_parameter_orientation,
                dut_output_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_calibration_loss_from_s2p(
        self,
        selector_string,
        calibration_loss_compensation_enabled,
        calibration_loss_s2p_file_path,
        calibration_loss_s_parameter_orientation,
        calibration_loss_temperature,
    ):
        r"""Loads the ohmic loss data from an S2P file, as a function of frequency of the loss elements between the noise source
        and the input port of the analyzer during the calibration step, excluding the loss specified as the noise source loss.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            calibration_loss_compensation_enabled (enums.NFCalibrationLossCompensationEnabled, int):
                This parameter specifies whether the noise figure (NF) measurement accounts for the ohmic losses between the noise
                source and input port of the analyzer during the calibration step, excluding any losses which you have specified using
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.Y_FACTOR_NOISE_SOURCE_LOSS` attribute. The default value is
                **False**.

                +--------------+---------------------------------------------------+
                | Name (Value) | Description                                       |
                +==============+===================================================+
                | False (0)    | The NF measurement ignores the ohmic losses.      |
                +--------------+---------------------------------------------------+
                | True (1)     | The NF measurement accounts for the ohmic losses. |
                +--------------+---------------------------------------------------+

            calibration_loss_s2p_file_path (string):
                This parameter specifies the path to the S2P file that contains Callibration Loss for the specified port.

            calibration_loss_s_parameter_orientation (enums.NFCalibrationLossS2pSParameterOrientation, int):
                This parameter specifies the orientation of the data in the S-parameter table relative to the port you specify. The
                default value is **Port1 Towards DUT**.

                +-----------------------+------------------------------------------------+
                | Name (Value)          | Description                                    |
                +=======================+================================================+
                | Port1 Towards DUT (0) | Port 1 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+
                | Port2 Towards DUT (1) | Port 2 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+

            calibration_loss_temperature (float):
                This parameter specifies the physical temperature of the ohmic loss elements specified by the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CALIBRATION_LOSS` attribute. This value is expressed in kelvin.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            calibration_loss_compensation_enabled = (
                calibration_loss_compensation_enabled.value
                if type(calibration_loss_compensation_enabled)
                is enums.NFCalibrationLossCompensationEnabled
                else calibration_loss_compensation_enabled
            )
            _helper.validate_not_none(
                calibration_loss_s2p_file_path, "calibration_loss_s2p_file_path"
            )
            calibration_loss_s_parameter_orientation = (
                calibration_loss_s_parameter_orientation.value
                if type(calibration_loss_s_parameter_orientation)
                is enums.NFCalibrationLossS2pSParameterOrientation
                else calibration_loss_s_parameter_orientation
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_calibration_loss_from_s2p(
                updated_selector_string,
                calibration_loss_compensation_enabled,
                calibration_loss_s2p_file_path,
                calibration_loss_s_parameter_orientation,
                calibration_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_cold_source_dut_s_parameter_from_s2p(
        self, selector_string, dut_s_parameters_s2p_file_path, dut_s_parameter_orientation
    ):
        r"""Loads the scattering parameter data from an S2P file and configures them as a function of frequency for use in the cold
        source measurement method.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dut_s_parameters_s2p_file_path (string):
                This parameterspecifies the path to the S2P file that contains DUT S-Parameters for the specified port.

            dut_s_parameter_orientation (enums.NFColdSourceDutS2pSParameterOrientation, int):
                This parameter specifies the orientation of the data in the S-parameter table relative to the port you specify. The
                default value is **Port1 Towards DUT**.

                +-----------------------+------------------------------------------------+
                | Name (Value)          | Description                                    |
                +=======================+================================================+
                | Port1 Towards DUT (0) | Port 1 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+
                | Port2 Towards DUT (1) | Port 2 of the S2P is oriented towards the DUT. |
                +-----------------------+------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(
                dut_s_parameters_s2p_file_path, "dut_s_parameters_s2p_file_path"
            )
            dut_s_parameter_orientation = (
                dut_s_parameter_orientation.value
                if type(dut_s_parameter_orientation)
                is enums.NFColdSourceDutS2pSParameterOrientation
                else dut_s_parameter_orientation
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_cold_source_dut_s_parameter_from_s2p(
                updated_selector_string, dut_s_parameters_s2p_file_path, dut_s_parameter_orientation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_y_factor_noise_source_loss_from_s2p(
        self,
        selector_string,
        noise_source_loss_compensation_enabled,
        noise_source_loss_s2p_file_path,
        noise_source_loss_s_parameter_orientation,
        noise_source_loss_temperature,
    ):
        r"""

        Args:
            selector_string (string):
            noise_source_loss_compensation_enabled (enums.NFYFactorNoiseSourceLossCompensationEnabled, int):
            noise_source_loss_s2p_file_path (string):
            noise_source_loss_s_parameter_orientation (enums.NFYFactorNoiseSourceLossS2pSParameterOrientation, int):
            noise_source_loss_temperature (float):
        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            noise_source_loss_compensation_enabled = (
                noise_source_loss_compensation_enabled.value
                if type(noise_source_loss_compensation_enabled)
                is enums.NFYFactorNoiseSourceLossCompensationEnabled
                else noise_source_loss_compensation_enabled
            )
            _helper.validate_not_none(
                noise_source_loss_s2p_file_path, "noise_source_loss_s2p_file_path"
            )
            noise_source_loss_s_parameter_orientation = (
                noise_source_loss_s_parameter_orientation.value
                if type(noise_source_loss_s_parameter_orientation)
                is enums.NFYFactorNoiseSourceLossS2pSParameterOrientation
                else noise_source_loss_s_parameter_orientation
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_y_factor_noise_source_loss_from_s2p(
                updated_selector_string,
                noise_source_loss_compensation_enabled,
                noise_source_loss_s2p_file_path,
                noise_source_loss_s_parameter_orientation,
                noise_source_loss_temperature,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_cold_source_input_termination_from_s1p(
        self, selector_string, termination_s1p_file_path, termination_temperature
    ):
        r"""

        Args:
            selector_string (string):
            termination_s1p_file_path (string):
            termination_temperature (float):
        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(termination_s1p_file_path, "termination_s1p_file_path")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_cold_source_input_termination_from_s1p(
                updated_selector_string, termination_s1p_file_path, termination_temperature
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def load_external_preamp_gain_from_s2p(
        self,
        selector_string,
        external_preamp_present,
        external_preamp_gain_s2p_file_path,
        external_preamp_gain_s_parameter_orientation,
    ):
        r"""

        Args:
            selector_string (string):
            external_preamp_present (enums.NFExternalPreampPresent, int):
            external_preamp_gain_s2p_file_path (string):
            external_preamp_gain_s_parameter_orientation (enums.NFExternalPreampGainS2pSParameterOrientation, int):
        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            external_preamp_present = (
                external_preamp_present.value
                if type(external_preamp_present) is enums.NFExternalPreampPresent
                else external_preamp_present
            )
            _helper.validate_not_none(
                external_preamp_gain_s2p_file_path, "external_preamp_gain_s2p_file_path"
            )
            external_preamp_gain_s_parameter_orientation = (
                external_preamp_gain_s_parameter_orientation.value
                if type(external_preamp_gain_s_parameter_orientation)
                is enums.NFExternalPreampGainS2pSParameterOrientation
                else external_preamp_gain_s_parameter_orientation
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.nf_load_external_preamp_gain_from_s2p(
                updated_selector_string,
                external_preamp_present,
                external_preamp_gain_s2p_file_path,
                external_preamp_gain_s_parameter_orientation,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
