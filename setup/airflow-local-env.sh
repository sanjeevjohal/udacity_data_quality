#!/bin/bash

AIRFLOW_VERSION=2.4.3
DOCKER_COMPOSE_PROJECT_NAME=local-airflow

display_help() {
   # Display Help
   echo "======================================"
   echo "   Airflow Local Runner CLI"
   echo "======================================"
   echo "Syntax: mwaa-local-runner [command]"
   echo
   echo "---commands---"
   echo "help                   Print CLI help"
   echo "build-image            Build Image Locally"
   echo "reset-db               Reset local PostgresDB container."
   echo "start                  Start Airflow local environment. (LocalExecutor, Using postgres DB)"
   echo "test-requirements      Install requirements on an ephemeral instance of the container."
   echo "validate-prereqs       Validate pre-reqs installed (docker, docker-compose, python3, pip3)"
   echo
}

validate_prereqs() {
   docker -v >/dev/null 2>&1
   if [ $? -ne 0 ]; then
      echo -e "'docker' is not installed or not runnable without sudo. \xE2\x9D\x8C"
   else
      echo -e "Docker is Installed. \xE2\x9C\x94"
   fi

   docker-compose -v >/dev/null 2>&1
   if [ $? -ne 0 ]; then
      echo -e "'docker-compose' is not installed. \xE2\x9D\x8C"
   else
      echo -e "Docker compose is Installed. \xE2\x9C\x94"
   fi

   python3 --version >/dev/null 2>&1
   if [ $? -ne 0 ]; then
      echo -e "Python3 is not installed. \xE2\x9D\x8C"
   else
      echo -e "Python3 is Installed \xE2\x9C\x94"
   fi

   pip3 --version >/dev/null 2>&1
   if [ $? -ne 0 ]; then
      echo -e "Pip3 is not installed. \xE2\x9D\x8C"
   else
      echo -e "Pip3 is Installed. \xE2\x9C\x94"
   fi
}

<<explain
This (re)builds the image locally. It uses the dockerfile in the docker folder.
--rm : Remove intermediate containers after a successful build to conserve disk space
--compress : Compress the build context which speeds up the build process and reduce network transfer time
--tag : Tag the image
explain
build_image() {
    local dockerfile=$1
    docker build --rm --compress -t apache/airflow:$AIRFLOW_VERSION $dockerfile
}


case "$1" in
validate-prereqs)
   validate_prereqs
   ;;
test-requirements)
   BUILT_IMAGE=$(docker images -q amazon/mwaa-local:$AIRFLOW_VERSION)
   if [[ -n "$BUILT_IMAGE" ]]; then
     echo "Container amazon/mwaa-local:$AIRFLOW_VERSION exists. Skipping build"
   else
     echo "Container amazon/mwaa-local:$AIRFLOW_VERSION not built. Building locally."
     build_image
   fi
   docker run -v $(pwd)/dags:/usr/local/airflow/dags -it amazon/mwaa-local:$AIRFLOW_VERSION test-requirements
   ;;
build-image)
   build_image ./docker
   ;;
build-image-test)
   build_image ./docker_test
   ;;
reset-db)
   docker-compose -p $DOCKER_COMPOSE_PROJECT_NAME -f ./docker/docker-compose-resetdb.yml up
   ;;
start)
   # this starts the set of containers based on the yaml file. It names the stack with the project name
   docker-compose -p $DOCKER_COMPOSE_PROJECT_NAME -f ./docker/docker-compose-local.yml up
   ;;
help)
   display_help
   ;;
*)
   echo "No command specified, displaying help"
   display_help
   ;;
esac
