from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from helpers import create_tables


default_args = {
    'owner': 'sjohal',
    'start_date': datetime.utcnow() - timedelta(minutes=5),
    'depends_on_past': False,
    'email_on_retry': False,
    'retry_delay': timedelta(minutes=1),
    'catchup_by_default': False
}

dag = DAG('create_tables',
          default_args=default_args,
          description='Create tables',
          schedule_interval=None,
          max_active_runs=1
        )

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS public.users (
	userid int4 NOT NULL,
	first_name varchar(256),
	last_name varchar(256),
	gender varchar(256),
	"level" varchar(256),
	CONSTRAINT users_pkey PRIMARY KEY (userid)
);
"""

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

create_all_tables = PostgresOperator(
    task_id="create_all_tables",
    dag=dag,
    postgres_conn_id="sj_redshift",
    sql=create_tables.create_all_tables_sql
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

# task dependencies
start_operator >> create_all_tables
create_all_tables >> end_operator

