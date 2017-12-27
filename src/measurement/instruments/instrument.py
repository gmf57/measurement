"""
Writing VisaInstrument interface. For now worry just about visa instruments
handle other interfaces later
"""

import logging
from measurement.instruments.param import Param
from measurement.util.printing import Table
from measurement.instruments.base import Loadable

log = logging.getLogger(__name__)


class Instrument(Loadable):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "<<{} {}>>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def __delattr__(self, name):
        res = self.__dict__.get(name)
        for method in ('__get__', '__set__', '__delete__'):
            if hasattr(res, method):
                # If the attribute implements a descriptor protocol, use it.
                res = res.__delete__(name)
                break
        else:
            res = object.__delattr__(self, name)
        return res

    def __getattribute__(self, *args):
        res = object.__getattribute__(self, *args)
        for method in ('__get__', '__set__', '__delete__'):
            if hasattr(res, method):
                # we have a descriptor, call it
                res = res.__get__(self, self.__class__)
        return res

    def __setattr__(self, name, value):
        try:
            obj = object.__getattribute__(self, name)
        except AttributeError:
            pass
        else:
            if hasattr(obj, '__set__'):
                return obj.__set__(self, value)
        return object.__setattr__(self, name, value)

    def sweep(self, attr, value, rate=None, step=None):
        """Smoothly adjust a parameter on the instrument."""
        pass

    def setup(self, attr, **kwargs):
        """Return a descriptor and optionally modify it's attributes.

        Bypasses the __getattribute__ descriptor protocal allowing inspection
        and modification of the descriptor attribues"""
        for key, value in kwargs.items():
            try:
                setattr(self.__dict__[attr], key, value)
            except AttributeError:
                pass
        return self.__dict__[attr]


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
