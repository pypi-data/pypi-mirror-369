"""Represents the Dpd measurement."""

import functools

import nirfmxspecan.dpd_apply_dpd as apply_dpd
import nirfmxspecan.dpd_configuration as configuration
import nirfmxspecan.dpd_pre_dpd as pre_dpd
import nirfmxspecan.dpd_results as results


def _raise_if_disposed(f):
    """From https://stackoverflow.com/questions/5929107/decorators-with-parameters."""

    @functools.wraps(f)
    def aux(*xs, **kws):
        meas_obj = xs[0]  # parameter 0 is 'self' which is the measurement object
        if meas_obj._signal_obj.is_disposed:
            raise Exception("Cannot access a disposed SpecAn signal configuration")
        return f(*xs, **kws)

    return aux


class Dpd(object):
    """Represents the Dpd measurement."""

    def __init__(self, signal_obj):
        """Represents the Dpd measurement."""
        self._signal_obj = signal_obj
        self._session_function_lock = signal_obj._session_function_lock
        self._interpreter = signal_obj._interpreter
        self.configuration = configuration.DpdConfiguration(signal_obj)  # type: ignore
        self.pre_dpd = pre_dpd.DpdPreDpd(signal_obj)  # type: ignore
        self.apply_dpd = apply_dpd.DpdApplyDpd(signal_obj)  # type: ignore
        self.results = results.DpdResults(signal_obj)  # type: ignore
