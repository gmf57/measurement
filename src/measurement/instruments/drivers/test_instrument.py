from measurement.instruments.instrument import Instrument
from measurement.instruments.param import ContinuousParam


class FakeInstrument(Instrument):
    I = ContinuousParam("I", "A")
    V = ContinuousParam("V", "V")

    def __init__(self, name):
        super(FakeInstrument, self).__init__(name)
        self.update_validator("I", {"minimum": -1, "maximum": 1})
