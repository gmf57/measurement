"""Reading and writing instrument settings and waiting are callable.

This allows sequences of adjusting/recording instrument parameters to be
set up to form a measurement.
"""
import numpy as np
import time
from collections import OrderedDict
from typing import Sequence, Callable, List
from measurement.instruments.instrument import Instrument
from measurement.measurements.measurement import Measurement

import logging
log = logging.getLogger(__name__)


class Setter(object):
    """Set an instrument setting.

    Makes a callable that utilizes a property's sweeping capabiliy
    """
    __slots__ = ["inst", "attr", "val"]

    def __init__(self, inst: Instrument, attr: str, val) -> None:
        self.isnt = inst
        self.attr = attr
        self.val = val

    def __call__(self):
        """Get the attribute and sweep it to val"""
        logging.info(str(self))
        setattr(self.inst, self.attr, self.val)
        logging.info("done")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<{}: {} on {} -> {:.3f}>".format(
            self.__class__.__name__, self.attr, self.instr, self.val)

    def validate(self):
        """Check if the setter violates limits on paramter."""
        pass


class Getter(object):
    __slots__ = ["inst", "attr"]

    def __init__(self, inst: Instrument, attr: str) -> None:
        self.inst = inst
        self.attr = attr

    def __call__(self):
        return getattr(self.inst, self.attr)

    def __str__(self):
        return "<{}: {} from {}>".format(self.__class__.__name__, self.attr,
                                         self.inst)

    def __repr__(self):
        return str(self)

    @property
    def units(self):
        return self.inst.get_validator(self.attr)['units']

    @property
    def name(self):
        return self.inst.name + "_" + self.attr

    @staticmethod
    def gen_getters(insts: Sequence[Instrument], attrs: Sequence[str]) -> List:
        """Create a list of getters from a list of instruments and attributes.
        """
        getters = []
        for inst, attr in zip(insts, attrs):
            getters.append(Getter(inst, attr))
        return getters


class Wait(object):
    """Callable waiting."""
    __slots__ = ["time"]

    def __init__(self, time):
        self.time = time

    def __call__(self):
        time.sleep(self.time)

    def __str__(self):
        return "<{} for {}>".format(self.__class__.__name__, self.time)


class TaskList(object):
    """
    """

    def __init__(self, callables: Sequence[Callable]) -> None:
        self.callables = callables

    def __iter__(self):
        return iter(self.callables)

    def __add__(self, other):
        return self.callables + other.callables

    @staticmethod
    def parse(call1, call2):
        """Take either a single callable or list of callables and make a
        TaskList
        """
        try:
            return call1 + call2
        except TypeError:
            pass

    @classmethod
    def combine_sweeps(cls, sweep: "Sweep", *args: "TaskList") -> "TaskList":
        """Nest one sequence of callables inside another.

        Takes two Sweeps with a structure:
        [a1, a2, a3]
        [b1, b2, b3]

        And makes a sequence of callables:
        [a1, (b1, b2, b3), a2, (b1, b2, b3), a3, (b1, b2, b3)]

        Recursive calls with a set of sweeps will generate a complete mapping
        of the parameter space specified by the sweeps without any reduntant
        Setters in the final TaskList.
        """
        callables = []
        # Append actions done once before sweeping the paramter
        if sweep.before:
            callables.append(sweep.before)
        # Iterate over callables in the sweep
        for call in sweep:
            # Append actions done at each set point for the parameter
            if sweep.during:
                callables.append(sweep.during)
            # Recursively insert the callables from other sweeps in args
            callables.append(call)
            if args:
                for other_call in TaskList.gen_callables(*args):
                    callables.append(other_call)
        # Append actions done once after the sweep is complete
        if sweep.after:
            callables.append(sweep.after)
        return cls(callables)


class Sweep(TaskList):
    """Describes the adjustment of a single instrument parameter.
    """

    def __init__(self,
                 inst: Instrument,
                 attr: str,
                 vals,
                 before=None,
                 after=None,
                 during=None) -> None:
        """
        """
        super(Sweep, self).__init__([Setter(attr, val) for val in vals])
        self.inst = inst
        self.attr = attr
        self.vals = vals
        self.before = before
        self.during = during
        self.after = after

    def __add__(self, other):
        if isinstance(other, Sweep):
            if other.attr == self.attr:
                # Then the Sweeps can add
                before = TaskList.parse(self.before, other.before)
                during = TaskList.parse(self.during, other.during)
                after = TaskList.parse(self.after, other.after)
                return Sweep(self.attr,
                             np.append(self.vals, other.vals), before, during,
                             after)
            else:
                raise ValueError("Cannot add Sweeps of different attributes.")
        else:
            return NotImplemented

    def __str__(self):
        return "<{}: {} on {}: {} -> {}>".format(self.__class__.__name__,
                                                 self.attr, self.inst,
                                                 self.vals[0], self.vals[-1])

    def __repr__(self):
        return str(self)

    def insert(self, other):
        """Nest one sequence of callables inside another.

        Takes two Sweeps with a structure:
        [a1, a2, a3]
        [b1, b2, b3]

        And makes a sequence of callables:
        [a1, (b1, b2, b3), a2, (b1, b2, b3), a3, (b1, b2, b3)]

        Recursive calls with a set of sweeps will generate a complete mapping
        of the parameter space specified by the sweeps without any reduntant
        Setters in the final TaskList.
        """
        callables = []
        if self.before:
            callables.append(self.before)
        for call in self.callables:
            callables.append(call)
            if self.during:
                callables.append(self.during)
            for other_call in other:
                callables.append(other_call)
        if self.after:
            callables.append(self.after)
        return TaskList(callables)


class Measure(OrderedDict):
    """A set of tasks executed at each point in a Measurement's parameter space.

    Has the structure of a dict with key/val pairs. Keys are names of parameters
    values are callables.
    """

    def __init__(self, *args, **kwargs):
        super(Measure, self).__init__(*args, **kwargs)

    def __call__(self):
        return [call() for call in self.values()]

    def validate(self):
        for call in self.tasks:
            if isinstance(call, (Getter, Measurement)):
                pass
            else:
                raise TypeError("Action {} not permitted in {}.".format(
                    call, self.__class__.__name))

    @classmethod
    def gen_measure(cls, callables: Sequence[Callable]) -> "Measure":
        """Create a Measure from a list of callables."""
        ret = cls()
        for call in callables:
            ret.update({call.name, call})
        return ret
