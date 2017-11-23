"""
Define classes that are designed to "store data"

subclass np.array with DataSet that contains info about units. Data can
can be collected in np.arrays in cast to DataSet with the np.array view 
feature. DataSets can also be directly instantiated during collection.
"""
import git
from datetime import datetime
import numpy as np

class DataSet(object):
    """A collection of DataArray

    Contains a DataArray for each recorded parameter in a measurement.
    """
    def __init__(self, filename, timestamp):
        self.filename = filename
        self.timestamp = timestamp

    def __str__(self):
        return "{} {}".format(self.__class__.__name__,
                              self.name)
    
    def add(self, data_set):
        """Add a data_set to the DataArray
        """
        setattr(self, data_set.name, data_set)

    def save(self, formatter):
        """Use the formatter to write a file
        """
        pass

    @classmethod
    def load(cls, filename):
        """
        """
        pass
    
class DataArray(np.ndarray):
    """Store data from a single measured parameter. 

    Behaves like an ndarray with a name and units parameter.    
    """
    def __new__(cls, input_array, name = None, units = None):
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
        return "{}: {}".format(self.__class__.__name__,
                               self.name)
    

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
        """
        """
        pass

    def git_info(self):
        """Get git info
        """
        pass

    def set_time(self):
        """Set metadata timestamp
        """
        pass

    def get_setup(self):
        """Get info about setup
        """
        pass

            
            
