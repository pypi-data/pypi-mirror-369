"""errors.py - Contains error classes and method(s) to handle error."""

import platform
from typing import Any


def _is_success(code: int) -> bool:
    return code == 0


def _is_error(code: int) -> bool:
    return code < 0


def _is_warning(code: int) -> bool:
    return code > 0


class Error(Exception):
    """Base error class for NI-RFmxSpecAn."""

    def __init__(self, message):
        """Base error class for NI-RFmxSpecAn."""
        super(Error, self).__init__(message)


class DriverNotInstalledError(Error):
    """An error due to using this module without the driver runtime installed."""

    def __init__(self):
        """An error due to using this module without the driver runtime installed."""
        super(DriverNotInstalledError, self).__init__("The NI-RFmxSpecAn runtime could not be loaded. Make sure it is installed and its bitness matches that of your Python interpreter. Please visit http://www.ni.com/downloads/drivers/ to download and install it.")  # type: ignore


class DriverTooOldError(Error):
    """An error due to using this module with an older version of the NI-RFmxSpecAn driver runtime."""

    def __init__(self):
        """An error due to using this module with an older version of the NI-RFmxSpecAn driver runtime."""
        super(DriverTooOldError, self).__init__("A function was not found in the NI-RFmxSpecAn runtime. Please visit http://www.ni.com/downloads/drivers/ to download a newer version and install it.")  # type: ignore


class DriverTooNewError(Error):
    """An error due to the NI-RFmxSpecAn driver runtime being too new for this module."""

    def __init__(self):
        """An error due to the NI-RFmxSpecAn driver runtime being too new for this module."""
        super(DriverTooNewError, self).__init__("The NI-RFmxSpecAn runtime returned an unexpected value. This can occur if it is too new for the nirfmxspecan Python module. Upgrade the nirfmxspecan Python module.")  # type: ignore


class UnsupportedConfigurationError(Error):
    """An error due to using this module in an usupported platform."""

    def __init__(self):
        """An error due to using this module in an usupported platform."""
        super(UnsupportedConfigurationError, self).__init__("System configuration is unsupported: " + platform.architecture()[0] + " " + platform.system())  # type: ignore


def handle_error(
    library_interpreter: Any, code: int, ignore_warnings: bool, is_error_handling: bool
) -> None:
    r"""Helper function for handling errors returned by NI-RFmxSpecAn Library.

    It calls back into the LibraryInterpreter to get the corresponding error
    description and raises if necessary.
    """
    if _is_success(code) or (_is_warning(code) and ignore_warnings):
        return

    if is_error_handling:
        # The caller is in the midst of error handling and an error occurred.
        # Don't try to get the description or we'll start recursing until the stack overflows.
        description = ""
    else:
        description = library_interpreter.get_error_description(code)

    if _is_error(code):
        import nirfmxinstr

        raise nirfmxinstr.RFmxError(code, description)  # type: ignore
