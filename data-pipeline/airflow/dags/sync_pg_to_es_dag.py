from airflow import DAG
from sync_pg_to_es import sync_pg_to_es
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 5, 26),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sync_pg_to_es",
    default_args=default_args,
    description='Postgre DB와 Elasticsearch 동기화 프로세스',
    schedule_interval="*/10 * * * *",
    catchup=False,
    tags=["sync", "postgres", "elasticsearch"]
) as dag:
    sync_task = PythonOperator(
        task_id="sync_postgres_to_elasticsearch",
        python_callable=sync_pg_to_es,
    )
