import os
import json
import glob
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# buffer 디렉토리에서 최신 JSON 파일 찾기
BUFFER_DIR = os.path.join(os.path.dirname(__file__), "buffer")
json_files = sorted(glob.glob(os.path.join(BUFFER_DIR, "data_*.json")), reverse=True)

if not json_files:
    print("JSON 파일 없음: 먼저 postgres_fetch.py 실행 필요")
    exit(0)

latest_file = json_files[0]
print(f"최신 JSON 파일 읽는 중: {latest_file}")

# Elasticsearch 주소
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200/news-articles/_doc")

# 파일 읽고 전송
try:
    with open(latest_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    success, fail = 0, 0

    for article in articles:
        # embedding은 Elasticsearch에 넣지 않음
        article.pop("embedding", None)

        # write_date 파싱 처리
        try:
            if isinstance(article["write_date"], str):
                dt = datetime.strptime(article["write_date"], "%Y-%m-%d %H:%M:%S")
                article["write_date"] = dt.isoformat()
        except Exception:
            pass

        try:
            res = requests.post(ES_URL, json=article)
            if res.status_code in [200, 201]:
                success += 1
            else:
                print(f"실패: {res.status_code}, 내용: {res.text}")
                fail += 1
        except Exception as e:
            print(f"예외 발생: {str(e)}")
            fail += 1

    print(f"전송 완료: 성공 {success} / 실패 {fail}")

except Exception as e:
    print(f"파일 처리 오류: {str(e)}")
