from .utils import KnitOut
from .knitout_opcodes import inhook, outhook


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
