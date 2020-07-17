import os


def makedocs():
    # Workaround until Poetry supports tasks or scripts
    # Ideally this would be setup in pyproject.toml as

    # [tool.poetry.scripts]
    # build_docs = "(cd docs && make html)"

    os.system("(cd docs && make html)")
