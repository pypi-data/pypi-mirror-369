from path_extract.project_paths import CLMTPath, DataType


SAMPLE_CLMT_PATH = CLMTPath("pier_6")
SAMPLE_CLMT_OVERVIEW_HTML = SAMPLE_CLMT_PATH.get_html(0, DataType.OVERVIEW)
SAMPLE_CLMT_BREAKDOWN_HTML = SAMPLE_CLMT_PATH.get_html(0, DataType.BREAKDOWN)
