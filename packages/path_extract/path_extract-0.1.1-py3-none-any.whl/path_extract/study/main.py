from path_extract.extract.extract import create_csvs_for_project
from path_extract.plots import (
    plot_elements,
    plot_experiment_summary,
)
from path_extract.data.dataframes import edit_breakdown_df
from path_extract.constants import ExperimentInfo
from path_extract.file_utils import read_csv
from path_extract.file_utils import read_json
from path_extract.plots.breakdown.categories import plot_use_categories
from path_extract.project_paths import CLMTPath, get_exp_num_from_path, DataType

import altair as alt


def read_exp_info(clmt_path: CLMTPath, experiment_num: int):
    data: ExperimentInfo = read_json(clmt_path.get_json(experiment_num))
    return f"{data['project']} -- {data['experiment']}"


def get_experiment_data(clmt_path: CLMTPath, experiment_num: int, renderer="browser"):
    name = read_exp_info(clmt_path, experiment_num)
    df = clmt_path.read_csv(experiment_num, DataType.BREAKDOWN)
    df_to_plot = edit_breakdown_df(df)
    return df_to_plot, name


# TODO this is all very redundant...
def plot_all_summaries(clmt_path: CLMTPath, renderer="browser"):
    charts = []
    for path in clmt_path.experiment_paths:
        exp_num = get_exp_num_from_path(path)
        df, name = get_experiment_data(clmt_path, exp_num, renderer)
        chart = plot_experiment_summary(df, name, renderer)
        charts.append(chart)
    all_chart = alt.hconcat(*charts).resolve_scale(y="shared").resolve_legend()
    return all_chart


def plot_all_use_categories(clmt_path: CLMTPath, renderer="browser"):
    charts = []
    for path in clmt_path.experiment_paths:
        exp_num = get_exp_num_from_path(path)
        df, name = get_experiment_data(clmt_path, exp_num, renderer)
        chart = plot_use_categories(df, name, renderer)
        charts.append(chart)
    all_chart = (
        alt.hconcat(*charts)
        .resolve_scale(y="shared")
        .resolve_legend()
        .configure_legend(orient="left", direction="vertical")
    )
    return all_chart


def plot_all_elements(clmt_path: CLMTPath, renderer="browser"):
    charts = []
    for path in clmt_path.experiment_paths:
        exp_num = get_exp_num_from_path(path)
        df, name = get_experiment_data(clmt_path, exp_num, renderer)
        chart = plot_elements(df, name, renderer)  # TODO
        charts.append(chart)
    all_chart = (
        alt.hconcat(*charts)
        .resolve_scale(y="shared")
        .resolve_legend()
        .configure_legend(
            orient="bottom", columns=5, symbolLimit=100, direction="vertical"
        )
    )
    return all_chart


# TODO rename -> analysis nb


# TODO compare overview of project experiments.. -> calc byself?

if __name__ == "__main__":
    clmt_path = CLMTPath("pier_6")
    # create_csvs_for_project(clmt_path) # TODO run automatically if csvs dont exist..
    # chart = plot_all_project_experiments(clmt_path)
    # chart.show()

    chart = plot_all_use_categories(clmt_path)
    chart.show()
