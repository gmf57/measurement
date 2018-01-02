"""
Writing VisaInstrument interface. For now worry just about visa instruments
handle other interfaces later
"""

import logging
from measurement.instruments.param import ContinuousValidator, ContinuousParam
from measurement.instruments.param import DiscreteValidator, DiscreteParam

from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Instrument(Loadable):
    def __init__(self, name):
        self.name = name
        for key, val in self.__class__.__dict__.items():
            if isinstance(val, ContinuousParam):
                setattr(self, "_" + key, ContinuousValidator(key))
            if isinstance(val, DiscreteParam):
                setattr(self, "_" + key, DiscreteValidator(key, val.values))

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def sweep(self, attr, value, rate=None, step=None):
        """Smoothly adjust a parameter on the instrument."""
        pass

    def get_validator(self, attr):
        return getattr(self, "_" + attr)

    def update_validator(self, attr, limits):
        self.get_validator(attr).set_limits(**limits)


class VisaInstrument(Instrument):
    """Describes an instrument that communicates via VISA interface."""

    def __init__(self, name, gpib_address):
        """Initialize an instrument with VISA communication."""
        super(VisaInstrument, self).__init__(name)
        self.gpib_address = gpib_address

    def add(self, prop, get_command, set_command, units):
        """Add a property to the instrument."""
        setattr(self, prop,
                VisaProperty(prop, get_command, set_command, units, self))

    def write_raw(self, cmd):
        bytes_written, ret_code = self.visa_handle.write(cmd)

    def ask_raw(self, cmd):
        return self.visa_handle.ask(cmd)

    def set_address(self, address):
        """Open VISA connection for instrument"""
        # Close an existing visa handle
        if getattr(self, 'visa_handle', None):
            self.visa_handle.close()

        resource_manager = visa.ResourceManager()
        self.visa_handle = resource_manager.open_resource(address)
        self._address = address

    def save(self):
        """Save the configuration of the instrument"""
        pass
