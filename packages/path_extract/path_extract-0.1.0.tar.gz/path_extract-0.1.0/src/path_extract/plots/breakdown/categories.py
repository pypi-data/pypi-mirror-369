from path_extract.constants import ClassNames, Columns
from path_extract.plots.helpers.constants import CARBON_EMIT_LABEL
from path_extract.plots.breakdown.color_category_map import map_use_category_colors
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
from rich import print as rprint
from path_extract.plots.helpers.theme import scape
from path_extract.data.utils import add_category_label
import path_extract.data.columns as col

import altair as alt
import polars as pl


def prep_df(
    project_name: ProjectNames,
    exp_num: int,
):
    df = get_exp_df(project_name, exp_num)
    return add_category_label(df)


def plot_use_categories(df: pl.DataFrame, title: str = "", renderer="browser"):
    rprint(df)
    alt.renderers.enable(renderer)

    domains, range_ = map_use_category_colors(df)
    chart = (
        alt.Chart(df, title=title)
        .mark_bar()
        .encode(
            x=alt.X(f"{col.CUSTOM_CATGEORY_LABEL}:N")
            .title("Use Categories")
            .sort(None),
            y=alt.Y(f"sum({col.VALUE})", axis=alt.Axis(format=NUMBER_FORMAT)).title(
                CARBON_EMIT_LABEL
            ),
            color=alt.Color(col.CATEGORY)
            .sort(None)
            .scale(domain=domains, range=range_),
            tooltip=[
                col.CATEGORY,
                alt.Tooltip(f"sum({col.VALUE})", format=".2s"),
            ],
        )
        .configure_axisX(labelAngle=DIAGONAL_LABEL_ANGLE)
    )

    return chart


def make_categorical_figure(
    project_name: ProjectNames,  # noqa: F821
    exp_num: int,
    renderer: RendererTypes = BROWSER,
):
    clmt_path = CLMTPath(project_name)
    df = prep_df(project_name, exp_num)
    chart = plot_use_categories(df, renderer=renderer)
    if renderer == HTML:
        fig_name = f"exp{exp_num}_categories.png"
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()

    return chart


if __name__ == "__main__":
    alt.theme.enable("scape")
    make_categorical_figure("newtown_creek", 0)
