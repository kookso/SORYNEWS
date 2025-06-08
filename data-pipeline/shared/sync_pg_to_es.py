import os
import psycopg2
import requests
from urllib.parse import quote
from airflow.utils.log.logging_mixin import LoggingMixin

logger = LoggingMixin().log

def sync_pg_to_es():
    print("PostgreSQL → Elasticsearch 동기화 시작")

    # PostgreSQL 연결
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "news"),
        user=os.getenv("DB_USERNAME", "ssafyuser"),
        password=os.getenv("DB_PASSWORD", "ssafy")
    )
    cursor = conn.cursor()

    # 최근 5분 내에 업데이트된 문서 조회
    cursor.execute("""
        SELECT title, writer, write_date, category, content, url, keywords, updated_at
        FROM news_article
        WHERE updated_at > now() - interval '5 minutes'
    """)
    rows = cursor.fetchall()
    print(f"가져온 문서 수: {len(rows)}")
    logger.info(f"가져온 문서 수: {len(rows)}")

    es_host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
    index_name = "news-articles"
    count = 0

    for row in rows:
        doc_id = quote(row[5], safe="")  # URL → 문서 ID
        doc = {
            "title": row[0],
            "writer": row[1],
            "write_date": row[2].isoformat(),
            "category": row[3],
            "content": row[4],
            "url": row[5],
            "keywords": row[6],
            "updated_at": row[7].isoformat()
        }

        # 먼저 HEAD로 문서 존재 여부 확인
        head_url = f"{es_host}/{index_name}/_doc/{doc_id}"
        head_response = requests.head(head_url)

        if head_response.status_code == 404:
            # 존재하지 않을 때만 PUT
            put_response = requests.put(head_url, json=doc)
            if put_response.status_code in [200, 201]:
                msg = f"저장됨: {doc_id}"
                count += 1
            else:
                msg = f"저장 실패 ({put_response.status_code}): {doc_id} - {put_response.text}"
        else:
            msg = f"이미 존재함 (건너뜀): {doc_id}"

        print(msg)
        logger.info(msg)

    cursor.close()
    conn.close()

    print(f"총 {count}개 문서 Elasticsearch에 새로 저장 완료")
    logger.info(f"총 {count}개 문서 Elasticsearch에 새로 저장 완료")
