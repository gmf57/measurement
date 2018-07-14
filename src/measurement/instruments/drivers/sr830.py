"""Driver for Stanford Research 830 lock in amplifier.
"""
from ..instruments.instrument import VisaInstrument
from ..instruments.param import VisaParam
from ..instruments.validators import ContinuousValidator


class SR830(VisaInstrument):
    def __init__(self, name, resource):
        super().__init__(name, resource)

        self.add_param(
            VisaParam(
                name="frequency",
                units="Hz",
                get_cmd="FREQ?",
                parser=float,
                set_cmd="FREQ {:.4f}"))

        self.add_param(
            VisaParam(
                name="amplitude",
                units="V",
                get_cmd="SLVL?",
                parser=float,
                set_cmd="SLVL {:.3f}",
                validator=ContinuousValidator(0.004, 5.)))

    def auto_range(self):
        """
        """
        pass
