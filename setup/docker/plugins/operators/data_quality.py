from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 conn_id: str = "",
                 table="",
                 dq_check_query="",
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        # Map params here
        # Example:
        self.conn_id = conn_id
        self.table = table
        self.dq_check_query = dq_check_query

    def execute(self, context):
        self.log.info('DataQualityOperator in progress')
        redshift_hook = PostgresHook(self.conn_id)
        self.log.info(f'Running query: {self.dq_check_query["check_sql"]}')
        records = redshift_hook.get_records(self.dq_check_query)
        # compare the result with the expected result
        if len(records[0]) == int(self.dq_check_query["expected_result"]["threshold"]):
            raise ValueError(f"Data quality check failed. {self.table} returned no results")