import polars as pl
from path_extract.data.categories.use_categories import UseCategories
from path_extract.constants import ClassNames, Columns
from path_extract.vega_colors import get_dict_of_colors
from path_extract.vega_colors import VegaColors


use_category_map: dict[UseCategories, VegaColors] = {
    UseCategories.PRESERVED_PLANTING: "greens",
    UseCategories.DEMOLITION: "browns",  # orange
    UseCategories.SITE_PREPARATION: "yellowOrangeBrown",  # orange
    UseCategories.SUBSTRUCTURE: "warmGreys",  # brown
    UseCategories.HARDSCAPE: "greys",  # grey
    UseCategories.NEW_PLANTING: "greens",
    UseCategories.GREEN_INFRA: "teals",
    UseCategories.ACCESSORIES: "darkGold",  # pink
    UseCategories.OPERATIONS: "purples",  # yellow
}


def map_use_category_colors(df: pl.DataFrame):
    domains = df[ClassNames.CATEGORY.name].unique(maintain_order=True).to_list()
    range_ = []

    dict_of_colors = get_dict_of_colors()

    category_groups = df.group_by(
        [ClassNames.CATEGORY.name, Columns.CUSTOM_CATEGORY.name],
        maintain_order=True,
    ).agg()

    for row in category_groups.iter_rows(named=True):
        use_category_name = row[Columns.CUSTOM_CATEGORY.name]
        color_scheme = use_category_map[UseCategories[use_category_name]]
        curr_color = next(dict_of_colors[color_scheme])
        range_.append(curr_color)

    return domains, range_


def map_use_category_colors_to_elements(df: pl.DataFrame):
    domains = df[ClassNames.ELEMENT.name].unique(maintain_order=True).to_list()
    range_ = []

    dict_of_colors = get_dict_of_colors()

    category_groups = df.group_by(
        [ClassNames.ELEMENT.name, Columns.CUSTOM_CATEGORY.name],
        maintain_order=True,
    ).agg()

    for row in category_groups.iter_rows(named=True):
        use_category_name = row[Columns.CUSTOM_CATEGORY.name]
        color_scheme = use_category_map[UseCategories[use_category_name]]
        curr_color = next(dict_of_colors[color_scheme])
        range_.append(curr_color)

    return domains, range_
