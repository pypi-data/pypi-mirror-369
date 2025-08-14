"""Library C<->Python interpreter.

    This class is responsible for interpreting the Library's C API. It is responsible for:
    * Converting ctypes to native Python types.
    * Dealing with string encoding.
    * Allocating memory.
    * Converting errors returned by Library into Python exceptions.
"""

import array
import ctypes
import math
from typing import Any

import nirfmxinstr
import nirfmxspecan.attributes as attributes
import nirfmxspecan.enums as enums
import nirfmxspecan.errors as errors
import nirfmxspecan.internal._custom_types as _custom_types
import nirfmxspecan.internal._helper as _helper
import nirfmxspecan.internal._library_singleton as _library_singleton
import numpy


# Helper functions for creating ctypes needed for calling into the driver DLL
def _get_ctypes_pointer_for_buffer(
    value: Any = None, library_type: Any = None, size: Any = None
) -> Any:
    if isinstance(value, array.array):
        assert library_type is not None, "library_type is required for array.array"
        addr, _ = value.buffer_info()
        return ctypes.cast(addr, ctypes.POINTER(library_type))
    elif str(type(value)).find("'numpy.ndarray'") != -1:
        import numpy

        if "complex" in str(value.dtype):
            complex_dtype = numpy.dtype(library_type)
            structured_array = value.view(complex_dtype)
            return structured_array.ctypes.data_as(ctypes.POINTER(library_type))
        else:
            return numpy.ctypeslib.as_ctypes(value)
    elif isinstance(value, bytes):
        return ctypes.cast(value, ctypes.POINTER(library_type))  # type: ignore
    elif isinstance(value, list):
        assert library_type is not None, "library_type is required for list"
        return (library_type * len(value))(*value)
    else:
        if library_type is not None and size is not None:
            return (library_type * size)()
        else:
            return None


def _convert_to_array(value: Any, array_type: Any) -> Any:
    if value is not None:
        if isinstance(value, array.array):
            value_array = value
        else:
            value_array = array.array(array_type, value)
    else:
        value_array = None

    return value_array


