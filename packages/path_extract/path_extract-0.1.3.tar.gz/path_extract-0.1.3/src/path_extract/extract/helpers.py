from typing import NamedTuple
from bs4.element import Tag
import re
from rich import print as rprint
from path_extract.constants import ClassNames
import numpy as np


class Comparison(NamedTuple):
    embodied: int
    biogenic: int

    def __eq__(self, other: object) -> bool:
        TOL = 1e-5
        if not isinstance(other, Comparison):
            raise Exception("Invalid object for comparision")
        embodied_check = np.isclose(self.embodied, other.embodied, rtol=TOL)
        if not embodied_check:
            raise Warning(f"Embodied check failed: {self.embodied} != {other.embodied}")
        biogenic_check = np.isclose(abs(self.biogenic), abs(other.biogenic), rtol=TOL)
        if not biogenic_check:
            raise Warning(f"Biogenic check failed: {self.biogenic} != {other.biogenic}")
        return bool(embodied_check) & bool(biogenic_check)


def is_element_row(tag: Tag):
    if tag.has_attr("class"):
        if len(tag["class"]) == 0:
            return True


def get_element_name(tag: Tag):
    td = tag.find("td", class_=ClassNames.ELEMENT.value)
    assert isinstance(td, Tag)
    # TODO add to obsidian [drop excess white space with regex](https://stackoverflow.com/questions/1546226/is-there-a-simple-way-to-remove-multiple-spaces-in-a-string)
    return re.sub(" +", " ", td.get_text(strip=True)).replace("\n", "")


ValueAndUnit = NamedTuple("ValueAndUnit", [("value", int), ("unit", str | None)])


def get_element_value(tag: Tag):
    td = tag.find("td", class_=ClassNames.VALUE.value)
    assert isinstance(td, Tag)

    result = td.get_text("|", strip=True).split(" ")
    if len(result) == 2:
        integer_value = int(result[0].replace(",", ""))
        if ClassNames.SEQUESTERING.value in td["class"]:
            # rprint(f"{tag.get_text()} IS SEQUESTERING!")
            integer_value *= -1
        return ValueAndUnit(integer_value, result[1])
    if len(result) == 1:
        return ValueAndUnit(0, None)
    else:
        raise NotImplementedError(
            f"Invalid result: `{result}` - should have len 1 or 2, but has len {len(result)}"
        )


def is_header_of_class_type(tag: Tag, class_: ClassNames):
    if tag.has_attr("class"):
        if class_.value in tag["class"]:
            return True


def get_header_name(tag: Tag):
    assert tag.td
    return tag.td.get_text(strip=True)


def create_list_of_class_type(_class: ClassNames, row: Tag, curr_value=""):
    if is_header_of_class_type(row, _class):
        curr_value = get_header_name(row)
    return curr_value
