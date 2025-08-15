import pyprojroot


BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))


PATH_TO_INPUTS = BASE_PATH / "inputs"
PATH_TO_FIGURES = BASE_PATH / "figures"

SAMPLE_HTML = PATH_TO_INPUTS / "sample" / "sample.html"

