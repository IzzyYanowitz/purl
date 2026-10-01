import sys
from itertools import chain
from functools import wraps
from abc import ABC
import inspect

from purl.knitout_opcodes import *
from purl.utils import *


def moves_loop(func):
    signature = inspect.signature(func)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        ko = func(self, *args, **kwargs)

        # Figure out which argument was destination_needle
        bound = signature.bind(self, *args, **kwargs)
        destination_needle = bound.arguments["destination_needle"]

        self.needle = destination_needle
        return ko

    return wrapper


class Loop:
    def __init__(self, needle: Needle):
        self.needle = needle

    def __repr__(self):
        return f"Loop({str(self.needle)})"

    def __str__(self):
        return f"Loop({str(self.needle)})"

    def knit(self, direction: CarrierDirection, carrier: int):
        return knit(direction=direction, source_needle=self.needle, carrier=carrier)

    def tuck(self, direction: CarrierDirection, carrier: int):
        return tuck(direction=direction, source_needle=self.needle, carrier=carrier)

    def miss(self, direction: CarrierDirection, carrier: int):
        return miss(direction=direction, source_needle=self.needle, carrier=carrier)

    @moves_loop
    def split(
        self, direction: CarrierDirection, carrier: int, destination_needle: Needle
    ):
        """by convention, split moves the old loop and creates a new one in its place"""
        return split(
            direction=direction,
            source_needle=self.needle,
            destination_needle=destination_needle,
            carrier=carrier,
        )

    @moves_loop
    def xfer(self, destination_needle: Needle):
        return xfer(source_needle=self.needle, destination_needle=destination_needle)


def clean_loops(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        seen_needles = set()
        safe_loops = []
        for i, l in enumerate(self.loops):
            if l.needle not in seen_needles:
                safe_loops.append(l)
                seen_needles.add(l.needle)

        self.loops = safe_loops

        return func(self, *args, **kwargs)

    return wrapper


class Loops:

    def __init__(self, loops: list[Loop] = []):
        self.loops = loops

    def __repr__(self):
        return "[%s]" % ", ".join([str(l) for l in self.loops])

    def __str__(self):
        return "[%s]" % ", ".join([str(l) for l in self.loops])

    @clean_loops
    def knit(self, direction: CarrierDirection, carrier: int):
        output = []
        for l in self.loops:
            output += l.knit(direction, carrier)

        return output

    @clean_loops
    def tuck(self, direction: CarrierDirection, carrier: int):
        output = []
        for l in self.loops:
            output += l.tuck(direction, carrier)

        return output

    @clean_loops
    def miss(self, direction: CarrierDirection, carrier: int):
        output = []
        for l in self.loops:
            output += l.miss(direction, carrier)

        return output

    # OK! you're doing great the next step is writing xfer which isn't as simple as the other ones
    # you're at the abstraction level now where you need to figure out how the racking works
    # if I remember correctly, you've already solved this! good job! Go check out the purl_test.py file where you wrote xfer needles way back when
    # I have to go to sleep now because all these characters are just shapes now
    # Good luck...


if __name__ == "__main__":
    ls = Loops([Loop(Needle(i, "f")) for i in range(10, 15)] + [Loop(Needle(10, "f"))])
    print(ls.knit(CarrierDirection.LEFT, 4))
    print(ls.tuck(CarrierDirection.LEFT, 4))
    print(ls.miss(CarrierDirection.LEFT, 4))
    print(ls.xfer)
