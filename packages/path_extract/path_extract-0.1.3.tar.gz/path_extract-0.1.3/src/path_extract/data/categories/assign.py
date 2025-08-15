from enum import Enum
from path_extract.data.categories.use_categories import (
    pathfinder_categories,
    PathFinderCategories,
    UseCategories,
)
from path_extract.utils import chain_flatten, set_difference
from collections import Counter
from rich import print as rprint


AssignDict = dict[UseCategories, list[PathFinderCategories]]

assign_dict: AssignDict = {
    UseCategories.DEMOLITION: ["Demolition Site Preparation"],
    UseCategories.SITE_PREPARATION: ["Soil Amendments"],
    UseCategories.PRESERVED_PLANTING: [
        "Ecosystem Restoration",
        "Trees Existing To Protect",
        "Ecosystems Existing To Protect",
    ],
    UseCategories.SUBSTRUCTURE: [
        "Infrastructure Subsurface",
    ],
    UseCategories.HARDSCAPE: [
        "Metal Wood Hardscape",
        "Concrete Hardscape",
        "Brick Stone Hardscape",
        "Aggregate Asphalt Hardscape",
    ],
    UseCategories.NEW_PLANTING: [
        "Perennials Perennial Grasses",
        "Shrubs",
        "Lawn",
        "Trees",
    ],
    UseCategories.GREEN_INFRA: [
        "Green Infrastructure"
    ],  # also on structure things.. green roof etc
    UseCategories.ACCESSORIES: [
        "Exterior Lighting",
        "Playground Athletic",
        "Furnishings",
        "Planting Accessories",
        "Site Elements",
    ],
    UseCategories.OPERATIONS: ["Landscape Water Use"],
}
# TODO can actually export image of all pathfinder categories! 

# checks -> all categories are used, none are used twice
def check_assign_dict():
    values = chain_flatten([v for v in assign_dict.values()])
    for name, cnt in Counter(values).items():
        if cnt > 1:
            raise Exception(f"`{name}` occurs {cnt} times! It should only occur once!")

    diff = set_difference(pathfinder_categories, values)
    if diff:
        raise Exception(f"Missing items: {diff}")

    # check nothing occurs twice with counter..


def create_pairs(mapping: dict[UseCategories, list[PathFinderCategories]]):
    lst = []
    for key, value in mapping.items():
        for element in value:
            lst.append((element, key))
    return lst
    # rprint(UseCategories["OPERATIONS"])


if __name__ == "__main__":
    check_assign_dict()
