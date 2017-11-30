"""Record the configuration of a collection of instruments."""

import logging
log = logging.getLogger(__name__)

from .base import Loadable


class Setup(Loadable):
    """Describes a configuration of instruments"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "setup {}".format(self.name)

    def add(self, inst):
        """Add an intsrument to the Setup"""
        setattr(self, inst.name, inst)

    def close(self):
        """Close the instruments"""
        pass
