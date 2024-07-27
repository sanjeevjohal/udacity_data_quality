from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators import (StageToRedshiftOperator, LoadFactOperator, LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries, DQChecks
from airflow.utils.task_group import TaskGroup

default_args = {
    'owner': 'sjohal',
    'start_date': datetime.utcnow() - timedelta(minutes=5),
    'depends_on_past': False,
    'email_on_retry': False,
    'catchup_by_default': False,
    'provide_context': True,
    'retries': 3,
}

dag = DAG('main',
          default_args=default_args,
          description='Create tables',
          schedule_interval=timedelta(hours=1),
          max_active_runs=1
          )

start_operator = DummyOperator(task_id='Begin_execution', dag=dag)
end_operator = DummyOperator(task_id='Stop_execution', dag=dag)


# region stage events
copy_events_from_s3_to_redshift = StageToRedshiftOperator(
    task_id="stage_events",
    dag=dag,
    conn_id="sj_redshift",
    aws_credentials_id="aws_credentials",
    table="staging_events",
    s3_bucket="sjohal/udacity-dend",
    s3_key="log_data",
    arn_iam_role="arn:aws:iam::288093678599:role/myRedshiftRole",
    region="us-west-2",
    json_path="s3://sjohal/udacity-dend/log_json_path.json"
)
# endregion

# region stage songs
copy_songs_from_s3_to_redshift = StageToRedshiftOperator(
    task_id="stage_songs",
    dag=dag,
    conn_id="sj_redshift",
    aws_credentials_id="aws_credentials",
    table="staging_songs",
    s3_bucket="sjohal/udacity-dend",
    s3_key="song_data",
    arn_iam_role="arn:aws:iam::288093678599:role/myRedshiftRole",
    region="us-west-2",
    json_path="auto"
)
# endregion

# region load songplays fact table
load_songplays_fact_table = LoadFactOperator(
    task_id="load_songplays_fact_table",
    dag=dag,
    conn_id="sj_redshift",
    table="songplays",
    columns="""
        songplay_id,
        start_time,
        userid,
        level,
        songid,
        artistid,
        sessionid,
        location,
        user_agent
    """,
    sql_stmt=SqlQueries.songplay_table_insert,
    append=True
)
# endregion


start_operator >> copy_events_from_s3_to_redshift >> load_songplays_fact_table
start_operator >> copy_songs_from_s3_to_redshift >> load_songplays_fact_table

# region load dimension tables
def get_columns_for_table(table_name):
    # Assume we have a mapping of table names to column names
    # Here is an example using a dictionary
    column_mapping = {
        "users": ["userid", "first_name", "last_name", "gender", "level"],
        "songs": ["songid", "title", "artistid", "year", "duration"],
        "artists": ["artistid", "name", "location", "lattitude", "longitude"],
        "time": ["start_time", "hour", "day", "week", "month", "year", "weekday"]
    }
    return ",".join(column_mapping[table_name])


# Define the tables and corresponding SQL queries
tables = {
    "users": SqlQueries.user_table_insert,
    "songs": SqlQueries.song_table_insert,
    "artists": SqlQueries.artist_table_insert,
    "time": SqlQueries.time_table_insert
}

# Create a task group
with TaskGroup(group_id='load_dim_tables', dag=dag) as load_dim_tables_group:
    # Create a task for each table
    for table, sql_stmt in tables.items():
        task_id = f"load_{table}_dim_table"
        column_names = get_columns_for_table(table)

        # Create an instance of the operator
        load_dim_operator = LoadDimensionOperator(
            task_id=task_id,
            dag=dag,
            conn_id="sj_redshift",
            table=table,
            sql_stmt=sql_stmt,
            column_names=column_names,
            append=True,
            load_sql_stmt=f"INSERT INTO {table} ({column_names}) {sql_stmt}"
        )

        # Set the dependencies of the operator
        load_songplays_fact_table >> load_dim_tables_group
# endregion

# run quality checks within task group using DQChecks class
with TaskGroup(group_id='run_quality_checks', dag=dag) as run_quality_checks_group:
    # Create a task for each table
    for table in tables.keys():
        task_id = f"run_dqcheck_{table}_empty"

        # Create an instance of the operator
        dq_checks = DQChecks(table)  # Create an instance of DQChecks
        dq_checks_dict = dq_checks.get_dq_checks()  # Get the dictionary of checks

        # Create an instance of the operator
        run_quality_checks = DataQualityOperator(
            task_id=task_id,
            dag=dag,
            conn_id="sj_redshift",
            table=table,
            dq_check_query=dq_checks_dict["empty"]
        )

        # Set the dependencies of the operator
        load_dim_tables_group >> run_quality_checks_group >> end_operator

