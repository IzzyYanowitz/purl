from .machine_types import KnitOut, CarrierDirection, Needle


def inhook(carrier: int) -> KnitOut:
    """returns the knitout \<inhook\> opcode"""
    return KnitOut([f"inhook {carrier}"])


def outhook(carrier: int) -> KnitOut:
    """returns the knitout \<outhook\> opcode"""
    return KnitOut([f"outhook {carrier}"])


def releasehook(carrier: int) -> KnitOut:
    """returns the knitout \<releasehook\> opcode"""
    return KnitOut([f"releasehook {carrier}"])


def tuck(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    """returns the knitout \<tuck\> opcode"""
    return KnitOut([f"tuck {direction} {source_needle} {carrier}"])


def knit(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    """returns the knitout \<knit\> opcode"""
    return KnitOut([f"knit {direction} {source_needle} {carrier}"])


def split(
    direction: CarrierDirection,
    source_needle: Needle,
    destination_needle: Needle,
    carrier: int,
) -> KnitOut:
    """

    returns the knitout \<split\> opcode

    we will want to implement sanity checking, e.g.
        if source_needle.bed == destination_needle.bed:
        pass
    but we haven't decided where that will live

    """

    return KnitOut(
        [f"split {direction} {source_needle} {destination_needle} {carrier}"]
    )


def miss(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    """returns the knitout \<miss\> opcode"""

    return KnitOut([f"miss {direction} {source_needle} {carrier}"])


def drop(source_needle: Needle) -> KnitOut:
    return KnitOut([f"drop {source_needle}"])


def rack(offset: float) -> KnitOut:
    """returns the knitout \<rack\> opcode"""

    return KnitOut([f"rack {offset}"])


def xfer(source_needle: Needle, destination_needle: Needle) -> KnitOut:
    """returns the knitout \<xfer\> opcode"""

    return KnitOut([f"xfer {source_needle} {destination_needle}"])
