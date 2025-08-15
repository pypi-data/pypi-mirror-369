from typing import Callable, get_args
from path_extract.data.categories.use_categories import UseCategories
from path_extract.plots.breakdown.categories import make_categorical_figure
from path_extract.plots.breakdown.elements import make_element_figure
from path_extract.plots.element_compare import make_element_compare_figure
from path_extract.plots.helpers.constants import HTML, clear_fig_path
from path_extract.plots.dot_compare import make_dot_comparison_figure
from path_extract.plots.stacked_compare import (
    make_stack_compare_figure,
    simplifed_graph,
)
from path_extract.plots.straight_compare import make_straight_compare_figure
from path_extract.plots.waterfall import make_waterfall_figure
from path_extract.plots.pie import make_pier_6_pie
import altair as alt
from path_extract.plots.helpers.theme import scape
from path_extract.project_paths import ProjectNames
import sys

# TODO: make function to reset figure paths..


def pier_6_figs():
    worse_alt = 0
    as_designed = 1
    landscape_only_as_designed = 2
    landscape_no_reuse = 3  # TODO!
    landscape_only_no_woodland = 4

    proj = "pier_6"
    clear_fig_path(proj)
    make_categorical_figure(proj, worse_alt, HTML)
    make_categorical_figure(proj, as_designed, HTML)
    make_categorical_figure(proj, landscape_only_as_designed, HTML)

    make_element_figure(
        proj,
        as_designed,
        renderer=HTML,
        filter_categories=[
            UseCategories.SUBSTRUCTURE,
            UseCategories.HARDSCAPE,
        ],
    )

    # sheet pile.
    make_stack_compare_figure(
        proj,
        as_designed,
        worse_alt,
        renderer=HTML,
          filter_categories=[UseCategories.SUBSTRUCTURE, UseCategories.HARDSCAPE],
        # TODO plot simple
    )
    
    make_straight_compare_figure(
        proj,
        as_designed,
        worse_alt,
        renderer=HTML,
          filter_categories=[UseCategories.SUBSTRUCTURE, UseCategories.HARDSCAPE],
        # TODO plot simple
    )

    # asphalt
    make_straight_compare_figure(
        proj,
        landscape_only_as_designed,
        landscape_no_reuse,
        renderer=HTML,
        filter_elements=["Concrete Hardscape"],
    )

    make_straight_compare_figure(
        proj,
        landscape_only_as_designed,
        landscape_no_reuse,
        renderer=HTML,
        filter_elements=["Concrete Hardscape"],
        chart_fx_str="simple",
    )

    # woodlands
    make_straight_compare_figure(
        proj,
        landscape_only_as_designed,
        landscape_only_no_woodland,
        renderer=HTML,
    )

    make_straight_compare_figure(
        proj,
        landscape_only_as_designed,
        landscape_only_no_woodland,
        renderer=HTML,
        chart_fx_str="simple",
    )

    #

    make_pier_6_pie(HTML)

    # make_comparison_figure(proj, as_designed, worse_alt, renderer=HTML)


def saginaw_figs():
    proj = "saginaw"
    as_designed = 0
    worse_alt = 1
    even_worse_alt = 2

    clear_fig_path(proj)
    make_categorical_figure(proj, as_designed, HTML)
    make_categorical_figure(proj, worse_alt, HTML)

    make_element_figure(
        proj,
        as_designed,
        HTML,
        filter_categories=[UseCategories.SITE_PREPARATION, UseCategories.DEMOLITION],
    )
    # make_categorical_figure(proj, worse_alt, HTML)

    make_stack_compare_figure(proj, as_designed, worse_alt, HTML)

    make_stack_compare_figure(proj, worse_alt, even_worse_alt, HTML)

    # make_comparison_figure(proj, as_designed, worse_alt, renderer=HTML)


def bpcr_figs():
    proj = "bpcr"
    as_designed = 0
    clear_fig_path("bpcr")
    make_categorical_figure("bpcr", as_designed, HTML)

    make_stack_compare_figure(
        "bpcr",
        2,
        3,
        HTML,
        chart_fx=simplifed_graph,
    )

    make_waterfall_figure(proj, 2, 3, HTML)
    make_element_figure(
        proj,
        as_designed,
        HTML,
        filter_categories=[
            UseCategories.NEW_PLANTING,
            UseCategories.NEW_PLANTING,
            UseCategories.DEMOLITION,
            UseCategories.SITE_PREPARATION,
        ],
    )

    make_element_compare_figure("bpcr", 0, renderer=HTML)


def newtown_creek_figs():
    as_designed = 0
    area = 1
    depth = 2
    both = 3
    categ = UseCategories.HARDSCAPE
    clear_fig_path("newtown_creek")

    make_categorical_figure("newtown_creek", as_designed, HTML)
    make_categorical_figure("newtown_creek", both, HTML)

    make_stack_compare_figure(
        "newtown_creek", as_designed, area, renderer=HTML, filter_categ=categ
    )
    make_stack_compare_figure(
        "newtown_creek", as_designed, depth, renderer=HTML, filter_categ=categ
    )
    make_stack_compare_figure(
        "newtown_creek", as_designed, both, renderer=HTML, filter_categ=categ
    )
    make_dot_comparison_figure("newtown_creek", as_designed, both, renderer=HTML)
    make_element_figure(
        "newtown_creek",
        0,
        renderer=HTML,
        filter_categories=[
            UseCategories.NEW_PLANTING,
            UseCategories.HARDSCAPE,
        ],
    )


fig_dict: dict[ProjectNames, Callable[[], None]] = {
    "pier_6": pier_6_figs,
    "bpcr": bpcr_figs,
    "saginaw": saginaw_figs,
    "newtown_creek": newtown_creek_figs,
}


if __name__ == "__main__":
    alt.theme.enable("scape")
    # pier_6_figs()
    # bpcr_figs()
    poss_projects = ["pier_6", "newtown_creek", "bpcr", "saginaw"]
    n = len(sys.argv)
    if n == 2:
        project = sys.argv[1]
        print(f"Prepareing figures for `{project}`")
    else:
        raise Exception(f"Choose a project in {poss_projects}!")

    assert project in poss_projects
    fx = fig_dict[project]  # type: ignore
    fx()
    # rprint(f"project to process: {project}")
