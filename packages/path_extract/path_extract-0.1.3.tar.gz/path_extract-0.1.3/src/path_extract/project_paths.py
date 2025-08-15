from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from path_extract.file_utils import read_csv
from path_extract.paths import PATH_TO_FIGURES, PATH_TO_INPUTS
from path_extract.file_utils import get_path_subdirectories
from enum import StrEnum, Enum

# TODO move clmt pilot stuff to folder.. / make super object if have many ..
CLMT_PROJECTS = "250701_CLMT_Pilot_Sprint"
CLMT_PROJECTS_INPUTS = PATH_TO_INPUTS / CLMT_PROJECTS


class DataType(Enum):
    OVERVIEW = 1
    BREAKDOWN = 2


# class ProjectNames(StrEnum):
#     PIER_6 = "pier_6"


# DataTypes = Literal["Breakdown", "Overview"]
ProjectNames = Literal["pier_6", "newtown_creek", "bpcr", "saginaw"]
# BREAKDOWN = 2
# OVERVIEW = 1
PILOT_PROJECTS = [
    "pier_6",
    "newtown_creek",
]  # TODO can use path lib to get names.. TODO make enum?
INFO = "info.json"


def EXP(x):
    return f"exp_{x}"


def HTML(x):
    return Path("html") / f"_{x}.html"


def CSV(x):
    return f"_{x}.csv"


def get_exp_num_from_path(exp_path: Path):
    res = exp_path.stem.split("_")
    return int(res[1])


@dataclass
class CLMTPath:
    name: ProjectNames

    @property
    def input_path(self):
        p = PATH_TO_INPUTS / CLMT_PROJECTS / self.name
        assert p.exists(), f"{self.name} does not exist in {CLMT_PROJECTS}!"
        return p

    @property
    def figures_path(self):
        # TODO might not exist, make it if it doesnt.. -> put function in utils.py
        # TODO local and presentation paths ..
        p = PATH_TO_FIGURES / CLMT_PROJECTS / self.name
        if not p.exists():
            p.mkdir()
        return p

    @property
    def experiment_paths(self):
        dirs = get_path_subdirectories(self.input_path)
        return dirs

    def get_experiment_path(self, experiment_num):
        p = self.input_path / EXP(experiment_num)
        assert p.exists(), f"No experiment with {experiment_num} exists!"
        return p

    def get_json(self, experiment_num: int):
        return self.get_experiment_path(experiment_num) / INFO

    def get_html(self, experiment_num: int, datatype: DataType = DataType.BREAKDOWN):
        # TODO wrapper function to test for existence..
        return self.get_experiment_path(experiment_num) / HTML(datatype.value)

    def get_csv(self, experiment_num: int, datatype: DataType = DataType.BREAKDOWN):
        return self.get_experiment_path(experiment_num) / CSV(datatype.value)

    def read_csv(self, experiment_num: int, datatype: DataType = DataType.BREAKDOWN):
        return read_csv(self.get_csv(experiment_num, datatype))

    @property
    def get_all_experiment_nums(self):
        return [get_exp_num_from_path(i) for i in self.experiment_paths]

    def get_all_experiment_csvs(self):
        experiment_nums = [get_exp_num_from_path(i) for i in self.experiment_paths]
        return [self.read_csv(i, DataType.BREAKDOWN) for i in experiment_nums]
