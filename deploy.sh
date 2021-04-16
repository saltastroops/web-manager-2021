#!/bin/bash

DEFAULT_DEVELOPMENT_GIT_BRANCH='development'
DEFAULT_ENV_FILE='.env.deployment'
DEFAULT_PRODUCTION_GIT_BRANCH='production'

# Text colors (see https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux)
RED=$(tput setaf 1)
AMBER=$(tput setaf 3)
GREEN=$(tput setaf 2)
RESET=$(tput sgr0)

# Deploy the Web Manager.
#
# USAGE: deploy.sh [-p] [-b GIT_BRANCH] [-e ENV_FILE]

# Exit with a usage message and an error status.
usage() {
  echo "USAGE: ${0} [-p] [-b GIT_BRANCH] [-e ENV_FILE]" >&2
  echo >&2
  echo '-b: Git branch to use (default: development or main, depending on whether' >&2
  echo '    the script is called with the -p option.' >&2
  echo '-e: Environment variable file to read in (default: python/.env). The' >&2
  echo '    variables of the file are used to figure where to deploy to, but they' >&2
  echo '    are not used on the deployment server, whivh must have its own .env' >&2
  echo '    file.' >&2
  echo '-p: Deploy to a production server (not supported yet)' >&2
}

# Exit with an error message and an error status.
exit_on_error() {
  echo "${RED}ERROR:${RESET} ${1}" >&2
  exit 1
}

# Check whether a variable is set and exit with an error message abnd an error status
# if it isn't.
check_env_variable_set() {
  VARIABLE_NAME="${1}"
  if [[ -z "${!VARIABLE_NAME}" ]]   # use indirection
  then
    exit_on_error "Environment variable not set: ${VARIABLE_NAME}"
  fi
}

# Parse the command line options
ENV_FILE=${DEFAULT_ENV_FILE}
while getopts b:e:p OPTION
do
  case ${OPTION} in
  b) GIT_BRANCH=${OPTARG} ;;
  e) ENV_FILE=${OPTARG} ;;
  p) PRODUCTION='true' ;;
  ?)
    echo "${RED}ERROR:${RESET} Illegal option" >&2
    echo
    usage
    exit 1
    ;;
  esac
done

# Deployment to a production server is not supported yet
if [[ -n "${PRODUCTION}" ]]
then
  exit_on_error "Deployment to a production server is not supported yet."
fi

# Use the default value if no git branch has been supplied
echo
if [[ -z "${GIT_BRANCH}" ]]
then
  if [[ -n "${PRODUCTION}" ]]
  then
    GIT_BRANCH='main'
  else
    GIT_BRANCH='development'
  fi
fi

echo "Branch: ${GIT_BRANCH}"
echo "Env file: ${ENV_FILE}"

# Warn the user if the environment file does not exist
if [[ ! -e "${ENV_FILE}" ]]
then
  echo "${AMBER}WARNING:${RESET} Environment variable file does not exist: ${ENV_FILE}" >&2
fi

# Read in the environment variables
# shellcheck source=/dev/null
. "${ENV_FILE}" &> /dev/null

# Check that the required environment variables exist
if [[ -n "${PRODUCTION}" ]]
then
  check_env_variable_set 'PRODUCTION_SERVER_HOST'
  check_env_variable_set 'PRODUCTION_SERVER_USER'
  check_env_variable_set 'PRODUCTION_SERVER_PROJECT_ROOT'
else
  check_env_variable_set 'DEVELOPMENT_SERVER_HOST'
  check_env_variable_set 'DEVELOPMENT_SERVER_USER'
  check_env_variable_set 'DEVELOPMENT_SERVER_PROJECT_ROOT'
fi

# Set the variables for remote access
if [[ -n "${PRODUCTION}" ]]
then
  REMOTE_HOST="${PRODUCTION_SERVER_HOST}"
  REMOTE_USER="${PRODUCTION_SERVER_USER}"
  REMOTE_PROJECT_ROOT="${PRODUCTION_SERVER_PROJECT_ROOT}"
else
  REMOTE_HOST="${DEVELOPMENT_SERVER_HOST}"
  REMOTE_USER="${DEVELOPMENT_SERVER_USER}"
  REMOTE_PROJECT_ROOT="${DEVELOPMENT_SERVER_PROJECT_ROOT}"
fi

# Deploy the server
ssh "${REMOTE_USER}@${REMOTE_HOST}" << HERE
cd "${REMOTE_PROJECT_ROOT}" || {
   echo "Could not change to directory: ${REMOTE_PROJECT_ROOT}"
   exit 1
}
git fetch || {
  echo 'git fetch failed' >&2
  exit 1
}
git checkout "${GIT_BRANCH}" || {
  echo "git branch could not be checked out: ${GIT_BRANCH}" >&2
  exit 1
}
git pull || {
  echo 'git pull failed' >&2
  exit 1
}
cd python || {
  echo 'Could not change into directory: $(pwd)/python' >&2
  exit 1
}
docker-compose down || {
  echo 'docker-compose down failed' >&2
  exit 1
}
docker-compose up -d --build || {
  echo 'docker-compose up -d --build failed' >&2
  exit 1
}
HERE

# Was deployment successful?
if [[ "${?}" -ne 0 ]]
then
  exit_on_error 'Deployment failed'
fi

# Done!
echo "${GREEN}Server deployed to ${REMOTE_HOST}${RESET}"
exit 0
