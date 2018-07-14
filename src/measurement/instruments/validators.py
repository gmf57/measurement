"""Validators to enforce limitations on Paramter set points.

Validators can be called with an argument. The argument is returned -
possibly modified - if it is a possible setpoint. If the value is not a
valid setpoint then a ValueError is raised.

Classes:
    Validator - Base class that implements the basic callable functionality
        expected for validators.
    ContinuousValidator - Enforces value limitations that lie anywhere
        between a minimum and a maximum value.
    DiscreteValidator - Enforce limitation that a value belongs to a finite
        set of values.
"""


class Validator:
    """Determine if a value for a parameter is within limits or not."""

    def __call__(self):
        raise NotImplementedError

    def __str__(self):
        return "{} for {} on {}".format(self.__class__.__name__,
                                        self.parameter.name,
                                        self.paramter.instrument.name)

    def __repr__(self):
        return str(self)


class ContinuousValidator(Validator):
    """Check if value lies between a maximum and minimum."""

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, value):
        if not self.minimum <= value <= self.maximum:
            raise ValueError("{} violates limits {}".format(
                value, (self.minimum, self.maximum)), value, self.minimum,
                             self.maximum)
        else:
            return value


class DiscreteValidator(Validator):
    """Check if values lie within a strict set of possible values."""

    def __init__(self, values):
        self.values = values

    def __call__(self, value):
        # If the requested value is in the values the return it for setting
        if value in self.values:
            return value
        # If the parameter is numeric try to get the closest allowed value
        else:
            try:
                closest = min(self.values, key=lambda x: abs(x - value))
            # Then the paramter is not numeric
            except TypeError:
                raise ValueError("{} not a valid value".format(value), value)
            else:
                return closest
