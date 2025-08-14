"""Defines a root class which is used to identify and control SpecAn signal configuration."""

import functools
import math

import nirfmxinstr
import nirfmxspecan.acp as acp
import nirfmxspecan.ampm as ampm
import nirfmxspecan.attributes as attributes
import nirfmxspecan.ccdf as ccdf
import nirfmxspecan.chp as chp
import nirfmxspecan.dpd as dpd
import nirfmxspecan.enums as enums
import nirfmxspecan.errors as errors
import nirfmxspecan.fcnt as fcnt
import nirfmxspecan.harm as harm
import nirfmxspecan.idpd as idpd
import nirfmxspecan.im as im
import nirfmxspecan.internal._helper as _helper
import nirfmxspecan.iq as iq
import nirfmxspecan.marker as marker
import nirfmxspecan.nf as nf
import nirfmxspecan.obw as obw
import nirfmxspecan.pavt as pavt
import nirfmxspecan.phase_noise as phase_noise
import nirfmxspecan.power_list as power_list
import nirfmxspecan.sem as sem
import nirfmxspecan.spectrum as spectrum
import nirfmxspecan.spur as spur
import nirfmxspecan.txp as txp
from nirfmxspecan.internal._helper import SignalConfiguration
from nirfmxspecan.internal._library_interpreter import LibraryInterpreter


class _SpecAnSignalConfiguration:
    """Contains static methods to create and delete SpecAn signal."""

    @staticmethod
    def get_specan_signal_configuration(instr_session, signal_name="", cloning=False):
        updated_signal_name = signal_name
        if signal_name:
            updated_signal_name = _helper.validate_and_remove_signal_qualifier(
                signal_name, "signal_name"
            )
            _helper.validate_signal_not_empty(updated_signal_name, "signal_name")
        return _SpecAnSignalConfiguration.init(instr_session, updated_signal_name, cloning)  # type: ignore

    @staticmethod
    def init(instr_session, signal_name, cloning):
        with instr_session._signal_lock:
            if signal_name.lower() == SpecAn._default_signal_name_user_visible.lower():
                signal_name = SpecAn._default_signal_name

            existing_signal = instr_session._signal_manager.find_signal_configuration(
                SpecAn._signal_configuration_type, signal_name
            )
            if existing_signal is None:
                signal_configuration = SpecAn(instr_session, signal_name, cloning)  # type: ignore
                instr_session._signal_manager.add_signal_configuration(signal_configuration)
            else:
                signal_configuration = existing_signal
                # Checking if signal exists in C layer
                if signal_configuration._interpreter.check_if_current_signal_exists() is False:
                    if not signal_configuration.signal_configuration_name.lower():
                        instr_session._interpreter.create_default_signal_configuration(
                            SpecAn._default_signal_name_user_visible,
                            int(math.log(nirfmxinstr.Personalities.SPECAN.value, 2.0)) + 1,
                        )
                    else:
                        signal_configuration._interpreter.create_signal_configuration(signal_name)

            return signal_configuration

    @staticmethod
    def remove_signal_configuration(instr_session, signal_configuration):
        with instr_session._signal_lock:
            instr_session._signal_manager.remove_signal_configuration(signal_configuration)


def _raise_if_disposed(f):
    """From https://stackoverflow.com/questions/5929107/decorators-with-parameters."""

    @functools.wraps(f)
    def aux(*xs, **kws):
        signal = xs[0]  # parameter 0 is 'self' which is the signal object
        if signal.is_disposed:
            raise Exception("Cannot access a disposed SpecAn signal configuration")
        return f(*xs, **kws)

    return aux


