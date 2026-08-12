#!/usr/bin/env python

import sys
import enum

from enum import StrEnum

from typing import TypeAlias
from functools import total_ordering
from itertools import chain

Carrier: TypeAlias = int
KnitOut: TypeAlias = list[str]


class CarrierDirection(StrEnum):
    LEFT = "-"
    RIGHT = "+"

    def opposite(self):
        if self == CarrierDirection.LEFT:
            return CarrierDirection.RIGHT
        return CarrierDirection.LEFT


class KnittingMachineBed(StrEnum):
    FRONT = "f"
    BACK = "b"

    def opposite(self):
        if self == KnittingMachineBed.FRONT:
            return KnittingMachineBed.BACK
        return KnittingMachineBed.FRONT


@total_ordering
class Needle:
    def __init__(self, index: int, bed: KnittingMachineBed):
        self.index = index
        self.bed = bed

    def __repr__(self):
        return f"{self.bed}{self.index}"

    def __eq__(self, other):
        return self.index == other.index and self.bed == other.bed

    def __lt__(self, other):
        return (self.index < other.index) or (
            self.index == other.index
            and self.bed != other.bed
            and self.bed == KnittingMachineBed.FRONT
        )

    def __int__(self):
        return self.index

    def opposite_needle(self):
        return Needle(index=self.index, bed=self.bed.opposite)


class NeedleList:
    def __init__(self, needles: list[Needle]):
        self.needles = list(needles)

    def __iter__(self):
        return iter(self.needles)

    def __repr__(self):
        return str([str(i) for i in self.needles])

    def __getitem__(self, index: int | slice) -> Needle:
        if isinstance(index, slice):
            return NeedleList(self.needles[index])

        return self.needles[index]

    def sorted(self, direction: CarrierDirection):
        sorted_needles = sorted(self.needles)

        if direction == CarrierDirection.RIGHT:
            return NeedleList(sorted_needles)

        return NeedleList(sorted_needles[::-1])

    def opposite(self):
        return NeedleList(i.opposite() for i in self.needles)


try:
    filename = sys.argv[1]
except:
    print(f"usage: {sys.argv[0]} file-to-compile")
    exit(1)

knitout_filename = filename + ".k"

carriers = [Carrier(i) for i in range(1, 11)]


def header(
    knit_out_version: str = "knitout-2",
    carriers: list[int] = carriers,
    machine: str = "SWG091N2",
    gauge: int = 13,
    width: int = 450,
    justify_position: str = "Keep",
) -> KnitOut:
    return [
        f";!{knit_out_version}",
        f";;Carriers: {' '.join(str(i) for i in carriers)}",
        f";;Machine: {machine}",
        f";;Gauge: {gauge}",
        f";;Width: {width}",
        f";;Position: {justify_position}",
    ]


def output(knitout_filename: str, lines: KnitOut) -> None:
    with open(knitout_filename, "w") as file:
        file.write("\n".join(lines))
        file.write("\n")


"""

  58 rack
  58 xfer

"""


def inhook(carrier: int) -> KnitOut:
    return KnitOut([f"inhook {carrier}"])


def outhook(carrier: int) -> KnitOut:
    return KnitOut([f"outhook {carrier}"])


def releasehook(carrier: int) -> KnitOut:
    return KnitOut([f"releasehook {carrier}"])


def tuck(direction: CarrierDirection, needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"tuck {direction} {needle} {carrier}"])


def tuck_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    knitout = KnitOut(
        tuck(needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )

    return list(chain.from_iterable(knitout))


def backwards_tuck(
    direction: CarrierDirection, needle: Needle, carrier: int
) -> KnitOut:

    return miss(direction=direction, needle=needle, carrier=carrier) + tuck(
        direction=direction.opposite(), needle=needle, carrier=carrier
    )


def backwards_tuck_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    sorted_needles = needles.sorted(direction)
    knitout = KnitOut(
        backwards_tuck(needle=n, direction=direction, carrier=carrier)
        for n in sorted_needles
    )

    return list(chain.from_iterable(knitout))


def knit(direction: CarrierDirection, needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"knit {direction} {needle} {carrier}"])


def knit_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    knitout = KnitOut(
        knit(needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )

    return list(chain.from_iterable(knitout))


def knit_rows(
    direction: CarrierDirection, needles: NeedleList, carrier: int, height: int
) -> KnitOut:
    knitout = KnitOut()
    for row in range(height):
        knitout += knit_needles(direction=direction, needles=needles, carrier=carrier)
        direction = direction.opposite()

    return knitout


def miss(direction: CarrierDirection, needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"miss {direction} {needle} {carrier}"])


def miss_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    knitout = KnitOut(
        miss(needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )

    return list(chain.from_iterable(knitout))


def backwards_loop_cast_on(
    needles: NeedleList, direction: CarrierDirection, carrier: Carrier
) -> KnitOut:

    return (
        inhook(carrier)
        + tuck(direction=direction, needle=needles[-1], carrier=carrier)
        + backwards_tuck_needles(direction, needles[:-1], carrier)
        + releasehook(carrier)
        + knit_needles(direction=direction.opposite(), needles=needles, carrier=carrier)
    )


def rack(racking: float) -> KnitOut:
    return KnitOut([f"rack {racking}"])


def xfer(
    starting_needle: Needle, ending_needle: Needle, do_rack: bool = True
) -> KnitOut:

    # TODO: make sure the racking for the xfers is correct, even when transfering from back to front. I'm pretty sure it gets weird because you only ever move the front bed? maybe not, but check

    knitout = KnitOut()
    if do_rack:
        gap = int(ending_needle) - int(starting_needle)
        knitout += rack(gap)

    knitout += KnitOut([f"xfer {starting_needle} {ending_needle}"])

    if do_rack:
        knitout += rack(0)

    return knitout


needles = NeedleList(Needle(i, KnittingMachineBed.FRONT) for i in range(390, 420))

""" knitout = (
    header()
    + backwards_loop_cast_on(
        needles=needles, direction=CarrierDirection.LEFT, carrier=Carrier(3)
    )
    + knit_rows(
        direction=CarrierDirection.LEFT, needles=needles, carrier=Carrier(3), height=30
    )
) """

knitout = header() + backwards_loop_cast_on(
    needles=needles, direction=CarrierDirection.LEFT, carrier=Carrier(3)
)

output(knitout_filename, knitout)
