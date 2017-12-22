import time


class Setter(object):
    """Set an instrument setting.

    Makes a callable that utilizes a property's sweeping capabiliy
    """
    __slots__ = ["attr", "val"]

    def __init__(self, attr, val):
        self.attr = attr
        self.val = val

    def __call__(self):
        """Get the attribute and sweep it to val"""
        logging.info(str(self))
        self.attr.set(val)
        logging.info("done")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{}: {} to {:.3f}".format(self.__class__.__name__, self.attr,
                                         self.val)


class Getter(object):
    """Makes a callable that reads a set of parameters from instruments.

    A Getter describes the action of recording a set of parameters. After
    adjusting parameters in a sweep, calls to the Getter will read data
    from the instruments.
    """
    __slots__ = ["attrs"]

    def __init__(self, attrs: List[Callable]):
        """Instantiate a callable that records attrs.

        Args:
            attrs (iterable): Attributes that are recorded on each call
                to the Getter. Each attr in attrs must be callable
        """
        self.attrs = attrs

    def __call__(self):
        return [attr() for attr in self.attrs]

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.attrs)

    def units(self):
        """Read the units for the attrs in the Getter."""
        return [attr.units for attr in self.attrs]


class Wait(object):
    """Callable waiting."""
    __slots__ = ["time"]

    def __init__(self, time):
        self.time = time

    def __call__(self):
        time.sleep(self.time)

    def __str__(self):
        return "{} for {}".format(self.__class__.__name__, self.time)
