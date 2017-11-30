"""Utilities for printing readable info."""

import sys
from datetime import datetime


class Table:
    """Generate nice tables.

    TODO - variable precision in
    """

    def __init__(self, headers, data, pad=2):
        """
        The formatting in fmt is applied to each row in data. The headers
        are followed by an h-line followed by the formatted data

        Args:
            headers (list): column names
            data (list of list): matrix of table entries. data[0] should
                be the 1st row, even if there is only one row of data
            pad (int): padding on the column width

        Example:
        data = ['test', [0.0, 'A.U.'], [-1, 1.22, 'A.U.'],
                [0.1, 'A.U.'], [0.1, 'A.U.']]
        headers = ['name', 'value', 'min/max', 'step', 'rate']
        # Table expects data to be a list of lists with data[0] a /row/
        t = Table(headers, [data])
        t.buld_table()
        """
        self.headers = headers
        self.data = data
        self.pad = pad
        self.cells = []
        self.widths = []

    def format_cells(self):
        """Iterate over all rows to formatt cells.
        """
        self.cells.append(self.headers)
        for row in self.data:
            self.cells.append(row)

    def get_widths(self):
        """Determine the widths of each column from the size of entries.
        """
        for i, _ in enumerate(self.headers):
            self.widths.append(
                max([len(row[i]) for row in self.cells]) + self.pad)

    def build_row(self, row):
        """Build row of the correct size
        """
        row = "|"
        for cell, width in zip(row, self.widths):
            row += "{:^{w}}|".format(cell, w=width)
        return row

    def build_hline(self):
        """Build hline for table.
        """
        row = "|"
        for width in self.widths:
            row += "{}|".format("-" * width)
        return row

    def build_table(self):
        """Construct the full table."""
        self.format_cells()
        self.get_widths()
        table = ""
        for i, row in enumerate(self.cells):
            table += self.build_row(row) + "\n"
            # Add hline if we are on the header row
            if i is 0:
                table += self.build_hline() + "\n"
        print(table)

    @classmethod
    def prop_formatter(cls, prop, prec=3):
        """Format an instrument property for printing.
        """
        keys = ["name", "value", "maximum", "minimum", "step", "rate"]
        data = []
        for key in keys:
            data.append(prop.fmt_prop(key, prec))
        return cls(keys, [data])

    @classmethod
    def instrument_table(cls, inst, prec=3):
        """
        Generate a table representation of an Instrument
        """
        keys = ["name", "value", "maximum", "minimum", "step", "rate"]
        data = []
        for _, val in inst.__dict__.items():
            if isinstance(val, Property):
                data.append([val.fmt_prop(key, prec) for key in keys])
        return cls(keys, data)


class StatusBar:
    """Print progress of a Measurement."""

    def __init__(self, num):
        self.start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.num = num
        self.done = 0
        # Write the start time
        sys.stdout.write("\nstart - " + self.start + "\n")

    def update(self):
        pass

    def print(self):
        pass
