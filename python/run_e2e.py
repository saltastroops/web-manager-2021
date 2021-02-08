import os
from subprocess import call

# Based on
# https://stackoverflow.com/questions/32757765/conditional-commands-in-tox-tox-travis-ci-and-coveralls

if __name__ == "__main__":
    if "GITHUB_ACTIONS" not in os.environ:
        return_code = call(["npx", "cypress", "run"], cwd="../e2e")
        raise SystemExit(return_code)
    else:
        print("Skipping end-to-end tests")  # noqa
