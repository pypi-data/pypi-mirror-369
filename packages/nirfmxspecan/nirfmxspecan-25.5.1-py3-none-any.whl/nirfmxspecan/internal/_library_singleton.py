"""Creates singleton instance of a module."""

import ctypes
import ctypes.util
import platform
import threading
from typing import Any

import nirfmxspecan.errors as errors
import nirfmxspecan.internal._library as _library

_instance = None
_instance_lock = threading.Lock()
_library_info = {"Windows": {"64bit": {"name": "niRFmxSpecAn.dll", "type": "cdll"}}}


def _get_library_name() -> str:
    try:
        lib_name = ctypes.util.find_library(
            _library_info[platform.system()][platform.architecture()[0]]["name"]
        )  # We find and return full path to the DLL
        if lib_name is None:
            raise errors.DriverNotInstalledError()  # type: ignore
        return lib_name
    except KeyError:
        raise errors.UnsupportedConfigurationError


def _get_library_type() -> Any:
    try:
        return _library_info[platform.system()][platform.architecture()[0]]["type"]
    except KeyError:
        raise errors.UnsupportedConfigurationError


def get() -> Any:
    """Returns the library.Library singleton for nirfmxspecan."""
    global _instance
    global _instance_lock

    with _instance_lock:
        if _instance is None:
            try:
                library_type = _get_library_type()
                if library_type == "windll":
                    ctypes_library = ctypes.WinDLL(_get_library_name())  # type: ignore
                else:
                    assert library_type == "cdll"
                    ctypes_library = ctypes.CDLL(_get_library_name())
            except OSError:
                raise errors.DriverNotInstalledError()  # type: ignore
            _instance = _library.Library(ctypes_library)  # type: ignore
        return _instance
