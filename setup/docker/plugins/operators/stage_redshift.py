from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140' # green color used in the Airflow UI

    copy_sql = """
            COPY {}
            FROM '{}'
            CREDENTIALS 'aws_iam_role={}'
            compupdate off
            REGION '{}'
            FORMAT AS JSON '{}'
            truncatecolumns;
        """

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 # redshift_conn_id=your-connection-name
                conn_id="",
                aws_credentials_id="",
                table="",
                s3_bucket="",
                s3_key="",
                json_path="",
                region="",
                arn_iam_role="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        # Map params here
        # Example:
        self.conn_id = conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.json_path = json_path
        self.region = region
        self.arn_iam_role = arn_iam_role


    def execute(self, context):
        self.log.info('StageToRedshiftOperator in progress')

        redshift_hook = PostgresHook(self.conn_id)
        self.log.info("Clearing data from destination Redshift table")
        redshift_hook.run("truncate {}".format(self.table))

        rendered_key = self.s3_key.format(**context)

        s3_path = "s3://{}/{}".format(self.s3_bucket, rendered_key)
        sql_stmt = StageToRedshiftOperator.copy_sql.format(
            self.table,
            s3_path,
            self.arn_iam_role,
            self.region,
            self.json_path
        )
        self.log.info(f"Running COPY SQL: {sql_stmt}")
        redshift_hook.run(sql_stmt)






