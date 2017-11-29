"""
Define classes that are designed to "store data"

subclass np.array with DataSet that contains info about units. Data can
can be collected in np.arrays in cast to DataSet with the np.array view
feature. DataSets can also be directly instantiated during collection.
"""
from git import Repo
from datetime import datetime
import numpy as np
import measurement


class DataSet(object):
    """A collection of DataArray

    Contains a DataArray for each recorded parameter in a measurement.
    """

    def __init__(self, measurement):
        pass

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.name)

    def add(self, data_array, name=None):
        """Add a data_set to the DataArray
        """
        try:
            setattr(self, name, data_array)
        except TypeError:
            setattr(self, data_array.name, data_array)

    def save(self, formatter):
        """Use the formatter to write a file."""
        pass

    def gen_filename(self, folder=None):
        """Find location for saving data.

        TODO - more robust filename generation (check for existing files)
        """
        name = (self.timestamp.strftime("%Y-%m-%d_%H%M%S") + "_" +
                self.__class__.__name__)
        try:
            self.path.os.path.join(folder, name)
        except TypeError:
            self.path = os.path.join(measurement.data_folder, name)

    @classmethod
    def from_measurement(cls, measurement, getter):
        """Create a dataset storing filenames from a Measurement series."""
        data_set = cls(measurement)

    @classmethod
    def from_getter(cls, getter):
        """Create a dataset designed to store parameters in a Getter."""
        data_set = cls()
        for attr in getter.attrs:
            data_set.add(
                DataArray(
                    np.full(measurement.shape, np.nana), attr.name,
                    attr.units))
        return data_set


class DataArray(np.ndarray):
    """Store data from a single measured parameter. 

    Behaves like an ndarray with a name and units parameter.    
    """

    def __new__(cls, input_array, name=None, units=None):
        """
        Args:
            input_array (array): Array to be cast to DataSet type
            name (str): Name of the DataSet
            units (str): Units of the data stored in the DataSet
        """
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.units = units
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.name = getattr(obj, "name", None)
        self.units = getattr(obj, "units", None)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)


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
        self.set_time()

    def git_info(self):
        """Get git info.
        """
        self.repo = Repo(os.path.dirname(measurement.__file__))
        self.git_hash = repo.git.log("-1", "--format=%H")
        self.git_diff = repo.git.diff()

    def set_time(self):
        """Set metadata timestamp.
        """
        self.timestamp = datetime.datetime.now()

    def get_setup(self):
        """Get info about setup.
        """
        pass

    def write(self):
        pass
