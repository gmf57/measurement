import pytest
from measurement.instruments.param import Param, DiscreteParam, ContinuousParam
from measurement.instruments.instrument import Instrument
from datetime import datetime


class FakeInstrument(Instrument):
    """An container for various Parameters.

    Parameters control values on Instrument instances so we must instatiate
    a simple instrument in order to test Parameter behavior.
    """
    no_limit = ContinuousParam("A.U.")
    val_limit = ContinuousParam("A.U.")
    sweep_limit = ContinuousParam("A.U.")
    single_limit = ContinuousParam("A.U.")

    def __init__(self, name="test"):
        super(FakeInstrument, self).__init__(name)
        self.update_validator("val_limit", {"minimum": -1, "maximum": 1})
        self.update_validator("sweep_limit", {"rate": 0.1, "step": 0.1})
        self.update_validator("single_limit", {"minimum": 1})
        # Manually set starting values for testing
        for attr in ["val_limit", "sweep_limit", "single_limit"]:
            self.__dict__[attr] = 0


class TestContinuousParam(object):
    @pytest.fixture
    def setup(self, request):
        """Generate Property instances with different configuration."""
        return FakeInstrument()

    def test_setting(self, setup):
        """Test that values can be set.

        Params should implement a descriptor protocal allowing you to set/read
        attributes with simple statements."""
        setup.no_limit = 0.5
        assert setup.no_limit == 0.5
        setup.val_limit = 0.5
        assert setup.val_limit == 0.5
        setup.sweep_limit = 0.5
        assert setup.sweep_limit == 0.5
        setup.single_limit = 2
        assert setup.single_limit == 2

    def test_limits(self, setup):
        """Test that values are limited."""
        with pytest.raises(ValueError):
            setup.val_limit = 2
        with pytest.raises(ValueError):
            setup.val_limit = -2
        with pytest.raises(ValueError):
            setup.single_limit = 0.1

    def test_sweep_timing(self, setup):
        start = datetime.now()
        setup.sweep_limit = 1
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
        setup.sweep_limit = 0
        setup.update_validator("sweep_limit", {
            "minimum": 1,
            "maximum": 2,
            "step": 0.2,
            "rate": 0.5
        })
        setup.sweep_limit = 1.0
        with pytest.raises(ValueError):
            setup.sweep_limit = 0.5


class DiscreteInstrument(Instrument):
    """An container for various Parameters.

    Parameters control values on Instrument instances so we must instatiate
    a simple instrument in order to test Parameter behavior.
    """
    numeric = DiscreteParam([1, 2, 3])
    string = DiscreteParam(["a", "b", "c"])

    def __init__(self, name="test"):
        super(DiscreteInstrument, self).__init__(name)
        self.__dict__["numeric"] = 0


class TestDiscreteParam(object):
    @pytest.fixture
    def setup(self):
        """Test parameters with string settings."""
        return DiscreteInstrument()

    def test_setting(self, setup):
        """Test setting numeric and string-like discrete parameters."""
        setup.numeric = 2
        assert setup.numeric == 2
        setup.string = "a"
        assert setup.string == "a"

    def test_nearest(self, setup):
        """Test setting with value outside the accepted values.
        DiscreteParams with numeric settings should set to the value
        closest to the requested value. DiscretParams with string settings
        will raise an exception.
        """
        setup.numeric = 4
        assert setup.numeric == 3

    def test_str_limits(self, setup):
        """DiscreteParams with str settings allow only expected values.
        with pytest.raises(ValueError):
            setup_str.set(5)
        with pytest.raises(ValueError):
            setup_str.set("d")
        """
        with pytest.raises(ValueError):
            setup.string = 5
        with pytest.raises(ValueError):
            setup.string = "d"
