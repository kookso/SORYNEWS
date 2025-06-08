FROM bitnami/spark:3.4

USER root

RUN apt-get update && \
    apt-get install -y fontconfig fonts-nanum python3-pip && \
    pip3 install pandas matplotlib hdfs python-dotenv && \
    apt-get clean

# matplotlib 캐시 경로 환경변수 설정 (모든 사용자 공용)
ENV MPLCONFIGDIR=/tmp/mplconfig

# 캐시 디렉토리 미리 생성해두기 (권한 문제 방지)
RUN mkdir -p /tmp/mplconfig && chmod -R 777 /tmp/mplconfig

# 원래 Spark 사용자로 복귀 (Bitnami: 1001)
USER 1001

