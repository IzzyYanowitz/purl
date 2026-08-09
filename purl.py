#!/usr/bin/env python

import sys
import enum

from enum import StrEnum

from typing import TypeAlias
from functools import total_ordering

Carrier: TypeAlias = int
KnitOut: TypeAlias = list[str]


class CarrierDirection(StrEnum):
    LEFT = "-"
    RIGHT = "+"


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

    def opposite_needle(self):
        return Needle(index=self.index, bed=self.bed.opposite)


class NeedleList:
    def __init__(self, needles: list[Needle]):
        self.needles = needles

    def __iter__(self):
        return iter(self.needles)

    def sorted(self, direction: CarrierDirection):
        sorted_needles = sorted(self.needles)

        if direction == CarrierDirection.RIGHT:
            return sorted_needles

        return sorted_needles[::-1]

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


def cast_on(needles: list[Needle], direction: CarrierDirection, carrier: Carrier):
    pass


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
    return KnitOut(
        tuck(needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )


def knit(direction: CarrierDirection, needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"knit {direction} {needle} {carrier}"])


def knit_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    return KnitOut(
        knit(needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )


def miss(direction: CarrierDirection, needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"miss {direction} {needle} {carrier}"])


def miss_needles(
    direction: CarrierDirection, needles: NeedleList, carrier: int
) -> KnitOut:
    return KnitOut(
        miss(needle=n, direction=direction, carrier=carrier)
        for n in needles.sorted(direction)
    )


knitout = header()

output(knitout_filename, knitout)
