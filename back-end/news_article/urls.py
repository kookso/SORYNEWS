from django.urls import path
from . import views

urlpatterns = [
    path("", views.news_list_view, name="news-list"),
    path("<int:article_id>/", views.news_detail_view, name="news-detail"),
    path("<int:article_id>/related/", views.related_news_view, name="news-related"),
]
