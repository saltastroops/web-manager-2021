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
* Running end-to-end tests: `make e2e`
* Launching the Cypress test runner: `make cypress`
* Running formatting and other tests: `make test`
* Running tox: `make tox`

## Making use of the git pre-commit hook

As forgetting to format code or run tests is human, but having to deal with failing GitHub actions is not fun, it is advisable to use git hooks to ensure whatever should be in place is in place before pushing your changes.

For example, you can create a file `.git/hooks/pre-commit` with the content

```shell
make black
make isort
```

and make it executable,

```shell
# in web-manager

chmod a+x .git/hooks/pre-commit
```

!!! warning
    If you forget to make the file executable, the hook will just not be executed, without any error raised.

Similarly you can add pre-push hook by creating a file `.git/hooks/pre-push` with the content

```shell
make test
```

Remember to make this file executable.

```shell
# in web-manager

chmod a+x .git/hooks/pre-push
```

!!! note
    In particular the pre-commit hook is *not* effective, as it formats *all* files, not just the committed ones. Also, it does not commit any reformatted code; so after the commit you may have new changes to commit...

## End-to-end tests

The end-to-end tests require the server to run, but the Makefile commands for running the tests (`cypress` and `end2end`) do not launch it. So you have to start the server yourself. The server must be listening on port 8001.

Due to their need to connect to a (somewhat) real database, no end-to-end tests are run by tox if executed as part of a GitHub Actions workflow. They are, however, run if you execute tox on your own machine.

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
