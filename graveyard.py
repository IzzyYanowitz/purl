"""def checkboard(pp: PerlProgram):
    # do a lot of knitting oeprations to make a checkboard pattern
    pp.op1()
    pp.op2()

class ThisProgram(PurlProgram):

    def checkerboard():
        pp.op1()
        pp.op2()

ts = this_specific_program()


pp = PurlProgram(output: knitout_filename)
needles = NeedleList(Needle(i KnittingMachineBed.FRONT) for i in range(390, 420))
pp.backwards_loop_cast_on(needles)
pp.knit_rows(needles)
pp.bind_off()
pp.output()
pp.active_carrier=3

 my_loops = Loops(starting_needles: NeedleList)
my_loops = Loops.cast_on(starting_needles: NeedleList, carrier: Carrier)
# starting_needles: NeedleList([f100...f200])
#. loops areb[0..99]
other_loops = Loops.init(stariting_needles: [f125...f175])

subset_of_loops = my_loops.slice(25,75)

subset_of_loops.xfer()
my_loops.xfer()


my_loops = [f23, f24, f25]
pp.xfer(my_loops, 3)
# my_loops = [b26, b27, b28]
pp.xfer(my_loops, 0)
# my_loops = [f26, f27, f28]
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

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
"""

# output(knitout_filename, knitout)
""" 
try:
    filename = sys.argv[1]
except:
    print(f"usage: {sys.argv[0]} output_filename")
    exit(1)

ss = StockinetteSquare(output_filename=filename, starting_needle=390, ending_needle=420)
ss.compile()
 """
