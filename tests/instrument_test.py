import unittest


class TestProperty(unittest.TestCase):
    def setUp(self):
        p = Property(
            name="test", units="V", rate=0.2, step=0.1, minimum=-1, maximum=1)

    def test_rate_limiting(self):
        """Test that sweep rate is limited by step size and sweep rate."""
        pass

    def test_value_limit(self):
        """Verify that the value of the Property is lmited."""

    def test_partial_limiting(self):
        """Verify that properties ony a few of min/max/rate/step
        defined still impose constraints - if possible.
        """
