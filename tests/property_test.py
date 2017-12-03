import pytest
from measurement.instruments.property import Property
from datetime import datetime


class TestProperty(object):
    # Define properties with different constraints.
    param_dict = [{
        "minimum": -1,
        "maximum": 1
    }, {
        "rate": 0.1,
        "step": 0.2,
        "minimum": -1,
        "maximum": 1
    }, {
        "maximum": 1
    }]

    @pytest.fixture(params=param_dict)
    def setup(self, request):
        """Generate Property instances with different configuration."""
        return Property("test", "A.U.", **request.param)

    @pytest.fixture
    def setup_single(self):
        return Property("test", "A.U.", 0.1, 0.1, -1, 1)

    @pytest.fixture
    def timing_test(self):
        return Property("test", "A.U.", 0.1, 0.1, -1, 1)

    def test_setting(self, setup_single):
        """Test that values can be set."""
        setup_single.set(0.5)
        assert setup_single.value == 0.5

    def test_limits(self, setup):
        """Test that values are limited."""
        if setup.minimum:
            with pytest.raises(ValueError):
                setup.set(setup.minimum - 1.)
        if setup.maximum:
            with pytest.raises(ValueError):
                setup.set(setup.maximum + 1.)

    def test_rate_limits(self, setup):
        """Test that rate/step are limited on sweeping."""
        if setup.step and setup.rate:
            with pytest.raises(ValueError):
                setup.set(-0.5, rate=setup.rate + 1)

    def test_step_limits(self, setup_single):
        """Test that limits on step work."""
        if setup_single.step and setup_single.rate:
            with pytest.raises(ValueError):
                setup_single.set(0.5, step=setup_single.step + 1)

    def test_sweep_timing(self, timing_test):
        """Test that sweep rate is at least slower than requested rate."""
        start = datetime.now()
        timing_test.set(1)
        delta = datetime.now() - start
        expected = 1 / timing_test.rate
        assert delta.total_seconds() > expected

    def test_callable(self, setup_single):
        """Test that Properties are callable for reading value."""
        assert setup_single() == setup_single.value

    def test_json(self, setup):
        """Verify that a Property can be written and recovered with json."""
        json = setup.to_json()
        copy = Property.from_json(json)
        assert setup.__dict__ == copy.__dict__

    # Test that value is /not/ written during load

    # Test that the logic in set is correct


class TestVisaProperty(object):
    @pytest.fixture
    def setup(self):
        pass

    # Test that Visa iterface works
