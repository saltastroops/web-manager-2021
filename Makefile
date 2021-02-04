.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
        from urllib import pathname2url
except:
        from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
        match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
        if match:
                target, help = match.groups()
                print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

bandit:
	cd python; bandit -r app

clean: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

coverage: ## check code coverage quickly with the default Python
	cd python; pytest --cov-report html
	$(BROWSER) htmlcov/index.html

black: ## format code with black
	cd python; black app tests

flake8: ## check style with flake8
	cd python; flake8 app tests

isort: ## sort import statements with isort
	cd python; isort app tests

mkdocs: ## start development documentation server
	mkdocs serve

mypy: ## check types with mypy
	cd python; mypy --config-file mypy.ini .

pytest: ## run tests quickly with the default Python
	cd python; pytest

start: ## start the development server
	cd python; uvicorn --reload --port 8001 app.main:app

test: ## run various tests
	cd python; mypy --config-file mypy.ini .
	cd python; bandit -r app
	cd python; flake8
	cd python; isort --check .
	cd python; black --check .
	cd python; pytest

tox: ## run tests on every Python version with tox
	cd python; tox
