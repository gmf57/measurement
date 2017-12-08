import pytest
from measurement.instruments.drivers.test_instrument import FakeInstrument
from measurement.instruments.param import Param


class TestInstrument(object):
    @pytest.fixture
    def setup(self):
        return (FakeInstrument("test1"), FakeInstrument("test2"))

    def test_setting(self, setup):
        """Verify that setting works like a descriptor."""
        setup[0].V = 1
        assert setup[0].V == 1

    def test_different_values(self, setup):
        """Test that two instruments can have different Param values."""
        setup[0].V = 0
        setup[1].V = 1
        assert setup[0].V == 0
        assert setup[1].V == 1

    def test_different_limits(self, setup):
        """Test that instruments can have different limist on the Param"""
        setup[0]._V.minimum = -1
        setup[0]._V.maximum = 1
        setup[1].V = 2
        assert setup[1].V == 2

    def test_param_update(self, setup):
        """Test that changes to the param settings work."""
        setup[0]._V.minimum = -1
        setup[0]._V.maximum = 1
        with pytest.raises(ValueError):
            setup[0].V = 2

    def test_param_access(self, setup):
        """Check that the underlying Params can be accessed."""
        assert type(setup[0]._V) is Param
