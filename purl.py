#!/usr/bin/env python

import sys

try:
    filename = sys.argv[1]
except:
    print(f"usage: {sys.argv[0]} file-to-compile")
    exit(1)

knitout_filename = filename + ".k"

knitout_lines = []
""";!knitout-2
;;Carriers: 1 2 3 4 5 6 7 8 9 10
;;Machine: SWG091N2
;;Gauge: 13
;;Width: 450
;;Position: Keep"""
carriers = list(range(1, 11))


def header(
    knit_out_version: str = "knitout-2",
    carriers: list[int] = carriers,
    machine: str = "SWG091N2",
    gauge: int = 13,
    width: int = 450,
    justify_position: str = "Keep",
) -> list[str]:
    return [
        f";!{knit_out_version}",
        f";;Carriers: {' '.join(str(i) for i in carriers)}",
        f";;Machine: {machine}",
        f";;Gauge: {gauge}",
        f";;Width: {width}",
        f";;Position: {justify_position}",
    ]


print("\n".join(header()))
