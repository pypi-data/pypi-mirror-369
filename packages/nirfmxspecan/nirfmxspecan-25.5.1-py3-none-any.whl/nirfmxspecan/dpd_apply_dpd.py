""""""

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


class DpdApplyDpd(object):
    """"""

    def __init__(self, signal_obj):
        """"""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_configuration_input(self, selector_string):
        r"""Gets whether to use the configuration parameters used by the DPD measurement for applying DPD.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measurement**.

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                                              |
        +=================+==========================================================================================================================+
        | Measurement (0) | Uses the computed DPD polynomial or lookup table for applying DPD on an input waveform using the same RFmx session       |
        |                 | handle. The configuration parameters for applying DPD such as the DPD DUT Avg Input Pwr, DPD Model, DPD Meas Sample      |
        |                 | Rate, DPD polynomial, and lookup table                                                                                   |
        |                 | are obtained from the DPD measurement configuration.                                                                     |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | User (1)        | Applies DPD by using a computed DPD polynomial or lookup table on an input waveform. You must set the configuration      |
        |                 | parameters for applying DPD such as the                                                                                  |
        |                 | DPD Apply DPD User DUT Avg Input Pwr, DPD Apply DPD User DPD Model, DPD Apply DPD User Meas Sample Rate, DPD             |
        |                 | polynomial, and lookup table. You do not need to call the RFmxSpecAn Initiate method when you set the DPD Apply DPD      |
        |                 | Config Input attribute User.                                                                                             |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdConfigurationInput):
                Specifies whether to use the configuration parameters used by the DPD measurement for applying DPD.

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
                attributes.AttributeID.DPD_APPLY_DPD_CONFIGURATION_INPUT.value,
            )
            attr_val = enums.DpdApplyDpdConfigurationInput(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_configuration_input(self, selector_string, value):
        r"""Sets whether to use the configuration parameters used by the DPD measurement for applying DPD.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Measurement**.

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)    | Description                                                                                                              |
        +=================+==========================================================================================================================+
        | Measurement (0) | Uses the computed DPD polynomial or lookup table for applying DPD on an input waveform using the same RFmx session       |
        |                 | handle. The configuration parameters for applying DPD such as the DPD DUT Avg Input Pwr, DPD Model, DPD Meas Sample      |
        |                 | Rate, DPD polynomial, and lookup table                                                                                   |
        |                 | are obtained from the DPD measurement configuration.                                                                     |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | User (1)        | Applies DPD by using a computed DPD polynomial or lookup table on an input waveform. You must set the configuration      |
        |                 | parameters for applying DPD such as the                                                                                  |
        |                 | DPD Apply DPD User DUT Avg Input Pwr, DPD Apply DPD User DPD Model, DPD Apply DPD User Meas Sample Rate, DPD             |
        |                 | polynomial, and lookup table. You do not need to call the RFmxSpecAn Initiate method when you set the DPD Apply DPD      |
        |                 | Config Input attribute User.                                                                                             |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdConfigurationInput, int):
                Specifies whether to use the configuration parameters used by the DPD measurement for applying DPD.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdConfigurationInput else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_CONFIGURATION_INPUT.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_lookup_table_correction_type(self, selector_string):
        r"""Gets the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
        **Lookup Table**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Magnitude and Phase**.

        +-------------------------+----------------------------------------------------------------------------+
        | Name (Value)            | Description                                                                |
        +=========================+============================================================================+
        | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
        +-------------------------+----------------------------------------------------------------------------+
        | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
        +-------------------------+----------------------------------------------------------------------------+
        | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
        +-------------------------+----------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdLookupTableCorrectionType):
                Specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
                **Lookup Table**.

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
                attributes.AttributeID.DPD_APPLY_DPD_LOOKUP_TABLE_CORRECTION_TYPE.value,
            )
            attr_val = enums.DpdApplyDpdLookupTableCorrectionType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_lookup_table_correction_type(self, selector_string, value):
        r"""Sets the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
        **Lookup Table**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Magnitude and Phase**.

        +-------------------------+----------------------------------------------------------------------------+
        | Name (Value)            | Description                                                                |
        +=========================+============================================================================+
        | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
        +-------------------------+----------------------------------------------------------------------------+
        | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
        +-------------------------+----------------------------------------------------------------------------+
        | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
        +-------------------------+----------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdLookupTableCorrectionType, int):
                Specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
                **Lookup Table**.

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
                value.value if type(value) is enums.DpdApplyDpdLookupTableCorrectionType else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_LOOKUP_TABLE_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_memory_model_correction_type(self, selector_string):
        r"""Gets the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
        **Memory Polynomial** or ** Generalized Memory Polynomial**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Magnitude and Phase**.

        +-------------------------+----------------------------------------------------------------------------+
        | Name (Value)            | Description                                                                |
        +=========================+============================================================================+
        | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
        +-------------------------+----------------------------------------------------------------------------+
        | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
        +-------------------------+----------------------------------------------------------------------------+
        | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
        +-------------------------+----------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdMemoryModelCorrectionType):
                Specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
                **Memory Polynomial** or ** Generalized Memory Polynomial**.

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
                attributes.AttributeID.DPD_APPLY_DPD_MEMORY_MODEL_CORRECTION_TYPE.value,
            )
            attr_val = enums.DpdApplyDpdMemoryModelCorrectionType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_memory_model_correction_type(self, selector_string, value):
        r"""Sets the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
        **Memory Polynomial** or ** Generalized Memory Polynomial**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Magnitude and Phase**.

        +-------------------------+----------------------------------------------------------------------------+
        | Name (Value)            | Description                                                                |
        +=========================+============================================================================+
        | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
        +-------------------------+----------------------------------------------------------------------------+
        | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
        +-------------------------+----------------------------------------------------------------------------+
        | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
        +-------------------------+----------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdMemoryModelCorrectionType, int):
                Specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
                **Memory Polynomial** or ** Generalized Memory Polynomial**.

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
                value.value if type(value) is enums.DpdApplyDpdMemoryModelCorrectionType else value
            )
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_MEMORY_MODEL_CORRECTION_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_dut_average_input_power(self, selector_string):
        r"""Gets the average input power for the device under test that was used to compute the DPD Apply DPD User DPD
        Polynomial or the DPD Apply DPD User LUT Complex Gain when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value is expressed in
        dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dBm.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the average input power for the device under test that was used to compute the DPD Apply DPD User DPD
                Polynomial or the DPD Apply DPD User LUT Complex Gain when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value is expressed in
                dBm.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_DUT_AVERAGE_INPUT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_dut_average_input_power(self, selector_string, value):
        r"""Sets the average input power for the device under test that was used to compute the DPD Apply DPD User DPD
        Polynomial or the DPD Apply DPD User LUT Complex Gain when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value is expressed in
        dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -20 dBm.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the average input power for the device under test that was used to compute the DPD Apply DPD User DPD
                Polynomial or the DPD Apply DPD User LUT Complex Gain when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value is expressed in
                dBm.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_DUT_AVERAGE_INPUT_POWER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_dpd_model(self, selector_string):
        r"""Gets the DPD model for applying DPD when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Lookup Table**.

        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                      | Description                                                                                                              |
        +===================================+==========================================================================================================================+
        | Lookup Table (0)                  | This model computes the complex gain coefficients applied to linearize systems with negligible memory effects.           |
        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Memory Polynomial (1)             | This model computes the memory polynomial predistortion coefficients used to linearize systems with moderate memory      |
        |                                   | effects.                                                                                                                 |
        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Generalized Memory Polynomial (2) | This model computes the generalized memory polynomial predistortion coefficients used to linearize systems with          |
        |                                   | significant memory effects.                                                                                              |
        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdUserDpdModel):
                Specifies the DPD model for applying DPD when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_APPLY_DPD_USER_DPD_MODEL.value
            )
            attr_val = enums.DpdApplyDpdUserDpdModel(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_dpd_model(self, selector_string, value):
        r"""Sets the DPD model for applying DPD when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Lookup Table**.

        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                      | Description                                                                                                              |
        +===================================+==========================================================================================================================+
        | Lookup Table (0)                  | This model computes the complex gain coefficients applied to linearize systems with negligible memory effects.           |
        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Memory Polynomial (1)             | This model computes the memory polynomial predistortion coefficients used to linearize systems with moderate memory      |
        |                                   | effects.                                                                                                                 |
        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Generalized Memory Polynomial (2) | This model computes the generalized memory polynomial predistortion coefficients used to linearize systems with          |
        |                                   | significant memory effects.                                                                                              |
        +-----------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdUserDpdModel, int):
                Specifies the DPD model for applying DPD when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdUserDpdModel else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_USER_DPD_MODEL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_measurement_sample_rate(self, selector_string):
        r"""Gets the acquisition sample rate used to compute the DPD Apply DPD User DPD Polynomial or DPD Apply DPD User LUT
        Complex Gain when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the acquisition sample rate used to compute the DPD Apply DPD User DPD Polynomial or DPD Apply DPD User LUT
                Complex Gain when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value is expressed in Hz.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEASUREMENT_SAMPLE_RATE.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_measurement_sample_rate(self, selector_string, value):
        r"""Sets the acquisition sample rate used to compute the DPD Apply DPD User DPD Polynomial or DPD Apply DPD User LUT
        Complex Gain when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value is expressed in Hz.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 120 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition sample rate used to compute the DPD Apply DPD User DPD Polynomial or DPD Apply DPD User LUT
                Complex Gain when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value is expressed in Hz.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEASUREMENT_SAMPLE_RATE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_apply_dpd_user_lookup_table_type(self, selector_string):
        r"""Gets the DPD Lookup Table (LUT) type when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        +--------------+-------------------------------------------------+
        | Name (Value) | Description                                     |
        +==============+=================================================+
        | Log (0)      | Input powers in the LUT are specified in dBm.   |
        +--------------+-------------------------------------------------+
        | Linear (1)   | Input powers in the LUT are specified in watts. |
        +--------------+-------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdUserLookupTableType):
                Specifies the DPD Lookup Table (LUT) type when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_LOOKUP_TABLE_TYPE.value,
            )
            attr_val = enums.DpdApplyDpdUserLookupTableType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_apply_dpd_user_lookup_table_type(self, selector_string, value):
        r"""Sets the DPD Lookup Table (LUT) type when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        +--------------+-------------------------------------------------+
        | Name (Value) | Description                                     |
        +==============+=================================================+
        | Log (0)      | Input powers in the LUT are specified in dBm.   |
        +--------------+-------------------------------------------------+
        | Linear (1)   | Input powers in the LUT are specified in watts. |
        +--------------+-------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdUserLookupTableType, int):
                Specifies the DPD Lookup Table (LUT) type when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdUserLookupTableType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_USER_LOOKUP_TABLE_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_lookup_table_input_power(self, selector_string):
        r"""Gets the input power array for the predistortion lookup table when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Lookup Table**. This value is expressed
        in dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the input power array for the predistortion lookup table when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Lookup Table**. This value is expressed
                in dBm.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_LOOKUP_TABLE_INPUT_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_lookup_table_input_power(self, selector_string, value):
        r"""Sets the input power array for the predistortion lookup table when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Lookup Table**. This value is expressed
        in dBm.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the input power array for the predistortion lookup table when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Lookup Table**. This value is expressed
                in dBm.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_LOOKUP_TABLE_INPUT_POWER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_order(self, selector_string):
        r"""Gets the order of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to K\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the order of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to K\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_order(self, selector_string, value):
        r"""Sets the order of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to K\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 3.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the order of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to K\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_memory_depth(self, selector_string):
        r"""Gets the memory depth of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to Q\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the memory depth of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to Q\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MEMORY_DEPTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_memory_depth(self, selector_string, value):
        r"""Sets the memory depth of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to Q\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the memory depth of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to Q\ :sub:`a`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_lead_order(self, selector_string):
        r"""Gets the lead order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
        to K\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
        polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lead order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
                to K\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
                polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LEAD_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_lead_order(self, selector_string, value):
        r"""Sets the lead order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
        to K\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
        polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lead order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
                to K\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
                polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LEAD_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_lag_order(self, selector_string):
        r"""Gets the lag order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
        to K\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
        polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lag order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
                to K\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
                polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LAG_ORDER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_lag_order(self, selector_string, value):
        r"""Sets the lag order cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
        to K\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
        polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lag order cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
                to K\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
                polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LAG_ORDER.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_lead_memory_depth(self, selector_string):
        r"""Gets the lead memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
        to Q\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
        polynomial.  The value of the DPD Apply DPD User Mem Poly Lead Mem Depth attribute must be greater than or equal to the
        value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lead memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
                to Q\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
                polynomial.  The value of the DPD Apply DPD User Mem Poly Lead Mem Depth attribute must be greater than or equal to the
                value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LEAD_MEMORY_DEPTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_lead_memory_depth(self, selector_string, value):
        r"""Sets the lead memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
        to Q\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
        polynomial.  The value of the DPD Apply DPD User Mem Poly Lead Mem Depth attribute must be greater than or equal to the
        value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lead memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Generalized Memory Polynomial** and set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to **User**. This value corresponds
                to Q\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_ for the generalized memory
                polynomial.  The value of the DPD Apply DPD User Mem Poly Lead Mem Depth attribute must be greater than or equal to the
                value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD` attribute.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LEAD_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_lag_memory_depth(self, selector_string):
        r"""Gets the lag memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to Q\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for the generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the lag memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to Q\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LAG_MEMORY_DEPTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_lag_memory_depth(self, selector_string, value):
        r"""Sets the lag memory depth cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to Q\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for the generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the lag memory depth cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to Q\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_LAG_MEMORY_DEPTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_maximum_lead(self, selector_string):
        r"""Gets the maximum lead stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to M\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for the generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum lead stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to M\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_maximum_lead(self, selector_string, value):
        r"""Sets the maximum lead stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to M\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for the generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum lead stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to M\ :sub:`c`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MAXIMUM_LEAD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_user_memory_polynomial_maximum_lag(self, selector_string):
        r"""Gets the maximum lag stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to M\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for the generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Specifies the maximum lag stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to M\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MAXIMUM_LAG.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_user_memory_polynomial_maximum_lag(self, selector_string, value):
        r"""Sets the maximum lag stagger cross term of the DPD polynomial when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
        Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
        **User**. This value corresponds to M\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
        for the generalized memory polynomial.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum lag stagger cross term of the DPD polynomial when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.USER_DPD_MODEL` attribute to **Memory Polynomial** or **Generalized
                Memory Polynomial** and set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CONFIGURATION_INPUT` attribute to
                **User**. This value corresponds to M\ :sub:`b`\ in the `DPD <www.ni.com/docs/en-US/bundle/rfmx-specan/page/dpd.html>`_
                for the generalized memory polynomial.

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
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEMORY_POLYNOMIAL_MAXIMUM_LAG.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_enabled(self, selector_string):
        r"""Gets whether to enable the crest factor reduction (CFR) on the pre-distorted waveform.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                           |
        +==============+=======================================================================================+
        | False (0)    | Disables CFR. The maximum increase in PAPR, after pre-distortion, is limited to 6 dB. |
        +--------------+---------------------------------------------------------------------------------------+
        | True (1)     | Enables CFR.                                                                          |
        +--------------+---------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdCfrEnabled):
                Specifies whether to enable the crest factor reduction (CFR) on the pre-distorted waveform.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_APPLY_DPD_CFR_ENABLED.value
            )
            attr_val = enums.DpdApplyDpdCfrEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_enabled(self, selector_string, value):
        r"""Sets whether to enable the crest factor reduction (CFR) on the pre-distorted waveform.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+---------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                           |
        +==============+=======================================================================================+
        | False (0)    | Disables CFR. The maximum increase in PAPR, after pre-distortion, is limited to 6 dB. |
        +--------------+---------------------------------------------------------------------------------------+
        | True (1)     | Enables CFR.                                                                          |
        +--------------+---------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdCfrEnabled, int):
                Specifies whether to enable the crest factor reduction (CFR) on the pre-distorted waveform.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdCfrEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_CFR_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_method(self, selector_string):
        r"""Gets the method used to perform the crest factor reduction (CFR) when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Clipping**.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | Clipping (0)       | Hard clips the signal such that the target PAPR is achieved.                                                             |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Peak Windowing (1) | Scales the peaks in the signal using weighted window function to get smooth peaks and achieve the target PAPR.           |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sigmoid (2)        | Scales the peaks using modified sigmoid transfer function to get smooth peaks and achieve the target PAPR. This method   |
        |                    | does not support the filter operation.                                                                                   |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdCfrMethod):
                Specifies the method used to perform the crest factor reduction (CFR) when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_APPLY_DPD_CFR_METHOD.value
            )
            attr_val = enums.DpdApplyDpdCfrMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_method(self, selector_string, value):
        r"""Sets the method used to perform the crest factor reduction (CFR) when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Clipping**.

        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)       | Description                                                                                                              |
        +====================+==========================================================================================================================+
        | Clipping (0)       | Hard clips the signal such that the target PAPR is achieved.                                                             |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Peak Windowing (1) | Scales the peaks in the signal using weighted window function to get smooth peaks and achieve the target PAPR.           |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Sigmoid (2)        | Scales the peaks using modified sigmoid transfer function to get smooth peaks and achieve the target PAPR. This method   |
        |                    | does not support the filter operation.                                                                                   |
        +--------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdCfrMethod, int):
                Specifies the method used to perform the crest factor reduction (CFR) when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdCfrMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_CFR_METHOD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_maximum_iterations(self, selector_string):
        r"""Gets the maximum number of iterations allowed to converge waveform PAPR to target PAPR when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

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
                Specifies the maximum number of iterations allowed to converge waveform PAPR to target PAPR when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_MAXIMUM_ITERATIONS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_maximum_iterations(self, selector_string, value):
        r"""Sets the maximum number of iterations allowed to converge waveform PAPR to target PAPR when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of iterations allowed to converge waveform PAPR to target PAPR when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_MAXIMUM_ITERATIONS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_target_papr_type(self, selector_string):
        r"""Gets the target PAPR type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
        to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Input PAPR**.

        +----------------+---------------------------------------------------------------------------------------------------+
        | Name (Value)   | Description                                                                                       |
        +================+===================================================================================================+
        | Input PAPR (0) | Sets the target PAPR for pre-distorted waveform equal to the PAPR of input waveform.              |
        +----------------+---------------------------------------------------------------------------------------------------+
        | Custom (1)     | Sets the target PAPR equal to the value that you set for the Apply DPD CFR Target PAPR attribute. |
        +----------------+---------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdCfrTargetPaprType):
                Specifies the target PAPR type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
                to **True**.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_TARGET_PAPR_TYPE.value,
            )
            attr_val = enums.DpdApplyDpdCfrTargetPaprType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_target_papr_type(self, selector_string, value):
        r"""Sets the target PAPR type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
        to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Input PAPR**.

        +----------------+---------------------------------------------------------------------------------------------------+
        | Name (Value)   | Description                                                                                       |
        +================+===================================================================================================+
        | Input PAPR (0) | Sets the target PAPR for pre-distorted waveform equal to the PAPR of input waveform.              |
        +----------------+---------------------------------------------------------------------------------------------------+
        | Custom (1)     | Sets the target PAPR equal to the value that you set for the Apply DPD CFR Target PAPR attribute. |
        +----------------+---------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdCfrTargetPaprType, int):
                Specifies the target PAPR type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
                to **True**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdCfrTargetPaprType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_CFR_TARGET_PAPR_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_target_papr(self, selector_string):
        r"""Gets the target PAPR when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to
        **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_TARGET_PAPR_TYPE` attribute to **Custom**. This
        value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 8.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the target PAPR when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to
                **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_TARGET_PAPR_TYPE` attribute to **Custom**. This
                value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_APPLY_DPD_CFR_TARGET_PAPR.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_target_papr(self, selector_string, value):
        r"""Sets the target PAPR when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to
        **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_TARGET_PAPR_TYPE` attribute to **Custom**. This
        value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 8.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the target PAPR when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to
                **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_TARGET_PAPR_TYPE` attribute to **Custom**. This
                value is expressed in dB.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_TARGET_PAPR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_window_type(self, selector_string):
        r"""Gets the window type to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak
        Windowing**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Kaiser-Bessel**.

        +---------------------+----------------------------------------------------------+
        | Name (Value)        | Description                                              |
        +=====================+==========================================================+
        | Flat Top (1)        | Uses the flat top window function to scale peaks.        |
        +---------------------+----------------------------------------------------------+
        | Hanning (2)         | Uses the Hanning window function to scale peaks.         |
        +---------------------+----------------------------------------------------------+
        | Hamming (3)         | Uses the Hamming window function to scale peaks.         |
        +---------------------+----------------------------------------------------------+
        | Gaussian (4)        | Uses the Gaussian window function to scale peaks.        |
        +---------------------+----------------------------------------------------------+
        | Blackman (5)        | Uses the Blackman window function to scale peaks.        |
        +---------------------+----------------------------------------------------------+
        | Blackman-Harris (6) | Uses the Blackman-Harris window function to scale peaks. |
        +---------------------+----------------------------------------------------------+
        | Kaiser-Bessel (7)   | Uses the Kaiser-Bessel window function to scale peaks.   |
        +---------------------+----------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdApplyDpdCfrWindowType):
                Specifies the window type to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak
                Windowing**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_APPLY_DPD_CFR_WINDOW_TYPE.value
            )
            attr_val = enums.DpdApplyDpdCfrWindowType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_window_type(self, selector_string, value):
        r"""Sets the window type to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak
        Windowing**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Kaiser-Bessel**.

        +---------------------+----------------------------------------------------------+
        | Name (Value)        | Description                                              |
        +=====================+==========================================================+
        | Flat Top (1)        | Uses the flat top window function to scale peaks.        |
        +---------------------+----------------------------------------------------------+
        | Hanning (2)         | Uses the Hanning window function to scale peaks.         |
        +---------------------+----------------------------------------------------------+
        | Hamming (3)         | Uses the Hamming window function to scale peaks.         |
        +---------------------+----------------------------------------------------------+
        | Gaussian (4)        | Uses the Gaussian window function to scale peaks.        |
        +---------------------+----------------------------------------------------------+
        | Blackman (5)        | Uses the Blackman window function to scale peaks.        |
        +---------------------+----------------------------------------------------------+
        | Blackman-Harris (6) | Uses the Blackman-Harris window function to scale peaks. |
        +---------------------+----------------------------------------------------------+
        | Kaiser-Bessel (7)   | Uses the Kaiser-Bessel window function to scale peaks.   |
        +---------------------+----------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdApplyDpdCfrWindowType, int):
                Specifies the window type to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak
                Windowing**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdApplyDpdCfrWindowType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_CFR_WINDOW_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_window_length(self, selector_string):
        r"""Gets the maximum window length to be used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True** and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak Windowing**.

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
                Specifies the maximum window length to be used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak Windowing**.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_WINDOW_LENGTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_window_length(self, selector_string, value):
        r"""Sets the maximum window length to be used when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True** and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak Windowing**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum window length to be used when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Peak Windowing**.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_WINDOW_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_shaping_factor(self, selector_string):
        r"""Gets the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
        Refer to DPD concept topic for more information about shaping factor.

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
                Specifies the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
                Refer to DPD concept topic for more information about shaping factor.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_SHAPING_FACTOR.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_shaping_factor(self, selector_string, value):
        r"""Sets the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
        Refer to DPD concept topic for more information about shaping factor.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 5.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
                Refer to DPD concept topic for more information about shaping factor.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_SHAPING_FACTOR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_shaping_threshold(self, selector_string):
        r"""Gets the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
        This value is expressed in dB. Refer to DPD concept topic for more information about shaping threshold.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -5.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
                This value is expressed in dB. Refer to DPD concept topic for more information about shaping threshold.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_SHAPING_THRESHOLD.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_shaping_threshold(self, selector_string, value):
        r"""Sets the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
        This value is expressed in dB. Refer to DPD concept topic for more information about shaping threshold.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -5.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
                This value is expressed in dB. Refer to DPD concept topic for more information about shaping threshold.

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
                attributes.AttributeID.DPD_APPLY_DPD_CFR_SHAPING_THRESHOLD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_configuration_input(self, selector_string, configuration_input):
        r"""Configures the source of measurement settings for applying DPD.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            configuration_input (enums.DpdApplyDpdConfigurationInput, int):
                This parameter specifies the mode of configuring parameters for applying DPD. The default value is **Measurement**.

                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value)    | Description                                                                                                              |
                +=================+==========================================================================================================================+
                | Measurement (0) | Uses the computed DPD polynomial or lookup table for applying DPD on an input waveform using the same RFmx session       |
                |                 | handle. The configuration parameters for applying DPD such as the DPD DUT Avg Input Pwr, DPD Model, DPD Meas Sample      |
                |                 | Rate, DPD polynomial, and lookup table                                                                                   |
                |                 | are obtained from the DPD measurement configuration.                                                                     |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+
                | User (1)        | Applies DPD by using a computed DPD polynomial or lookup table on an input waveform. You must set the configuration      |
                |                 | parameters for applying DPD such as the                                                                                  |
                |                 | DPD Apply DPD User DUT Avg Input Pwr, DPD Apply DPD User DPD Model, DPD Apply DPD User Meas Sample Rate, DPD             |
                |                 | polynomial, and lookup table.                                                                                            |
                +-----------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            configuration_input = (
                configuration_input.value
                if type(configuration_input) is enums.DpdApplyDpdConfigurationInput
                else configuration_input
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_configuration_input(
                updated_selector_string, configuration_input
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_lookup_table_correction_type(self, selector_string, lut_correction_type):
        r"""Configures the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to
        **Lookup Table**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            lut_correction_type (enums.DpdApplyDpdLookupTableCorrectionType, int):
                This parameter specifies the predistortion type when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
                attribute to **Lookup Table**. The default value is **Magnitude and Phase**.

                +-------------------------+----------------------------------------------------------------------------+
                | Name (Value)            | Description                                                                |
                +=========================+============================================================================+
                | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
                +-------------------------+----------------------------------------------------------------------------+
                | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
                +-------------------------+----------------------------------------------------------------------------+
                | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
                +-------------------------+----------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            lut_correction_type = (
                lut_correction_type.value
                if type(lut_correction_type) is enums.DpdApplyDpdLookupTableCorrectionType
                else lut_correction_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_lookup_table_correction_type(
                updated_selector_string, lut_correction_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_user_lookup_table(self, selector_string, lut_input_powers, lut_complex_gains):
        r"""Configures the predistortion lookup table when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        property to
        **
        Lookup Table
        **
        .

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            lut_input_powers (float):
                This parameter specifies the array of lookup table power levels, in dBm.

            lut_complex_gains (numpy.complex64):
                This parameter specifies the array of lookup table complex gain values for magnitude and phase predistortion.

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
            error_code = self._interpreter.dpd_configure_user_lookup_table(
                updated_selector_string, lut_input_powers, lut_complex_gains
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_user_dpd_polynomial(self, selector_string, dpd_polynomial):
        r"""Configures the array of memory polynomial or generalized memory polynomial coefficients when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Memory Polynomial** or **Generalized Memory
        Polynomial**.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            dpd_polynomial (numpy.complex64):
                This parameter specifies the array of memory polynomial or generalized memory polynomial coefficients when you set the
                DPD Model attribute to **Memory Polynomial** or **Generalized Memory Polynomial**.

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
            error_code = self._interpreter.dpd_configure_user_dpd_polynomial(
                updated_selector_string, dpd_polynomial
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_memory_model_correction_type(self, selector_string, memory_model_correction_type):
        r"""Configures the predistortion type when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL`
        property to
        **
        Memory Polynomial
        **
        or
        **
        Generalized Memory Polynomial
        **
        .

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            memory_model_correction_type (enums.DpdApplyDpdMemoryModelCorrectionType, int):
                This parameter specifies the predistortion type when you set the DPD Model attribute to **Memory Polynomial** or
                **Generalized Memory Polynomial**. The default value is **Magnitude and Phase**.

                +-------------------------+----------------------------------------------------------------------------+
                | Name (Value)            | Description                                                                |
                +=========================+============================================================================+
                | Magnitude and Phase (0) | The measurement predistorts the magnitude and phase of the input waveform. |
                +-------------------------+----------------------------------------------------------------------------+
                | Magnitude Only (1)      | The measurement predistorts only the magnitude of the input waveform.      |
                +-------------------------+----------------------------------------------------------------------------+
                | Phase Only (2)          | The measurement predistorts only the phase of the input waveform.          |
                +-------------------------+----------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            memory_model_correction_type = (
                memory_model_correction_type.value
                if type(memory_model_correction_type) is enums.DpdApplyDpdMemoryModelCorrectionType
                else memory_model_correction_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.dpd_configure_memory_model_correction_type(
                updated_selector_string, memory_model_correction_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def fetch_pre_cfr_papr(self, selector_string, timeout):
        r"""Fetches the PAPR of the pre-distorted waveform before CFR is applied to it.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (pre_cfr_papr, error_code):

            pre_cfr_papr (float):
                This parameter returns the PAPR of the pre-distorted waveform before CFR is applied when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. This value is expressed in dB.

                When you set the DPD Apply DPD CFR Enabled attribute to **False** and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.MODEL` attribute to **Lookup Table**, the PAPR of the pre-distorted
                waveform is returned.

                When you set the DPD Apply DPD CFR Enabled attribute to **False** and the DPD Model attribute to **Memory
                Polynomial** or **Generalized Memory Polynomial**, the PAPR of the clipped pre-distorted waveform is returned. The
                pre-distorted waveform is clipped such that its peak amplitude does not exceed the peak of the input waveform, scaled
                to DUT average input power, by 6 dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            pre_cfr_papr, error_code = self._interpreter.dpd_fetch_pre_cfr_papr(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return pre_cfr_papr, error_code

    @_raise_if_disposed
    def apply_digital_predistortion(
        self,
        selector_string,
        x0_in,
        dx_in,
        waveform_in,
        idle_duration_present,
        measurement_timeout,
        waveform_out,
    ):
        r"""Scales the input waveform to DUT average input power and then predistorts using the DPD polynomial or the lookup table.
        To scale the waveform correctly, specify if the idle duration is present in the waveform.

        Args:
            selector_string (string):
                Specifies the result name. Example: "", "result::r1".
                You can use the build_result_string method to build the selector string.

            x0_in (float):
                Specifies the start time, in seconds.

            dx_in (float):
                Specifies the sample duration, in seconds.

            waveform_in (numpy.complex64):
                Specifies the complex baseband equivalent of the RF signal on which to apply digital predistortion.

            idle_duration_present (enums.DpdApplyDpdIdleDurationPresent, int):
                Specifies whether the waveform contains an idle duration.

            measurement_timeout (float):
                Specifies the timeout, in seconds, for fetching the specified measurement.

            waveform_out (numpy.complex64):
                Upon return, contains the complex baseband equivalent of the RF signal on which to apply digital predistortion.

        Returns:
            Tuple (float, float, float, float, int):

            x0_out (float):
                Contains the start time, in seconds.

            dx_out (float):
                Contains the sample duration, in seconds.

            papr (float):
                Contains the peak-to-average power ratio of the waveform obtained after applying digital predistortion.
                This value is expressed in dB.

            power_offset (float):
                Contains the change in the average power in the waveform due to applying digital predistion.
                This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            idle_duration_present = (
                idle_duration_present.value
                if type(idle_duration_present) is enums.DpdApplyDpdIdleDurationPresent
                else idle_duration_present
            )
            x0_out, dx_out, papr, power_offset, error_code = (
                self._interpreter.dpd_apply_digital_predistortion(
                    updated_selector_string,
                    x0_in,
                    dx_in,
                    waveform_in,
                    idle_duration_present,
                    measurement_timeout,
                    waveform_out,
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0_out, dx_out, papr, power_offset, error_code
