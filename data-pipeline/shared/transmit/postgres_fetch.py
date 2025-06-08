import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# 저장할 디렉토리
BUFFER_DIR = os.path.join(os.path.dirname(__file__), "buffer")
os.makedirs(BUFFER_DIR, exist_ok=True)

# 2파일명 생성 (예: data_20250525_1400.json)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
file_path = os.path.join(BUFFER_DIR, f"data_{timestamp}.json")

try:
    # PostgreSQL 연결
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    cursor = conn.cursor()

    # 10분 전 시점 기준 조회
    query = """
    SELECT id, title, writer, write_date, category, content, url, summary, source, keywords, embedding, updated_at
    FROM news_article
    WHERE updated_at < NOW() - INTERVAL '10 minutes'
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    # 딕셔너리로 변환
    result = [dict(zip(colnames, row)) for row in rows]

    # JSON으로 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"{len(result)}건 저장 완료 → {file_path}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"오류 발생: {str(e)}")
