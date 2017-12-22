"""
Get rid of redundant setting.
Where is the callable array generated?
How does the function of MeasureList differ from TaskList?
Make Sweep accept lists of before/during/after

Write "validators" for measurements/Sweeps/etc.
"""
import os
import numpy as np
import sched
import copy
from typing import Callable, Sequence, List
from measurement.instruments.instrument import Instrument

import logging
log = logging.getLogger(__name__)


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
