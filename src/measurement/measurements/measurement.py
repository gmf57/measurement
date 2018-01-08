"""Implement Measurements. Adjust instruments and record the response.

Measurements adjust n different instrument settings exploring a n-dimensional
parameter space. At each point in parameter a list of tasks are executed.

The tasks executed at each point in parameter space can be simple (record
a value on an instrument) or more complicated (execute a different
Measurement).

How does the function of MeasureList differ from TaskList?
Make Sweep accept lists of before/during/after

Write "validators" for measurements/Sweeps/etc.
"""
from typing import Sequence
from measurement.measurements.callables import (Setter, Getter, Wait, TaskList,
                                                Sweep, Measure)

import logging
log = logging.getLogger(__name__)


class Measurement(object):
    """Measurements must be callable.

    Should describe the parameter space that is explored as well as the
    parameters that are recorded during the measurement.
    """

    def __init__(self, sweeps: Sequence[Sweep], measure: Measure) -> None:
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
        self.callables = TaskList.gen_callables(*self.sweeps, measure)

    def __str__(self):
        return "<{} @ {}>".format(self.__class__.name, self.timestamp)

    def __repr__(self):
        return str(self)

    def __call__(self):
        self.run()

    def run(self):
        # Attach an empty, timestamped dataset
        self.data = DataSet.from_measure(self.measure)
        # Collect data
        for call in self.callables:
            if isinstance(call, Measure):
                # Get the data from the callable
                self.data.append(call())
            else:
                call()
        # Save
        self.save()

    def save(self):
        pass

    def duplocate(self):
        pass

    def validate(self):
        """Verify that actions in the measurement will execute.
        """
        for call in self.callables:
            if isinstance(call, (Getter, Setter, Wait, Measurement)):
                if hasattr(call, "validate"):
                    call.validate()
            else:
                raise TypeError("Action {} not permitted in {}.".format(
                    call, self.__class__.__name__))

    @classmethod
    def load(cls, path):
        inst = cls()
        return inst

    @classmethod
    def from_callables(cls, callables):
        """Instantiate a measurement directly from a sequence of callables."""
        inst = cls(None, None)
        inst.callables = callables
        return inst


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
