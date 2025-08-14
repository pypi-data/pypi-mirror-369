"""Represents the Pavt measurement."""

import functools

import nirfmxspecan.pavt_configuration as configuration
import nirfmxspecan.pavt_results as results


def _raise_if_disposed(f):
    """From https://stackoverflow.com/questions/5929107/decorators-with-parameters."""

    @functools.wraps(f)
    def aux(*xs, **kws):
        meas_obj = xs[0]  # parameter 0 is 'self' which is the measurement object
        if meas_obj._signal_obj.is_disposed:
            raise Exception("Cannot access a disposed SpecAn signal configuration")
        return f(*xs, **kws)

    return aux


class Pavt(object):
    """Represents the Pavt measurement."""

    def __init__(self, signal_obj):
        """Represents the Pavt measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter
        self.configuration = configuration.PavtConfiguration(signal_obj)  # type: ignore
        self.results = results.PavtResults(signal_obj)  # type: ignore
