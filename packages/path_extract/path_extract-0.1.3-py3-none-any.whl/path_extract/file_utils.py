import polars as pl
import json
from pathlib import Path


# TODO combine this repetion! BUt also make sure do have both behaviors ... maybe try to consolidate?
def read_csv(path: Path, file_name: str | None = None):
    if file_name:
        _path = path / file_name
    else:
        _path = path
    assert _path.exists(), f"{_path} does not exist!"
    return pl.read_csv(_path)


def read_json(path: Path, file_name: str | None = None):
    if file_name:
        _path = path / file_name
    else:
        _path = path
    assert _path.exists(), f"{_path} does not exist!"
    with open(_path, "r") as f:
        data = json.load(f)
        # print(data)
        return data


def get_path_subdirectories(path: Path):
    return [i for i in path.iterdir() if i.is_dir]


def get_path_files(path: Path):
    return [
        i for i in path.iterdir() if i.is_file() and not i.stem.startswith(".")
    ]  # ignore hidden files..
