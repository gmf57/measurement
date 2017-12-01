"""Define a Property - a representation of a single instrument setting.

Each setting on an instrument should be representable as a Property.
"""
import sched
import time
import math
import logging
import operator
import numpy as np
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


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

    def __init__(self,
                 name,
                 units,
                 rate=None,
                 step=None,
                 minimum=None,
                 maximum=None,
                 safe="high"):
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
        return "{} = {:.3f} ({}) on {}.".format(self.name, self.value,
                                                self.units, self.instrument)

    def __call__(self):
        """Make Properties callable for interface with Getter."""
        return self.get()

    def set(self, value, rate=None, step=None):
        """Try to set the parameter as safely as possible.

        Use available data to find the safest way to set the value. There
        are 4 different cases:
        - min/max/rate/step all set (value and sweep rate matters)
        - only min/max is set (value but not sweep rate matters)
        - only rate/step is set (sweep rate but not value matters)
        - none of min/max/rate/step are set (no limits on setting value)
        """
        # Raise a ValueError if value is not in [minimum, maximum]
        try:
            self.value_check("minimum", value, operator.ge)
            self.value_check("maximum", value, operator.le)
        except TypeError:
            # Value limits are not set
            pass
        finally:
            # Raise a ValueError if rate/step are set too high
            try:
                self.value_check("rate", rate, operator.le)
                self.value_check("step", step, operator.le)
            except TypeError:
                # Rate limits are not set - directly set the parameter
                self._set(value)
            else:
                # Rate limits are set - sweep the value safely
                self.sweep(value, rate, step)

    def value_check(self, attr, val, op):
        """Verify that requested parameter is within limits."""
        try:
            if op(val, getattr(self, attr)):
                raise ValueError("attempted to set {} to {:.3f}. {} is limit.".
                                 format(attr, val, getattr(self, attr)))
        except ValueError as message:
            log.exception(message)
            raise

    def _set(self, value):
        """Directly set the parameter."""
        self.value = value

    def get(self):
        """Read value of parameter."""
        return self.value

    def sweep(self, val, rate=None, step=None):
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
        """
        # Check that requsted rate does not exceed limit
        if not rate:
            rate = self.rate
        if not step:
            step = self.step
        # Define the values that are swept over
        num = math.ceil(np.abs(self.value - val) / step)
        vals = np.linspace(self.value, val, num)
        # Schedule the sweep
        s = sched.scheduler(time.time, time.sleep)
        delay = step / rate
        _ = [s.enter(delay, 1, self._set, (v, )) for v in vals]
        s.run()

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

    """
    def table(self, prec=3):
        Table.property_table(self, prec=prec).build_table()
    """


class VisaProperty(Property):
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
        super(VisaProperty, self).__init__(name, units, instrument, rate, step,
                                           minimum, maximum, safe)
        self.get_command = get_command
        self.set_command = set_command

        def get(self):
            return self.instrument.ask(get_command)

        def _set(self):
            self.instrument.write(set_command)
