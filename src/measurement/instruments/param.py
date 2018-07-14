"""Define a Param - a representation of a single setting on an instrument.
"""
import time
import math
import logging
import numpy as np
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Param(Loadable):
    """
    How to set allowable values?

    TODO - knows how to use a mapping to get/set values
    """

    def __init__(self,
                 name,
                 units,
                 instrument=None,
                 mapping=None,
                 validator=None,
                 max_rate=None,
                 max_step=None):
        self.name = name
        self.units = units
        self.instrument = instrument
        self.mapping = mapping
        self.validator = validator
        self.rate = max_rate,
        self.step = max_step

    def __call__(self, value=None, **kwargs):
        """Define call interface to parameters."""
        if not value:
            return self.getter()
        else:
            self.setter(value, **kwargs)

    def __str__(self):
        return "<{}: {} = {} ({})>".format(self.__class__.__name__, self.name,
                                           self(), self.units)

    def __repr__(self):
        return str(self)

    def getter(self):
        raise NotImplementedError

    def setter(self):
        raise NotImplementedError


class VisaParam(Param):
    """An instrument parameter that uses VISA for communication.
    
    Reads and writes parameter settings via the VISA handle that it's
    parent instrument uses.

    TODO implemet rate limits
    TODO should rate limit default to max safe or raise an exception?
    """

    def __init__(self,
                 name,
                 units,
                 get_cmd,
                 set_cmd,
                 parser,
                 instrument=None,
                 mapping=None,
                 validator=None,
                 max_rate=None,
                 max_step=None):
        super.__init__(instrument, name, units, mapping, validator, max_rate,
                       max_step)
        self.write_str = get_cmd
        self.read_str = set_cmd
        self.parser = parser

    def getter(self):
        """Read value from instrument."""
        if self.parser:
            return self.parser.format(self.instrument.ask(self.read_str))
        else:
            return self.instrument.ask(self.read_str)

    def _set(self, value):
        """Directly write value to instrument."""
        if self.mapping:
            self.instrument.write(self.mapping[value])
        else:
            self.instrument.write(self.write_str.format(value))

    def setter(self, value, **kwargs):
        """Handle setting of parameter values.

        Limits on the parameter setpoint and sweep rate are applied if 
        available.

        Args:
            value - new setpoint for parameter.
        Kwargs:
            step - step size for sweeping the paramter.
            rate - sweep rate in units/second for paramter.
        """
        # Check that the requested value does not violate limits
        if self.validator:
            try:
                value = self.validator(value)
            # If the validator raises an exception, re-raise it with
            # information about the instrument and parameter that caused
            # the exception
            except ValueError as e:
                raise ValueError("{}: {} - ".format(self.instrument.name,
                                                    self.name) + e.args[0])
        # If limits are set on the sweep rate then sweep the parameter
        if ["step", "rate"] in kwargs.keys():
            self.sweep(self, value, kwargs["step"], kwargs["rate"])
        # If sweep limits are not provided use the maximum safe values
        elif self.max_rate and self.max_step:
            self.sweep(self, value, self.max_rate, self.max_step)
        # If no sweep limits are set then directly set the parameter.
        else:
            self._set(value)

    def sweep(self, value, step, rate):
        """Continuously adjust the parameter.

        The number of points for the sweep is selected such that the
        maximum step size is not exceeded. The rate of the sweep is
        selected such that the maximum sweep rate is not exceeded

        Args:
            val (float): value of the parameter to sweep to
            rate (float): rate (step/s) to sweep parameter
            step (float): maximum step size of parameter during sweep
        """
        # Check that step size is not too large
        if step > self.max_step:
            raise ValueError("step size {} larger than max {} on {} {}".format(
                step, self.max_step, self.instrument.name, self.name))
        # Check that sweep rate is not too fast
        if rate > self.max_rate:
            raise ValueError(
                "sweep rate {} larger than max {} on {} {}".format(
                    rate, self.max_rate, self.instrument.name, self.name))
        # Define the values that are swept over
        start = self.getter()
        num = math.ceil(np.abs(start - value) / step)
        vals = np.linspace(start, value, num)
        delay = step / rate
        # Run the sweep
        for val in vals:
            self._set(val)
            time.sleep(delay)


def discrete_validator(value, values):
    if value in values:
        return value

    else:
        try:
            closest = min(values, key=lambda x: abs(x - value))
        except TypeError:
            raise ValueError("{} not a valid value".format(value), value)
        else:
            return closest


def continuous_validator(value, minimum, maximum):
    if not minimum <= value <= maximum:
        raise ValueError("{} violates imits {}".format(value, (
            minimum, maximum)), value, minimum, maximum)
    else:
        return value
