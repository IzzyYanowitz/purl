from enum import StrEnum
from typing import TypeAlias
from functools import total_ordering

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

    def assert_has_needles(self) -> bool:
        if self.needles:
            return True

        raise ValueError(
            f"asked to operate on an empty list of needles, you probably don't want that"
        )

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
