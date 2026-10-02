from .utils import KnitOut, NeedleList, CarrierDirection
from .knitout_opcodes import inhook, outhook
from .loops import Loops


class Carrier:

    def __init__(self, index: int):
        self.index = index
        self.inhooked = False
        self.position = None

    def __int__(self):
        return self.index

    def __repr__(self):
        return f"c{self.index}"

    def __str__(self):
        return f"c{self.index}"

    def inhook(self) -> KnitOut:
        self.inhooked = True
        self.position = 450

        return inhook(self.index)

    def outhook(self) -> KnitOut:
        self.inhooked = False
        self.positon = None

        return outhook(self.index)

    def set_position(self, position: int) -> KnitOut:

        if not self.inhooked:
            raise Exception(f"Tried to move carrier {self.index}, but it is not active")

        self.position = position

    def infer_direction(self, needles: Loops | NeedleList) -> CarrierDirection:

        needle_ints = [int(n) for n in needles]
        left_most = min(needle_ints)
        right_most = max(needle_ints)
        error_margin = len(needle_ints) // 3

        if self.position <= left_most + error_margin:
            return CarrierDirection.RIGHT
        elif self.position >= right_most - error_margin:
            return CarrierDirection.LEFT
        else:
            raise Exception(
                f"Could not infer carrier direction for carrier {self.index} at position {self.position} going from {left_most} to {right_most}"
            )
