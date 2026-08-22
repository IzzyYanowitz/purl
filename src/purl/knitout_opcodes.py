from .utils import KnitOut, CarrierDirection, Needle


def inhook(carrier: int) -> KnitOut:
    return KnitOut([f"inhook {carrier}"])


def outhook(carrier: int) -> KnitOut:
    return KnitOut([f"outhook {carrier}"])


def releasehook(carrier: int) -> KnitOut:
    return KnitOut([f"releasehook {carrier}"])


def tuck(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"tuck {direction} {source_needle} {carrier}"])


def knit(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"knit {direction} {source_needle} {carrier}"])


def miss(direction: CarrierDirection, source_needle: Needle, carrier: int) -> KnitOut:
    return KnitOut([f"miss {direction} {source_needle} {carrier}"])


def rack(offset: float) -> KnitOut:
    return KnitOut([f"rack {offset}"])


def xfer(source_needle: Needle, destination_needle: Needle) -> KnitOut:
    return KnitOut([f"xfer {source_needle} {destination_needle}"])
