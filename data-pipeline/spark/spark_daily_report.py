# spark_daily_report.py
import os
import argparse
from io import BytesIO
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from hdfs import InsecureClient
import matplotlib.font_manager as fm
from pyspark.sql import SparkSession
from datetime import datetime, timedelta
from pyspark.sql.types import ArrayType, StringType
from matplotlib.backends.backend_pdf import PdfPages
from pyspark.sql.functions import col, explode, count, from_json, to_timestamp


def main(report_date_str):
    print(f"리포트 대상 날짜: {report_date_str}")

    FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"    
    HDFS_URL = os.getenv("HDFS_URL", "http://hadoop-namenode:9870")     
    TEMP_PATH = "/news/temporary"                                       # HDFS 임시 저장소 위치
    REPORT_PATH = f"/news/report/daily_report_{report_date_str}.pdf"    # 분석 리포트 HDFS 저장소 위치
    ARCHIVE_PATH = f"/news/archive/{report_date_str}/"                  # HDFS 장기 저장소 위치
    font_prop = fm.FontProperties(fname=FONT_PATH, size=12)

    # 날짜 범위 계산 (HDFS 파일의 수정 시간 기준)
    report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
    start_ts = int(report_date.timestamp() * 1000)
    end_ts = int((report_date + timedelta(days=1)).timestamp() * 1000)

    # HDFS 연결 및 대상 파일 필터링
    client = InsecureClient(HDFS_URL, user="root")
    temp_files = client.list(TEMP_PATH, status=True)
    filtered_files = [
        f"hdfs://hadoop-namenode:8020{TEMP_PATH}/{name}"
        for name, meta in temp_files
        if name.endswith(".json") and start_ts <= meta["modificationTime"] < end_ts
    ]

    if not filtered_files:
        print("전날 저장된 파일이 없습니다. 종료합니다.")
        return

    # Spark 세션
    spark = SparkSession.builder \
        .appName("DailyNewsReport") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://hadoop-namenode:8020") \
        .getOrCreate()

    # JSON 읽기
    df = spark.read.option("multiline", "true").json(filtered_files)
    df = df.withColumn("write_date", to_timestamp(col("write_date")))
    df.cache()
    print(f"분석 대상 기사 수: {df.count()}")

    # 카테고리 분석
    category_df = df.groupBy("category").agg(count("*").alias("count")).orderBy(col("count").desc())
    category_pd = category_df.toPandas().head(10)

    # 수정: from_json 제거하고 바로 explode
    df = df.withColumn("keyword", explode(col("keywords")))
    keyword_df = df.groupBy("keyword").agg(count("*").alias("count")).orderBy(col("count").desc())
    keyword_pd = keyword_df.toPandas().head(10)

    # PDF를 메모리 버퍼에 생성
    pdf_buffer = BytesIO()
    with plt.rc_context({'font.family': font_prop.get_name()}), \
         plt.style.context('ggplot'), plt.ioff(), PdfPages(pdf_buffer) as pdf:

        # 카테고리 그래프 시각화
        plt.figure(figsize=(10, 6))
        plt.bar(category_pd["category"], category_pd["count"])
        plt.title(f"{report_date_str} 뉴스 리포트 - Top 10 Categories", fontproperties=font_prop)
        plt.xlabel("카테고리", fontproperties=font_prop)
        plt.ylabel("기사 수", fontproperties=font_prop)
        plt.xticks(rotation=45, fontproperties=font_prop)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # 키워드 그래프 시각화
        plt.figure(figsize=(10, 6))
        plt.bar(keyword_pd["keyword"], keyword_pd["count"])
        plt.title(f"{report_date_str} 뉴스 리포트 - Top 10 Keywords", fontproperties=font_prop)
        plt.xlabel("키워드", fontproperties=font_prop)
        plt.ylabel("기사 수", fontproperties=font_prop)
        plt.xticks(rotation=45, fontproperties=font_prop)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # PDF를 HDFS에 바로 업로드
    pdf_buffer.seek(0)
    with client.write(REPORT_PATH, overwrite=True) as writer:
        writer.write(pdf_buffer.read())
    print(f"PDF 업로드 완료: {REPORT_PATH}")

    # JSON 파일 아카이브 이동
    try:
        if not client.status(ARCHIVE_PATH, strict=False):
            client.makedirs(ARCHIVE_PATH)
            print(f"아카이브 디렉토리 생성됨: {ARCHIVE_PATH}")
    except Exception as e:
        print(f"아카이브 디렉토리 생성 실패: {e}")
        return

    for full_path in filtered_files:
        filename = os.path.basename(full_path)
        src = os.path.join(TEMP_PATH, filename)
        dst = f"{ARCHIVE_PATH}{filename}"
        try:
            client.rename(src, dst)
            print(f"{src} → {dst} 이동 완료")
        except Exception as e:
            print(f"파일 이동 실패: {src} → {dst} | 에러: {e}")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="보고서 날짜 (예: 2025-05-23)")
    args = parser.parse_args()
    main(args.date)
