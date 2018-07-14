"""Write down the interface that I want the measrurement code to have.
"""

# Set an instrument param by calling it
param(val)

# Sweep a param
[param(val) for val in vals]
# or
for val in vals:
    time.sleep(pause)
    param(val)

# Get the value of an instrument param
param()

# Sweep a param while recording values
sweep = Sweep(sweep_param, values, measurement, rate)

# Here measurement is a callable that I do at every point in the sweep
# It should return the data that I want to collect
data = measurement()


# But it could do other things as well...
def measure():
    time.sleep(pause)  # Some other thing that measure does
    print(param1())  # Some other thing that measure does
    return param2  # this callable returns data


# So maybe I need a class that standardizes the creation of these callables
# That are executed @ each point in parameter space

sweep = Sweep(sweep_param, np.linspace(0, 1, 10), measure, 0.1)
"""
Do you make nested measurements by putting sweeps inside sweeps?
Or do you use a list of sweeps to make the measurement. Nesting
the sweeps seems cleaneset because the you don't have to "re-organize"
the measurement when you combine sweeps

So measurement is the thing that combines sweeping, a plotting interface
and data i/o.

Perhaps it's better to use a function to make these classes? I think so

A nice use of meta classes could be instrument drivers. They could detect
what is going on @ class definition and automatically generate some methods
"""
task = Measure(wait(1.), [daq.ai0, daq.ai1, m.B], s.reset)
task1 = Measure(None, [l.chan6.T], None)
s1 = Sweep(param, vals, task, rate)
s2 = Sweep(param2, vals, [task1, s1], rate)
s2.run()
""" 
DaqSweeps
Sweep channels over the values and record other channels
This lets you take linecuts in arbitrary directions
A DAQ sweep must define both the sweep values and the measured values to
get timing right. 

In this way a daq sweep is fundamentally different than the more generic sweeps
since during the adjustment of the daq outputs, only daq inputs can be recorded

If the daq outputs are set during a generic Sweep, then arbitrary prameters
can be read during the sweep.

I might need a way of nesting DaqSweeps
"""
daq_sweep = DaqSweep([ao0, ao1, ao2], [vals0, vals1, vals2], [ai0, ai1, ai2],
                     rate)

# Define the lines I want to scan - the rate and the things I want to do
# at each line 

scan = Scan(lines, rate, measure)
line = Line(start, end, plane, num)


class Scan(Measurement):
    """Constructs a set of DAQ sweeps that constitutes the scan.

    I want a "default" scan.

    Args:
        lines - a set of line cuts to scan over.
        rate - the scan rate in V/s.
        measure - the input channels that are recorded while scanning.
        before - called before each line is taken.    
        after - called after each line is taken.
    """

    def __init__(lines, rate, measure, before, after):
        # Must make the right set of daq sweeps
        self.lines = lines
        self.rate = rate

    @classmethod
    def scan_grid(cls, center, span, rate, measure, before, after):
        """Make a scan over a grid."""
        pass

    @classmethod
    def raster_scan(cls, center, span, rate, measure, before, after):
        """Raster scan a grid."""
        pass

    @classmethod
    def scan_angle(cls, line1, line2, rate, measure, before, after):
        """Scan parallel to line1 starting @ each point in line2"""
        pass

    @classmethod
    def search(cls, lines, rate, measure, before, after):
        """Take lines to accelerate searching for features."""
        pass

    @classmethod
    def default_scan(cls, center, span, plane, rate):
        """Set some nice defaults for before after and measure."""
        pass


"""
If I'm doing a lot of a particular type of scan (typical during the 
heart of measuring a particular sample) then I can define class factories
that construct the appropriate scan objects.
"""


def scan_factory(plane, offset, center, span, rate):
    return Scan(*args, **kwargs)


"""
Call Lists - I want a nice way of assembling sets of tasks that are run
during measurements.
"""


class CallList:
    """An interfcace for creating callback functions that run in measurements.
    """

    def __init__(self):
        pass


"""
Receiving data from instruments

I want a way to record parameters @ different frequencies - for example,
record the temperature of the fridge between each scan but not @ every line.

Or, report overloading on a lockin after a gate sweep - I don't think this
has to go in the data file - it can be written to logs and reported @ the
console.

So I really just need to record extra parameters @ the start/end of measurements
which should be easy (start and stop snapshots of the "setup" object)

This means the size/shape of the sweep and measure objects uniquely determine
the size/shape of the data set. This also means that only the inner most
loop of the sweep should have a measure object
"""
# Inner loop
s1 = Sweep(param1, vals1, [wait(1.), measure, s.reset], 0.1)
# Outer loop
s2 = Sweep(param2, vals2, [wait(1.), s1, wait(1.)], 0.1)

# Another possibility - do 2 different (un-nested) sweeps @ different points
# Is this worth considering? I could imagining sweeping gate bias and field
# but not wanting to map the full 2D gate/bias space. Each of s0 and s1
# would have a measure
s3 = Sweep(param3, vals3, [wait(1.), s0, s1, wait(1.)], 0.1)
