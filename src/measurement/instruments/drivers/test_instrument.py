from measurement.instruments.instrument import Instrument
from measurement.instruments.param import ContinuousParam
from measurement.instruments.param import Param
import numpy as np


class FakeInstrument(Instrument):
    I = ContinuousParam("I", "A")
    V = ContinuousParam("V", "V")

    def __init__(self, name):
        super(FakeInstrument, self).__init__(name)


class RandomInstrument(Instrument):
    """An instrument that generates random values."""
    pass


class VirtualDAQ(Instrument):
    """Emulate the DAQ interface."""
    pass


class RandomParam(Param):
    """Emulate a parameter."""

    def getter(self):
        return np.random.randn()


class VirtualParam(Param):
    def __init__(self,
                 name,
                 units,
                 instrument=None,
                 mapping=None,
                 validator=None,
                 max_rate=None,
                 max_step=None):
        super(self).__init__(name, units, instrument, mapping, validator,
                             max_rate, max_step)
        self.value = 0.

    def getter(self):
        return self.value

    def setter(self, value):
        self.value = value
