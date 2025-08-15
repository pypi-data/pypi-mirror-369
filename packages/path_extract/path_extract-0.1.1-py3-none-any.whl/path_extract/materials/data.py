from typing import NamedTuple


class ElementGWP(NamedTuple):
    name: str
    value: float


playground_alts = [
    ElementGWP("Synthetic Turf", 5.5),
    ElementGWP("EPDM Safety Surface", 3.713),
    ElementGWP("EPDM Safety Surface - Recycled", 0.752),
    ElementGWP("Engineer Fiber Mulch Safety Surface", 0.312),
]
