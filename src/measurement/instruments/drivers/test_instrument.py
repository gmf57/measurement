from measurement.instruments.instrument import Instrument
from measurement.instruments.param import Param


class FakeInstrument(Instrument):
    def __init__(self, name):
        super(FakeInstrument, self).__init__(name)
        self.add(Param("V", "V"))
        self.add(Param("I", "A", 0.1, 0.1, -1, 1))
