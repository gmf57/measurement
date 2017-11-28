"""
Writing VisaInstrument interface. For now worry just about visa instruments
handle other interfaces later

TODO: Detect value errors before run
TODO: Think about automatically using a "simple" setter if limits are not
defined
"""
import math
import numpy as np
import importlib
from measurement.instruments.property import Property
from measurement.util.printing import Table
from measurement.instruments.base import Loadable

import logging
log = logging.getLogger(__name__)


class Instrument(Loadable):
    def __init__(self, name):
        """
        instrument base class
        """
        self.name = name

    def add(self, prop):
        """Add a property to the instrument"""
        key = "_" + prop.name
        setattr(self, key, prop)
        # Construct a property that uses the get/set methods defined in prop
        setattr(self.__class__, prop.name,
                property(lambda self: getattr(self, key).get(),
                         lambda self, val: getattr(self, key).set(val)))

    def save(self):
        """Save instrument properties"""
        pass

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self.name)

    def table(self, prec=3):
        """Generate a table representation of the instrument
        """
        Table.instrument_table(self, prec=prec).build_table()


class VisaInstrument(Instrument):
    def __init__(self, name, gpib_address):
        self.name = name
        self.gpib_address = gpib_address

    def add(self, prop, get_command, set_command, units):
        """Add a property to the instrument"""
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
