import os
import json
import glob
from datetime import datetime
from dotenv import load_dotenv
from hdfs import InsecureClient

load_dotenv()

# buffer 디렉토리에서 최신 JSON 파일 찾기
BUFFER_DIR = os.path.join(os.path.dirname(__file__), "buffer")
json_files = sorted(glob.glob(os.path.join(BUFFER_DIR, "data_*.json")), reverse=True)

if not json_files:
    print("JSON 파일 없음: 먼저 postgres_fetch.py 실행 필요")
    exit(0)

latest_file = json_files[0]
print(f"최신 JSON 파일 읽는 중: {latest_file}")

# HDFS 클라이언트 설정
HDFS_URL = os.getenv("HDFS_URL", "http://hadoop-namenode:9870")
HDFS_DIR = "/news/temporary"
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
hdfs_path = f"{HDFS_DIR}/data_{timestamp}.json"

client = InsecureClient(HDFS_URL, user="root")

# 파일 읽고 HDFS로 전송
try:
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # HDFS 디렉토리 생성 (없을 경우)
    client.makedirs(HDFS_DIR, permission=0o755)

    with client.write(hdfs_path, encoding="utf-8") as writer:
        json.dump(data, writer, ensure_ascii=False, indent=2)

    print(f" HDFS 저장 완료 → hdfs://{HDFS_DIR}/data_{timestamp}.json")

except Exception as e:
    print(f"HDFS 저장 실패: {str(e)}")
