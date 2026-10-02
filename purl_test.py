#!/usr/bin/env python


import sys
from itertools import chain
from functools import wraps
import inspect
from abc import ABC

from purl.knitout_opcodes import *
from purl.machine_types import *
from purl.loops import *
from purl.carrier import *


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

    def add_knitout_comment(self, comment: str) -> KnitOut:
        """
        formats writes a comment to knitout
        """
        output = KnitOut(";" + comment)
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
        carrier = self.get_carrier(carrier_index)

        if carrier not in self.inhooked_carriers:
            self.activate_carrier(carrier)

        self.active_carrier = carrier

        return carrier

    def get_carrier(self, carrier_index: int) -> Carrier:
        """
        returns the carrier matching the index
        indices must be 1-10 inclusive
        """

        if carrier_index > len(self.all_carriers) or carrier_index <= 0:
            raise Exception(
                f"Tried to activate carrier {carrier_index}, but allowed carrier indices are 1 to 10 inclusive"
            )

        carrier = self.all_carriers[carrier_index - 1]

        return carrier

    def request_needles(
        self, start: int, end: int, bed: KnittingMachineBed
    ) -> NeedleList:
        """
        returns a list of needles going from start up to but not including end on bed
        Precondition: 0 < start <= end <= bed_width
        request_needles(1, 5, KnittingMachineBed.FRONT) = [f1, f2, f3, f4]
        """

        if start < 0 or start > end or end > self.front_needles.len():
            raise ValueError(
                f"ERROR: start and end must be of the form 0 < start <= end <= bed_width not {start = }, {end = }"
            )

        if bed == KnittingMachineBed.FRONT:
            return self.front_needles[start - 1 : end - 1]
        elif bed == KnittingMachineBed.BACK:
            return self.back_needles[start - 1 : end - 1]
        else:
            raise TypeError(
                f"ERROR: requested needles on bed that does't exist. bed must be of type KnittingMachineBed"
            )

    def make_loops(self, needles: NeedleList) -> Loops:
        """
        adds any needles not already in self.all_loops then returns a list of loops on needles
        """

        output_loops = Loops()
        for n in needles:
            a_loop = Loop(n)

            self.all_loops.append(a_loop)
            if n.bed == KnittingMachineBed.FRONT:
                self.front_loops.append(a_loop)
            else:
                self.back_loops.append(a_loop)

            output_loops.append(a_loop)

        return output_loops

    def request_loops(self, needles: NeedleList) -> Loops:
        """
        returns loops of needles
        all input needles must have loops on them
        """

        output_loops = Loops()

        for n in needles:
            a_loop = Loop(n)
            if a_loop not in self.all_loops:
                raise Exception(
                    f"You requested {a_loop} but there is no loop on that needle"
                )
            output_loops.append(a_loop)

        return output_loops

    def twisted_cast_on(
        self,
        needles: NeedleList,
        carrier_index: int = None,
        direction: CarrierDirection = None,
    ) -> Loops:
        """
        casts on needles using the twisted cast on and writes the knitout
        carrier and direction are optional, kind ofs
        """
        output = KnitOut()

        if carrier_index == None:
            carrier = self.active_carrier
            carrier_index = int(carrier)
        elif type(carrier_index) == int:
            carrier = self.get_carrier(carrier_index)
        else:
            raise TypeError(
                f"carrier_index must be int or None not {type(carrier_index)}"
            )

        if direction == None:
            direction = carrier.infer_direction(needles)

        needles = needles.sorted(direction)
        first = needles[0]
        opp_direct = direction.opposite()

        if first.bed == KnittingMachineBed.BACK:
            output += tuck(direction, first.opposite(), carrier_index)
            output += tuck(opp_direct, first, carrier_index)
        else:
            output += tuck(direction, first, carrier_index)

        for n in needles[1:]:
            output += tuck(opp_direct, n, carrier_index)

        carrier.set_position(needles[-1].index)

        self.knitout += output
        loops = self.make_loops(needles)

        return loops

    def knit(
        self,
        loops: Loops,
        carrier_index: int = None,
        direction: CarrierDirection = None,
    ) -> KnitOut:
        """
        writes the knitout for knitting the specified loops
        """

        if carrier_index == None:
            carrier = self.active_carrier
            carrier_index = int(carrier)
        elif type(carrier_index) == int:
            carrier = self.get_carrier(carrier_index)
        else:
            raise TypeError(
                f"carrier_index must be int or None not {type(carrier_index)}"
            )

        if direction == None:
            direction = carrier.infer_direction(loops)

        output = loops.knit(direction, carrier_index)

        self.knitout += output

        carrier.move(direction, loops)

        return output

    def tuck(
        self,
        loops: Loops,
        carrier_index: int = None,
        direction: CarrierDirection = None,
    ) -> KnitOut:
        """
        writes the knitout for tucking the specified loops
        """

        if carrier_index == None:
            carrier = self.active_carrier
            carrier_index = int(carrier)
        elif type(carrier_index) == int:
            carrier = self.get_carrier(carrier_index)
        else:
            raise TypeError(
                f"carrier_index must be int or None not {type(carrier_index)}"
            )

        if direction == None:
            direction = carrier.infer_direction(loops)

        output = loops.tuck(direction, carrier_index)

        self.knitout += output

        carrier.move(direction, loops)

        return output

    def miss(
        self,
        loops: Loops,
        carrier_index: int = None,
        direction: CarrierDirection = None,
    ) -> KnitOut:
        """
        writes the knitout for missing the specified loops
        """

        if carrier_index == None:
            carrier = self.active_carrier
            carrier_index = int(carrier)
        elif type(carrier_index) == int:
            carrier = self.get_carrier(carrier_index)
        else:
            raise TypeError(
                f"carrier_index must be int or None not {type(carrier_index)}"
            )

        if direction == None:
            direction = carrier.infer_direction(loops)

        output = loops.miss(direction, carrier_index)

        self.knitout += output

        carrier.move(direction, loops)

        return output

    def xfer(self, loops: Loops, offset: int = 0) -> KnitOut:
        """
        writes the knitscript for xfering loops with optional offset
        positive offset is right, negative is left
        all loops must be on the same bed
        """

        output = loops.xfer(offset)

        self.knitout += output

        return output

    def split(
        self,
        loops: Loops,
        offset: int = 0,
        carrier_index: int = None,
        direction: CarrierDirection = None,
    ) -> Loops:

        if carrier_index == None:
            carrier = self.active_carrier
            carrier_index = int(carrier)
        elif type(carrier_index) == int:
            carrier = self.get_carrier(carrier_index)
        else:
            raise TypeError(
                f"carrier_index must be int or None not {type(carrier_index)}"
            )

        if direction == None:
            direction = carrier.infer_direction(loops)

        output = loops.split(direction, carrier, offset)
        self.knitout += output
        carrier.move(direction, loops)

        new_loop_locations = NeedleList([l.needle.opposite(offset) for l in loops])
        new_loops = self.make_loops(new_loop_locations)

        return new_loops

    def output(self, lines: KnitOut) -> str:
        program = "\n".join(lines) + "\n"
        with open(self.output_filename, "w") as file:
            file.write(program)
        return program

    def compile(self) -> str:
        """outputs a .k file"""
        self.header()
        self.run()
        return self.output(self.knitout)

    def run() -> KnitOut:
        raise NotImplementedError("unimplemented, inherit and do that in your program")


class Test(Pattern):
    def run(self) -> KnitOut:
        self.set_active_carrier(3)
        my_needles = self.request_needles(390, 420, KnittingMachineBed.FRONT)

        my_loops = self.twisted_cast_on(my_needles)

        self.releasehook()
        for i in range(31):
            self.knit(my_loops)


# you can invoke this and test it via...
# ./purl_test.py new_output.k &&  cmp new_output.k expected_output.k && echo "new_output matches expected output. woo hoo\!"

if __name__ == "__main__":
    test1 = Test("test.k")
    test1.compile()
    print("completed execution!")
