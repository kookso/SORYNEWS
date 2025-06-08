from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions

from mynews.models import NewsLike, NewsView


# 뉴스 좋아요 등록/취소
@api_view(["POST", "PUT"])
@permission_classes([permissions.IsAuthenticated])
def news_like_view(request, article_id):
    user = request.user

    if request.method == "POST":
        if NewsLike.objects.filter(user=user, article_id=article_id).exists():
            return Response({"detail": "이미 좋아요를 눌렀습니다."}, status=400)

        like = NewsLike.objects.create(user=user, article_id=article_id)
        return Response({
            "id": like.id,
            "user_id": like.user_id,
            "article_id": like.article_id,
            "liked_at": like.liked_at
        }, status=201)

    elif request.method == "PUT":
        like = NewsLike.objects.filter(user=user, article_id=article_id).first()
        if not like:
            return Response({"detail": "좋아요 기록이 없습니다."}, status=404)
        like.delete()
        return Response({"message": "좋아요가 취소되었습니다."}, status=200)


# 뉴스 좋아요 수 조회
@api_view(["GET"])
def news_like_count_view(request, article_id):
    count = NewsLike.objects.filter(article_id=article_id).count()
    return Response({"article_id": article_id, "count": count})


# 뉴스 좋아요 여부 조회
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def news_like_status_view(request, article_id):
    user = request.user
    liked = NewsLike.objects.filter(user=user, article_id=article_id).exists()
    return Response({"article_id": article_id, "liked": liked})


# 뉴스 조회 등록
@api_view(["POST"])
def news_view_register_view(request, article_id):
    user = request.user if request.user.is_authenticated else None
    view = NewsView.objects.create(user=user, article_id=article_id)
    return Response({
        "id": view.id,
        "user_id": view.user_id,
        "article_id": view.article_id,
        "viewed_at": view.viewed_at,
    })


# 뉴스 조회 수 조회
@api_view(["GET"])
def news_view_count_view(request, article_id):
    count = NewsView.objects.filter(article_id=article_id).count()
    return Response({"article_id": article_id, "count": count})
