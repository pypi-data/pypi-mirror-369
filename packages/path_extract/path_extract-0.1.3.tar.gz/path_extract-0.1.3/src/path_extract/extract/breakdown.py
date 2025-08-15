from bs4 import BeautifulSoup
from bs4.filter import SoupStrainer
from bs4.element import Tag
from path_extract.extract.helpers import (
    Comparison,
    ValueAndUnit,
    create_list_of_class_type,
    get_element_name,
    get_element_value,
    is_element_row,
)
from typing import IO, TypeAlias, Union

# from path_extract.project_paths import SAMPLE_CLMT_BREAKDOWN_HTML
from path_extract.constants import ClassNames, Columns, Headings
from pathlib import Path
import polars as pl

from collections import Counter

# just read main
MAIN_WRAPPER = "main-wrapper"
SCORECARD = "score-card"


IncomingMarkup: TypeAlias = Union[str, bytes, IO[str], IO[bytes]]

def read_breakdown(
    path: Path | None = None, file_contents: IncomingMarkup | None = None
) -> pl.DataFrame:
    def get_soup(file_data):
        return BeautifulSoup(
            file_data,
            features="html.parser",
            # features="html5lib",
            from_encoding="utf-8",
            parse_only=SoupStrainer(class_=SCORECARD),
        )

    if path:
        assert path.exists()
        with open(path, "r") as file:
            soup = get_soup(file)
    elif file_contents:
        soup = get_soup(file_contents)
    else:
        raise Exception("Need either a path or file contents!")

    all_rows = [i for i in soup.find_all("tr") if isinstance(i, Tag)]

    if not all_rows:
        raise Exception(
            f"Invalid file! `{path}` does not have a top-level class of `{SCORECARD}`: all_rows: {all_rows}"
        )

    category_counter = Counter()
    elements = []
    values: list[ValueAndUnit] = []

    type_counter = Counter()
    section_counter = Counter()

    curr_category = ""
    curr_section = ""
    curr_type = ""

    for row in all_rows:
        # type_counter = Counter()
        curr_section = create_list_of_class_type(
            ClassNames.SECTION, row, curr_section
        )  # TODO rename function ..  # TODO put in its own loop? break out to different function..
        curr_type = create_list_of_class_type(ClassNames.TYPE, row, curr_type)
        curr_category = create_list_of_class_type(
            ClassNames.CATEGORY, row, curr_category
        )

        if curr_category:
            if is_element_row(row):
                elements.append(get_element_name(row))
                values.append(get_element_value(row))

                category_counter[curr_category] += 1
                section_counter[curr_section] += 1
                type_counter[curr_type] += 1

    assert (
        section_counter.total()
        == type_counter.total()
        == category_counter.total()
        == len(elements)
    )
    # rprint(section_counter, type_counter)

    data = {
        ClassNames.SECTION.name: section_counter.elements(),
        ClassNames.TYPE.name: type_counter.elements(),
        ClassNames.CATEGORY.name: category_counter.elements(),
        ClassNames.ELEMENT.name: elements,
        ClassNames.VALUE.name: [i.value for i in values],
        Columns.UNIT.name: [i.unit for i in values],
    }
    return pl.DataFrame(data)


def get_breakdown_comparison(df):
    embodied = df.filter(
        pl.col(ClassNames.TYPE.name) == Headings.EMBODIED_CARBON_EMISSIONS
    )[ClassNames.VALUE.name].sum()
    biogenic = df.filter(pl.col(ClassNames.TYPE.name) == Headings.BIOGENIC)[
        ClassNames.VALUE.name
    ].sum()
    return Comparison(embodied, biogenic)


# if __name__ == "__main__":
#     df = read_breakdown(SAMPLE_CLMT_BREAKDOWN_HTML)
#     rprint(df)
# f = get_breakdown_comparison(df)
# rprint(f)
