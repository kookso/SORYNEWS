#!/bin/bash

# Airflow DB 초기화 (한 번만 실행되도록 처리)
airflow db upgrade

# 사용자 생성 (이미 있으면 에러 무시)
airflow users create \
  --username "${AIRFLOW_USERNAME}" \
  --password "${AIRFLOW_PASSWORD}" \
  --firstname Air \
  --lastname Flow \
  --role Admin \
  --email airflow@example.com || true

# 전달된 명령(webserver, scheduler 등)에 따라 실행 분기
exec airflow "$@"