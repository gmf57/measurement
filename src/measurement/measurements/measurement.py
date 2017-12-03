"""
Get rid of redundant setting.
Where is the callable array generated?
How does the function of MeasureList differ from TaskList?
Make Sweep accept lists of before/during/after
"""
import os
import math
import numpy as np
import time
import sched
import itertools
import copy
from typing import Callable, Sequence, List
from measurement.instruments.instrument import Instrument

import logging
log = logging.getLogger(__name__)


class Sweep(object):
    """Describes a series of setpoints for an instrument parameter.
    """

    def __init__(self,
                 attr,
                 vals: Sequence,
                 before: Callable=None,
                 during: Callable=None,
                 after: Callable=None) -> None:
        self.attr = attr
        self.vals = vals

        self.before = before
        self.during = during
        self.after = after

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{}: {} from {} to {}".format(
            self.__class__.__name__, self.attr, self.vals[0], self.vals[-1])

    def __add__(self, other: "Sweep") -> "Sweep":
        """Sweeps of the same parameter may be added together."""
        if isinstance(other, Sweep):
            if self.attr == other.attr:
                # Handle before/during/after?
                return Sweep(self.attr, np.append(self.vals, other.vals))
            else:
                raise ValueError("Cannot add Sweeps of different Parameters.")
        else:
            return NotImplemented

    def __iter__(self):
        """Sweep iterates over its values."""
        return iter(self.vals)

    @staticmethod
    def gen_callables(sweep: "Sweep", *args: "Sweep") -> List:
        """Combine n Sweeps into a 1D list of callables.
        """
        callables = []
        # Append any "before" actions
        if sweep.before: callables.append(sweep.before)
        for val in sweep:
            if sweep.during: callables.append(sweep.during)
            callables.append(Setter(sweep.attr, val))
            # Recursively insert elements of other Sweeps
            if args:
                for call in Sweep.gen_callables(*args):
                    callables.append(call)
        # Append any "after" actions
        if sweep.after: callables.append(sweep.after)
        return callables


class MeasureList(object):
    def __init__(self, *args: Callable) -> None:
        self.mlist = args

    def __iter__(self):
        return iter(self.mlist)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.mlist)

    def __call__(self):
        return [c() for c in self.callables]

    def __repr__(self):
        return str(self)


class Measurement(object):
    """Measurements must be callable.

    Should describe the parameter space that is explored as well as the
    parameters that are recorded during the measurement.
    """

    def __init__(self, sweeps, measure):
        """Create a new measurement from sweeps.

        Describe a parameter space to explore with sweeps. Describe what
        parameters are recorded with measure. Measure can either be a set
        or parameters to record or another Measurement.

        Args:
            sweeps (iterable): A set of Sweeps that specifies an
                n-dimensional parameter space to explore.
            measure (iterable): A set of callable that specifies what is
                recorded or what is measured @ each point in sweeps.

        TODO: if you have a Measurement that will run other Measurements,
        how do you make saving work in a reasonable way?
        """
        self.sweeps = sweeps
        self.measure = measure
        self.callables = Sweep.gen_callables(*self.sweeps, measure)

    def __str__(self):
        return "{} @ {}".format(self.__class__.name, self.timestamp)

    def __repr__(self):
        return str(self)

    def __call__(self):
        self.run()

    def run(self):
        # Attach an empty, timestamped dataset
        self.timestamp = datetime.now()
        self.gen_filename()
        self.data = DataSet(self)

        # Collect data
        for c in self.callables:
            if isinstance(c, Getter):
                data = c()
            else:
                c()
                pass
            pass

        # Save

    def gen_filename(self):
        """Find location for saving data.

        TODO - more robust filename generation (check for existing files)
        """
        name = (self.timestamp.strftime("%Y-%m-%d_%H%M%S") + "_" +
                self.__class__.__name__)
        if self.folder:
            self.path = os.path.join(self.folder, name)
        else:
            self.path = os.path.join(measurement.data_folder, name)


class MeasureTime(Measurement):
    """Record a set of parameters periodically over a period of time."""

    def __init__(self, period, time, measure):
        """
        """
        self.period = period
        self.measure = measure
        self.time = time

    def setup(self):
        """Generate a list of callables to execute the measurement."""
        num = int(self.time / self.period)
        self.shape = num
        self.callables = []
        for i in range(num):
            self.callables.append(measure)
            self.callables.append(Wait(self.period))


class Setter(object):
    """Set an instrument setting.

    Makes a callable that utilizes a property's sweeping capabiliy
    """

    def __init__(self, attr, val):
        self.attr = attr
        self.val = val

    def __call__(self):
        """Get the attribute and sweep it to val"""
        logging.info(str(self))
        self.attr.set(val)
        logging.info("done")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "set: {} on {} to {:.3f}".format(self.attr, self.inst, self.val)


class Getter(object):
    """Makes a callable that reads a set of parameters from instruments.

    A Getter describes the action of recording a set of parameters. After
    adjusting parameters in a sweep, calls to the Getter will read data
    from the instruments.
    """

    def __init__(self, attrs: List[Callable]):
        """Instantiate a callable that records attrs.

        Args:
            attrs (iterable): Attributes that are recorded on each call
                to the Getter. Each attr in attrs must be callable
        """
        self.attrs = attrs

    def __call__(self):
        return [attr() for attr in self.attrs]

    def __str__(self):
        return "{} for {}".format(self.__class__.__name__, self.attrs)

    def units(self):
        """Read the units for the attrs in the Getter."""
        return [attr.units for attr in self.attrs]


class Wait(object):
    """Callable waiting."""

    def __init__(self, time):
        self.time = time

    def __call__(self):
        time.sleep(self.time)

    def __str__(self):
        return "{} for {}".format(self.__class__.__name__, self.time)
