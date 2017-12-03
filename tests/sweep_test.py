import numpy as np
import pytest
from measurement.measurements.measurement import Sweep
from measurement.instruments.drivers.test_instrument import InstrumentTest


class TestSweep(object):
    @pytest.fixture
    def setup(self):
        ti = InstrumentTest("test")
        s1 = Sweep(ti._V, np.linspace(0, 1, 10))
        s2 = Sweep(ti._I, np.linspace(0, 1, 10))
        s3 = Sweep(ti._V, np.linspace(1, 2, 10))
        return [s1, s2, s3]

    def test_addition(self, setup):
        """Test addition of Sweeps."""
        # Adding Sweeps of different parameters raises a ValueError
        with pytest.raises(ValueError):
            setup[0] + setup[1]
        # Adding Sweeps with other objects raises a TypeError
        with pytest.raises(TypeError):
            setup[0] + 5
        # Adding Sweeps of the same Parameter is fine
        sweep_sum = setup[0] + setup[2]
        assert sweep_sum.__class__ == setup[0].__class__
        assert (sweep_sum.vals == np.append(setup[0].vals,
                                            setup[2].vals)).all()

    def test_iter(self, setup):
        """Verify that Sweeps iterate over sweep.vals."""
        for i, val in enumerate(setup[0]):
            assert val == setup[0].vals[i]

    def test_gen_callables(self, setup):
        """Test flattening of multiple sweeps into a list of Callables."""
        callables = Sweep.gen_callables(*setup)
        assert False  # Finish this test


class TestSetter(object):
    pass
