# consumer_flink.py
import os
import sys
import time
import json
import psycopg2
import uuid 
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
from hdfs import InsecureClient
from collections import defaultdict
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
from preprocess import transform_extract_keywords, transform_to_embedding



load_dotenv()
last_msg_time = time.time()

# Flink 실행 환경 설정
env = StreamExecutionEnvironment.get_execution_environment()
kafka_connector_path = os.getenv("KAFKA_CONNECTOR_PATH")
env.add_jars(f"file://{kafka_connector_path}")

# Kafka 연결 정보 + 다중 토픽
kafka_props = {
    'bootstrap.servers': 'kafka:9092',
    "auto.offset.reset": "earliest" # 처음부터 읽어오기 
}

category_topics = [
    "economy", "politics", "society", "world", "industry", "stock",
    "real_estate", "entertainment", "sports", "game", "health", "it"
]

consumer = FlinkKafkaConsumer(
    topics=category_topics,  # 여러 토픽에서 동시에 수신
    deserialization_schema=SimpleStringSchema(),
    properties=kafka_props
)

stream = env.add_source(consumer)

def monitor_timeout(timeout_sec=360):  # 6분
    global last_msg_time
    while True:
        if time.time() - last_msg_time > timeout_sec:
            print("6분 이상 새 메시지가 없어 종료합니다.")
            sys.exit(0)
        time.sleep(10)

# 메시지 처리 함수
def apply_transforms(text: str) -> str:
    # 여기 두줄 
    global last_msg_time
    last_msg_time = time.time()  # 메시지 수신 시 타이머 초기화

    try:
        # HDFS 클라이언트 초기화
        hdfs_client = InsecureClient('http://hadoop-namenode:9870', user='root')
        data = json.loads(text)
        title = data.get("title", "")
        writer = data.get("writer", "")
        write_date = data.get("write_date", "")
        content = data.get("content", "")
        url = data.get("url", "")
        category = data.get("category", "") 
        source = data.get("source", "")

        if not all([title, writer, write_date, content, url, category, source]):
            return json.dumps({"skipped": "필수 필드 누락"})

        # 키워드 + 임베딩
        keywords = transform_extract_keywords(content)
        embedding = transform_to_embedding(content)
        keywords_json = json.dumps(keywords, ensure_ascii=False)
        updated_at = datetime.utcnow()

        # hdfs 저장
        data["keywords"] = keywords
        data["embedding"] = embedding
        data["updated_at"] = updated_at.isoformat()
        file_name = f"article_{int(time.time())}_{uuid.uuid4().hex}.json"
        hdfs_path = f"/news/temporary/{file_name}"
        with hdfs_client.write(hdfs_path, encoding='utf-8') as writer_fp:
            json.dump(data, writer_fp, ensure_ascii=False)
        print(f"HDFS 저장 완료 → hdfs://hadoop-namenode:8020{hdfs_path}")

        # db 저장
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cursor = conn.cursor()

        # 중복 URL 확인
        cursor.execute("SELECT 1 FROM news_article WHERE url = %s", (url,))
        if cursor.fetchone():
            print(f"중복 URL로 인해 PostgreSQL/Elasticsearch 저장 생략됨: {url}")
            cursor.close()
            conn.close()
            return "HDFS 저장만 수행됨 (중복 URL)"
        
        cursor.execute(
            """
            INSERT INTO news_article 
            (title, writer, write_date, category, content, url, keywords, embedding, source, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (title, writer, write_date, category, content, url, keywords_json, embedding, source, updated_at)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"PostgreSQL 저장 완료: {title}")

        # Elasticsearch 전송
        try:
            write_date_iso = datetime.strptime(write_date, "%Y-%m-%d %H:%M:%S").isoformat()
        except ValueError:
            write_date_iso = write_date

        es_data = {
            "title": title,
            "writer": writer,
            "write_date": write_date_iso,
            "content": content,
            "url": url,
            "category": category,
            "keywords": keywords,
            "source": source,
            "updated_at": updated_at.isoformat()
        }
        # URL을 기반으로 Elasticsearch 문서 ID 생성
        doc_id = quote(url, safe="")

        # 지정된 ID에 저장
        es_host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
        index_name = "news-articles"
        es_url = f"{es_host}/{index_name}/_doc/{doc_id}"

        es_response = requests.put(es_url, json=es_data)
        if es_response.status_code in [200, 201]:
            print(f"Elasticsearch 저장 완료: {title}")
        else:
            print(f"Elasticsearch 저장 실패: {es_response.status_code} - {es_response.text}")
        return "HDFS → PostgreSQL → Elasticsearch 처리 완료"

    except Exception as e:
        return json.dumps({"error": str(e)})
    
# Flink 스트림 실행
processed_stream = stream.map(apply_transforms)
processed_stream.print()
# 이 부분에 타이머 모니터링 스레드 시작
threading.Thread(target=monitor_timeout, daemon=True).start()
print("Starting Flink Job...")
env.execute("Flink Kafka Consumer Job (Category Topics)")
print("Flink Job execution complete.")
