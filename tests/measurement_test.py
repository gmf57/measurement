import pytest
from measurement.measurements.measurement import Measurement
from measurement.instruments.drivers.test_instrument import InstrumentTest

class TestMeasurement(object):
    @pytest.fixture
    def setup(self):
        # Create a measurement
        ti = InstrumentTest("test")
        s1 = Sweep(ti._I, np.linspace(0, 1, 10))
        ml = Getter([ti._V])
    # Test that measurements are callable
    def 
        



