from typing import Callable
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


def get_max_value(df: pl.DataFrame):
    p = df.select([col.VALUE, col.VALUE_ALT]).max().max_horizontal().to_list()[0]
    return p


def prep_df(
    project_name: ProjectNames,
    base_exp_num: int,
    alt_exp_num: int,
    filter_categories: list[UseCategories] = [],
    filter_elements: list[str] = [],
):
    _df = compare_two_experiments(project_name, base_exp_num, alt_exp_num)

    # if filter_categories or filter_elements:

    df = filter_df(
        _df, filter_categories=filter_categories, filter_elements=filter_elements
    )
    MIN_PERC = 0.05
    max_val = get_max_value(df)
    min_val = max_val * MIN_PERC
    rprint(f"max_val: {max_val}, min_val: {min_val}")

    # df_to_print = df.select(pl.exclude(col.SECTION))
    # print_whole_df(df_to_print)
    # agg_df = df_to_print.group_by(pl.col(col.CUSTOM_CATEGORY)).agg(
    #     pl.col(col.CATEGORY).unique(),
    #     pl.col(col.ELEMENT).unique(),
    #     pl.col(col.VALUE).sum(),
    #     pl.col(col.VALUE_ALT).sum(),
    # )

    # print_whole_df(agg_df)
    # for ir in agg_df.iter_rows(named=True):
    #     rprint(f"ir: {ir}")
    # print_whole_df(
    #     df_to_print.group_by(by=(pl.col(col.VALUE) > 0)).agg(p)
    # )

    # print_whole_df(df..sum())

    comparison = pl.col(DATA) > min_val

    d = df.unpivot(
        on=[col.VALUE, col.VALUE_ALT],
        index=[col.ELEMENT, col.CUSTOM_CATEGORY],
        variable_name=KEY,
        value_name=DATA,
    ).with_columns(
        pl.when(comparison).then(col.ELEMENT).otherwise(pl.lit("")).alias(SHOW_LABEL)
    )

    # print_whole_df(d.select([col.ELEMENT, KEY, DATA, SHOW_LABEL]))
    # return filtered_df

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
        base.transform_aggregate(total="sum(data)", groupby=["AxisName"])
        .mark_text(dy=-10)
        .encode(
            text=alt.Text("total:Q").format(NUMBER_FORMAT),
            x=alt.X("AxisName:N").sort(),
            y="total:Q",
        )
    )

    text = (
        # val>, AxisName..
        base.mark_text(dx=40, align="left", dy=10).encode(
            # ONLY MARK those with certain height ..
            y=alt.Y("sum(data):Q").stack("zero"),
            x=alt.X("AxisName:N").sort(),  # n
            detail="AxisName:N",  # f"{col.ELEMENT}:N",
            text=alt.Text(f"{SHOW_LABEL}:N"),
            color=f"{col.ELEMENT}:N",
        )
    )
    chart = bar + total + text  # )  # .facet(column="AxisName:N")

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
        color=alt.Color(f"{col.CUSTOM_CATEGORY}:N").legend(labelLimit=500).sort(),
    )

    text = (
        post_base.transform_aggregate(
            Total="sum(data)", groupby=[f"{col.CUSTOM_CATEGORY}", "AxisName"]
        )
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
        )  # TODO give numbers so can sort by this explicitly..
    )

    return chart_fx(base)


def make_stack_compare_figure(
    project_name: ProjectNames,
    base_exp_num: int,
    alt_exp_num: int,
    renderer: RendererTypes = BROWSER,
    filter_categories: list[UseCategories] = [],
    filter_elements: list[str] = [],
    chart_fx: CHART_GRAPH_FX = stacked_graph,
):
    alt.renderers.enable(renderer)
    clmt_path = CLMTPath(project_name)
    df = prep_df(
        project_name, base_exp_num, alt_exp_num, filter_categories, filter_elements
    )
    chart = plot_stack_compare(df, chart_fx)
    categ_names = "_".join([i.name for i in filter_categories])
    if renderer == HTML:
        fig_name = f"exp{base_exp_num}_{alt_exp_num}_{categ_names}_stack_compare.png"
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()
    return chart


if __name__ == "__main__":
    alt.theme.enable("scape")

    # make_stack_compare_figure(
    #     "bpcr",
    #     2,
    #     3,
    #     renderer=BROWSER,
    #     chart_fx=simplifed_graph,
    # )
    make_stack_compare_figure(
        "pier_6",
        2,
        3,
        renderer=BROWSER,
        filter_elements=["Concrete Hardscape"],
        # TODO plot simple 
    )

    # rprint("Hello!")
