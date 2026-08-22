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

    def opposite(self, offset: int = 0):
        # TODO: surface to user boundary violations (i.e., invalid indexes for that machine)
        return Needle(index=self.index + offset, bed=self.bed.opposite)


class NeedleList:
    def __init__(self, needles: list[Needle]):
        self.needles = list(needles)

    def __iter__(self):
        return iter(self.needles)

    def __repr__(self):
        return str([str(i) for i in self.needles])

    def __getitem__(self, index: int | slice) -> Needle:
        match index:
            case slice():
                return NeedleList(self.needles[index])
            case int():
                return self.needles[index]
            case _:
                raise ValueError(f"expected slice | int, got {type(index)}")

    def assert_same_bed(self) -> bool:
        if len({needle.bed for needle in self.needles}) == 1:
            return True
        raise ValueError(f"expected all needles to belong to same bed")

    def sorted(self, direction: CarrierDirection):
        sorted_needles = sorted(self.needles)

        if direction == CarrierDirection.RIGHT:
            return NeedleList(sorted_needles)

        return NeedleList(sorted_needles[::-1])

    def opposite(self, offset: int = 0):
        """
        offset: int - how many needles over (negative shifts left, positive shifts right), defaults to 0
        """

        return NeedleList(i.opposite(offset) for i in self.needles)


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


def tuck(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"tuck {direction} {source_needle} {carrier}"])


def tuck_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    knitout = KnitOut(
        tuck(source_needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )

    return list(chain.from_iterable(knitout))


def backwards_tuck(
    direction: CarrierDirection, source_needle: Needle, carrier: int
) -> KnitOut:

    return miss(
        direction=direction, source_needle=source_needle, carrier=carrier
    ) + tuck(
        direction=direction.opposite(), source_needle=source_needle, carrier=carrier
    )


def backwards_tuck_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    sorted_needles = needles.sorted(direction)
    knitout = KnitOut(
        backwards_tuck(source_needle=n, direction=direction, carrier=carrier)
        for n in sorted_needles
    )

    return list(chain.from_iterable(knitout))


def knit(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"knit {direction} {source_needle} {carrier}"])


def knit_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    knitout = KnitOut(
        knit(source_needle=n, direction=direction, carrier=carrier)
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


def miss(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"miss {direction} {source_needle} {carrier}"])


def miss_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    knitout = KnitOut(
        miss(source_needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )

    return list(chain.from_iterable(knitout))


def backwards_loop_cast_on(
    needles: NeedleList, direction: CarrierDirection, carrier: Carrier
) -> KnitOut:

    return (
        inhook(carrier)
        + tuck(direction=direction, source_needle=needles[-1], carrier=carrier)
        + backwards_tuck_needles(direction, needles[:-1], carrier)
        + releasehook(carrier)
        + knit_needles(direction=direction.opposite(), needles=needles, carrier=carrier)
    )


def rack(offset: float) -> KnitOut:
    return KnitOut([f"rack {offset}"])


def xfer(source_needle: Needle, destination_needle: Needle) -> KnitOut:
    return KnitOut([f"xfer {source_needle} {destination_needle}"])


def xfer_needles(starting_needles: NeedleList, offset: int) -> KnitOut:
    knitout = KnitOut()
    starting_needles.assert_same_bed()

    sign = 1

    return knitout


needles = NeedleList(Needle(i, KnittingMachineBed.FRONT) for i in range(390, 420))

knitout = (
    header()
    + backwards_loop_cast_on(
        needles=needles, direction=CarrierDirection.LEFT, carrier=Carrier(3)
    )
    + knit_rows(
        direction=CarrierDirection.LEFT, needles=needles, carrier=Carrier(3), height=30
    )
)

output(knitout_filename, knitout)
