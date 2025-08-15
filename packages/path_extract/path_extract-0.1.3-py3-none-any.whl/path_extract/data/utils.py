import polars as pl
from rich import print as rprint
from path_extract.data.categories.use_categories import UseCategories
import path_extract.data.columns as col


def print_whole_df(df, dfname=""):
    with pl.Config(tbl_rows=-1):
        rprint(f"{dfname}: {df}")


def add_category_label(df: pl.DataFrame):
    return df.with_columns(
        pl.col(col.CUSTOM_CATEGORY)
        .str.replace_all("_", " ")
        .str.to_titlecase()
        .alias(col.CUSTOM_CATGEORY_LABEL)
    )


def filter_df(
    df: pl.DataFrame,
    filter_categories: list[UseCategories] = [],
    filter_elements: list[str] = [],
):
    categ_expr = pl.col(col.CUSTOM_CATEGORY).is_in([i.name for i in filter_categories])

    # TODO add categories properly, here, temp chamge 
    element_expr = pl.col(col.CATEGORY).str.contains_any([i for i in filter_elements])

    if filter_categories and filter_elements:
        return df.filter(categ_expr & element_expr)  # .filter(element_expr)
    elif filter_categories:
        return df.filter(categ_expr)
    elif filter_elements:
        return df.filter(element_expr)
    else:
        return df
