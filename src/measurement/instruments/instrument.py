"""Define an Instrument - a python representation of a single instrument.

Instruments are implemented as a collection of Params. A few methods are
implemented to make modifying the Params easier.
"""

import logging
from measurement.instruments.param import Param
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Instrument(Loadable):
    """Generic representation of an instrument.

    Class-level descriptors manage instance-level data. The discriptors
    use instance-level data stored in Validators to to check changes to
    the values of a instrument parameter.
    """

    def __init__(self, name):
        """Create an instrument with validators to class-level descriptors."""
        self.name = name
        for key, val in self.__class__.__dict__.items():
            if isinstance(val, Param):
                # Create a validator for managing the attribute.
                setattr(self, "_" + key, val._setup())

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def sweep(self, attr, value, rate=None, step=None):
        """Smoothly adjust a parameter on the instrument."""
        pass

    def get_descriptor(self, attr):
        return self.__class__.__dict__[attr]

    def zero(self, attr):
        """Zero an attribute."""
        self.sweep(attr, 0)
