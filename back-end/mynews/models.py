from django.db import models
from django.contrib.auth import get_user_model
from pgvector.django import VectorField

User = get_user_model()

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    write_date = models.DateTimeField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    url = models.URLField(unique=True)
    summary = models.TextField()
    source = models.CharField(max_length=200)
    keywords = models.JSONField(default=list)
    embedding = VectorField(dimensions=1536, null=True)

    class Meta:
        db_table = "news_article"
        managed = False

class NewsLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "news_like"

class NewsView(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "news_view"
