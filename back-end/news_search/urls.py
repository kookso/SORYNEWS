from django.urls import path
from .views import search_news_view

urlpatterns = [
    path("", search_news_view, name="news-search"),
]
