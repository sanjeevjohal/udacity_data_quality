from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.decorators import apply_defaults
from airflow.models import BaseOperator

class LoadDimensionOperator(BaseOperator):
    """Custom operator to load dimension tables"""

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(
            self,
            conn_id: str = "",
            table: str = "",
            sql_stmt: str = "",
            column_names: str = "",
            append: bool = False,
            load_sql_stmt: str = "",
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Map params here
        self.conn_id = conn_id
        self.table = table
        self.sql_stmt = sql_stmt
        self.column_names = column_names
        self.append = append
        self.load_sql_stmt = load_sql_stmt


    def execute(self, context):
        self.log.info(f"Loading data into {self.table} dimension table")
        self.log.info(f"Executing SQL query: {self.load_sql_stmt}")
        redshift_hook = PostgresHook(self.conn_id)

        # If append is False, truncate the table and reload it
        if not self.append:
            self.log.info(f"Truncating {self.table} dimension table and then reload it")
            redshift_hook.run(f"TRUNCATE TABLE {self.table}")
            redshift_hook.run(self.load_sql_stmt)
        else:
            self.log.info(f"Append mode is on for {self.table} dimension table")
            redshift_hook.run(self.load_sql_stmt)

        self.log.info(f"Finished loading data into {self.table} dimension table")