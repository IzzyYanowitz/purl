#!/usr/bin/env python


import sys
from itertools import chain
from functools import wraps
import inspect
from abc import ABC

from purl.knitout_opcodes import *
from purl.utils import *
from purl.loops import *
from purl.carrier import *

# IZZY TODO: move carriers and header into AbstractPurlProgram


"""

  58 rack
  58 xfer

"""


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


def xfer_needles(source_needles: NeedleList, offset: int) -> KnitOut:
    knitout = KnitOut()

    source_needles.assert_has_needles()
    source_needles.assert_same_bed()

    source_bed = source_needles[0].bed

    # you can only shift the back bed, so to make it easier on the user, we
    # calculate which direction based on source bed
    if offset:
        sign = 1
        if source_bed == KnittingMachineBed.FRONT:
            sign = -1
        knitout += rack(sign * offset)

    for n in source_needles:
        knitout += xfer(n, n.opposite(offset))

    if offset:
        knitout += rack(0)

    return knitout


def chain_bind_off(
    needles: NeedleList, direction: CarrierDirection, carrier: Carrier
) -> KnitOut:
    knitout = KnitOut()
    sorted_needles = needles.sorted(direction)

    return knitout


class Pattern(ABC):
    def __init__(
        self,
        output_filename: str,
        knitout_version: str = "knitout-2",
        machine_name: str = "SWG091N2",
        gauge: int = 13,
        width: int = 450,
        justify_position: str = "Keep",
    ):
        # program settings
        self.output_filename = output_filename

        # machine settings
        self.carriers = [Carrier(i) for i in range(1, 11)]
        self.knitout_version = knitout_version
        self.machine_name = machine_name
        self.gauge = gauge
        self.width = width
        self.justify_position = justify_position

        # needles
        self.front_needles = NeedleList(
            [Needle(i, KnittingMachineBed.FRONT) for i in range(1, width + 1)]
        )
        self.back_needles = NeedleList(
            [Needle(i, KnittingMachineBed.BACK) for i in range(1, width + 1)]
        )
        self.all_needles = self.front_needles + self.back_needles

        # loops
        self.all_loops = Loops([])
        self.front_loops = Loops([])
        self.back_loops = Loops([])

        # carriers
        self.yarn_inserting_hook = 0
        self.inhooked_carriers = set()
        self.active_carrier = 0
        self.all_carriers = [Carrier(i) for i in range(1, 11)]

        # knitout
        self.knitout = KnitOut([])

    def header(self) -> KnitOut:
        """writes the knitout for the header"""
        output = [
            f";!{self.knitout_version}",
            f";;Carriers: {' '.join(str(i) for i in self.carriers)}",
            f";;Machine: {self.machine_name}",
            f";;Gauge: {self.gauge}",
            f";;Width: {self.width}",
            f";;Position: {self.justify_position}",
        ]
        self.knitout += output
        return output

    def activate_carrier(self, carrier: Carrier) -> KnitOut:
        """
        inhooks carrier and writes the KnitOut
        be sure to releasehook before you try to activate another carrier
        activate_carrier(already_active_carrier) is a safe no-op
        """

        if carrier in self.inhooked_carriers:
            return

        if self.yarn_inserting_hook:
            raise Exception(
                f"yarn inserting hook is full but you tried to inhook carrier {carrier}. Did you forget to releasehook?"
            )

        self.inhooked_carriers.add(carrier)
        self.yarn_inserting_hook = carrier.index
        output = carrier.inhook()
        self.knitout += output
        return output

    def releasehook(self) -> KnitOut:
        """
        writes the knitout to release the yarn inserting hook
        if yarn inserting hook is empty, this is a safe no-op
        """

        if not self.yarn_inserting_hook:
            return

        output = releasehook(self.yarn_inserting_hook)
        self.yarn_inserting_hook = 0

        self.knitout += output
        return output

    def cut(self, carrier: int | Carrier) -> KnitOut:
        """synonym for outhook"""
        return self.outhook(carrier)

    def outhook(self, carrier: int | Carrier) -> KnitOut:
        """
        outhooks the current carrier
        """
        if type(carrier) == int:
            carrier = self.all_carriers[carrier - 1]

        if carrier not in self.inhooked_carriers:
            print(
                f"WARNING: You outhooked a carrier ({carrier}) that you never inhooked!"
            )

        if self.yarn_inserting_hook:
            raise Exception(
                f"You tried to outhook carrier {carrier} but the yarn inserting hook is already full. Did you forget to releasehook?"
            )

        if self.active_carrier == carrier:
            self.active_carrier = 0

        output = carrier.outhook()
        self.inhooked_carriers.remove(carrier)

        self.knitout += output

        return output

    def set_active_carrier(self, carrier_index: int) -> Carrier:
        """
        TODO: figure out if this should take an int or carrier and if it should return an int or a carrier
        sets the active carrier and inhooks if neccesary
        carriers on our machine can be 1 to 10
        """
        if carrier_index > len(self.all_carriers) or carrier_index <= 0:
            raise Exception(
                f"Tried to activate carrier {carrier_index}, but allowed carrier indices are 1 to 10 inclusive"
            )

        carrier = self.all_carriers[carrier_index - 1]

        if carrier not in self.inhooked_carriers:
            self.activate_carrier(carrier)

        self.active_carrier = carrier

        return carrier

    def output(self, lines: KnitOut) -> str:
        program = "\n".join(lines) + "\n"
        with open(self.output_filename, "w") as file:
            file.write(program)
        return program

    def compile(self) -> str:
        """outputs a .k file"""
        self.run()
        return self.output(self.knitout)

    def run() -> KnitOut:
        raise NotImplementedError("unimplemented, inherit and do that in your program")


class StockinetteSquare(Pattern):
    def run(self) -> KnitOut:
        needles = self.cast_on_needles
        knitout = (
            self.header()
            + backwards_loop_cast_on(
                needles=needles,
                direction=CarrierDirection.LEFT,
                carrier=Carrier(3),
            )
            + knit_rows(
                direction=CarrierDirection.LEFT,
                needles=needles,
                carrier=Carrier(3),
                height=30,
            )
            + chain_bind_off(
                needles=needles, direction=CarrierDirection.LEFT, carrier=Carrier(3)
            )
        )

        return knitout


class Test(Pattern):
    def run(self) -> KnitOut:
        print("hello world")


"""
taking a step back, this is roughly the behaviour i want to implement

pattern.set_active_carrier(5)
my_loops = pattern.cast_on(pattern.Front_Needles[25 : 50])
# print(my_loops) -> [Loop(f25), Loop(f26), Loop(f27)..., Loop(f49)]
for i in range(20):
    pattern.knit(my_loops)

pattern.bind_off(my_loops)

# print(my_loops) -> [Loop(f25)]
"""


# you can invoke this and test it via...
# ./purl_test.py new_output.k &&  cmp new_output.k expected_output.k && echo "new_output matches expected output. woo hoo\!"
""" 
try:
    filename = sys.argv[1]
except:
    print(f"usage: {sys.argv[0]} output_filename")
    exit(1)

ss = StockinetteSquare(output_filename=filename, starting_needle=390, ending_needle=420)
ss.compile()
 """
if __name__ == "__main__":
    test1 = Test("foo")
    test1.run()
