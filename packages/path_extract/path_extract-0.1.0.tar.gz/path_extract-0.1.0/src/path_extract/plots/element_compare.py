from path_extract.constants import Columns
from path_extract.plots.helpers.constants import CARBON_EMIT_LABEL
from path_extract.data.utils import add_category_label, print_whole_df
from path_extract.project_paths import CLMTPath, ProjectNames
from path_extract.data.dataframes import (
    UseCategories,
    edit_breakdown_df,
    get_net_emissions,
)
import polars as pl
from rich import print as rprint
import altair as alt
from path_extract.plots.helpers.constants import (
    HTML,
    NUMBER_FORMAT,
    POINT_SIZE,
    get_exp_df,
    save_fig,
    BROWSER,
)
from typing import NamedTuple, TypedDict
from prefixed import Float
from path_extract.plots.helpers.theme import scape, category_pallete, FONT_COLOR
import path_extract.data.columns as col


from path_extract.plots.helpers.constants import RendererTypes, DEF_DIMENSIONS

EXP_NUM = "num"
EXP_NAME = "name"
VAL = "value"
FORMATTED_VALUE = "formatted_val"
X_CHANGE = "xchange"

BASELINE = "As Designed"
ALTERNATIVE = "Alternative"
EXPERIMENT_NAMES = "Experiment Names"


# NOTE rn, VERY specific to BPCR
def prep_df(project_name: ProjectNames, exp_num: int):
    df = get_exp_df(project_name, exp_num)
    # rprint(df[Columns.CUSTOM_CATEGORY.name].unique().to_list())

    # want to look at demo  where element name contains trees
    TREE_REMOVAL_ELEMENT = "EXISTING TREE REMOVAL"
    # TODO own function
    tree_removal = df.filter(
        (pl.col(col.CUSTOM_CATEGORY) == UseCategories.DEMOLITION.name)
        & (pl.col(col.ELEMENT).str.to_uppercase().str.contains(TREE_REMOVAL_ELEMENT))
    )

    # then compare with new planting
    new_planting = df.filter(
        pl.col(col.CUSTOM_CATEGORY) == UseCategories.NEW_PLANTING.name
    )

    # print_whole_df(tree_removal)
    # print_whole_df(new_planting)
    new_df = pl.concat([tree_removal, new_planting]).with_columns()

    return add_category_label(new_df)


def plot_element_compare(df: pl.DataFrame, renderer=BROWSER):
    alt.renderers.enable(renderer)  # TODO make this a base fx..

    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{col.CUSTOM_CATGEORY_LABEL}:N").stack("zero").title(None),
            y=alt.Y(f"sum({col.VALUE}):Q")
            .axis(format=NUMBER_FORMAT)
            .title(CARBON_EMIT_LABEL),
            color=alt.Color(f"{col.CUSTOM_CATGEORY_LABEL}:N").legend(None),
            # color=alt.Color(f"{col.ELEMENT}:N"),
        )
    ).configure_axisX(labelAngle=0)

    # need to compute where the text should be.. => halfway between the two values..
    # first bar, then simple waterfall..

    # bars.show()

    return bars


def make_element_compare_figure(
    project_name: ProjectNames, exp_num: int, renderer: RendererTypes = BROWSER
):
    clmt_path = CLMTPath(project_name)
    df = prep_df(project_name, exp_num)
    chart = plot_element_compare(df, renderer)
    if renderer == HTML:
        fig_name = f"exp{exp_num}_element_compare.png"
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()

    return chart


if __name__ == "__main__":
    # alt.theme.enable("carbonwhite")
    alt.theme.enable("scape")

    # as_designed = ExpeMetaData(0, BASELINE)
    # better_alt = ExpeMetaData(3, ALTERNATIVE)

    make_element_compare_figure("bpcr", 0, renderer=BROWSER)
