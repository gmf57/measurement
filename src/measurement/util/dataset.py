"""
Define classes that are designed to "store data"

subclass np.array with DataSet that contains info about units. Data can
can be collected in np.arrays in cast to DataSet with the np.array view
feature. DataSets can also be directly instantiated during collection.
"""
from datetime import datetime
import os
from git import Repo
import numpy as np
import measurement
from typing import Sequence
from measurement.measurements.callables import Getter, Sweep
from measurement.measurements.measurement import Measurement


class DataSet(object):
    """A collection of DataArray

    Contains a DataArray for each recorded parameter in a measurement.
    """

    def __init__(self,
                 sweeps: Sequence[Sweep],
                 getters: Sequence[Getter],
                 measurements: Sequence[Measurement],
                 shape):
        """
        """
        self._timestamp = datetime.now()
        self.metadata = self.get_metadata()
        for getter in getters:
            setattr(self, getter.name,
                    DataArray(
                        np.full(shape, np.nan), getter.name, getter.units))
        for m in measurements:
            setattr(self, m.name, [])
        for sweep in sweeps:
            setattr(self, sweep.name, [val for val in sweep.vals])

    def __str__(self):
        return "<{} {}>".format(self.__class__.__name__, self.filename)

    def __repr__(self):
        return str(self)

    def add(self, instrument, attr, shape):
        """Add a data set for a particualr attribute on an instrument."""
        if hasattr(self, instrument.name):
            setattr(self, instrument.name + attr,
                    DataArray(np.full(shape, np.nan)))  # Units?
        else:
            setattr(self, instrument.name, object())

    def append(self, data):
        """Append a new data."""
        for value in data:
            pass

    def save(self):
        """Use the formatter to write a file."""
        return NotImplemented

    def load(self):
        return NotImplemented

    def get_metadata(self):
        """Record information about setup and git repo."""
        repo = Repo(os.path.dirname(measurement.__file__))
        return {
            "git_hash": repo.get.log("-1", "--format=%H"),
            "git_diff": repo.git.diff(),
            "setup": "fix"
        }

    @property
    def timestamp(self):
        """Timestamp is set @ object creation and should not be modified.
        """
        return self._timestamp

    @property
    def filename(self):
        """Filename is set @ object creation and should not be modified.
        """
        return self._filename

    @classmethod
    def from_measure(cls, sweeps, measure, size):
        """Parse a measure into getters and measurements."""
        getters = (call for call in measure if isinstance(call, Getter))
        measurements = (call for call in measure
                        if isinstance(call, Measurement))
        return cls(sweeps, getters, measurements, size)


class TextDataSet(DataSet):
    """Write data to a .txt file."""

    def save(self):
        pass

    def load(self):
        pass


class Hdf5DataSet(DataSet):
    """Write data to a .h5 file."""

    def save(self):
        pass

    def load(self):
        pass


class DataArray(np.ndarray):
    """Store data from a single measured parameter.

    Behaves like an ndarray with a name and units parameter.
    """

    def __new__(cls, input_array, name=None, units=None, dataset=None):
        """
        Args:
            input_array (array): Array to be cast to DataSet type
            name (str): Name of the DataSet
            units (str): Units of the data stored in the DataSet
            dataset (DataSet): Collection of data that the DataArray is a
                member of.
        """
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.units = units
        obj.dataset = dataset
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, "name", None)
        self.units = getattr(obj, "units", None)

    def __str__(self):
        return "<{}: {} ({}) from {}\n{}>".format(
            self.__class__.__name__, self.name, self.units, self.filename,
            np.array2string(self))

    def __repr__(self):
        return str(self)

    @property
    def filename(self):
        """Read filename from parent DataSet."""
        if hasattr(self, "parent"):
            return getattr(self.parent, "filename")
        else:
            return None
