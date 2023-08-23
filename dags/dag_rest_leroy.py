import random
import time
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

def start_url_collection(search_term):
    print(f"URL collection triggered for search term: {search_term}")
    # Your scraping logic using the provided search_term and additional libraries

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'api_trigger_url_collection',
    default_args=default_args,
    schedule_interval=None, 
    catchup=False,
)

def on_search_term_received(ti, **kwargs):
    search_term = ti.xcom_pull(task_ids='wait_for_search_term')
    if search_term:
        start_url_collection(search_term)
    else:
        print("No search term received, URL collection not triggered.")

with dag:
    http_sensor_task = HttpSensor(
        task_id='wait_for_search_term',
        http_conn_id='http_sensor_connection', 
        endpoint='/api/search',
        request_params={"method": "GET"},
    )

    trigger_url_collection_task = PythonOperator(
        task_id='trigger_url_collection',
        python_callable=on_search_term_received,
        provide_context=True,
    )

    dummy_task = DummyOperator(
        task_id='dummy_task'
    )

http_sensor_task >> trigger_url_collection_task >> dummy_task
