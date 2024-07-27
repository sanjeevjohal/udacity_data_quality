class DQChecks:
    def __init__(self, table, column):
        self.table = table
        self.column = column

    def empty_table(self):
        return f"""
            SELECT COUNT(*)
            FROM {self.table}
        """

    def null_check(self, column):
        return f"""
            SELECT COUNT(*)
            FROM {self.table}
            WHERE {self.column} IS NULL
        """

    def get_dq_checks(self):
        checks = {
            "empty": {
                "check_sql": self.empty_table()
                , "expected_result": {"threshold": 0}
            },
            "null": {
                "check_sql": self.null_check(self.column)
                , "expected_result": {"threshold": 0}
            }
        }
        return checks
