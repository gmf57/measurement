from measurement.instruments.instrument import Instrument
from measurement.instruments.param import ContinuousParam


class FakeInstrument(Instrument):
    def __init__(self, name):
        super(FakeInstrument, self).__init__(name)
        self.I = ContinuousParam("I", "A", -1, 1, 0.1, 0.1)
        self.V = ContinuousParam("V", "V", -10, 10)
