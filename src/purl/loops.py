import sys
from itertools import chain
from functools import wraps, total_ordering
from abc import ABC
import inspect

from .machine_types import (
    Needle,
    CarrierDirection,
    KnitOut,
    KnittingMachineBed,
    NeedleList,
)
from .knitout_opcodes import knit, tuck, miss, split, xfer, rack


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


@total_ordering
class Loop:
    def __init__(self, needle: Needle):
        self.needle = needle

    def __repr__(self):
        return f"Loop({str(self.needle)})"

    def __str__(self):
        return f"Loop({str(self.needle)})"

    def __int__(self):
        return int(self.needle)

    def __eq__(self, other):
        return self.needle == other.needle

    def __lt__(self, other):
        return self.needle < other.needle

    def opposite(self, offset: int) -> Needle:
        """
        returns the needle opposite this loop with optional offset
        """

        return self.needle.opposite(offset)

    def knit(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """
        returns the knitout for knitting this loop
        """

        return knit(direction=direction, source_needle=self.needle, carrier=carrier)

    def tuck(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """
        returns the knitout for tucking this loop
        """

        return tuck(direction=direction, source_needle=self.needle, carrier=carrier)

    def miss(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """
        returns the knitout for missing this loop
        """
        return miss(direction=direction, source_needle=self.needle, carrier=carrier)

    def split(
        self, direction: CarrierDirection, carrier: int, destination_needle: Needle
    ) -> KnitOut:
        """
        returns the knitout for splitting this loop
        DOES NOT move the loop to destination_needle
        """

        return split(
            direction=direction,
            source_needle=self.needle,
            destination_needle=destination_needle,
            carrier=carrier,
        )

    @moves_loop
    def xfer(self, destination_needle: Needle) -> KnitOut:
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

        output = func(self, *args, **kwargs)

        seen_needles = set()
        safe_loops = []
        for i, l in enumerate(self.loops):
            if l.needle not in seen_needles:
                safe_loops.append(l)
                seen_needles.add(l.needle)

        self.loops = safe_loops

        return output

    return wrapper


def needs_loops(func):
    """checks if Loops object has loops
    throws an error if not"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):

        self.assert_has_loops()
        return func(self, *args, **kwargs)

    return wrapper


class Loops:

    def __init__(self, loops: list[Loop] = []):
        self.loops = loops

    def __repr__(self):
        return "[%s]" % ", ".join([str(l) for l in self.loops])

    def __str__(self):
        return "[%s]" % ", ".join([str(l) for l in self.loops])

    def __getitem__(self, index: slice | int):
        match index:
            case slice():
                return Loops(self.loops[index])
            case int():
                return self.loops[index]
            case _:
                raise ValueError(f"expected slice | int, got {type(index)}")

    def __iter__(self):
        return iter(self.loops)

    def __contains__(self, l: Loop) -> bool:
        for loop in self.loops:
            if l.needle == loop.needle:
                return True
        return False

    @clean_loops
    def sorted(self, direction: CarrierDirection):
        ls = sorted(self.loops)
        if direction == CarrierDirection.RIGHT:
            return ls
        return ls[::-1]

    @clean_loops
    def len(self):
        return len(self.loops)

    @clean_loops
    def append(self, loop: Loop) -> None:
        self.loops.append(loop)

    @clean_loops
    def join(self, loops) -> None:
        for l in loops:
            self.loops.append(l)

    def assert_same_bed(self) -> bool:
        if len({loop.needle.bed for loop in self.loops}) == 1:
            return True
        raise ValueError(f"expected all needles to belong to same bed")

    def assert_has_loops(self) -> bool:
        if len(self.loops) > 0:
            return True

        raise ValueError(
            f"asked to operate on an empty list of needles, you probably don't want that"
        )

    @clean_loops
    @needs_loops
    def knit(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """returns the knitout for knitting a list of loops"""
        output = []
        for l in self.sorted(direction):
            output += l.knit(direction, carrier)

        return output

    @clean_loops
    @needs_loops
    def tuck(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """returns the knitout for tucking a list of loops"""
        output = []
        for l in self.sorted(direction):
            output += l.tuck(direction, carrier)

        return output

    @clean_loops
    @needs_loops
    def miss(self, direction: CarrierDirection, carrier: int) -> KnitOut:
        """returns the knitout for missing a list of loops"""
        output = []
        for l in self.sorted(direction):
            output += l.miss(direction, carrier)

        return output

    def rack(self, offset: int, source_bed: KnittingMachineBed) -> KnitOut:
        """
        calculates the required racking for a given shift then returns the cooresponding knitout
        its slightly weird because only the back bed actually moves
        """
        sign = 1
        if source_bed == KnittingMachineBed.FRONT:
            sign = -1

        return rack(sign * offset)

    @clean_loops
    @needs_loops
    def opposite(self, offset: int = 0) -> NeedleList:
        """
        returns the cooresponding needles on the opposite bed with an optional offset
        negative is left, positive is right.
        """

        opposite_needles = []

        for l in self.loops:
            opposite_needles.append(l.opposite(offset))

        return opposite_needles

    @clean_loops
    @needs_loops
    def xfer(self, offset: int = 0) -> KnitOut:
        """
        returns the knitout for xfering a list of loops with optional offset
        all loops must be on the same  bed
        """

        self.assert_same_bed()
        source_bed = self.loops[0].needle.bed

        output = []

        if offset:
            output += self.rack(offset, source_bed)

        destination_needles = self.opposite(offset)

        for i, l in enumerate(self.loops):
            output += l.xfer(destination_needles[i])

        if offset:
            output += self.rack(0, source_bed)

        return output

    @clean_loops
    @needs_loops
    def split(
        self, direction: CarrierDirection, carrier: int, offset: int = 0
    ) -> KnitOut:
        """
        returns the knitout for splitting a list of loops with optional offset
        by convention, split doesn't move the loops, but creates new ones that can be requested from the purl program
        all loops must be on the same bed
        """
        self.assert_same_bed()
        source_bed = self.loops[0].needle.bed

        output = []

        if offset:
            output += self.rack(offset, source_bed)

        destination_needles = self.opposite(offset)

        for i, l in enumerate(self.sorted(direction)):
            output += l.split(direction, carrier, destination_needles[i])

        if offset:
            output += self.rack(0, source_bed)

        return output


if __name__ == "__main__":
    ls = Loops(
        [Loop(Needle(i, KnittingMachineBed.FRONT)) for i in range(10, 15)]
        + [Loop(Needle(10, KnittingMachineBed.FRONT))]
    )
    print(ls.knit(CarrierDirection.LEFT, 4))
    print(ls.tuck(CarrierDirection.LEFT, 4))
    print(ls.miss(CarrierDirection.LEFT, 4))
    print(ls.xfer(3))

    print(ls.split(CarrierDirection.RIGHT, 4, 1))

    # l1 = Loop(Needle(20, KnittingMachineBed.FRONT))
    # l2 = Needle(22, KnittingMachineBed.BACK)
