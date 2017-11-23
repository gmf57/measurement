import sched
import time
import math
import numpy as np

import logging
log = logging.getLogger(__name__)

import sys
sys.path.append("/Users/Matt/emacs/testing")
import measurement
from measurement.util.printing import Table
from measurement.instruments.base import Loadable

class Property(Loadable):
    """A property of an instrument

    This is a generic interface between settings on an Instrument and
    code. Allows richer interaction than simple @property since arbitrary
    features may exist in the Property class. Features include:
        1. Units
        2. Limits on max/min values, sweep rates, and step sizes
    
    The units of Property should be the units that the peice of test
    equipment uses.
    """
    def __init__(self, name, units, rate=None, step=None,
                 minimum=None, maximum=None, safe="high"):
        """
        Args:
            name (str): Name of the parameter.
            get_command (str): String Visa uses to get parameter.
            set_command (str): String Visa uses to set parameter.
            units (str): Unit for the parameter. Should be units that the
                relevant instrument uses.

        Kwargs:
            rate (float): Maximum rate of change (units/second) for the
                 parameter.
            step (float): Maximum ammount param can be changed in a 
                single command.
            minimum (float): Minimum value the parameter may be set to.
            maximum (float): Maximum value the parameter may be set to.
            safe (str): Sets rules for setting the parameter. Values are
                can be ["high", "rate", "value", "none"]
        """
        # Info about the property
        self.name = name
        self.units = units
        self.safe = safe

        # Do not specify an instrument until the property is "added"
        self.instrument = None
        
        # Limit what the parameter can be set to
        self.rate = rate
        self.step = step
        self.maximum = maximum
        self.minimum = minimum

        # Temporary have a "value" until real visa interface is implemented
        self.value = 0.0

    def __str__(self):
        return "{} = {:.3f} ({}) on {}.".format(
            self.name,
            self.value,
            self.units,
            self.instrument)
    
    def set(self, value):
        """Safely set the parameter"""
        if self.safe == "value":
            self.setter(value)
        elif self.safe == "rate":
            self.sweep(value, set_func=self._set)
        elif self.safe == "none":
            self._set(value)
        # Default to maximum safety in setting parameters
        else:
            self.sweep(value)

    def _set(self, value):
        """Directly set the parameter"""
        self.value = value

    def get(self):
        """Read value of parameter"""
        return self.value

    def setter(self, value):
        """Set the attribute

        Check to see if the setpoint falls within the limits of allowed
        setpoints. Set the value by safely sweeping with sweep.

        TODO: Should this check that the requsted value doesn't exceed the
        step? This is in principle done in sweep.
        """
        # Check that the value to write is allowed
        try:
            if value > self.maximum:
                raise ValueError(
                    "attempted to set {0} to {1}. {2} is the max".format(
                        str(self),
                        value,
                        self.maximum))
            if value < self.minimum:
                raise ValueError(
                    "attempted to set {0} to {1}. {2} is the min".format(
                        str(self),
                        value,
                        self.minimum))
        except ValueError as e:
            log.exception(e)
            raise
        except TypeError as e:
            log.exception(e)
            raise
        # If the value is not outside [min, max] then set the value
        self._set(value)

    def sweep(self, val, rate=None, step=None, set_func = None):
        """Sweep the parameter from current value to val

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
            set_func (function): function used to set the value
        """
        # Check that requsted rate does not exceed limit
        if not rate:
            rate = self.rate
        if not step:
            step = self.step
        if not set_func:
            set_func = self.setter
        try:
            if rate > self.rate:
                raise ValueError("invalid sweep rate {} on {}".format(
                    rate,
                    str(self)))
            if step > self.step:
                raise ValueError("invalid step size {} on {}".format(
                    step,
                    str(self)))
        except ValueError as e:
            log.exception(e)
            raise
        # Define the values that are swept over
        num = math.ceil(np.abs(self.value - val) / step)
        vals = np.linspace(self.value, val, num)
        # Schedule the sweep
        s = sched.scheduler(time.time, time.sleep)
        delay = step / rate
        [s.enter(delay, 1, set_func, (v,)) for v in vals]
        s.run()

    def fmt_prop(self, key, prec=3):
        """Format a value for priting with units"""
        # Template for adjusting precision of float formatting
        f_fmt = "{{:.{}f}}".format(prec)

        # Check if the attr is None
        if getattr(self, key) is None:
            return "None"
        
        # If the attr accepts float formatting then format with the
        # requested precision and with units
        try:
            s = f_fmt.format(getattr(self, key))
            s += " ({}{})".format(self.units,
                                  "/s" if key is "rate" else "")
            return s
        
        # If the attr does not accept float formatting don't use units.
        except ValueError:
            return "{}".format(getattr(self, key))

    def table(self, prec = 3):
        """Print a table representation of the property
        """
        Table.property_table(self, prec = prec).build_table()

class VisaProperty(Property):
    """A property that uses Visa to set and read values"""
    def __init__(self, name, get_command, set_command, units,
                 rate=None, step=None, minimum=None, maximum=None, safe=True):
        """
        """
        super(VisaProperty, self).__init__(name, units, instrument, rate,
                                           step, minimum, maximum, safe)
        self.get_command = get_command
        self.set_command = set_command

        def get(self):
            return self.instrument.ask(get_command)

        def _set(self):
            self.instrument.write(set_command)
