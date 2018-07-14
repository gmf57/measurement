import logging
import logging.handlers
from datetime import datetime
import os

log = logging.getLogger(__name__)


def console_log(level=logging.WARNING):
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    return ch


def file_log(filename, level=logging.INFO):
    ch = logging.FileHandler(filename)
    ch.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    return ch


def setup(name=__name__,
          logger=None,
          console=True,
          console_level="DEBUG",
          file_level="INFO",
          filename=None):
    if logger is None:
        logger = logging.getLogger(name)
    if filename is None:
        filename = gen_filename()
    logger.handlers = []
    if console:
        logger.addHandler(console_log())
        logger.info("setting up console logging")
    logger.addHandler(file_log(filename))
    logger.info("set up file logging")
    return logger


def gen_filename(directory="/Users/Matt/emacs/testing/measurement/logs"):
    stamp = datetime.now().strftime("%Y-%m-%d") + ".log"
    return os.path.join(directory, stamp)
