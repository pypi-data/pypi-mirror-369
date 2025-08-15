from typing import Literal
from enum import Enum

# TODO why is this a tuple?
class UseCategories(Enum):
    PRESERVED_PLANTING = (0,)  # "Preserved Planting / Restoration"
    DEMOLITION = (1,)  # "Demolition"
    SITE_PREPARATION = (2,)  # "Preparation"
    SUBSTRUCTURE = (3,)  # "Substructure"
    HARDSCAPE = (4,)  # "Hardscape"
    NEW_PLANTING = (5,)  # "New Planting"  # TODO 'on-structure'
    GREEN_INFRA = (6,)  # "Green Infrasturcture"  # these are composites..
    ACCESSORIES = (7,)  # "Accessories"
    OPERATIONS = (8,)  # "Operations"

    def title(self):
        return " ".join(self.name.title().split("_"))


PathFinderCategories = Literal[
    "Exterior Lighting",
    "Demolition Site Preparation",
    "Perennials Perennial Grasses",
    "Green Infrastructure",
    "Landscape Water Use",
    "Metal Wood Hardscape",
    "Soil Amendments",
    "Playground Athletic",
    "Concrete Hardscape",
    "Furnishings",
    "Shrubs",
    "Planting Accessories",
    "Brick Stone Hardscape",
    "Ecosystem Restoration",
    "Site Elements",
    "Trees",
    "Aggregate Asphalt Hardscape",
    "Infrastructure Subsurface",
    "Lawn",
    "Trees Existing To Protect",
    "Ecosystems Existing To Protect",
]


pathfinder_categories: list[PathFinderCategories] = [
    "Exterior Lighting",
    "Demolition Site Preparation",
    "Perennials Perennial Grasses",
    "Green Infrastructure",
    "Landscape Water Use",
    "Metal Wood Hardscape",
    "Soil Amendments",
    "Playground Athletic",
    "Concrete Hardscape",
    "Furnishings",
    "Shrubs",
    "Planting Accessories",
    "Brick Stone Hardscape",
    "Ecosystem Restoration",
    "Site Elements",
    "Trees",
    "Aggregate Asphalt Hardscape",
    "Infrastructure Subsurface",
    "Lawn",
    "Trees Existing To Protect",
    "Ecosystems Existing To Protect",
]
