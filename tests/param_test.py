import pytest
from measurement.instruments.param import Param, DiscreteParam, ContinuousParam
from measurement.instruments.instrument import Instrument
from datetime import datetime


class FakeInstrument(Instrument):
    """An container for various Parameters.

    Parameters control values on Instrument instances so we must instatiate
    a simple instrument in order to test Parameter behavior.
    """
    no_limit = ContinuousParam("no_limit", "V")
    val_limit = ContinuousParam("val_limit", "V", -1, 1)
    sweep_limit = ContinuousParam("sweep_limit", "V", -1, 1, 0.1, 0.1)
    single_limit = ContinuousParam("single_limit", "V", maximum=10)


class TestContinuousParam(object):
    @pytest.fixture
    def setup(self, request):
        """Generate Property instances with different configuration."""
        return FakeInstrument("test")

    def test_setting(self, setup):
        """Test that values can be set.

        Params should implement a callable api - you read/write params
        with the __call__ method."""
        setup.no_limit(0.5)
        assert setup.no_limit() == 0.5
        setup.val_limit(0.5)
        assert setup.val_limit() == 0.5
        setup.sweep_limit(0.5)
        assert setup.sweep_limit() == 0.5
        setup.single_limit(-1)
        assert setup.sweep_limit() == -1

    def test_limits(self, setup):
        """Test that values are limited."""
        with pytest.raises(ValueError):
            setup.val_limit(2)
        with pytest.raises(ValueError):
            setup.val_limit(-2)
        with pytest.raises(ValueError):
            setup.single_limit(11)

    def test_sweep_timing(self, setup):
        """Test that sweep rate is limited."""
        start = datetime.now()
        setup.sweep_limit(1)
        end = datetime.now()
        delta = end - start
        assert delta.seconds >= 10

    def test_json(self, setup):
        """Verify that a Property can be written and recovered with json."""
        json = setup.__class__.sweep_limit.to_json()
        copy = ContinuousParam.from_json(json)
        assert setup.__class__.sweep_limit.__dict__ == copy.__dict__

    def test_new_limit(self, setup):
        """Verify that changing the min/max when value is outside the new
        limits works.

        This is accomplished by checking value limits of final value only
        instead of at each intermediate step."""
        setup.sweep_limit(0)
        setup.sweep_limit.minimum = 1
        setup.sweep_limit.maximum = 2
        setup.sweep_limit(1.5)
        # Check that adjustment works
        assert setup.sweep_limit() == 1.5
        with pytest.raises(ValueError):
            setup.sweep_limit(0.5)


class DiscreteInstrument(Instrument):
    """An container for various Parameters.

    Parameters control values on Instrument instances so we must instatiate
    a simple instrument in order to test Parameter behavior.
    """
    numeric = DiscreteParam("numeric", "V", [1, 2, 3])
    string = DiscreteParam("string", None, ["a", "b", "c"])

    def __init__(self, name="test"):
        super(DiscreteInstrument, self).__init__(name)


class TestDiscreteParam(object):
    @pytest.fixture
    def setup(self):
        """Test parameters with string settings."""
        return DiscreteInstrument()

    def test_setting(self, setup):
        """Test setting numeric and string-like discrete parameters."""
        setup.numeric(2)
        assert setup.numeric() == 2
        setup.string("a")
        assert setup.string() == "a"

    def test_nearest(self, setup):
        """Test setting with value outside the accepted values.
        DiscreteParams with numeric settings should set to the value
        closest to the requested value. DiscretParams with string settings
        will raise an exception.
        """
        setup.numeric(4)
        assert setup.numeric() == 3

    def test_str_limits(self, setup):
        """DiscreteParams with str settings allow only expected values.
        with pytest.raises(ValueError):
            setup_str.set(5)
        with pytest.raises(ValueError):
            setup_str.set("d")
        """
        with pytest.raises(ValueError):
            setup.string(5)
        with pytest.raises(ValueError):
            setup.string("d")
