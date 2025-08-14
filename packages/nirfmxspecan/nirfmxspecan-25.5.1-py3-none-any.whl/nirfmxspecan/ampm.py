"""Represents the Ampm measurement."""

import functools

import nirfmxspecan.ampm_configuration as configuration
import nirfmxspecan.ampm_results as results


def _raise_if_disposed(f):
    """From https://stackoverflow.com/questions/5929107/decorators-with-parameters."""

    @functools.wraps(f)
    def aux(*xs, **kws):
        meas_obj = xs[0]  # parameter 0 is 'self' which is the measurement object
        if meas_obj._signal_obj.is_disposed:
            raise Exception("Cannot access a disposed SpecAn signal configuration")
        return f(*xs, **kws)

    return aux


class Ampm(object):
    """Represents the Ampm measurement."""

    def __init__(self, signal_obj):
        """Represents the Ampm measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter
        self.configuration = configuration.AmpmConfiguration(signal_obj)  # type: ignore
        self.results = results.AmpmResults(signal_obj)  # type: ignore
