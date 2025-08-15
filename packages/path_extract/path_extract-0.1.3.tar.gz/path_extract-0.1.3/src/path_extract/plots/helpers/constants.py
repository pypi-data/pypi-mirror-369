from typing import Literal, TypedDict

from path_extract.project_paths import CLMTPath, DataType, ProjectNames
from path_extract.data.dataframes import edit_breakdown_df
import altair as alt
from path_extract.file_utils import get_path_files


## Markers
POINT_SIZE = 1000


## Axes
DIAGONAL_LABEL_ANGLE = -20 # chart..configure_axisX(labelAngle=0)
HORIZONTAL_LABEL_ANGLE = 0
NUMBER_FORMAT = ".2s"
NUMBER_FORMAT_3 = ".3s"

# asxis label names
CARBON_EMIT_LABEL = "Equivalent Carbon Emissions [kg-Co2-e]"
AS_DESIGNED = "As Designed"
ALTERNATIVE = "Alternative"
EXPERIMENT_NAMES = "Experiment Names"
AXIS_NAMES = "Axis Names"

# Size of the plot
class Dimensions(TypedDict):
    width: int
    height: int


DEF_DIMENSIONS: Dimensions = {"width": 340, "height": 300}


## Rendering
RendererTypes = Literal["browser", "html"]
BROWSER = "browser"
HTML = "html"


# TODO share with pres works
def get_exp_df(
    project_name: ProjectNames,
    exp_num: int,
):
    clmt_path = CLMTPath(project_name)
    init_df = clmt_path.read_csv(exp_num)
    return edit_breakdown_df(init_df)

def get_exp_df_overview(
    project_name: ProjectNames,
    exp_num: int,
):
    clmt_path = CLMTPath(project_name)
    init_df = clmt_path.read_csv(exp_num, DataType.OVERVIEW)
    return init_df


# Saving figs
PPI = 200
IMG_FORMAT = "png"


def save_fig(
    chart: alt.Chart | alt.LayerChart | alt.HConcatChart | alt.ConcatChart | alt.FacetChart,
    clmt_path: CLMTPath,
    fig_name: str,
):
    chart.save(clmt_path.figures_path / fig_name, format=IMG_FORMAT, ppi=PPI)


def clear_fig_path(project_name: ProjectNames):
    clmt_path = CLMTPath(project_name)
    files = get_path_files(clmt_path.figures_path)
    for f in files:
        f.unlink()



