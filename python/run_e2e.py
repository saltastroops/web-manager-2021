import os
from subprocess import call

# Based on
# https://stackoverflow.com/questions/32757765/conditional-commands-in-tox-tox-travis-ci-and-coveralls

if __name__ == "__main__":
    if not os.environ.get("SKIP_E2E"):
        return_code = call(["npx", "cypress", "run"], cwd="../e2e")
        raise SystemExit(return_code)
    else:
        print("Skipping end-to-end tests")  # noqa
