# daily_report_dag.py
import pendulum
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_report_dag',
    default_args=default_args,
    description='매일 새벽 1시에 Spark를 이용해 뉴스 리포트 생성',
    schedule_interval='0 1 * * *',
    start_date=datetime(2025, 5, 1, tzinfo=local_tz),          
    catchup=False,
    tags=['daily', 'report', 'spark']
) as dag:
    
    run_spark_report = BashOperator(
    task_id='spark_daily_report',
    bash_command='docker exec spark spark-submit /opt/spark/spark_daily_report.py --date {{ ds }}'
)

    notify_report_generated = BashOperator(
        task_id='notify_report_generated',
        bash_command=(
            'echo "리포트가 생성되었습니다: {{ ds }} 날짜의 이메일 보내기 "'
        )
    )

    run_spark_report >> notify_report_generated
