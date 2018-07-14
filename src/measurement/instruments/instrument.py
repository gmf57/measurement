"""Define an Instrument - a python representation of a single instrument.

Instruments are implemented as a collection of Params. A few methods are
implemented to make modifying the Params easier.
"""

import logging
from measurement.instruments.param import Param
from measurement.instruments.base import Loadable
import visa

log = logging.getLogger(__name__)


class Instrument(Loadable):
    """Generic representation of an instrument.
    """

    def __init__(self, name):
        """
        """
        self.name = name

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)

    def sweep(self, attr, value, rate=None, step=None):
        """Smoothly adjust a parameter on the instrument."""
        pass

    def zero(self, attr):
        """Zero an attribute."""
        self.sweep(attr, 0)

    def add_param(self, param):
        if hasattr(self, param.name):
            raise AttributeError(
                "Instrument already has a parameter {}".format(param.name))
        else:
            setattr(self, param.name, param)
            setattr(param, "instrument", self)


def named_instrument(name, config_file, base):
    """Create an instrument class from a configuation file."""

    def __init__(self, name):
        self.name = name

    namespace = {
        "__init__": __init__,
    }

    return type(name, (Instrument, ), namespace)


class VisaInstrument(Instrument):
    """An instrument using the VISA communication protocol."""

    def __init__(self, name, resource=None, timeout=5, terminator=""):
        super().__init__(name)
        self.resouce = resource
        self.timeout = timeout
        rm = visa.ResourceManager()
        try:
            self.visa_handle = rm.open_resource(resource)
        except Exception as e:
            log.info("Connecting to {} instrument at {} failed.".format(
                name, resource))
            self.close()
            raise e
        self._terminator = terminator
        self.visa_handle.write_termination = terminator
        self.visa_handle.read_termination = terminator
        if timeout:
            # Visa uses ms for timeout
            self.visa_handle.timeout = timeout * 1000
        else:
            self.visa_handle.timeout = None

    def check_error(self, code):
        """Let visa return code errors propagate up to the instrument."""
        if code is not 0:
            raise visa.VisaIOError(code)

    def close(self):
        """Close the visa handle when closing the instrument."""
        if hasattr(self, "visa_handle"):
            self.visa_handle.close()

    def write(self, cmd):
        """Write data to the visa handle."""
        written, code = self.visa_handle.write(cmd)
        self.check_error(code)

    def ask(self, cmd):
        """Ask for data from the visa handle."""
        return self.visa_handle.query(cmd)
