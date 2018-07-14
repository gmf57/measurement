"""Driver for NI DAQ.

- Get instrument level multi channel tasks to work in conjunction with
simple single channel tasks

- e.g. I need to wrap all of the functionality of nidaqmx
"""
from ..instruments.instrument import Instrument
from ..instruments.param import Param
from pyDAQmx.DAQmxFunctions import *


class DaqInput(Param):
    def __init__(self, name, units, number, min_val=-10, max_val=10):
        super().__init__(name, units)
        self.min_val = min_val
        self.max_val = max_val
        self.address = self.instrument.name + "/ai" + self.number

    def rename(self, name):
        """Rename daq channel."""
        # Change the name attribute on this daq channel
        # setattr on the daq to make ref to the renamed channel
        # delete the ref to the channel on the old name
        pass

    def add_to(self, task):
        """Add this input channel to a task."""
        task.CreateAIVoltageChan(self.address, self.name,
                                 DAQmx_Val_Cfg_Default, self.min_val,
                                 self.max_val, DAQmx_Val_Volts, None)

    def __call__(self):
        return self.getter()

    def getter(self):
        """Perform a single read of the channel."""
        task = Task()
        data = np.zeros((1, ), dtpye=np.float64)
        read = int32()
        self.add_to(task)
        task.StartTask()
        task.ReadAnalogF64(1, 10.0, DAQmx_Val_GroupByChannel, data, 1,
                           byref(read), None)
        task.StopTask()
        return data[0]


class DaqOutput(Param):
    def __init__(self, name, units, number):
        """Create a virtual DAQ channel.

        Args:
            name (str): name for the channel
            units (str): units for the channal (should always be Volts)
            number (int): number of the channel on the physical device
        """
        super().__init__(name, units)
        self.address = self.instrument.name + "/ai" + self.number

    def rename(self, name):
        """Rename daq channel."""
        pass

    def task(self, task, data):
        """Create a Task using this channel."""
        pass

    def set(self, value):
        """Directly write a value to the output channel."""
        task = Task()
        task.CreateAOVoltageChan(self.address, self.name, self.min_val,
                                 self.max_val, DAQmx_Val_Volts, None)
        task.StartTask()
        task.WriteAnalogScalarF64(1, 10.0, value, None)
        task.StopTask()

    def setter(self, value, rate, step):
        pass

    def getter(self):
        pass

    def sweep(self, value, rate, step):
        task = Task()
        pass


class NIDAQ(Instrument):
    def __init__(self, name, device):
        super().__init__(name)

        self.add_param(DaqInput(name="ai0", units="V", validator=None))

        self.add_param(DaqOutput(name="ao0", units="V", validator=None))

    def rename_chan(self, old, new):
        """Rename a daq channel."""
        old_chan = getattr(self, old)
        old_chan.name = new
        setattr(self, new, old_chan)
        setattr(self, old, None)


class AnalogIO():
    """Class that synchronizes read/write on the analog daq channels.
    
        make a different task object for each type of channel used
        then what?
        Create a master clock
        Configure timing on the sub-tasks
        Write "data" to the output channels
        Start the task (acquires data on input channels)
        Read the acquired data
        Stop the task
        Clear the task/release resources
    """

    def __init__(self, *channels):
        self.channels = channels
        self._mtasks = {}

    def configure_timing(self):
        pass

    def write(self, data):
        pass

    def start(self):
        pass

    def read(self):
        pass

    def stop(self):
        pass

    def clear(self):
        pass


class AnalogOutput:
    """
    """

    def __init__(self, channels):
        self.channels = channels
        self.daq = channels[0].instrument

    def configure(self):
        pass

    def write(self, handle):
        pass

    def write_all(self, handle):
        pass


class AnalogInput:
    def __init__(self, channels):
        self.channels = channels
        self.daq = channels[0].instrument

    def configure(self):
        # Create a task handle per channel
        self.task = Task()
        for channel in self.channels:
            channel.add_to(self.task)

    def read(self, handle):
        data = np.zeros((1, ), dtpye=np.float64)
        read = int32()
        task.StartTask()
        task.ReadAnalogF64(1, 10.0, DAQmx_Val_GroupByChannel, data, 1,
                           byref(read), None)
        task.StopTask()
        return data[0]

    def read_all(self):
        return tuple(self.read(handle) for handle in self.handles)


class MultiChannelAnalogInput():
    """Class to create a multi-channel analog input
    
    Usage: AI = MultiChannelInput(physicalChannel)
        physicalChannel: a string or a list of strings
    optional parameter: limit: tuple or list of tuples, the AI limit values
                        reset: Boolean
    Methods:
        read(name), return the value of the input name
        readAll(), return a dictionary name:value
    """

    def __init__(self, physicalChannel, limit=None, reset=False):
        if type(physicalChannel) == type(""):
            self.physicalChannel = [physicalChannel]
        else:
            self.physicalChannel = physicalChannel
        self.numberOfChannel = physicalChannel.__len__()
        if limit is None:
            self.limit = dict([(name, (-10.0, 10.0))
                               for name in self.physicalChannel])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in self.physicalChannel])
        else:
            self.limit = dict([(name, limit[i])
                               for i, name in enumerate(self.physicalChannel)])
        if reset:
            DAQmxResetDevice(physicalChannel[0].split('/')[0])

    def configure(self):
        # Create one task handle per Channel
        taskHandles = dict([(name, TaskHandle(0))
                            for name in self.physicalChannel])
        for name in self.physicalChannel:
            DAQmxCreateTask("", byref(taskHandles[name]))
            DAQmxCreateAIVoltageChan(taskHandles[name], name, "",
                                     DAQmx_Val_RSE, self.limit[name][0],
                                     self.limit[name][1], DAQmx_Val_Volts,
                                     None)
        self.taskHandles = taskHandles

    def readAll(self):
        result = []
        for name in self.physicalChannel:
            result.append((name, self.read(name)))

        return dict([(name, self.read(name)) for name in self.physicalChannel])

    def read(self, name=None):
        if name is None:
            name = self.physicalChannel[0]
        taskHandle = self.taskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((1, ), dtype=numpy.float64)
        #        data = AI_data_type()
        read = int32()
        DAQmxReadAnalogF64(taskHandle, 1, 10.0, DAQmx_Val_GroupByChannel, data,
                           1, byref(read), None)
        DAQmxStopTask(taskHandle)
        return data[0]
