"""Define a Param - a representation of a single setting on an instrument.
"""
import operator
import time
import math
import logging
import numpy as np
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Validator(Loadable):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def set_limits(self, **limits):
        """Use a dictionary to update limits on a parameter."""
        for key, val in limits.items():
            setattr(self, key, val)


class ContinuousValidator(Validator):
    def __init__(self, name, minimum=None, maximum=None, rate=None, step=None):
        super(ContinuousValidator, self).__init__(name)
        self.minimum = minimum
        self.maximum = maximum
        self.rate = rate
        self.step = step

    def check_limit(self, value):
        """Confirm that the requested setpoint does not violate limits."""
        try:
            if value > self.maximum:
                raise ValueError("{} violates limit {} on {}".format(
                    value, self.maximum, self.name))
        except TypeError:
            pass
        try:
            if value < self.minimum:
                raise ValueError("{} violates limit {} on {}".format(
                    value, self.minimum, self.name))
        except TypeError:
            pass

    def check_sweep(self, value, rate=None, step=None):
        """Confirm that the sweep parameters do not violate any limits."""
        self.check_limit(value)
        try:
            if rate > self.rate:
                raise ValueError("{} violates limit {} on {}".format(
                    rate, self.rate, self.name))
        except TypeError:
            pass
        try:
            if step > self.step:
                raise ValueError("{} violoates limit {} on {}".format(
                    step, self.step, self.name))
        except TypeError:
            pass


class DiscreteValidator(Validator):
    def __init__(self, name, values):
        super(DiscreteValidator, self).__init__(name)
        self.values = values

    def check_value(self, value):
        """Confirm that the setpoint is valid for the parameter."""
        if value in self.values:
            return value
        else:
            try:
                closest = min(self.values, key=lambda x: abs(x - value))
            except TypeError:
                # Then it's not a numeric parameter. Raise a value error
                raise ValueError(
                    "{} cannot be set to {}".format(self.name, value))
            else:
                return closest


class Param(Loadable):
    """
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
        validator = instance.__dict__["_" + self.key]
        validator.check_limit(value)
        if validator.step and validator.rate:
            self.sweep(instance, value, validator.step, validator.rate)
        else:
            self._set(instance, value)

    def __str__(self):
        return "<{}: {} ({})>".format(self.__class__.__name__, self.key,
                                      self.units)

    def _set(self, instance, value):
        """Directly adjust the paramter without checking limits."""
        instance.__dict__[self.key] = value

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
        closest = instance.__dict__["_" + self.key].check_value(value)
        instance.__dict__[self.key] = closest