class LibraryInterpreter(object):
    """Library C<->Python interpreter.

    This class is responsible for interpreting the Library's C API. It is responsible for:
    * Converting ctypes to native Python types.
    * Dealing with string encoding.
    * Allocating memory.
    * Converting errors returned by Library into Python exceptions.
    """

    _cls_encoding = "windows-1251"
    _cls_library = _library_singleton.get()

    def __init__(self, encoding, session=None, signal_obj=None):
        """Initializes the LibraryInterpreter."""
        self._encoding = encoding
        self._library = _library_singleton.get()
        self._error_message_buffer_size = 256
        self._signal_obj = signal_obj
        self._instr_session = session
        # Initialize _vi to 0 for now.
        # Session will directly update it once the driver runtime init function has been called and
        # we have a valid session handle.
        self.set_session_handle()

    def set_session_handle(self, value: Any = 0) -> None:
        """Sets the session handle."""
        self._vi = value

    def get_session_handle(self) -> Any:
        """Returns the session handle."""
        return self._vi

    def get_error_string(self, error_code: int) -> Any:
        """Returns the error message."""
        error_code_ctype = ctypes.c_int32(error_code)
        error_string_ctype = ctypes.create_string_buffer(0)
        size_or_error_code = self._library.RFmxSpecAn_GetErrorString(
            self._vi, error_code_ctype, 0, None
        )
        if size_or_error_code > 0 and error_code_ctype.value != 0:
            error_string_ctype = ctypes.create_string_buffer(size_or_error_code)
            self._library.RFmxSpecAn_GetErrorString(
                self._vi, error_code_ctype, size_or_error_code, error_string_ctype
            )
        return error_string_ctype.value

    def get_error(self) -> tuple[int, Any]:
        """Returns the error code and error message."""
        error_code_ctype = ctypes.c_int32()
        error_string_ctype = ctypes.create_string_buffer(0)
        size_or_error_code = self._library.RFmxSpecAn_GetError(self._vi, error_code_ctype, 0, None)
        if size_or_error_code > 0 and error_code_ctype.value != 0:
            error_code_ctype = ctypes.c_int32(error_code_ctype.value)
            error_string_ctype = ctypes.create_string_buffer(size_or_error_code)
            self._library.RFmxSpecAn_GetError(
                self._vi, error_code_ctype, size_or_error_code, error_string_ctype
            )
        return error_code_ctype.value, error_string_ctype.value

    def get_error_description(self, error_code: Any) -> Any:
        """Returns the error description."""
        try:
            returned_error_code, error_string = self.get_error()
            if returned_error_code == error_code:
                return error_string
        except errors.Error:
            pass

        try:
            """
            It is expected for get_error to raise when the session is invalid
            Use get_error_string instead. It doesn't require a session.
            """
            error_string = self.get_error_string(error_code)
            return error_string
        except errors.Error:
            pass
        return "Failed to retrieve error description."

    def reset_attribute(self, selector_string, attribute_id):
        """reset_attribute."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_int32(attribute_id)
        error_code = self._library.RFmxSpecAn_ResetAttribute(
            vi_ctype, selector_string_ctype, attribute_id_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def check_if_current_signal_exists(self):
        """check_if_current_signal_exists."""
        return_value = False
        if self._signal_obj is not None and not self._signal_obj.signal_configuration_name:
            signal_configuration_exists, local_personality, _ = (
                self._signal_obj._rfmxinstrsession_interpreter.check_if_signal_exists(
                    self._signal_obj._default_signal_name_user_visible
                )
            )
            return_value = signal_configuration_exists and (
                local_personality.value == nirfmxinstr.Personalities.SPECAN.value
            )
        elif self._signal_obj is not None:
            signal_configuration_exists, local_personality, _ = (
                self._signal_obj._rfmxinstrsession_interpreter.check_if_signal_exists(
                    self._signal_obj.signal_configuration_name
                )
            )
            return_value = signal_configuration_exists and (
                local_personality.value == nirfmxinstr.Personalities.SPECAN.value
            )
        return return_value

    def get_attribute_i8(self, selector_string, attribute_id):
        """get_attribute_i8."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int8()
        error_code = self._library.RFmxSpecAn_GetAttributeI8(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_i8(self, selector_string, attribute_id, attr_val):
        """set_attribute_i8."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int8(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeI8(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_i8_array(self, selector_string, attribute_id):
        """get_attribute_i8_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeI8Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.int8)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_int8
        )
        error_code = self._library.RFmxSpecAn_GetAttributeI8Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_i8_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_i8_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="i")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_int8
        )
        error_code = self._library.RFmxSpecAn_SetAttributeI8Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_i16(self, selector_string, attribute_id):
        """get_attribute_i16."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int16()
        error_code = self._library.RFmxSpecAn_GetAttributeI16(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_i16(self, selector_string, attribute_id, attr_val):
        """set_attribute_i16."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int16(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeI16(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_i32(self, selector_string, attribute_id):
        """get_attribute_i32."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeI32(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_i32(self, selector_string, attribute_id, attr_val):
        """set_attribute_i32."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int32(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeI32(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_i32_array(self, selector_string, attribute_id):
        """get_attribute_i32_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeI32Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.int32)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_int32
        )
        error_code = self._library.RFmxSpecAn_GetAttributeI32Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_i32_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_i32_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="i")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_int32
        )
        error_code = self._library.RFmxSpecAn_SetAttributeI32Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_i64(self, selector_string, attribute_id):
        """get_attribute_i64."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int64()
        error_code = self._library.RFmxSpecAn_GetAttributeI64(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_i64(self, selector_string, attribute_id, attr_val):
        """set_attribute_i64."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_int64(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeI64(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_i64_array(self, selector_string, attribute_id):
        """get_attribute_i64_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeI64Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.int64)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_int64
        )
        error_code = self._library.RFmxSpecAn_GetAttributeI64Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_i64_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_i64_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="i")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_int64
        )
        error_code = self._library.RFmxSpecAn_SetAttributeI64Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_u8(self, selector_string, attribute_id):
        """get_attribute_u8."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_uint8()
        error_code = self._library.RFmxSpecAn_GetAttributeU8(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_u8(self, selector_string, attribute_id, attr_val):
        """set_attribute_u8."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_uint8(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeU8(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_u8_array(self, selector_string, attribute_id):
        """get_attribute_u8_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeU8Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.uint8)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_uint8
        )
        error_code = self._library.RFmxSpecAn_GetAttributeU8Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_u8_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_u8_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="i")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_uint8
        )
        error_code = self._library.RFmxSpecAn_SetAttributeU8Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_u16(self, selector_string, attribute_id):
        """get_attribute_u16."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_uint16()
        error_code = self._library.RFmxSpecAn_GetAttributeU16(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_u16(self, selector_string, attribute_id, attr_val):
        """set_attribute_u16."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_uint16(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeU16(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_u32(self, selector_string, attribute_id):
        """get_attribute_u32."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_uint32()
        error_code = self._library.RFmxSpecAn_GetAttributeU32(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_u32(self, selector_string, attribute_id, attr_val):
        """set_attribute_u32."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_uint32(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeU32(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_u32_array(self, selector_string, attribute_id):
        """get_attribute_u32_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeU32Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.uint32)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_uint32
        )
        error_code = self._library.RFmxSpecAn_GetAttributeU32Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_u32_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_u32_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="i")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_uint32
        )
        error_code = self._library.RFmxSpecAn_SetAttributeU32Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_u64_array(self, selector_string, attribute_id):
        """get_attribute_u64_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeU64Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.uint64)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_uint64
        )
        error_code = self._library.RFmxSpecAn_GetAttributeU64Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_u64_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_u64_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="i")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_uint64
        )
        error_code = self._library.RFmxSpecAn_SetAttributeU64Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_f32(self, selector_string, attribute_id):
        """get_attribute_f32."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_float()
        error_code = self._library.RFmxSpecAn_GetAttributeF32(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_f32(self, selector_string, attribute_id, attr_val):
        """set_attribute_f32."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_float(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeF32(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_f32_array(self, selector_string, attribute_id):
        """get_attribute_f32_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeF32Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.float32)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_float
        )
        error_code = self._library.RFmxSpecAn_GetAttributeF32Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_f32_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_f32_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="f")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_float
        )
        error_code = self._library.RFmxSpecAn_SetAttributeF32Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_f64(self, selector_string, attribute_id):
        """get_attribute_f64."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_GetAttributeF64(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            None if attr_val_ctype is None else (ctypes.pointer(attr_val_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value, error_code

    def set_attribute_f64(self, selector_string, attribute_id, attr_val):
        """set_attribute_f64."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.c_double(attr_val)
        error_code = self._library.RFmxSpecAn_SetAttributeF64(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_f64_array(self, selector_string, attribute_id):
        """get_attribute_f64_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeF64Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.float64)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_double
        )
        error_code = self._library.RFmxSpecAn_GetAttributeF64Array(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_f64_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_f64_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="d")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_double
        )
        error_code = self._library.RFmxSpecAn_SetAttributeF64Array(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_nicomplexsingle_array(self, selector_string, attribute_id):
        """get_attribute_nicomplexsingle_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeNIComplexSingleArray(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.complex64)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_float
        )
        error_code = self._library.RFmxSpecAn_GetAttributeNIComplexSingleArray(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_nicomplexsingle_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_nicomplexsingle_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_float
        )
        error_code = self._library.RFmxSpecAn_SetAttributeNIComplexSingleArray(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_nicomplexdouble_array(self, selector_string, attribute_id):
        """get_attribute_nicomplexdouble_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = None
        array_size_ctype = ctypes.c_int32()
        actual_array_size_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_GetAttributeNIComplexDoubleArray(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            array_size_ctype,
            None if actual_array_size_ctype is None else (ctypes.pointer(actual_array_size_ctype)),
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        attr_val_array = numpy.empty(actual_array_size_ctype.value, dtype=numpy.complex128)
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_double
        )
        error_code = self._library.RFmxSpecAn_GetAttributeNIComplexDoubleArray(
            vi_ctype,
            selector_string_ctype,
            attribute_id_ctype,
            attr_val_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_array, error_code

    def set_attribute_nicomplexdouble_array(self, selector_string, attribute_id, attr_val):
        """set_attribute_nicomplexdouble_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_array = _convert_to_array(value=attr_val, array_type="")
        attr_val_ctype = _get_ctypes_pointer_for_buffer(
            value=attr_val_array, library_type=ctypes.c_double
        )
        error_code = self._library.RFmxSpecAn_SetAttributeNIComplexDoubleArray(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype, len(attr_val)
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_attribute_string(self, selector_string, attribute_id):
        """get_attribute_string."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        array_size_ctype = ctypes.c_int32(0)
        attr_val_ctype = None
        size_or_error_code = self._library.RFmxSpecAn_GetAttributeString(
            vi_ctype, selector_string_ctype, attribute_id_ctype, array_size_ctype, attr_val_ctype
        )
        if size_or_error_code < 0:
            errors.handle_error(
                self, size_or_error_code, ignore_warnings=True, is_error_handling=False
            )
            return None, size_or_error_code
        array_size_ctype = ctypes.c_int32(size_or_error_code)
        attr_val_ctype = (ctypes.c_char * array_size_ctype.value)()
        error_code = self._library.RFmxSpecAn_GetAttributeString(
            vi_ctype, selector_string_ctype, attribute_id_ctype, array_size_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return attr_val_ctype.value.decode(self._encoding), error_code

    def set_attribute_string(self, selector_string, attribute_id, attr_val):
        """set_attribute_string."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        attribute_id_ctype = ctypes.c_uint32(attribute_id)
        attr_val_ctype = ctypes.create_string_buffer(attr_val.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_SetAttributeString(
            vi_ctype, selector_string_ctype, attribute_id_ctype, attr_val_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_clear_calibration_database(self, calibration_setup_id):
        """nf_clear_calibration_database."""
        vi_ctype = ctypes.c_uint32(self._vi)
        calibration_setup_id_ctype = ctypes.create_string_buffer(
            calibration_setup_id.encode(self._encoding)
        )
        error_code = self._library.RFmxSpecAn_NFClearCalibrationDatabase(
            vi_ctype, calibration_setup_id_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_frequency_list_start_stop_points(
        self, selector_string, start_frequency, stop_frequency, number_of_points
    ):
        """nf_configure_frequency_list_start_stop_points."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        start_frequency_ctype = ctypes.c_double(start_frequency)
        stop_frequency_ctype = ctypes.c_double(stop_frequency)
        number_of_points_ctype = ctypes.c_int32(number_of_points)
        error_code = self._library.RFmxSpecAn_NFCfgFrequencyList_StartStopPoints(
            vi_ctype,
            selector_string_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
            number_of_points_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_frequency_list_start_stop_step(
        self, selector_string, start_frequency, stop_frequency, step_size
    ):
        """nf_configure_frequency_list_start_stop_step."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        start_frequency_ctype = ctypes.c_double(start_frequency)
        stop_frequency_ctype = ctypes.c_double(stop_frequency)
        step_size_ctype = ctypes.c_double(step_size)
        error_code = self._library.RFmxSpecAn_NFCfgFrequencyList_StartStopStep(
            vi_ctype,
            selector_string_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
            step_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_recommend_reference_level(self, selector_string, dut_max_gain, dut_max_noise_figure):
        """nf_recommend_reference_level."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_max_gain_ctype = ctypes.c_double(dut_max_gain)
        dut_max_noise_figure_ctype = ctypes.c_double(dut_max_noise_figure)
        reference_level_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_NFRecommendReferenceLevel(
            vi_ctype,
            selector_string_ctype,
            dut_max_gain_ctype,
            dut_max_noise_figure_ctype,
            reference_level_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return reference_level_ctype.value, error_code

    def nf_validate_calibration_data(self, selector_string):
        """nf_validate_calibration_data."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        calibration_data_valid_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_NFValidateCalibrationData(
            vi_ctype, selector_string_ctype, calibration_data_valid_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return enums.NFCalibrationDataValid(calibration_data_valid_ctype.value), error_code

    def nf_load_dut_input_loss_from_s2p(
        self,
        selector_string,
        dut_input_loss_compensation_enabled,
        dut_input_loss_s2p_file_path,
        dut_input_loss_s_parameter_orientation,
        dut_input_loss_temperature,
    ):
        """nf_load_dut_input_loss_from_s2p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_input_loss_compensation_enabled_ctype = ctypes.c_int32(
            dut_input_loss_compensation_enabled
        )
        dut_input_loss_s2p_file_path_ctype = ctypes.create_string_buffer(
            dut_input_loss_s2p_file_path.encode(self._encoding)
        )
        dut_input_loss_s_parameter_orientation_ctype = ctypes.c_int32(
            dut_input_loss_s_parameter_orientation
        )
        dut_input_loss_temperature_ctype = ctypes.c_double(dut_input_loss_temperature)
        error_code = self._library.RFmxSpecAn_NFLoadDUTInputLossFromS2p(
            vi_ctype,
            selector_string_ctype,
            dut_input_loss_compensation_enabled_ctype,
            dut_input_loss_s2p_file_path_ctype,
            dut_input_loss_s_parameter_orientation_ctype,
            dut_input_loss_temperature_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_load_dut_output_loss_from_s2p(
        self,
        selector_string,
        dut_output_loss_compensation_enabled,
        dut_output_loss_s2p_file_path,
        dut_output_loss_s_parameter_orientation,
        dut_output_loss_temperature,
    ):
        """nf_load_dut_output_loss_from_s2p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_output_loss_compensation_enabled_ctype = ctypes.c_int32(
            dut_output_loss_compensation_enabled
        )
        dut_output_loss_s2p_file_path_ctype = ctypes.create_string_buffer(
            dut_output_loss_s2p_file_path.encode(self._encoding)
        )
        dut_output_loss_s_parameter_orientation_ctype = ctypes.c_int32(
            dut_output_loss_s_parameter_orientation
        )
        dut_output_loss_temperature_ctype = ctypes.c_double(dut_output_loss_temperature)
        error_code = self._library.RFmxSpecAn_NFLoadDUTOutputLossFromS2p(
            vi_ctype,
            selector_string_ctype,
            dut_output_loss_compensation_enabled_ctype,
            dut_output_loss_s2p_file_path_ctype,
            dut_output_loss_s_parameter_orientation_ctype,
            dut_output_loss_temperature_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_load_calibration_loss_from_s2p(
        self,
        selector_string,
        calibration_loss_compensation_enabled,
        calibration_loss_s2p_file_path,
        calibration_loss_s_parameter_orientation,
        calibration_loss_temperature,
    ):
        """nf_load_calibration_loss_from_s2p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        calibration_loss_compensation_enabled_ctype = ctypes.c_int32(
            calibration_loss_compensation_enabled
        )
        calibration_loss_s2p_file_path_ctype = ctypes.create_string_buffer(
            calibration_loss_s2p_file_path.encode(self._encoding)
        )
        calibration_loss_s_parameter_orientation_ctype = ctypes.c_int32(
            calibration_loss_s_parameter_orientation
        )
        calibration_loss_temperature_ctype = ctypes.c_double(calibration_loss_temperature)
        error_code = self._library.RFmxSpecAn_NFLoadCalibrationLossFromS2p(
            vi_ctype,
            selector_string_ctype,
            calibration_loss_compensation_enabled_ctype,
            calibration_loss_s2p_file_path_ctype,
            calibration_loss_s_parameter_orientation_ctype,
            calibration_loss_temperature_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_load_cold_source_dut_s_parameter_from_s2p(
        self, selector_string, dut_s_parameters_s2p_file_path, dut_s_parameter_orientation
    ):
        """nf_load_cold_source_dut_s_parameter_from_s2p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_s_parameters_s2p_file_path_ctype = ctypes.create_string_buffer(
            dut_s_parameters_s2p_file_path.encode(self._encoding)
        )
        dut_s_parameter_orientation_ctype = ctypes.c_int32(dut_s_parameter_orientation)
        error_code = self._library.RFmxSpecAn_NFLoadColdSourceDUTSParametersFromS2p(
            vi_ctype,
            selector_string_ctype,
            dut_s_parameters_s2p_file_path_ctype,
            dut_s_parameter_orientation_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_load_y_factor_noise_source_loss_from_s2p(
        self,
        selector_string,
        noise_source_loss_compensation_enabled,
        noise_source_loss_s2p_file_path,
        noise_source_loss_s_parameter_orientation,
        noise_source_loss_temperature,
    ):
        """nf_load_y_factor_noise_source_loss_from_s2p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_source_loss_compensation_enabled_ctype = ctypes.c_int32(
            noise_source_loss_compensation_enabled
        )
        noise_source_loss_s2p_file_path_ctype = ctypes.create_string_buffer(
            noise_source_loss_s2p_file_path.encode(self._encoding)
        )
        noise_source_loss_s_parameter_orientation_ctype = ctypes.c_int32(
            noise_source_loss_s_parameter_orientation
        )
        noise_source_loss_temperature_ctype = ctypes.c_double(noise_source_loss_temperature)
        error_code = self._library.RFmxSpecAn_NFLoadYFactorNoiseSourceLossFromS2p(
            vi_ctype,
            selector_string_ctype,
            noise_source_loss_compensation_enabled_ctype,
            noise_source_loss_s2p_file_path_ctype,
            noise_source_loss_s_parameter_orientation_ctype,
            noise_source_loss_temperature_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_load_cold_source_input_termination_from_s1p(
        self, selector_string, termination_s1p_file_path, termination_temperature
    ):
        """nf_load_cold_source_input_termination_from_s1p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        termination_s1p_file_path_ctype = ctypes.create_string_buffer(
            termination_s1p_file_path.encode(self._encoding)
        )
        termination_temperature_ctype = ctypes.c_double(termination_temperature)
        error_code = self._library.RFmxSpecAn_NFLoadColdSourceInputTerminationFromS1p(
            vi_ctype,
            selector_string_ctype,
            termination_s1p_file_path_ctype,
            termination_temperature_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_load_external_preamp_gain_from_s2p(
        self,
        selector_string,
        external_preamp_present,
        external_preamp_gain_s2p_file_path,
        external_preamp_gain_s_parameter_orientation,
    ):
        """nf_load_external_preamp_gain_from_s2p."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        external_preamp_present_ctype = ctypes.c_int32(external_preamp_present)
        external_preamp_gain_s2p_file_path_ctype = ctypes.create_string_buffer(
            external_preamp_gain_s2p_file_path.encode(self._encoding)
        )
        external_preamp_gain_s_parameter_orientation_ctype = ctypes.c_int32(
            external_preamp_gain_s_parameter_orientation
        )
        error_code = self._library.RFmxSpecAn_NFLoadExternalPreampGainFromS2p(
            vi_ctype,
            selector_string_ctype,
            external_preamp_present_ctype,
            external_preamp_gain_s2p_file_path_ctype,
            external_preamp_gain_s_parameter_orientation_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_frequency_start_stop(
        self, selector_string, start_frequency, stop_frequency
    ):
        """spectrum_configure_frequency_start_stop."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        start_frequency_ctype = ctypes.c_double(start_frequency)
        stop_frequency_ctype = ctypes.c_double(stop_frequency)
        error_code = self._library.RFmxSpecAn_SpectrumCfgFrequencyStartStop(
            vi_ctype, selector_string_ctype, start_frequency_ctype, stop_frequency_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_validate_noise_calibration_data(self, selector_string):
        """spectrum_validate_noise_calibration_data."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_calibration_data_valid_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_SpectrumValidateNoiseCalibrationData(
            vi_ctype, selector_string_ctype, noise_calibration_data_valid_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.SpectrumNoiseCalibrationDataValid(noise_calibration_data_valid_ctype.value),
            error_code,
        )

    def ampm_configure_reference_waveform(
        self, selector_string, x0, dx, reference_waveform, idle_duration_present, signal_type
    ):
        """ampm_configure_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(reference_waveform, "reference_waveform", "complex64")
        reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=reference_waveform, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(reference_waveform) if reference_waveform is not None else 0
        )
        idle_duration_present_ctype = ctypes.c_int32(idle_duration_present)
        signal_type_ctype = ctypes.c_int32(signal_type)
        error_code = self._library.RFmxSpecAn_AMPMCfgReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            reference_waveform_ctype,
            array_size_ctype,
            idle_duration_present_ctype,
            signal_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_user_dpd_polynomial(self, selector_string, dpd_polynomial):
        """dpd_configure_user_dpd_polynomial."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        _helper.validate_numpy_array(dpd_polynomial, "dpd_polynomial", "complex64")
        dpd_polynomial_ctype = _get_ctypes_pointer_for_buffer(
            value=dpd_polynomial, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(len(dpd_polynomial) if dpd_polynomial is not None else 0)
        error_code = self._library.RFmxSpecAn_DPDCfgApplyDPDUserDPDPolynomial(
            vi_ctype, selector_string_ctype, dpd_polynomial_ctype, array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_user_lookup_table(self, selector_string, lut_input_powers, lut_complex_gains):
        """dpd_configure_user_lookup_table."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        lut_input_powers_ctype = _get_ctypes_pointer_for_buffer(
            value=lut_input_powers, library_type=ctypes.c_float
        )
        _helper.validate_numpy_array(lut_complex_gains, "lut_complex_gains", "complex64")
        lut_complex_gains_ctype = _get_ctypes_pointer_for_buffer(
            value=lut_complex_gains, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["lut_input_powers", "lut_complex_gains"], lut_input_powers, lut_complex_gains
            )
        )
        error_code = self._library.RFmxSpecAn_DPDCfgApplyDPDUserLookupTable(
            vi_ctype,
            selector_string_ctype,
            lut_input_powers_ctype,
            lut_complex_gains_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_previous_dpd_polynomial(self, selector_string, previous_dpd_polynomial):
        """dpd_configure_previous_dpd_polynomial."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        _helper.validate_numpy_array(
            previous_dpd_polynomial, "previous_dpd_polynomial", "complex64"
        )
        previous_dpd_polynomial_ctype = _get_ctypes_pointer_for_buffer(
            value=previous_dpd_polynomial, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(previous_dpd_polynomial) if previous_dpd_polynomial is not None else 0
        )
        error_code = self._library.RFmxSpecAn_DPDCfgPreviousDPDPolynomial(
            vi_ctype, selector_string_ctype, previous_dpd_polynomial_ctype, array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_reference_waveform(
        self, selector_string, x0, dx, reference_waveform, idle_duration_present, signal_type
    ):
        """dpd_configure_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(reference_waveform, "reference_waveform", "complex64")
        reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=reference_waveform, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(reference_waveform) if reference_waveform is not None else 0
        )
        idle_duration_present_ctype = ctypes.c_int32(idle_duration_present)
        signal_type_ctype = ctypes.c_int32(signal_type)
        error_code = self._library.RFmxSpecAn_DPDCfgReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            reference_waveform_ctype,
            array_size_ctype,
            idle_duration_present_ctype,
            signal_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_extract_model_target_waveform(self, selector_string, x0, dx, target_waveform):
        """dpd_configure_extract_model_target_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(target_waveform, "target_waveform", "complex64")
        target_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=target_waveform, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(target_waveform) if target_waveform is not None else 0
        )
        error_code = self._library.RFmxSpecAn_DPDCfgExtractModelTargetWaveform(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            target_waveform_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_carrier_and_offsets(
        self, selector_string, integration_bandwidth, number_of_offsets, channel_spacing
    ):
        """acp_configure_carrier_and_offsets."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integration_bandwidth_ctype = ctypes.c_double(integration_bandwidth)
        number_of_offsets_ctype = ctypes.c_int32(number_of_offsets)
        channel_spacing_ctype = ctypes.c_double(channel_spacing)
        error_code = self._library.RFmxSpecAn_ACPCfgCarrierAndOffsets(
            vi_ctype,
            selector_string_ctype,
            integration_bandwidth_ctype,
            number_of_offsets_ctype,
            channel_spacing_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_validate_noise_calibration_data(self, selector_string):
        """acp_validate_noise_calibration_data."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_calibration_data_valid_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_ACPValidateNoiseCalibrationData(
            vi_ctype, selector_string_ctype, noise_calibration_data_valid_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.AcpNoiseCalibrationDataValid(noise_calibration_data_valid_ctype.value),
            error_code,
        )

    def chp_validate_noise_calibration_data(self, selector_string):
        """chp_validate_noise_calibration_data."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_calibration_data_valid_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_CHPValidateNoiseCalibrationData(
            vi_ctype, selector_string_ctype, noise_calibration_data_valid_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.ChpNoiseCalibrationDataValid(noise_calibration_data_valid_ctype.value),
            error_code,
        )

    def marker_configure_number_of_markers(self, selector_string, number_of_markers):
        """marker_configure_number_of_markers."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_markers_ctype = ctypes.c_int32(number_of_markers)
        error_code = self._library.RFmxSpecAn_MarkerCfgNumberOfMarkers(
            vi_ctype, selector_string_ctype, number_of_markers_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_peak_excursion(
        self, selector_string, peak_excursion_enabled, peak_excursion
    ):
        """marker_configure_peak_excursion."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        peak_excursion_enabled_ctype = ctypes.c_int32(peak_excursion_enabled)
        peak_excursion_ctype = ctypes.c_double(peak_excursion)
        error_code = self._library.RFmxSpecAn_MarkerCfgPeakExcursion(
            vi_ctype, selector_string_ctype, peak_excursion_enabled_ctype, peak_excursion_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_reference_marker(self, selector_string, reference_marker):
        """marker_configure_reference_marker."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        reference_marker_ctype = ctypes.c_int32(reference_marker)
        error_code = self._library.RFmxSpecAn_MarkerCfgReferenceMarker(
            vi_ctype, selector_string_ctype, reference_marker_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_threshold(self, selector_string, threshold_enabled, threshold):
        """marker_configure_threshold."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_enabled_ctype = ctypes.c_int32(threshold_enabled)
        threshold_ctype = ctypes.c_double(threshold)
        error_code = self._library.RFmxSpecAn_MarkerCfgThreshold(
            vi_ctype, selector_string_ctype, threshold_enabled_ctype, threshold_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_trace(self, selector_string, trace):
        """marker_configure_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        trace_ctype = ctypes.c_int32(trace)
        error_code = self._library.RFmxSpecAn_MarkerCfgTrace(
            vi_ctype, selector_string_ctype, trace_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_type(self, selector_string, marker_type):
        """marker_configure_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        marker_type_ctype = ctypes.c_int32(marker_type)
        error_code = self._library.RFmxSpecAn_MarkerCfgType(
            vi_ctype, selector_string_ctype, marker_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_x_location(self, selector_string, marker_x_location):
        """marker_configure_x_location."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        marker_x_location_ctype = ctypes.c_double(marker_x_location)
        error_code = self._library.RFmxSpecAn_MarkerCfgXLocation(
            vi_ctype, selector_string_ctype, marker_x_location_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_y_location(self, selector_string, marker_y_location):
        """marker_configure_y_location."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        marker_y_location_ctype = ctypes.c_double(marker_y_location)
        error_code = self._library.RFmxSpecAn_MarkerCfgYLocation(
            vi_ctype, selector_string_ctype, marker_y_location_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_function_type(self, selector_string, function_type):
        """marker_configure_function_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        function_type_ctype = ctypes.c_int32(function_type)
        error_code = self._library.RFmxSpecAn_MarkerCfgFunctionType(
            vi_ctype, selector_string_ctype, function_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def marker_configure_band_span(self, selector_string, span):
        """marker_configure_band_span."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        span_ctype = ctypes.c_double(span)
        error_code = self._library.RFmxSpecAn_MarkerCfgBandSpan(
            vi_ctype, selector_string_ctype, span_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_segment_start_time_step(
        self, selector_string, number_of_segments, segment0_start_time, segment_interval
    ):
        """pavt_configure_segment_start_time_step."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_segments_ctype = ctypes.c_int32(number_of_segments)
        segment0_start_time_ctype = ctypes.c_double(segment0_start_time)
        segment_interval_ctype = ctypes.c_double(segment_interval)
        error_code = self._library.RFmxSpecAn_PAVTCfgSegmentStartTimeStep(
            vi_ctype,
            selector_string_ctype,
            number_of_segments_ctype,
            segment0_start_time_ctype,
            segment_interval_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def idpd_configure_reference_waveform(
        self, selector_string, x0, dx, reference_waveform, idle_duration_present, signal_type
    ):
        """idpd_configure_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(reference_waveform, "reference_waveform", "complex64")
        reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=reference_waveform, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(reference_waveform) if reference_waveform is not None else 0
        )
        idle_duration_present_ctype = ctypes.c_int32(idle_duration_present)
        signal_type_ctype = ctypes.c_int32(signal_type)
        error_code = self._library.RFmxSpecAn_IDPDCfgReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            reference_waveform_ctype,
            array_size_ctype,
            idle_duration_present_ctype,
            signal_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def idpd_configure_predistorted_waveform(
        self, selector_string, x0, dx, predistorted_waveform, target_gain
    ):
        """idpd_configure_predistorted_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(predistorted_waveform, "predistorted_waveform", "complex64")
        predistorted_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=predistorted_waveform, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(predistorted_waveform) if predistorted_waveform is not None else 0
        )
        target_gain_ctype = ctypes.c_double(target_gain)
        error_code = self._library.RFmxSpecAn_IDPDCfgPredistortedWaveform(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            predistorted_waveform_ctype,
            array_size_ctype,
            target_gain_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def idpd_configure_equalizer_coefficients(
        self, selector_string, x0, dx, equalizer_coefficients
    ):
        """idpd_configure_equalizer_coefficients."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(equalizer_coefficients, "equalizer_coefficients", "complex64")
        equalizer_coefficients_ctype = _get_ctypes_pointer_for_buffer(
            value=equalizer_coefficients, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(
            len(equalizer_coefficients) if equalizer_coefficients is not None else 0
        )
        error_code = self._library.RFmxSpecAn_IDPDCfgEqualizerCoefficients(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            equalizer_coefficients_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def abort_measurements(self, selector_string):
        """abort_measurements."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_AbortMeasurements(vi_ctype, selector_string_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def auto_level(self, selector_string, bandwidth, measurement_interval):
        """auto_level."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        bandwidth_ctype = ctypes.c_double(bandwidth)
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        reference_level_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_AutoLevel(
            vi_ctype,
            selector_string_ctype,
            bandwidth_ctype,
            measurement_interval_ctype,
            reference_level_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return reference_level_ctype.value, error_code

    def check_measurement_status(self, selector_string):
        """check_measurement_status."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        is_done_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_CheckMeasurementStatus(
            vi_ctype, selector_string_ctype, is_done_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return bool(is_done_ctype.value), error_code

    def clear_all_named_results(self, selector_string):
        """clear_all_named_results."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_ClearAllNamedResults(vi_ctype, selector_string_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def clear_named_result(self, selector_string):
        """clear_named_result."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_ClearNamedResult(vi_ctype, selector_string_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def commit(self, selector_string):
        """commit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_Commit(vi_ctype, selector_string_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def configure_digital_edge_trigger(
        self, selector_string, digital_edge_source, digital_edge, trigger_delay, enable_trigger
    ):
        """configure_digital_edge_trigger."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        digital_edge_source_ctype = ctypes.create_string_buffer(
            digital_edge_source.encode(self._encoding)
        )
        digital_edge_ctype = ctypes.c_int32(digital_edge)
        trigger_delay_ctype = ctypes.c_double(trigger_delay)
        enable_trigger_ctype = ctypes.c_int32(enable_trigger)
        error_code = self._library.RFmxSpecAn_CfgDigitalEdgeTrigger(
            vi_ctype,
            selector_string_ctype,
            digital_edge_source_ctype,
            digital_edge_ctype,
            trigger_delay_ctype,
            enable_trigger_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

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
        """configure_iq_power_edge_trigger."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        iq_power_edge_trigger_source_ctype = ctypes.create_string_buffer(
            iq_power_edge_trigger_source.encode(self._encoding)
        )
        iq_power_edge_trigger_level_ctype = ctypes.c_double(iq_power_edge_trigger_level)
        iq_power_edge_slope_ctype = ctypes.c_int32(iq_power_edge_slope)
        trigger_delay_ctype = ctypes.c_double(trigger_delay)
        minimum_quiet_time_mode_ctype = ctypes.c_int32(minimum_quiet_time_mode)
        minimum_quiet_time_duration_ctype = ctypes.c_double(minimum_quiet_time_duration)
        enable_trigger_ctype = ctypes.c_int32(enable_trigger)
        error_code = self._library.RFmxSpecAn_CfgIQPowerEdgeTrigger(
            vi_ctype,
            selector_string_ctype,
            iq_power_edge_trigger_source_ctype,
            iq_power_edge_trigger_level_ctype,
            iq_power_edge_slope_ctype,
            trigger_delay_ctype,
            minimum_quiet_time_mode_ctype,
            minimum_quiet_time_duration_ctype,
            enable_trigger_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def configure_software_edge_trigger(self, selector_string, trigger_delay, enable_trigger):
        """configure_software_edge_trigger."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        trigger_delay_ctype = ctypes.c_double(trigger_delay)
        enable_trigger_ctype = ctypes.c_int32(enable_trigger)
        error_code = self._library.RFmxSpecAn_CfgSoftwareEdgeTrigger(
            vi_ctype, selector_string_ctype, trigger_delay_ctype, enable_trigger_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def create_list(self, list_name):
        """create_list."""
        vi_ctype = ctypes.c_uint32(self._vi)
        list_name_ctype = ctypes.create_string_buffer(list_name.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_CreateList(vi_ctype, list_name_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def create_list_step(self, selector_string):
        """create_list_step."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        created_step_index_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_CreateListStep(
            vi_ctype, selector_string_ctype, created_step_index_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return created_step_index_ctype.value, error_code

    def create_signal_configuration(self, signal_name):
        """create_signal_configuration."""
        vi_ctype = ctypes.c_uint32(self._vi)
        signal_name_ctype = ctypes.create_string_buffer(signal_name.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_CreateSignalConfiguration(vi_ctype, signal_name_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def delete_list(self, list_name):
        """delete_list."""
        vi_ctype = ctypes.c_uint32(self._vi)
        list_name_ctype = ctypes.create_string_buffer(list_name.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_DeleteList(vi_ctype, list_name_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def disable_trigger(self, selector_string):
        """disable_trigger."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_DisableTrigger(vi_ctype, selector_string_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def initiate(self, selector_string, result_name):
        """initiate."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        result_name_ctype = ctypes.create_string_buffer(result_name.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_Initiate(
            vi_ctype, selector_string_ctype, result_name_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def reset_to_default(self, selector_string):
        """reset_to_default."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_ResetToDefault(vi_ctype, selector_string_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def select_measurements(self, selector_string, measurements, enable_all_traces):
        """select_measurements."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurements_ctype = ctypes.c_uint32(measurements)
        enable_all_traces_ctype = ctypes.c_int32(enable_all_traces)
        error_code = self._library.RFmxSpecAn_SelectMeasurements(
            vi_ctype, selector_string_ctype, measurements_ctype, enable_all_traces_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def wait_for_measurement_complete(self, selector_string, timeout):
        """wait_for_measurement_complete."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        error_code = self._library.RFmxSpecAn_WaitForMeasurementComplete(
            vi_ctype, selector_string_ctype, timeout_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def validate_list_step_number(self, list_name, step_number):
        """validate_list_step_number."""
        vi_ctype = ctypes.c_uint32(self._vi)
        list_name_ctype = ctypes.create_string_buffer(list_name.encode(self._encoding))
        step_number_ctype = ctypes.c_int32(step_number)
        error_code = self._library.RFmxSpecAn_ValidateListStepNumber(
            vi_ctype, list_name_ctype, step_number_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_auto_intermods_setup(
        self, selector_string, auto_intermods_setup_enabled, maximum_intermod_order
    ):
        """im_configure_auto_intermods_setup."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        auto_intermods_setup_enabled_ctype = ctypes.c_int32(auto_intermods_setup_enabled)
        maximum_intermod_order_ctype = ctypes.c_int32(maximum_intermod_order)
        error_code = self._library.RFmxSpecAn_IMCfgAutoIntermodsSetup(
            vi_ctype,
            selector_string_ctype,
            auto_intermods_setup_enabled_ctype,
            maximum_intermod_order_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """im_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_IMCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_fft(self, selector_string, fft_window, fft_padding):
        """im_configure_fft."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        fft_padding_ctype = ctypes.c_double(fft_padding)
        error_code = self._library.RFmxSpecAn_IMCfgFFT(
            vi_ctype, selector_string_ctype, fft_window_ctype, fft_padding_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_frequency_definition(self, selector_string, frequency_definition):
        """im_configure_frequency_definition."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        frequency_definition_ctype = ctypes.c_int32(frequency_definition)
        error_code = self._library.RFmxSpecAn_IMCfgFrequencyDefinition(
            vi_ctype, selector_string_ctype, frequency_definition_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_fundamental_tones(
        self, selector_string, lower_tone_frequency, upper_tone_frequency
    ):
        """im_configure_fundamental_tones."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        lower_tone_frequency_ctype = ctypes.c_double(lower_tone_frequency)
        upper_tone_frequency_ctype = ctypes.c_double(upper_tone_frequency)
        error_code = self._library.RFmxSpecAn_IMCfgFundamentalTones(
            vi_ctype, selector_string_ctype, lower_tone_frequency_ctype, upper_tone_frequency_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_intermod_array(
        self,
        selector_string,
        intermod_order,
        lower_intermod_frequency,
        upper_intermod_frequency,
        intermod_side,
        intermod_enabled,
    ):
        """im_configure_intermod_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        intermod_order_ctype = _get_ctypes_pointer_for_buffer(
            value=intermod_order, library_type=ctypes.c_int32
        )
        lower_intermod_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=lower_intermod_frequency, library_type=ctypes.c_double
        )
        upper_intermod_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=upper_intermod_frequency, library_type=ctypes.c_double
        )
        intermod_side_ctype = _get_ctypes_pointer_for_buffer(
            value=intermod_side, library_type=ctypes.c_int32
        )
        intermod_enabled_ctype = _get_ctypes_pointer_for_buffer(
            value=intermod_enabled, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                [
                    "intermod_order",
                    "lower_intermod_frequency",
                    "upper_intermod_frequency",
                    "intermod_side",
                    "intermod_enabled",
                ],
                intermod_order,
                lower_intermod_frequency,
                upper_intermod_frequency,
                intermod_side,
                intermod_enabled,
            )
        )
        error_code = self._library.RFmxSpecAn_IMCfgIntermodArray(
            vi_ctype,
            selector_string_ctype,
            intermod_order_ctype,
            lower_intermod_frequency_ctype,
            upper_intermod_frequency_ctype,
            intermod_side_ctype,
            intermod_enabled_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_intermod(
        self,
        selector_string,
        intermod_order,
        lower_intermod_frequency,
        upper_intermod_frequency,
        intermod_side,
        intermod_enabled,
    ):
        """im_configure_intermod."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        intermod_order_ctype = ctypes.c_int32(intermod_order)
        lower_intermod_frequency_ctype = ctypes.c_double(lower_intermod_frequency)
        upper_intermod_frequency_ctype = ctypes.c_double(upper_intermod_frequency)
        intermod_side_ctype = ctypes.c_int32(intermod_side)
        intermod_enabled_ctype = ctypes.c_int32(intermod_enabled)
        error_code = self._library.RFmxSpecAn_IMCfgIntermod(
            vi_ctype,
            selector_string_ctype,
            intermod_order_ctype,
            lower_intermod_frequency_ctype,
            upper_intermod_frequency_ctype,
            intermod_side_ctype,
            intermod_enabled_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_measurement_method(self, selector_string, measurement_method):
        """im_configure_measurement_method."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_method_ctype = ctypes.c_int32(measurement_method)
        error_code = self._library.RFmxSpecAn_IMCfgMeasurementMethod(
            vi_ctype, selector_string_ctype, measurement_method_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_number_of_intermods(self, selector_string, number_of_intermods):
        """im_configure_number_of_intermods."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_intermods_ctype = ctypes.c_int32(number_of_intermods)
        error_code = self._library.RFmxSpecAn_IMCfgNumberOfIntermods(
            vi_ctype, selector_string_ctype, number_of_intermods_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """im_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_IMCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        """im_configure_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_IMCfgSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_averaging(self, selector_string, averaging_enabled, averaging_count):
        """nf_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        error_code = self._library.RFmxSpecAn_NFCfgAveraging(
            vi_ctype, selector_string_ctype, averaging_enabled_ctype, averaging_count_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_calibration_loss(
        self,
        selector_string,
        calibration_loss_compensation_enabled,
        calibration_loss_frequency,
        calibration_loss,
        calibration_loss_temperature,
    ):
        """nf_configure_calibration_loss."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        calibration_loss_compensation_enabled_ctype = ctypes.c_int32(
            calibration_loss_compensation_enabled
        )
        calibration_loss_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=calibration_loss_frequency, library_type=ctypes.c_double
        )
        calibration_loss_ctype = _get_ctypes_pointer_for_buffer(
            value=calibration_loss, library_type=ctypes.c_double
        )
        calibration_loss_temperature_ctype = ctypes.c_double(calibration_loss_temperature)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["calibration_loss_frequency", "calibration_loss"],
                calibration_loss_frequency,
                calibration_loss,
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgCalibrationLoss(
            vi_ctype,
            selector_string_ctype,
            calibration_loss_compensation_enabled_ctype,
            calibration_loss_frequency_ctype,
            calibration_loss_ctype,
            calibration_loss_temperature_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_cold_source_dut_s_parameters(
        self, selector_string, dut_s_parameters_frequency, dut_s21, dut_s12, dut_s11, dut_s22
    ):
        """nf_configure_cold_source_dut_s_parameters."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_s_parameters_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=dut_s_parameters_frequency, library_type=ctypes.c_double
        )
        dut_s21_ctype = _get_ctypes_pointer_for_buffer(value=dut_s21, library_type=ctypes.c_double)
        dut_s12_ctype = _get_ctypes_pointer_for_buffer(value=dut_s12, library_type=ctypes.c_double)
        dut_s11_ctype = _get_ctypes_pointer_for_buffer(value=dut_s11, library_type=ctypes.c_double)
        dut_s22_ctype = _get_ctypes_pointer_for_buffer(value=dut_s22, library_type=ctypes.c_double)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["dut_s_parameters_frequency", "dut_s21", "dut_s12", "dut_s11", "dut_s22"],
                dut_s_parameters_frequency,
                dut_s21,
                dut_s12,
                dut_s11,
                dut_s22,
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgColdSourceDUTSParameters(
            vi_ctype,
            selector_string_ctype,
            dut_s_parameters_frequency_ctype,
            dut_s21_ctype,
            dut_s12_ctype,
            dut_s11_ctype,
            dut_s22_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_cold_source_input_termination(
        self, selector_string, termination_vswr, termination_vswr_frequency, termination_temperature
    ):
        """nf_configure_cold_source_input_termination."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        termination_vswr_ctype = _get_ctypes_pointer_for_buffer(
            value=termination_vswr, library_type=ctypes.c_double
        )
        termination_vswr_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=termination_vswr_frequency, library_type=ctypes.c_double
        )
        termination_temperature_ctype = ctypes.c_double(termination_temperature)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["termination_vswr", "termination_vswr_frequency"],
                termination_vswr,
                termination_vswr_frequency,
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgColdSourceInputTermination(
            vi_ctype,
            selector_string_ctype,
            termination_vswr_ctype,
            termination_vswr_frequency_ctype,
            termination_temperature_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_cold_source_mode(self, selector_string, cold_source_mode):
        """nf_configure_cold_source_mode."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        cold_source_mode_ctype = ctypes.c_int32(cold_source_mode)
        error_code = self._library.RFmxSpecAn_NFCfgColdSourceMode(
            vi_ctype, selector_string_ctype, cold_source_mode_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_dut_input_loss(
        self,
        selector_string,
        dut_input_loss_compensation_enabled,
        dut_input_loss_frequency,
        dut_input_loss,
        dut_input_loss_temperature,
    ):
        """nf_configure_dut_input_loss."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_input_loss_compensation_enabled_ctype = ctypes.c_int32(
            dut_input_loss_compensation_enabled
        )
        dut_input_loss_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=dut_input_loss_frequency, library_type=ctypes.c_double
        )
        dut_input_loss_ctype = _get_ctypes_pointer_for_buffer(
            value=dut_input_loss, library_type=ctypes.c_double
        )
        dut_input_loss_temperature_ctype = ctypes.c_double(dut_input_loss_temperature)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["dut_input_loss_frequency", "dut_input_loss"],
                dut_input_loss_frequency,
                dut_input_loss,
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgDUTInputLoss(
            vi_ctype,
            selector_string_ctype,
            dut_input_loss_compensation_enabled_ctype,
            dut_input_loss_frequency_ctype,
            dut_input_loss_ctype,
            dut_input_loss_temperature_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_dut_output_loss(
        self,
        selector_string,
        dut_output_loss_compensation_enabled,
        dut_output_loss_frequency,
        dut_output_loss,
        dut_output_loss_temperature,
    ):
        """nf_configure_dut_output_loss."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_output_loss_compensation_enabled_ctype = ctypes.c_int32(
            dut_output_loss_compensation_enabled
        )
        dut_output_loss_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=dut_output_loss_frequency, library_type=ctypes.c_double
        )
        dut_output_loss_ctype = _get_ctypes_pointer_for_buffer(
            value=dut_output_loss, library_type=ctypes.c_double
        )
        dut_output_loss_temperature_ctype = ctypes.c_double(dut_output_loss_temperature)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["dut_output_loss_frequency", "dut_output_loss"],
                dut_output_loss_frequency,
                dut_output_loss,
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgDUTOutputLoss(
            vi_ctype,
            selector_string_ctype,
            dut_output_loss_compensation_enabled_ctype,
            dut_output_loss_frequency_ctype,
            dut_output_loss_ctype,
            dut_output_loss_temperature_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_frequency_list(self, selector_string, frequency_list):
        """nf_configure_frequency_list."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        frequency_list_ctype = _get_ctypes_pointer_for_buffer(
            value=frequency_list, library_type=ctypes.c_double
        )
        array_size_ctype = ctypes.c_int32(len(frequency_list) if frequency_list is not None else 0)
        error_code = self._library.RFmxSpecAn_NFCfgFrequencyList(
            vi_ctype, selector_string_ctype, frequency_list_ctype, array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_measurement_bandwidth(self, selector_string, measurement_bandwidth):
        """nf_configure_measurement_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_bandwidth_ctype = ctypes.c_double(measurement_bandwidth)
        error_code = self._library.RFmxSpecAn_NFCfgMeasurementBandwidth(
            vi_ctype, selector_string_ctype, measurement_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_measurement_interval(self, selector_string, measurement_interval):
        """nf_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_NFCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_measurement_method(self, selector_string, measurement_method):
        """nf_configure_measurement_method."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_method_ctype = ctypes.c_int32(measurement_method)
        error_code = self._library.RFmxSpecAn_NFCfgMeasurementMethod(
            vi_ctype, selector_string_ctype, measurement_method_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_y_factor_mode(self, selector_string, y_factor_mode):
        """nf_configure_y_factor_mode."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        y_factor_mode_ctype = ctypes.c_int32(y_factor_mode)
        error_code = self._library.RFmxSpecAn_NFCfgYFactorMode(
            vi_ctype, selector_string_ctype, y_factor_mode_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_y_factor_noise_source_enr(
        self, selector_string, enr_frequency, enr, cold_temperature, off_temperature
    ):
        """nf_configure_y_factor_noise_source_enr."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        enr_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=enr_frequency, library_type=ctypes.c_double
        )
        enr_ctype = _get_ctypes_pointer_for_buffer(value=enr, library_type=ctypes.c_double)
        cold_temperature_ctype = ctypes.c_double(cold_temperature)
        off_temperature_ctype = ctypes.c_double(off_temperature)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["enr_frequency", "enr"], enr_frequency, enr
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgYFactorNoiseSourceENR(
            vi_ctype,
            selector_string_ctype,
            enr_frequency_ctype,
            enr_ctype,
            cold_temperature_ctype,
            off_temperature_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_y_factor_noise_source_loss(
        self,
        selector_string,
        noise_source_loss_compensation_enabled,
        noise_source_loss_frequency,
        noise_source_loss,
        noise_source_loss_temperature,
    ):
        """nf_configure_y_factor_noise_source_loss."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_source_loss_compensation_enabled_ctype = ctypes.c_int32(
            noise_source_loss_compensation_enabled
        )
        noise_source_loss_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=noise_source_loss_frequency, library_type=ctypes.c_double
        )
        noise_source_loss_ctype = _get_ctypes_pointer_for_buffer(
            value=noise_source_loss, library_type=ctypes.c_double
        )
        noise_source_loss_temperature_ctype = ctypes.c_double(noise_source_loss_temperature)
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["noise_source_loss_frequency", "noise_source_loss"],
                noise_source_loss_frequency,
                noise_source_loss,
            )
        )
        error_code = self._library.RFmxSpecAn_NFCfgYFactorNoiseSourceLoss(
            vi_ctype,
            selector_string_ctype,
            noise_source_loss_compensation_enabled_ctype,
            noise_source_loss_frequency_ctype,
            noise_source_loss_ctype,
            noise_source_loss_temperature_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def nf_configure_y_factor_noise_source_settling_time(self, selector_string, settling_time):
        """nf_configure_y_factor_noise_source_settling_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        settling_time_ctype = ctypes.c_double(settling_time)
        error_code = self._library.RFmxSpecAn_NFCfgYFactorNoiseSourceSettlingTime(
            vi_ctype, selector_string_ctype, settling_time_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def fcnt_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """fcnt_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_FCntCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def fcnt_configure_measurement_interval(self, selector_string, measurement_interval):
        """fcnt_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_FCntCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def fcnt_configure_rbw_filter(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """fcnt_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_FCntCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_ctype, rbw_filter_type_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def fcnt_configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """fcnt_configure_threshold."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_enabled_ctype = ctypes.c_int32(threshold_enabled)
        threshold_level_ctype = ctypes.c_double(threshold_level)
        threshold_type_ctype = ctypes.c_int32(threshold_type)
        error_code = self._library.RFmxSpecAn_FCntCfgThreshold(
            vi_ctype,
            selector_string_ctype,
            threshold_enabled_ctype,
            threshold_level_ctype,
            threshold_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """spectrum_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_SpectrumCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_detector(self, selector_string, detector_type, detector_points):
        """spectrum_configure_detector."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        detector_type_ctype = ctypes.c_int32(detector_type)
        detector_points_ctype = ctypes.c_int32(detector_points)
        error_code = self._library.RFmxSpecAn_SpectrumCfgDetector(
            vi_ctype, selector_string_ctype, detector_type_ctype, detector_points_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_fft(self, selector_string, fft_window, fft_padding):
        """spectrum_configure_fft."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        fft_padding_ctype = ctypes.c_double(fft_padding)
        error_code = self._library.RFmxSpecAn_SpectrumCfgFFT(
            vi_ctype, selector_string_ctype, fft_window_ctype, fft_padding_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_noise_compensation_enabled(
        self, selector_string, noise_compensation_enabled
    ):
        """spectrum_configure_noise_compensation_enabled."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_compensation_enabled_ctype = ctypes.c_int32(noise_compensation_enabled)
        error_code = self._library.RFmxSpecAn_SpectrumCfgNoiseCompensationEnabled(
            vi_ctype, selector_string_ctype, noise_compensation_enabled_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_power_units(self, selector_string, spectrum_power_units):
        """spectrum_configure_power_units."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        spectrum_power_units_ctype = ctypes.c_int32(spectrum_power_units)
        error_code = self._library.RFmxSpecAn_SpectrumCfgPowerUnits(
            vi_ctype, selector_string_ctype, spectrum_power_units_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """spectrum_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_SpectrumCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_span(self, selector_string, span):
        """spectrum_configure_span."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        span_ctype = ctypes.c_double(span)
        error_code = self._library.RFmxSpecAn_SpectrumCfgSpan(
            vi_ctype, selector_string_ctype, span_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        """spectrum_configure_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_SpectrumCfgSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_vbw_filter(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        """spectrum_configure_vbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        vbw_auto_ctype = ctypes.c_int32(vbw_auto)
        vbw_ctype = ctypes.c_double(vbw)
        vbw_to_rbw_ratio_ctype = ctypes.c_double(vbw_to_rbw_ratio)
        error_code = self._library.RFmxSpecAn_SpectrumCfgVBWFilter(
            vi_ctype, selector_string_ctype, vbw_auto_ctype, vbw_ctype, vbw_to_rbw_ratio_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spectrum_configure_measurement_method(self, selector_string, measurement_method):
        """spectrum_configure_measurement_method."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_method_ctype = ctypes.c_int32(measurement_method)
        error_code = self._library.RFmxSpecAn_SpectrumCfgMeasurementMethod(
            vi_ctype, selector_string_ctype, measurement_method_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """spur_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_SpurCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_fft_window_type(self, selector_string, fft_window):
        """spur_configure_fft_window_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        error_code = self._library.RFmxSpecAn_SpurCfgFFTWindowType(
            vi_ctype, selector_string_ctype, fft_window_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_number_of_ranges(self, selector_string, number_of_ranges):
        """spur_configure_number_of_ranges."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_ranges_ctype = ctypes.c_int32(number_of_ranges)
        error_code = self._library.RFmxSpecAn_SpurCfgNumberOfRanges(
            vi_ctype, selector_string_ctype, number_of_ranges_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_absolute_limit_array(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        """spur_configure_range_absolute_limit_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        absolute_limit_mode_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit_mode, library_type=ctypes.c_int32
        )
        absolute_limit_start_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit_start, library_type=ctypes.c_double
        )
        absolute_limit_stop_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit_stop, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["absolute_limit_mode", "absolute_limit_start", "absolute_limit_stop"],
                absolute_limit_mode,
                absolute_limit_start,
                absolute_limit_stop,
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeAbsoluteLimitArray(
            vi_ctype,
            selector_string_ctype,
            absolute_limit_mode_ctype,
            absolute_limit_start_ctype,
            absolute_limit_stop_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_absolute_limit(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        """spur_configure_range_absolute_limit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        absolute_limit_mode_ctype = ctypes.c_int32(absolute_limit_mode)
        absolute_limit_start_ctype = ctypes.c_double(absolute_limit_start)
        absolute_limit_stop_ctype = ctypes.c_double(absolute_limit_stop)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeAbsoluteLimit(
            vi_ctype,
            selector_string_ctype,
            absolute_limit_mode_ctype,
            absolute_limit_start_ctype,
            absolute_limit_stop_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_detector_array(self, selector_string, detector_type, detector_points):
        """spur_configure_range_detector_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        detector_type_ctype = _get_ctypes_pointer_for_buffer(
            value=detector_type, library_type=ctypes.c_int32
        )
        detector_points_ctype = _get_ctypes_pointer_for_buffer(
            value=detector_points, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["detector_type", "detector_points"], detector_type, detector_points
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeDetectorArray(
            vi_ctype,
            selector_string_ctype,
            detector_type_ctype,
            detector_points_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_detector(self, selector_string, detector_type, detector_points):
        """spur_configure_range_detector."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        detector_type_ctype = ctypes.c_int32(detector_type)
        detector_points_ctype = ctypes.c_int32(detector_points)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeDetector(
            vi_ctype, selector_string_ctype, detector_type_ctype, detector_points_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_frequency_array(
        self, selector_string, start_frequency, stop_frequency, range_enabled
    ):
        """spur_configure_range_frequency_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        start_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=start_frequency, library_type=ctypes.c_double
        )
        stop_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=stop_frequency, library_type=ctypes.c_double
        )
        range_enabled_ctype = _get_ctypes_pointer_for_buffer(
            value=range_enabled, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["start_frequency", "stop_frequency", "range_enabled"],
                start_frequency,
                stop_frequency,
                range_enabled,
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeFrequencyArray(
            vi_ctype,
            selector_string_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
            range_enabled_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_frequency(
        self, selector_string, start_frequency, stop_frequency, range_enabled
    ):
        """spur_configure_range_frequency."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        start_frequency_ctype = ctypes.c_double(start_frequency)
        stop_frequency_ctype = ctypes.c_double(stop_frequency)
        range_enabled_ctype = ctypes.c_int32(range_enabled)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeFrequency(
            vi_ctype,
            selector_string_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
            range_enabled_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_number_of_spurs_to_report_array(
        self, selector_string, number_of_spurs_to_report
    ):
        """spur_configure_range_number_of_spurs_to_report_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_spurs_to_report_ctype = _get_ctypes_pointer_for_buffer(
            value=number_of_spurs_to_report, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(number_of_spurs_to_report) if number_of_spurs_to_report is not None else 0
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReportArray(
            vi_ctype,
            selector_string_ctype,
            number_of_spurs_to_report_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_number_of_spurs_to_report(
        self, selector_string, number_of_spurs_to_report
    ):
        """spur_configure_range_number_of_spurs_to_report."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_spurs_to_report_ctype = ctypes.c_int32(number_of_spurs_to_report)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeNumberOfSpursToReport(
            vi_ctype, selector_string_ctype, number_of_spurs_to_report_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_peak_criteria_array(self, selector_string, threshold, excursion):
        """spur_configure_range_peak_criteria_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_ctype = _get_ctypes_pointer_for_buffer(
            value=threshold, library_type=ctypes.c_double
        )
        excursion_ctype = _get_ctypes_pointer_for_buffer(
            value=excursion, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["threshold", "excursion"], threshold, excursion
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangePeakCriteriaArray(
            vi_ctype,
            selector_string_ctype,
            threshold_ctype,
            excursion_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_peak_criteria(self, selector_string, threshold, excursion):
        """spur_configure_range_peak_criteria."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_ctype = ctypes.c_double(threshold)
        excursion_ctype = ctypes.c_double(excursion)
        error_code = self._library.RFmxSpecAn_SpurCfgRangePeakCriteria(
            vi_ctype, selector_string_ctype, threshold_ctype, excursion_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_rbw_array(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """spur_configure_range_rbw_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = _get_ctypes_pointer_for_buffer(value=rbw_auto, library_type=ctypes.c_int32)
        rbw_ctype = _get_ctypes_pointer_for_buffer(value=rbw, library_type=ctypes.c_double)
        rbw_filter_type_ctype = _get_ctypes_pointer_for_buffer(
            value=rbw_filter_type, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["rbw_auto", "rbw", "rbw_filter_type"], rbw_auto, rbw, rbw_filter_type
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeRBWArray(
            vi_ctype,
            selector_string_ctype,
            rbw_auto_ctype,
            rbw_ctype,
            rbw_filter_type_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """spur_configure_range_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_relative_attenuation_array(
        self, selector_string, relative_attenuation
    ):
        """spur_configure_range_relative_attenuation_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_attenuation_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_attenuation, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(relative_attenuation) if relative_attenuation is not None else 0
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeRelativeAttenuationArray(
            vi_ctype, selector_string_ctype, relative_attenuation_ctype, number_of_elements_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_relative_attenuation(self, selector_string, relative_attenuation):
        """spur_configure_range_relative_attenuation."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_attenuation_ctype = ctypes.c_double(relative_attenuation)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeRelativeAttenuation(
            vi_ctype, selector_string_ctype, relative_attenuation_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_sweep_time_array(
        self, selector_string, sweep_time_auto, sweep_time_interval
    ):
        """spur_configure_range_sweep_time_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = _get_ctypes_pointer_for_buffer(
            value=sweep_time_auto, library_type=ctypes.c_int32
        )
        sweep_time_interval_ctype = _get_ctypes_pointer_for_buffer(
            value=sweep_time_interval, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["sweep_time_auto", "sweep_time_interval"], sweep_time_auto, sweep_time_interval
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeSweepTimeArray(
            vi_ctype,
            selector_string_ctype,
            sweep_time_auto_ctype,
            sweep_time_interval_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_sweep_time(
        self, selector_string, sweep_time_auto, sweep_time_interval
    ):
        """spur_configure_range_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_vbw_filter_array(
        self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio
    ):
        """spur_configure_range_vbw_filter_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        vbw_auto_ctype = _get_ctypes_pointer_for_buffer(value=vbw_auto, library_type=ctypes.c_int32)
        vbw_ctype = _get_ctypes_pointer_for_buffer(value=vbw, library_type=ctypes.c_double)
        vbw_to_rbw_ratio_ctype = _get_ctypes_pointer_for_buffer(
            value=vbw_to_rbw_ratio, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["vbw_auto", "vbw", "vbw_to_rbw_ratio"], vbw_auto, vbw, vbw_to_rbw_ratio
            )
        )
        error_code = self._library.RFmxSpecAn_SpurCfgRangeVBWFilterArray(
            vi_ctype,
            selector_string_ctype,
            vbw_auto_ctype,
            vbw_ctype,
            vbw_to_rbw_ratio_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_range_vbw_filter(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        """spur_configure_range_vbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        vbw_auto_ctype = ctypes.c_int32(vbw_auto)
        vbw_ctype = ctypes.c_double(vbw)
        vbw_to_rbw_ratio_ctype = ctypes.c_double(vbw_to_rbw_ratio)
        error_code = self._library.RFmxSpecAn_SpurCfgRangeVBWFilter(
            vi_ctype, selector_string_ctype, vbw_auto_ctype, vbw_ctype, vbw_to_rbw_ratio_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def spur_configure_trace_range_index(self, selector_string, trace_range_index):
        """spur_configure_trace_range_index."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        trace_range_index_ctype = ctypes.c_int32(trace_range_index)
        error_code = self._library.RFmxSpecAn_SpurCfgTraceRangeIndex(
            vi_ctype, selector_string_ctype, trace_range_index_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_am_to_am_curve_fit(
        self, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
    ):
        """ampm_configure_am_to_am_curve_fit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        am_to_am_curve_fit_order_ctype = ctypes.c_int32(am_to_am_curve_fit_order)
        am_to_am_curve_fit_type_ctype = ctypes.c_int32(am_to_am_curve_fit_type)
        error_code = self._library.RFmxSpecAn_AMPMCfgAMToAMCurveFit(
            vi_ctype,
            selector_string_ctype,
            am_to_am_curve_fit_order_ctype,
            am_to_am_curve_fit_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_am_to_pm_curve_fit(
        self, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
    ):
        """ampm_configure_am_to_pm_curve_fit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        am_to_pm_curve_fit_order_ctype = ctypes.c_int32(am_to_pm_curve_fit_order)
        am_to_pm_curve_fit_type_ctype = ctypes.c_int32(am_to_pm_curve_fit_type)
        error_code = self._library.RFmxSpecAn_AMPMCfgAMToPMCurveFit(
            vi_ctype,
            selector_string_ctype,
            am_to_pm_curve_fit_order_ctype,
            am_to_pm_curve_fit_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_averaging(self, selector_string, averaging_enabled, averaging_count):
        """ampm_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        error_code = self._library.RFmxSpecAn_AMPMCfgAveraging(
            vi_ctype, selector_string_ctype, averaging_enabled_ctype, averaging_count_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_compression_points(
        self, selector_string, compression_point_enabled, compression_level
    ):
        """ampm_configure_compression_points."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        compression_point_enabled_ctype = ctypes.c_int32(compression_point_enabled)
        compression_level_ctype = _get_ctypes_pointer_for_buffer(
            value=compression_level, library_type=ctypes.c_double
        )
        array_size_ctype = ctypes.c_int32(
            len(compression_level) if compression_level is not None else 0
        )
        error_code = self._library.RFmxSpecAn_AMPMCfgCompressionPoints(
            vi_ctype,
            selector_string_ctype,
            compression_point_enabled_ctype,
            compression_level_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_dut_average_input_power(self, selector_string, dut_average_input_power):
        """ampm_configure_dut_average_input_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_average_input_power_ctype = ctypes.c_double(dut_average_input_power)
        error_code = self._library.RFmxSpecAn_AMPMCfgDUTAverageInputPower(
            vi_ctype, selector_string_ctype, dut_average_input_power_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_measurement_interval(self, selector_string, measurement_interval):
        """ampm_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_AMPMCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_measurement_sample_rate(
        self, selector_string, sample_rate_mode, sample_rate
    ):
        """ampm_configure_measurement_sample_rate."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sample_rate_mode_ctype = ctypes.c_int32(sample_rate_mode)
        sample_rate_ctype = ctypes.c_double(sample_rate)
        error_code = self._library.RFmxSpecAn_AMPMCfgMeasurementSampleRate(
            vi_ctype, selector_string_ctype, sample_rate_mode_ctype, sample_rate_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_reference_power_type(self, selector_string, reference_power_type):
        """ampm_configure_reference_power_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        reference_power_type_ctype = ctypes.c_int32(reference_power_type)
        error_code = self._library.RFmxSpecAn_AMPMCfgReferencePowerType(
            vi_ctype, selector_string_ctype, reference_power_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_synchronization_method(self, selector_string, synchronization_method):
        """ampm_configure_synchronization_method."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        synchronization_method_ctype = ctypes.c_int32(synchronization_method)
        error_code = self._library.RFmxSpecAn_AMPMCfgSynchronizationMethod(
            vi_ctype, selector_string_ctype, synchronization_method_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ampm_configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """ampm_configure_threshold."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_enabled_ctype = ctypes.c_int32(threshold_enabled)
        threshold_level_ctype = ctypes.c_double(threshold_level)
        threshold_type_ctype = ctypes.c_int32(threshold_type)
        error_code = self._library.RFmxSpecAn_AMPMCfgThreshold(
            vi_ctype,
            selector_string_ctype,
            threshold_enabled_ctype,
            threshold_level_ctype,
            threshold_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_configuration_input(self, selector_string, configuration_input):
        """dpd_configure_configuration_input."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        configuration_input_ctype = ctypes.c_int32(configuration_input)
        error_code = self._library.RFmxSpecAn_DPDCfgApplyDPDConfigurationInput(
            vi_ctype, selector_string_ctype, configuration_input_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_lookup_table_correction_type(self, selector_string, lut_correction_type):
        """dpd_configure_lookup_table_correction_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        lut_correction_type_ctype = ctypes.c_int32(lut_correction_type)
        error_code = self._library.RFmxSpecAn_DPDCfgApplyDPDLookupTableCorrectionType(
            vi_ctype, selector_string_ctype, lut_correction_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_memory_model_correction_type(
        self, selector_string, memory_model_correction_type
    ):
        """dpd_configure_memory_model_correction_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        memory_model_correction_type_ctype = ctypes.c_int32(memory_model_correction_type)
        error_code = self._library.RFmxSpecAn_DPDCfgApplyDPDMemoryModelCorrectionType(
            vi_ctype, selector_string_ctype, memory_model_correction_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_averaging(self, selector_string, averaging_enabled, averaging_count):
        """dpd_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        error_code = self._library.RFmxSpecAn_DPDCfgAveraging(
            vi_ctype, selector_string_ctype, averaging_enabled_ctype, averaging_count_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_dpd_model(self, selector_string, dpd_model):
        """dpd_configure_dpd_model."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dpd_model_ctype = ctypes.c_int32(dpd_model)
        error_code = self._library.RFmxSpecAn_DPDCfgDPDModel(
            vi_ctype, selector_string_ctype, dpd_model_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_dut_average_input_power(self, selector_string, dut_average_input_power):
        """dpd_configure_dut_average_input_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        dut_average_input_power_ctype = ctypes.c_double(dut_average_input_power)
        error_code = self._library.RFmxSpecAn_DPDCfgDUTAverageInputPower(
            vi_ctype, selector_string_ctype, dut_average_input_power_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_generalized_memory_polynomial_cross_terms(
        self,
        selector_string,
        memory_polynomial_lead_order,
        memory_polynomial_lag_order,
        memory_polynomial_lead_memory_depth,
        memory_polynomial_lag_memory_depth,
        memory_polynomial_maximum_lead,
        memory_polynomial_maximum_lag,
    ):
        """dpd_configure_generalized_memory_polynomial_cross_terms."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        memory_polynomial_lead_order_ctype = ctypes.c_int32(memory_polynomial_lead_order)
        memory_polynomial_lag_order_ctype = ctypes.c_int32(memory_polynomial_lag_order)
        memory_polynomial_lead_memory_depth_ctype = ctypes.c_int32(
            memory_polynomial_lead_memory_depth
        )
        memory_polynomial_lag_memory_depth_ctype = ctypes.c_int32(
            memory_polynomial_lag_memory_depth
        )
        memory_polynomial_maximum_lead_ctype = ctypes.c_int32(memory_polynomial_maximum_lead)
        memory_polynomial_maximum_lag_ctype = ctypes.c_int32(memory_polynomial_maximum_lag)
        error_code = self._library.RFmxSpecAn_DPDCfgGeneralizedMemoryPolynomialCrossTerms(
            vi_ctype,
            selector_string_ctype,
            memory_polynomial_lead_order_ctype,
            memory_polynomial_lag_order_ctype,
            memory_polynomial_lead_memory_depth_ctype,
            memory_polynomial_lag_memory_depth_ctype,
            memory_polynomial_maximum_lead_ctype,
            memory_polynomial_maximum_lag_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_iterative_dpd_enabled(self, selector_string, iterative_dpd_enabled):
        """dpd_configure_iterative_dpd_enabled."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        iterative_dpd_enabled_ctype = ctypes.c_int32(iterative_dpd_enabled)
        error_code = self._library.RFmxSpecAn_DPDCfgIterativeDPDEnabled(
            vi_ctype, selector_string_ctype, iterative_dpd_enabled_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_lookup_table_am_to_am_curve_fit(
        self, selector_string, am_to_am_curve_fit_order, am_to_am_curve_fit_type
    ):
        """dpd_configure_lookup_table_am_to_am_curve_fit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        am_to_am_curve_fit_order_ctype = ctypes.c_int32(am_to_am_curve_fit_order)
        am_to_am_curve_fit_type_ctype = ctypes.c_int32(am_to_am_curve_fit_type)
        error_code = self._library.RFmxSpecAn_DPDCfgLookupTableAMToAMCurveFit(
            vi_ctype,
            selector_string_ctype,
            am_to_am_curve_fit_order_ctype,
            am_to_am_curve_fit_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_lookup_table_am_to_pm_curve_fit(
        self, selector_string, am_to_pm_curve_fit_order, am_to_pm_curve_fit_type
    ):
        """dpd_configure_lookup_table_am_to_pm_curve_fit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        am_to_pm_curve_fit_order_ctype = ctypes.c_int32(am_to_pm_curve_fit_order)
        am_to_pm_curve_fit_type_ctype = ctypes.c_int32(am_to_pm_curve_fit_type)
        error_code = self._library.RFmxSpecAn_DPDCfgLookupTableAMToPMCurveFit(
            vi_ctype,
            selector_string_ctype,
            am_to_pm_curve_fit_order_ctype,
            am_to_pm_curve_fit_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_lookup_table_step_size(self, selector_string, step_size):
        """dpd_configure_lookup_table_step_size."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        step_size_ctype = ctypes.c_double(step_size)
        error_code = self._library.RFmxSpecAn_DPDCfgLookupTableStepSize(
            vi_ctype, selector_string_ctype, step_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_lookup_table_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """dpd_configure_lookup_table_threshold."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_enabled_ctype = ctypes.c_int32(threshold_enabled)
        threshold_level_ctype = ctypes.c_double(threshold_level)
        threshold_type_ctype = ctypes.c_int32(threshold_type)
        error_code = self._library.RFmxSpecAn_DPDCfgLookupTableThreshold(
            vi_ctype,
            selector_string_ctype,
            threshold_enabled_ctype,
            threshold_level_ctype,
            threshold_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_lookup_table_type(self, selector_string, lookup_table_type):
        """dpd_configure_lookup_table_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        lookup_table_type_ctype = ctypes.c_int32(lookup_table_type)
        error_code = self._library.RFmxSpecAn_DPDCfgLookupTableType(
            vi_ctype, selector_string_ctype, lookup_table_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_measurement_interval(self, selector_string, measurement_interval):
        """dpd_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_DPDCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_measurement_sample_rate(self, selector_string, sample_rate_mode, sample_rate):
        """dpd_configure_measurement_sample_rate."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sample_rate_mode_ctype = ctypes.c_int32(sample_rate_mode)
        sample_rate_ctype = ctypes.c_double(sample_rate)
        error_code = self._library.RFmxSpecAn_DPDCfgMeasurementSampleRate(
            vi_ctype, selector_string_ctype, sample_rate_mode_ctype, sample_rate_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_memory_polynomial(
        self, selector_string, memory_polynomial_order, memory_polynomial_memory_depth
    ):
        """dpd_configure_memory_polynomial."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        memory_polynomial_order_ctype = ctypes.c_int32(memory_polynomial_order)
        memory_polynomial_memory_depth_ctype = ctypes.c_int32(memory_polynomial_memory_depth)
        error_code = self._library.RFmxSpecAn_DPDCfgMemoryPolynomial(
            vi_ctype,
            selector_string_ctype,
            memory_polynomial_order_ctype,
            memory_polynomial_memory_depth_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_configure_synchronization_method(self, selector_string, synchronization_method):
        """dpd_configure_synchronization_method."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        synchronization_method_ctype = ctypes.c_int32(synchronization_method)
        error_code = self._library.RFmxSpecAn_DPDCfgSynchronizationMethod(
            vi_ctype, selector_string_ctype, synchronization_method_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """acp_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_ACPCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_carrier_integration_bandwidth(self, selector_string, integration_bandwidth):
        """acp_configure_carrier_integration_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integration_bandwidth_ctype = ctypes.c_double(integration_bandwidth)
        error_code = self._library.RFmxSpecAn_ACPCfgCarrierIntegrationBandwidth(
            vi_ctype, selector_string_ctype, integration_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_carrier_mode(self, selector_string, carrier_mode):
        """acp_configure_carrier_mode."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        carrier_mode_ctype = ctypes.c_int32(carrier_mode)
        error_code = self._library.RFmxSpecAn_ACPCfgCarrierMode(
            vi_ctype, selector_string_ctype, carrier_mode_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_carrier_frequency(self, selector_string, carrier_frequency):
        """acp_configure_carrier_frequency."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        carrier_frequency_ctype = ctypes.c_double(carrier_frequency)
        error_code = self._library.RFmxSpecAn_ACPCfgCarrierFrequency(
            vi_ctype, selector_string_ctype, carrier_frequency_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_carrier_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        """acp_configure_carrier_rrc_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rrc_filter_enabled_ctype = ctypes.c_int32(rrc_filter_enabled)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_ACPCfgCarrierRRCFilter(
            vi_ctype, selector_string_ctype, rrc_filter_enabled_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_fft(self, selector_string, fft_window, fft_padding):
        """acp_configure_fft."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        fft_padding_ctype = ctypes.c_double(fft_padding)
        error_code = self._library.RFmxSpecAn_ACPCfgFFT(
            vi_ctype, selector_string_ctype, fft_window_ctype, fft_padding_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_measurement_method(self, selector_string, measurement_method):
        """acp_configure_measurement_method."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_method_ctype = ctypes.c_int32(measurement_method)
        error_code = self._library.RFmxSpecAn_ACPCfgMeasurementMethod(
            vi_ctype, selector_string_ctype, measurement_method_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_noise_compensation_enabled(self, selector_string, noise_compensation_enabled):
        """acp_configure_noise_compensation_enabled."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        noise_compensation_enabled_ctype = ctypes.c_int32(noise_compensation_enabled)
        error_code = self._library.RFmxSpecAn_ACPCfgNoiseCompensationEnabled(
            vi_ctype, selector_string_ctype, noise_compensation_enabled_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_number_of_carriers(self, selector_string, number_of_carriers):
        """acp_configure_number_of_carriers."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_carriers_ctype = ctypes.c_int32(number_of_carriers)
        error_code = self._library.RFmxSpecAn_ACPCfgNumberOfCarriers(
            vi_ctype, selector_string_ctype, number_of_carriers_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_number_of_offsets(self, selector_string, number_of_offsets):
        """acp_configure_number_of_offsets."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_offsets_ctype = ctypes.c_int32(number_of_offsets)
        error_code = self._library.RFmxSpecAn_ACPCfgNumberOfOffsets(
            vi_ctype, selector_string_ctype, number_of_offsets_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_array(
        self, selector_string, offset_frequency, offset_sideband, offset_enabled
    ):
        """acp_configure_offset_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_frequency, library_type=ctypes.c_double
        )
        offset_sideband_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_sideband, library_type=ctypes.c_int32
        )
        offset_enabled_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_enabled, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["offset_frequency", "offset_sideband", "offset_enabled"],
                offset_frequency,
                offset_sideband,
                offset_enabled,
            )
        )
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetArray(
            vi_ctype,
            selector_string_ctype,
            offset_frequency_ctype,
            offset_sideband_ctype,
            offset_enabled_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_frequency_definition(
        self, selector_string, offset_frequency_definition
    ):
        """acp_configure_offset_frequency_definition."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_frequency_definition_ctype = ctypes.c_int32(offset_frequency_definition)
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetFrequencyDefinition(
            vi_ctype, selector_string_ctype, offset_frequency_definition_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_integration_bandwidth_array(
        self, selector_string, integration_bandwidth
    ):
        """acp_configure_offset_integration_bandwidth_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integration_bandwidth_ctype = _get_ctypes_pointer_for_buffer(
            value=integration_bandwidth, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(integration_bandwidth) if integration_bandwidth is not None else 0
        )
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidthArray(
            vi_ctype, selector_string_ctype, integration_bandwidth_ctype, number_of_elements_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_integration_bandwidth(self, selector_string, integration_bandwidth):
        """acp_configure_offset_integration_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integration_bandwidth_ctype = ctypes.c_double(integration_bandwidth)
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetIntegrationBandwidth(
            vi_ctype, selector_string_ctype, integration_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_power_reference_array(
        self, selector_string, offset_power_reference_carrier, offset_power_reference_specific
    ):
        """acp_configure_offset_power_reference_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_power_reference_carrier_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_power_reference_carrier, library_type=ctypes.c_int32
        )
        offset_power_reference_specific_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_power_reference_specific, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["offset_power_reference_carrier", "offset_power_reference_specific"],
                offset_power_reference_carrier,
                offset_power_reference_specific,
            )
        )
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetPowerReferenceArray(
            vi_ctype,
            selector_string_ctype,
            offset_power_reference_carrier_ctype,
            offset_power_reference_specific_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_power_reference(
        self, selector_string, offset_reference_carrier, offset_reference_specific
    ):
        """acp_configure_offset_power_reference."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_reference_carrier_ctype = ctypes.c_int32(offset_reference_carrier)
        offset_reference_specific_ctype = ctypes.c_int32(offset_reference_specific)
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetPowerReference(
            vi_ctype,
            selector_string_ctype,
            offset_reference_carrier_ctype,
            offset_reference_specific_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_relative_attenuation_array(
        self, selector_string, relative_attenuation
    ):
        """acp_configure_offset_relative_attenuation_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_attenuation_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_attenuation, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(relative_attenuation) if relative_attenuation is not None else 0
        )
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetRelativeAttenuationArray(
            vi_ctype, selector_string_ctype, relative_attenuation_ctype, number_of_elements_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_relative_attenuation(self, selector_string, relative_attenuation):
        """acp_configure_offset_relative_attenuation."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_attenuation_ctype = ctypes.c_double(relative_attenuation)
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetRelativeAttenuation(
            vi_ctype, selector_string_ctype, relative_attenuation_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_rrc_filter_array(self, selector_string, rrc_filter_enabled, rrc_alpha):
        """acp_configure_offset_rrc_filter_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rrc_filter_enabled_ctype = _get_ctypes_pointer_for_buffer(
            value=rrc_filter_enabled, library_type=ctypes.c_int32
        )
        rrc_alpha_ctype = _get_ctypes_pointer_for_buffer(
            value=rrc_alpha, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["rrc_filter_enabled", "rrc_alpha"], rrc_filter_enabled, rrc_alpha
            )
        )
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetRRCFilterArray(
            vi_ctype,
            selector_string_ctype,
            rrc_filter_enabled_ctype,
            rrc_alpha_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        """acp_configure_offset_rrc_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rrc_filter_enabled_ctype = ctypes.c_int32(rrc_filter_enabled)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_ACPCfgOffsetRRCFilter(
            vi_ctype, selector_string_ctype, rrc_filter_enabled_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_offset(
        self, selector_string, offset_frequency, offset_sideband, offset_enabled
    ):
        """acp_configure_offset."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_frequency_ctype = ctypes.c_double(offset_frequency)
        offset_sideband_ctype = ctypes.c_int32(offset_sideband)
        offset_enabled_ctype = ctypes.c_int32(offset_enabled)
        error_code = self._library.RFmxSpecAn_ACPCfgOffset(
            vi_ctype,
            selector_string_ctype,
            offset_frequency_ctype,
            offset_sideband_ctype,
            offset_enabled_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_power_units(self, selector_string, power_units):
        """acp_configure_power_units."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        power_units_ctype = ctypes.c_int32(power_units)
        error_code = self._library.RFmxSpecAn_ACPCfgPowerUnits(
            vi_ctype, selector_string_ctype, power_units_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """acp_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_ACPCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        """acp_configure_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_ACPCfgSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def acp_configure_detector(self, selector_string, detector_type, detector_points):
        """acp_configure_detector."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        detector_type_ctype = ctypes.c_int32(detector_type)
        detector_points_ctype = ctypes.c_int32(detector_points)
        error_code = self._library.RFmxSpecAn_ACPCfgDetector(
            vi_ctype, selector_string_ctype, detector_type_ctype, detector_points_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ccdf_configure_measurement_interval(self, selector_string, measurement_interval):
        """ccdf_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_CCDFCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ccdf_configure_number_of_records(self, selector_string, number_of_records):
        """ccdf_configure_number_of_records."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_records_ctype = ctypes.c_int32(number_of_records)
        error_code = self._library.RFmxSpecAn_CCDFCfgNumberOfRecords(
            vi_ctype, selector_string_ctype, number_of_records_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ccdf_configure_rbw_filter(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """ccdf_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_CCDFCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_ctype, rbw_filter_type_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def ccdf_configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """ccdf_configure_threshold."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_enabled_ctype = ctypes.c_int32(threshold_enabled)
        threshold_level_ctype = ctypes.c_double(threshold_level)
        threshold_type_ctype = ctypes.c_int32(threshold_type)
        error_code = self._library.RFmxSpecAn_CCDFCfgThreshold(
            vi_ctype,
            selector_string_ctype,
            threshold_enabled_ctype,
            threshold_level_ctype,
            threshold_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """chp_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_CHPCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_carrier_offset(self, selector_string, carrier_frequency):
        """chp_configure_carrier_offset."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        carrier_frequency_ctype = ctypes.c_double(carrier_frequency)
        error_code = self._library.RFmxSpecAn_CHPCfgCarrierOffset(
            vi_ctype, selector_string_ctype, carrier_frequency_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_fft(self, selector_string, fft_window, fft_padding):
        """chp_configure_fft."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        fft_padding_ctype = ctypes.c_double(fft_padding)
        error_code = self._library.RFmxSpecAn_CHPCfgFFT(
            vi_ctype, selector_string_ctype, fft_window_ctype, fft_padding_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_integration_bandwidth(self, selector_string, integration_bandwidth):
        """chp_configure_integration_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integration_bandwidth_ctype = ctypes.c_double(integration_bandwidth)
        error_code = self._library.RFmxSpecAn_CHPCfgIntegrationBandwidth(
            vi_ctype, selector_string_ctype, integration_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_number_of_carriers(self, selector_string, number_of_carriers):
        """chp_configure_number_of_carriers."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_carriers_ctype = ctypes.c_int32(number_of_carriers)
        error_code = self._library.RFmxSpecAn_CHPCfgNumberOfCarriers(
            vi_ctype, selector_string_ctype, number_of_carriers_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """chp_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_CHPCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        """chp_configure_rrc_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rrc_filter_enabled_ctype = ctypes.c_int32(rrc_filter_enabled)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_CHPCfgRRCFilter(
            vi_ctype, selector_string_ctype, rrc_filter_enabled_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_span(self, selector_string, span):
        """chp_configure_span."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        span_ctype = ctypes.c_double(span)
        error_code = self._library.RFmxSpecAn_CHPCfgSpan(
            vi_ctype, selector_string_ctype, span_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        """chp_configure_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_CHPCfgSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def chp_configure_detector(self, selector_string, detector_type, detector_points):
        """chp_configure_detector."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        detector_type_ctype = ctypes.c_int32(detector_type)
        detector_points_ctype = ctypes.c_int32(detector_points)
        error_code = self._library.RFmxSpecAn_CHPCfgDetector(
            vi_ctype, selector_string_ctype, detector_type_ctype, detector_points_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_auto_harmonics(self, selector_string, auto_harmonics_setup_enabled):
        """harm_configure_auto_harmonics."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        auto_harmonics_setup_enabled_ctype = ctypes.c_int32(auto_harmonics_setup_enabled)
        error_code = self._library.RFmxSpecAn_HarmCfgAutoHarmonics(
            vi_ctype, selector_string_ctype, auto_harmonics_setup_enabled_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """harm_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_HarmCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_fundamental_measurement_interval(
        self, selector_string, measurement_interval
    ):
        """harm_configure_fundamental_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_HarmCfgFundamentalMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_fundamental_rbw(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """harm_configure_fundamental_rbw."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_HarmCfgFundamentalRBW(
            vi_ctype, selector_string_ctype, rbw_ctype, rbw_filter_type_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_harmonic_array(
        self,
        selector_string,
        harmonic_order,
        harmonic_bandwidth,
        harmonic_enabled,
        harmonic_measurement_interval,
    ):
        """harm_configure_harmonic_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        harmonic_order_ctype = _get_ctypes_pointer_for_buffer(
            value=harmonic_order, library_type=ctypes.c_int32
        )
        harmonic_bandwidth_ctype = _get_ctypes_pointer_for_buffer(
            value=harmonic_bandwidth, library_type=ctypes.c_double
        )
        harmonic_enabled_ctype = _get_ctypes_pointer_for_buffer(
            value=harmonic_enabled, library_type=ctypes.c_int32
        )
        harmonic_measurement_interval_ctype = _get_ctypes_pointer_for_buffer(
            value=harmonic_measurement_interval, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                [
                    "harmonic_order",
                    "harmonic_bandwidth",
                    "harmonic_enabled",
                    "harmonic_measurement_interval",
                ],
                harmonic_order,
                harmonic_bandwidth,
                harmonic_enabled,
                harmonic_measurement_interval,
            )
        )
        error_code = self._library.RFmxSpecAn_HarmCfgHarmonicArray(
            vi_ctype,
            selector_string_ctype,
            harmonic_order_ctype,
            harmonic_bandwidth_ctype,
            harmonic_enabled_ctype,
            harmonic_measurement_interval_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_harmonic(
        self,
        selector_string,
        harmonic_order,
        harmonic_bandwidth,
        harmonic_enabled,
        harmonic_measurement_interval,
    ):
        """harm_configure_harmonic."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        harmonic_order_ctype = ctypes.c_int32(harmonic_order)
        harmonic_bandwidth_ctype = ctypes.c_double(harmonic_bandwidth)
        harmonic_enabled_ctype = ctypes.c_int32(harmonic_enabled)
        harmonic_measurement_interval_ctype = ctypes.c_double(harmonic_measurement_interval)
        error_code = self._library.RFmxSpecAn_HarmCfgHarmonic(
            vi_ctype,
            selector_string_ctype,
            harmonic_order_ctype,
            harmonic_bandwidth_ctype,
            harmonic_enabled_ctype,
            harmonic_measurement_interval_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def harm_configure_number_of_harmonics(self, selector_string, number_of_harmonics):
        """harm_configure_number_of_harmonics."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_harmonics_ctype = ctypes.c_int32(number_of_harmonics)
        error_code = self._library.RFmxSpecAn_HarmCfgNumberOfHarmonics(
            vi_ctype, selector_string_ctype, number_of_harmonics_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """sem_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_SEMCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_carrier_channel_bandwidth(self, selector_string, carrier_channel_bandwidth):
        """sem_configure_carrier_channel_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        carrier_channel_bandwidth_ctype = ctypes.c_double(carrier_channel_bandwidth)
        error_code = self._library.RFmxSpecAn_SEMCfgCarrierChannelBandwidth(
            vi_ctype, selector_string_ctype, carrier_channel_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_carrier_enabled(self, selector_string, carrier_enabled):
        """sem_configure_carrier_enabled."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        carrier_enabled_ctype = ctypes.c_int32(carrier_enabled)
        error_code = self._library.RFmxSpecAn_SEMCfgCarrierEnabled(
            vi_ctype, selector_string_ctype, carrier_enabled_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_carrier_integration_bandwidth(self, selector_string, integration_bandwidth):
        """sem_configure_carrier_integration_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integration_bandwidth_ctype = ctypes.c_double(integration_bandwidth)
        error_code = self._library.RFmxSpecAn_SEMCfgCarrierIntegrationBandwidth(
            vi_ctype, selector_string_ctype, integration_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_carrier_frequency(self, selector_string, carrier_frequency):
        """sem_configure_carrier_frequency."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        carrier_frequency_ctype = ctypes.c_double(carrier_frequency)
        error_code = self._library.RFmxSpecAn_SEMCfgCarrierFrequency(
            vi_ctype, selector_string_ctype, carrier_frequency_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_carrier_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """sem_configure_carrier_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_SEMCfgCarrierRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_carrier_rrc_filter(self, selector_string, rrc_filter_enabled, rrc_alpha):
        """sem_configure_carrier_rrc_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rrc_filter_enabled_ctype = ctypes.c_int32(rrc_filter_enabled)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_SEMCfgCarrierRRCFilter(
            vi_ctype, selector_string_ctype, rrc_filter_enabled_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_fft(self, selector_string, fft_window, fft_padding):
        """sem_configure_fft."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        fft_padding_ctype = ctypes.c_double(fft_padding)
        error_code = self._library.RFmxSpecAn_SEMCfgFFT(
            vi_ctype, selector_string_ctype, fft_window_ctype, fft_padding_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_number_of_carriers(self, selector_string, number_of_carriers):
        """sem_configure_number_of_carriers."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_carriers_ctype = ctypes.c_int32(number_of_carriers)
        error_code = self._library.RFmxSpecAn_SEMCfgNumberOfCarriers(
            vi_ctype, selector_string_ctype, number_of_carriers_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_number_of_offsets(self, selector_string, number_of_offsets):
        """sem_configure_number_of_offsets."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_offsets_ctype = ctypes.c_int32(number_of_offsets)
        error_code = self._library.RFmxSpecAn_SEMCfgNumberOfOffsets(
            vi_ctype, selector_string_ctype, number_of_offsets_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_absolute_limit_array(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        """sem_configure_offset_absolute_limit_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        absolute_limit_mode_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit_mode, library_type=ctypes.c_int32
        )
        absolute_limit_start_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit_start, library_type=ctypes.c_double
        )
        absolute_limit_stop_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit_stop, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["absolute_limit_mode", "absolute_limit_start", "absolute_limit_stop"],
                absolute_limit_mode,
                absolute_limit_start,
                absolute_limit_stop,
            )
        )
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetAbsoluteLimitArray(
            vi_ctype,
            selector_string_ctype,
            absolute_limit_mode_ctype,
            absolute_limit_start_ctype,
            absolute_limit_stop_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_absolute_limit(
        self, selector_string, absolute_limit_mode, absolute_limit_start, absolute_limit_stop
    ):
        """sem_configure_offset_absolute_limit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        absolute_limit_mode_ctype = ctypes.c_int32(absolute_limit_mode)
        absolute_limit_start_ctype = ctypes.c_double(absolute_limit_start)
        absolute_limit_stop_ctype = ctypes.c_double(absolute_limit_stop)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetAbsoluteLimit(
            vi_ctype,
            selector_string_ctype,
            absolute_limit_mode_ctype,
            absolute_limit_start_ctype,
            absolute_limit_stop_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_bandwidth_integral(self, selector_string, bandwidth_integral):
        """sem_configure_offset_bandwidth_integral."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        bandwidth_integral_ctype = ctypes.c_int32(bandwidth_integral)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetBandwidthIntegral(
            vi_ctype, selector_string_ctype, bandwidth_integral_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_frequency_array(
        self,
        selector_string,
        offset_start_frequency,
        offset_stop_frequency,
        offset_enabled,
        offset_sideband,
    ):
        """sem_configure_offset_frequency_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_start_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_start_frequency, library_type=ctypes.c_double
        )
        offset_stop_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_stop_frequency, library_type=ctypes.c_double
        )
        offset_enabled_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_enabled, library_type=ctypes.c_int32
        )
        offset_sideband_ctype = _get_ctypes_pointer_for_buffer(
            value=offset_sideband, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                [
                    "offset_start_frequency",
                    "offset_stop_frequency",
                    "offset_enabled",
                    "offset_sideband",
                ],
                offset_start_frequency,
                offset_stop_frequency,
                offset_enabled,
                offset_sideband,
            )
        )
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetFrequencyArray(
            vi_ctype,
            selector_string_ctype,
            offset_start_frequency_ctype,
            offset_stop_frequency_ctype,
            offset_enabled_ctype,
            offset_sideband_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_frequency_definition(
        self, selector_string, offset_frequency_definition
    ):
        """sem_configure_offset_frequency_definition."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_frequency_definition_ctype = ctypes.c_int32(offset_frequency_definition)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetFrequencyDefinition(
            vi_ctype, selector_string_ctype, offset_frequency_definition_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_frequency(
        self,
        selector_string,
        offset_start_frequency,
        offset_stop_frequency,
        offset_enabled,
        offset_sideband,
    ):
        """sem_configure_offset_frequency."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        offset_start_frequency_ctype = ctypes.c_double(offset_start_frequency)
        offset_stop_frequency_ctype = ctypes.c_double(offset_stop_frequency)
        offset_enabled_ctype = ctypes.c_int32(offset_enabled)
        offset_sideband_ctype = ctypes.c_int32(offset_sideband)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetFrequency(
            vi_ctype,
            selector_string_ctype,
            offset_start_frequency_ctype,
            offset_stop_frequency_ctype,
            offset_enabled_ctype,
            offset_sideband_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_limit_fail_mask(self, selector_string, limit_fail_mask):
        """sem_configure_offset_limit_fail_mask."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        limit_fail_mask_ctype = ctypes.c_int32(limit_fail_mask)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetLimitFailMask(
            vi_ctype, selector_string_ctype, limit_fail_mask_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_rbw_filter_array(
        self, selector_string, rbw_auto, rbw, rbw_filter_type
    ):
        """sem_configure_offset_rbw_filter_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = _get_ctypes_pointer_for_buffer(value=rbw_auto, library_type=ctypes.c_int32)
        rbw_ctype = _get_ctypes_pointer_for_buffer(value=rbw, library_type=ctypes.c_double)
        rbw_filter_type_ctype = _get_ctypes_pointer_for_buffer(
            value=rbw_filter_type, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["rbw_auto", "rbw", "rbw_filter_type"], rbw_auto, rbw, rbw_filter_type
            )
        )
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetRBWFilterArray(
            vi_ctype,
            selector_string_ctype,
            rbw_auto_ctype,
            rbw_ctype,
            rbw_filter_type_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """sem_configure_offset_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_relative_attenuation_array(
        self, selector_string, relative_attenuation
    ):
        """sem_configure_offset_relative_attenuation_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_attenuation_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_attenuation, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(relative_attenuation) if relative_attenuation is not None else 0
        )
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetRelativeAttenuationArray(
            vi_ctype, selector_string_ctype, relative_attenuation_ctype, number_of_elements_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_relative_attenuation(self, selector_string, relative_attenuation):
        """sem_configure_offset_relative_attenuation."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_attenuation_ctype = ctypes.c_double(relative_attenuation)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetRelativeAttenuation(
            vi_ctype, selector_string_ctype, relative_attenuation_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_relative_limit_array(
        self, selector_string, relative_limit_mode, relative_limit_start, relative_limit_stop
    ):
        """sem_configure_offset_relative_limit_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_limit_mode_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_limit_mode, library_type=ctypes.c_int32
        )
        relative_limit_start_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_limit_start, library_type=ctypes.c_double
        )
        relative_limit_stop_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_limit_stop, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["relative_limit_mode", "relative_limit_start", "relative_limit_stop"],
                relative_limit_mode,
                relative_limit_start,
                relative_limit_stop,
            )
        )
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetRelativeLimitArray(
            vi_ctype,
            selector_string_ctype,
            relative_limit_mode_ctype,
            relative_limit_start_ctype,
            relative_limit_stop_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_offset_relative_limit(
        self, selector_string, relative_limit_mode, relative_limit_start, relative_limit_stop
    ):
        """sem_configure_offset_relative_limit."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        relative_limit_mode_ctype = ctypes.c_int32(relative_limit_mode)
        relative_limit_start_ctype = ctypes.c_double(relative_limit_start)
        relative_limit_stop_ctype = ctypes.c_double(relative_limit_stop)
        error_code = self._library.RFmxSpecAn_SEMCfgOffsetRelativeLimit(
            vi_ctype,
            selector_string_ctype,
            relative_limit_mode_ctype,
            relative_limit_start_ctype,
            relative_limit_stop_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_power_units(self, selector_string, power_units):
        """sem_configure_power_units."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        power_units_ctype = ctypes.c_int32(power_units)
        error_code = self._library.RFmxSpecAn_SEMCfgPowerUnits(
            vi_ctype, selector_string_ctype, power_units_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_reference_type(self, selector_string, reference_type):
        """sem_configure_reference_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        reference_type_ctype = ctypes.c_int32(reference_type)
        error_code = self._library.RFmxSpecAn_SEMCfgReferenceType(
            vi_ctype, selector_string_ctype, reference_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def sem_configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        """sem_configure_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_SEMCfgSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """obw_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_OBWCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_bandwidth_percentage(self, selector_string, bandwidth_percentage):
        """obw_configure_bandwidth_percentage."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        bandwidth_percentage_ctype = ctypes.c_double(bandwidth_percentage)
        error_code = self._library.RFmxSpecAn_OBWCfgBandwidthPercentage(
            vi_ctype, selector_string_ctype, bandwidth_percentage_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_fft(self, selector_string, fft_window, fft_padding):
        """obw_configure_fft."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        fft_window_ctype = ctypes.c_int32(fft_window)
        fft_padding_ctype = ctypes.c_double(fft_padding)
        error_code = self._library.RFmxSpecAn_OBWCfgFFT(
            vi_ctype, selector_string_ctype, fft_window_ctype, fft_padding_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_power_units(self, selector_string, power_units):
        """obw_configure_power_units."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        power_units_ctype = ctypes.c_int32(power_units)
        error_code = self._library.RFmxSpecAn_OBWCfgPowerUnits(
            vi_ctype, selector_string_ctype, power_units_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_rbw_filter(self, selector_string, rbw_auto, rbw, rbw_filter_type):
        """obw_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_auto_ctype = ctypes.c_int32(rbw_auto)
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        error_code = self._library.RFmxSpecAn_OBWCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_auto_ctype, rbw_ctype, rbw_filter_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_span(self, selector_string, span):
        """obw_configure_span."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        span_ctype = ctypes.c_double(span)
        error_code = self._library.RFmxSpecAn_OBWCfgSpan(
            vi_ctype, selector_string_ctype, span_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def obw_configure_sweep_time(self, selector_string, sweep_time_auto, sweep_time_interval):
        """obw_configure_sweep_time."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sweep_time_auto_ctype = ctypes.c_int32(sweep_time_auto)
        sweep_time_interval_ctype = ctypes.c_double(sweep_time_interval)
        error_code = self._library.RFmxSpecAn_OBWCfgSweepTime(
            vi_ctype, selector_string_ctype, sweep_time_auto_ctype, sweep_time_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def txp_configure_averaging(
        self, selector_string, averaging_enabled, averaging_count, averaging_type
    ):
        """txp_configure_averaging."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_enabled_ctype = ctypes.c_int32(averaging_enabled)
        averaging_count_ctype = ctypes.c_int32(averaging_count)
        averaging_type_ctype = ctypes.c_int32(averaging_type)
        error_code = self._library.RFmxSpecAn_TXPCfgAveraging(
            vi_ctype,
            selector_string_ctype,
            averaging_enabled_ctype,
            averaging_count_ctype,
            averaging_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def txp_configure_measurement_interval(self, selector_string, measurement_interval):
        """txp_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_ctype = ctypes.c_double(measurement_interval)
        error_code = self._library.RFmxSpecAn_TXPCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_interval_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def txp_configure_rbw_filter(self, selector_string, rbw, rbw_filter_type, rrc_alpha):
        """txp_configure_rbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_ctype = ctypes.c_double(rbw)
        rbw_filter_type_ctype = ctypes.c_int32(rbw_filter_type)
        rrc_alpha_ctype = ctypes.c_double(rrc_alpha)
        error_code = self._library.RFmxSpecAn_TXPCfgRBWFilter(
            vi_ctype, selector_string_ctype, rbw_ctype, rbw_filter_type_ctype, rrc_alpha_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def txp_configure_threshold(
        self, selector_string, threshold_enabled, threshold_level, threshold_type
    ):
        """txp_configure_threshold."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        threshold_enabled_ctype = ctypes.c_int32(threshold_enabled)
        threshold_level_ctype = ctypes.c_double(threshold_level)
        threshold_type_ctype = ctypes.c_int32(threshold_type)
        error_code = self._library.RFmxSpecAn_TXPCfgThreshold(
            vi_ctype,
            selector_string_ctype,
            threshold_enabled_ctype,
            threshold_level_ctype,
            threshold_type_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def txp_configure_vbw_filter(self, selector_string, vbw_auto, vbw, vbw_to_rbw_ratio):
        """txp_configure_vbw_filter."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        vbw_auto_ctype = ctypes.c_int32(vbw_auto)
        vbw_ctype = ctypes.c_double(vbw)
        vbw_to_rbw_ratio_ctype = ctypes.c_double(vbw_to_rbw_ratio)
        error_code = self._library.RFmxSpecAn_TXPCfgVBWFilter(
            vi_ctype, selector_string_ctype, vbw_auto_ctype, vbw_ctype, vbw_to_rbw_ratio_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def iq_configure_acquisition(
        self, selector_string, sample_rate, number_of_records, acquisition_time, pretrigger_time
    ):
        """iq_configure_acquisition."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        sample_rate_ctype = ctypes.c_double(sample_rate)
        number_of_records_ctype = ctypes.c_int32(number_of_records)
        acquisition_time_ctype = ctypes.c_double(acquisition_time)
        pretrigger_time_ctype = ctypes.c_double(pretrigger_time)
        error_code = self._library.RFmxSpecAn_IQCfgAcquisition(
            vi_ctype,
            selector_string_ctype,
            sample_rate_ctype,
            number_of_records_ctype,
            acquisition_time_ctype,
            pretrigger_time_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def iq_configure_bandwidth(self, selector_string, bandwidth_auto, bandwidth):
        """iq_configure_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        bandwidth_auto_ctype = ctypes.c_int32(bandwidth_auto)
        bandwidth_ctype = ctypes.c_double(bandwidth)
        error_code = self._library.RFmxSpecAn_IQCfgBandwidth(
            vi_ctype, selector_string_ctype, bandwidth_auto_ctype, bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_auto_range(
        self, selector_string, start_frequency, stop_frequency, rbw_percentage
    ):
        """phasenoise_configure_auto_range."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        start_frequency_ctype = ctypes.c_double(start_frequency)
        stop_frequency_ctype = ctypes.c_double(stop_frequency)
        rbw_percentage_ctype = ctypes.c_double(rbw_percentage)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgAutoRange(
            vi_ctype,
            selector_string_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
            rbw_percentage_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_averaging_multiplier(self, selector_string, averaging_multiplier):
        """phasenoise_configure_averaging_multiplier."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        averaging_multiplier_ctype = ctypes.c_int32(averaging_multiplier)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgAveragingMultiplier(
            vi_ctype, selector_string_ctype, averaging_multiplier_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_cancellation(
        self,
        selector_string,
        cancellation_enabled,
        cancellation_threshold,
        frequency,
        reference_phase_noise,
    ):
        """phasenoise_configure_cancellation."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        cancellation_enabled_ctype = ctypes.c_int32(cancellation_enabled)
        cancellation_threshold_ctype = ctypes.c_double(cancellation_threshold)
        frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=frequency, library_type=ctypes.c_float
        )
        reference_phase_noise_ctype = _get_ctypes_pointer_for_buffer(
            value=reference_phase_noise, library_type=ctypes.c_float
        )
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["frequency", "reference_phase_noise"], frequency, reference_phase_noise
            )
        )
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgCancellation(
            vi_ctype,
            selector_string_ctype,
            cancellation_enabled_ctype,
            cancellation_threshold_ctype,
            frequency_ctype,
            reference_phase_noise_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_integrated_noise(
        self,
        selector_string,
        integrated_noise_range_definition,
        integrated_noise_start_frequency,
        integrated_noise_stop_frequency,
    ):
        """phasenoise_configure_integrated_noise."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        integrated_noise_range_definition_ctype = ctypes.c_int32(integrated_noise_range_definition)
        integrated_noise_start_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=integrated_noise_start_frequency, library_type=ctypes.c_double
        )
        integrated_noise_stop_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=integrated_noise_stop_frequency, library_type=ctypes.c_double
        )
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["integrated_noise_start_frequency", "integrated_noise_stop_frequency"],
                integrated_noise_start_frequency,
                integrated_noise_stop_frequency,
            )
        )
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgIntegratedNoise(
            vi_ctype,
            selector_string_ctype,
            integrated_noise_range_definition_ctype,
            integrated_noise_start_frequency_ctype,
            integrated_noise_stop_frequency_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_number_of_ranges(self, selector_string, number_of_ranges):
        """phasenoise_configure_number_of_ranges."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_ranges_ctype = ctypes.c_int32(number_of_ranges)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgNumberOfRanges(
            vi_ctype, selector_string_ctype, number_of_ranges_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_range_array(
        self,
        selector_string,
        range_start_frequency,
        range_stop_frequency,
        range_rbw_percentage,
        range_averaging_count,
    ):
        """phasenoise_configure_range_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        range_start_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=range_start_frequency, library_type=ctypes.c_double
        )
        range_stop_frequency_ctype = _get_ctypes_pointer_for_buffer(
            value=range_stop_frequency, library_type=ctypes.c_double
        )
        range_rbw_percentage_ctype = _get_ctypes_pointer_for_buffer(
            value=range_rbw_percentage, library_type=ctypes.c_double
        )
        range_averaging_count_ctype = _get_ctypes_pointer_for_buffer(
            value=range_averaging_count, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                [
                    "range_start_frequency",
                    "range_stop_frequency",
                    "range_rbw_percentage",
                    "range_averaging_count",
                ],
                range_start_frequency,
                range_stop_frequency,
                range_rbw_percentage,
                range_averaging_count,
            )
        )
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgRangeArray(
            vi_ctype,
            selector_string_ctype,
            range_start_frequency_ctype,
            range_stop_frequency_ctype,
            range_rbw_percentage_ctype,
            range_averaging_count_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_range_definition(self, selector_string, range_definition):
        """phasenoise_configure_range_definition."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        range_definition_ctype = ctypes.c_int32(range_definition)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgRangeDefinition(
            vi_ctype, selector_string_ctype, range_definition_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_smoothing(self, selector_string, smoothing_type, smoothing_percentage):
        """phasenoise_configure_smoothing."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        smoothing_type_ctype = ctypes.c_int32(smoothing_type)
        smoothing_percentage_ctype = ctypes.c_double(smoothing_percentage)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgSmoothing(
            vi_ctype, selector_string_ctype, smoothing_type_ctype, smoothing_percentage_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_spot_noise_frequency_list(self, selector_string, frequency_list):
        """phasenoise_configure_spot_noise_frequency_list."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        frequency_list_ctype = _get_ctypes_pointer_for_buffer(
            value=frequency_list, library_type=ctypes.c_double
        )
        array_size_ctype = ctypes.c_int32(len(frequency_list) if frequency_list is not None else 0)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgSpotNoiseFrequencyList(
            vi_ctype, selector_string_ctype, frequency_list_ctype, array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def phasenoise_configure_spur_removal(
        self, selector_string, spur_removal_enabled, peak_excursion
    ):
        """phasenoise_configure_spur_removal."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        spur_removal_enabled_ctype = ctypes.c_int32(spur_removal_enabled)
        peak_excursion_ctype = ctypes.c_double(peak_excursion)
        error_code = self._library.RFmxSpecAn_PhaseNoiseCfgSpurRemoval(
            vi_ctype, selector_string_ctype, spur_removal_enabled_ctype, peak_excursion_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_measurement_bandwidth(self, selector_string, measurement_bandwidth):
        """pavt_configure_measurement_bandwidth."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_bandwidth_ctype = ctypes.c_double(measurement_bandwidth)
        error_code = self._library.RFmxSpecAn_PAVTCfgMeasurementBandwidth(
            vi_ctype, selector_string_ctype, measurement_bandwidth_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_measurement_interval_mode(self, selector_string, measurement_interval_mode):
        """pavt_configure_measurement_interval_mode."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_interval_mode_ctype = ctypes.c_int32(measurement_interval_mode)
        error_code = self._library.RFmxSpecAn_PAVTCfgMeasurementIntervalMode(
            vi_ctype, selector_string_ctype, measurement_interval_mode_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_measurement_interval(
        self, selector_string, measurement_offset, measurement_length
    ):
        """pavt_configure_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_offset_ctype = ctypes.c_double(measurement_offset)
        measurement_length_ctype = ctypes.c_double(measurement_length)
        error_code = self._library.RFmxSpecAn_PAVTCfgMeasurementInterval(
            vi_ctype, selector_string_ctype, measurement_offset_ctype, measurement_length_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_measurement_location_type(self, selector_string, measurement_location_type):
        """pavt_configure_measurement_location_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        measurement_location_type_ctype = ctypes.c_int32(measurement_location_type)
        error_code = self._library.RFmxSpecAn_PAVTCfgMeasurementLocationType(
            vi_ctype, selector_string_ctype, measurement_location_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_number_of_segments(self, selector_string, number_of_segments):
        """pavt_configure_number_of_segments."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_segments_ctype = ctypes.c_int32(number_of_segments)
        error_code = self._library.RFmxSpecAn_PAVTCfgNumberOfSegments(
            vi_ctype, selector_string_ctype, number_of_segments_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_segment_measurement_interval_array(
        self, selector_string, segment_measurement_offset, segment_measurement_length
    ):
        """pavt_configure_segment_measurement_interval_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        segment_measurement_offset_ctype = _get_ctypes_pointer_for_buffer(
            value=segment_measurement_offset, library_type=ctypes.c_double
        )
        segment_measurement_length_ctype = _get_ctypes_pointer_for_buffer(
            value=segment_measurement_length, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["segment_measurement_offset", "segment_measurement_length"],
                segment_measurement_offset,
                segment_measurement_length,
            )
        )
        error_code = self._library.RFmxSpecAn_PAVTCfgSegmentMeasurementIntervalArray(
            vi_ctype,
            selector_string_ctype,
            segment_measurement_offset_ctype,
            segment_measurement_length_ctype,
            number_of_elements_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_segment_measurement_interval(
        self, selector_string, segment_measurement_offset, segment_measurement_length
    ):
        """pavt_configure_segment_measurement_interval."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        segment_measurement_offset_ctype = ctypes.c_double(segment_measurement_offset)
        segment_measurement_length_ctype = ctypes.c_double(segment_measurement_length)
        error_code = self._library.RFmxSpecAn_PAVTCfgSegmentMeasurementInterval(
            vi_ctype,
            selector_string_ctype,
            segment_measurement_offset_ctype,
            segment_measurement_length_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_segment_start_time_list(self, selector_string, segment_start_time):
        """pavt_configure_segment_start_time_list."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        segment_start_time_ctype = _get_ctypes_pointer_for_buffer(
            value=segment_start_time, library_type=ctypes.c_double
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(segment_start_time) if segment_start_time is not None else 0
        )
        error_code = self._library.RFmxSpecAn_PAVTCfgSegmentStartTimeList(
            vi_ctype, selector_string_ctype, segment_start_time_ctype, number_of_elements_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_segment_type_array(self, selector_string, segment_type):
        """pavt_configure_segment_type_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        segment_type_ctype = _get_ctypes_pointer_for_buffer(
            value=segment_type, library_type=ctypes.c_int32
        )
        number_of_elements_ctype = ctypes.c_int32(
            len(segment_type) if segment_type is not None else 0
        )
        error_code = self._library.RFmxSpecAn_PAVTCfgSegmentTypeArray(
            vi_ctype, selector_string_ctype, segment_type_ctype, number_of_elements_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def pavt_configure_segment_type(self, selector_string, segment_type):
        """pavt_configure_segment_type."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        segment_type_ctype = ctypes.c_int32(segment_type)
        error_code = self._library.RFmxSpecAn_PAVTCfgSegmentType(
            vi_ctype, selector_string_ctype, segment_type_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def powerlist_configure_rbw_filter_array(
        self, selector_string, rbw, rbw_filter_type, rrc_alpha
    ):
        """powerlist_configure_rbw_filter_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        rbw_ctype = _get_ctypes_pointer_for_buffer(value=rbw, library_type=ctypes.c_double)
        rbw_filter_type_ctype = _get_ctypes_pointer_for_buffer(
            value=rbw_filter_type, library_type=ctypes.c_int32
        )
        rrc_alpha_ctype = _get_ctypes_pointer_for_buffer(
            value=rrc_alpha, library_type=ctypes.c_double
        )
        array_size_ctype = ctypes.c_int32(
            _helper.validate_array_parameter_sizes_are_equal(
                ["rbw", "rbw_filter_type", "rrc_alpha"], rbw, rbw_filter_type, rrc_alpha
            )
        )
        error_code = self._library.RFmxSpecAn_PowerListCfgRBWFilterArray(
            vi_ctype,
            selector_string_ctype,
            rbw_ctype,
            rbw_filter_type_ctype,
            rrc_alpha_ctype,
            array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def configure_external_attenuation(self, selector_string, external_attenuation):
        """configure_external_attenuation."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        external_attenuation_ctype = ctypes.c_double(external_attenuation)
        error_code = self._library.RFmxSpecAn_CfgExternalAttenuation(
            vi_ctype, selector_string_ctype, external_attenuation_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def configure_frequency(self, selector_string, center_frequency):
        """configure_frequency."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        center_frequency_ctype = ctypes.c_double(center_frequency)
        error_code = self._library.RFmxSpecAn_CfgFrequency(
            vi_ctype, selector_string_ctype, center_frequency_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def configure_reference_level(self, selector_string, reference_level):
        """configure_reference_level."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        reference_level_ctype = ctypes.c_double(reference_level)
        error_code = self._library.RFmxSpecAn_CfgReferenceLevel(
            vi_ctype, selector_string_ctype, reference_level_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def configure_rf(
        self, selector_string, center_frequency, reference_level, external_attenuation
    ):
        """configure_rf."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        center_frequency_ctype = ctypes.c_double(center_frequency)
        reference_level_ctype = ctypes.c_double(reference_level)
        external_attenuation_ctype = ctypes.c_double(external_attenuation)
        error_code = self._library.RFmxSpecAn_CfgRF(
            vi_ctype,
            selector_string_ctype,
            center_frequency_ctype,
            reference_level_ctype,
            external_attenuation_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def im_fetch_fundamental_measurement(self, selector_string, timeout):
        """im_fetch_fundamental_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        lower_tone_power_ctype = ctypes.c_double()
        upper_tone_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_IMFetchFundamentalMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            lower_tone_power_ctype,
            upper_tone_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return lower_tone_power_ctype.value, upper_tone_power_ctype.value, error_code

    def im_fetch_intercept_power(self, selector_string, timeout):
        """im_fetch_intercept_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        intermod_order_ctype = ctypes.c_int32()
        worst_case_output_intercept_power_ctype = ctypes.c_double()
        lower_output_intercept_power_ctype = ctypes.c_double()
        upper_output_intercept_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_IMFetchInterceptPower(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            intermod_order_ctype,
            worst_case_output_intercept_power_ctype,
            lower_output_intercept_power_ctype,
            upper_output_intercept_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            intermod_order_ctype.value,
            worst_case_output_intercept_power_ctype.value,
            lower_output_intercept_power_ctype.value,
            upper_output_intercept_power_ctype.value,
            error_code,
        )

    def im_fetch_intermod_measurement(self, selector_string, timeout):
        """im_fetch_intermod_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        intermod_order_ctype = ctypes.c_int32()
        lower_intermod_absolute_power_ctype = ctypes.c_double()
        upper_intermod_absolute_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_IMFetchIntermodMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            intermod_order_ctype,
            lower_intermod_absolute_power_ctype,
            upper_intermod_absolute_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            intermod_order_ctype.value,
            lower_intermod_absolute_power_ctype.value,
            upper_intermod_absolute_power_ctype.value,
            error_code,
        )

    def fcnt_fetch_allan_deviation(self, selector_string, timeout):
        """fcnt_fetch_allan_deviation."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        allan_deviation_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_FCntFetchAllanDeviation(
            vi_ctype, selector_string_ctype, timeout_ctype, allan_deviation_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return allan_deviation_ctype.value, error_code

    def fcnt_fetch_measurement(self, selector_string, timeout):
        """fcnt_fetch_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        average_relative_frequency_ctype = ctypes.c_double()
        average_absolute_frequency_ctype = ctypes.c_double()
        mean_phase_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_FCntFetchMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            average_relative_frequency_ctype,
            average_absolute_frequency_ctype,
            mean_phase_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            average_relative_frequency_ctype.value,
            average_absolute_frequency_ctype.value,
            mean_phase_ctype.value,
            error_code,
        )

    def fcnt_read(self, selector_string, timeout):
        """fcnt_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        average_relative_frequency_ctype = ctypes.c_double()
        average_absolute_frequency_ctype = ctypes.c_double()
        mean_phase_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_FCntRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            average_relative_frequency_ctype,
            average_absolute_frequency_ctype,
            mean_phase_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            average_relative_frequency_ctype.value,
            average_absolute_frequency_ctype.value,
            mean_phase_ctype.value,
            error_code,
        )

    def spectrum_fetch_measurement(self, selector_string, timeout):
        """spectrum_fetch_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        peak_amplitude_ctype = ctypes.c_double()
        peak_frequency_ctype = ctypes.c_double()
        frequency_resolution_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SpectrumFetchMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            peak_amplitude_ctype,
            peak_frequency_ctype,
            frequency_resolution_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            peak_amplitude_ctype.value,
            peak_frequency_ctype.value,
            frequency_resolution_ctype.value,
            error_code,
        )

    def spur_fetch_measurement_status(self, selector_string, timeout):
        """spur_fetch_measurement_status."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        measurement_status_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_SpurFetchMeasurementStatus(
            vi_ctype, selector_string_ctype, timeout_ctype, measurement_status_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return enums.SpurMeasurementStatus(measurement_status_ctype.value), error_code

    def spur_fetch_range_status(self, selector_string, timeout):
        """spur_fetch_range_status."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        range_status_ctype = ctypes.c_int32()
        detected_spurs_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_SpurFetchRangeStatus(
            vi_ctype, selector_string_ctype, timeout_ctype, range_status_ctype, detected_spurs_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.SpurRangeStatus(range_status_ctype.value),
            detected_spurs_ctype.value,
            error_code,
        )

    def spur_fetch_spur_measurement(self, selector_string, timeout):
        """spur_fetch_spur_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        spur_frequency_ctype = ctypes.c_double()
        spur_amplitude_ctype = ctypes.c_double()
        spur_margin_ctype = ctypes.c_double()
        spur_absolute_limit_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SpurFetchSpurMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            spur_frequency_ctype,
            spur_amplitude_ctype,
            spur_margin_ctype,
            spur_absolute_limit_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            spur_frequency_ctype.value,
            spur_amplitude_ctype.value,
            spur_margin_ctype.value,
            spur_absolute_limit_ctype.value,
            error_code,
        )

    def ampm_fetch_curve_fit_residual(self, selector_string, timeout):
        """ampm_fetch_curve_fit_residual."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        am_to_am_residual_ctype = ctypes.c_double()
        am_to_pm_residual_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_AMPMFetchCurveFitResidual(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            am_to_am_residual_ctype,
            am_to_pm_residual_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return am_to_am_residual_ctype.value, am_to_pm_residual_ctype.value, error_code

    def ampm_fetch_dut_characteristics(self, selector_string, timeout):
        """ampm_fetch_dut_characteristics."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        mean_linear_gain_ctype = ctypes.c_double()
        one_db_compression_point_ctype = ctypes.c_double()
        mean_rms_evm_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_AMPMFetchDUTCharacteristics(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            mean_linear_gain_ctype,
            one_db_compression_point_ctype,
            mean_rms_evm_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            mean_linear_gain_ctype.value,
            one_db_compression_point_ctype.value,
            mean_rms_evm_ctype.value,
            error_code,
        )

    def ampm_fetch_error(self, selector_string, timeout):
        """ampm_fetch_error."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        gain_error_range_ctype = ctypes.c_double()
        phase_error_range_ctype = ctypes.c_double()
        mean_phase_error_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_AMPMFetchError(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            gain_error_range_ctype,
            phase_error_range_ctype,
            mean_phase_error_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            gain_error_range_ctype.value,
            phase_error_range_ctype.value,
            mean_phase_error_ctype.value,
            error_code,
        )

    def dpd_fetch_pre_cfr_papr(self, selector_string, timeout):
        """dpd_fetch_pre_cfr_papr."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        pre_cfr_papr_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_DPDFetchApplyDPDPreCFRPAPR(
            vi_ctype, selector_string_ctype, timeout_ctype, pre_cfr_papr_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return pre_cfr_papr_ctype.value, error_code

    def dpd_fetch_average_gain(self, selector_string, timeout):
        """dpd_fetch_average_gain."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        average_gain_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_DPDFetchAverageGain(
            vi_ctype, selector_string_ctype, timeout_ctype, average_gain_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return average_gain_ctype.value, error_code

    def dpd_fetch_nmse(self, selector_string, timeout):
        """dpd_fetch_nmse."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        nmse_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_DPDFetchNMSE(
            vi_ctype, selector_string_ctype, timeout_ctype, nmse_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return nmse_ctype.value, error_code

    def acp_fetch_carrier_measurement(self, selector_string, timeout):
        """acp_fetch_carrier_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        absolute_power_ctype = ctypes.c_double()
        total_relative_power_ctype = ctypes.c_double()
        carrier_offset_ctype = ctypes.c_double()
        integration_bandwidth_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_ACPFetchCarrierMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            absolute_power_ctype,
            total_relative_power_ctype,
            carrier_offset_ctype,
            integration_bandwidth_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            absolute_power_ctype.value,
            total_relative_power_ctype.value,
            carrier_offset_ctype.value,
            integration_bandwidth_ctype.value,
            error_code,
        )

    def acp_fetch_frequency_resolution(self, selector_string, timeout):
        """acp_fetch_frequency_resolution."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        frequency_resolution_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_ACPFetchFrequencyResolution(
            vi_ctype, selector_string_ctype, timeout_ctype, frequency_resolution_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return frequency_resolution_ctype.value, error_code

    def acp_fetch_offset_measurement(self, selector_string, timeout):
        """acp_fetch_offset_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        lower_relative_power_ctype = ctypes.c_double()
        upper_relative_power_ctype = ctypes.c_double()
        lower_absolute_power_ctype = ctypes.c_double()
        upper_absolute_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_ACPFetchOffsetMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            lower_relative_power_ctype,
            upper_relative_power_ctype,
            lower_absolute_power_ctype,
            upper_absolute_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            lower_relative_power_ctype.value,
            upper_relative_power_ctype.value,
            lower_absolute_power_ctype.value,
            upper_absolute_power_ctype.value,
            error_code,
        )

    def acp_fetch_total_carrier_power(self, selector_string, timeout):
        """acp_fetch_total_carrier_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_carrier_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_ACPFetchTotalCarrierPower(
            vi_ctype, selector_string_ctype, timeout_ctype, total_carrier_power_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return total_carrier_power_ctype.value, error_code

    def acp_read(self, selector_string, timeout):
        """acp_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        carrier_absolute_power_ctype = ctypes.c_double()
        offset_ch0_lower_relative_power_ctype = ctypes.c_double()
        offset_ch0_upper_relative_power_ctype = ctypes.c_double()
        offset_ch1_lower_relative_power_ctype = ctypes.c_double()
        offset_ch1_upper_relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_ACPRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            carrier_absolute_power_ctype,
            offset_ch0_lower_relative_power_ctype,
            offset_ch0_upper_relative_power_ctype,
            offset_ch1_lower_relative_power_ctype,
            offset_ch1_upper_relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            carrier_absolute_power_ctype.value,
            offset_ch0_lower_relative_power_ctype.value,
            offset_ch0_upper_relative_power_ctype.value,
            offset_ch1_lower_relative_power_ctype.value,
            offset_ch1_upper_relative_power_ctype.value,
            error_code,
        )

    def ccdf_fetch_basic_power_probabilities(self, selector_string, timeout):
        """ccdf_fetch_basic_power_probabilities."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        ten_percent_power_ctype = ctypes.c_double()
        one_percent_power_ctype = ctypes.c_double()
        one_tenth_percent_power_ctype = ctypes.c_double()
        one_hundredth_percent_power_ctype = ctypes.c_double()
        one_thousandth_percent_power_ctype = ctypes.c_double()
        one_ten_thousandth_percent_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_CCDFFetchBasicPowerProbabilities(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            ten_percent_power_ctype,
            one_percent_power_ctype,
            one_tenth_percent_power_ctype,
            one_hundredth_percent_power_ctype,
            one_thousandth_percent_power_ctype,
            one_ten_thousandth_percent_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            ten_percent_power_ctype.value,
            one_percent_power_ctype.value,
            one_tenth_percent_power_ctype.value,
            one_hundredth_percent_power_ctype.value,
            one_thousandth_percent_power_ctype.value,
            one_ten_thousandth_percent_power_ctype.value,
            error_code,
        )

    def ccdf_fetch_power(self, selector_string, timeout):
        """ccdf_fetch_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        mean_power_ctype = ctypes.c_double()
        mean_power_percentile_ctype = ctypes.c_double()
        peak_power_ctype = ctypes.c_double()
        measured_samples_count_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_CCDFFetchPower(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            mean_power_ctype,
            mean_power_percentile_ctype,
            peak_power_ctype,
            measured_samples_count_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            mean_power_ctype.value,
            mean_power_percentile_ctype.value,
            peak_power_ctype.value,
            measured_samples_count_ctype.value,
            error_code,
        )

    def ccdf_read(self, selector_string, timeout):
        """ccdf_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        mean_power_ctype = ctypes.c_double()
        mean_power_percentile_ctype = ctypes.c_double()
        peak_power_ctype = ctypes.c_double()
        measured_samples_count_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_CCDFRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            mean_power_ctype,
            mean_power_percentile_ctype,
            peak_power_ctype,
            measured_samples_count_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            mean_power_ctype.value,
            mean_power_percentile_ctype.value,
            peak_power_ctype.value,
            measured_samples_count_ctype.value,
            error_code,
        )

    def chp_fetch_total_carrier_power(self, selector_string, timeout):
        """chp_fetch_total_carrier_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_carrier_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_CHPFetchTotalCarrierPower(
            vi_ctype, selector_string_ctype, timeout_ctype, total_carrier_power_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return total_carrier_power_ctype.value, error_code

    def chp_read(self, selector_string, timeout):
        """chp_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        absolute_power_ctype = ctypes.c_double()
        psd_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_CHPRead(
            vi_ctype, selector_string_ctype, timeout_ctype, absolute_power_ctype, psd_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return absolute_power_ctype.value, psd_ctype.value, error_code

    def harm_fetch_harmonic_measurement(self, selector_string, timeout):
        """harm_fetch_harmonic_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        average_relative_power_ctype = ctypes.c_double()
        average_absolute_power_ctype = ctypes.c_double()
        rbw_ctype = ctypes.c_double()
        frequency_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_HarmFetchHarmonicMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            average_relative_power_ctype,
            average_absolute_power_ctype,
            rbw_ctype,
            frequency_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            average_relative_power_ctype.value,
            average_absolute_power_ctype.value,
            rbw_ctype.value,
            frequency_ctype.value,
            error_code,
        )

    def harm_fetch_total_harmonic_distortion(self, selector_string, timeout):
        """harm_fetch_total_harmonic_distortion."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_harmonic_distortion_ctype = ctypes.c_double()
        average_fundamental_power_ctype = ctypes.c_double()
        fundamental_frequency_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_HarmFetchTHD(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            total_harmonic_distortion_ctype,
            average_fundamental_power_ctype,
            fundamental_frequency_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            total_harmonic_distortion_ctype.value,
            average_fundamental_power_ctype.value,
            fundamental_frequency_ctype.value,
            error_code,
        )

    def harm_read(self, selector_string, timeout):
        """harm_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_harmonic_distortion_ctype = ctypes.c_double()
        average_fundamental_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_HarmRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            total_harmonic_distortion_ctype,
            average_fundamental_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            total_harmonic_distortion_ctype.value,
            average_fundamental_power_ctype.value,
            error_code,
        )

    def marker_fetch_xy(self, selector_string):
        """marker_fetch_xy."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        marker_x_location_ctype = ctypes.c_double()
        marker_y_location_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_MarkerFetchXY(
            vi_ctype, selector_string_ctype, marker_x_location_ctype, marker_y_location_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return marker_x_location_ctype.value, marker_y_location_ctype.value, error_code

    def marker_next_peak(self, selector_string, next_peak):
        """marker_next_peak."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        next_peak_ctype = ctypes.c_int32(next_peak)
        next_peak_found_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_MarkerNextPeak(
            vi_ctype, selector_string_ctype, next_peak_ctype, next_peak_found_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return bool(next_peak_found_ctype.value), error_code

    def marker_peak_search(self, selector_string):
        """marker_peak_search."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        number_of_peaks_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_MarkerPeakSearch(
            vi_ctype, selector_string_ctype, number_of_peaks_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return number_of_peaks_ctype.value, error_code

    def marker_fetch_function_value(self, selector_string):
        """marker_fetch_function_value."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        function_value_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_MarkerFetchFunctionValue(
            vi_ctype, selector_string_ctype, function_value_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return function_value_ctype.value, error_code

    def sem_fetch_carrier_measurement(self, selector_string, timeout):
        """sem_fetch_carrier_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        absolute_power_ctype = ctypes.c_double()
        peak_absolute_power_ctype = ctypes.c_double()
        peak_frequency_ctype = ctypes.c_double()
        total_relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchCarrierMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            absolute_power_ctype,
            peak_absolute_power_ctype,
            peak_frequency_ctype,
            total_relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            absolute_power_ctype.value,
            peak_absolute_power_ctype.value,
            peak_frequency_ctype.value,
            total_relative_power_ctype.value,
            error_code,
        )

    def sem_fetch_composite_measurement_status(self, selector_string, timeout):
        """sem_fetch_composite_measurement_status."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        composite_measurement_status_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_SEMFetchCompositeMeasurementStatus(
            vi_ctype, selector_string_ctype, timeout_ctype, composite_measurement_status_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.SemCompositeMeasurementStatus(composite_measurement_status_ctype.value),
            error_code,
        )

    def sem_fetch_frequency_resolution(self, selector_string, timeout):
        """sem_fetch_frequency_resolution."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        frequency_resolution_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchFrequencyResolution(
            vi_ctype, selector_string_ctype, timeout_ctype, frequency_resolution_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return frequency_resolution_ctype.value, error_code

    def sem_fetch_lower_offset_margin(self, selector_string, timeout):
        """sem_fetch_lower_offset_margin."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        measurement_status_ctype = ctypes.c_int32()
        margin_ctype = ctypes.c_double()
        margin_frequency_ctype = ctypes.c_double()
        margin_absolute_power_ctype = ctypes.c_double()
        margin_relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchLowerOffsetMargin(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            measurement_status_ctype,
            margin_ctype,
            margin_frequency_ctype,
            margin_absolute_power_ctype,
            margin_relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.SemLowerOffsetMeasurementStatus(measurement_status_ctype.value),
            margin_ctype.value,
            margin_frequency_ctype.value,
            margin_absolute_power_ctype.value,
            margin_relative_power_ctype.value,
            error_code,
        )

    def sem_fetch_lower_offset_power(self, selector_string, timeout):
        """sem_fetch_lower_offset_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_absolute_power_ctype = ctypes.c_double()
        total_relative_power_ctype = ctypes.c_double()
        peak_absolute_power_ctype = ctypes.c_double()
        peak_frequency_ctype = ctypes.c_double()
        peak_relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchLowerOffsetPower(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            total_absolute_power_ctype,
            total_relative_power_ctype,
            peak_absolute_power_ctype,
            peak_frequency_ctype,
            peak_relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            total_absolute_power_ctype.value,
            total_relative_power_ctype.value,
            peak_absolute_power_ctype.value,
            peak_frequency_ctype.value,
            peak_relative_power_ctype.value,
            error_code,
        )

    def sem_fetch_total_carrier_power(self, selector_string, timeout):
        """sem_fetch_total_carrier_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_carrier_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchTotalCarrierPower(
            vi_ctype, selector_string_ctype, timeout_ctype, total_carrier_power_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return total_carrier_power_ctype.value, error_code

    def sem_fetch_upper_offset_margin(self, selector_string, timeout):
        """sem_fetch_upper_offset_margin."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        measurement_status_ctype = ctypes.c_int32()
        margin_ctype = ctypes.c_double()
        margin_frequency_ctype = ctypes.c_double()
        margin_absolute_power_ctype = ctypes.c_double()
        margin_relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchUpperOffsetMargin(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            measurement_status_ctype,
            margin_ctype,
            margin_frequency_ctype,
            margin_absolute_power_ctype,
            margin_relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            enums.SemUpperOffsetMeasurementStatus(measurement_status_ctype.value),
            margin_ctype.value,
            margin_frequency_ctype.value,
            margin_absolute_power_ctype.value,
            margin_relative_power_ctype.value,
            error_code,
        )

    def sem_fetch_upper_offset_power(self, selector_string, timeout):
        """sem_fetch_upper_offset_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        total_absolute_power_ctype = ctypes.c_double()
        total_relative_power_ctype = ctypes.c_double()
        peak_absolute_power_ctype = ctypes.c_double()
        peak_frequency_ctype = ctypes.c_double()
        peak_relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_SEMFetchUpperOffsetPower(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            total_absolute_power_ctype,
            total_relative_power_ctype,
            peak_absolute_power_ctype,
            peak_frequency_ctype,
            peak_relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            total_absolute_power_ctype.value,
            total_relative_power_ctype.value,
            peak_absolute_power_ctype.value,
            peak_frequency_ctype.value,
            peak_relative_power_ctype.value,
            error_code,
        )

    def obw_fetch_measurement(self, selector_string, timeout):
        """obw_fetch_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        occupied_bandwidth_ctype = ctypes.c_double()
        average_power_ctype = ctypes.c_double()
        frequency_resolution_ctype = ctypes.c_double()
        start_frequency_ctype = ctypes.c_double()
        stop_frequency_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_OBWFetchMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            occupied_bandwidth_ctype,
            average_power_ctype,
            frequency_resolution_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            occupied_bandwidth_ctype.value,
            average_power_ctype.value,
            frequency_resolution_ctype.value,
            start_frequency_ctype.value,
            stop_frequency_ctype.value,
            error_code,
        )

    def obw_read(self, selector_string, timeout):
        """obw_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        occupied_bandwidth_ctype = ctypes.c_double()
        average_power_ctype = ctypes.c_double()
        frequency_resolution_ctype = ctypes.c_double()
        start_frequency_ctype = ctypes.c_double()
        stop_frequency_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_OBWRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            occupied_bandwidth_ctype,
            average_power_ctype,
            frequency_resolution_ctype,
            start_frequency_ctype,
            stop_frequency_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            occupied_bandwidth_ctype.value,
            average_power_ctype.value,
            frequency_resolution_ctype.value,
            start_frequency_ctype.value,
            stop_frequency_ctype.value,
            error_code,
        )

    def txp_fetch_measurement(self, selector_string, timeout):
        """txp_fetch_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        average_mean_power_ctype = ctypes.c_double()
        peak_to_average_ratio_ctype = ctypes.c_double()
        maximum_power_ctype = ctypes.c_double()
        minimum_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_TXPFetchMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            average_mean_power_ctype,
            peak_to_average_ratio_ctype,
            maximum_power_ctype,
            minimum_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            average_mean_power_ctype.value,
            peak_to_average_ratio_ctype.value,
            maximum_power_ctype.value,
            minimum_power_ctype.value,
            error_code,
        )

    def txp_read(self, selector_string, timeout):
        """txp_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        average_mean_power_ctype = ctypes.c_double()
        peak_to_average_ratio_ctype = ctypes.c_double()
        maximum_power_ctype = ctypes.c_double()
        minimum_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_TXPRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            average_mean_power_ctype,
            peak_to_average_ratio_ctype,
            maximum_power_ctype,
            minimum_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            average_mean_power_ctype.value,
            peak_to_average_ratio_ctype.value,
            maximum_power_ctype.value,
            minimum_power_ctype.value,
            error_code,
        )

    def iq_get_records_done(self, selector_string):
        """iq_get_records_done."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        records_done_ctype = ctypes.c_int32()
        error_code = self._library.RFmxSpecAn_IQGetRecordsDone(
            vi_ctype, selector_string_ctype, records_done_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return records_done_ctype.value, error_code

    def phasenoise_fetch_carrier_measurement(self, selector_string, timeout):
        """phasenoise_fetch_carrier_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        carrier_frequency_ctype = ctypes.c_double()
        carrier_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchCarrierMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            carrier_frequency_ctype,
            carrier_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return carrier_frequency_ctype.value, carrier_power_ctype.value, error_code

    def pavt_fetch_phase_and_amplitude(self, selector_string, timeout):
        """pavt_fetch_phase_and_amplitude."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        mean_relative_phase_ctype = ctypes.c_double()
        mean_relative_amplitude_ctype = ctypes.c_double()
        mean_absolute_phase_ctype = ctypes.c_double()
        mean_absolute_amplitude_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_PAVTFetchPhaseAndAmplitude(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            mean_relative_phase_ctype,
            mean_relative_amplitude_ctype,
            mean_absolute_phase_ctype,
            mean_absolute_amplitude_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            mean_relative_phase_ctype.value,
            mean_relative_amplitude_ctype.value,
            mean_absolute_phase_ctype.value,
            mean_absolute_amplitude_ctype.value,
            error_code,
        )

    def chp_fetch_carrier_measurement(self, selector_string, timeout):
        """chp_fetch_carrier_measurement."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        absolute_power_ctype = ctypes.c_double()
        psd_ctype = ctypes.c_double()
        relative_power_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_CHPFetchCarrierMeasurement(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            absolute_power_ctype,
            psd_ctype,
            relative_power_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return absolute_power_ctype.value, psd_ctype.value, relative_power_ctype.value, error_code

    def im_fetch_intercept_power_array(self, selector_string, timeout):
        """im_fetch_intercept_power_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IMFetchInterceptPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        intermod_order_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )
        worst_case_output_intercept_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        lower_output_intercept_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        upper_output_intercept_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IMFetchInterceptPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            intermod_order_ctype,
            worst_case_output_intercept_power_ctype,
            lower_output_intercept_power_ctype,
            upper_output_intercept_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            intermod_order_ctype[:],
            worst_case_output_intercept_power_ctype[:],
            lower_output_intercept_power_ctype[:],
            upper_output_intercept_power_ctype[:],
            error_code,
        )

    def im_fetch_intermod_measurement_array(self, selector_string, timeout):
        """im_fetch_intermod_measurement_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IMFetchIntermodMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        intermod_order_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )
        lower_intermod_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        upper_intermod_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IMFetchIntermodMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            intermod_order_ctype,
            lower_intermod_absolute_power_ctype,
            upper_intermod_absolute_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            intermod_order_ctype[:],
            lower_intermod_absolute_power_ctype[:],
            upper_intermod_absolute_power_ctype[:],
            error_code,
        )

    def im_fetch_spectrum(self, selector_string, timeout, spectrum_index, spectrum):
        """im_fetch_spectrum."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        spectrum_index_ctype = ctypes.c_int32(spectrum_index)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IMFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            spectrum_index_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IMFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            spectrum_index_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def nf_fetch_analyzer_noise_figure(self, selector_string, timeout):
        """nf_fetch_analyzer_noise_figure."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_NFFetchAnalyzerNoiseFigure(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        analyzer_noise_figure_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_NFFetchAnalyzerNoiseFigure(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            analyzer_noise_figure_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return analyzer_noise_figure_ctype[:], error_code

    def nf_fetch_cold_source_power(self, selector_string, timeout):
        """nf_fetch_cold_source_power."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_NFFetchColdSourcePower(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        cold_source_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_NFFetchColdSourcePower(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            cold_source_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return cold_source_power_ctype[:], error_code

    def nf_fetch_dut_noise_figure_and_gain(self, selector_string, timeout):
        """nf_fetch_dut_noise_figure_and_gain."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        dut_noise_figure_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        dut_noise_temperature_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        dut_gain_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_NFFetchDUTNoiseFigureAndGain(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            dut_noise_figure_ctype,
            dut_noise_temperature_ctype,
            dut_gain_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            dut_noise_figure_ctype[:],
            dut_noise_temperature_ctype[:],
            dut_gain_ctype[:],
            error_code,
        )

    def nf_fetch_y_factor_powers(self, selector_string, timeout):
        """nf_fetch_y_factor_powers."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_NFFetchYFactorPowers(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        hot_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        cold_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_NFFetchYFactorPowers(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            hot_power_ctype,
            cold_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return hot_power_ctype[:], cold_power_ctype[:], error_code

    def nf_fetch_y_factors(self, selector_string, timeout):
        """nf_fetch_y_factors."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_NFFetchYFactors(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        measurement_y_factor_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        calibration_y_factor_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_NFFetchYFactors(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            measurement_y_factor_ctype,
            calibration_y_factor_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return measurement_y_factor_ctype[:], calibration_y_factor_ctype[:], error_code

    def fcnt_fetch_frequency_trace(self, selector_string, timeout, frequency_trace):
        """fcnt_fetch_frequency_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_FCntFetchFrequencyTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(frequency_trace, "frequency_trace", "float32")
        if len(frequency_trace) != actual_array_size_ctype.value:
            frequency_trace.resize((actual_array_size_ctype.value,), refcheck=False)
        frequency_trace_ctype = _get_ctypes_pointer_for_buffer(
            value=frequency_trace, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_FCntFetchFrequencyTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            frequency_trace_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def fcnt_fetch_phase_trace(self, selector_string, timeout, phase_trace):
        """fcnt_fetch_phase_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_FCntFetchPhaseTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(phase_trace, "phase_trace", "float32")
        if len(phase_trace) != actual_array_size_ctype.value:
            phase_trace.resize((actual_array_size_ctype.value,), refcheck=False)
        phase_trace_ctype = _get_ctypes_pointer_for_buffer(
            value=phase_trace, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_FCntFetchPhaseTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            phase_trace_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def fcnt_fetch_power_trace(self, selector_string, timeout, power_trace):
        """fcnt_fetch_power_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_FCntFetchPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(power_trace, "power_trace", "float32")
        if len(power_trace) != actual_array_size_ctype.value:
            power_trace.resize((actual_array_size_ctype.value,), refcheck=False)
        power_trace_ctype = _get_ctypes_pointer_for_buffer(
            value=power_trace, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_FCntFetchPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            power_trace_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def spectrum_fetch_power_trace(self, selector_string, timeout, power):
        """spectrum_fetch_power_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpectrumFetchPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(power, "power", "float32")
        if len(power) != actual_array_size_ctype.value:
            power.resize((actual_array_size_ctype.value,), refcheck=False)
        power_ctype = _get_ctypes_pointer_for_buffer(value=power, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpectrumFetchPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def spectrum_fetch_spectrum(self, selector_string, timeout, spectrum):
        """spectrum_fetch_spectrum."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpectrumFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpectrumFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def spectrum_read(self, selector_string, timeout, spectrum):
        """spectrum_read."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpectrumRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpectrumRead(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def spur_fetch_all_spurs(self, selector_string, timeout):
        """spur_fetch_all_spurs."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpurFetchAllSpurs(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        spur_frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_amplitude_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_margin_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_absolute_limit_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_range_index_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpurFetchAllSpurs(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            spur_frequency_ctype,
            spur_amplitude_ctype,
            spur_margin_ctype,
            spur_absolute_limit_ctype,
            spur_range_index_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            spur_frequency_ctype[:],
            spur_amplitude_ctype[:],
            spur_margin_ctype[:],
            spur_absolute_limit_ctype[:],
            spur_range_index_ctype[:],
            error_code,
        )

    def spur_fetch_range_absolute_limit_trace(self, selector_string, timeout, absolute_limit):
        """spur_fetch_range_absolute_limit_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(absolute_limit, "absolute_limit", "float32")
        if len(absolute_limit) != actual_array_size_ctype.value:
            absolute_limit.resize((actual_array_size_ctype.value,), refcheck=False)
        absolute_limit_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_limit, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpurFetchRangeAbsoluteLimitTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            absolute_limit_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def spur_fetch_range_spectrum_trace(self, selector_string, timeout, range_spectrum):
        """spur_fetch_range_spectrum_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpurFetchRangeSpectrumTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(range_spectrum, "range_spectrum", "float32")
        if len(range_spectrum) != actual_array_size_ctype.value:
            range_spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        range_spectrum_ctype = _get_ctypes_pointer_for_buffer(
            value=range_spectrum, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpurFetchRangeSpectrumTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            range_spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def spur_fetch_range_status_array(self, selector_string, timeout):
        """spur_fetch_range_status_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpurFetchRangeStatusArray(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        range_status_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )
        number_of_detected_spurs_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpurFetchRangeStatusArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            range_status_ctype,
            number_of_detected_spurs_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            [enums.SpurRangeStatus(value) for value in range_status_ctype],
            number_of_detected_spurs_ctype[:],
            error_code,
        )

    def spur_fetch_spur_measurement_array(self, selector_string, timeout):
        """spur_fetch_spur_measurement_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SpurFetchSpurMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        spur_frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_amplitude_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_absolute_limit_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        spur_margin_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SpurFetchSpurMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            spur_frequency_ctype,
            spur_amplitude_ctype,
            spur_absolute_limit_ctype,
            spur_margin_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            spur_frequency_ctype[:],
            spur_amplitude_ctype[:],
            spur_absolute_limit_ctype[:],
            spur_margin_ctype[:],
            error_code,
        )

    def ampm_fetch_am_to_am_trace(self, selector_string, timeout):
        """ampm_fetch_am_to_am_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchAMToAMTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        reference_powers_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        measured_am_to_am_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        curve_fit_am_to_am_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchAMToAMTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            reference_powers_ctype,
            measured_am_to_am_ctype,
            curve_fit_am_to_am_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            reference_powers_ctype[:],
            measured_am_to_am_ctype[:],
            curve_fit_am_to_am_ctype[:],
            error_code,
        )

    def ampm_fetch_am_to_pm_trace(self, selector_string, timeout):
        """ampm_fetch_am_to_pm_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchAMToPMTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        reference_powers_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        measured_am_to_pm_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        curve_fit_am_to_pm_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchAMToPMTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            reference_powers_ctype,
            measured_am_to_pm_ctype,
            curve_fit_am_to_pm_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            reference_powers_ctype[:],
            measured_am_to_pm_ctype[:],
            curve_fit_am_to_pm_ctype[:],
            error_code,
        )

    def ampm_fetch_compression_points(self, selector_string, timeout):
        """ampm_fetch_compression_points."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchCompressionPoints(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        input_compression_point_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        output_compression_point_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchCompressionPoints(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            input_compression_point_ctype,
            output_compression_point_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return input_compression_point_ctype[:], output_compression_point_ctype[:], error_code

    def ampm_fetch_curve_fit_coefficients(self, selector_string, timeout):
        """ampm_fetch_curve_fit_coefficients."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchCurveFitCoefficients(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        am_to_am_coefficients_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        am_to_pm_coefficients_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchCurveFitCoefficients(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            am_to_am_coefficients_ctype,
            am_to_pm_coefficients_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return am_to_am_coefficients_ctype[:], am_to_pm_coefficients_ctype[:], error_code

    def ampm_fetch_processed_mean_acquired_waveform(
        self, selector_string, timeout, processed_mean_acquired_waveform
    ):
        """ampm_fetch_processed_mean_acquired_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            processed_mean_acquired_waveform, "processed_mean_acquired_waveform", "complex64"
        )
        if len(processed_mean_acquired_waveform) != actual_array_size_ctype.value:
            processed_mean_acquired_waveform.resize(
                (actual_array_size_ctype.value,), refcheck=False
            )
        processed_mean_acquired_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=processed_mean_acquired_waveform, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchProcessedMeanAcquiredWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            processed_mean_acquired_waveform_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def ampm_fetch_processed_reference_waveform(
        self, selector_string, timeout, processed_reference_waveform
    ):
        """ampm_fetch_processed_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            processed_reference_waveform, "processed_reference_waveform", "complex64"
        )
        if len(processed_reference_waveform) != actual_array_size_ctype.value:
            processed_reference_waveform.resize((actual_array_size_ctype.value,), refcheck=False)
        processed_reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=processed_reference_waveform, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchProcessedReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            processed_reference_waveform_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def ampm_fetch_relative_phase_trace(self, selector_string, timeout, relative_phase):
        """ampm_fetch_relative_phase_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchRelativePhaseTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(relative_phase, "relative_phase", "float32")
        if len(relative_phase) != actual_array_size_ctype.value:
            relative_phase.resize((actual_array_size_ctype.value,), refcheck=False)
        relative_phase_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_phase, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchRelativePhaseTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            relative_phase_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def ampm_fetch_relative_power_trace(self, selector_string, timeout, relative_power):
        """ampm_fetch_relative_power_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_AMPMFetchRelativePowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(relative_power, "relative_power", "float32")
        if len(relative_power) != actual_array_size_ctype.value:
            relative_power.resize((actual_array_size_ctype.value,), refcheck=False)
        relative_power_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_power, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_AMPMFetchRelativePowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            relative_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def dpd_fetch_dpd_polynomial(self, selector_string, timeout, dpd_polynomial):
        """dpd_fetch_dpd_polynomial."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_DPDFetchDPDPolynomial(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        _helper.validate_numpy_array(dpd_polynomial, "dpd_polynomial", "complex64")
        if len(dpd_polynomial) != actual_array_size_ctype.value:
            dpd_polynomial.resize((actual_array_size_ctype.value,), refcheck=False)
        dpd_polynomial_ctype = _get_ctypes_pointer_for_buffer(
            value=dpd_polynomial, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_DPDFetchDPDPolynomial(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            dpd_polynomial_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_fetch_dvr_model(self, selector_string, timeout, dvr_model):
        """dpd_fetch_dvr_model."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_DPDFetchDVRModel(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        _helper.validate_numpy_array(dvr_model, "dvr_model", "complex64")
        if len(dvr_model) != actual_array_size_ctype.value:
            dvr_model.resize((actual_array_size_ctype.value,), refcheck=False)
        dvr_model_ctype = _get_ctypes_pointer_for_buffer(
            value=dvr_model, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_DPDFetchDVRModel(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            dvr_model_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def dpd_fetch_lookup_table(self, selector_string, timeout, complex_gains):
        """dpd_fetch_lookup_table."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_DPDFetchLookupTable(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        input_powers_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        _helper.validate_numpy_array(complex_gains, "complex_gains", "complex64")
        if len(complex_gains) != actual_array_size_ctype.value:
            complex_gains.resize((actual_array_size_ctype.value,), refcheck=False)
        complex_gains_ctype = _get_ctypes_pointer_for_buffer(
            value=complex_gains, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_DPDFetchLookupTable(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            input_powers_ctype,
            complex_gains_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return input_powers_ctype[:], error_code

    def dpd_fetch_processed_mean_acquired_waveform(
        self, selector_string, timeout, processed_mean_acquired_waveform
    ):
        """dpd_fetch_processed_mean_acquired_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            processed_mean_acquired_waveform, "processed_mean_acquired_waveform", "complex64"
        )
        if len(processed_mean_acquired_waveform) != actual_array_size_ctype.value:
            processed_mean_acquired_waveform.resize(
                (actual_array_size_ctype.value,), refcheck=False
            )
        processed_mean_acquired_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=processed_mean_acquired_waveform, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_DPDFetchProcessedMeanAcquiredWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            processed_mean_acquired_waveform_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def dpd_fetch_processed_reference_waveform(
        self, selector_string, timeout, processed_reference_waveform
    ):
        """dpd_fetch_processed_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_DPDFetchProcessedReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            processed_reference_waveform, "processed_reference_waveform", "complex64"
        )
        if len(processed_reference_waveform) != actual_array_size_ctype.value:
            processed_reference_waveform.resize((actual_array_size_ctype.value,), refcheck=False)
        processed_reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=processed_reference_waveform, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_DPDFetchProcessedReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            processed_reference_waveform_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def acp_fetch_absolute_powers_trace(
        self, selector_string, timeout, trace_index, absolute_powers_trace
    ):
        """acp_fetch_absolute_powers_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        trace_index_ctype = ctypes.c_int32(trace_index)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_ACPFetchAbsolutePowersTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(absolute_powers_trace, "absolute_powers_trace", "float32")
        if len(absolute_powers_trace) != actual_array_size_ctype.value:
            absolute_powers_trace.resize((actual_array_size_ctype.value,), refcheck=False)
        absolute_powers_trace_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_powers_trace, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_ACPFetchAbsolutePowersTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            x0_ctype,
            dx_ctype,
            absolute_powers_trace_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def acp_fetch_offset_measurement_array(self, selector_string, timeout):
        """acp_fetch_offset_measurement_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_ACPFetchOffsetMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        lower_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        upper_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        lower_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        upper_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_ACPFetchOffsetMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            lower_relative_power_ctype,
            upper_relative_power_ctype,
            lower_absolute_power_ctype,
            upper_absolute_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            lower_relative_power_ctype[:],
            upper_relative_power_ctype[:],
            lower_absolute_power_ctype[:],
            upper_absolute_power_ctype[:],
            error_code,
        )

    def acp_fetch_relative_powers_trace(
        self, selector_string, timeout, trace_index, relative_powers_trace
    ):
        """acp_fetch_relative_powers_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        trace_index_ctype = ctypes.c_int32(trace_index)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_ACPFetchRelativePowersTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(relative_powers_trace, "relative_powers_trace", "float32")
        if len(relative_powers_trace) != actual_array_size_ctype.value:
            relative_powers_trace.resize((actual_array_size_ctype.value,), refcheck=False)
        relative_powers_trace_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_powers_trace, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_ACPFetchRelativePowersTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            x0_ctype,
            dx_ctype,
            relative_powers_trace_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def acp_fetch_spectrum(self, selector_string, timeout, spectrum):
        """acp_fetch_spectrum."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_ACPFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_ACPFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def ccdf_fetch_gaussian_probabilities_trace(
        self, selector_string, timeout, gaussian_probabilities
    ):
        """ccdf_fetch_gaussian_probabilities_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(gaussian_probabilities, "gaussian_probabilities", "float32")
        if len(gaussian_probabilities) != actual_array_size_ctype.value:
            gaussian_probabilities.resize((actual_array_size_ctype.value,), refcheck=False)
        gaussian_probabilities_ctype = _get_ctypes_pointer_for_buffer(
            value=gaussian_probabilities, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_CCDFFetchGaussianProbabilitiesTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            gaussian_probabilities_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def ccdf_fetch_probabilities_trace(self, selector_string, timeout, probabilities):
        """ccdf_fetch_probabilities_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_CCDFFetchProbabilitiesTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(probabilities, "probabilities", "float32")
        if len(probabilities) != actual_array_size_ctype.value:
            probabilities.resize((actual_array_size_ctype.value,), refcheck=False)
        probabilities_ctype = _get_ctypes_pointer_for_buffer(
            value=probabilities, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_CCDFFetchProbabilitiesTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            probabilities_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def chp_fetch_spectrum(self, selector_string, timeout, spectrum):
        """chp_fetch_spectrum."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_CHPFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_CHPFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def harm_fetch_harmonic_power_trace(self, selector_string, timeout, power):
        """harm_fetch_harmonic_power_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_HarmFetchHarmonicPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(power, "power", "float32")
        if len(power) != actual_array_size_ctype.value:
            power.resize((actual_array_size_ctype.value,), refcheck=False)
        power_ctype = _get_ctypes_pointer_for_buffer(value=power, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_HarmFetchHarmonicPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def harm_fetch_harmonic_measurement_array(self, selector_string, timeout):
        """harm_fetch_harmonic_measurement_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_HarmFetchHarmonicMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        average_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        average_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        rbw_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_HarmFetchHarmonicMeasurementArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            average_relative_power_ctype,
            average_absolute_power_ctype,
            rbw_ctype,
            frequency_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            average_relative_power_ctype[:],
            average_absolute_power_ctype[:],
            rbw_ctype[:],
            frequency_ctype[:],
            error_code,
        )

    def sem_fetch_absolute_mask_trace(self, selector_string, timeout, absolute_mask):
        """sem_fetch_absolute_mask_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchAbsoluteMaskTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(absolute_mask, "absolute_mask", "float32")
        if len(absolute_mask) != actual_array_size_ctype.value:
            absolute_mask.resize((actual_array_size_ctype.value,), refcheck=False)
        absolute_mask_ctype = _get_ctypes_pointer_for_buffer(
            value=absolute_mask, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchAbsoluteMaskTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            absolute_mask_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def sem_fetch_lower_offset_margin_array(self, selector_string, timeout):
        """sem_fetch_lower_offset_margin_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchLowerOffsetMarginArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        measurement_status_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )
        margin_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        margin_frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        margin_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        margin_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchLowerOffsetMarginArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            measurement_status_ctype,
            margin_ctype,
            margin_frequency_ctype,
            margin_absolute_power_ctype,
            margin_relative_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            [enums.SemLowerOffsetMeasurementStatus(value) for value in measurement_status_ctype],
            margin_ctype[:],
            margin_frequency_ctype[:],
            margin_absolute_power_ctype[:],
            margin_relative_power_ctype[:],
            error_code,
        )

    def sem_fetch_lower_offset_power_array(self, selector_string, timeout):
        """sem_fetch_lower_offset_power_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchLowerOffsetPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        total_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        total_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        peak_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        peak_frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        peak_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchLowerOffsetPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            total_absolute_power_ctype,
            total_relative_power_ctype,
            peak_absolute_power_ctype,
            peak_frequency_ctype,
            peak_relative_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            total_absolute_power_ctype[:],
            total_relative_power_ctype[:],
            peak_absolute_power_ctype[:],
            peak_frequency_ctype[:],
            peak_relative_power_ctype[:],
            error_code,
        )

    def sem_fetch_relative_mask_trace(self, selector_string, timeout, relative_mask):
        """sem_fetch_relative_mask_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchRelativeMaskTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(relative_mask, "relative_mask", "float32")
        if len(relative_mask) != actual_array_size_ctype.value:
            relative_mask.resize((actual_array_size_ctype.value,), refcheck=False)
        relative_mask_ctype = _get_ctypes_pointer_for_buffer(
            value=relative_mask, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchRelativeMaskTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            relative_mask_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def sem_fetch_spectrum(self, selector_string, timeout, spectrum):
        """sem_fetch_spectrum."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchSpectrum(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def sem_fetch_upper_offset_margin_array(self, selector_string, timeout):
        """sem_fetch_upper_offset_margin_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchUpperOffsetMarginArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        measurement_status_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_int32, size=actual_array_size_ctype.value
        )
        margin_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        margin_frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        margin_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        margin_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchUpperOffsetMarginArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            measurement_status_ctype,
            margin_ctype,
            margin_frequency_ctype,
            margin_absolute_power_ctype,
            margin_relative_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            [enums.SemUpperOffsetMeasurementStatus(value) for value in measurement_status_ctype],
            margin_ctype[:],
            margin_frequency_ctype[:],
            margin_absolute_power_ctype[:],
            margin_relative_power_ctype[:],
            error_code,
        )

    def sem_fetch_upper_offset_power_array(self, selector_string, timeout):
        """sem_fetch_upper_offset_power_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_SEMFetchUpperOffsetPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        total_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        total_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        peak_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        peak_frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        peak_relative_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_SEMFetchUpperOffsetPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            total_absolute_power_ctype,
            total_relative_power_ctype,
            peak_absolute_power_ctype,
            peak_frequency_ctype,
            peak_relative_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            total_absolute_power_ctype[:],
            total_relative_power_ctype[:],
            peak_absolute_power_ctype[:],
            peak_frequency_ctype[:],
            peak_relative_power_ctype[:],
            error_code,
        )

    def obw_fetch_spectrum_trace(self, selector_string, timeout, spectrum):
        """obw_fetch_spectrum_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_OBWFetchSpectrumTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        if len(spectrum) != actual_array_size_ctype.value:
            spectrum.resize((actual_array_size_ctype.value,), refcheck=False)
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_OBWFetchSpectrumTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def txp_fetch_power_trace(self, selector_string, timeout, power):
        """txp_fetch_power_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_TXPFetchPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(power, "power", "float32")
        if len(power) != actual_array_size_ctype.value:
            power.resize((actual_array_size_ctype.value,), refcheck=False)
        power_ctype = _get_ctypes_pointer_for_buffer(value=power, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_TXPFetchPowerTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def iq_fetch_data(self, selector_string, timeout, record_to_fetch, samples_to_read, data):
        """iq_fetch_data."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        record_to_fetch_ctype = ctypes.c_int32(record_to_fetch)
        samples_to_read_ctype = ctypes.c_int64(samples_to_read)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IQFetchData(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            record_to_fetch_ctype,
            samples_to_read_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        t0_ctype = ctypes.c_double()
        dt_ctype = ctypes.c_double()
        _helper.validate_numpy_array(data, "data", "complex64")
        if len(data) != actual_array_size_ctype.value:
            data.resize((actual_array_size_ctype.value,), refcheck=False)
        data_ctype = _get_ctypes_pointer_for_buffer(
            value=data, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IQFetchData(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            record_to_fetch_ctype,
            samples_to_read_ctype,
            t0_ctype,
            dt_ctype,
            data_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return t0_ctype.value, dt_ctype.value, error_code

    def phasenoise_fetch_integrated_noise(self, selector_string, timeout):
        """phasenoise_fetch_integrated_noise."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        integrated_phase_noise_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        residual_pm_in_radian_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        residual_pm_in_degree_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        residual_fm_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        jitter_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchIntegratedNoise(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            integrated_phase_noise_ctype,
            residual_pm_in_radian_ctype,
            residual_pm_in_degree_ctype,
            residual_fm_ctype,
            jitter_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            integrated_phase_noise_ctype[:],
            residual_pm_in_radian_ctype[:],
            residual_pm_in_degree_ctype[:],
            residual_fm_ctype[:],
            jitter_ctype[:],
            error_code,
        )

    def phasenoise_fetch_measured_log_plot_trace(self, selector_string, timeout):
        """phasenoise_fetch_measured_log_plot_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        measured_phase_noise_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchMeasuredLogPlotTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            frequency_ctype,
            measured_phase_noise_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return frequency_ctype[:], measured_phase_noise_ctype[:], error_code

    def phasenoise_fetch_smoothed_log_plot_trace(self, selector_string, timeout):
        """phasenoise_fetch_smoothed_log_plot_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace(
            vi_ctype, selector_string_ctype, timeout_ctype, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        frequency_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )
        smoothed_phase_noise_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_float, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchSmoothedLogPlotTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            frequency_ctype,
            smoothed_phase_noise_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return frequency_ctype[:], smoothed_phase_noise_ctype[:], error_code

    def phasenoise_fetch_spot_noise(self, selector_string, timeout):
        """phasenoise_fetch_spot_noise."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchSpotNoise(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        spot_phase_noise_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PhaseNoiseFetchSpotNoise(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            spot_phase_noise_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return spot_phase_noise_ctype[:], error_code

    def pavt_fetch_amplitude_trace(self, selector_string, timeout, trace_index, amplitude):
        """pavt_fetch_amplitude_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        trace_index_ctype = ctypes.c_int32(trace_index)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PAVTFetchAmplitudeTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(amplitude, "amplitude", "float32")
        if len(amplitude) != actual_array_size_ctype.value:
            amplitude.resize((actual_array_size_ctype.value,), refcheck=False)
        amplitude_ctype = _get_ctypes_pointer_for_buffer(
            value=amplitude, library_type=ctypes.c_float
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PAVTFetchAmplitudeTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            x0_ctype,
            dx_ctype,
            amplitude_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def pavt_fetch_phase_and_amplitude_array(self, selector_string, timeout):
        """pavt_fetch_phase_and_amplitude_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        mean_relative_phase_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        mean_relative_amplitude_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        mean_absolute_phase_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )
        mean_absolute_amplitude_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PAVTFetchPhaseAndAmplitudeArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            mean_relative_phase_ctype,
            mean_relative_amplitude_ctype,
            mean_absolute_phase_ctype,
            mean_absolute_amplitude_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            mean_relative_phase_ctype[:],
            mean_relative_amplitude_ctype[:],
            mean_absolute_phase_ctype[:],
            mean_absolute_amplitude_ctype[:],
            error_code,
        )

    def pavt_fetch_phase_trace(self, selector_string, timeout, trace_index, phase):
        """pavt_fetch_phase_trace."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        trace_index_ctype = ctypes.c_int32(trace_index)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PAVTFetchPhaseTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(phase, "phase", "float32")
        if len(phase) != actual_array_size_ctype.value:
            phase.resize((actual_array_size_ctype.value,), refcheck=False)
        phase_ctype = _get_ctypes_pointer_for_buffer(value=phase, library_type=ctypes.c_float)

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PAVTFetchPhaseTrace(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            trace_index_ctype,
            x0_ctype,
            dx_ctype,
            phase_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def idpd_fetch_processed_mean_acquired_waveform(
        self, selector_string, timeout, processed_mean_acquired_waveform
    ):
        """idpd_fetch_processed_mean_acquired_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            processed_mean_acquired_waveform, "processed_mean_acquired_waveform", "complex64"
        )
        if len(processed_mean_acquired_waveform) != actual_array_size_ctype.value:
            processed_mean_acquired_waveform.resize(
                (actual_array_size_ctype.value,), refcheck=False
            )
        processed_mean_acquired_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=processed_mean_acquired_waveform, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IDPDFetchProcessedMeanAcquiredWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            processed_mean_acquired_waveform_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def idpd_fetch_processed_reference_waveform(
        self, selector_string, timeout, processed_reference_waveform
    ):
        """idpd_fetch_processed_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            processed_reference_waveform, "processed_reference_waveform", "complex64"
        )
        if len(processed_reference_waveform) != actual_array_size_ctype.value:
            processed_reference_waveform.resize((actual_array_size_ctype.value,), refcheck=False)
        processed_reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=processed_reference_waveform, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IDPDFetchProcessedReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            processed_reference_waveform_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def idpd_fetch_predistorted_waveform(self, selector_string, timeout, predistorted_waveform):
        """idpd_fetch_predistorted_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IDPDFetchPredistortedWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(predistorted_waveform, "predistorted_waveform", "complex64")
        if len(predistorted_waveform) != actual_array_size_ctype.value:
            predistorted_waveform.resize((actual_array_size_ctype.value,), refcheck=False)
        predistorted_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=predistorted_waveform, library_type=_custom_types.ComplexSingle
        )
        papr_ctype = ctypes.c_double()
        power_offset_ctype = ctypes.c_double()
        gain_ctype = ctypes.c_double()

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IDPDFetchPredistortedWaveform(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            predistorted_waveform_ctype,
            papr_ctype,
            power_offset_ctype,
            gain_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            x0_ctype.value,
            dx_ctype.value,
            papr_ctype.value,
            power_offset_ctype.value,
            gain_ctype.value,
            error_code,
        )

    def idpd_fetch_equalizer_coefficients(self, selector_string, timeout, equalizer_coefficients):
        """idpd_fetch_equalizer_coefficients."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IDPDFetchEqualizerCoefficients(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            None,
            None,
            None,
            0,
            actual_array_size_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(equalizer_coefficients, "equalizer_coefficients", "complex64")
        if len(equalizer_coefficients) != actual_array_size_ctype.value:
            equalizer_coefficients.resize((actual_array_size_ctype.value,), refcheck=False)
        equalizer_coefficients_ctype = _get_ctypes_pointer_for_buffer(
            value=equalizer_coefficients, library_type=_custom_types.ComplexSingle
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IDPDFetchEqualizerCoefficients(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            x0_ctype,
            dx_ctype,
            equalizer_coefficients_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, error_code

    def idpd_get_equalizer_reference_waveform(self, selector_string, equalizer_reference_waveform):
        """idpd_get_equalizer_reference_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform(
            vi_ctype, selector_string_ctype, None, None, None, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        x0_ctype = ctypes.c_double()
        dx_ctype = ctypes.c_double()
        _helper.validate_numpy_array(
            equalizer_reference_waveform, "equalizer_reference_waveform", "complex64"
        )
        if len(equalizer_reference_waveform) != actual_array_size_ctype.value:
            equalizer_reference_waveform.resize((actual_array_size_ctype.value,), refcheck=False)
        equalizer_reference_waveform_ctype = _get_ctypes_pointer_for_buffer(
            value=equalizer_reference_waveform, library_type=_custom_types.ComplexSingle
        )
        papr_ctype = ctypes.c_double()

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_IDPDGetEqualizerReferenceWaveform(
            vi_ctype,
            selector_string_ctype,
            x0_ctype,
            dx_ctype,
            equalizer_reference_waveform_ctype,
            papr_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_ctype.value, dx_ctype.value, papr_ctype.value, error_code

    def powerlist_fetch_mean_absolute_power_array(self, selector_string, timeout):
        """powerlist_fetch_mean_absolute_power_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        mean_absolute_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PowerListFetchMeanAbsolutePowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            mean_absolute_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return mean_absolute_power_ctype[:], error_code

    def powerlist_fetch_maximum_power_array(self, selector_string, timeout):
        """powerlist_fetch_maximum_power_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PowerListFetchMaximumPowerArray(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        maximum_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PowerListFetchMaximumPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            maximum_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return maximum_power_ctype[:], error_code

    def powerlist_fetch_minimum_power_array(self, selector_string, timeout):
        """powerlist_fetch_minimum_power_array."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        timeout_ctype = ctypes.c_double(timeout)
        actual_array_size_ctype = ctypes.c_int32(0)

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_PowerListFetchMinimumPowerArray(
            vi_ctype, selector_string_ctype, timeout_ctype, None, 0, actual_array_size_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        minimum_power_ctype = _get_ctypes_pointer_for_buffer(
            library_type=ctypes.c_double, size=actual_array_size_ctype.value
        )

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_PowerListFetchMinimumPowerArray(
            vi_ctype,
            selector_string_ctype,
            timeout_ctype,
            minimum_power_ctype,
            actual_array_size_ctype,
            None,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return minimum_power_ctype[:], error_code

    def clone_signal_configuration(self, old_signal_name, new_signal_name):
        """clone_signal_configuration."""
        vi_ctype = ctypes.c_uint32(self._vi)
        old_signal_name_ctype = ctypes.create_string_buffer(old_signal_name.encode(self._encoding))
        new_signal_name_ctype = ctypes.create_string_buffer(new_signal_name.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_CloneSignalConfiguration(
            vi_ctype, old_signal_name_ctype, new_signal_name_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        import nirfmxspecan

        signal_configuration = (
            nirfmxspecan._SpecAnSignalConfiguration.get_specan_signal_configuration(  # type: ignore
                self._instr_session, new_signal_name, True
            )
        )
        return signal_configuration, error_code

    def delete_signal_configuration(self, ignore_driver_error):
        """delete_signal_configuration."""
        vi_ctype = ctypes.c_uint32(self._vi)
        signal_name_ctype = ctypes.create_string_buffer(
            self._signal_obj.signal_configuration_name.encode(self._encoding)
        )
        error_code = self._library.RFmxSpecAn_DeleteSignalConfiguration(vi_ctype, signal_name_ctype)
        if not ignore_driver_error:
            errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def send_software_edge_trigger(self):
        """send_software_edge_trigger."""
        vi_ctype = ctypes.c_uint32(self._vi)
        error_code = self._library.RFmxSpecAn_SendSoftwareEdgeTrigger(vi_ctype)
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def get_all_named_result_names(self, selector_string):
        """get_all_named_result_names."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        actual_result_names_size_ctype = ctypes.c_int32(0)
        default_result_exists_ctype = ctypes.c_int32()

        # call library function to get the size of array
        error_code = self._library.RFmxSpecAn_GetAllNamedResultNames(
            vi_ctype,
            selector_string_ctype,
            None,
            0,
            actual_result_names_size_ctype,
            default_result_exists_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        result_names_ctype = (ctypes.c_char * actual_result_names_size_ctype.value)()

        # call library function again to get array
        error_code = self._library.RFmxSpecAn_GetAllNamedResultNames(
            vi_ctype,
            selector_string_ctype,
            result_names_ctype,
            actual_result_names_size_ctype,
            None,
            default_result_exists_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)

        return (
            _helper.split_string_by_comma(result_names_ctype.value.decode(self._encoding)),
            default_result_exists_ctype.value,
            error_code,
        )

    def dpd_apply_digital_predistortion(
        self,
        selector_string,
        x0_in,
        dx_in,
        waveform_in,
        idle_duration_present,
        measurement_timeout,
        waveform_out,
    ):
        """dpd_apply_digital_predistortion."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_in_ctype = ctypes.c_double(x0_in)
        dx_in_ctype = ctypes.c_double(dx_in)
        _helper.validate_numpy_array(waveform_in, "waveform_in", "complex64")
        waveform_in_ctype = _get_ctypes_pointer_for_buffer(
            value=waveform_in, library_type=_custom_types.ComplexSingle
        )
        array_size_in_ctype = ctypes.c_int32(len(waveform_in) if waveform_in is not None else 0)
        idle_duration_present_ctype = ctypes.c_int32(idle_duration_present)
        measurement_timeout_ctype = ctypes.c_double(measurement_timeout)

        updated_selector_string = _helper.prepend_signal_string(
            self._signal_obj.signal_configuration_name, ""
        )
        dpd_configuration_input, _ = self.get_attribute_i32(  # type: ignore
            updated_selector_string, attributes.AttributeID.DPD_APPLY_DPD_CONFIGURATION_INPUT.value
        )

        if dpd_configuration_input == enums.DpdApplyDpdConfigurationInput.MEASUREMENT.value:
            dpd_measurement_sample_rate_mode, _ = self.get_attribute_i32(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.DPD_MEASUREMENT_SAMPLE_RATE_MODE.value,
            )
            if (
                dpd_measurement_sample_rate_mode
                == enums.DpdMeasurementSampleRateMode.REFERENCE_WAVEFORM.value
            ):
                output_sample_rate = 1 / dx_in
            else:
                output_sample_rate, _ = self.get_attribute_f64(  # type: ignore
                    updated_selector_string,
                    attributes.AttributeID.DPD_MEASUREMENT_SAMPLE_RATE.value,
                )
        else:
            output_sample_rate, _ = self.get_attribute_f64(  # type: ignore
                updated_selector_string,
                attributes.AttributeID.DPD_APPLY_DPD_USER_MEASUREMENT_SAMPLE_RATE.value,
            )

        array_size_out = int(math.ceil(output_sample_rate * dx_in * array_size_in_ctype.value))
        x0_out_ctype = ctypes.c_double()
        dx_out_ctype = ctypes.c_double()
        _helper.validate_numpy_array(waveform_out, "waveform_out", "complex64")
        if len(waveform_out) != array_size_out:
            waveform_out.resize((array_size_out,), refcheck=False)
        waveform_out_ctype = _get_ctypes_pointer_for_buffer(
            value=waveform_out, library_type=_custom_types.ComplexSingle
        )
        array_size_out_ctype = ctypes.c_int32(array_size_out)
        actual_array_size_out_ctype = ctypes.c_int32(0)
        papr_ctype = ctypes.c_double()
        power_offset_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_DPDApplyDigitalPredistortion(
            vi_ctype,
            selector_string_ctype,
            x0_in_ctype,
            dx_in_ctype,
            waveform_in_ctype,
            array_size_in_ctype,
            idle_duration_present_ctype,
            measurement_timeout_ctype,
            x0_out_ctype,
            dx_out_ctype,
            waveform_out_ctype,
            array_size_out_ctype,
            actual_array_size_out_ctype,
            papr_ctype,
            power_offset_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return (
            x0_out_ctype.value,
            dx_out_ctype.value,
            papr_ctype.value,
            power_offset_ctype.value,
            error_code,
        )

    def dpd_apply_pre_dpd_signal_conditioning(
        self, selector_string, x0_in, dx_in, waveform_in, idle_duration_present, waveform_out
    ):
        """dpd_apply_pre_dpd_signal_conditioning."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        x0_in_ctype = ctypes.c_double(x0_in)
        dx_in_ctype = ctypes.c_double(dx_in)
        _helper.validate_numpy_array(waveform_in, "waveform_in", "complex64")
        waveform_in_ctype = _get_ctypes_pointer_for_buffer(
            value=waveform_in, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(len(waveform_in) if waveform_in is not None else 0)
        idle_duration_present_ctype = ctypes.c_int32(idle_duration_present)

        x0_out_ctype = ctypes.c_double()
        dx_out_ctype = ctypes.c_double()
        _helper.validate_numpy_array(waveform_out, "waveform_out", "complex64")
        if len(waveform_out) != array_size_ctype.value:
            waveform_out.resize((array_size_ctype.value,), refcheck=False)
        waveform_out_ctype = _get_ctypes_pointer_for_buffer(
            value=waveform_out, library_type=_custom_types.ComplexSingle
        )
        actual_array_size_out_ctype = ctypes.c_int32(0)
        papr_ctype = ctypes.c_double()
        error_code = self._library.RFmxSpecAn_DPDApplyPreDPDSignalConditioning(
            vi_ctype,
            selector_string_ctype,
            x0_in_ctype,
            dx_in_ctype,
            waveform_in_ctype,
            array_size_ctype,
            idle_duration_present_ctype,
            x0_out_ctype,
            dx_out_ctype,
            waveform_out_ctype,
            array_size_ctype,
            actual_array_size_out_ctype,
            papr_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return x0_out_ctype.value, dx_out_ctype.value, papr_ctype.value, error_code

    def clear_noise_calibration_database(self, selector_string):
        """clear_noise_calibration_database."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        error_code = self._library.RFmxSpecAn_ClearNoiseCalibrationDatabase(
            vi_ctype, selector_string_ctype
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def analyze_iq_1_waveform(self, selector_string, result_name, x0, dx, iq, reset):
        """analyze_iq_1_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        result_name_ctype = ctypes.create_string_buffer(result_name.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(iq, "iq", "complex64")
        iq_ctype = _get_ctypes_pointer_for_buffer(
            value=iq, library_type=_custom_types.ComplexSingle
        )
        array_size_ctype = ctypes.c_int32(len(iq) if iq is not None else 0)
        reset_ctype = ctypes.c_int32(reset)
        reserved_ctype = ctypes.c_int64(0)
        error_code = self._library.RFmxSpecAn_AnalyzeIQ1Waveform(
            vi_ctype,
            selector_string_ctype,
            result_name_ctype,
            x0_ctype,
            dx_ctype,
            iq_ctype,
            array_size_ctype,
            reset_ctype,
            reserved_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code

    def analyze_spectrum_1_waveform(self, selector_string, result_name, x0, dx, spectrum, reset):
        """analyze_spectrum_1_waveform."""
        vi_ctype = ctypes.c_uint32(self._vi)
        selector_string_ctype = ctypes.create_string_buffer(selector_string.encode(self._encoding))
        result_name_ctype = ctypes.create_string_buffer(result_name.encode(self._encoding))
        x0_ctype = ctypes.c_double(x0)
        dx_ctype = ctypes.c_double(dx)
        _helper.validate_numpy_array(spectrum, "spectrum", "float32")
        spectrum_ctype = _get_ctypes_pointer_for_buffer(value=spectrum, library_type=ctypes.c_float)
        array_size_ctype = ctypes.c_int32(len(spectrum) if spectrum is not None else 0)
        reset_ctype = ctypes.c_int32(reset)
        reserved_ctype = ctypes.c_int64(0)
        error_code = self._library.RFmxSpecAn_AnalyzeSpectrum1Waveform(
            vi_ctype,
            selector_string_ctype,
            result_name_ctype,
            x0_ctype,
            dx_ctype,
            spectrum_ctype,
            array_size_ctype,
            reset_ctype,
            reserved_ctype,
        )
        errors.handle_error(self, error_code, ignore_warnings=True, is_error_handling=False)
        return error_code
