# flink:1.17 이미지 기반
FROM flink:1.17

# Python 및 의존 패키지 설치
# RUN apt-get update && apt-get install -y python3-pip python3-dev
# RUN apt-get update && apt-get install -y python3-pip python3-dev python-is-python3
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    ln -s /usr/bin/python3 /usr/bin/python  

# # Hadoop CLI 설치 (HDFS 접근용)
# RUN wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz && \
#     tar -xzf hadoop-3.3.6.tar.gz && \
#     mv hadoop-3.3.6 /opt/hadoop && \
#     ln -s /opt/hadoop/bin/hadoop /usr/local/bin/hadoop

# # 환경 변수 설정 (필요시)
# ENV HADOOP_HOME=/opt/hadoop
# ENV PATH=$PATH:/opt/hadoop/bin

# requirements.txt 복사 및 설치
COPY flink/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# 작업 디렉토리 생성
WORKDIR /app

# PyFlink 작업 코드 복사
COPY flink/jobs/ jobs/
COPY flink/config/ /app/config/ 

# .env 파일 복사
COPY ../.env .env 

