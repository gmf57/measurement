import sys
sys.path.append("/Users/Matt/emacs/testing")
from measurement.instruments.instrument import Instrument
from measurement.instruments.property import Property


class InstrumentTest(Instrument):
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
