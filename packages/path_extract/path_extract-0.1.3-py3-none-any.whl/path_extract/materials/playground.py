from typing import NamedTuple
import polars as pl
import altair as alt
from path_extract.materials.data import playground_alts
from rich import print as rprint

from path_extract.plots.helpers.constants import BROWSER, RendererTypes


# original -> epdm safety surface..

NAME = "name"
VALUE = "value"


def prep_df():
    data = {
        NAME: [i.name for i in playground_alts],
        VALUE: [i.value for i in playground_alts],
    }
    df = pl.DataFrame(data).sort(by=VALUE)
    rprint(df)
    return df


def plot_material(
    df,
    renderer: RendererTypes = BROWSER,
):
    alt.renderers.enable(renderer)
    base = alt.Chart(df).encode(
        x=f"{VALUE}:Q", y=alt.Y(f"{NAME}:N").sort(None), text=f"{VALUE}:Q"
    )
    chart = base.mark_bar() + base.mark_text(align="left", dx=2)
    chart.show()


def make_material_plot():
    df = prep_df()
    plot_material(df)
    # TODO save


if __name__ == "__main__":
    alt.theme.enable("scape")
    make_material_plot()
