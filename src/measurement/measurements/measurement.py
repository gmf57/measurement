"""
Use cases
1. Sweep temp/magnet and do a scan
2. Measure transport as a function of temperature / magnetic field
3. Scan SQUID on various lines while recording data
4.

TODO: Data structure for saving data
TODO: Save in folders
TODO: write logging files
"""
import os
import math
import numpy as np
import time
import sched
import itertools
import copy
from typing import Callable, Sequence
from measurement.instruments.instrument import Instrument

import logging
log = logging.getLogger(__name__)


class Sweep(object):
    """Specify an instrument and values to sweep over.

    Provides an interface for sweeping a tuning parameter on an
    instrument over a range of values. Allows a set of callables to be
    executed before the sweep, after the sweep or at each point in the
    sweep.

    TODO - define + for sweeps
    """

    def __init__(self, attr, setters: Sequence[Callable]) -> None:
        """Specify an instrument and values to sweep over.

        Args:
            inst (Instrument): The instrument that will be swept
            attr (str): The property of inst that will be swept
            setters (list): List of setters that the Sweep will apply
        """
        self.attr = attr
        self.setters = setters

    def compare(self, other):
        return self.attr == other.attr

    def __add__(self, other):
        """Create composite sweeps with + operator.
        
        For sweeps to add they must operate on the same instrument
        parameter."""
        if not isinstance(other, Sweep):
            raise NotImplementedError
        elif self.compare(other):
            setters = self.setters + other.setters
            return Setter(self.attr, setters)

    def __mul__(self, other):
        """Outer product of sweeps."""
        return Sweep(self.attr + other.attr, self.setters + other.setters)

    def __iter__(self):
        """Make Sweeps iterable."""
        return (setter for setter in self.setters)

    def __len__(self):
        return len(self.setters)

    def append(self, obj: [Callable]) -> None:
        """Append a Callable to the sweep."""
        self.setters.append(obj)

    def pop(self, index):
        """Remove and return the ith setter."""
        return self.setters.pop(index)

    def reverse(self):
        """Reverse the sweep direction - in place."""
        self.setters = self.setters.reverse()

    def __str__(self):
        return "sweep {0}: {1} -> {2} on instrument {3}".format(
            self.attr, self.vals[0], self.vals[-1], self.inst)

    @classmethod
    def sweep(cls,
              inst: Instrument,
              attr,
              vals,
              before: Callable=None,
              after: Callable=None,
              during: Callable=None) -> Any:
        """
        Generate a sweep instance from a set of values.

        Args:
            inst (Instrument): The instrument that will be swept
            attr (str): The property of inst that will be swept
            vals (iterable): Values that attr will be set to
            before (callable): Action to perform before the sweep begins
            after (callable): Action to perform after sweep ends
            during (callable): Action to perform between setting vals
        """
        setters = []
        if before: setters.append(before)
        for val in vals:
            if during: setters.append(during)
            setters.append(Setter(inst, attr, val))
        if after: setters.append(after)
        return cls([attr], [setters])


class Measurement:
    """Measurements must be callable.

    Should describe the parameter space that is explored as well as the
    parameters that are recorded during the measurement.
    """

    def __init__(self, measure):
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
        self.measure = measure

    def __str__(self):
        return "{} @ {}".format(self.__class__.name, self.timestamp)

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

    def __call__(self):
        self.run()


class MeasureSweep(Measurement):
    """Record parameters while sweeping setting on instruments.

    Performs the measurements in mlist at each point in the configuration
    space specified by set of Sweep in sweeps.
    """

    def __init__(self, mlist: Sequence[Callable], sweep: Sweep) -> None:
        """Set up a series of measurements.
        Args:
            mlist (iterable): generates a sequence of measurements.
            sweeps (list): a list of Sweep.
        """
        self.mlist = mlist
        if isinstance(sweeps, Sweep):
            self.sweeps = [sweeps]
        else:
            self.sweeps = sweeps
        self.callables = self.setup(self.sweeps)

    def setup(self, sweeps, callables=[]):
        """Test"""
        sweep = sweeps[0]
        for setting in sweep:
            callables.append(setting)
            try:
                self.setup(sweeps[1:], callables)
            except IndexError:
                callables = callables + [copy.copy(m) for m in self.mlist]
        return callables

    def show(self):
        """Print a diagram of the measurement series"""
        pass


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

    def __init__(self, inst, attr, val):
        self.inst = inst
        self.attr = attr
        self.val = val

    def __call__(self):
        """Get the attribute and sweep it to val"""
        logging.info(str(self))
        getattr(inst, attr).set(val)
        logging.info("done")

    def __str__(self):
        return "set: param {} to {.3f}".format(self.attr, self.val)


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
