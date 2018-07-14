from measurement.util import logging
from measurement.util import files
import configparser
import os

# Read the local configuration file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

# Set up logging
folder = files.get_dated_folder(config['DIRECTORIES']['logs'], fmt="YYYY")
filename = logging.gen_filename(folder)
logging.setup(filename=filename)

# Name of current series of experiments
experiment = None