class _SpecAnBase(SignalConfiguration):
    """Defines a base class for SpecAn."""

    _default_signal_name = ""
    _default_signal_name_user_visible = "default@SpecAn"
    _signal_configuration_type = "<'nirfmxspecan.specan.SpecAn'>"

    def __init__(self, session, signal_name="", cloning=False):
        self.is_disposed = False
        self._rfmxinstrsession = session
        self._rfmxinstrsession_interpreter = session._interpreter
        self.signal_configuration_name = signal_name
        self.signal_configuration_type = type(self)  # type: ignore
        self._signal_configuration_mode = "Signal"

        interpreter = LibraryInterpreter("windows-1251", session, self)  # type: ignore

        self._interpreter = interpreter
        self._interpreter.set_session_handle(self._rfmxinstrsession_interpreter._vi)
        self._session_function_lock = _helper.SessionFunctionLock()

        # Measurements object
        self.im = im.IM(self)  # type: ignore
        self.nf = nf.NF(self)  # type: ignore
        self.fcnt = fcnt.Fcnt(self)  # type: ignore
        self.spectrum = spectrum.Spectrum(self)  # type: ignore
        self.spur = spur.Spur(self)  # type: ignore
        self.ampm = ampm.Ampm(self)  # type: ignore
        self.dpd = dpd.Dpd(self)  # type: ignore
        self.acp = acp.Acp(self)  # type: ignore
        self.ccdf = ccdf.Ccdf(self)  # type: ignore
        self.chp = chp.Chp(self)  # type: ignore
        self.harm = harm.Harm(self)  # type: ignore
        self.marker = marker.Marker(self)  # type: ignore
        self.sem = sem.Sem(self)  # type: ignore
        self.obw = obw.Obw(self)  # type: ignore
        self.txp = txp.Txp(self)  # type: ignore
        self.iq = iq.IQ(self)  # type: ignore
        self.phase_noise = phase_noise.PhaseNoise(self)  # type: ignore
        self.pavt = pavt.Pavt(self)  # type: ignore
        self.idpd = idpd.Idpd(self)  # type: ignore
        self.power_list = power_list.PowerList(self)  # type: ignore

        if not signal_name and not cloning:
            signal_exists, personality, _ = (
                self._rfmxinstrsession_interpreter.check_if_signal_exists(
                    self._default_signal_name_user_visible
                )
            )
            if not (signal_exists and personality.value == nirfmxinstr.Personalities.SPECAN.value):
                self._rfmxinstrsession_interpreter.create_default_signal_configuration(
                    self._default_signal_name_user_visible,
                    int(math.log(nirfmxinstr.Personalities.SPECAN.value, 2.0)) + 1,
                )
        elif signal_name and not cloning:
            signal_exists, personality, _ = (
                self._rfmxinstrsession_interpreter.check_if_signal_exists(signal_name)
            )
            if not (signal_exists and personality.value == nirfmxinstr.Personalities.SPECAN.value):
                self._interpreter.create_signal_configuration(signal_name)  # type: ignore

    def __enter__(self):
        """Enters the context of the SpecAn signal configuration."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the context of the SpecAn signal configuration."""
        self.dispose()  # type: ignore
        pass

    def dispose(self):
        r"""Deletes the signal configuration if it is not the default signal configuration
        and clears any trace of the current signal configuration, if any.

        .. note::
            You can call this function safely more than once, even if the signal is already deleted.
        """
        if not self.is_disposed:
            if self.signal_configuration_name == self._default_signal_name:
                self.is_disposed = True
                return
            else:
                _ = self._delete_signal_configuration(True)  # type: ignore
                self.is_disposed = True

    @_raise_if_disposed
    def delete_signal_configuration(self):
        r"""Deletes the current instance of a signal.

        Returns:
            error_code:
                Returns the status code of this method.
                The status code either indicates success or describes a warning condition.
        """
        error_code = self._delete_signal_configuration(False)  # type: ignore
        return error_code

    def _delete_signal_configuration(self, ignore_driver_error):
        error_code = 0
        try:
            if not self.is_disposed:
                self._session_function_lock.enter_write_lock()
                error_code = self._interpreter.delete_signal_configuration(ignore_driver_error)  # type: ignore
                _SpecAnSignalConfiguration.remove_signal_configuration(self._rfmxinstrsession, self)  # type: ignore
                self.is_disposed = True
        finally:
            self._session_function_lock.exit_write_lock()

        return error_code

    @_raise_if_disposed
    def get_warning(self):
        r"""Retrieves and then clears the warning information for the session.

        Returns:
            Tuple (warning_code, warning_message):

            warning_code (int):
                Contains the latest warning code.

            warning_message (string):
                Contains the latest warning description.
        """
        try:
            self._session_function_lock.enter_read_lock()
            warning_code, warning_message = self._interpreter.get_error()
        finally:
            self._session_function_lock.exit_read_lock()

        return warning_code, warning_message

    @_raise_if_disposed
    def get_error_string(self, error_code):
        r"""Gets the description of a driver error code.

        Args:
            error_code (int):
                Specifies an error or warning code.

        Returns:
            string:
                Contains the error description.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_message = self._interpreter.get_error_string(error_code)
        finally:
            self._session_function_lock.exit_read_lock()

        return error_message

    @_raise_if_disposed
    def reset_attribute(self, selector_string, attribute_id):
        r"""Resets the attribute to its default value.

        Args:
            selector_string (string):
                Specifies the selector string for the property being reset.

            attribute_id (PropertyId):
                Specifies an attribute identifier.

        Returns:
            int:
                Returns the status code of this method.
                The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attribute_id = (
                attribute_id.value if type(attribute_id) is attributes.AttributeID else attribute_id
            )
            error_code = self._interpreter.reset_attribute(  # type: ignore
                updated_selector_string, attribute_id
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_selected_ports(self, selector_string):
        r"""Gets the instrument port to be configured to acquire a signal. Use
        :py:meth:`nirfmxinstr.session.Session.get_available_ports` method to get the valid port names.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        **Valid values**

        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)   | Description                                                                                                              |
        +================+==========================================================================================================================+
        | PXIe-5830      | if0, if1                                                                                                                 |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5831/5832 | if0, if1, rf<0-1>/port<x>, where 0-1 indicates one (0) or two (1) mmRH-5582 connections and x is the port number on the  |
        |                | mmRH-5582 front panel                                                                                                    |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Other devices  | "" (empty string)                                                                                                        |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+

        **Default values**

        +---------------------+-------------------+
        | Name (value)        | Description       |
        +=====================+===================+
        | PXIe-5830/5831/5832 | if1               |
        +---------------------+-------------------+
        | Other devices       | "" (empty string) |
        +---------------------+-------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the instrument port to be configured to acquire a signal. Use
                :py:meth:`nirfmxinstr.session.Session.get_available_ports` method to get the valid port names.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                updated_selector_string, attributes.AttributeID.SELECTED_PORTS.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_selected_ports(self, selector_string, value):
        r"""Sets the instrument port to be configured to acquire a signal. Use
        :py:meth:`nirfmxinstr.session.Session.get_available_ports` method to get the valid port names.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        **Valid values**

        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (value)   | Description                                                                                                              |
        +================+==========================================================================================================================+
        | PXIe-5830      | if0, if1                                                                                                                 |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | PXIe-5831/5832 | if0, if1, rf<0-1>/port<x>, where 0-1 indicates one (0) or two (1) mmRH-5582 connections and x is the port number on the  |
        |                | mmRH-5582 front panel                                                                                                    |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Other devices  | "" (empty string)                                                                                                        |
        +----------------+--------------------------------------------------------------------------------------------------------------------------+

        **Default values**

        +---------------------+-------------------+
        | Name (value)        | Description       |
        +=====================+===================+
        | PXIe-5830/5831/5832 | if1               |
        +---------------------+-------------------+
        | Other devices       | "" (empty string) |
        +---------------------+-------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the instrument port to be configured to acquire a signal. Use
                :py:meth:`nirfmxinstr.session.Session.get_available_ports` method to get the valid port names.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                updated_selector_string, attributes.AttributeID.SELECTED_PORTS.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_center_frequency(self, selector_string):
        r"""Gets the expected carrier frequency of the RF signal that needs to be acquired. This value is expressed in Hz. The
        signal analyzer tunes to this frequency.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the expected carrier frequency of the RF signal that needs to be acquired. This value is expressed in Hz. The
                signal analyzer tunes to this frequency.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.CENTER_FREQUENCY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_center_frequency(self, selector_string, value):
        r"""Sets the expected carrier frequency of the RF signal that needs to be acquired. This value is expressed in Hz. The
        signal analyzer tunes to this frequency.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the expected carrier frequency of the RF signal that needs to be acquired. This value is expressed in Hz. The
                signal analyzer tunes to this frequency.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.CENTER_FREQUENCY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_reference_level(self, selector_string):
        r"""Gets the reference level which represents the maximum expected power of the RF input signal. This value is
        configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the reference level which represents the maximum expected power of the RF input signal. This value is
                configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.REFERENCE_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_reference_level(self, selector_string, value):
        r"""Sets the reference level which represents the maximum expected power of the RF input signal. This value is
        configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the reference level which represents the maximum expected power of the RF input signal. This value is
                configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.REFERENCE_LEVEL.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_external_attenuation(self, selector_string):
        r"""Gets the attenuation of a switch (or cable) connected to the RF IN connector of the signal analyzer. This value is
        expressed in dB. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your
        device in the *NI RF Vector Signal Analyzers Help*.

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
                Specifies the attenuation of a switch (or cable) connected to the RF IN connector of the signal analyzer. This value is
                expressed in dB. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your
                device in the *NI RF Vector Signal Analyzers Help*.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.EXTERNAL_ATTENUATION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_external_attenuation(self, selector_string, value):
        r"""Sets the attenuation of a switch (or cable) connected to the RF IN connector of the signal analyzer. This value is
        expressed in dB. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your
        device in the *NI RF Vector Signal Analyzers Help*.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the attenuation of a switch (or cable) connected to the RF IN connector of the signal analyzer. This value is
                expressed in dB. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your
                device in the *NI RF Vector Signal Analyzers Help*.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.EXTERNAL_ATTENUATION.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_reference_level_headroom(self, selector_string):
        r"""Gets the margin RFmx adds to the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute. The
        margin avoids clipping and overflow warnings if the input signal exceeds the configured reference level.

        RFmx configures the input gain to avoid clipping and associated overflow warnings provided the instantaneous
        power of the input signal remains within the Reference Level plus the Reference Level Headroom. If you know the input
        power of the signal precisely or previously included the margin in the Reference Level, you could improve the
        signal-to-noise ratio by reducing the Reference Level Headroom.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        **Supported devices: **PXIe-5668, PXIe-5830/5831/5832/5840/5841/5842/5860.

        **Default values**

        +------------------------------------+-------------+
        | Name (value)                       | Description |
        +====================================+=============+
        | PXIe-5668                          | 6 dB        |
        +------------------------------------+-------------+
        | PXIe-5830/5831/5832/5841/5842/5860 | 1 dB        |
        +------------------------------------+-------------+
        | PXIe-5840                          | 0 dB        |
        +------------------------------------+-------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the margin RFmx adds to the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute. The
                margin avoids clipping and overflow warnings if the input signal exceeds the configured reference level.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.REFERENCE_LEVEL_HEADROOM.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_reference_level_headroom(self, selector_string, value):
        r"""Sets the margin RFmx adds to the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute. The
        margin avoids clipping and overflow warnings if the input signal exceeds the configured reference level.

        RFmx configures the input gain to avoid clipping and associated overflow warnings provided the instantaneous
        power of the input signal remains within the Reference Level plus the Reference Level Headroom. If you know the input
        power of the signal precisely or previously included the margin in the Reference Level, you could improve the
        signal-to-noise ratio by reducing the Reference Level Headroom.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        **Supported devices: **PXIe-5668, PXIe-5830/5831/5832/5840/5841/5842/5860.

        **Default values**

        +------------------------------------+-------------+
        | Name (value)                       | Description |
        +====================================+=============+
        | PXIe-5668                          | 6 dB        |
        +------------------------------------+-------------+
        | PXIe-5830/5831/5832/5841/5842/5860 | 1 dB        |
        +------------------------------------+-------------+
        | PXIe-5840                          | 0 dB        |
        +------------------------------------+-------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the margin RFmx adds to the :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL` attribute. The
                margin avoids clipping and overflow warnings if the input signal exceeds the configured reference level.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.REFERENCE_LEVEL_HEADROOM.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trigger_type(self, selector_string):
        r"""Gets the trigger type.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **None**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | None (0)          | No Reference Trigger is configured.                                                                                      |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Digital Edge (1)  | The Reference Trigger is not asserted until a digital edge is detected. The source of the digital edge is specified      |
        |                   | using the Digital Edge Source attribute.                                                                                 |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | IQ Power Edge (2) | The Reference Trigger is asserted when the signal changes past the level specified by the slope (rising or falling),     |
        |                   | which is configured using the IQ Power Edge Slope attribute.                                                             |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Software (3)      | The Reference Trigger is not asserted until a software trigger occurs.                                                   |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TriggerType):
                Specifies the trigger type.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                updated_selector_string, attributes.AttributeID.TRIGGER_TYPE.value
            )
            attr_val = enums.TriggerType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_trigger_type(self, selector_string, value):
        r"""Sets the trigger type.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **None**.

        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)      | Description                                                                                                              |
        +===================+==========================================================================================================================+
        | None (0)          | No Reference Trigger is configured.                                                                                      |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Digital Edge (1)  | The Reference Trigger is not asserted until a digital edge is detected. The source of the digital edge is specified      |
        |                   | using the Digital Edge Source attribute.                                                                                 |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | IQ Power Edge (2) | The Reference Trigger is asserted when the signal changes past the level specified by the slope (rising or falling),     |
        |                   | which is configured using the IQ Power Edge Slope attribute.                                                             |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Software (3)      | The Reference Trigger is not asserted until a software trigger occurs.                                                   |
        +-------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TriggerType, int):
                Specifies the trigger type.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            value = value.value if type(value) is enums.TriggerType else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                updated_selector_string, attributes.AttributeID.TRIGGER_TYPE.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_digital_edge_trigger_source(self, selector_string):
        r"""Gets the source terminal for the digital edge trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the source terminal for the digital edge trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                updated_selector_string, attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_digital_edge_trigger_source(self, selector_string, value):
        r"""Sets the source terminal for the digital edge trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the source terminal for the digital edge trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_digital_edge_trigger_edge(self, selector_string):
        r"""Gets the active edge for the trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Rising Edge**.

        +------------------+--------------------------------------------------------+
        | Name (Value)     | Description                                            |
        +==================+========================================================+
        | Rising Edge (0)  | The trigger asserts on the rising edge of the signal.  |
        +------------------+--------------------------------------------------------+
        | Falling Edge (1) | The trigger asserts on the falling edge of the signal. |
        +------------------+--------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.DigitalEdgeTriggerEdge):
                Specifies the active edge for the trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                updated_selector_string, attributes.AttributeID.DIGITAL_EDGE_TRIGGER_EDGE.value
            )
            attr_val = enums.DigitalEdgeTriggerEdge(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_digital_edge_trigger_edge(self, selector_string, value):
        r"""Sets the active edge for the trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Rising Edge**.

        +------------------+--------------------------------------------------------+
        | Name (Value)     | Description                                            |
        +==================+========================================================+
        | Rising Edge (0)  | The trigger asserts on the rising edge of the signal.  |
        +------------------+--------------------------------------------------------+
        | Falling Edge (1) | The trigger asserts on the falling edge of the signal. |
        +------------------+--------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.DigitalEdgeTriggerEdge, int):
                Specifies the active edge for the trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **Digital Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            value = value.value if type(value) is enums.DigitalEdgeTriggerEdge else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.DIGITAL_EDGE_TRIGGER_EDGE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iq_power_edge_trigger_source(self, selector_string):
        r"""Gets the channel from which the device monitors the trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):
                Specifies the channel from which the device monitors the trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                updated_selector_string, attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SOURCE.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iq_power_edge_trigger_source(self, selector_string, value):
        r"""Sets the channel from which the device monitors the trigger. This attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):
                Specifies the channel from which the device monitors the trigger. This attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SOURCE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iq_power_edge_trigger_level(self, selector_string):
        r"""Gets the power level at which the device triggers. This value is expressed in dB when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` attribute to **Relative** and is
        expressed in dBm when you set the IQ Power Edge Level Type attribute to **Absolute**. The device asserts the trigger
        when the signal exceeds the level specified by the value of this attribute, taking into consideration the specified
        slope. This attribute is used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`
        attribute to **IQ Power Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the power level at which the device triggers. This value is expressed in dB when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` attribute to **Relative** and is
                expressed in dBm when you set the IQ Power Edge Level Type attribute to **Absolute**. The device asserts the trigger
                when the signal exceeds the level specified by the value of this attribute, taking into consideration the specified
                slope. This attribute is used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`
                attribute to **IQ Power Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iq_power_edge_trigger_level(self, selector_string, value):
        r"""Sets the power level at which the device triggers. This value is expressed in dB when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` attribute to **Relative** and is
        expressed in dBm when you set the IQ Power Edge Level Type attribute to **Absolute**. The device asserts the trigger
        when the signal exceeds the level specified by the value of this attribute, taking into consideration the specified
        slope. This attribute is used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`
        attribute to **IQ Power Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the power level at which the device triggers. This value is expressed in dB when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE` attribute to **Relative** and is
                expressed in dBm when you set the IQ Power Edge Level Type attribute to **Absolute**. The device asserts the trigger
                when the signal exceeds the level specified by the value of this attribute, taking into consideration the specified
                slope. This attribute is used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`
                attribute to **IQ Power Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iq_power_edge_trigger_level_type(self, selector_string):
        r"""Gets the reference for the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL` attribute.
        The IQ Power Edge Level Type attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Absolute**.

        +--------------+----------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                  |
        +==============+==============================================================================================+
        | Relative (0) | The IQ Power Edge Level attribute is relative to the value of the Reference Level attribute. |
        +--------------+----------------------------------------------------------------------------------------------+
        | Absolute (1) | The IQ Power Edge Level attribute specifies the absolute power.                              |
        +--------------+----------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IQPowerEdgeTriggerLevelType):
                Specifies the reference for the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL` attribute.
                The IQ Power Edge Level Type attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE.value,
            )
            attr_val = enums.IQPowerEdgeTriggerLevelType(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iq_power_edge_trigger_level_type(self, selector_string, value):
        r"""Sets the reference for the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL` attribute.
        The IQ Power Edge Level Type attribute is used only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Absolute**.

        +--------------+----------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                  |
        +==============+==============================================================================================+
        | Relative (0) | The IQ Power Edge Level attribute is relative to the value of the Reference Level attribute. |
        +--------------+----------------------------------------------------------------------------------------------+
        | Absolute (1) | The IQ Power Edge Level attribute specifies the absolute power.                              |
        +--------------+----------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IQPowerEdgeTriggerLevelType, int):
                Specifies the reference for the :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL` attribute.
                The IQ Power Edge Level Type attribute is used only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE` attribute to **IQ Power Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            value = value.value if type(value) is enums.IQPowerEdgeTriggerLevelType else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_LEVEL_TYPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_iq_power_edge_trigger_slope(self, selector_string):
        r"""Gets whether the device asserts the trigger when the signal power is rising or when it is falling. The device
        asserts the trigger when the signal power exceeds the specified level with the slope you specify. This attribute is
        used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`  attribute to **IQ Power
        Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Rising Slope**.

        +-------------------+-------------------------------------------------------+
        | Name (Value)      | Description                                           |
        +===================+=======================================================+
        | Rising Slope (0)  | The trigger asserts when the signal power is rising.  |
        +-------------------+-------------------------------------------------------+
        | Falling Slope (1) | The trigger asserts when the signal power is falling. |
        +-------------------+-------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.IQPowerEdgeTriggerSlope):
                Specifies whether the device asserts the trigger when the signal power is rising or when it is falling. The device
                asserts the trigger when the signal power exceeds the specified level with the slope you specify. This attribute is
                used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`  attribute to **IQ Power
                Edge**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                updated_selector_string, attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE.value
            )
            attr_val = enums.IQPowerEdgeTriggerSlope(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_iq_power_edge_trigger_slope(self, selector_string, value):
        r"""Sets whether the device asserts the trigger when the signal power is rising or when it is falling. The device
        asserts the trigger when the signal power exceeds the specified level with the slope you specify. This attribute is
        used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`  attribute to **IQ Power
        Edge**.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Rising Slope**.

        +-------------------+-------------------------------------------------------+
        | Name (Value)      | Description                                           |
        +===================+=======================================================+
        | Rising Slope (0)  | The trigger asserts when the signal power is rising.  |
        +-------------------+-------------------------------------------------------+
        | Falling Slope (1) | The trigger asserts when the signal power is falling. |
        +-------------------+-------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.IQPowerEdgeTriggerSlope, int):
                Specifies whether the device asserts the trigger when the signal power is rising or when it is falling. The device
                asserts the trigger when the signal power exceeds the specified level with the slope you specify. This attribute is
                used only when you set the :py:attr:`~nirfmxspecan.attributes.AttributeID.TRIGGER_TYPE`  attribute to **IQ Power
                Edge**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            value = value.value if type(value) is enums.IQPowerEdgeTriggerSlope else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trigger_delay(self, selector_string):
        r"""Gets the trigger delay time. This value is expressed in seconds.

        If the delay is negative, the measurement acquires pre-trigger samples. If the delay is positive, the
        measurement acquires post-trigger samples.

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
                Specifies the trigger delay time. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.TRIGGER_DELAY.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_trigger_delay(self, selector_string, value):
        r"""Sets the trigger delay time. This value is expressed in seconds.

        If the delay is negative, the measurement acquires pre-trigger samples. If the delay is positive, the
        measurement acquires post-trigger samples.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the trigger delay time. This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.TRIGGER_DELAY.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trigger_minimum_quiet_time_mode(self, selector_string):
        r"""Gets whether the measurement computes the minimum quiet time used for triggering.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Manual**.

        +--------------+---------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                 |
        +==============+=============================================================================================+
        | Manual (0)   | The minimum quiet time for triggering is the value of the Trigger Min Quiet Time attribute. |
        +--------------+---------------------------------------------------------------------------------------------+
        | Auto (1)     | The measurement computes the minimum quiet time used for triggering.                        |
        +--------------+---------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.TriggerMinimumQuietTimeMode):
                Specifies whether the measurement computes the minimum quiet time used for triggering.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.TRIGGER_MINIMUM_QUIET_TIME_MODE.value,
            )
            attr_val = enums.TriggerMinimumQuietTimeMode(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_trigger_minimum_quiet_time_mode(self, selector_string, value):
        r"""Sets whether the measurement computes the minimum quiet time used for triggering.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is **Manual**.

        +--------------+---------------------------------------------------------------------------------------------+
        | Name (Value) | Description                                                                                 |
        +==============+=============================================================================================+
        | Manual (0)   | The minimum quiet time for triggering is the value of the Trigger Min Quiet Time attribute. |
        +--------------+---------------------------------------------------------------------------------------------+
        | Auto (1)     | The measurement computes the minimum quiet time used for triggering.                        |
        +--------------+---------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.TriggerMinimumQuietTimeMode, int):
                Specifies whether the measurement computes the minimum quiet time used for triggering.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            value = value.value if type(value) is enums.TriggerMinimumQuietTimeMode else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.TRIGGER_MINIMUM_QUIET_TIME_MODE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_trigger_minimum_quiet_time_duration(self, selector_string):
        r"""Gets the time duration for which the signal must be quiet before the signal analyzer arms the I/Q power edge
        trigger. This value is expressed in seconds. If you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE` attribute to **Rising Slope**, the signal
        is quiet below the trigger level.  If you set the IQ Power Edge Slope attribute to **Falling Slope**, the signal is
        quiet above the trigger level.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the time duration for which the signal must be quiet before the signal analyzer arms the I/Q power edge
                trigger. This value is expressed in seconds. If you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE` attribute to **Rising Slope**, the signal
                is quiet below the trigger level.  If you set the IQ Power Edge Slope attribute to **Falling Slope**, the signal is
                quiet above the trigger level.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.TRIGGER_MINIMUM_QUIET_TIME_DURATION.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_trigger_minimum_quiet_time_duration(self, selector_string, value):
        r"""Sets the time duration for which the signal must be quiet before the signal analyzer arms the I/Q power edge
        trigger. This value is expressed in seconds. If you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE` attribute to **Rising Slope**, the signal
        is quiet below the trigger level.  If you set the IQ Power Edge Slope attribute to **Falling Slope**, the signal is
        quiet above the trigger level.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default of this attribute is hardware dependent.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the time duration for which the signal must be quiet before the signal analyzer arms the I/Q power edge
                trigger. This value is expressed in seconds. If you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.IQ_POWER_EDGE_TRIGGER_SLOPE` attribute to **Rising Slope**, the signal
                is quiet below the trigger level.  If you set the IQ Power Edge Slope attribute to **Falling Slope**, the signal is
                quiet above the trigger level.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.TRIGGER_MINIMUM_QUIET_TIME_DURATION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_list_step_timer_duration(self, selector_string):
        r"""Gets the duration of a given list step. This value is expressed in seconds.

        You need to use a selector string to configure or read this attribute for the list step instance.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the duration of a given list step. This value is expressed in seconds.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.LIST_STEP_TIMER_DURATION.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_list_step_timer_duration(self, selector_string, value):
        r"""Sets the duration of a given list step. This value is expressed in seconds.

        You need to use a selector string to configure or read this attribute for the list step instance.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the duration of a given list step. This value is expressed in seconds.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.LIST_STEP_TIMER_DURATION.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_list_step_timer_offset(self, selector_string):
        r"""Gets the time offset from the start of the step for which the measurements are computed. This value is expressed
        in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute to **TimerEvent**.

        You need to use a selector string to configure or read this attribute for the list step instance.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the time offset from the start of the step for which the measurements are computed. This value is expressed
                in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute to **TimerEvent**.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.LIST_STEP_TIMER_OFFSET.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_list_step_timer_offset(self, selector_string, value):
        r"""Sets the time offset from the start of the step for which the measurements are computed. This value is expressed
        in seconds. This attribute is valid only when you set the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute to **TimerEvent**.

        You need to use a selector string to configure or read this attribute for the list step instance.

        The default value is 0.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the time offset from the start of the step for which the measurements are computed. This value is expressed
                in seconds. This attribute is valid only when you set the
                :py:attr:`~nirfmxspecan.attributes.AttributeID.DIGITAL_EDGE_TRIGGER_SOURCE` attribute to **TimerEvent**.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.LIST_STEP_TIMER_OFFSET.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_auto_level_initial_reference_level(self, selector_string):
        r"""Gets the initial reference level, in dBm, which the :py:meth:`auto_level` method uses to estimate the peak power
        of the input signal.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 30.

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (float):
                Specifies the initial reference level, in dBm, which the :py:meth:`auto_level` method uses to estimate the peak power
                of the input signal.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.AUTO_LEVEL_INITIAL_REFERENCE_LEVEL.value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_auto_level_initial_reference_level(self, selector_string, value):
        r"""Sets the initial reference level, in dBm, which the :py:meth:`auto_level` method uses to estimate the peak power
        of the input signal.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 30.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the initial reference level, in dBm, which the :py:meth:`auto_level` method uses to estimate the peak power
                of the input signal.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.AUTO_LEVEL_INITIAL_REFERENCE_LEVEL.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_limited_configuration_change(self, selector_string):
        r"""Gets the set of attributes that are considered by RFmx in the locked signal configuration state.

        If your test system performs the same measurement at different selected ports, multiple frequencies and/or
        power levels repeatedly, enabling this attribute will help achieve faster measurements. When you set this attribute to
        a value other than **Disabled**, the RFmx driver will use an optimized code path and skip some checks. Because RFmx
        skips some checks when you use this attribute, you need to be aware of the limitations of this feature, which are
        listed in the `limitations <www.ni.com/docs/en-US/bundle/rfmx-specan/page/limitations.html>`_ topic.

        You can also use this attribute to lock a specific instrument configuration for a signal so that every time
        that you initiate the signal, RFmx applies the RFmxInstr attributes from a locked configuration.

        NI recommends you use this attribute in conjunction with named signal configurations. Create named signal
        configurations for each measurement configuration in your test program and set this attribute to a value other than
        **Disabled** for one or more of the named signal configurations. This allows RFmx to precompute the acquisition
        settings for your measurement configurations and re-use the precomputed settings each time you initiate the
        measurement. You do not need to use this attribute if you create named signals for all the measurement configurations
        in your test program during test sequence initialization and do not change any RFInstr or personality attributes while
        testing each device under test. RFmx automatically optimizes that use case.

        Specify the named signal configuration you are setting this attribute in the selector string input.  You do not
        need to use a selector string to configure or read this attribute for the default signal instance. Refer to the
        Selector String topic for information about the string syntax for named signals.

        The default value is **Disabled**.

        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                           | Description                                                                                                              |
        +========================================+==========================================================================================================================+
        | Disabled (0)                           | This is the normal mode of RFmx operation. All configuration changes in RFmxInstr attributes or in personality           |
        |                                        | attributes will be applied during RFmx Commit.                                                                           |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | No Change (1)                          | Signal configuration and RFmxInstr configuration are locked after the first Commit or Initiate of the named signal       |
        |                                        | configuration. Any configuration change thereafter either in RFmxInstr attributes or personality attributes will not be  |
        |                                        | considered by subsequent RFmx Commits or Initiates of this signal.                                                       |
        |                                        | Use No Change if you have created named signal configurations for all measurement configurations but are setting some    |
        |                                        | RFmxInstr attributes. Refer to the Limitations of the Limited Configuration Change Property topic for more details       |
        |                                        | about the limitations of using this mode.                                                                                |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Frequency (2)                          | Signal configuration, other than center frequency, external attenuation, and RFInstr configuration, is locked after      |
        |                                        | first Commit or Initiate of the named signal configuration. Thereafter, only the Center Frequency and External           |
        |                                        | Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of this signal.         |
        |                                        | Refer to the Limitations of the Limited Configuration Change Property topic for more details about the limitations of    |
        |                                        | using this mode.                                                                                                         |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Reference Level (3)                    | Signal configuration, other than the reference level and RFInstr configuration, is locked after first Commit or          |
        |                                        | Initiate of the named signal configuration. Thereafter only the Reference Level attribute value change will be           |
        |                                        | considered by subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ     |
        |                                        | Power Edge Trigger, NI recommends that you set the IQ Power Edge Level Type to Relative so that the trigger level is     |
        |                                        | automatically adjusted as you adjust the reference level. Refer to the Limitations of the Limited Configuration Change   |
        |                                        | Property topic for more details about the limitations of using this mode.                                                |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Freq and Ref Level (4)                 | Signal configuration, other than center frequency, reference level, external attenuation, and RFInstr configuration, is  |
        |                                        | locked after first Commit or Initiate of the named signal configuration. Thereafter only Center Frequency, Reference     |
        |                                        | Level, and External Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of  |
        |                                        | this signal. If you have configured this signal to use an IQ Power Edge Trigger, NI recommends you set the IQ Power      |
        |                                        | Edge Level Type to Relative so that the trigger level is automatically adjusted as you adjust the reference level.       |
        |                                        | Refer to the Limitations of the Limited Configuration Change Property topic for more details about the limitations of    |
        |                                        | using this mode.                                                                                                         |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Selected Ports, Freq and Ref Level (5) | Signal configuration, other than Selected Ports, Center frequency, Reference level, External attenuation, and RFInstr    |
        |                                        | configuration, is locked after first Commit or Initiate of the named signal configuration. Thereafter only Selected      |
        |                                        | Ports, Center Frequency, Reference Level, and External Attenuation attribute value changes will be considered by         |
        |                                        | subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ Power Edge        |
        |                                        | Trigger, NI recommends you set the IQ Power Edge Level Type to Relative so that the trigger level is automatically       |
        |                                        | adjusted as you adjust the reference level. Refer to the Limitations of the Limited Configuration Change Property topic  |
        |                                        | for more details about the limitations of using this mode.                                                               |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (enums.LimitedConfigurationChange):
                Specifies the set of attributes that are considered by RFmx in the locked signal configuration state.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_i32(  # type: ignore
                updated_selector_string, attributes.AttributeID.LIMITED_CONFIGURATION_CHANGE.value
            )
            attr_val = enums.LimitedConfigurationChange(attr_val)
        except (KeyError, ValueError):
            raise errors.DriverTooNewError()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_limited_configuration_change(self, selector_string, value):
        r"""Sets the set of attributes that are considered by RFmx in the locked signal configuration state.

        If your test system performs the same measurement at different selected ports, multiple frequencies and/or
        power levels repeatedly, enabling this attribute will help achieve faster measurements. When you set this attribute to
        a value other than **Disabled**, the RFmx driver will use an optimized code path and skip some checks. Because RFmx
        skips some checks when you use this attribute, you need to be aware of the limitations of this feature, which are
        listed in the `limitations <www.ni.com/docs/en-US/bundle/rfmx-specan/page/limitations.html>`_ topic.

        You can also use this attribute to lock a specific instrument configuration for a signal so that every time
        that you initiate the signal, RFmx applies the RFmxInstr attributes from a locked configuration.

        NI recommends you use this attribute in conjunction with named signal configurations. Create named signal
        configurations for each measurement configuration in your test program and set this attribute to a value other than
        **Disabled** for one or more of the named signal configurations. This allows RFmx to precompute the acquisition
        settings for your measurement configurations and re-use the precomputed settings each time you initiate the
        measurement. You do not need to use this attribute if you create named signals for all the measurement configurations
        in your test program during test sequence initialization and do not change any RFInstr or personality attributes while
        testing each device under test. RFmx automatically optimizes that use case.

        Specify the named signal configuration you are setting this attribute in the selector string input.  You do not
        need to use a selector string to configure or read this attribute for the default signal instance. Refer to the
        Selector String topic for information about the string syntax for named signals.

        The default value is **Disabled**.

        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Name (Value)                           | Description                                                                                                              |
        +========================================+==========================================================================================================================+
        | Disabled (0)                           | This is the normal mode of RFmx operation. All configuration changes in RFmxInstr attributes or in personality           |
        |                                        | attributes will be applied during RFmx Commit.                                                                           |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | No Change (1)                          | Signal configuration and RFmxInstr configuration are locked after the first Commit or Initiate of the named signal       |
        |                                        | configuration. Any configuration change thereafter either in RFmxInstr attributes or personality attributes will not be  |
        |                                        | considered by subsequent RFmx Commits or Initiates of this signal.                                                       |
        |                                        | Use No Change if you have created named signal configurations for all measurement configurations but are setting some    |
        |                                        | RFmxInstr attributes. Refer to the Limitations of the Limited Configuration Change Property topic for more details       |
        |                                        | about the limitations of using this mode.                                                                                |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Frequency (2)                          | Signal configuration, other than center frequency, external attenuation, and RFInstr configuration, is locked after      |
        |                                        | first Commit or Initiate of the named signal configuration. Thereafter, only the Center Frequency and External           |
        |                                        | Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of this signal.         |
        |                                        | Refer to the Limitations of the Limited Configuration Change Property topic for more details about the limitations of    |
        |                                        | using this mode.                                                                                                         |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Reference Level (3)                    | Signal configuration, other than the reference level and RFInstr configuration, is locked after first Commit or          |
        |                                        | Initiate of the named signal configuration. Thereafter only the Reference Level attribute value change will be           |
        |                                        | considered by subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ     |
        |                                        | Power Edge Trigger, NI recommends that you set the IQ Power Edge Level Type to Relative so that the trigger level is     |
        |                                        | automatically adjusted as you adjust the reference level. Refer to the Limitations of the Limited Configuration Change   |
        |                                        | Property topic for more details about the limitations of using this mode.                                                |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Freq and Ref Level (4)                 | Signal configuration, other than center frequency, reference level, external attenuation, and RFInstr configuration, is  |
        |                                        | locked after first Commit or Initiate of the named signal configuration. Thereafter only Center Frequency, Reference     |
        |                                        | Level, and External Attenuation attribute value changes will be considered by subsequent driver Commits or Initiates of  |
        |                                        | this signal. If you have configured this signal to use an IQ Power Edge Trigger, NI recommends you set the IQ Power      |
        |                                        | Edge Level Type to Relative so that the trigger level is automatically adjusted as you adjust the reference level.       |
        |                                        | Refer to the Limitations of the Limited Configuration Change Property topic for more details about the limitations of    |
        |                                        | using this mode.                                                                                                         |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
        | Selected Ports, Freq and Ref Level (5) | Signal configuration, other than Selected Ports, Center frequency, Reference level, External attenuation, and RFInstr    |
        |                                        | configuration, is locked after first Commit or Initiate of the named signal configuration. Thereafter only Selected      |
        |                                        | Ports, Center Frequency, Reference Level, and External Attenuation attribute value changes will be considered by         |
        |                                        | subsequent driver Commits or Initiates of this signal. If you have configured this signal to use an IQ Power Edge        |
        |                                        | Trigger, NI recommends you set the IQ Power Edge Level Type to Relative so that the trigger level is automatically       |
        |                                        | adjusted as you adjust the reference level. Refer to the Limitations of the Limited Configuration Change Property topic  |
        |                                        | for more details about the limitations of using this mode.                                                               |
        +----------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

        Args:
            selector_string (string):
                Pass an empty string.

            value (enums.LimitedConfigurationChange, int):
                Specifies the set of attributes that are considered by RFmx in the locked signal configuration state.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            value = value.value if type(value) is enums.LimitedConfigurationChange else value
            error_code = self._interpreter.set_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.LIMITED_CONFIGURATION_CHANGE.value,
                value,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_selected_path(self, selector_string):
        r"""

        Args:
            selector_string (string):
                Pass an empty string.

        Returns:
            Tuple (attr_val, error_code):

            attr_val (string):

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_string(  # type: ignore
                updated_selector_string, attributes.AttributeID.SELECTED_PATH.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_selected_path(self, selector_string, value):
        r"""

        Args:
            selector_string (string):
                Pass an empty string.

            value (string):

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            _helper.validate_not_none(value, "value")
            error_code = self._interpreter.set_attribute_string(  # type: ignore
                updated_selector_string, attributes.AttributeID.SELECTED_PATH.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_result_fetch_timeout(self, selector_string):
        r"""Gets the time, in seconds, to wait before results are available in the RFmxSpecAn Attribute. Set this value to a
        time longer than expected for fetching the measurement. A value of -1 specifies that the RFmxSpecAn Attribute waits
        until the measurement is complete.

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
                Specifies the time, in seconds, to wait before results are available in the RFmxSpecAn Attribute. Set this value to a
                time longer than expected for fetching the measurement. A value of -1 specifies that the RFmxSpecAn Attribute waits
                until the measurement is complete.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            attr_val, error_code = self._interpreter.get_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.RESULT_FETCH_TIMEOUT.value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return attr_val, error_code

    @_raise_if_disposed
    def set_result_fetch_timeout(self, selector_string, value):
        r"""Sets the time, in seconds, to wait before results are available in the RFmxSpecAn Attribute. Set this value to a
        time longer than expected for fetching the measurement. A value of -1 specifies that the RFmxSpecAn Attribute waits
        until the measurement is complete.

        You do not need to use a selector string to configure or read this attribute for the default signal instance.
        Refer to the `Selector String <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ topic for
        information about the string syntax for named signals.

        The default value is 10.

        Args:
            selector_string (string):
                Pass an empty string.

            value (float):
                Specifies the time, in seconds, to wait before results are available in the RFmxSpecAn Attribute. Set this value to a
                time longer than expected for fetching the measurement. A value of -1 specifies that the RFmxSpecAn Attribute waits
                until the measurement is complete.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.set_attribute_f64(  # type: ignore
                updated_selector_string, attributes.AttributeID.RESULT_FETCH_TIMEOUT.value, value
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def abort_measurements(self, selector_string):
        r"""Stops acquisition and measurements  associated with signal instance that you specify in the  **Selector String**
        parameter, which were previously initiated by the :py:meth:`initiate` method or measurement read methods. Calling this
        method is optional, unless you want to stop a measurement before it is complete. This method executes even if there is
        an incoming error.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.abort_measurements(  # type: ignore
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def auto_level(self, selector_string, bandwidth, measurement_interval):
        r"""Examines the input signal to calculate the peak power level and sets it as the value of the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.REFERENCE_LEVEL`
        property. Use this method to help calculate an approximate setting for the reference level.

        The RFmxSpecAn Auto Level method does the following:

        - Resets the mixer level, mixer level offset and IF output power offset.

        - Sets the starting reference level to the maximum reference level supported by the device based on the current RF attenuation, mechanical attenuation and preamp enabled settings.

        - Iterates to adjust the reference level based on the input signal peak power.

        - Uses immediate triggering and restores the trigger settings back to user setting after completing execution.

        You can also specify the starting reference level using the
        :py:attr:`~nirfmxspecan.attributes.AttributeID.AUTO_LEVEL_INITIAL_REFERENCE_LEVEL`
        property.

        When using PXIe-5663, 5665, or 5668R devices, NI recommends that you set an appropriate value for mechanical
        attenuation before calling the RFmx SpecAn Auto Level method. Setting an appropriate value for mechanical attenuation
        reduces the number of times the attenuator settings are changed by this method, thus reducing wear and tear, and
        maximizing the life time of the attenuator.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            bandwidth (float):
                This parameter specifies the bandwidth, in Hz, of the signal to be analyzed. The default value is 200 kHz.

            measurement_interval (float):
                This parameter specifies the acquisition length. Use this value to compute the number of samples to acquire from the
                signal analyzer. This value is expressed in seconds. The default value is 10 ms.

                Auto Level method does not use any trigger for acquisition. It ignores the user-configured trigger attributes.
                NI recommends that you set a sufficiently high measurement interval to ensure that the acquired waveform is at least as
                long as one period of the signal.

        Returns:
            Tuple (reference_level, error_code):

            reference_level (float):
                This parameter returns the estimated peak power level of the input signal. This value is expressed in dBm for RF
                devices and as Vpk-pk for baseband devices.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            reference_level, error_code = self._interpreter.auto_level(  # type: ignore
                updated_selector_string, bandwidth, measurement_interval
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return reference_level, error_code

    @_raise_if_disposed
    def check_measurement_status(self, selector_string):
        r"""Checks the status of the measurement. Use this method to check for any errors that may occur during measurement or to
        check whether the measurement is complete and results are available.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

        Returns:
            Tuple (is_done, error_code):

            is_done (bool):
                This parameter indicates whether the measurement is complete.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            is_done, error_code = self._interpreter.check_measurement_status(  # type: ignore
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return is_done, error_code

    @_raise_if_disposed
    def clear_all_named_results(self, selector_string):
        r"""Clears all results for the signal that you specify in the **Selector String** parameter.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.clear_all_named_results(  # type: ignore
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def clear_named_result(self, selector_string):
        r"""Clears a result instance specified by the result name in the **Selector String** parameter.

        Args:
            selector_string (string):
                This parameter specifies a `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_ comprising of result
                name.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method to build the selector string.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.clear_named_result(  # type: ignore
                updated_selector_string
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def commit(self, selector_string):
        r"""Commits settings to the hardware. Calling this method is optional. RFmxSpecAn commits settings to the hardware when you
        call the :py:meth:`initiate` method or any of the measurement Read methods.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.commit(updated_selector_string)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_digital_edge_trigger(
        self, selector_string, digital_edge_source, digital_edge, trigger_delay, enable_trigger
    ):
        r"""Configures the device to wait for a digital edge trigger and then marks a reference point within the record.

        Spectral measurements are sometimes implemented with multiple acquisitions and therefore will require that
        digital triggers are sent for each acquisition. Multiple factors, including the desired span versus the realtime
        bandwidth of the hardware, affect the number of acquisitions. RFmx recommends repeating the generation until the
        measurement is completed in order to ensure that all the acquisitions are triggered.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            digital_edge_source (string):
                This parameter specifies the source terminal for the digital edge trigger. The default of this attribute is hardware
                dependent.

                +----------------------------+-----------------------------------------------------------+
                | Name (Value)               | Description                                               |
                +============================+===========================================================+
                | PFI0 (PFI0)                | The trigger is received on PFI 0.                         |
                +----------------------------+-----------------------------------------------------------+
                | PFI1 (PFI1)                | The trigger is received on PFI 1.                         |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig0 (PXI_Trig0)      | The trigger is received on PXI trigger line 0.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig1 (PXI_Trig1)      | The trigger is received on PXI trigger line 1.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig2 (PXI_Trig2)      | The trigger is received on PXI trigger line 2.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig3 (PXI_Trig3)      | The trigger is received on PXI trigger line 3.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig4 (PXI_Trig4)      | The trigger is received on PXI trigger line 4.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig5 (PXI_Trig5)      | The trigger is received on PXI trigger line 5.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig6 (PXI_Trig6)      | The trigger is received on PXI trigger line 6.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_Trig7 (PXI_Trig7)      | The trigger is received on PXI trigger line 7.            |
                +----------------------------+-----------------------------------------------------------+
                | PXI_STAR (PXI_STAR)        | The trigger is received on the PXI star trigger line.     |
                +----------------------------+-----------------------------------------------------------+
                | PXIe_DStarB (PXIe_DStarB ) | The trigger is received on the PXIe DStar B trigger line. |
                +----------------------------+-----------------------------------------------------------+
                | TimerEvent (TimerEvent)    | The trigger is received from the timer event.             |
                +----------------------------+-----------------------------------------------------------+

            digital_edge (enums.DigitalEdgeTriggerEdge, int):
                This parameter specifies the trigger edge to detect. The default value is **Rising Edge**.

                +------------------+--------------------------------------------------------+
                | Name (Value)     | Description                                            |
                +==================+========================================================+
                | Rising Edge (0)  | The trigger asserts on the rising edge of the signal.  |
                +------------------+--------------------------------------------------------+
                | Falling Edge (1) | The trigger asserts on the falling edge of the signal. |
                +------------------+--------------------------------------------------------+

            trigger_delay (float):
                This parameter specifies the trigger delay time, in seconds. The default value is 0.

            enable_trigger (bool):
                This parameter specifies whether to enable the trigger. The default value is TRUE.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(digital_edge_source, "digital_edge_source")
            digital_edge = (
                digital_edge.value
                if type(digital_edge) is enums.DigitalEdgeTriggerEdge
                else digital_edge
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_digital_edge_trigger(  # type: ignore
                updated_selector_string,
                digital_edge_source,
                digital_edge,
                trigger_delay,
                enable_trigger,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_external_attenuation(self, selector_string, external_attenuation):
        r"""Specifies the attenuation of a switch (or cable) connected to the RF IN connector of the signal analyzer.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            external_attenuation (float):
                This parameter specifies the attenuation, in dB, of a switch (or cable) connected to the RF IN connector of the signal
                analyzer. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your device in
                the* NI RF Vector Signal Analyzers Help*. The default value is 0.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_external_attenuation(  # type: ignore
                updated_selector_string, external_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_frequency(self, selector_string, center_frequency):
        r"""Configures the expected carrier frequency of the RF signal to acquire. The signal analyzer tunes to this frequency.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            center_frequency (float):
                This parameter specifies the expected carrier frequency, in Hz, of the RF signal to acquire. The signal analyzer tunes
                to this frequency. The default of this attribute is hardware dependent.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_frequency(  # type: ignore
                updated_selector_string, center_frequency
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_iq_power_edge_trigger(
        self,
        selector_string,
        iq_power_edge_trigger_source,
        iq_power_edge_trigger_level,
        iq_power_edge_slope,
        trigger_delay,
        minimum_quiet_time_mode,
        minimum_quiet_time_duration,
        enable_trigger,
    ):
        r"""Configures the device to wait for the complex power of the I/Q data to cross the specified threshold and then marks a
        reference point within the record.

        To trigger on bursty signals, specify a minimum quiet time, which ensures that the trigger does not occur in the
        middle of the burst signal. The quiet time must be set to a value smaller than the time between bursts, but large
        enough to ignore power changes within a burst.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            iq_power_edge_trigger_source (string):
                This parameter specifies the channel from which the device monitors the trigger. The default of this attribute is
                hardware dependent.

            iq_power_edge_trigger_level (float):
                This parameter specifies the power level at which the device triggers. This value is expressed in dB when you set the
                **IQ Power Edge Level Type** parameter to **Relative** and is expressed in dBm when you set the **IQ Power Edge Level
                Type** parameter to **Absolute**. The device asserts the trigger when the signal exceeds the level specified by the
                value of this parameter, taking into consideration the specified slope. The default of this attribute is hardware
                dependent.

            iq_power_edge_slope (enums.IQPowerEdgeTriggerSlope, int):
                This parameter specifies whether the device asserts the trigger when the signal power is rising or when it is falling.
                The device asserts the trigger when the signal power exceeds the specified level with the slope you specify. The
                default value is **Rising Slope**.

                +-------------------+-------------------------------------------------------+
                | Name (Value)      | Description                                           |
                +===================+=======================================================+
                | Rising Slope (0)  | The trigger asserts when the signal power is rising.  |
                +-------------------+-------------------------------------------------------+
                | Falling Slope (1) | The trigger asserts when the signal power is falling. |
                +-------------------+-------------------------------------------------------+

            trigger_delay (float):
                This parameter specifies the trigger delay time, in seconds. The default value is 0.

            minimum_quiet_time_mode (enums.TriggerMinimumQuietTimeMode, int):
                This parameter specifies whether the measurement computes the minimum quiet time used for triggering. The default value
                is **Manual**.

                +--------------+------------------------------------------------------------------------------------------+
                | Name (Value) | Description                                                                              |
                +==============+==========================================================================================+
                | Manual (0)   | The minimum quiet time used for triggering is the value of the Min Quiet Time parameter. |
                +--------------+------------------------------------------------------------------------------------------+
                | Auto (1)     | The measurement computes the minimum quiet time used for triggering.                     |
                +--------------+------------------------------------------------------------------------------------------+

            minimum_quiet_time_duration (float):
                This parameter specifies the duration, in seconds, for which the signal must be quiet before the signal analyzer arms
                the I/Q Power Edge trigger. If you set the **IQ Power Edge Slope** parameter to **Rising Slope**, the signal is quiet
                when it is below the trigger level. If you set the **IQ Power Edge Slope** parameter to **Falling Slope**, the signal
                is quiet when it is above the trigger level. The default of this attribute is hardware dependent.

            enable_trigger (bool):
                This parameter specifies whether to enable the trigger. The default value is TRUE.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(iq_power_edge_trigger_source, "iq_power_edge_trigger_source")
            iq_power_edge_slope = (
                iq_power_edge_slope.value
                if type(iq_power_edge_slope) is enums.IQPowerEdgeTriggerSlope
                else iq_power_edge_slope
            )
            minimum_quiet_time_mode = (
                minimum_quiet_time_mode.value
                if type(minimum_quiet_time_mode) is enums.TriggerMinimumQuietTimeMode
                else minimum_quiet_time_mode
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_iq_power_edge_trigger(  # type: ignore
                updated_selector_string,
                iq_power_edge_trigger_source,
                iq_power_edge_trigger_level,
                iq_power_edge_slope,
                trigger_delay,
                minimum_quiet_time_mode,
                minimum_quiet_time_duration,
                enable_trigger,
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_reference_level(self, selector_string, reference_level):
        r"""Configures the reference level, which represents the maximum expected power of an RF input signal.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            reference_level (float):
                This parameter specifies the reference level which represents the maximum expected power of an RF input signal. This
                value is configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices. The default of this attribute
                is hardware dependent.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_reference_level(  # type: ignore
                updated_selector_string, reference_level
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_rf(
        self, selector_string, center_frequency, reference_level, external_attenuation
    ):
        r"""Configures the RF attributes of the signal specified by the selector string.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            center_frequency (float):
                This parameter specifies the expected carrier frequency, in Hz, of the RF signal to acquire. The signal analyzer tunes
                to this frequency. The default of this attribute is hardware dependent.

            reference_level (float):
                This parameter specifies the reference level which represents the maximum expected power of an RF input signal. This
                value is configured in dBm for RF devices and as V\ :sub:`pk-pk`\ for baseband devices. The default of this attribute
                is hardware dependent.

            external_attenuation (float):
                This parameter specifies the attenuation, in dB, of a switch (or cable) connected to the RF IN connector of the signal
                analyzer. For more information about attenuation, refer to the Attenuation and Signal Levels topic for your device in
                the* NI RF Vector Signal Analyzers Help*. The default value is 0.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_rf(  # type: ignore
                updated_selector_string, center_frequency, reference_level, external_attenuation
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def configure_software_edge_trigger(self, selector_string, trigger_delay, enable_trigger):
        r"""Configures the device to wait for a software trigger and then marks a reference point within the record.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            trigger_delay (float):
                This parameter specifies the trigger delay time, in seconds. The default value is 0.

            enable_trigger (bool):
                This parameter specifies whether to enable the trigger. The default value is TRUE.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.configure_software_edge_trigger(  # type: ignore
                updated_selector_string, trigger_delay, enable_trigger
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def disable_trigger(self, selector_string):
        r"""Configures the device to not wait for a trigger to mark a reference point within a record. This method defines the
        signal triggering as immediate.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.disable_trigger(updated_selector_string)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def initiate(self, selector_string, result_name):
        r"""Initiates all enabled measurements. Call this method after configuring the signal and measurement. This method
        asynchronously launches measurements in the background and immediately returns to the caller program. You can fetch
        measurement results using the Fetch methods or result attributes in the attribute node. To get the status of
        measurements, use the :py:meth:`wait_for_measurement_complete` method or :py:meth:`check_measurement_status` method.

        Args:
            selector_string (string):
                This parameter specifies the signal name and result name.  The result name can either be specified through this input
                or the **Result Name** parameter. If you do
                not specify the result name in this parameter, either the result name specified by the **Result Name**  parameter  or
                the default result instance is used.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method  to build the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_.

            result_name (string):
                This parameter specifies the name to be associated with measurement results. Provide a unique name, such as "r1" to
                enable fetching of multiple measurement results and traces. This input accepts the result name with or without the
                "result::" prefix. The default value is "" (empty string), which refers to the default result instance.

                Example:

                ""

                "result::r1"

                "r1"

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(result_name, "result_name")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.initiate(  # type: ignore
                updated_selector_string, result_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def reset_to_default(self, selector_string):
        r"""Resets a signal to the default values.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.reset_to_default(updated_selector_string)  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def select_measurements(self, selector_string, measurements, enable_all_traces):
        r"""Enables all the measurements that you specify in the **Measurements** parameter and disables all other measurements.

        Args:
            selector_string (string):
                Pass and empty string.
                The signal name that is passed when creating the signal configuration is used.

            measurements (enums.MeasurementTypes, int):
                This parameter specifies the measurement to perform. You can specify one or more of the following measurements. The
                default is an empty array.

                +-----------------+------------------------------------------------+
                | Name (Value)    | Description                                    |
                +=================+================================================+
                | ACP (0)         | Enables ACP measurement.                       |
                +-----------------+------------------------------------------------+
                | CCDF (1)        | Enables CCDF measurement.                      |
                +-----------------+------------------------------------------------+
                | CHP (2)         | Enables CHP measurement.                       |
                +-----------------+------------------------------------------------+
                | FCnt (3)        | Enables FCnt measurement.                      |
                +-----------------+------------------------------------------------+
                | Harmonics (4)   | Enables harmonics measurement.                 |
                +-----------------+------------------------------------------------+
                | OBW (5)         | Enables OBW measurement.                       |
                +-----------------+------------------------------------------------+
                | SEM (6)         | Enables SEM measurement.                       |
                +-----------------+------------------------------------------------+
                | Spectrum (7)    | Enables spectrum measurement.                  |
                +-----------------+------------------------------------------------+
                | Spur (8)        | Enables spurious emissions (Spur) measurement. |
                +-----------------+------------------------------------------------+
                | TXP (9)         | Enables TXP measurement.                       |
                +-----------------+------------------------------------------------+
                | AMPM (10)       | Enables AMPM measurement.                      |
                +-----------------+------------------------------------------------+
                | DPD (11)        | Enables DPD measurement.                       |
                +-----------------+------------------------------------------------+
                | IQ (12)         | Enables I/Q measurement.                       |
                +-----------------+------------------------------------------------+
                | IM (13)         | Enables IM measurement.                        |
                +-----------------+------------------------------------------------+
                | NF (14)         | Enables NF measurement.                        |
                +-----------------+------------------------------------------------+
                | PhaseNoise (15) | Enables phase noise measurement.               |
                +-----------------+------------------------------------------------+
                | PAVT (16)       | Enables PAVT measurement.                      |
                +-----------------+------------------------------------------------+

            enable_all_traces (bool):
                This parameter specifies whether to enable all traces for the selected measurement. The default value is FALSE.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            measurements = (
                measurements.value if type(measurements) is enums.MeasurementTypes else measurements
            )
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.select_measurements(  # type: ignore
                updated_selector_string, measurements, enable_all_traces
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def wait_for_measurement_complete(self, selector_string, timeout):
        r"""Waits for the specified number for seconds for all the measurements to complete.

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
                This parameter specifies the time, in seconds, for which the method waits for the measurement to complete. A value of
                -1 specifies that the method waits until the measurement is complete.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.wait_for_measurement_complete(  # type: ignore
                updated_selector_string, timeout
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @staticmethod
    def build_result_string(result_name):
        r"""Creates selector string for use with configuration or fetch.

        Args:
            result_name (string):
                Specifies the result name for building the selector string.
                This input accepts the result name with or without the "result::" prefix.
                Example: "", "result::r1", "r1".

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(result_name, "result_name")
        return _helper.build_result_string(result_name)

    @staticmethod
    def build_carrier_string(selector_string, carrier_number):
        r"""Creates the carrier string to use as the selector string with the SEM, ACP, and CHP carrier configuration or fetch
        attributes and methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            carrier_number (int):
                This parameter specifies the carrier number for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_carrier_string(selector_string, carrier_number)  # type: ignore

    @staticmethod
    def build_harmonic_string(selector_string, harmonic_number):
        r"""Creates the selector string to use with Harmonics configuration or fetch attributes and methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            harmonic_number (int):
                This parameter specifies the harmonic number for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_harmonic_string(selector_string, harmonic_number)  # type: ignore

    @staticmethod
    def build_intermod_string(selector_string, intermod_number):
        r"""Creates the intermod string to use as the selector string with the IM configuration or fetch attributes and methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            intermod_number (int):
                This parameter specifies the intermod number for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_intermod_string(selector_string, intermod_number)  # type: ignore

    @staticmethod
    def build_marker_string(selector_string, marker_number):
        r"""Creates selector string for use with marker configuration or fetch attributes and methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            marker_number (int):
                This parameter specifies the marker number for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_marker_string(selector_string, marker_number)  # type: ignore

    @staticmethod
    def build_offset_string(selector_string, offset_number):
        r"""Creates the offset string to use as the selector string with SEM and ACP offset configuration or fetch attributes and
        methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            offset_number (int):
                This parameter specifies the offset number for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_offset_string(selector_string, offset_number)  # type: ignore

    @staticmethod
    def build_range_string(selector_string, range_number):
        r"""Creates selector string for use with spurious emissions (Spur) configuration or fetch attributes and methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            range_number (int):
                This parameter specifies the range number for building the range string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_range_string(selector_string, range_number)  # type: ignore

    @staticmethod
    def build_segment_string(selector_string, segment_number):
        r"""Creates a selector string for use with the PAVT configuration or fetch attributes and methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            segment_number (int):
                This parameter specifies the segment number for building the selector string.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_segment_string(selector_string, segment_number)  # type: ignore

    @staticmethod
    def build_spur_string(selector_string, spur_number):
        r"""Creates the selector string for use with spurious emissions (Spur) measurement results or fetch methods.

        Args:
            selector_string (string):
                Specifies the result name for building the selector string.

            spur_number (int):
                This parameter specifies the Spur number.

        Returns:
            string:
                Contains the selector string created by this method.
        """
        _helper.validate_not_none(selector_string, "selector_string")
        return _helper.build_spur_string(selector_string, spur_number)  # type: ignore

    @_raise_if_disposed
    def clone_signal_configuration(self, new_signal_name):
        r"""Creates a new instance of a signal by copying all the properties from an existing signal instance.

        Args:
            new_signal_name (string):
                This parameter specifies the name of the new signal. This parameter accepts the signal name with or without the \"signal::\" prefix.

                Example:

                \"signal::NewSigName\"

                \"NewSigName\"

        Returns:
            Tuple (cloned_signal, error_code):

            cloned_signal (specan):
                Contains a new SpecAn signal instance.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(new_signal_name, "new_signal_name")
            updated_new_signal_name = _helper.validate_and_remove_signal_qualifier(
                new_signal_name, self
            )
            cloned_signal, error_code = self._interpreter.clone_signal_configuration(  # type: ignore
                self.signal_configuration_name, updated_new_signal_name
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return cloned_signal, error_code

    @_raise_if_disposed
    def send_software_edge_trigger(self):
        r"""Sends a trigger to the device when you use the [RFmxSpecAn Configure Trigger](RFmxSpecAn_Configure_Trigger.html) function to choose a software version of a trigger and the device is waiting for the trigger to be sent. You can also use this function to override a hardware trigger.

        This function returns an error in the following situations:

        - You configure an invalid trigger.

        - You have not previously called the initiate function.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            error_code = self._interpreter.send_software_edge_trigger()  # type: ignore
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def get_all_named_result_names(self, selector_string):
        r"""Returns all the named result names of the signal that you specify in the Selector String parameter.

        Args:
            selector_string (string):
                Pass an empty string. The signal name that is passed when creating the signal configuration is used.

        Returns:
            Tuple (result_names, default_result_exists, error_code):

            result_names (string):
                Returns an array of result names.

            default_result_exists (bool):
                Indicates whether the default result exists.

            error_code (int):
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            result_names, default_result_exists, error_code = (
                self._interpreter.get_all_named_result_names(updated_selector_string)  # type: ignore
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return result_names, default_result_exists, error_code

    @_raise_if_disposed
    def analyze_iq_1_waveform(self, selector_string, result_name, x0, dx, iq, reset):
        r"""Performs the enabled measurements on the  I/Q complex waveform  that you specify in the **IQ** parameter. Call this
        method after you configure the signal and measurement attributes. You can fetch measurement results using the Fetch
        methods or result attributes in the attribute node.
        Use this method only if the :py:attr:`~nirfmxinstr.attribute.AttributeID.RECOMMENDED_ACQUISITION_TYPE` attribute value
        is either **IQ** or **IQ or Spectral**.

        .. note::
           Query the Recommended Acquisition Type attribute from the RFmxInstr Attribute after calling the :py:meth:`commit`
           method.

        Args:
            selector_string (string):
                This parameter specifies the signal name and result name.  The result name can either be specified through this input
                or the **Result Name** parameter. If you do
                not specify the result name in this parameter, either the result name specified by the **Result Name**  parameter  or
                the default result instance is used.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method  to build the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_.

            result_name (string):
                This parameter specifies the name to be associated with measurement results. Provide a unique name, such as "r1" to
                enable fetching of multiple measurement results and traces. This input accepts the result name with or without the
                "result::" prefix. The default value is "" (empty string), which refers to the default result instance.

                Example:

                ""

                "result::r1"

                "r1"

            x0 (float):
                This parameter specifies the start time of the input **y** array. This value is expressed in seconds.

            dx (float):
                This parameter specifies the time interval between the samples in the input **y** array. This value is expressed in
                seconds. The reciprocal of **dx** indicates the I/Q rate of the input signal.

            iq (numpy.complex64):
                This parameter specifies an array of complex-valued time domain data. The real and imaginary parts of this complex data
                array correspond to the in-phase (I) and quadrature-phase (Q) data, respectively.

            reset (bool):
                This parameter resets measurement averaging. If you enable averaging, set this parameter to TRUE for the first record
                and FALSE for the subsequent records.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(result_name, "result_name")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.analyze_iq_1_waveform(  # type: ignore
                updated_selector_string, result_name, x0, dx, iq, reset
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code

    @_raise_if_disposed
    def analyze_spectrum_1_waveform(self, selector_string, result_name, x0, dx, spectrum, reset):
        r"""Performs the enabled measurements on the spectrum that you specify in the **Spectrum** parameter. Call this method
        after you configure the signal and measurement attributes. You can fetch measurement results using the Fetch methods or
        result attributes in the attribute node.
        Use this method only if the :py:attr:`~nirfmxinstr.attribute.AttributeID.RECOMMENDED_ACQUISITION_TYPE` attribute value
        is either **Spectral** or **IQ or Spectral**.

        .. note::
           Query the Recommended Acquisition Type attribute from the RFmxInstr Attribute after calling the :py:meth:`commit`
           method.

        Args:
            selector_string (string):
                This parameter specifies the signal name and result name.  The result name can either be specified through this input
                or the **Result Name** parameter. If you do
                not specify the result name in this parameter, either the result name specified by the **Result Name**  parameter  or
                the default result instance is used.

                Example:

                ""

                "result::r1"

                You can use the :py:meth:`build_result_string` method  to build the `Selector String
                <https://www.ni.com/docs/en-US/bundle/rfmx/page/selector-strings-net.html>`_.

            result_name (string):
                This parameter specifies the name to be associated with measurement results. Provide a unique name, such as "r1" to
                enable fetching of multiple measurement results and traces. This input accepts the result name with or without the
                "result::" prefix. The default value is "" (empty string), which refers to the default result instance.

                Example:

                ""

                "result::r1"

                "r1"

            x0 (float):
                This parameter specifies the start frequency of the spectrum. This value is expressed in Hz.

            dx (float):
                This parameter specifies the frequency interval between data points in the spectrum.

            spectrum (numpy.float32):
                This parameter specifies the real-value power spectrum.

            reset (bool):
                This parameter resets measurement averaging. If you enable averaging, set this parameter to TRUE for the first record
                and FALSE for the subsequent records.

        Returns:
            int:
                Returns the status code of this method. The status code either indicates success or describes a warning condition.
        """
        try:
            self._session_function_lock.enter_read_lock()
            _helper.validate_not_none(selector_string, "selector_string")
            _helper.validate_not_none(result_name, "result_name")
            updated_selector_string = _helper.validate_and_update_selector_string(
                selector_string, self
            )
            error_code = self._interpreter.analyze_spectrum_1_waveform(  # type: ignore
                updated_selector_string, result_name, x0, dx, spectrum, reset
            )
        finally:
            self._session_function_lock.exit_read_lock()

        return error_code


class SpecAn(_SpecAnBase):
    """Defines a root class which is used to identify and control SpecAn signal configuration."""

    def __init__(self, session, signal_name="", cloning=False):
        """Initializes a SpecAn signal configuration."""
        super(SpecAn, self).__init__(
            session=session,
            signal_name=signal_name,
            cloning=cloning,
        )  # type: ignore

    def __enter__(self):
        """Enters the context of the SpecAn signal configuration."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the context of the SpecAn signal configuration."""
        self.dispose()  # type: ignore
        pass
