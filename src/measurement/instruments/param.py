"""Define a Param - a representation of a single setting on an instrument.
"""
import operator
import time
import math
import logging
import numpy as np
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Param(Loadable):
    """
    """

    def __init__(self, name):
        self.name = name
        self.value = None

    def _setup(self):
        """Write instance specific data needed to manage the value.

        For continuous params it sets limits for discrete params it
        specifies allowed values"""
        raise NotImplementedError

    def __get__(self, instance, owner):
        """
        """
        if instance is None:
            return self
        return self.value

    def __set__(self, instance, value):
        """Should validate then set."""
        raise NotImplementedError

    def __str__(self):
        return "<<{} {}>>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)


class ContinuousParam(Param):
    """Param use cases

    Impose limits on parameter values - look in a dict on the instrument to get
    the right limits.
    Variable rate sweeping. Use a bunch of sweep rate that do not exceed the
    master sweep rate -> implement a sweep that adjusts the sweep rate limits.
    """

    def __init__(self,
                 name,
                 units=None,
                 minimum=None,
                 maximum=None,
                 rate=None,
                 step=None):
        super(ContinuousParam, self).__init__(name)
        self.units = units
        self.minimum = minimum
        self.maximum = maximum
        self.rate = rate
        self.step = step

    def __set__(self, instance, value):
        self._check_limits(value)
        if self.step and self.rate:
            self.sweep(value, instance, None)
        else:
            self._set(instance, value)

    def _set(self, instance, value):
        """Directly adjust the paramter without checking limits."""
        self.value = value

    def value_check(self, op, val, attr):
        if not op(val, getattr(self, attr)):
            raise ValueError(
                "{:.3f} violates limit on {}. Limit is set to {:.3f}".format(
                    val, attr, getattr(self, attr)))

    def _check_limits(self, value):
        if self.minimum:
            self.value_check(operator.ge, value, "minimum")
        if self.maximum:
            self.value_check(operator.le, value, "maximum")

    def sweep(self, value, instance, owner):
        """Continuously adjust the parameter.

        The number of points for the sweep is selected such that the
        maximum step size is not exceeded. The rate of the sweep is
        selected such that the maximum sweep rate is not exceeded

        To limit the sweep rate but not the value that you sweep to, use
        a set_func that doesn't check the the values vs. self.maximum and
        self.minimum.

        Args:
            val (float): value of the parameter to sweep to
            rate (float): rate (unit/s) to sweep parameter
            step (float): maximum step size of parameter during sweep
        """
        # Define the values that are swept over
        start = self.__get__(instance, owner)
        num = math.ceil(np.abs(start - value) / self.step)
        vals = np.linspace(start, value, num)
        delay = self.step / self.rate
        # Run the sweep
        for val in vals:
            self._set(instance, val)
            time.sleep(delay)


class DiscreteParam(Param):
    """A parameter that takes on a small set of hardware-defined values."""

    def __init__(self, name, values):
        """
        Args:
            values (list): values that the Param can take
        """
        super(DiscreteParam, self).__init__(name)
        self.values = values

    def __set__(self, instance, value):
        """If possible sets the range to the nearest value.

        If setting is str-like then it require matches."""
        try:
            closest = min(self.values, key=lambda x: abs(x - value))
        except TypeError:
            self._set(value)
        else:
            self._set(closest)

    def _set(self, value):
        try:
            if value not in self.values:
                raise ValueError(
                    "setpoint {} not in lookup table".format(value))
        except ValueError as message:
            log.exception(message)
            raise
        else:
            self.value = value
