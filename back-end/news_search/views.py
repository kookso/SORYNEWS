from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from elasticsearch import Elasticsearch
from psycopg2.extras import RealDictCursor
import psycopg2
import os

@api_view(["GET"])
def search_news_view(request):
    query = request.query_params.get("q", "").strip()

    if not query:
        return Response({"detail": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    # Elasticsearch
    try:
        es = Elasticsearch("http://localhost:9200")
        index_name = "news-articles"
        es_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"title": query}},
                        {"match": {"content": query}},
                        {"match": {"writer": query}},
                        {"match": {"keywords": query}}
                    ]
                }
            }
        }
        es_result = es.search(index=index_name, body=es_query, size=20)
        urls = [hit["_id"] for hit in es_result["hits"]["hits"]]

        if not urls:
            return Response({"message": "검색 결과가 없습니다.", "data": []})

    except Exception as e:
        print("❌ Elasticsearch 오류:", str(e))
        return Response({"detail": "Elasticsearch 오류", "error": str(e)}, status=500)

    # PostgreSQL
    try:
        pg_conn = psycopg2.connect(
            host="localhost",
            dbname="news",
            user="ssafyuser",
            password="ssafy"
        )
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)

        pg_cursor.execute("""
            SELECT 
                A.id, A.title, A.writer, A.write_date, A.category, A.content, A.url, A.keywords, A.embedding,
                COALESCE(L.likes, 0) AS likes,
                COALESCE(V.reads, 0) AS read
            FROM news_article A
            LEFT JOIN (
                SELECT article_id, COUNT(*) AS likes
                FROM news_like
                GROUP BY article_id
            ) L ON A.id = L.article_id
            LEFT JOIN (
                SELECT article_id, COUNT(*) AS reads
                FROM news_view
                GROUP BY article_id
            ) V ON A.id = V.article_id
            WHERE A.url = ANY(%s)
        """, (urls,))

        rows = pg_cursor.fetchall()
        for row in rows:
            row["article_interaction"] = {
                "likes": row.pop("likes", 0),
                "read": row.pop("read", 0)
            }

    except Exception as e:
        print("❌ PostgreSQL 오류:", str(e))
        return Response({"detail": "PostgreSQL 오류", "error": str(e)}, status=500)

    finally:
        if 'pg_cursor' in locals():
            pg_cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()

    return Response({
        "message": "검색 결과입니다.",
        "data": rows
    })
