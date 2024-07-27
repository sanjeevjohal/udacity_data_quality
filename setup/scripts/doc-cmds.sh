#!/usr/bin/env zsh

case $1 in
    rebuild-image)
        docker images "apache/airflow:2.4.3" -q | xargs docker rmi -f && \
        ../airflow-local-env.sh build-image
        ;;
    stop-all-containers)
        docker stop $(docker ps -q | grep -v $( docker ps -q -f name=portainer)) && \
        docker system prune
        ;;
    restart-all-containers)
        docker container restart $(docker ps -q | grep -v $( docker ps -q -f name=portainer))
        ;;
    restart-webserver)
        docker restart "$(docker ps -q -f name=local-airflow-airflow-webserver)"
        ;;
    help)
        echo "Usage: $0 [rebuild-image|stop-all-containers|restart-all-containers|restart-webserver]"
        ;;
esac
