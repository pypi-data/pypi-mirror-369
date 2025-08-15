from rich import print as rprint
from typing import Iterable, Iterator, Literal
from itertools import cycle
from pypalettes import load_cmap

# TODO use pypalettes

# color schemes used in vega-altair
# https://github.com/vega/vega/blob/main/packages/vega-scale/src/palettes.js
# code based on https://www.xoolive.org/2021/09/27/vega-colorschemes.html
# all vega colors https://vega.github.io/vega/docs/schemes/


VegaColors = Literal[
    "blues",
    "greens",
    "greys",
    "oranges",
    "purples",
    "reds",
    "browns",
    "tealBlues",
    "teals",
    "warmGreys",
    "darkGold",
    "yellowOrangeBrown",
]

vega_colors: dict[VegaColors, str] = {
    "blues": "cfe1f2bed8eca8cee58fc1de74b2d75ba3cf4592c63181bd206fb2125ca40a4a90",
    "greens": "d3eecdc0e6baabdda594d3917bc77d60ba6c46ab5e329a512089430e7735036429",
    "greys": "e2e2e2d4d4d4c4c4c4b1b1b19d9d9d8888887575756262624d4d4d3535351e1e1e",
    "oranges": "fdd8b3fdc998fdb87bfda55efc9244f87f2cf06b18e4580bd14904b93d029f3303",
    "purples": "e2e1efd4d4e8c4c5e0b4b3d6a3a0cc928ec3827cb97566ae684ea25c3696501f8c",
    "reds": "fdc9b4fcb49afc9e80fc8767fa7051f6573fec3f2fdc2a25c81b1db21218970b13",
    "browns": "eedbbdecca96e9b97ae4a865dc9856d18954c7784cc0673fb85536ad44339f3632",
    "tealBlues": "bce4d89dd3d181c3cb65b3c245a2b9368fae347da0306a932c5985",
    "teals": "bbdfdfa2d4d58ac9c975bcbb61b0af4da5a43799982b8b8c1e7f7f127273006667",
    "warmGreys": "dcd4d0cec5c1c0b8b4b3aaa7a59c9998908c8b827f7e7673726866665c5a59504e",
    "darkGold": "3c3c3c584b37725e348c7631ae8b2bcfa424ecc31ef9de30fff184ffffff",
    "yellowOrangeBrown": "feeaa1fedd84fecc63feb746fca031f68921eb7215db5e0bc54c05ab3d038f3204",
}


def make_cycle_of_colors(scheme: VegaColors):
    LEN_OF_HEX_COLOR = 6
    curr_scheme = vega_colors[scheme]
    return iter(cycle(
        "#"
        + curr_scheme[LEN_OF_HEX_COLOR * i : LEN_OF_HEX_COLOR * i + LEN_OF_HEX_COLOR]
        for i in range(len(curr_scheme) // LEN_OF_HEX_COLOR)
    ))


def get_dict_of_colors() -> dict[VegaColors, Iterator[str]]:
    return {k: make_cycle_of_colors(k) for k in vega_colors.keys()}


if __name__ == "__main__":
    d = get_dict_of_colors()
    rprint(next(d["greens"]))
    # scheme = continuous_colors["greens"]
    # colors = make_list_of_colors("greens")
    # rprint(colors)
    # cmap = load_cmap("Althoff")
    # rprint(cmap.hex)
