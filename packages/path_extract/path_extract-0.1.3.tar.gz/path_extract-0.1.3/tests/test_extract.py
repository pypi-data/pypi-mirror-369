import pytest
import polars as pl

from path_extract.examples import SAMPLE_CLMT_BREAKDOWN_HTML, SAMPLE_CLMT_OVERVIEW_HTML
from path_extract.constants import ClassNames, Headings, Emissions, Area
from path_extract.extract.breakdown import read_breakdown
from path_extract.extract.overview import read_overview
from path_extract.extract.helpers import is_element_row, is_header_of_class_type
from path_extract.paths import SAMPLE_HTML
from rich import print as rprint
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag

from path_extract.project_paths import CLMTPath, DataType


# @pytest.mark.skip("Trivial")
# def test_setup():
#     assert 1 + 1 == 2


def test_is_category_header():
    tag = """
        <tr class="category-header">
            <td colspan="2">Aggregate Asphalt Hardscape</td>
        </tr>
        """
    soup = BeautifulSoup(tag, features="html.parser")
    tr = soup.find("tr")
    assert isinstance(tr, Tag)
    result = is_header_of_class_type(tr, ClassNames.CATEGORY)
    assert result


def test_is_element_row():
    tag = """ 
        <tr class>
            <td class="element-name">Brick Paving</td>
            <td class="element-co2 neutral ">
                <span>0 kgCO₂e</span>
            </td>
        </tr>
    """
    soup = BeautifulSoup(tag, features="html.parser")
    tr = soup.find("tr")
    assert isinstance(tr, Tag)
    result = is_element_row(tr)
    assert result


# @pytest.mark.skip("Not here yet")
def test_read_breakdown():
    sample_categories = [
        "Aggregate Asphalt Hardscape",
        "Brick Stone Hardscape",
        "Concrete Hardscape",
    ]
    sample_elements = ["Asphalt Curb", "Brick Paving", "Cast-in-Place Concrete Paving"]
    sample_values = [0, 0, 4082]
    sample_types = [Headings.EMBODIED_CARBON_EMISSIONS.value] * len(sample_categories)

    df = read_breakdown(SAMPLE_HTML)

    data = {
        ClassNames.TYPE.name: sample_types,
        ClassNames.CATEGORY.name: sample_categories,
        ClassNames.ELEMENT.name: sample_elements,
        ClassNames.VALUE.name: sample_values,
    }
    expected_df_top = pl.DataFrame(data)

    assert df.select(data.keys()).head(3).equals(expected_df_top)


def test_clmt_paths():
    pier_6_paths = CLMTPath("pier_6")
    overview_html = pier_6_paths.get_html(0, DataType.OVERVIEW)
    assert overview_html.exists()


def test_read_breakdown_real_case():
    df = read_breakdown(SAMPLE_CLMT_BREAKDOWN_HTML)
    assert len(df) > 1 #TODO could get info about how long this is supposed to be?
    # TODO check that has correct columns

def test_read_breakdown_with_file_contents():
    with open(SAMPLE_CLMT_BREAKDOWN_HTML, "r") as file:
        df = read_breakdown(file_contents=file)
    assert len(df) > 1 





def test_read_overview():
    df = read_overview(SAMPLE_CLMT_OVERVIEW_HTML)
    assert len(df) > 1
    # TODO check that has correct columns
    # keys = [i.name for i in Emissions] + [i.name for i in Area]
    # assert sorted(keys) == sorted(list(result.keys()))


if __name__ == "__main__":
    test_read_breakdown()
