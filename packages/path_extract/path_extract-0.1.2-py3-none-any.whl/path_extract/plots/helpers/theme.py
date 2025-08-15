import altair as alt

CLEARVIEW = "ClearviewText"
FONT = f'{CLEARVIEW}, system-ui, -apple-system, BlinkMacSystemFont, ".SFNSText-Regular", sans-serif'
FONT_SIZE = 14
LABEL_FONT_SIZE = 12
FONT_COLOR = "#161616"
LABEL_COLOR = "#525252"
DEF_WIDTH = 350


category_pallete = [
    "#5c898a",
    "#022B3A",
    "#52AA5E",
    "#976391",
    "#F7996E",
    "#B28B84",
    "#6D696A",
]
scape_categ_pallete = [
    "#008080",
    "#007373",
    "#006666",
    "#005959",
    "#004c4c",
    "#004040",
    "#003434",
    "#002929",
]

brown_pallete = [
"#008080",
"#3c8570",
"#5e8764",
"#7a895e",
"#938960",
"#a7896b",
"#b58b7c",
"#bc8f8f",
]


@alt.theme.register("scape", enable=True)
def scape() -> alt.theme.ThemeConfig:
    return {
        "config": {
            "view": {
                "width": 350,
                "height": 280,
            },
            "axis": {
                "labelColor": LABEL_COLOR,
                "labelFontSize": LABEL_FONT_SIZE,
                "labelFont": FONT,
                "labelFontWeight": 400,
                "titleColor": FONT_COLOR,
                "titleFontWeight": 400,
                "titleFontSize": FONT_SIZE,
                "titleFont": FONT,
            },
            "axisX": {"titlePadding": 10},
            "axisY": {"titlePadding": 2.5},
            "text": {"font": FONT, "fontSize": FONT_SIZE},
            "range": {
                "ordinal": {"scheme": "teals"},
                "category": category_pallete,
                "sequential": {"scheme": "teals"},
                "diverging": {"scheme": "brownbluegreen"},
            },  # type: ignore
            "legend": {
                "labelFont": FONT,
                "labelFontSize": LABEL_FONT_SIZE,
                "labelLimit": 500,
            },
        }
    }
