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

black: ## format code with black
	cd python; black app tests

clean: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

coverage: ## check code coverage quickly with the default Python
	cd python; pytest --cov-report html:../htmlcov --cov=app tests/
	$(BROWSER) htmlcov/index.html

cypress: ## launch the Cypress test runner
	cd e2e; npx cypress open

end2end: ## run end-to-end tests
	cd e2e; npx cypress run

flake8: ## check style with flake8
	cd python; flake8 app tests

isort: ## sort import statements with isort
	cd python; isort app tests

mkdocs: ## start development documentation server
	mkdocs serve

mypy: ## check types with mypy
	cd python; mypy --config-file mypy.ini .

prettier: ## format JavaScript code
	cd e2e; npx prettier --write cypress

prettier-staged: ## format staged JavaScript files
	cd e2e; npm run pretty-quick:staged

pytest: ## run tests quickly with the default Python
	cd python; pytest

start: ## start the development server
	cd python; uvicorn --reload --port 8001 app.main:app

test: ## run various tests (but no end-to-end tests)
	cd python; poetry run mypy --config-file mypy.ini .
	cd python; poetry run bandit -r app
	cd python; poetry run flake8
	cd python; poetry run isort --check .
	cd python; poetry run black --check .
	cd python; poetry run pytest
	cd e2e; npx prettier --check cypress
	cd e2e; npm run cypress:run

tox: ## run tests on every Python version with tox
	cd python; tox
