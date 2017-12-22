"""
Define classes that are designed to "store data"

subclass np.array with DataSet that contains info about units. Data can
can be collected in np.arrays in cast to DataSet with the np.array view
feature. DataSets can also be directly instantiated during collection.
"""
from git import Repo
import numpy as np


class DataSet(object):
    """A collection of DataArray

    Contains a DataArray for each recorded parameter in a measurement.
    """

    def __init__(self, measurement):
        self.measurement = measurement

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.filename)

    def __repr__(self):
        return str(self)

    def add(self, data_array, name=None):
        """Add a DataArray to the DataSet
        """
        # Re-name data_array in place so the names always match
        if name:
            data_array.name = name
        if hasattr(self, data_array.name):
            raise AttributeError("{} {} already has an attribute {}".format(
                self.__class__.__name__, self.name, data_array.name))
        else:
            setattr(self, data_array.name, data_array)

    def save(self, formatter):
        """Use the formatter to write a file."""
        pass

    @property
    def filename(self):
        """Inherit the filename from the parent Measurement."""
        if hasattr(self.measurement, "filename"):
            return self.measurement.filename

    @classmethod
    def from_getter(cls, measurement, getter):
        """Create a dataset designed to store parameters in a Getter."""
        data_set = cls(measurement)
        for attr in getter.attrs:
            data_set.add(
                DataArray(
                    np.full(measurement.shape, np.nan), attr.name, attr.units))
        return data_set


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
        if obj is None: return
        self.name = getattr(obj, "name", None)
        self.units = getattr(obj, "units", None)

    def __str__(self):
        return "<<{}: {} ({}) from {}\n{}>>".format(
            self.__class__.__name__, self.name, self.units, self.filename,
            np.array2string(self))

    def __repr__(self):
        return str(self)

    @property
    def filename(self):
        """Read filename from parent DataSet."""
        if hasattr(self, "parent"): return getattr(self.parent, "filename")
        else: return None


class Metadata(object):
    """
    Get metadata information for saving.

    Contains:
    - git hash
    - git diff
    - date/time
    - instrument config
    - writing to file
    - printing/slicing utilities
    """

    def __init__(self):
        """Initialize Metadata object.
        """
        self.git_info()
        self.get_setup()

    def git_info(self):
        """Get git info.
        """
        self.repo = Repo(os.path.dirname(measurement.__file__))
        self.git_hash = repo.git.log("-1", "--format=%H")
        self.git_diff = repo.git.diff()

    def get_setup(self):
        """Get info about setup.
        """
        pass

    def write(self):
        """Write a human-readable metadata file.
        """
        pass
