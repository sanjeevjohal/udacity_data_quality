set -o vi
export PS1='$(pwd): '
alias ls_dir="ls -l | grep ^d"

# airflow aliases
alias af_list='airflow dags list'
alias af_test='airflow dags test $1 2021-01-01'
alias af_list_import_errors='airflow dags list-import-errors'
