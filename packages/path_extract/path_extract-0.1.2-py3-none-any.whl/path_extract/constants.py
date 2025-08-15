from enum import StrEnum
from typing import TypedDict

MAIN_WRAPPER = "main-wrapper"


# TODO can do "linked str enums.. "
class Emissions(StrEnum):
    EMBODIED = "Embodied"
    OPERATIONAL = "Operational"
    BIOGENIC = "Biogenic"
    STORAGE = "Carbon Stored"


class Area(StrEnum):
    TOTAL = "Site"
    PLANTED = "Planted"


class Other(StrEnum):
    NET = "Net"
    EMIT_PA = "Emissions per Area"
    SEQ_PA = "Seq per Area"


overview_map = {
    "Net Impact over 60 years": Other.NET,
    "Total Embodied Emissions": Emissions.EMBODIED,
    "Total Biogenic(Sequestration + Emissions)": Emissions.BIOGENIC,
    "Total Operational Emissions": Emissions.OPERATIONAL,
    "Total Carbon Stored": Emissions.STORAGE,
    "Site Area": Area.TOTAL,
    "Planted Area": Area.PLANTED,
    "Emissions per Area": Other.EMIT_PA,
    "Sequestration per Area": Other.SEQ_PA,
}

# class OverviewNames(StrEnum):
#     EMBODIED = "Total Embodied Emissions"
#     OPERATIONAL = "Total Biogenic(Sequestration + Emissions)"
#     BIOGENIC = "Biogenic"
#     STORAGE = "Carbon Stored"


class Headings(StrEnum):
    CARBON_IMPACT = "Carbon Impact"
    EMBODIED_CARBON_EMISSIONS = "Embodied Carbon Emissions"
    BIOGENIC = "Biogenic (Sequestration + Emissions)"
    OPERATIONAL = "Operational Emissions"


class ClassNames(StrEnum):
    SECTION = "section-header"
    TYPE = "type-header"
    CATEGORY = "category-header"
    ELEMENT = "element-name"
    VALUE = "element-co2"
    SEQUESTERING = "seq"


class Columns(
    StrEnum
):  # TODO make better datatype, so donthave to put .name everywhere..
    SECTION = "SECTION"
    TYPE = "TYPE"
    CATEGORY = "CATEGORY"
    ELEMENT = "ELEMENT"
    VALUE = "VALUE"
    UNIT = "UNITS"
    CUSTOM_CATEGORY = "CUSTOM_CATEGORY"
    NAME = "NAMES"
    VALUE_ALT = "VALUE_ALT"
    VALUE_DIFF = "VALUE_DIFF"
    BASELINE = "BASELINE"
    ALT = "ALT"
    CUSTOM_CATGEORY_LABEL = "CUSTOM_CATEGORY_LABEL"


class ExperimentInfo(TypedDict):
    project: str
    experiment: str
    index: int


