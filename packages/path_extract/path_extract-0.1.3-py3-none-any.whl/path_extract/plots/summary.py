from path_extract.plots.breakdown.elements import plot_elements
from path_extract.extract.breakdown import read_breakdown
from path_extract.constants import (
    ClassNames,
    Columns,
    Emissions,
    Headings,
)
import polars as pl
import altair as alt


from path_extract.examples import (
    SAMPLE_CLMT_BREAKDOWN_HTML,
)


# group by category


def plot_experiment_summary(
    df: pl.DataFrame, title: str, renderer="browser", show=False
):
    # TODO should be making its own dataframe edits..
    alt.renderers.enable(renderer)
    res = df.group_by(ClassNames.TYPE.name).agg(pl.col(ClassNames.VALUE.name).sum())
    # rprint(res)
    df2 = (
        res.transpose(column_names=ClassNames.TYPE.name)
        .select([Headings.EMBODIED_CARBON_EMISSIONS.value, Headings.BIOGENIC.value])
        .rename(
            {
                Headings.EMBODIED_CARBON_EMISSIONS.value: Emissions.EMBODIED.name,
                Headings.BIOGENIC.value: Emissions.BIOGENIC.name,
                # "Operational Emissions": Emissions.OPERATIONAL.name
                # Headings.OPERATIONAL.value: Emissions.OPERATIONAL.name,
            }
        )
        .with_columns(
            (pl.col(Emissions.EMBODIED.name) + pl.col(Emissions.BIOGENIC.name)).alias(
                "TOTAL"
            )
        )
    )
    df3 = df2.unpivot(variable_name=Columns.NAME.name, value_name=ClassNames.VALUE.name)

    # rprint(df3)

    chart = (
        alt.Chart(df3, title=title)
        .mark_bar()
        .encode(
            x=alt.X(Columns.NAME.name).title("Emissions Type"),
            y=alt.Y(ClassNames.VALUE.name).title(
                "Equivalent Carbon Emissions [kg-Co2-e]"
            ),
            color=alt.Color(Columns.NAME.name).title("Emissions Type"),
            tooltip=[
                Columns.NAME.name,
                alt.Tooltip(ClassNames.VALUE.name, format=".2s"),
            ],
        )
    )
    return chart


# TODO move this elsewhere..
if __name__ == "__main__":
    df = read_breakdown(SAMPLE_CLMT_BREAKDOWN_HTML)
    chart = plot_elements(df, "example")
    chart.show()
    # map_use_category_colors(edit_breakdown_df(df))
