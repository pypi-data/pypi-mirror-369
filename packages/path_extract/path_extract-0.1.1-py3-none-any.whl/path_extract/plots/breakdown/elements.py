from path_extract.constants import ClassNames, Columns
from path_extract.data.categories.use_categories import UseCategories
from path_extract.plots.helpers.constants import CARBON_EMIT_LABEL
from path_extract.data.dataframes import edit_breakdown_df
from path_extract.data.utils import add_category_label
from path_extract.project_paths import CLMTPath, ProjectNames
from path_extract.data.dataframes import edit_breakdown_df
from path_extract.plots.helpers.constants import (
    BROWSER,
    HTML,
    DIAGONAL_LABEL_ANGLE,
    NUMBER_FORMAT,
    RendererTypes,
    get_exp_df,
    save_fig,
)
import altair as alt
import polars as pl
import path_extract.data.columns as col

from path_extract.plots.breakdown.color_category_map import (
    map_use_category_colors_to_elements,
)


def prep_df(
    project_name: ProjectNames,
    exp_num: int,
    filter_categories: list[UseCategories] | None = None,
):
    df = add_category_label(get_exp_df(project_name, exp_num))
    if filter_categories:
        return df.filter(
            pl.col(col.CUSTOM_CATEGORY).is_in([i.name for i in filter_categories])
        )

    # rprint(df)

    return df


def plot_elements(df: pl.DataFrame, title: str = "", renderer="browser"):
    alt.renderers.enable(renderer)
    domains, range_ = map_use_category_colors_to_elements(df)

    chart = (
        alt.Chart(df, title=title)
        .mark_bar()
        .encode(
            x=alt.X(col.CUSTOM_CATGEORY_LABEL).title("Category").sort(None),
            y=alt.Y(f"sum({ClassNames.VALUE.name})")
            .title(CARBON_EMIT_LABEL)
            .axis(format=NUMBER_FORMAT),
            color=alt.Color(ClassNames.ELEMENT.name)
            .sort(None)
            .scale(domain=domains, range=range_),
            tooltip=[
                ClassNames.ELEMENT.name,
                alt.Tooltip(ClassNames.VALUE.name, format=NUMBER_FORMAT),
            ],
        )
        # .facet(column=TableNames.CUSTOM_CATEGORY.name)
    ).configure_axisX(labelAngle=DIAGONAL_LABEL_ANGLE)

    return chart


def make_element_figure(
    project_name: ProjectNames,  # noqa: F821
    exp_num: int,
    renderer: RendererTypes = BROWSER,
    filter_categories: list[UseCategories] | None = None,
):
    clmt_path = CLMTPath(project_name)
    df = prep_df(project_name, exp_num, filter_categories=filter_categories)
    chart = plot_elements(df, renderer=renderer)
    if renderer == HTML:
        fig_name = f"exp{exp_num}_elements.png"
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()

    return chart


if __name__ == "__main__":
    alt.theme.enable("scape")
    make_element_figure(
        "newtown_creek",
        0,
        filter_categories=[
            UseCategories.NEW_PLANTING,
            UseCategories.HARDSCAPE,
        ],
    )
