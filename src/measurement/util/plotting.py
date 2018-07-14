"""
Plot measurements.

Classes that generate plot layouts from data

Live plotting over TCP.
"""

from matplotlib import pyplot as plt
import socket


def layout_2D(timestamp, data_name, x_name=None, y_name=None):
    pass


def layout_1D(timestamp, x_name=None, y_name=None):
    pass


class Plotter:
    """Quickly lay out plots of many parameters.
    
    Make 1 plot per channel that is in the socket
    """

    def __init__(self, socket):
        pass

    def read(self):
        pass

    def close(self):
        pass


class DataServer:
    """Spit data @ a socket for plotting.

    Specify the socket to spit data at and the info that will be given
    """

    def __init__(self, sock, channels):
        self.sock = sock
        self.channels = channels

    def close(self):
        pass

    def start(self):
        pass


class TCPlotter(Plotter):
    """Plot data arriving over TCP."""

    def __init__(self, sock):
        self.sock = sock


class FilePlotter(Plotter):
    """Plot data written to a file."""

    def __init__(self, channels, fname):
        self.channels = channels
        self.fname = fname
