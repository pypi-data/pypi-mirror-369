# read the html for each project
# create csvs for each
# create a master csv..
from path_extract.extract.breakdown import read_breakdown
from path_extract.project_paths import CLMTPath, EXP, CSV
from path_extract.file_utils import get_path_files
from rich import print as rprint
from path_extract.file_utils import read_csv
import polars as pl

PROJECTS = "projects"
BPCR = "bpcr"
HTML_DIR = "html"
CSV_DIR = "csv"
# TODO this probably shouldnt be in here since it is a one off thing..


def read_bpcr_projects_to_csv():
    clmt_path = CLMTPath(BPCR).input_path
    path_to_projects = clmt_path / PROJECTS / HTML_DIR
    path_to_csv = clmt_path / PROJECTS / CSV_DIR
    assert path_to_csv.exists()
    rprint(path_to_projects)
    assert path_to_projects.exists()
    projects = get_path_files(path_to_projects)
    for path in projects:
        rprint(path)
        df = read_breakdown(path)
        csv_name = f"{path.stem}.csv"
        df.write_csv(path_to_csv / csv_name)


def prep_projects():
    clmt_path = CLMTPath(BPCR).input_path
    path_to_csv = clmt_path / PROJECTS / CSV_DIR
    assert path_to_csv.exists()
    csvs = get_path_files(path_to_csv)
    data = {i.stem: read_csv(i) for i in csvs}
    return data
    rprint(data)


def combine_bpcr_projects():
    def make_exp(names, exp_num):
        dfs = [data[i] for i in names]
        new_df = pl.concat(dfs)
        # concat the dataframes
        save_path = clmt_path / EXP(exp_num) / CSV(2)
        new_df.write_csv(save_path)
        # skipping the json for now, but is helpful for knowing what is what , this fx will provide documentation

    # read all files  into dataframes
    data = prep_projects()
    rprint(data.keys())
    clmt_path = CLMTPath(BPCR).input_path
    make_exp(["soils", "planting", "paving", "tree_removal"], 0)
    make_exp(["soils", "planting_and_hardscape", "tree_removal"], 1)
    make_exp(["planting_base"], 2)
    make_exp(["planting_prop"], 3)

    # choose the ones that would like and make experiment
    pass


if __name__ == "__main__":
    read_bpcr_projects_to_csv()
    combine_bpcr_projects()
    # df = read_breakdown(SAMPLE_CLMT_BREAKDOWN_HTML)
    # rprint(df)
    # # f = get_breakdown_comparison(df)
    # # rprint(f)
