#!/usr/bin/env python


import sys
from itertools import chain

from purl.knitout_opcodes import *
from purl.utils import *

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


# TODO: there's a decorator to decalre an abstract class (or interface), use it
class AbstractPurlProgram:
    def __init__(
        self,
        output_filename: str,
        starting_needle: int,
        ending_needle: int,
    ):
        self.output_filename = output_filename
        self.starting_needle = starting_needle
        self.ending_needle = ending_needle
        self.cast_on_needles = NeedleList(
            Needle(i, KnittingMachineBed.FRONT)
            for i in range(self.starting_needle, self.ending_needle)
        )

    def output(self, lines: KnitOut) -> str:
        program = "\n".join(lines) + "\n"
        with open(self.output_filename, "w") as file:
            file.write(program)
        return program

    def compile(self) -> str:
        """outputs a .k file"""
        knit_out = self.run()
        return self.output(knit_out)

    def run() -> KnitOut:
        raise "unimplemented, inherit and do that in your program"


class StockinetteSquare(AbstractPurlProgram):
    def run(self) -> KnitOut:
        needles = self.cast_on_needles
        knitout = (
            header()
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


# you can invoke this and test it via...
# ./purl_test.py new_output.k &&  cmp new_output.k expected_output.k && echo "new_output matches expected output. woo hoo\!"
if True or __name__ == "main":
    try:
        filename = sys.argv[1]
    except:
        print(f"usage: {sys.argv[0]} output_filename")
        exit(1)

    ss = StockinetteSquare(
        output_filename=filename, starting_needle=390, ending_needle=420
    )
    ss.compile()
