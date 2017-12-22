"""Define a Property - a representation of a single instrument setting.

Each setting on an instrument should be representable as a Property.

Write a lookup table style property
"""
import time
import math
import logging
import operator
import numpy as np
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Param(Loadable):
    """A single Parmeter on an Instrument

    This is a generic interface between settings on an Instrument and
    code. Allows richer interaction than simple @property since arbitrary
    features may exist in the Property class. Features include:
        1. Units
        2. Limits on max/min values, sweep rates, and step sizes
    The units of Property should be the units that the peice of test
    equipment uses.
    """

    def __init__(self,
                 name,
                 units,
                 rate=None,
                 step=None,
                 minimum=None,
                 maximum=None):
        """Create a continuous instrument parameter.

        The value and adjustment of the parameter is controlled by the
        limitations placed on it with minimum/maximum/rate/step.

        Parameters
        ----------
        name : str
            Should have only one Param with a given name per instrument.
        units : str
            Units that the Param is measured in.
        rate : float
            Maximum rate of change of the Param in (units/second).
        step : float
            Maximum step size when the parameter is adjusted.
        minimum : float
            Minimum value of the parameter.
        maximum : float
            Maximum value of the parameter.

        """

        super(Param, self).__init__(name)
        # Info about the property
        self.units = units
        # Limit what the parameter can be set to
        self.rate = rate
        self.step = step
        self.maximum = maximum
        self.minimum = minimum
        # Temporary have a "value" until real visa interface is implemented
        self.value = 0.0

    def __str__(self):
        return "<<{}: {}>>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def __call__(self):
        return self.get()

    def set(self, value, rate=None, step=None):
        """Adjust the parameter as safely as possible.

        Parameters
        ----------
        value : float
            Value to set parameter to.
        rate : float
            Sweep rate of parameter.
        step : float
            Step size of parameter during sweep.

        """
        # Raise a ValueError if the requseted value is restrited
        self.lim_check(value)
        # Use sweep if enough parmeters are set
        if self.rate and self.step:
            self.sweep(value, rate, step)
        else:
            self._set(value)

    def value_check(self, op, val, attr):
        """Raise an exception if a limit on a parameter is violated.

        Parameters
        ----------
        op : function
            Operator comparing value and attribute (e.g. operator.ge)
        val : float
            Requested value.
        attr : str
            Key to get the corresponding limit on the property.

        Raises
        ------
        ValueError
            if val exceeds a limitation when compared to self.attr

        """

        try:
            if not op(val, getattr(self, attr)):
                raise ValueError("{:.3f} violates limit on {}. {} is limit.".
                                 format(val, attr, getattr(self, attr)))
        except ValueError as message:
            log.exception(message)
            raise

    def lim_check(self, val):
        """Verify that parameter setpoint falls within minimum and maximum.

        Parameters
        ----------
        val : float
            Value to compare to minimum and maximum.
        """
        if self.minimum:
            self.value_check(operator.ge, val, "minimum")
        if self.maximum:
            self.value_check(operator.le, val, "maximum")

    def _set(self, value):
        """Directly set the parameter."""
        self.value = value

    def get(self):
        """Read value of parameter."""
        return self.value

    def sweep(self, val, rate=None, step=None):
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
        # Check that requsted rate does not exceed limit
        if not rate: rate = self.rate
        if not step: step = self.step
        self.value_check(operator.le, rate, "rate")
        self.value_check(operator.le, step, "step")

        # Define the values that are swept over
        num = math.ceil(np.abs(self.value - val) / step)
        vals = np.linspace(self.value, val, num)
        delay = step / rate
        # Run the sweep
        for val in vals:
            self._set(val)
            time.sleep(delay)

    def fmt_prop(self, key, prec=3):
        """Format a value for priting with units."""
        # Template for adjusting precision of float formatting
        f_fmt = "{{:.{}f}}".format(prec)
        # Check if the attr is None
        if getattr(self, key) is None:
            return "None"
        # If the attr accepts float formatting then format with the
        # requested precision and with units
        try:
            s = f_fmt.format(getattr(self, key))
            s += " ({}{})".format(self.units, "/s" if key is "rate" else "")
            return s
        # If the attr does not accept float formatting don't use units.
        except ValueError:
            return "{}".format(getattr(self, key))


class DiscreteParam(Loadable):
    """A parameter that takes on a small set of hardware-defined values."""

    def __init__(self, name, values):
        """
        Args:
            values (list): values that the Param can take
        """
        super(DiscreteParam, self).__init__(name)
        self.values = values

    def get(self):
        return self.value

    def set(self, value):
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


class VisaProperty(Loadable):
    """A property that uses Visa to set and read values"""

    def __init__(self,
                 name,
                 get_command,
                 set_command,
                 units,
                 rate=None,
                 step=None,
                 minimum=None,
                 maximum=None,
                 safe=True):
        """
        """
        super(VisaProperty, self).__init__(name, units, rate, step, minimum,
                                           maximum, safe)
        self.get_command = get_command
        self.set_command = set_command

        def get(self):
            return self.instrument.ask(get_command)

        def _set(self):
            self.instrument.write(set_command)
