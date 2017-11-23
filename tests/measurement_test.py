import numpy as np
import sys
sys.path.append("/Users/Matt/emacs/testing")
import measurement
from measurement.measurements.measurement import Measurement
from measurement.instruments.property import Property
from measurement.instruments.instrument import Instrument

class TestMeasurement(Measurement):
    """A measurement that uses a TestInstrument"""
    def __init__(self, instruments, currents):
        self.instruments = instruments
        self.currents = currents
        self.data = []
    def run(self):
        for current in self.currents:
            self.instruments.I.value = current
            self.data.append(self.instruments.Vsin.__get__())

class TestInstrument(Instrument):
    def __init__(self, name):
        self.name = name
        # add varios property objects
        self._V = Property("V", "V")
        self._I = Property("I", "A", 0.1, 0.1, -1, 1)

    @property
    def V(self):
        # read the property
        return self._I.value * 10 + np.random.randn(1)
    
    @V.setter
    def V(self, value):
        # call setter here for the attribute
        self._V.set(value)
        
    @property
    def I(self):
        return self._I.value

    @I.setter
    def I(self, value):
        self._I.set(value)


def timing_test():
    """
    Test the timing of instrument sweeps
    """
    times = []
    
        



