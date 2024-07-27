from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadFactOperator(BaseOperator):
    ui_color = '#F98866'  # orange

    sql_stmt = """
        INSERT INTO {} {} {}
    """

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 conn_id="",
                 table="",
                 columns="",
                 sql_stmt="",
                 append=False,
                 *args, **kwargs):
        super(LoadFactOperator, self).__init__(*args, **kwargs)
        # Map params here
        # Example:
        self.conn_id = conn_id
        self.table = table
        self.columns = columns
        self.sql_stmt = sql_stmt
        self.append = append

    def execute(self, context):
        self.log.info('LoadFactOperator in progress')
        redshift_hook = PostgresHook(self.conn_id)
        columns = "({})".format(self.columns)
        if self.append == False:
            self.log.info("Clearing data from destination Redshift table")
            redshift_hook.run("truncate {}".format(self.table))

        load_sql = LoadFactOperator.sql_stmt.format(
            self.table,
            columns,
            self.sql_stmt
        )
        redshift_hook.run(load_sql)
