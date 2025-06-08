"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

# 기본 페이지 뷰 함수
def home(request):
    return HttpResponse("Welcome to the homepage!")


urlpatterns = [
    path('', home),  # 빈 경로에 대한 URL 패턴
    path("health-check/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/article/", include("news_article.urls")),
    path("api/v1/interaction/", include("news_interaction.urls")),
    path("api/v1/dashboard/", include("news_dashboard.urls")),
    path("api/v1/search/", include("news_search.urls")),
    path("api/v1/chat/", include("news_chatbot.urls")),
]
