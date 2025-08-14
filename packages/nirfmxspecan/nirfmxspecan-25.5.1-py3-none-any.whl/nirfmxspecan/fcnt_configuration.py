"""Provides methods to configure the Fcnt measurement."""

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


class FcntConfiguration(object):
    """Provides methods to configure the Fcnt measurement."""

    def __init__(self, signal_obj):
        """Provides methods to configure the Fcnt measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter

    @_raise_if_disposed
    def get_measurement_enabled(self, selector_string):
        r"""Gets whether to enable the FCnt measurement.

        You do not need to use a selector string to read this result for default signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (bool):
                Specifies whether to enable the FCnt measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_MEASUREMENT_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_enabled(self, selector_string, value):
        r"""Sets whether to enable the FCnt measurement.

        You do not need to use a selector string to read this result for default signal instance. Refer to the
        `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for information
        about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the FCnt measurement.

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
                attributes.AttributeID.FCNT_MEASUREMENT_ENABLED.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_measurement_interval(self, selector_string):
        r"""Gets the acquisition time for the FCnt measurement. This value is expressed in seconds.

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
                Specifies the acquisition time for the FCnt measurement. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(
                updated_selector_string, attributes.AttributeID.FCNT_MEASUREMENT_INTERVAL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_measurement_interval(self, selector_string, value):
        r"""Sets the acquisition time for the FCnt measurement. This value is expressed in seconds.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.001.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the acquisition time for the FCnt measurement. This value is expressed in seconds.

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
                attributes.AttributeID.FCNT_MEASUREMENT_INTERVAL.value,
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
                updated_selector_string, attributes.AttributeID.FCNT_RBW_FILTER_BANDWIDTH.value
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
                attributes.AttributeID.FCNT_RBW_FILTER_BANDWIDTH.value,
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

        The default value is **None**.

        +--------------+-------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                           |
        +==============+=======================================================================================================+
        | None (5)     | The measurement does not use any RBW filtering.                                                       |
        +--------------+-------------------------------------------------------------------------------------------------------+
        | Gaussian (1) | The RBW filter has a Gaussian response.                                                               |
        +--------------+-------------------------------------------------------------------------------------------------------+
        | Flat (2)     | The RBW filter has a flat response.                                                                   |
        +--------------+-------------------------------------------------------------------------------------------------------+
        | RRC (6)      | The RRC filter with the roll-off specified by FCnt RBW RRC Alpha attribute is used as the RBW filter. |
        +--------------+-------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.FcntRbwFilterType):
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
                updated_selector_string, attributes.AttributeID.FCNT_RBW_FILTER_TYPE.value
            )
            attr_val = enums.FcntRbwFilterType(attr_val)
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

        The default value is **None**.

        +--------------+-------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                           |
        +==============+=======================================================================================================+
        | None (5)     | The measurement does not use any RBW filtering.                                                       |
        +--------------+-------------------------------------------------------------------------------------------------------+
        | Gaussian (1) | The RBW filter has a Gaussian response.                                                               |
        +--------------+-------------------------------------------------------------------------------------------------------+
        | Flat (2)     | The RBW filter has a flat response.                                                                   |
        +--------------+-------------------------------------------------------------------------------------------------------+
        | RRC (6)      | The RRC filter with the roll-off specified by FCnt RBW RRC Alpha attribute is used as the RBW filter. |
        +--------------+-------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.FcntRbwFilterType, int):
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
            value = value.value if type(value) is enums.FcntRbwFilterType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_RBW_FILTER_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_rbw_filter_rrc_alpha(self, selector_string):
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
                updated_selector_string, attributes.AttributeID.FCNT_RBW_FILTER_RRC_ALPHA.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_rbw_filter_rrc_alpha(self, selector_string, value):
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
                updated_selector_string,
                attributes.AttributeID.FCNT_RBW_FILTER_RRC_ALPHA.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_enabled(self, selector_string):
        r"""Gets whether to enable thresholding of the acquired samples to be used for the FCnt measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | All samples are considered for the FCnt measurement.                                                                     |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The samples above the threshold level specified in the FCnt Threshold Level attribute are considered for the FCnt        |
        |              | measurement.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.FcntThresholdEnabled):
                Specifies whether to enable thresholding of the acquired samples to be used for the FCnt measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_THRESHOLD_ENABLED.value
            )
            attr_val = enums.FcntThresholdEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_enabled(self, selector_string, value):
        r"""Sets whether to enable thresholding of the acquired samples to be used for the FCnt measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | All samples are considered for the FCnt measurement.                                                                     |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The samples above the threshold level specified in the FCnt Threshold Level attribute are considered for the FCnt        |
        |              | measurement.                                                                                                             |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.FcntThresholdEnabled, int):
                Specifies whether to enable thresholding of the acquired samples to be used for the FCnt measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.FcntThresholdEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_THRESHOLD_ENABLED.value, value
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

            attr_val (enums.FcntThresholdType):
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
                updated_selector_string, attributes.AttributeID.FCNT_THRESHOLD_TYPE.value
            )
            attr_val = enums.FcntThresholdType(attr_val)
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

            value (enums.FcntThresholdType, int):
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
            value = value.value if type(value) is enums.FcntThresholdType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_THRESHOLD_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_threshold_level(self, selector_string):
        r"""Gets either the relative or absolute threshold power level based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

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
                updated_selector_string, attributes.AttributeID.FCNT_THRESHOLD_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_threshold_level(self, selector_string, value):
        r"""Sets either the relative or absolute threshold power level based on the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.THRESHOLD_TYPE` attribute.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

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
                updated_selector_string, attributes.AttributeID.FCNT_THRESHOLD_LEVEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_enabled(self, selector_string):
        r"""Gets whether to enable averaging for the FCnt measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The FCnt measurement uses the FCnt Averaging Count attribute as the number of acquisitions over which the FCnt           |
        |              | measurement is averaged.                                                                                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.FcntAveragingEnabled):
                Specifies whether to enable averaging for the FCnt measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_AVERAGING_ENABLED.value
            )
            attr_val = enums.FcntAveragingEnabled(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_enabled(self, selector_string, value):
        r"""Sets whether to enable averaging for the FCnt measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **False**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | False (0)    | The measurement is performed on a single acquisition.                                                                    |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | True (1)     | The FCnt measurement uses the FCnt Averaging Count attribute as the number of acquisitions over which the FCnt           |
        |              | measurement is averaged.                                                                                                 |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.FcntAveragingEnabled, int):
                Specifies whether to enable averaging for the FCnt measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.FcntAveragingEnabled else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_AVERAGING_ENABLED.value, value
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
                updated_selector_string, attributes.AttributeID.FCNT_AVERAGING_COUNT.value
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
                updated_selector_string, attributes.AttributeID.FCNT_AVERAGING_COUNT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_averaging_type(self, selector_string):
        r"""Gets the averaging type for the FCnt measurement. The averaged instantaneous signal phase difference is used for
        the measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Mean**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Mean (6)     | The mean of the instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Max (3)      | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Min (4)      | The minimum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Min Max (7)  | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement. The  |
        |              | sign of the phase difference is ignored to find the maximum instantaneous value.                                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.FcntAveragingType):
                Specifies the averaging type for the FCnt measurement. The averaged instantaneous signal phase difference is used for
                the measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_AVERAGING_TYPE.value
            )
            attr_val = enums.FcntAveragingType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_averaging_type(self, selector_string, value):
        r"""Sets the averaging type for the FCnt measurement. The averaged instantaneous signal phase difference is used for
        the measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Mean**.

        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                                              |
        +==============+==========================================================================================================================+
        | Mean (6)     | The mean of the instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.  |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Max (3)      | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Min (4)      | The minimum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+
        | Min Max (7)  | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement. The  |
        |              | sign of the phase difference is ignored to find the maximum instantaneous value.                                         |
        +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.FcntAveragingType, int):
                Specifies the averaging type for the FCnt measurement. The averaged instantaneous signal phase difference is used for
                the measurement.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            value = value.value if type(value) is enums.FcntAveragingType else value
            error_code = self._interpreter.set_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_AVERAGING_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_traces_enabled(self, selector_string):
        r"""Gets whether to enable the traces to be stored and retrieved after performing the FCnt measurement.

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
                Specifies whether to enable the traces to be stored and retrieved after performing the FCnt measurement.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(
                updated_selector_string, attributes.AttributeID.FCNT_ALL_TRACES_ENABLED.value
            )
            attr_val = bool(attr_val)
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_all_traces_enabled(self, selector_string, value):
        r"""Sets whether to enable the traces to be stored and retrieved after performing the FCnt measurement.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is FALSE.

        Args:
            selector_string (string):
                Pass an empty string.

            value (bool):
                Specifies whether to enable the traces to be stored and retrieved after performing the FCnt measurement.

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
                updated_selector_string, attributes.AttributeID.FCNT_ALL_TRACES_ENABLED.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_number_of_analysis_threads(self, selector_string):
        r"""Gets the maximum number of threads used for parallelism for FCnt measurement.

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
                Specifies the maximum number of threads used for parallelism for FCnt measurement.

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
                attributes.AttributeID.FCNT_NUMBER_OF_ANALYSIS_THREADS.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_number_of_analysis_threads(self, selector_string, value):
        r"""Sets the maximum number of threads used for parallelism for FCnt measurement.

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
                Specifies the maximum number of threads used for parallelism for FCnt measurement.

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
                attributes.AttributeID.FCNT_NUMBER_OF_ANALYSIS_THREADS.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        r"""Configures averaging for the frequency count (FCnt) measurement.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            averaging_enabled (enums.FcntAveragingEnabled, int):
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

            averaging_type (enums.FcntAveragingType, int):
                This parameter specifies the averaging type for averaging multiple acquisitions. The default value is **Mean**.

                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                                              |
                +==============+==========================================================================================================================+
                | Mean (6)     | The mean of the instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.  |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Max (3)      | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Min (4)      | The minimum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement.      |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+
                | Min Max (7)  | The maximum instantaneous signal phase difference over multiple acquisitions is used for the frequency measurement. The  |
                |              | sign of the phase difference is ignored to find the maximum instantaneous value.                                         |
                +--------------+--------------------------------------------------------------------------------------------------------------------------+

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            averaging_enabled = (
                averaging_enabled.value
                if type(averaging_enabled) is enums.FcntAveragingEnabled
                else averaging_enabled
            )
            averaging_type = (
                averaging_type.value
                if type(averaging_type) is enums.FcntAveragingType
                else averaging_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.fcnt_configure_averaging(
                updated_selector_string, averaging_enabled, averaging_count, averaging_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_measurement_interval(self, selector_string, measurement_interval):
        r"""Configures the acquisition time, in seconds, for the frequency count (FCnt) measurement.

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
            error_code = self._interpreter.fcnt_configure_measurement_interval(
                updated_selector_string, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rbw_filter(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        r"""Configures the resolution bandwidth (RBW) filter to be applied before measuring the frequency.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            rbw (float):
                This parameter specifies the bandwidth, in Hz, of the resolution bandwidth (RBW) filter used to measure the signal. The
                default value is 100 kHz.

            rbw_filter_type (enums.FcntRbwFilterType, int):
                This parameter specifies the shape of the digital RBW filter. The default value is **None**.

                +--------------+----------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                                  |
                +==============+==============================================================================================+
                | None (5)     | The measurement does not use any RBW filtering.                                              |
                +--------------+----------------------------------------------------------------------------------------------+
                | Gaussian (1) | The RBW filter has a Gaussian response.                                                      |
                +--------------+----------------------------------------------------------------------------------------------+
                | Flat (2)     | The RBW filter has a flat response.                                                          |
                +--------------+----------------------------------------------------------------------------------------------+
                | RRC (6)      | The RRC filter with the roll-off specified by RRC Alpha parameter is used as the RBW filter. |
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
                if type(rbw_filter_type) is enums.FcntRbwFilterType
                else rbw_filter_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.fcnt_configure_rbw_filter(
                updated_selector_string, rbw, rbw_filter_type, rrc_alpha
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        r"""Configures the threshold level for the samples that need to be considered for the frequency count (FCnt) measurement.
        Enable the threshold when analyzing burst signals or signals with dead time.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            threshold_enabled (enums.FcntThresholdEnabled, int):
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

            threshold_type (enums.FcntThresholdType, int):
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
                if type(threshold_enabled) is enums.FcntThresholdEnabled
                else threshold_enabled
            )
            threshold_type = (
                threshold_type.value
                if type(threshold_type) is enums.FcntThresholdType
                else threshold_type
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self._signal_obj
            )
            error_code = self._interpreter.fcnt_configure_threshold(
                updated_selector_string, threshold_enabled, threshold_level, threshold_type
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code
