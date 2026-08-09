#!/usr/bin/env python

import sys

try:
    filename = sys.argv[1]
except:
    print(f"usage: {sys.argv[0]} file-to-compile")
    exit(1)

knitout_filename = filename + ".k"

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


def output(knitout_filename: str, lines: list[str]) -> None:
    with open(knitout_filename, "w") as file:
        file.write("\n".join(lines))
        file.write("\n")


knitout = header()

output(knitout_filename, knitout)
