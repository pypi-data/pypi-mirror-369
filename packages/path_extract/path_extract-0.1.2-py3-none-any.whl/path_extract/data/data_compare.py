from enum import StrEnum
from typing import NamedTuple
from rich import print as rprint
import polars as pl

from path_extract.constants import Columns
from path_extract.utils import are_sets_equal, set_difference, set_union

# TODO this will all be deleted, just to help figure stuff out --> or moved to tests..

NAME = "name"
VAL = "val"
VAL2 = "val2"


class Fruit(StrEnum):
    GRAPES = "grapes"
    APPLES = "apples"
    PEARS = "pears"
    ORANGES = "oranges"
    PEACHES = "peaches"


class FruitPair(NamedTuple):
    fruit: str
    value: float


pairs = [
    FruitPair(i.value, k)
    for i, k in [
        (Fruit.GRAPES, 10.0),
        (Fruit.APPLES, 14.0),
        (Fruit.PEARS, 12.0),
        (Fruit.ORANGES, 8.0),
        (Fruit.PEACHES, 12.0),
    ]
]


def create_df(pairs: list[FruitPair], mult=1.0):
    return pl.DataFrame(
        {NAME: [i.fruit for i in pairs], VAL: [i.value * mult for i in pairs]}
    )




def create_examples():
    baseline = create_df(pairs[0:3])
    small_alt = create_df(pairs[0:2], mult=0.5)
    large_alt = create_df(pairs, mult=2)
    return baseline, small_alt, large_alt


def get_names(df: pl.DataFrame, name_col=NAME):
    return df[name_col].unique().to_list()


def get_expected_elements(base: pl.DataFrame, alt: pl.DataFrame, name_col=NAME):
    return set_union(get_names(base, name_col), get_names(alt, name_col))


def check_elements(
    joined_df: pl.DataFrame, base: pl.DataFrame, alt: pl.DataFrame, name_col=NAME
):
    expected_names = get_expected_elements(base, alt, name_col)
    joined_names = get_names(joined_df, name_col)
    are_sets_equal(expected_names, joined_names)


def check_sums(
    joined_df: pl.DataFrame,
    base: pl.DataFrame,
    alt: pl.DataFrame,
    val1_col=VAL,
    val2_col=VAL2,
):
    try:
        assert joined_df[val1_col].sum() == base[val1_col].sum()
        assert joined_df[val2_col].sum() == alt[val1_col].sum()
    except AssertionError:
        rprint(f"Mismatch: Joined DF: {joined_df}.  ")


def print_names_ordered(df: pl.DataFrame, df_name: str = "Test"):
    with pl.Config(tbl_rows=-1):
        rprint(f"{df_name}: {df[Columns.ELEMENT.name].unique().sort()}")


def calc_diff(
    df: pl.DataFrame, val1_col=VAL, val2_col=VAL2, val_diff_col=Columns.VALUE_DIFF.name
):
    return df.with_columns((pl.col(val2_col) - pl.col(val1_col)).alias(val_diff_col))


def get_diff(df: pl.DataFrame):
    return df.filter(pl.col(Columns.VALUE_DIFF.name) != 0)


def compare_two_datafames_simple(base: pl.DataFrame, alt: pl.DataFrame):
    df = base.join(alt, on=[NAME], how="left", suffix="2")

    names_in_joined = get_names(df)
    alt_names = get_names(alt)
    missing_from_base = set_difference(alt_names, names_in_joined)
    df_to_add = (
        alt.filter(pl.col(NAME).is_in(missing_from_base))
        .with_columns(pl.col(VAL).alias(VAL2))
        .with_columns(val=pl.lit(0.0))
    )

    rprint(f"df_to_add: {df_to_add}")

    d = df.extend(df_to_add).fill_null(0.0)

    check_sums(d, base, alt)
    check_elements(d, base, alt)

    diffed =  calc_diff(d)
    rprint(f"diffed: {diffed}")
    return diffed


if __name__ == "__main__":
    baseline, small_alt, large_alt = create_examples()
    df_pair = (large_alt, baseline)
    rprint("baseline+alt", *df_pair)
    r = compare_two_datafames_simple(*df_pair)
    rprint(r)
