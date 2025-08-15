from rich import print as rprint
from path_extract.data.data_compare import get_names
from path_extract.data.data_compare import get_expected_elements
from path_extract.data.data_waterfall import compare_two_experiments
from path_extract.utils import are_sets_equal
from path_extract.data.data_compare import (
    create_examples,
    compare_two_datafames_simple,
)
from path_extract.constants import Columns
import polars as pl
import pytest


@pytest.fixture()
def examples():
    return create_examples()


def test_small_baseline_df(examples):
    baseline, small_alt, _ = examples
    df = compare_two_datafames_simple(baseline, small_alt)
    df_names = get_names(df)
    rprint(df_names)
    expected_names = get_expected_elements(baseline, small_alt)
    assert are_sets_equal(df_names, expected_names)


# @pytest.mark.skip()
def test_large_baseline_df(examples):
    baseline, _, large_alt = examples
    df = compare_two_datafames_simple(baseline, large_alt)
    df_names = get_names(df)
    expected_names = get_expected_elements(baseline, large_alt)
    assert are_sets_equal(df_names, expected_names)


@pytest.fixture()
def df_and_rev(examples):
    baseline, _, large_alt = examples
    df = compare_two_datafames_simple(baseline, large_alt)
    reverse_df = compare_two_datafames_simple(large_alt, baseline)
    return df, reverse_df


def test_reverse(df_and_rev):
    df, reverse_df = df_and_rev
    df_names = get_names(df)
    reverse_names = get_names(reverse_df)
    assert are_sets_equal(df_names, reverse_names)


def get_values(df: pl.DataFrame, rev=False):
    lst = df[Columns.VALUE_DIFF.name].unique().to_list()
    if rev:
        return [-1 * i for i in lst]
    return lst


def test_reverse_values(df_and_rev):
    df, reverse_df = df_and_rev
    rev_vals = get_values(reverse_df, True)
    vals = get_values(df)
    assert are_sets_equal(vals, rev_vals)

    # the columns in the final df should be the union ..


@pytest.mark.parametrize("project_name", ["pier_6", "newtown_creek"])
def test_reveres(project_name):
    d10 = compare_two_experiments(project_name, 1, 0)
    d01 = compare_two_experiments(project_name, 0, 1)
    d10_vals = get_values(d10)
    d01_vals = get_values(d01, rev=True)
    assert are_sets_equal(d10_vals, d01_vals)


if __name__ == "__main__":
    # rprint(baseline, small_alt, large_alt)
    # rprint(get_expected_elements(baseline, large_alt))
    pass
