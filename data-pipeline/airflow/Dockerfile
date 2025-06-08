FROM apache/airflow:2.7.2
USER root
# Docker CLI 설치
#RUN apt-get update && apt-get install -y docker.io

RUN apt-get update && apt-get install -y docker.io && apt-get clean

# entrypoint.sh 복사 & 실행권한 부여
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY ./dags /opt/airflow/dags

# ENTRYPOINT 설정 (에어플로우 디비 초기화, 어드민 계정 생성)
ENTRYPOINT ["/entrypoint.sh"]
