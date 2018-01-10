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
    """Describe a single parameter on an Instrument.
    """

    def __get__(self, instance, owner):
        """
        """
        if instance is None:
            return self
        return instance.__dict__[self.key]

    def __set__(self, instance, value):
        """Should validate then set."""
        raise NotImplementedError

    def __set_name__(self, owner, name):
        self.key = name

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def _setup(self):
        """Write instance specific data needed to manage the value.

        For continuous params it sets limits for discrete params it
        specifies allowed values"""
        raise NotImplementedError


class ContinuousParam(Param):
    """Param use cases

    Impose limits on parameter values - look in a dict on the instrument to get
    the right limits.
    Variable rate sweeping. Use a bunch of sweep rate that do not exceed the
    master sweep rate -> implement a sweep that adjusts the sweep rate limits.
    """

    def __init__(self,
                 units=None,
                 minimum=None,
                 maximum=None,
                 rate=None,
                 step=None):
        super(ContinuousParam, self).__init__()
        self.units = units
        self.minimum = minimum
        self.maximum = maximum
        self.rate = rate
        self.step = step

    def __set__(self, instance, value):
        limits = getattr(instance, "_" + self.key)
        # Check that the value does not violate limits
        self.check_value(value, limits["minimum"], limits["maximum"])
        # Sweep the parameter in small steps if possible
        if limits["rate"] and limits["step"]:
            self.sweep(instance, value, limits["rate"], limits["step"])
        # Directly set the parameter if not
        else:
            self._set(instance, value)

    def check_value(self, value, minimum, maximum):
        if not minimum <= value <= maximum:
            raise ValueError(
                "{} violates limits {} on {}".format(value, limits, self.key))

    def __str__(self):
        return "<{}: {} ({})>".format(self.__class__.__name__, self.key,
                                      self.units)

    def _set(self, instance, value):
        """Directly adjust the paramter without checking limits."""
        instance.__dict__[self.key]["value"] = value

    def _setup(self):
        """Return a dict for managing a ContinuousParam."""
        return {
            "value": None,
            "units": self.units,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "rate": self.rate,
            "step": self.step
        }

    def sweep(self, instance, value, step, rate):
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
        start = self.__get__(instance, None)
        num = math.ceil(np.abs(start - value) / step)
        vals = np.linspace(start, value, num)
        delay = step / rate
        # Run the sweep
        for val in vals:
            self._set(instance, val)
            time.sleep(delay)


class DiscreteParam(Param):
    """A parameter that takes on a small set of hardware-defined values."""

    def __init__(self, values):
        """
        Args:
            values (list): values that the Param can take
        """
        super(DiscreteParam, self).__init__()
        self.values = values

    def __set__(self, instance, value):
        """If possible sets the range to the nearest value.

        If setting is str-like then it require matches."""
        closest = self.check_value(value,
                                   instance.__dict__["_" + self.key]["values"])
        instance.__dict__[self.key] = closest

    def check_value(self, value, values):
        """Take a requested value and return the closest match for setting."""
        # If the value is allowed then return it for setting
        if value in values:
            return value
        else:
            try:
                closest = min(self.values, key=lambda x: abs(x - value))
            except TypeError:
                # Then it's not a numeric paramter. Raise a value error.
                raise ValueError(
                    "{} cannot be set to {}".format(self.name, value))
            else:
                return closest

    def _setup(self):
        """Return a dict that manages a DiscreteParam."""
        return {"value": None, "values": self.values}
