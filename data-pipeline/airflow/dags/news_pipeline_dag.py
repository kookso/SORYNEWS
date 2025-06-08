#news_pipeline_dag.py
from airflow import DAG
from datetime import datetime,timedelta
from airflow.operators.bash import BashOperator


default_args = {
    'start_date': datetime(2025, 5, 23),
    'retries': 1,
}

with DAG(
    dag_id='news_data_pipeline',
    default_args=default_args,
    description='뉴스 RSS -> KAFKA -> FLINK로 데이터 가공 처리',
    schedule_interval="*/10 * * * *",  # 10분마다 실행
    catchup=False,
    tags=['news', 'kafka', 'flink', 'postgres', 'es', 'hdfs']
) as dag:

    # 3곳의 뉴스 크롤러 수행
    produce_hk = BashOperator(
        task_id='produce_hk_news',
        bash_command='python /opt/shared/producer_hk.py'
    )

    produce_mk = BashOperator(
        task_id='produce_mk_news',
        bash_command='python /opt/shared/producer_mk.py'
    )

    produce_yna = BashOperator(
        task_id='produce_yna_news',
        bash_command='python /opt/shared/producer_yna.py'
    )

    run_flink = BashOperator(
        task_id='run_flink_consumer',
        bash_command='docker exec flink-jobmanager python /app/jobs/consumer_flink.py'
    )


    [produce_hk, produce_mk, produce_yna] >> run_flink 


''' 고안했던 다른 방식의 아키텍처 덱 프로세스

    # PostgreSQL에서 데이터 조회 후 buffer에 저장
    fetch_from_postgres = BashOperator(
        task_id='fetch_pg_data',
        bash_command='python /opt/shared/transmit/postgres_fetch.py'
    )

    # ES 전송
    send_to_elasticsearch = BashOperator(
        task_id='transmit_to_es',
        bash_command='python /opt/shared/transmit/transmit_es.py'
    )

    # HDFS 전송
    send_to_hdfs = BashOperator(
        task_id='transmit_to_hdfs',
        bash_command='python /opt/shared/transmit/transmit_hdfs.py'
    )


    크롤러 → 플링크 ->  포스트그레 패치 -> 엘라스틱,hdfs에 전송 순서로 실행
    [produce_hk, produce_mk, produce_yna] >> run_flink >> fetch_from_postgres >> [send_to_elasticsearch, send_to_hdfs]
'''