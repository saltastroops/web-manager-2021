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

!!! tip
    You may call the created directory whatever you want. However, the following instructions assume it is called `web-manager`.

Go to the directory  `web-manager/python` and install the required packages.

```shell
cd web-manager/python
poetry install
```

!!! note
    In theory this is all you have to do. In practice you might have to jump through various hoops and loops to get the `cryptography` package installed. The [installation instructions](https://cryptography.io/en/latest/installation.html) may be of help, but you might still have to consult Google.

!!! note
    If you are using an IDE such as IntelliJ, you might have to mark the `python` folder as a sources root folder, as otherwise the IDE might complain about incorrect import statements.

## Settings

All settings for the Web Manager must be provided as environment variables, or in an `.env` file at the project's root level. _Remember that the `.env` file must **never** be put under version control._

You can find the list of settings in the module `app.settings`; each property of the `Settings` class corresponds to an environment variable. The names aren't case-sensitive; so, for example, the property `secret_key` can be defined in an environment variable `SECRET_KEY`. Talking of secret keys, any secret key should be generated with `openssh`.

```shell
openssl rand -hex 32
```

## Running the server

You can now run the server.

```shell
# In web-manager/python

uvicorn --reload --port 8001 app.main:app
```

!!! tip
    Note the non-default port. This has been chosen as the development documentation server (MkDocs) is listening on port 8000.

However, you can also use the provided Makefile to launch it.

```shell
# In web-manager

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

## Using a test database

For development purposes the easiest choice is to work with a copy of the SALT Science Database (SDB). But there are cases where just using a copy is not ideal, and a database without sensitive information is called for. Notable examples are unit tests checking against database content and screen shots for the documentation.

To facilitate the creation of such a test database there is a command line tool `createtestdb` which clones a source database (which should be a copy of the SDB) and then replaces sensitive information in the new database with fake data.

This tool is installed automatically when you run `poetry install`. It takes the following options.

Command line option | Description | Required?
--- | --- | ---
--help | Output a help message | No
--source-db-host | Host of the source database | Yes
--source-db-name | Name of the source database | Yes
--source-db-password | Password of the source database user account | No
--source-db-user | Username of the source database user account | Yes
--test-db-host | Host of the test database | Yes
--test-db-name | Name of the test database | Yes
--test-db-password | Password of the test database user account | No
--test-db-user | Username of the test database user account | Yes

While the password options are not required, you will be prompted for the passwords if you don't include them.

When running the `createtestdb` command, you might get an error stating that the definer 'abcd'@'some_host' does not exist (obviously with a username and host other than 'abcd' and 'some_host'). In this case, you should create the missing user in MySQL and grant the user full privileges.

```mysql
CREATE USER 'abcd'@'some_host' IDENTIFIED BY 'some_strong_password';
GRANT ALL ON *.* TO 'abcd'@'some_host';
```

The following sensitive information is replaced.

* The username in the `PiptUser` table.
* The first name, surname, email address and phone number in the `Investigator` table.
* The right ascension and declination in the `TargetCoordinates` table.

!!! warning
    While these details should be the most sensitive ones, this does not mean that the resulting database should be considered public. Indeed, you should consider it as confidential as the SDB, and you should only share it with people with whom you would be comfortable sharing the SDB itself.

## Making use of the git pre-commit hook

As forgetting to format code or run tests is human, but having to deal with failing GitHub actions is not fun, it is advisable to use git hooks to ensure whatever should be in place is in place before pushing your changes.

For example, you can create a file `.git/hooks/pre-commit` with the content

```shell
make black
make isort
```

and make it executable,

```shell
# In web-manager

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
# In web-manager

chmod a+x .git/hooks/pre-push
```

!!! note
    In particular the pre-commit hook is *not* effective, as it formats *all* files, not just the committed ones. Also, it does not commit any reformatted code; so after the commit you may have new changes to commit...

## End-to-end tests

The end-to-end tests require the server to run, but the Makefile commands for running the tests (`cypress` and `end2end`) do not launch it. So you have to start the server yourself. The server must be listening on port 8001.

In case you need to skip the end-to-end tests when running tox, you can set the environment variable `SKIP_E2E` to any non-empty value. This is done for the Github Action workflows.

## Documentation

The documentation is created with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). You can start a development server for viewing the documentation either by executing

```shell
# In web-manager

mkdocs serve
```

or by using the Makefile.

```shell
# In web-manager

make mkdocs
```
