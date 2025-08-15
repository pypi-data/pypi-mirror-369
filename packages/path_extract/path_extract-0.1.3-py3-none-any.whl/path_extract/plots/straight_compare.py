from typing import Callable, Literal
import altair as alt
import polars as pl

from path_extract.data.categories.use_categories import UseCategories
from path_extract.constants import Columns
from path_extract.plots.helpers.constants import CARBON_EMIT_LABEL
from path_extract.project_paths import CLMTPath, ProjectNames
from path_extract.plots.helpers.constants import (
    BROWSER,
    NUMBER_FORMAT,
    RendererTypes,
    HTML,
    save_fig,
    HORIZONTAL_LABEL_ANGLE,
)
from path_extract.data.data_waterfall import compare_two_experiments
from path_extract.data.utils import filter_df, print_whole_df
import path_extract.data.columns as col

# from path_extract.plots.helpers.theme import scape
from rich import print as rprint

SHOW_LABEL = "SHOW_LABEL"
KEY = "key"
DATA = "data"


def prep_df(
    project_name: ProjectNames,
    base_exp_num: int,
    alt_exp_num: int,
    filter_categories: list[UseCategories] = [],
    filter_elements: list[str] = [],
):
    _df = compare_two_experiments(project_name, base_exp_num, alt_exp_num, True)

    # if filter_categories or filter_elements:

    df = filter_df(
        _df, filter_categories=filter_categories, filter_elements=filter_elements
    )
    # print_whole_df(df)
    rprint(df.sum())

    d = df.unpivot(
        on=[col.VALUE, col.VALUE_ALT],
        index=[col.ELEMENT, col.CUSTOM_CATEGORY],
        variable_name=KEY,
        value_name=DATA,
    )
    return d


CHART_GRAPH_FX = Callable[[alt.Chart], alt.LayerChart | alt.FacetChart | alt.Chart]


def stacked_graph(base: alt.Chart) -> alt.LayerChart | alt.FacetChart | alt.Chart:
    bar = base.mark_bar().encode(
        x=alt.X("AxisName:N")
        .sort()  # TODO make sure sort order is correct ..
        .title("Scenarios")
        .scale(alt.Scale(paddingInner=0.8, paddingOuter=0.4)),
        y=alt.Y("sum(data):Q").axis(format=NUMBER_FORMAT).title(CARBON_EMIT_LABEL),
        color=alt.Color(f"{col.ELEMENT}:N").legend(labelLimit=500),
    )

    total = (
        base.transform_aggregate(total="sum(data)", groupby=["IsEmit", "AxisName"])
        .mark_text(dy=-10)
        .encode(
            text=alt.Text("total:Q").format(NUMBER_FORMAT),
            x=alt.X("AxisName:N").sort(),
            y="total:Q",
        )
    )

    chart = bar + total  # )  # .facet(column="AxisName:N")

    return chart.properties(width=700).configure_axisX(
        labelAngle=HORIZONTAL_LABEL_ANGLE
    )  # .facet(column="AxisName:N")


def simplifed_graph(base: alt.Chart) -> alt.LayerChart:
    post_base = base.transform_calculate(
        IsEmit=alt.expr.if_(alt.datum.data > 0, True, False)
    )

    bar = post_base.mark_bar().encode(
        x=alt.X("AxisName:N").sort().title("Scenarios"),
        y=alt.Y("sum(data):Q").axis(format=NUMBER_FORMAT).title(CARBON_EMIT_LABEL),
        color=alt.Color("IsEmit:N").legend(labelLimit=500).sort(),
    )

    text = (
        post_base.transform_aggregate(Total="sum(data)", groupby=["IsEmit", "AxisName"])
        .encode(
            text=alt.Text("Total:Q").format(NUMBER_FORMAT),
            x=alt.X("AxisName:N").sort(),
            y=alt.Y("Total:Q"),
        )
        .mark_text(dy=10)
    )

    # contents = (
    #     post_base.transform_aggregate(
    #         Contents="values(ELEMENT)", groupby=["IsEmit", "AxisName"]
    #     )
    #     .encode(
    #         text=alt.Text("Contents:N"),
    #         x=alt.X("AxisName:N").sort(),
    #         y=alt.Y("Total:Q"),
    #     )
    #     .mark_text(dy=-50, dx=400)
    # )
    # rprint(extract_data(contents))

    return (bar + text).configure_axisX(labelAngle=0)


def plot_stack_compare(df: pl.DataFrame, chart_fx: CHART_GRAPH_FX = stacked_graph):
    base = alt.Chart(df).transform_calculate(
        AxisName=alt.expr.if_(
            alt.datum.key == Columns.VALUE.name, "As Designed", "Alternative"
        ),
        IsEmit=alt.expr.if_(alt.datum.data > 0, True, False),
    )

    return chart_fx(base)


fx_dict = {"simple": simplifed_graph, "stacked": stacked_graph}


def make_straight_compare_figure(
    project_name: ProjectNames,
    base_exp_num: int,
    alt_exp_num: int,
    renderer: RendererTypes = BROWSER,
    filter_categories: list[UseCategories] = [],
    filter_elements: list[str] = [],
    chart_fx_str: Literal["stacked", "simple"] = "stacked",
):
    alt.renderers.enable(renderer)
    clmt_path = CLMTPath(project_name)
    df = prep_df(
        project_name, base_exp_num, alt_exp_num, filter_categories, filter_elements
    )
    chart_fx = fx_dict[chart_fx_str]
    chart = plot_stack_compare(df, chart_fx)
    categ_names = "_".join([i.name.lower() for i in filter_categories])
    el_names = "_".join([i.lower() for i in filter_elements])
    fx_type = "simple" if chart_fx_str == "simple" else "stacked"
    fig_name = f"exp{base_exp_num}_{alt_exp_num}_{categ_names}_{el_names}_{fx_type}_straight_compare.png"
    rprint(f"fig name: {fig_name}")
    if renderer == HTML:
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()
    return chart


if __name__ == "__main__":
    alt.theme.enable("scape")
    make_straight_compare_figure(
        "pier_6",
        2,
        4,
        renderer=BROWSER,
        # filter_elements=["Concrete Hardscape"],
        # chart_fx_str="simple",
        # TODO plot simple
    )
