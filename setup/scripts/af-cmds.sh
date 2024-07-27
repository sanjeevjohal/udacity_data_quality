#!/usr/bin/env zsh

case $1 in
    list-connections)
        ./airflow.sh connections list
        ;;
    info)
        ./airflow.sh info
        ;;
    cheatsheet)
        ./airflow.sh cheatsheet
        ;;
esac
