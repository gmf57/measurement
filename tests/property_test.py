import pytest


class TestProperty(object):
    @pytest.fixture
    def setup(self):
        from measurement.instruments.property import Property
        p = Property("test", "A.U.")
        return p

    def test_prop(setup):
        assert setup.value == 0


# Test that Properties are limited correctly

# Test timing on Property sweep

# Test that Properties are callable
