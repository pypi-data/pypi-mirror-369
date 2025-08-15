from pathlib import Path
from path_extract.extract.breakdown import read_breakdown
from path_extract.data.dataframes import edit_breakdown_df

def create_carbon_df(html_file: Path):
    assert html_file.suffix == ".html"
    # going to assume the file exists if we are getting it from marimo .. 
    df = read_breakdown(html_file)
    return edit_breakdown_df(df)

# TODO use dataframely or patito to assign types to this data.. cr

PIER_6_BREAKDOWN = r"C:\Users\juliet.intern\_SCAPECode\path_extract\inputs\250701_CLMT_Pilot_Sprint\pier_6\exp_0\html\_2.html"

if __name__ == "__main__":
    test_file = Path(PIER_6_BREAKDOWN)
    df = create_carbon_df(test_file)
    print(df)