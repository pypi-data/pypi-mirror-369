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


class DpdPreDpd(object):
    """"""

    def __init__(self, signal_obj):
        """"""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_cfr_enabled(self, selector_string):
        r"""Gets whether to enable the crest factor reduction (CFR) when applying pre-DPD signal conditioning.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables the CFR. The RFmxSpecAn DPD Apply Pre-DPD Signal Conditioning method returns an error when the CFR is           |
        |              | disabled.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables the CFR.                                                                                                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdPreDpdCfrEnabled):
                Specifies whether to enable the crest factor reduction (CFR) when applying pre-DPD signal conditioning.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_ENABLED.value
            )
            attr_val = enums.DpdPreDpdCfrEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_enabled(self, selector_string, value):
        r"""Sets whether to enable the crest factor reduction (CFR) when applying pre-DPD signal conditioning.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables the CFR. The RFmxSpecAn DPD Apply Pre-DPD Signal Conditioning method returns an error when the CFR is           |
        |              | disabled.                                                                                                                |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables the CFR.                                                                                                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdPreDpdCfrEnabled, int):
                Specifies whether to enable the crest factor reduction (CFR) when applying pre-DPD signal conditioning.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdPreDpdCfrEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_method(self, selector_string):
        r"""Gets the method used to perform crest factor reduction (CFR) when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
        information about CFR methods.

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

            attr_val (enums.DpdPreDpdCfrMethod):
                Specifies the method used to perform crest factor reduction (CFR) when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
                information about CFR methods.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_METHOD.value
            )
            attr_val = enums.DpdPreDpdCfrMethod(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_method(self, selector_string, value):
        r"""Sets the method used to perform crest factor reduction (CFR) when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
        information about CFR methods.

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

            value (enums.DpdPreDpdCfrMethod, int):
                Specifies the method used to perform crest factor reduction (CFR) when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
                information about CFR methods.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdPreDpdCfrMethod else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_METHOD.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_maximum_iterations(self, selector_string):
        r"""Gets the maximum number of iterations allowed to converge waveform PAPR to target PAPR, when you set the
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
                Specifies the maximum number of iterations allowed to converge waveform PAPR to target PAPR, when you set the
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
                attributes.AttributeID.DPD_PRE_DPD_CFR_MAXIMUM_ITERATIONS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_maximum_iterations(self, selector_string, value):
        r"""Sets the maximum number of iterations allowed to converge waveform PAPR to target PAPR, when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the maximum number of iterations allowed to converge waveform PAPR to target PAPR, when you set the
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
                attributes.AttributeID.DPD_PRE_DPD_CFR_MAXIMUM_ITERATIONS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_target_papr(self, selector_string):
        r"""Gets the target peak-to-average power ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. This value is expressed in dB.

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
                Specifies the target peak-to-average power ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. This value is expressed in dB.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_TARGET_PAPR.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_target_papr(self, selector_string, value):
        r"""Sets the target peak-to-average power ratio when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. This value is expressed in dB.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 8.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the target peak-to-average power ratio when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. This value is expressed in dB.

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
                attributes.AttributeID.DPD_PRE_DPD_CFR_TARGET_PAPR.value,
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

            attr_val (enums.DpdPreDpdCfrWindowType):
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
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_WINDOW_TYPE.value
            )
            attr_val = enums.DpdPreDpdCfrWindowType(attr_val)
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

            value (enums.DpdPreDpdCfrWindowType, int):
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
            value = value.value if type(value) is enums.DpdPreDpdCfrWindowType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_PRE_DPD_CFR_WINDOW_TYPE.value,
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
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_WINDOW_LENGTH.value
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
                attributes.AttributeID.DPD_PRE_DPD_CFR_WINDOW_LENGTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_shaping_factor(self, selector_string):
        r"""Gets the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
        Refer to the DPD concept topic for more information about shaping factor.

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
                Refer to the DPD concept topic for more information about shaping factor.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_SHAPING_FACTOR.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_shaping_factor(self, selector_string, value):
        r"""Sets the shaping factor to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**.
        Refer to the DPD concept topic for more information about shaping factor.

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
                Refer to the DPD concept topic for more information about shaping factor.

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
                attributes.AttributeID.DPD_PRE_DPD_CFR_SHAPING_FACTOR.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_shaping_threshold(self, selector_string):
        r"""Gets the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**. This
        value is expressed in dB. Refer to the DPD concept topic for more information about shaping threshold.

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
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**. This
                value is expressed in dB. Refer to the DPD concept topic for more information about shaping threshold.

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
                attributes.AttributeID.DPD_PRE_DPD_CFR_SHAPING_THRESHOLD.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_shaping_threshold(self, selector_string, value):
        r"""Sets the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
        attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**. This
        value is expressed in dB. Refer to the DPD concept topic for more information about shaping threshold.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is -5.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the shaping threshold to be used when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED`
                attribute to **True** and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_METHOD` attribute to **Sigmoid**. This
                value is expressed in dB. Refer to the DPD concept topic for more information about shaping threshold.

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
                attributes.AttributeID.DPD_PRE_DPD_CFR_SHAPING_THRESHOLD.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_filter_enabled(self, selector_string):
        r"""Gets whether to enable the filtering operation when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
        information about filtering.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables the filter operation when performing CFR.                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables filter operation when performing CFR. Filter operation is not supported when you set the DPD Pre-DPD CFR Method  |
        |              | attribute to Sigmoid.                                                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DpdPreDpdCfrFilterEnabled):
                Specifies whether to enable the filtering operation when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
                information about filtering.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CFR_FILTER_ENABLED.value
            )
            attr_val = enums.DpdPreDpdCfrFilterEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_filter_enabled(self, selector_string, value):
        r"""Sets whether to enable the filtering operation when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
        information about filtering.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | Disables the filter operation when performing CFR.                                                                       |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | Enables filter operation when performing CFR. Filter operation is not supported when you set the DPD Pre-DPD CFR Method  |
        |              | attribute to Sigmoid.                                                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DpdPreDpdCfrFilterEnabled, int):
                Specifies whether to enable the filtering operation when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute to **True**. Refer to DPD concept topic for more
                information about filtering.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.DpdPreDpdCfrFilterEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string,
                attributes.AttributeID.DPD_PRE_DPD_CFR_FILTER_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_cfr_number_of_carriers(self, selector_string):
        r"""Gets the number of carriers in the input waveform when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**.

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
                Specifies the number of carriers in the input waveform when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**.

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
                attributes.AttributeID.DPD_PRE_DPD_CFR_NUMBER_OF_CARRIERS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_cfr_number_of_carriers(self, selector_string, value):
        r"""Sets the number of carriers in the input waveform when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 1.

        Args:
            selector_string (string):
                Pass an empty string.

            value (int):
                Specifies the number of carriers in the input waveform when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**.

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
                attributes.AttributeID.DPD_PRE_DPD_CFR_NUMBER_OF_CARRIERS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_offset(self, selector_string):
        r"""Gets the carrier offset relative to the center of the complex baseband equivalent of the RF signal when you set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is expressed in
        Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the carrier offset relative to the center of the complex baseband equivalent of the RF signal when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is expressed in
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
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CARRIER_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_offset(self, selector_string, value):
        r"""Sets the carrier offset relative to the center of the complex baseband equivalent of the RF signal when you set
        the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is expressed in
        Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the carrier offset relative to the center of the complex baseband equivalent of the RF signal when you set
                the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute and the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is expressed in
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
                attributes.AttributeID.DPD_PRE_DPD_CARRIER_OFFSET.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_carrier_bandwidth(self, selector_string):
        r"""Gets the carrier bandwidth when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
        and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is
        expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 20 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the carrier bandwidth when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
                and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is
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
                updated_selector_string, attributes.AttributeID.DPD_PRE_DPD_CARRIER_BANDWIDTH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_carrier_bandwidth(self, selector_string, value):
        r"""Sets the carrier bandwidth when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
        and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is
        expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to configure or read this attribute.

        The default value is 20 MHz.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the carrier bandwidth when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_ENABLED` attribute
                and the :py:attr:`~nirfmxspecan.attributes.AttributeID.CFR_FILTER_ENABLED` attribute to **True**. This value is
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
                attributes.AttributeID.DPD_PRE_DPD_CARRIER_BANDWIDTH.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def apply_pre_dpd_signal_conditioning(
        self, selector_string, x0_in, dx_in, waveform_in, idle_duration_present, waveform_out
    ):
        r"""Applies crest factor reduction on the input waveform.

        Args:
            selector_string (string):
                Pass an empty string. The signal name that is passed when creating the signal configuration is used.

            x0_in (float):
                Specifies the start time, in seconds.

            dx_in (float):
                Specifies the sample duration, in seconds.

            waveform_in (numpy.complex64):
                Specifies the complex baseband equivalent of the RF signal on which the pre-DPD signal conditioning is applied.

            idle_duration_present (enums.DpdApplyDpdIdleDurationPresent, int):
                Specifies whether the waveform contains an idle duration. The default value is False.

            waveform_out (numpy.complex64):
                Upon return, contains the complex baseband equivalent of the RF signal after applying signal conditioning on the input waveform.

        Returns:
            Tuple (float, float, float, int):

            x0_out (float):
                Contains the start time, in seconds.

            dx_out (float):
                Contains the sample duration, in seconds.

            papr (float):
                Contains the peak-to-average power ratio of the waveform obtained after applying pre-DPD signal conditioning on the input waveform.
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
            x0_out, dx_out, papr, error_code = (
                self._interpreter.dpd_apply_pre_dpd_signal_conditioning(
                    updated_selector_string,
                    x0_in,
                    dx_in,
                    waveform_in,
                    idle_duration_present,
                    waveform_out,
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0_out, dx_out, papr, error_code
