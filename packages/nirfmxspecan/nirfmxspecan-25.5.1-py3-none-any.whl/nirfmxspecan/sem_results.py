"""Provides methods to fetch and read the Sem measurement results."""

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


class SemResults(object):
    """Provides methods to fetch and read the Sem measurement results."""

    def __init__(self, signal_obj):
        """Provides methods to fetch and read the Sem measurement results."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_total_carrier_power(self, selector_string):
        r"""Gets the total integrated power, in dBm, of all the enabled carriers measured when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. Returns the power spectral density,
        in dBm/Hz, when you set the SEM Power Units attribute to **dBm/Hz**.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the total integrated power, in dBm, of all the enabled carriers measured when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**. Returns the power spectral density,
                in dBm/Hz, when you set the SEM Power Units attribute to **dBm/Hz**.

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
                attributes.AttributeID.SEM_RESULTS_TOTAL_CARRIER_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_composite_measurement_status(self, selector_string):
        r"""Indicates the overall measurement status based on the measurement limits and the fail criteria that you set in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute for each offset segment.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        +--------------+--------------------------------------------+
        | Name (Value) | Description                                |
        +==============+============================================+
        | Fail (0)     | Indicates that the measurement has failed. |
        +--------------+--------------------------------------------+
        | Pass (1)     | Indicates that the measurement has passed. |
        +--------------+--------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemCompositeMeasurementStatus):
                Indicates the overall measurement status based on the measurement limits and the fail criteria that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute for each offset segment.

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
                attributes.AttributeID.SEM_RESULTS_COMPOSITE_MEASUREMENT_STATUS.value,
            )
            attr_val = enums.SemCompositeMeasurementStatus(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_frequency_resolution(self, selector_string):
        r"""Gets the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.

        You do not need to use a selector string to read this result for default signal and result instance. Refer to
        the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals and results.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency bin spacing of the spectrum acquired by the measurement. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_FREQUENCY_RESOLUTION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_total_relative_power(self, selector_string):
        r"""Gets the carrier power relative to the total carrier power of all enabled carriers. This value is expressed in dB.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the carrier power relative to the total carrier power of all enabled carriers. This value is expressed in dB.

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
                attributes.AttributeID.SEM_RESULTS_CARRIER_TOTAL_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_absolute_power(self, selector_string):
        r"""Gets the carrier power.

        The carrier power is reported in dBm when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the SEM
        Power Units attribute to **dBm/Hz**.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the carrier power.

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
                attributes.AttributeID.SEM_RESULTS_CARRIER_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_peak_absolute_power(self, selector_string):
        r"""Gets the peak power in the carrier channel.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power in the carrier channel.

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
                attributes.AttributeID.SEM_RESULTS_CARRIER_PEAK_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_peak_frequency(self, selector_string):
        r"""Gets the frequency at which the peak power occurs in the carrier channel. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency at which the peak power occurs in the carrier channel. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_CARRIER_PEAK_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_frequency(self, selector_string):
        r"""Gets the center frequency of the carrier relative to the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the center frequency of the carrier relative to the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.CENTER_FREQUENCY` attribute. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.SEM_RESULTS_CARRIER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_carrier_integration_bandwidth(self, selector_string):
        r"""Gets the frequency range, over which the measurement integrates the carrier power. This value is expressed in Hz.

        Use "carrier<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency range, over which the measurement integrates the carrier power. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_CARRIER_INTEGRATION_BANDWIDTH.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_measurement_status(self, selector_string):
        r"""Indicates the lower offset segment measurement status based on measurement limits and the fail criteria that you
        specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        +--------------+--------------------------------------------+
        | Name (Value) | Description                                |
        +==============+============================================+
        | Fail (0)     | Indicates that the measurement has failed. |
        +--------------+--------------------------------------------+
        | Pass (1)     | Indicates that the measurement has passed. |
        +--------------+--------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemLowerOffsetMeasurementStatus):
                Indicates the lower offset segment measurement status based on measurement limits and the fail criteria that you
                specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_MEASUREMENT_STATUS.value,
            )
            attr_val = enums.SemLowerOffsetMeasurementStatus(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_total_absolute_power(self, selector_string):
        r"""Gets the power measured in the lower (negative) offset segment.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power measured in the lower (negative) offset segment.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_TOTAL_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_total_relative_power(self, selector_string):
        r"""Gets the power measured in the lower (negative) offset segment relative to either the integrated or peak power of
        the reference carrier.

        When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
        the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
        **Peak**, the reference carrier power is the peak power in the reference carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power measured in the lower (negative) offset segment relative to either the integrated or peak power of
                the reference carrier.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_TOTAL_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_peak_absolute_power(self, selector_string):
        r"""Gets the peak power measured in the lower (negative) offset segment.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured in the lower (negative) offset segment.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_PEAK_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_peak_relative_power(self, selector_string):
        r"""Gets the peak power measured in the lower (negative) offset segment relative to the integrated or peak power of the
        reference carrier.

        When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
        the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
        **Peak**, the reference carrier power is the peak power in the reference carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured in the lower (negative) offset segment relative to the integrated or peak power of the
                reference carrier.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_PEAK_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_peak_frequency(self, selector_string):
        r"""Gets the frequency at which the peak power occurred in the lower offset segment. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency at which the peak power occurred in the lower offset segment. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_PEAK_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_margin(self, selector_string):
        r"""Gets the margin from the limit mask value that you set in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. This value is expressed in dB. Margin
        is defined as the maximum difference between the spectrum and the limit mask.

        When you set the SEM Offset Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
        absolute limit mask.

        When you set the SEM Offset Limit Fail Mask attribute to **Relative**, the margin is with reference to the
        relative limit mask.

        When you set the SEM Offset Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
        margins referenced to the absolute and relative limit masks.

        When you set the SEM Offset Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
        margins referenced to the absolute and relative limit masks.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the margin from the limit mask value that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. This value is expressed in dB. Margin
                is defined as the maximum difference between the spectrum and the limit mask.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_MARGIN.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_margin_absolute_power(self, selector_string):
        r"""Gets the power, at which the margin occurred in the lower (negative) offset segment.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power, at which the margin occurred in the lower (negative) offset segment.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_MARGIN_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_margin_relative_power(self, selector_string):
        r"""Gets the power at which the margin occurred in the lower (negative) offset segment relative to the integrated or
        peak power of the reference carrier. This value is expressed in dB.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power at which the margin occurred in the lower (negative) offset segment relative to the integrated or
                peak power of the reference carrier. This value is expressed in dB.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_MARGIN_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_margin_frequency(self, selector_string):
        r"""Gets the frequency at which the margin occurred in the lower (negative) offset segment. This value is expressed in
        Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency at which the margin occurred in the lower (negative) offset segment. This value is expressed in
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
                updated_selector_string,
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_MARGIN_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_start_frequency(self, selector_string):
        r"""Gets the start frequency of the lower (negative) offset segment. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the start frequency of the lower (negative) offset segment. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_START_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_stop_frequency(self, selector_string):
        r"""Gets the stop frequency of the lower (negative) offset segment. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the stop frequency of the lower (negative) offset segment. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_STOP_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_lower_offset_power_reference_carrier(self, selector_string):
        r"""Gets the index of the carrier that was used as the power reference to define the lower (negative) offset segment
        relative power. The reference carrier is the carrier that has an offset closest to the offset segment.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the index of the carrier that was used as the power reference to define the lower (negative) offset segment
                relative power. The reference carrier is the carrier that has an offset closest to the offset segment.

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
                attributes.AttributeID.SEM_RESULTS_LOWER_OFFSET_POWER_REFERENCE_CARRIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_measurement_status(self, selector_string):
        r"""Indicates the upper offset measurement status based on measurement limits and the fail criteria that you specify in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        +--------------+--------------------------------------------+
        | Name (Value) | Description                                |
        +==============+============================================+
        | Fail (0)     | Indicates that the measurement has failed. |
        +--------------+--------------------------------------------+
        | Pass (1)     | Indicates that the measurement has passed. |
        +--------------+--------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.SemUpperOffsetMeasurementStatus):
                Indicates the upper offset measurement status based on measurement limits and the fail criteria that you specify in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_MEASUREMENT_STATUS.value,
            )
            attr_val = enums.SemUpperOffsetMeasurementStatus(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_total_absolute_power(self, selector_string):
        r"""Gets the offset segment power measured in the upper (positive) offset segment.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the offset segment power measured in the upper (positive) offset segment.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_TOTAL_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_total_relative_power(self, selector_string):
        r"""Gets the power measured in the upper (positive) offset segment relative to the integrated or peak power of the
        reference carrier.

        When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
        the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
        **Peak**, the reference carrier power is the peak power in the reference.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power measured in the upper (positive) offset segment relative to the integrated or peak power of the
                reference carrier.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_TOTAL_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_peak_absolute_power(self, selector_string):
        r"""Gets the peak power measured in the upper (positive) offset segment.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured in the upper (positive) offset segment.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_PEAK_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_peak_relative_power(self, selector_string):
        r"""Gets the peak power measured in the upper (positive) offset segment relative to the integrated or peak power of the
        reference carrier.

        When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
        the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
        **Peak**, the reference carrier power is the peak power in the reference carrier.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the peak power measured in the upper (positive) offset segment relative to the integrated or peak power of the
                reference carrier.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_PEAK_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_peak_frequency(self, selector_string):
        r"""Gets the frequency at which the peak power occurred in the upper offset segment. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency at which the peak power occurred in the upper offset segment. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_PEAK_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_margin(self, selector_string):
        r"""Gets the margin from the limit mask value that you set in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. This value is expressed in dB. Margin
        is defined as the maximum difference between the spectrum and the limit mask.

        When you set the SEM Offset Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
        absolute limit mask.

        When you set the SEM Offset Limit Fail Mask attribute to **Relative**, the margin is with reference to the
        relative limit mask.

        When you set the SEM Offset Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
        margin referenced to the absolute and relative limit masks.

        When you set the SEM Offset Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
        margin referenced to the absolute and relative limit masks.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the margin from the limit mask value that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. This value is expressed in dB. Margin
                is defined as the maximum difference between the spectrum and the limit mask.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_MARGIN.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_margin_absolute_power(self, selector_string):
        r"""Gets the power, at which the margin occurred in the upper (positive) offset segment.

        The power is reported in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
        attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power, at which the margin occurred in the upper (positive) offset segment.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_MARGIN_ABSOLUTE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_margin_relative_power(self, selector_string):
        r"""Gets the power at which the margin occurred in the upper (positive) offset segment relative to the integrated or
        peak power of the reference carrier. This value is expressed in dB.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the power at which the margin occurred in the upper (positive) offset segment relative to the integrated or
                peak power of the reference carrier. This value is expressed in dB.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_MARGIN_RELATIVE_POWER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_margin_frequency(self, selector_string):
        r"""Gets the frequency at which the margin occurred in the upper (positive)  offset. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the frequency at which the margin occurred in the upper (positive)  offset. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_MARGIN_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_start_frequency(self, selector_string):
        r"""Gets the start frequency of the upper (positive) offset segment. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the start frequency of the upper (positive) offset segment. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_START_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_stop_frequency(self, selector_string):
        r"""Gets the stop frequency of the upper (positive) offset segment. This value is expressed in Hz.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Returns the stop frequency of the upper (positive) offset segment. This value is expressed in Hz.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_STOP_FREQUENCY.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def get_upper_offset_power_reference_carrier(self, selector_string):
        r"""Gets the index of the carrier that was used as the power reference to define the upper (positive) offset segment
        relative power. The reference carrier is the carrier that has an offset closest to the offset segment.

        Use "offset<*n*>" as the `Selector String
        <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ to read this result.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (int):
                Returns the index of the carrier that was used as the power reference to define the upper (positive) offset segment
                relative power. The reference carrier is the carrier that has an offset closest to the offset segment.

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
                attributes.AttributeID.SEM_RESULTS_UPPER_OFFSET_POWER_REFERENCE_CARRIER.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def fetch_absolute_mask_trace(self, selector_string, timeout, absolute_mask):
        r"""Fetches the absolute mask trace used for SEM measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            absolute_mask (numpy.float32):
                This parameter returns absolute mask used for the channel.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency of the channel. This value is expressed in Hz.

            dx (float):
                This parameter returns the frequency bin spacing. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.sem_fetch_absolute_mask_trace(
                updated_selector_string, timeout, absolute_mask
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_carrier_measurement(self, selector_string, timeout):
        r"""Returns the carrier power measurement.
        Use "carrier<*n*>" as the selector string to read results from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and carrier number.

                Example:

                "carrier0"

                "result::r1/carrier0"

                You can use the :py:meth:`build_carrier_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (absolute_power, peak_absolute_power, peak_frequency, total_relative_power, error_code):

            absolute_power (float):
                This parameter returns the carrier power. The power is measured in dBm when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to dBm, and in dBm/Hz when you set the SEM Power
                Units attribute to dBm/Hz.

            peak_absolute_power (float):
                This parameter returns the peak power in the carrier channel. The power is measured in dBm when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to dBm, and in dBm/Hz when you set the SEM Power
                Units attribute to dBm/Hz.

            peak_frequency (float):
                This parameter returns the frequency, in Hz, at which the peak power occurs in the carrier channel.

            total_relative_power (float):
                This parameter returns the carrier power, in dB, relative to the total carrier power of all enabled carriers.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                absolute_power,
                peak_absolute_power,
                peak_frequency,
                total_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_carrier_measurement(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return absolute_power, peak_absolute_power, peak_frequency, total_relative_power, error_code

    @_raise_if_disposed
    def fetch_composite_measurement_status(self, selector_string, timeout):
        r"""Indicates the overall SEM measurement status based on the measurement limits and the fail criteria that you set in the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute for each offset segment.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (composite_measurement_status, error_code):

            composite_measurement_status (enums.SemCompositeMeasurementStatus):
                This parameter indicates the overall measurement status based on the measurement limits and the fail criteria that you
                set in the SEM Offset Seg Limit Fail Mask attribute for each offset segment.

                +--------------+-----------------------------+
                | Name (Value) | Description                 |
                +==============+=============================+
                | Fail (0)     | The measurement has failed. |
                +--------------+-----------------------------+
                | Pass (1)     | The measurement has passed. |
                +--------------+-----------------------------+

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            composite_measurement_status, error_code = (
                self._interpreter.sem_fetch_composite_measurement_status(
                    updated_selector_string, timeout
                )
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return composite_measurement_status, error_code

    @_raise_if_disposed
    def fetch_frequency_resolution(self, selector_string, timeout):
        r"""Returns the frequency bin spacing, in Hz, of the spectrum acquired by the measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (frequency_resolution, error_code):

            frequency_resolution (float):
                This parameter returns the frequency bin spacing, in Hz, of the spectrum acquired by the measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            frequency_resolution, error_code = self._interpreter.sem_fetch_frequency_resolution(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return frequency_resolution, error_code

    @_raise_if_disposed
    def fetch_lower_offset_margin_array(self, selector_string, timeout):
        r"""Returns the array of measurement statuses and margins from the limit line measured in the lower offset segments.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (measurement_status, margin, margin_frequency, margin_absolute_power, margin_relative_power, error_code):

            measurement_status (enums.SemLowerOffsetMeasurementStatus):
                This parameter returns the array of lower offset measurement statuses based on measurement limits and the fail criteria
                that you specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

                +--------------+--------------------------------------------+
                | Name (Value) | Description                                |
                +==============+============================================+
                | Fail (0)     | Indicates that the measurement has failed. |
                +--------------+--------------------------------------------+
                | Pass (1)     | Indicates that the measurement has passed. |
                +--------------+--------------------------------------------+

            margin (float):
                This parameter returns the array of margins, in dB, from the limit mask value that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. Margin is defined as the maximum
                difference between the spectrum and the limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
                absolute limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Relative**, the margin is with reference to the
                relative limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
                margins referenced to the absolute and relative limit masks.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
                margins referenced to the absolute and relative limit masks.

            margin_frequency (float):
                This parameter returns the array of frequencies, in Hz, at which the margin occurred in each lower (negative) offset
                segment.

            margin_absolute_power (float):
                This parameter returns the array of powers, in dBm or dBm/Hz, at which the margin occurred in the lower (negative)
                offset segment. The power is measured in dBm when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the SEM
                Power Units attribute to **dBm/Hz**.

            margin_relative_power (float):
                This parameter returns the array of powers, in dB, at which the margin occurred in each lower (negative) offset segment
                relative to the integrated or peak power of the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                measurement_status,
                margin,
                margin_frequency,
                margin_absolute_power,
                margin_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_lower_offset_margin_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_lower_offset_margin(self, selector_string, timeout):
        r"""Returns the measurement status and margin from the limit line measured in the lower offset segment.
        Use "offset<*n*>" as the selector string to read parameters from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and offset number.

                Example:

                "offset0"

                "result::r1/offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (measurement_status, margin, margin_frequency, margin_absolute_power, margin_relative_power, error_code):

            measurement_status (enums.SemLowerOffsetMeasurementStatus):
                This parameter indicates the lower offset measurement status based on measurement limits and the fail criteria that you
                specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

                +--------------+--------------------------------------------+
                | Name (Value) | Description                                |
                +==============+============================================+
                | Fail (0)     | Indicates that the measurement has failed. |
                +--------------+--------------------------------------------+
                | Pass (1)     | Indicates that the measurement has passed. |
                +--------------+--------------------------------------------+

            margin (float):
                This parameter returns the margin, in dB, from the limit mask value that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. Margin is defined as the maximum
                difference between the spectrum and the limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
                absolute limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Relative**, the margin is with reference to the
                relative limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
                margins referenced to the absolute and relative limit masks.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
                margins referenced to the absolute and relative limit masks.

            margin_frequency (float):
                This parameter returns the frequency, in Hz, at which the margin occurred in the lower (negative) offset.

            margin_absolute_power (float):
                This parameter returns the power, in dBm or dBm/Hz, at which the margin occurred in the lower (negative) offset
                segment. The power is measured in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
                attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

            margin_relative_power (float):
                This parameter returns the power, in dB, at which the margin occurred in the lower (negative) offset segment relative
                to the integrated or peak power of the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                measurement_status,
                margin,
                margin_frequency,
                margin_absolute_power,
                margin_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_lower_offset_margin(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_lower_offset_power_array(self, selector_string, timeout):
        r"""Returns the arrays of lower offset segment power measurements.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (total_absolute_power, total_relative_power, peak_absolute_power, peak_frequency, peak_relative_power, error_code):

            total_absolute_power (float):
                This parameter returns the array of lower (negative) offset segment powers measured.

                The power is measured in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
                attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

            total_relative_power (float):
                This parameter returns the array of powers in each lower (negative) offset segment relative to the integrated or peak
                power of the reference carrier.

                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
                the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
                **Peak**, the reference carrier power is the peak power in the reference.

            peak_absolute_power (float):
                This parameter returns the array of peak powers measured in each lower (negative) offset segment. The power is measured
                in dBm when you set the SEM Power Units attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute
                to **dBm/Hz**.

            peak_frequency (float):
                This parameter returns the array of frequencies, in Hz, at which the peak power occurred in each offset segment.

            peak_relative_power (float):
                This parameter returns the array of peak powers in the lower (negative) offset segment relative to the integrated or
                peak power of the reference carrier.

                When you set the SEM Ref Type attribute to **Integration**, the reference carrier power is the total power in
                the reference carrier. When you set the SEM Ref Type attribute to **Peak**, the reference carrier power is the peak
                power in the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                total_absolute_power,
                total_relative_power,
                peak_absolute_power,
                peak_frequency,
                peak_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_lower_offset_power_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_lower_offset_power(self, selector_string, timeout):
        r"""Returns the lower offset segment power measurements.
        Use "offset<*n*>" as the selector string to read parameters from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and offset number.

                Example:

                "offset0"

                "result::r1/offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (total_absolute_power, total_relative_power, peak_absolute_power, peak_frequency, peak_relative_power, error_code):

            total_absolute_power (float):
                This parameter returns the lower (negative) offset segment power measured.

                The power is measured in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
                attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

            total_relative_power (float):
                This parameter returns the power in the lower (negative) offset segment relative to the integrated or peak power of the
                reference carrier.

                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
                the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
                **Peak**, the reference carrier power is the peak power in the reference.

            peak_absolute_power (float):
                This parameter returns the peak power measured in the lower (negative) offset segment. The power is measured in dBm
                when you set the SEM Power Units attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to
                **dBm/Hz**.

            peak_frequency (float):
                This parameter returns the frequency, in Hz, at which the peak power occurred in the offset segment.

            peak_relative_power (float):
                This parameter returns the peak power in the lower (negative) offset segment relative to the integrated or peak power
                of the reference carrier.

                When you set the SEM Ref Type attribute to **Integration**, the reference carrier power is the total power in
                the reference carrier. When you set the SEM Ref Type attribute to **Peak**, the reference carrier power is the peak
                power in the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                total_absolute_power,
                total_relative_power,
                peak_absolute_power,
                peak_frequency,
                peak_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_lower_offset_power(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_relative_mask_trace(self, selector_string, timeout, relative_mask):
        r"""Fetches the relative mask trace used for SEM measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            relative_mask (numpy.float32):
                This parameter returns relative mask used for the channel.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency of the channel. This value is expressed in Hz.

            dx (float):
                This parameter returns the frequency bin spacing. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.sem_fetch_relative_mask_trace(
                updated_selector_string, timeout, relative_mask
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_spectrum(self, selector_string, timeout, spectrum):
        r"""Fetches the spectrum used for SEM measurement.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

            spectrum (numpy.float32):
                This parameter returns the array of averaged powers measured at each frequency bin. This value is expressed in dBm.

        Returns:
            Tuple (x0, dx, error_code):

            x0 (float):
                This parameter returns the start frequency. This value is expressed in Hz.

            dx (float):
                This parameter returns the frequency bin spacing. This value is expressed in Hz.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            x0, dx, error_code = self._interpreter.sem_fetch_spectrum(
                updated_selector_string, timeout, spectrum
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return x0, dx, error_code

    @_raise_if_disposed
    def fetch_total_carrier_power(self, selector_string, timeout):
        r"""Returns the total integrated power, in dBm, of all the carriers or the power spectral density, in dBm/Hz, based on the
        value of the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (total_carrier_power, error_code):

            total_carrier_power (float):
                This parameter returns the total integrated power, in dBm, of all the active carriers measured when you set the SEM
                Power Units attribute to **dBm**. Returns the power spectral density, in dBm/Hz, when you set the SEM Power Units
                attribute to **dBm/Hz**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            total_carrier_power, error_code = self._interpreter.sem_fetch_total_carrier_power(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return total_carrier_power, error_code

    @_raise_if_disposed
    def fetch_upper_offset_margin_array(self, selector_string, timeout):
        r"""Returns the measurement status and margin from the limit line measured in the upper offset segments.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (measurement_status, margin, margin_frequency, margin_absolute_power, margin_relative_power, error_code):

            measurement_status (enums.SemUpperOffsetMeasurementStatus):
                This parameter returns the array of upper offset measurement statuses based on measurement limits and the fail criteria
                that you specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

                +--------------+--------------------------------------------+
                | Name (Value) | Description                                |
                +==============+============================================+
                | Fail (0)     | Indicates that the measurement has failed. |
                +--------------+--------------------------------------------+
                | Pass (1)     | Indicates that the measurement has passed. |
                +--------------+--------------------------------------------+

            margin (float):
                This parameter returns the array of margins, in dB, from the limit mask value that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. Margin is defined as the maximum
                difference between the spectrum and the limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
                absolute limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Relative**, the margin is with reference to the
                relative limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
                margins referenced to the absolute and relative limit masks.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
                margins referenced to the absolute and relative limit masks.

            margin_frequency (float):
                This parameter returns the array of frequencies, in Hz, at which the margin occurred in each upper (positive) offset.

            margin_absolute_power (float):
                This parameter returns the array of powers, in dBm or dBm/Hz, at which the margin occurred in each upper (positive)
                offset segment. The power is measured in dBm when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when you set the SEM
                Power Units attribute to **dBm/Hz**.

            margin_relative_power (float):
                This parameter returns the array of powers, in dB, at which the margin occurred in each upper (positive) offset segment
                relative to the integrated or peak power of the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                measurement_status,
                margin,
                margin_frequency,
                margin_absolute_power,
                margin_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_upper_offset_margin_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_upper_offset_margin(self, selector_string, timeout):
        r"""Returns the measurement status and margin from the limit line measured in the upper offset segment.
        Use "offset<*n*>" as the selector string to read parameters from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and offset number.

                Example:

                "offset0"

                "result::r1/offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (measurement_status, margin, margin_frequency, margin_absolute_power, margin_relative_power, error_code):

            measurement_status (enums.SemUpperOffsetMeasurementStatus):
                This parameter indicates the upper offset measurement status based on measurement limits and the fail criteria that you
                specify in the :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute.

                +--------------+--------------------------------------------+
                | Name (Value) | Description                                |
                +==============+============================================+
                | Fail (0)     | Indicates that the measurement has failed. |
                +--------------+--------------------------------------------+
                | Pass (1)     | Indicates that the measurement has passed. |
                +--------------+--------------------------------------------+

            margin (float):
                This parameter returns the margin, in dB, from the limit mask value that you set in the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.OFFSET_LIMIT_FAIL_MASK` attribute. Margin is defined as the maximum
                difference between the spectrum and the limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Absolute**, the margin is with reference to the
                absolute limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Relative**, the margin is with reference to the
                relative limit mask.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs AND Rel**, the margin is the maximum of the
                margins referenced to the absolute and relative limit masks.

                When you set the SEM Offset Seg Limit Fail Mask attribute to **Abs OR Rel**, the margin is the minimum of the
                margins referenced to the absolute and relative limit masks.

            margin_frequency (float):
                This parameter returns the frequency, in Hz, at which the margin occurred in the upper (positive) offset.

            margin_absolute_power (float):
                This parameter returns the power, in dBm or dBm/Hz, at which the margin occurred in the upper (positive) offset
                segment. The power is measured in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
                attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

            margin_relative_power (float):
                This parameter returns the power, in dB, at which the margin occurred in the upper (positive) offset segment relative
                to the integrated or peak power of the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                measurement_status,
                margin,
                margin_frequency,
                margin_absolute_power,
                margin_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_upper_offset_margin(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            measurement_status,
            margin,
            margin_frequency,
            margin_absolute_power,
            margin_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_upper_offset_power_array(self, selector_string, timeout):
        r"""Returns the arrays of upper offset segment power measurements.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (total_absolute_power, total_relative_power, peak_absolute_power, peak_frequency, peak_relative_power, error_code):

            total_absolute_power (float):
                This parameter returns the array of upper (positive) offset segment powers measured.

                The power is measured in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
                attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

            total_relative_power (float):
                This parameter returns the array of powers measured in each upper (positive) offset segment relative to the integrated
                or peak power of the reference carrier.

                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
                the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
                **Peak**, the reference carrier power is the peak power in the reference.

            peak_absolute_power (float):
                This parameter returns the array of peak powers measured in each upper (positive) offset segment. The power is measured
                in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz
                when you set the SEM Power Units attribute to **dBm/Hz**.

            peak_frequency (float):
                This parameter returns the array of frequencies, in Hz, at which the peak power occurred in each offset segment.

            peak_relative_power (float):
                This parameter returns the array of peak powers measured in each upper (positive) offset segment relative to the
                integrated or peak power of the reference carrier.

                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
                the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
                **Peak**, the reference carrier power is the peak power in the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                total_absolute_power,
                total_relative_power,
                peak_absolute_power,
                peak_frequency,
                peak_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_upper_offset_power_array(
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
            error_code,
        )

    @_raise_if_disposed
    def fetch_upper_offset_power(self, selector_string, timeout):
        r"""Returns the upper offset segment power measurements.
        Use "offset<*n*>" as the selector string to read parameters from this method.

        Args:
            selector_string (string):
                This parameter  specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name, and offset number.

                Example:

                "offset0"

                "result::r1/offset0"

                You can use the :py:meth:`build_offset_string` method  to build the selector string.

            timeout (float):
                This parameter specifies the timeout, in seconds, for fetching the specified measurement. Set this value to an
                appropriate time, longer than expected for fetching the measurement. A value of -1 specifies that the method waits
                until the measurement is complete. The default value is 10.

        Returns:
            Tuple (total_absolute_power, total_relative_power, peak_absolute_power, peak_frequency, peak_relative_power, error_code):

            total_absolute_power (float):
                This parameter returns the upper (positive) offset segment power measured.

                The power is measured in dBm when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS`
                attribute to **dBm**, and in dBm/Hz when you set the SEM Power Units attribute to **dBm/Hz**.

            total_relative_power (float):
                This parameter returns the power in the upper (positive) offset segment relative to the integrated or peak power of the
                reference carrier.

                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
                the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
                **Peak**, the reference carrier power is the peak power in the reference.

            peak_absolute_power (float):
                This parameter returns the peak power measured in the upper (positive) offset segment. The power is measured in dBm
                when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.POWER_UNITS` attribute to **dBm**, and in dBm/Hz when
                you set the SEM Power Units attribute to **dBm/Hz**.

            peak_frequency (float):
                This parameter returns the frequency, in Hz, at which the peak power occurred in the offset segment.

            peak_relative_power (float):
                This parameter returns the peak power in the upper (positive) offset segment relative to the integrated or peak power
                of the reference carrier.

                When you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_TYPE` attribute to **Integration**,
                the reference carrier power is the total power in the reference carrier. When you set the SEM Ref Type attribute to
                **Peak**, the reference carrier power is the peak power in the reference carrier.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            (
                total_absolute_power,
                total_relative_power,
                peak_absolute_power,
                peak_frequency,
                peak_relative_power,
                error_code,
            ) = self._interpreter.sem_fetch_upper_offset_power(updated_selector_string, timeout)
        finally:
            self._session_function_lock.exit_read_lock()

        return (
            total_absolute_power,
            total_relative_power,
            peak_absolute_power,
            peak_frequency,
            peak_relative_power,
            error_code,
        )
