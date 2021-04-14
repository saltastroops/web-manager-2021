# Developing the Web Manager

This page outlines how to develop the Web Manager.

## Requirements

The following must be installed on your machine.

- [Python](https://www.python.org) 3.9.0 or higher
- [Poetry](https://python-poetry.org) 1.1.0 or higher

In case you are using the Docker image, you probably need a Linux or macOS machine, and you certainly need Docker:

- [Docker](https://www.docker.com) 20.10.0 or higher

## Installation

Clone the repository.

```shell
git clone git@github.com:saltastroops/web-manager-2021.git web-manager
```

!!! tip
    You may call the created directory whatever you want. However, the following instructions assume it is called `web-manager`.

Go to the directory `web-manager/python` and install the required packages.

```shell
cd web-manager/python
poetry install
```

!!! note
    In theory this is all you have to do. In practice you might have to jump through various hoops and loops to get the `cryptography` package installed. The [installation instructions](https://cryptography.io/en/latest/installation.html) may be of help, but you might still have to consult Google.

!!! note
    If you are using an IDE such as IntelliJ, you might have to mark the `python` folder as a sources root folder, as otherwise the IDE might complain about incorrect import statements.

## Settings

All settings for the Web Manager must be provided as environment variables or in a file. By default that file is the file `.env` in the server's root folder (i.e. in the `python` folder). However, you can choose another file by setting the environment variable `DOTENV_FILE`. _Remember that a file defining environment variables must **never** be put under version control._

The unit tests always use the file `.env.test` in the server's root folder, and you cannot change this file.

You can find the list of settings in the module `app.settings`; each property of the `Settings` class corresponds to an environment variable. The names aren't case-sensitive; so, for example, the property `secret_key` can be defined in an environment variable `SECRET_KEY`. Talking of secret keys, any secret key should be generated with `openssl`.

```shell
openssl rand -hex 32
```

!!! warning
    Never run the unit tests or end-to-end tests in production mode. Evil things might happen to your production database!

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

- Formatting the Python code: `make black`
- Sorting the Python import statements: `make isort`
- Checking styling: `make flake8`
- Checking types: `make mypy`
- Checking for security issues: `make bandit`
- Running pytest: `make pytest`
- Showing code coverage: `make coverage`
- Running end-to-end tests: `make end2end`
- Formatting the JavaScript code: `make prettier`
- Formatting staged JavaScript files: `make prettier-staged`
- Launching the Cypress test runner: `make cypress`
- Running formatting and other tests: `make test`
- Running tox: `make tox`

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
make prettier-staged
```

and make it executable,

```shell
# In web-manager

chmod a+x .git/hooks/pre-commit
```

!!! warning
    If you forget to make the file executable, the hook will just not be executed, without any error raised.
    
    Similarly you can add a pre-push hook by creating a file `.git/hooks/pre-push` with the content

```shell
make test
```

Remember to make this file executable.

```shell
# In web-manager

chmod a+x .git/hooks/pre-push
```

!!! note
    In particular the pre-commit hook is _not_ effective, as it formats _all_ files, not just the committed ones. Also, it does not commit any reformatted code; so after the commit you may have new changes to commit...

## Unit tests

`pytest` is used for the unit-testing, and all the test files are contained in the `tests` folder. The structure within this folder should mirror the structure within the `app` folder. The name of all files containing test functions must start with `test_`.

### Using a test database

If a unit test requires access to a (test) database, you should use the `db` fixture, which returns an `aiomysql` database pool. The DSN of the database must be set in the same environment variable `SDB_DSN` used by the server for setting the database connection parameters.

Any test function using the `db` fixture must be an async function and must be marked with `pytest.mark.asyncio`. This implies that you cannot use Starlette's test client (as, for example, provided by the `client` fixture) together with the `db` fixture.

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

## Styling

The base page template automatically loads the CSS file `static/global.css`, which defines styles that should apply across the website. In addition, it includes a block named `extra_css` which allows child templates to load additional CSS files, as shown in the following example.

```html
{% block extra_css %}
<link
  rel="stylesheet"
  href="{% raw %}{{ url_for('static', path='css/login.css') | autoversion }}{% endraw %}"
/>
{% endblock %}
```

Remember to use the `autoversion` filter to avoid caching issues.

The following rules should be followed when styling.

- Use the BEM naming scheme wherever reasonable.
- Avoid using id values in style rule selectors.
- Avoid using composite selectors.
- Every page should have its own CSS file, which is only loaded on that page. Styles which apply to multiple pages should be defined in a separate file. If they in principle apply to all pages, they should be defined in `static/global.css`.
- Variables should be used for all color values, and semantic colour variables are strongly preferred. For example, use `--color-success` rather than, say, `--green`.

## Adding JavaScript files

The base page template includes a block `extra_js` in which you can load JavaScript files, as shown in this example.

```html
{%raw %}{% block extra_js %}
<script src="{{ url_for('strict', 'js/salt-block-view.js') | autoversion }}"></script>
{% endblock %}{% endraw %}
```

Don't forget to use the `autoversion` filter to avoid caching issues.

## Jinja2 templates

The website is using Jinja2 for rendering content.

### Loading static files

In order to avoid caching issues, you should not load static files such as JavaScript files, stylesheets and images, you should not use the raw URLs of such files in a template. Instead, apply the `autoversion` filter. For example:

```html
<link
  rel="stylesheet"
  href="{% raw %}{{ url_for('static', path='/css/main.css') | autoversion }}{% endraw %}"
/>
```

The filter adds a query parameter `v` to the URL, whose value is the MD5 hash of the file to which the URL is pointing. This avoids caching issues.

### Adding custom template filters

Adding a Jinja2 template filter is a two-step process. First, you define your filter function in `app/jinja2/filters.py`. For example, here is a filter for cheering everyone up.

```python
def keepsmiling(text: str) -> str:
    return f"{text} 😀️"
```

Second, you register the filter in `app/routers/views.py`.

```python hl_lines="2 6"
from starlette.templating import Jinja2Templates
from app.jinja2.filters import keepsmiling

templates = Jinja2Templates(directory="templates")

templates.env.filters['keepsmiling'] = keepsmiling
```

You can then use your custom filter as you would any regular Jinja2 filter.

```html
<h1>{% raw %}{{ "Stay positive" | keepsmiling }}{% endraw %}</h1>
```

## Roles and permissions

Authorization should be done with `Permission` instances, which in turn use `Role` instances.

### Roles

The `app.util.role` module provides an abstract  base class `Role`, which all user role classes should extend. The extending class should not make any database query itself, but rather call a function from the module `app.service.user`. As an example, here is the implementation of the `Investigator` role.

```python
from aiomysql import Pool
from app.service import user as user_service
from app.util.role import Role

class Investigator(Role):
    """
    The role of being an investigator on a proposal.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_investigator(user, self.proposal_code, self.db)
```

Once you have a `Role` instance, you can use its `is_assigned_to` method to check whether a user has that role. Alternatively, you can use the user's `has_role_of` method. As a guideline, the `has_role_of` method should be preferred.

```python
investigator = Investigator("2020-2-SCI-017", db)

is_investigator = investigator.is_assigned_to(user)

# alternatively (and preferred):
is_investigator = user.has_role_of(investigator)
```

If you need to check whether a user has any of a list of multiple roles, you should call the user's `has_any_role_of` method.

```python
salt_astronomer = SaltAstronomer(db)
salt_operator = SaltOperator(db)
is_salt_astronmomer_or_operator = user.has_any_role_of(salt_astronomer, salt_operator)
```

It might be tempting to user these methods for directly checking authorization. However. you shouldn't. Authorization should always be checked with the user's `is_permitted_to` method, as discussed in the next section.

### Permissions

The `app.util.permission` module provides an abstract base class `Permission`, which all permission classes should extend. All permissions should be defined in terms of user roles. As an example, here is the implementation of the `ViewProposal`class.

```python
from aiomysql import Pool

from app.models.pydantic import User
from app.util import role
from app.util.permission import Permission

class ViewProposal(Permission):
    """
    Permission to view a proposal.

    A user may view a proposal if at least one of the following is true.

    - The user is an investigator on the proposal.
    - The user is a SALT Astronomer.
    - The user is a SALT Operator.
    - The user is a SALT Engineer.
    - The user is a TAC member for a partner from which the proposal has requested time.
    - The user is an administrator.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_permitted_for(self, user: User) -> bool:
        """Check whether a user has the permission."""

        roles = [role.Investigator(self.proposal_code, self.db),
                 role.SaltAstronomer(self.db),
                 role.SaltOperator(self.db),
                 role.SaltEngineer(self.db),
                 role.ProposalTacMember(self.proposal_code, self.db),
                 role.Administrator(self.db)
                 ]

        return await user.has_any_role_of(roles)
```

Once you have a `Permission` instance, you can use its `is_permitted_for` method to check whether a user has the permission. Alternatively, you can call the user's `is_permitted_to` method. As a guideline, the `is_permitted_to` method should be preferred.

```python
view_proposal = ViewProposal("2020-2-SCI-034", db)

may_view_proposal = view_proposal.is_permitted_for(user)

# alternatively (and preferred):
may_view_proposal = user.is_permitted_to(view_proposal)
```
