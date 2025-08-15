from enum import StrEnum
from rich import print as rprint
from path_extract.project_paths import CLMT_PROJECTS_INPUTS, CLMTPath, ProjectNames
from path_extract.constants import ClassNames, Headings, Columns
from pathlib import Path
from path_extract.utils import chain_flatten
from path_extract.file_utils import read_csv
import polars as pl

from path_extract.file_utils import get_path_subdirectories

# TODO get list of all categories from all projects
# map them to new categories associated with the use


def get_categories():
    def get_project_data(project: Path) -> list[pl.DataFrame]:
        clmt_path = CLMTPath(project.stem)  # type: ignore # TODO fix this type issue -> names should probably be an enum
        csv_paths = clmt_path.get_all_experiment_csvs()
        return [pl.DataFrame(read_csv(i)) for i in csv_paths]

    def get_values_across_dataframes(dataframes: list[pl.DataFrame], column_name: str):
        values = chain_flatten(
            [
                i.filter(
                    pl.col(ClassNames.SECTION.name) == Headings.CARBON_IMPACT.value
                )[column_name].unique(maintain_order=True)
                for i in dataframes
            ]
        )

        return list(set(values))

    projects = get_path_subdirectories(CLMT_PROJECTS_INPUTS)
    dataframes = chain_flatten([get_project_data(i) for i in projects])

    # rprint(len(dataframes))
    # rprint(dataframes[1].filter(pl.col(ClassNames.SECTION.name) == Headings.CARBON_IMPACT.value))

    # categories =
    categories = get_values_across_dataframes(dataframes, ClassNames.CATEGORY.name)

    # # rprint([i[ClassNames.CATEGORY.name].unique() for i in dataframes])

    rprint(categories)

    # get all projects
    # fore each project, get all csvs (run if have not already been run)
    # get the materials list


if __name__ == "__main__":
    r = get_categories()
    # rprint(r)
