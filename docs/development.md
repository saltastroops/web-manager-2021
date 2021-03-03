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

All settings for the Web Manager must be provided as environment variables, or in an `.env` file at the project's root level. _Remember that the `.env` file must **never** be put under version control._

You can find the list of settings in the module `app.settings`; each property of the `Settings` class corresponds to an environment variable. The names aren't case-sensitive; so, for example, the property `secret_key` can be defined in an environment variable `SECRET_KEY`. Talking of secret keys, any secret key should be generated with `openssl`.

```shell
openssl rand -hex 32
```

## Running the server

You can now run the server.

```shell
# In web-manager/python

uvicorn --reload --port 8001 app.main:app
```

!!!tip
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

## End-to-end tests

The end-to-end tests require the server to run, but the Makefile commands for running the tests (`cypress` and `end2end`) do not launch it. So you have to start the server yourself. The server must be listening on port 8001.

In case you need to skip the end-to-end tests when running tox, you can set the environment variable SKIP_E2E to any non-empty value. This is done for the Github Action workflows.

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
  href="{{ url_for('static', path='css/login.css') | autoversion }}"
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
