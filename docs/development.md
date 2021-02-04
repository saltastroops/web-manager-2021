# Developing the Web Manager

This page outlines how to develop the Web Manager.

## Requirements

The following must be installed on your machine.

* [Python](https://www.python.org) 3.9.0 or higher
* [Poetry](https://python-poetry.org) 1.1.0 or higher
  
In case you are using the Docker image, you probably need a Linux or macOS machine, and you certainly need Docker:

* [Docker](https://www.docker.com) 20.10.0 or higher

## Installation

Clone the repository.

```shell
git clone git@github.com:saltastroops/web-manager-2021.git web-manager
```

Go to the Python directory and install the required packages.

```shell
cd web-manager/python
poetry install
```

## Running the server

You can now run the server.

```shell
# in web-manager/python

uvicorn --reload --port 8001 app.main:app
```

!!!tip
    Note the non-default port. This has been chosen as the development documentation server (MkDocs) is listening on port 8000.

However, you can also use the provided Makefile to launch it.

```shell
# in web-manager

make start
```

## Formatting and Testing

The Makefile provides various rules for formatting and testing.

* Formatting the code: `make black`
* Sorting the import statements: `make isort`
* Checking styling: `make flake8`
* Checking types: `make mypy`
* Checking for security issues: `make bandit`
* Running pytest: `make pytest`
* Showing code coverage: `make coverage`
* Running formatting and other tests: `make test`
* Running tox: `make tox`

## Documentation

The documentation is created with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). You can start a development server for viewing the documentation either by executing

```shell
# in web-manager

mkdocs serve
```

or by using the Makefile.

```shell
# in web-manager

make mkdocs
```
