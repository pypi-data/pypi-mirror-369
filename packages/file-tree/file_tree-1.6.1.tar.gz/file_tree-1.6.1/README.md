[![PyPI - Downloads](https://img.shields.io/pypi/dm/file-tree)](https://pypi.org/project/file-tree/)
[![Documentation](https://img.shields.io/badge/Documentation-file--tree-blue)](https://open.win.ox.ac.uk/pages/fsl/file-tree/)
[![Documentation](https://img.shields.io/badge/Documentation-fsleyes-blue)](https://open.win.ox.ac.uk/pages/fsl/fsleyes/fsleyes/userdoc/filetree.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6576809.svg)](https://doi.org/10.5281/zenodo.6576809)
[![Pipeline status](https://git.fmrib.ox.ac.uk/fsl/file-tree/badges/master/pipeline.svg)](https://git.fmrib.ox.ac.uk/fsl/file-tree/-/pipelines)
[![Coverage report](https://git.fmrib.ox.ac.uk/fsl/file-tree/badges/master/coverage.svg)](https://open.win.ox.ac.uk/pages/fsl/file-tree/htmlcov)

Framework to represent structured directories in python as FileTree objects. FileTrees can be read in from simple text files describing the directory structure. This is particularly useful for pipelines with large number of input, output, and intermediate files. It can also be used to visualise the data in structured directories using FSLeyes or `file-tree` on the command line.

- General documentation: https://open.win.ox.ac.uk/pages/fsl/file-tree/
- FSLeyes documentation on using FileTrees: https://open.win.ox.ac.uk/pages/fsl/fsleyes/fsleyes/userdoc/filetree.html

# Setting up local development environment
This package uses [uv](https://docs.astral.sh/uv/) for project management.
You will need to install uv to develop this package.

First clone the repository:
```shell
git clone https://git.fmrib.ox.ac.uk/fsl/file-tree.git
```

Then we can ask uv to set up the local envoriment.
```shell
cd file-tree
uv sync
```

## Running tests
Tests are run using the [pytest](https://docs.pytest.org) framework.
This will already be available in the `uv` virtual environment.
```shell
uv run pytest src/tests
```

## Compiling documentation
The documentation is build using [sphinx](https://www.sphinx-doc.org/en/master/).
```shell
cd doc
uv run sphinx-build source build
open build/index.html
```

## Contributing
[Merge requests](https://git.fmrib.ox.ac.uk/fsl/file-tree/-/merge_requests) with any bug fixes or documentation updates are always welcome.

For new features, please raise an [issue](https://git.fmrib.ox.ac.uk/fsl/file-tree/-/issues) to allow for discussion before you spend the time implementing them.

## Releasing new versions
- Ensure CHANGELOG.md is up to date.
    - All commits can be seen in gitlab by clicking the "Unreleased" link in "CHANGELOG.md"
    - Add new header just below "## [Unreleased]" with the new version
    - Update the footnotes for both the new version and [Unreleased]
- Edit the version number on `pyproject.toml`
- Create a new tag for the version number
- Push to gitlab (including tags)
    - Check the tagged pipeline to see if it successfully uploaded file-tree to [pypi](https://pypi.org/project/file-tree/).
- Upload code on conda-forge using their automated release detection.

## Running tests
Tests are run using the [pytest](https://docs.pytest.org) framework. After installation (`pip install pytest`) they can be run from the project root as:
```shell
pytest src/tests
```
