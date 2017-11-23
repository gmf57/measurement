"""
Use cases
1. Sweep temp/magnet and do a scan
2. Measure transport as a function of temperature / magnetic field
3. Scan SQUID on various lines while recording data
4.

TODO: Data structure for saving data
TODO: Save in folders
TODO: write logging files
"""
import math
import numpy as np
import time
import sched
import itertools
from datetime import datetime
import copy

import logging
log = logging.getLogger(__name__)

class Measurement:
    """Measurements must be callable"""
    def __init__(self, instruments):
        self.instruments = instruments

    def __str__(self):
        return "measure"

    def run(self):
        pass

    def __call__(self):
        self.run()

    def save(self):
        pass


class Series(Measurement):
    """Execute a list of measurements in a nested fashion"""
    def __init__(self, mlist, sweeps):
        """Set up a series of measurements
        
        Args:
            mlist (iterable): generates a sequence of measurements.
            sweeps (list): a list of Sweep.
        """
        self.mlist = mlist
        self.sweeps = sweeps
        self.data = []
        self.callables = self.setup(self.sweeps)        
        
    def __str__(self):
        return "measurement"

    def save(self):
        """Should save in its own folder"""
        pass

    def run(self):
        """Run the measurement series"""
        # Check if we are have a single sweep or list of sweeps
        [c() for c in self.callables]
        

    def setup(self, sweeps, callables=[]):
        """Change settings for a single round of measurements"""
        if type(sweeps) is list:
            sweep = sweeps[0]
        else:
            sweep = sweeps
        for setting in sweep:
            callables.append(setting)
            # If len(sweeps) > 1 then there are more parameters to set
            if sweeps[1:]:
                self.setup(sweeps[1:], callables)
            # If len(sweeps) = 1 then all parameters are set
            else:
                callables +=  [copy.copy(m) for m in self.mlist]
        return callables
        
    def measure(self):
        return [m() for m in self.mlist]
            
    def show(self):
        """Print a diagram of the measurement series"""
        pass

        
class Setter:
    """Set an instrument setting

    Makes a callable that utilizes a property's sweeping capabiliy"""
    def __init__(self, inst, attr, val):
        self.inst = inst
        self.attr = attr
        self.val = val

    def __call__(self):
        """Get the attribute and sweep it to val"""
        logging.info(str(self))
        getattr(inst, attr).__set__(val)
        logging.info("done")
            
    def __str__(self):
        return "set: param {0} to  val {1} on instrument {2}".format(
            self.attr,
            self.val,
            self.inst)

class Sweep:
    """Specify an instrument and values to sweep over
    """
    def __init__(self, inst, attr, vals, before=None, after=None, during=None):
        """Specify an instrument and values to sweep over

        Args:
            inst (Instrument): The instrument that will be swept
            attr (str): The property of inst that will be swept
            vals (iterable): Values that attr will be set to
            before (callable): Action to perform before the sweep begins
            after (callable): Action to perform after sweep ends
            during (callable): Action to perform between setting vals
        """
        self.inst = inst
        self.attr = attr
        self.vals = vals

        # Check that before after and during are callables
        for action in [before, after, during]:
            if action is not None and action is not callable:
                raise TypeError("before, after and durring must be callable")

        # Construct a list of callables for the Sweep
        self.setters = []
        if before: self.setters.append(before)
        for val in vals:
            if during: self.setters.append(during)
            self.setters.append(Setter(self.inst, self.attr, val))
        if after: self.setters.append(after)
         
    def __iter__(self):
        """Make Sweeps iterable"""
        return (setter for setter in self.setters)
        
    def __str__(self):
        return "sweep {0}: {1} -> {2} on instrument {3}".format(
            self.attr,
            self.vals[0],
            self.vals[-1],
            self.inst)


