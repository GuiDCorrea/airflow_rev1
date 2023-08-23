from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from plugins.hooks.custom_sqlalchemy_hook import CustomSQLAlchemyHook



class CustomSQLAlchemyOperator(BaseOperator):
    @apply_defaults
    def __init__(self, sql, conn_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sql = sql
        self.conn_id = conn_id

    def execute(self, context):
        hook = CustomSQLAlchemyHook(self.conn_id)
        engine = hook.get_conn()
        with engine.connect() as connection:
            result = connection.execute(self.sql)
            for row in result:
                print(row)
