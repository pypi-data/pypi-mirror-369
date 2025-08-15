from path_extract.plots.helpers.constants import CARBON_EMIT_LABEL
from path_extract.project_paths import CLMTPath, ProjectNames
from path_extract.data.dataframes import edit_breakdown_df, get_net_emissions
import polars as pl
from rich import print as rprint
import altair as alt
from path_extract.plots.helpers.constants import (
    HTML,
    NUMBER_FORMAT,
    POINT_SIZE,
    save_fig,
    BROWSER,
)
from typing import NamedTuple, TypedDict
from prefixed import Float
from path_extract.plots.helpers.theme import scape, category_pallete, FONT_COLOR


from path_extract.plots.helpers.constants import RendererTypes, DEF_DIMENSIONS

EXP_NUM = "num"
EXP_NAME = "name"
VAL = "value"
FORMATTED_VALUE = "formatted_val"
X_CHANGE = "xchange"

BASELINE = "As Designed"
ALTERNATIVE = "Alternative"
EXPERIMENT_NAMES = "Experiment Names"


class ExpeMetaData(NamedTuple):
    num: int
    name: str


class MultiExperimentMetaData(TypedDict):
    num: list[int]
    name: list[str]


def create_multi_exp_dict(exps: list[ExpeMetaData]) -> MultiExperimentMetaData:
    return {EXP_NAME: [i.name for i in exps], EXP_NUM: [i.num for i in exps]}


def prep_df(project_name: ProjectNames, exps: list[ExpeMetaData]):
    def get_experiment_emissions(exp_num: int):
        return get_net_emissions(edit_breakdown_df(clmt_path.read_csv(exp_num)))

    clmt_path = CLMTPath(project_name)

    exp_meta_data = create_multi_exp_dict(exps)
    emissions = [get_experiment_emissions(i) for i in exp_meta_data[EXP_NUM]]

    res = dict({VAL: emissions}, **exp_meta_data)  # TODO want value sat the end?
    df = (
        pl.DataFrame(res)
        .with_columns(
            pl.col(VAL)
            .cumulative_eval(pl.element().last() / pl.element().first(), min_samples=2)
            .round_sig_figs(2)
            .alias(X_CHANGE)
        )
        .with_columns(pl.col(X_CHANGE).fill_null(0))
        .with_columns(
            pl.col(VAL).map_elements(lambda x: f"{Float(x):.2H}").alias(FORMATTED_VALUE)
        )
    )

    # rprint(df)
    return df


def plot_comparison(df: pl.DataFrame, renderer=BROWSER, y_datum=150, dx_multiplier=1.5):
    alt.renderers.enable(renderer)  # TODO make this a base fx..
    # need to compute where the text should be.. => halfway between the two values..

    font_size = 20
    font_size_plus = font_size + 10
    text_align = "left"

    chart = alt.Chart(df)

    line = (
        chart.mark_line(point=alt.OverlayMarkDef(size=POINT_SIZE))
        .encode(
            x=alt.X(f"{EXP_NAME}:O")
            .sort(None)
            .axis(labels=False)
            .title(EXPERIMENT_NAMES),
            y=alt.Y(f"{VAL}:Q").axis(format=NUMBER_FORMAT).title(CARBON_EMIT_LABEL),
            color=alt.value(category_pallete[0]),
        )
        .properties(**DEF_DIMENSIONS)
    )

    prc_change = (
        chart.transform_calculate(FormatChange="datum.xchange + 'x difference'")
        .encode(
            x=alt.datum(ALTERNATIVE),
            y=alt.value(y_datum),
            text=alt.Text("FormatChange:N"),
        )
        .mark_text(
            dx=dx_multiplier * font_size,
            fontSize=font_size_plus,
        )
        .transform_filter((alt.datum.xchange != 0))
    )

    init_dx = font_size
    init_dy = 0
    text_align = "left"

    label = (
        line.transform_calculate(
            label_name="split(datum.name + ':, '+ datum.formatted_val + ' kg-CO2-eq', ',')"
        )
        .encode(text=alt.Text("label_name:N"), color=alt.value(FONT_COLOR))
        .mark_text(
            lineBreak=r"\n",
            align=text_align,
            dx=init_dx,
            dy=init_dy,
            fontSize=font_size,
        )
    )

    chart = line + prc_change + label

    return chart


def make_dot_comparison_figure(
    project_name: ProjectNames,
    exp1_num: int,
    exp2_num: int,
    renderer: RendererTypes = BROWSER,
    y_datum: int = 150,
    dx_multiplier: float = 1.5,
    exp1_name=BASELINE,
    exp2_name=ALTERNATIVE,
):
    exp1 = ExpeMetaData(exp1_num, exp1_name)
    exp2 = ExpeMetaData(exp2_num, exp2_name)

    clmt_path = CLMTPath(project_name)
    df = prep_df(project_name, [exp1, exp2])
    chart = plot_comparison(df, renderer, y_datum, dx_multiplier)
    if renderer == HTML:
        fig_name = f"exp{exp1.num}_{exp2.num}_comparison.png"
        save_fig(chart, clmt_path, fig_name)
    else:
        chart.show()

    return chart


if __name__ == "__main__":
    # alt.theme.enable("carbonwhite")
    alt.theme.enable("scape")

    # as_designed = ExpeMetaData(0, BASELINE)
    # better_alt = ExpeMetaData(3, ALTERNATIVE)

    make_dot_comparison_figure("newtown_creek", 0, 3, renderer=BROWSER)
