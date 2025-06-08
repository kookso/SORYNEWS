from django.urls import path
from .views import ChatbotView, ChatbotResetView

urlpatterns = [
    path("", ChatbotView.as_view(), name="news-chat"),
    path("reset/<int:article_id>/", ChatbotResetView.as_view(), name="news-chat-reset"),
]
