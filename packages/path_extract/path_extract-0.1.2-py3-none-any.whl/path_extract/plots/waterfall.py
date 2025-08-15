import altair as alt
import polars as pl
from rich import print as rprint
from path_extract.constants import Columns
from enum import StrEnum
from pathlib import Path

from path_extract.plots.helpers.constants import CARBON_EMIT_LABEL
from path_extract.project_paths import CLMTPath, ProjectNames
from path_extract.data.dataframes import (
    edit_breakdown_df,
    get_net_emissions,
)
from path_extract.plots.helpers.constants import (
    HTML,
    NUMBER_FORMAT_3,
    get_exp_df,
    BROWSER,
    save_fig,
)
from path_extract.plots.helpers.constants import RendererTypes
from path_extract.data.data_waterfall import compare_two_experiments
from path_extract.plots.helpers.theme import scape

FINAL_VALUE = 0
LABEL_ANGLE = -20
NUMBER_FORMAT = ".2s"


class wfc(StrEnum):  # WaterfallColumns
    AMOUNT = "amount"
    LABEL = "label"
    BEGIN = "Baseline"
    END = "Alternative"
    X_LABEL = "Elements"
    Y_LABEL = "Amount"


def prep_df(
    project_name: ProjectNames, baseline_exp_num: int, alternative_exp_num: int
):
    df = (
        compare_two_experiments(project_name, baseline_exp_num, alternative_exp_num)
        .rename(
            # NOTE: this is the point where can make decisions about what goes on the axis..
            {Columns.ELEMENT: wfc.LABEL, Columns.VALUE_DIFF: wfc.AMOUNT}
        )
        .select(wfc.LABEL, wfc.AMOUNT)
    )
    baseline = get_exp_df(project_name, baseline_exp_num)
    init = pl.DataFrame(
        {wfc.LABEL: wfc.BEGIN.value, wfc.AMOUNT: get_net_emissions(baseline)}
    )
    end = pl.DataFrame({wfc.LABEL: wfc.END.value, wfc.AMOUNT: FINAL_VALUE})

    df2 = pl.concat([init, df, end])
    # rprint(df2)

    return df2


def plot_waterfall(df: pl.DataFrame, renderer: RendererTypes = BROWSER):
    alt.renderers.enable(renderer)
    # values
    amount = alt.datum.amount
    label = alt.datum.label
    window_lead_label = alt.datum.window_lead_label
    window_sum_amount = alt.datum.window_sum_amount

    # Define frequently referenced/long expressions
    calc_prev_sum = alt.expr.if_(label == wfc.END.value, 0, window_sum_amount - amount)
    calc_amount = alt.expr.if_(label == wfc.END.value, window_sum_amount, amount)
    calc_text_amount = alt.expr.if_(
        (label != wfc.BEGIN.value) & (label != wfc.END.value) & calc_amount > 0,
        "+",
        "",
    ) + alt.expr.format(calc_amount, NUMBER_FORMAT)

    format_sum_dec = alt.expr.if_(
        alt.datum.calc_sum_dec != "",
        alt.expr.format(alt.datum.calc_sum_dec, NUMBER_FORMAT),
        "",
    )
    format_sum_inc = alt.expr.if_(
        alt.datum.calc_sum_inc != "",
        alt.expr.format(alt.datum.calc_sum_inc, NUMBER_FORMAT),
        "",
    )
    # The "base_chart" defines the transform_window, transform_calculate, and X axis
    base_chart = (
        alt.Chart(df)
        .transform_window(
            window_sum_amount="sum(amount)",
            window_lead_label="lead(label)",
        )
        .transform_calculate(
            calc_lead=alt.expr.if_(
                (window_lead_label == None), label, window_lead_label
            ),
            calc_prev_sum=calc_prev_sum,
            calc_amount=calc_amount,
            calc_text_amount=calc_text_amount,
            calc_center=(window_sum_amount + calc_prev_sum) / 2,
            calc_sum_dec=alt.expr.if_(
                window_sum_amount < calc_prev_sum, window_sum_amount, ""
            ),
            calc_sum_inc=alt.expr.if_(
                window_sum_amount > calc_prev_sum, window_sum_amount, ""
            ),
        )
        .transform_calculate(
            format_sum_dec=format_sum_dec,
            format_sum_inc=format_sum_inc,
        )
        .encode(
            x=alt.X(
                "label:O",
                axis=alt.Axis(
                    title=wfc.X_LABEL.value, labelAngle=LABEL_ANGLE, labelFontSize=10
                ),
                sort=None,
            )
        )
    )

    color_coding = (
        alt.when((label == wfc.BEGIN.value) | (label == wfc.END.value))
        .then(alt.value("#878d96"))
        .when(calc_amount < 0)
        .then(alt.value("#24a148"))
        .otherwise(alt.value("#fa4d56"))
    )

    bar = base_chart.mark_bar(size=45).encode(
        y=alt.Y("calc_prev_sum:Q").title(CARBON_EMIT_LABEL).axis(format=NUMBER_FORMAT),
        y2=alt.Y2("window_sum_amount:Q"),
        color=color_coding,
    )

    # The "rule" chart is for the horizontal lines that connect the bars
    rule = base_chart.mark_rule(xOffset=-22.5, x2Offset=22.5).encode(
        y="window_sum_amount:Q",
        x2="calc_lead",
    )

    # Add values as text
    text_pos_values_top_of_bar = base_chart.mark_text(baseline="bottom", dy=-4).encode(
        text=alt.Text("format_sum_inc:N"),
        y="calc_sum_inc:Q",
    )

    text_neg_values_bot_of_bar = base_chart.mark_text(baseline="top", dy=4).encode(
        text=alt.Text("format_sum_dec:N"),
        y="calc_sum_dec:Q",
    )
    text_bar_values_mid_of_bar = base_chart.mark_text(
        baseline="middle", fontSize=10
    ).encode(
        text=alt.Text("calc_text_amount:N"),  #
        y="calc_center:Q",
        color=alt.value("white"),
    )

    chart = (
        alt.layer(
            bar,
            rule,
            text_pos_values_top_of_bar,
            text_neg_values_bot_of_bar,
            text_bar_values_mid_of_bar,
        )
        .properties(width=800, height=450)
        .configure_axisX(labelAngle=LABEL_ANGLE)
    )

    return chart


def make_waterfall_figure(
    project_name: ProjectNames,
    base_exp_num: int,
    alt_exp_num: int,
    renderer: RendererTypes = BROWSER,
):
    clmt_path = CLMTPath(project_name)
    df = prep_df(project_name, base_exp_num, alt_exp_num)
    chart = plot_waterfall(df)
    if renderer == HTML:
        fig_name = f"exp{base_exp_num}_{alt_exp_num}_waterfall.png"
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()
    return chart


if __name__ == "__main__":
    alt.theme.enable("scape")
    make_waterfall_figure("newtown_creek", 0, 1)
    # df = prep_dataframe("newtown_creek", 0, 1)
    # chart = plot_waterfall(df)
    # chart.show()
