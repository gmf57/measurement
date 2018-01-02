import pytest
from measurement.instruments.param import ContinuousParam
from measurement.instruments.instrument import Instrument


class FakeInstrument(Instrument):
    """Create a skeleton instrument class so tests don't depend on drivers."""

    def __init__(self, name):
        super(FakeInstrument, self).__init__(name)
        self.I = ContinuousParam("I", "A", -1, 1, 0.1, 0.1)
        self.V = ContinuousParam("V", "V", -10, 10)


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
        """Test that instruments can have different limits on the Param"""
        setup[0].setup("V").minimum
        assert setup[1].V == 2

    def test_param_update(self, setup):
        """Test that changes to the param settings work."""
        setup[0]._V.minimum = -1
        setup[0]._V.maximum = 1
        with pytest.raises(ValueError):
            setup[0].V = 2

    def test_param_access(self, setup):
        """Check that the underlying Params can be accessed."""
        assert isinstance(setup[0].setup("V"), ContinuousParam)

    def test_normal_attr(self, setup):
        """Check that normal attribute access works."""
        pass
