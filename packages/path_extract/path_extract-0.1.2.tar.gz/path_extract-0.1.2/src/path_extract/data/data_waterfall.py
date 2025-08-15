from path_extract.constants import Columns
from path_extract.data.utils import print_whole_df
from path_extract.plots.helpers.constants import get_exp_df
from path_extract.utils import set_difference
from path_extract.data.data_compare import (
    get_names,
    check_elements,
    check_sums,
    get_diff,
    print_names_ordered,
    calc_diff,
)

import polars as pl
from rich import print as rprint

from path_extract.project_paths import ProjectNames


def initial_join(base: pl.DataFrame, alt: pl.DataFrame):
    df = base.join(
        alt,
        on=[
            Columns.SECTION.name,
            Columns.TYPE.name,
            Columns.CATEGORY.name,
            Columns.ELEMENT.name,
            Columns.UNIT.name,
            Columns.CUSTOM_CATEGORY.name,
        ],
        how="left",
        suffix="_ALT",
    )

    return df


def secondary_extend(intermed: pl.DataFrame, base: pl.DataFrame, alt: pl.DataFrame):
    def get_missing_from_base():
        names_in_joined = get_names(intermed, Columns.ELEMENT.name)
        alt_names = get_names(alt, Columns.ELEMENT.name)
        return set_difference(alt_names, names_in_joined)

    missing_from_base = get_missing_from_base()

    df_to_add = (
        alt.filter(pl.col(Columns.ELEMENT.name).is_in(missing_from_base))
        .with_columns(pl.col(Columns.VALUE.name).alias(Columns.VALUE_ALT.name))
        .with_columns(pl.lit(0, dtype=pl.Int64).alias(Columns.VALUE.name))
    )
    return intermed.extend(df_to_add).fill_null(0)


def compare_two_experiments(
    project_name: ProjectNames, base_exp_num: int, alt_exp_num: int, ALL=False
):
    base = get_exp_df(project_name, base_exp_num)
    alt = get_exp_df(project_name, alt_exp_num)
    # rprint(base.head())

    # print_names_ordered(base, "base")

    intermed = initial_join(base, alt)
    # print_names_ordered(intermed, "intermed")
    df = secondary_extend(intermed, base, alt)

    check_elements(df, base, alt, name_col=Columns.ELEMENT.name)
    check_sums(
        df, base, alt, val1_col=Columns.VALUE.name, val2_col=Columns.VALUE_ALT.name
    )

    if ALL:
        return df.sort(
            by=[
                Columns.CUSTOM_CATEGORY.name,
                Columns.ELEMENT.name,
            ]  # TODO sort by use category..
        )

    # rprint(d)

    with_diff = calc_diff(
        df, val1_col=Columns.VALUE.name, val2_col=Columns.VALUE_ALT.name
    )
    return get_diff(with_diff).sort(
        by=[
            Columns.CUSTOM_CATEGORY.name,
            Columns.VALUE_DIFF.name,
            Columns.ELEMENT.name,
        ]  # TODO sort by use category..
    )


if __name__ == "__main__":
    # d = compare_two_experiments("pier_6", 1, 0)
    # rprint(get_diff(d))
    d = compare_two_experiments("pier_6", 2, 1)
    print_whole_df(get_diff(d))
