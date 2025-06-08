from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions, status

from django.db.models import Count
from django.db import connection

import numpy as np
import json

from pgvector.django import CosineDistance

from mynews.models import NewsArticle, NewsLike, NewsView


def fetch_keywords(article_ids):
    if not article_ids:
        return {}

    sql = """
        SELECT id, keywords
        FROM news_article
        WHERE id IN %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [tuple(article_ids)])
        rows = cursor.fetchall()

    result = {}
    for aid, raw in rows:
        if isinstance(raw, list):
            result[aid] = raw
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                result[aid] = parsed if isinstance(parsed, list) else []
            except Exception:
                result[aid] = []
        else:
            result[aid] = []
    return result


# 뉴스 목록 조회 (최신순 또는 추천순)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def news_list_view(request):
    class Pagination(PageNumberPagination):
        page_size = 10

    sort = request.query_params.get("sort", "latest")
    category = request.query_params.get("category", "").strip()

    if sort == "recommend" and request.user.is_authenticated:
        liked_ids = NewsLike.objects.filter(user=request.user).values_list("article_id", flat=True)
        vectors = NewsArticle.objects.filter(id__in=liked_ids).values_list("embedding", flat=True)

        parsed_vectors = []
        for v in vectors:
            if isinstance(v, (list, np.ndarray)):
                parsed_vectors.append(list(v))
            elif isinstance(v, str):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        parsed_vectors.append(parsed)
                except Exception:
                    continue

        if not parsed_vectors:
            return Response({"detail": "추천을 위한 임베딩 정보가 없습니다."}, status=400)

        avg_vector = np.mean(np.array(parsed_vectors), axis=0).tolist()
        queryset = NewsArticle.objects.order_by(CosineDistance("embedding", avg_vector))
    else:
        queryset = NewsArticle.objects.order_by("-write_date")

    if category:
        queryset = queryset.filter(category=category)

    articles = list(queryset.values(
        "id", "title", "writer", "write_date", "category", "content", "url"
    ))

    article_ids = [a["id"] for a in articles]

    keyword_dict = fetch_keywords(article_ids)

    like_counts = dict(
        NewsLike.objects.filter(article_id__in=article_ids)
        .values("article_id")
        .annotate(count=Count("id"))
        .values_list("article_id", "count")
    )
    view_counts = dict(
        NewsView.objects.filter(article_id__in=article_ids)
        .values("article_id")
        .annotate(count=Count("id"))
        .values_list("article_id", "count")
    )

    for article in articles:
        article["keywords"] = keyword_dict.get(article["id"], [])
        article["article_interaction"] = {
            "likes": like_counts.get(article["id"], 0),
            "read": view_counts.get(article["id"], 0),
        }

    paginator = Pagination()
    page = paginator.paginate_queryset(articles, request)

    return Response({
        "count": paginator.page.paginator.count,
        "total_pages": paginator.page.paginator.num_pages,
        "current_page": paginator.page.number,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": page,
    })


# 뉴스 상세 조회
@api_view(["GET"])
def news_detail_view(request, article_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, writer, write_date, category, content, url, keywords
            FROM news_article
            WHERE id = %s
        """, [article_id])
        row = cursor.fetchone()

    if not row:
        return Response({"detail": "Not found."}, status=404)

    id, title, writer, write_date, category, content, url, keywords = row

    try:
        if isinstance(keywords, str):
            keywords = json.loads(keywords)
        elif not isinstance(keywords, list):
            keywords = []
    except Exception:
        keywords = []

    like_count = NewsLike.objects.filter(article_id=article_id).count()
    view_count = NewsView.objects.filter(article_id=article_id).count()

    return Response({
        "id": id,
        "title": title,
        "writer": writer,
        "write_date": write_date,
        "category": category,
        "content": content,
        "url": url,
        "keywords": keywords,
        "article_interaction": {
            "likes": like_count,
            "read": view_count,
        }
    })


# 관련 뉴스 추천
@api_view(["GET"])
def related_news_view(request, article_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT embedding FROM news_article WHERE id = %s", [article_id])
        row = cursor.fetchone()

    if not row:
        return Response({"detail": "Not found."}, status=404)

    (embedding,) = row
    try:
        if isinstance(embedding, str):
            embedding = json.loads(embedding)
        elif not isinstance(embedding, list):
            return Response({"detail": "유효한 임베딩 정보가 없습니다."}, status=400)
    except Exception:
        return Response({"detail": "임베딩 파싱 실패"}, status=400)

    articles = list(
        NewsArticle.objects.exclude(id=article_id)
        .order_by(CosineDistance("embedding", embedding))
        .values("id", "title", "writer", "write_date", "category", "url")[:10]
    )
    article_ids = [a["id"] for a in articles]

    like_counts = dict(
        NewsLike.objects.filter(article_id__in=article_ids)
        .values("article_id")
        .annotate(count=Count("id"))
        .values_list("article_id", "count")
    )
    view_counts = dict(
        NewsView.objects.filter(article_id__in=article_ids)
        .values("article_id")
        .annotate(count=Count("id"))
        .values_list("article_id", "count")
    )

    for article in articles:
        article["article_interaction"] = {
            "likes": like_counts.get(article["id"], 0),
            "read": view_counts.get(article["id"], 0),
        }

    return Response(articles)
