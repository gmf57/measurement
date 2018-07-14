"""
Utilities for operating on timestamped files.
"""
from datetime import datetime
import os


def get_dated_folder(directory, fmt="YYYY-mm-dd"):
    """Create a dated folder in the provided directory."""
    if os.path.isdir(directory):
        path = os.path.join(directory, datetime.now().strftime(fmt))
        if os.path.isdir(path):
            return path
        else:
            os.mkdir(path)
            return path
    else:
        raise OSError("{} is not a valid directory.".format(directory))


def get_current_experiment():
    """Find the folder of the current experiment."""
    pass


def gen_measurement_filename(directory, description, version=0):
    """Generate a unique filename for a measurement."""
    filename = datetime.now().strftime("YYYY-mm-dd_HHMMSS") + description
    if version is not 0:
        filename = filename + "_{}".format(version)
    path = os.path.join(directory, filename)
    if os.path.exists(path):
        return gen_measurement_filename(
            directory, description, version=version + 1)
    else:
        return path
