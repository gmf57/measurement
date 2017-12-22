import numpy as np
from typing import Sequence, Callable
from measurement.measurements.callables import Setter


class TaskList(object):
    """
    """

    def __init__(self, callables: Sequence[Callable]) -> None:
        self.callables = callables

    def __iter__(self):
        return iter(self.callables)

    def __add__(self, other):
        return self.callables + other.callables

    def __call__(self):
        [c() for c in self.callables]

    @classmethod
    def parse(call1, call2):
        """Take either a single callable or list of callables and make a
        TaskList
        """
        try:
            return call1 + call2
        except TypeError:
            pass


class Sweep(TaskList):
    """
    """

    def __init__(self, attr, vals, before=None, after=None,
                 during=None) -> None:
        """
        """
        super(Sweep, self).__init__([Setter(attr, val) for val in vals])
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
        return "{}: {}: {} -> {}".format(self.__class__.__name__, self.attr,
                                         self.vals[0], self.vals[-1])

    def __repr__(self):
        return str(self)

    def insert(self, other):
        """
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


class MeasureList(TaskList):
    """
    """

    def __init__(self, callables: Sequence[Callable]) -> None:
        """
        """
        super(TaskList, self).__init__(callables)

    def __call__(self):
        return [c() for c in self.callables]

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.callables)

    def __repr__(self):
        return str(self)
