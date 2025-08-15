import altair as alt
from path_extract.plots.helpers.constants import (
    BROWSER,
    CARBON_EMIT_LABEL,
    HORIZONTAL_LABEL_ANGLE,
    RendererTypes,
    get_exp_df_overview,
    AS_DESIGNED,
    ALTERNATIVE,
    AXIS_NAMES,
)
from rich import print as rprint
import path_extract.data.columns as col
from path_extract.constants import Emissions

from path_extract.plots.waterfall import NUMBER_FORMAT
from path_extract.project_paths import ProjectNames
import polars as pl


def prep_df(
    project_name: ProjectNames,
    exp1: int,
    exp2: int,
):
    df1 = get_exp_df_overview(project_name, exp1)
    df2 = get_exp_df_overview(project_name, exp2)

    expr = (pl.col(col.NAME) == Emissions.BIOGENIC.value) | (
        pl.col(col.NAME) == Emissions.STORAGE.value
    )
    d = (
        df1.filter(expr)
        .join(df2, on=[col.NAME], suffix=col.SUFFIX)
        .unpivot(
            on=[col.VALUE, col.VALUE_ALT],
            index=[col.NAME],
            variable_name=col.KEY,
            value_name=col.DATA,
        )
        .with_columns(
            pl.when(pl.col(col.KEY) == col.VALUE)
            .then(pl.lit(AS_DESIGNED))
            .otherwise(pl.lit(ALTERNATIVE))
            .alias(AXIS_NAMES)
        )
    )
    rprint(d)
    return d


def plot_seq(
    df: pl.DataFrame,
    renderer: RendererTypes = BROWSER,
):
    alt.renderers.enable(renderer)
    base = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{AXIS_NAMES}:N").sort().title(None),
            y=alt.Y(f"{col.DATA}:Q")
            .axis(format=NUMBER_FORMAT)
            .title(CARBON_EMIT_LABEL),
            color=alt.Color(f"{AXIS_NAMES}:N").legend(None),
        )
    )

    text = base.encode(
        text=alt.Text(f"{col.DATA}:Q").format(NUMBER_FORMAT),
        x=alt.X(f"{AXIS_NAMES}:N").sort(),
        y=alt.Y(f"{col.DATA}:Q"),
        color=alt.value("black")
    ).mark_text(dy=-10)

    chart = (base + text).facet(column=f"{col.NAME}:N",).configure_axisX(labelAngle=HORIZONTAL_LABEL_ANGLE)

    chart.show()


if __name__ == "__main__":
    alt.theme.enable("scape")
    df = prep_df("pier_6", 2, 4)
    plot_seq(df)
