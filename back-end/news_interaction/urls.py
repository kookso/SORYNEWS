from django.urls import path
from . import views

urlpatterns = [
    # 좋아요
    path("like/<int:article_id>/", views.news_like_view, name="news-like"),
    path("like/<int:article_id>/count/", views.news_like_count_view, name="news-like-count"),
    path("like/<int:article_id>/status/", views.news_like_status_view, name="news-like-status"),

    # 조회
    path("view/<int:article_id>/", views.news_view_register_view, name="news-view"),
    path("view/<int:article_id>/count/", views.news_view_count_view, name="news-view-count"),
]
