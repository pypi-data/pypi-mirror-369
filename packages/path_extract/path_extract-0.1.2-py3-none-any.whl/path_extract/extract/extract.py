from path_extract.extract.breakdown import get_breakdown_comparison, read_breakdown
from path_extract.extract.overview import get_overview_comparison, read_overview
from path_extract.project_paths import (
    DataType,
    HTML,
    CLMTPath,
    get_exp_num_from_path,
)
from rich import print as rprint
import sys


# TODO create csvs for breakdown only..


def create_csvs_for_project(clmt_path: CLMTPath):
    rprint(f"-------EXTRACTING CSVS FOR {clmt_path.input_path.stem}-----------------")
    def make_breakdown():
        html = exp_dir / HTML(DataType.BREAKDOWN.value)
        rprint(f"html is {html}")
        df = read_breakdown(html)
        return df, get_breakdown_comparison(df)

    def make_overview():
        html = exp_dir / HTML(DataType.OVERVIEW.value)
        df = read_overview(html)
        return df, get_overview_comparison(df)

    for exp_dir in clmt_path.experiment_paths:
        exp_num = get_exp_num_from_path(exp_dir)

        breakdown_df, breakdown_comp = make_breakdown()

        try:
            overview_df, overview_comp = make_overview()
        except Exception:
            rprint(
                f"The Overview HTML for {exp_num} of {clmt_path.name} is invalid.. Writing only the breakdown csv "
            )
            breakdown_df.write_csv(clmt_path.get_csv(exp_num, DataType.BREAKDOWN))
            continue

        assert overview_comp == breakdown_comp, (
            f"Invalid comparisons! Breakdown: {breakdown_comp}. Overview: {overview_comp}"
        )
        breakdown_df.write_csv(clmt_path.get_csv(exp_num, DataType.BREAKDOWN))
        overview_df.write_csv(clmt_path.get_csv(exp_num, DataType.OVERVIEW))


if __name__ == "__main__":
    n = len(sys.argv)
    if n == 2:
        project = sys.argv[1]
    else:
        project = "newtown_creek"
    rprint(f"project to process: {project}")
    clmt_path = CLMTPath(
        project
    )  # TODO fix the literal.. => do some checks on the class
    create_csvs_for_project(clmt_path)
