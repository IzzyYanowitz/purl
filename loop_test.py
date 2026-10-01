import sys
from itertools import chain
from functools import wraps
from abc import ABC
import inspect

from purl.knitout_opcodes import *
from purl.utils import *


def moves_loop(func):
    """
    decorator for Loop functions that move the loop
    """

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
        """
        returns the knitout for knitting this loop
        """

        return knit(direction=direction, source_needle=self.needle, carrier=carrier)

    def tuck(self, direction: CarrierDirection, carrier: int):
        """
        returns the knitout for tucking this loop
        """

        return tuck(direction=direction, source_needle=self.needle, carrier=carrier)

    def miss(self, direction: CarrierDirection, carrier: int):
        """
        returns the knitout for missing this loop
        """
        return miss(direction=direction, source_needle=self.needle, carrier=carrier)

    @moves_loop
    def split(
        self, direction: CarrierDirection, carrier: int, destination_needle: Needle
    ):
        """
        TODO: Figure out how exactly split creates new loops...
        returns the knitout for splitting this loop
        moves the loop to destination_needle

        """

        return split(
            direction=direction,
            source_needle=self.needle,
            destination_needle=destination_needle,
            carrier=carrier,
        )

    @moves_loop
    def xfer(self, destination_needle: Needle):
        """
        returns the knitout for xfering this loop
        moves the loop to destination_needle
        """
        return xfer(source_needle=self.needle, destination_needle=destination_needle)


def clean_loops(func):
    """removes duplicate loops from a Loops object"""

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
    def knit(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """returns the knitout for knitting a list of loops"""
        output = []
        for l in self.loops:
            output += l.knit(direction, carrier)

        return output

    @clean_loops
    def tuck(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """returns the knitout for tucking a list of loops"""
        output = []
        for l in self.loops:
            output += l.tuck(direction, carrier)

        return output

    @clean_loops
    def miss(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """returns the knitout for missing a list of loops"""
        output = []
        for l in self.loops:
            output += l.miss(direction, carrier)

        return output

    def rack(self, offset: int, source_bed) -> KnitOut:
        """
        calculates the required racking for a given shift then returns the cooresponding knitout
        its slightly weird because only the back bed actually moves
        """
        knitout = []
        if offset:
            sign = 1
            if source_bed == KnittingMachineBed.FRONT:
                sign = -1
            knitout += rack(sign * offset)

        return knitout

    @clean_loops
    def xfer(self, offset: int = 0) -> KnitOut:
        """
        returns the knitout for xfering a list of loops with optional offset
        all loops must be on the same side of the bed
        """
        output = []

    # Before you write split, consider what you were talking about with Yuki


if __name__ == "__main__":
    ls = Loops([Loop(Needle(i, "f")) for i in range(10, 15)] + [Loop(Needle(10, "f"))])
    print(ls.knit(CarrierDirection.LEFT, 4))
    print(ls.tuck(CarrierDirection.LEFT, 4))
    print(ls.miss(CarrierDirection.LEFT, 4))
    print(ls.xfer)
