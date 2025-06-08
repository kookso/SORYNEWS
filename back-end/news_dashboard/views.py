from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

from django.db.models import Count, Subquery, OuterRef, IntegerField
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.db import connection

from collections import Counter
from datetime import timedelta
import json

from mynews.models import NewsArticle, NewsLike, NewsView


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_view(request):
    user = request.user

    # 관심 카테고리 통계
    liked_ids = NewsLike.objects.filter(user=user).values_list('article_id', flat=True)
    category_stats = (
        NewsArticle.objects
        .filter(id__in=liked_ids)
        .values('category')
        .annotate(count=Count('category'))
        .order_by('-count')
    )

    # 키워드 통계
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.keywords
            FROM news_like l
            JOIN news_article a ON l.article_id = a.id
            WHERE l.user_id = %s
        """, [user.id])
        rows = cursor.fetchall()

    all_keywords = []
    for (kw_json,) in rows:
        try:
            if isinstance(kw_json, str):
                all_keywords.extend(json.loads(kw_json))
            elif isinstance(kw_json, list):
                all_keywords.extend(kw_json)
        except Exception:
            continue

    top_keywords = Counter(all_keywords).most_common(5)
    keyword_stats = [{"keyword": k, "count": c} for k, c in top_keywords]

    # 주간 조회수 (최근 7일, 비어 있는 날짜 포함)
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    raw_views = (
        NewsView.objects
        .filter(user=user, viewed_at__date__gte=week_ago, viewed_at__date__lte=today)
        .annotate(day=TruncDate('viewed_at'))
        .values('day')
        .annotate(count=Count('id'))
    )

    raw_views_dict = {item["day"]: item["count"] for item in raw_views}

    daily_views = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        daily_views.append({
            "day": day.strftime("%Y-%m-%d"),
            "count": raw_views_dict.get(day, 0)
        })

    # 좋아요한 기사 + article_interaction 포함
    liked_ids = NewsLike.objects.filter(user=user).values_list('article_id', flat=True)

    like_subquery = (
        NewsLike.objects
        .filter(article_id=OuterRef("pk"))
        .values("article_id")
        .annotate(count=Count("id"))
        .values("count")
    )

    view_subquery = (
        NewsView.objects
        .filter(article_id=OuterRef("pk"))
        .values("article_id")
        .annotate(count=Count("id"))
        .values("count")
    )

    liked_data_raw = NewsArticle.objects.filter(id__in=liked_ids).annotate(
        likes=Subquery(like_subquery, output_field=IntegerField()),
        read=Subquery(view_subquery, output_field=IntegerField())
    ).values("id", "title", "writer", "write_date", "likes", "read")

    liked_data = []
    for article in liked_data_raw:
        liked_data.append({
            "id": article["id"],
            "title": article["title"],
            "writer": article["writer"],
            "write_date": article["write_date"],
            "article_interaction": {
                "likes": article["likes"] or 0,
                "read": article["read"] or 0
            }
        })

    return Response({
        "category_stats": list(category_stats),
        "top_keywords": keyword_stats,
        "daily_views": daily_views,
        "liked_articles": liked_data
    })
