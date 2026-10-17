#!/usr/bin/env python


import sys
from pathlib import Path
from os import path, makedirs

from itertools import chain
from functools import wraps
import inspect
from abc import ABC

from .knitout_opcodes import *
from .machine_types import *
from .loops import *
from .carrier import *

from knitout_compilers.compile_knitout import knitout_to_dat


class Pattern(ABC):

    def __init__(
        self,
        filename: str,
        knitout_version: str = "knitout-2",
        machine_name: str = "SWG091N2",
        gauge: int = 13,
        bed_width: int = 450,
        justify_position: str = "Keep",
        copy_to_drive: bool = False,
    ):
        # program settings
        self.filename = filename
        self.generate_output_files(copy_to_drive)

        # machine settings
        self.carriers = [Carrier(i) for i in range(1, 11)]
        self.knitout_version = knitout_version
        self.machine_name = machine_name
        self.gauge = gauge
        self.bed_width = bed_width
        self.justify_position = justify_position

        # needles
        self.front_needles = NeedleList(
            [Needle(i, KnittingMachineBed.FRONT) for i in range(1, bed_width + 1)]
        )
        self.back_needles = NeedleList(
            [Needle(i, KnittingMachineBed.BACK) for i in range(1, bed_width + 1)]
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

    def generate_output_files(self, copy_to_drive: bool = False):

        dir_path = str(Path(sys.modules["__main__"].__file__).resolve().parent)
        if copy_to_drive:
            dir_path = "/Volumes/NO NAME/_Izzy Yanowitz/" + str(
                path.basename(Path(sys.modules["__main__"].__file__).resolve().parent)
            )

        self.knitout_file_name = dir_path + "/" + self.filename + ".k"
        self.dat_file_name = dir_path + "/" + self.filename + ".dat"

        if not copy_to_drive:
            return

        if path.isdir("/Volumes/NO NAME/_Izzy Yanowitz"):
            if not path.isdir(dir_path):
                print(f"Making dirs to {dir_path}")
                makedirs(dir_path)
        else:
            raise Exception("No drive connected")

    def header(self) -> KnitOut:
        """writes the knitout for the header"""
        output = [
            f";!{self.knitout_version}",
            f";;Carriers: {' '.join(str(i) for i in self.carriers)}",
            f";;Machine: {self.machine_name}",
            f";;Gauge: {self.gauge}",
            f";;Width: {self.bed_width}",
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

    def cut(self, carrier: int | Carrier | None = None) -> KnitOut:
        """synonym for outhook"""
        return self.outhook(carrier)

    def outhook(self, carrier: int | Carrier | None = None) -> KnitOut:
        """
        outhooks the current carrier
        """
        carrier = self.infer_carrier(carrier)

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
        self, start: int, width: int, bed: KnittingMachineBed
    ) -> NeedleList:
        """
        returns a list of needles going from start up to but not including end on bed
        Precondition: 0 < start <= end <= bed_width
        request_needles(1, 5, KnittingMachineBed.FRONT) = [f1, f2, f3, f4]
        """
        end = start + width
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
        ns = list(self.all_loops.needles())

        for n in needles:
            try:
                i = ns.index(n)
            except:
                raise Exception(
                    f"You requested Loop({n}) but there is no loop on that needle"
                )
            output_loops.append(self.all_loops[i])

        return output_loops

    def is_real_loops(self, loops: Loops) -> bool:
        """returns true if the inputed loops are all in self.all_loops"""
        loops.clean()

        for l in loops:
            if l not in self.all_loops:
                return False
        return True

    def clean_input(func):
        """decorator to clean the input of a function that takes loops, a direction, and a carrier"""

        @wraps(func)
        def wrapper(
            self,
            loops: NeedleList | Loops,
            carrier: int | Carrier | None = None,
            direction: CarrierDirection | None = None,
            *args,
            **kwargs,
        ):
            if type(loops) == Loops:
                if not self.is_real_loops(loops):
                    raise Exception(
                        f"You tried to {func.__name__} {loops}, but some of those loops aren't real"
                    )

            self.clean()
            direction, carrier = self.infer_direction_and_carrier(
                loops, direction, carrier
            )

            output = func(self, loops, carrier, direction, *args, **kwargs)

            return output

        return wrapper

    def infer_carrier(self, carrier_index: int | Carrier | None = None) -> Carrier:
        """returns the carrier from carrier_index"""
        if carrier_index == None:
            carrier = self.active_carrier
            carrier_index = int(carrier)
        elif type(carrier_index) == int:
            carrier = self.get_carrier(carrier_index)
        elif type(carrier_index) == Carrier:
            carrier = carrier_index
            carrier_index = int(carrier)
        else:
            raise TypeError(
                f"carrier_index must be int or None not {type(carrier_index)}"
            )
        return carrier

    def infer_direction_and_carrier(
        self,
        loops: Loops | NeedleList,
        direction: CarrierDirection | None = None,
        carrier: int | Carrier | None = None,
    ) -> tuple[CarrierDirection, Carrier]:
        """returns proper carrier direction, carrier"""
        carrier = self.infer_carrier(carrier)
        if direction == None:
            direction = carrier.infer_direction(loops)

        return direction, carrier

    @clean_input
    def knit(
        self,
        loops: Loops,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
    ) -> None:
        """
        writes the knitout for knitting the specified loops
        """

        output = loops.knit(direction, carrier)

        self.knitout += output

        carrier.move(direction, loops)

    @clean_input
    def tuck(
        self,
        loops: Loops,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
    ) -> None:
        """
        writes the knitout for tucking the specified loops
        """

        output = loops.tuck(direction, carrier)

        self.knitout += output

        carrier.move(direction, loops)

    def needle_tuck(
        self,
        needles: NeedleList,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
    ):
        """tucks needles, returns the formed loops"""

        direction, carrier = self.infer_direction_and_carrier(
            needles, direction, carrier
        )
        needles = needles.sorted(direction)
        carrier.set_position(needles[-1])
        for n in needles:
            self.knitout += tuck(direction, n, carrier.index)
        ls = self.make_loops(needles)

        return ls

    @clean_input
    def miss(
        self,
        loops: Loops,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
    ) -> None:
        """
        writes the knitout for missing the specified loops
        """

        output = loops.miss(direction, carrier)

        self.knitout += output

        carrier.move(direction, loops)

    def drop(self, loops: Loops) -> None:
        """drops these loops"""
        self.knitout += loops.drop()

    @clean_input
    def split(
        self,
        loops: Loops,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
        offset: int = 0,
    ) -> Loops:
        """splits loops, outputs the loops at the location opposite the input loops"""

        direction, carrier = self.infer_direction_and_carrier(loops, direction, carrier)

        loops.clean()
        self.clean()

        output = loops.split(direction, carrier, offset)
        self.knitout += output
        carrier.move(direction, loops)

        new_loop_locations = NeedleList([l.needle.opposite(offset) for l in loops])
        new_loops = self.make_loops(new_loop_locations)

        return new_loops

    def xfer(self, loops: Loops, offset: int = 0) -> None:
        """
        writes the knitscript for xfering loops with optional offset
        positive offset is right, negative is left
        all loops must be on the same bed
        """
        loops.clean()
        self.clean()
        output = loops.xfer(offset)

        self.knitout += output

    @clean_input
    def twisted_cast_on(
        self,
        needles: NeedleList,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
    ) -> Loops:
        """
        casts on needles using the twisted cast on and writes the knitout
        carrier and direction are optional, kind ofs
        """
        output = KnitOut()

        needles = needles.sorted(direction)
        first = needles[0]
        opp_direct = direction.opposite()

        if first.bed == KnittingMachineBed.BACK:
            output += tuck(direction, first.opposite(), carrier)
            output += tuck(opp_direct, first, carrier)
        else:
            output += tuck(direction, first, carrier)

        for n in needles[1:]:
            output += tuck(opp_direct, n, carrier)

        carrier.set_position(needles[-1].index)

        self.knitout += output
        loops = self.make_loops(needles)

        self.knit(loops[0:-1])
        self.releasehook()

        return loops

    def clean(self) -> None:
        self.all_loops.clean()
        self.front_loops = Loops([])
        self.back_loops = Loops([])

        for l in self.all_loops:
            if l.needle.bed == front_bed:
                self.front_loops.append(l)
            else:
                self.back_loops.append(l)

    @clean_input
    def chain_bind_off(
        self,
        loops: Loops,
        carrier: int | Carrier | None = None,
        direction: CarrierDirection | None = None,
        do_hold: bool = True,
    ) -> None:
        """
        writes the knitout for binding off using the chain bind off
        do_hold controlls if the loops are split or knit
        """

        loops = loops.sorted(direction)

        for _ in range(loops.len() - 1):
            gap = int(loops[1]) - int(loops[0])

            l = loops[0:1]

            self.knit(l, carrier, direction)

            if do_hold:
                self.split(l, carrier, direction)

            self.xfer(l, gap)

            self.xfer(l)

        self.knit(loops, carrier, direction)

    def output(self, lines: KnitOut) -> str:
        program = "\n".join(lines) + "\n"
        with open(self.knitout_file_name, "w") as file:
            file.write(program)
        return program

    def cut_all_carriers(self) -> None:
        for carr in list(self.inhooked_carriers):
            self.cut(carr)

    def compile(self) -> str:
        """outputs a .k file"""
        self.header()
        self.run()
        self.releasehook()
        self.cut_all_carriers()
        output = self.output(self.knitout)
        knitout_to_dat(self.knitout_file_name, self.dat_file_name)
        return output

    def run() -> KnitOut:
        raise NotImplementedError("unimplemented, inherit and do that in your program")
