from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine

class CustomSQLAlchemyHook(BaseHook):
    def __init__(self, conn_id):
        self.conn_id = conn_id

    def get_conn(self):
        conn = self.get_connection(self.conn_id)
        conn_uri = f"mssql+pyodbc://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}?driver=ODBC+Driver+17+for+SQL+Server"
        engine = create_engine(conn_uri)
        return engine
