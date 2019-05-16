from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django_extensions.db.models import TimeStampedModel


# Create your models here.
class Schedule(models.Model):
    title = models.CharField(max_length=50)
    datetime = models.DateTimeField()
    channel = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.id} / {self.title} / {self.channel} / {self.datetime}"
        
class Movie(models.Model):
    title = models.CharField(max_length=50)
    posterUrl = models.TextField(blank=True)
    productionYear = models.IntegerField(default=0, null=True)
    genre = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    runningTime = models.IntegerField(default=0, null=True)
    # 10점만점
    score = models.DecimalField(decimal_places=2, max_digits=10, default=0, null=True)
    # 1.6만명, 단위가 만 명이라능
    audience = models.CharField(max_length=20, blank=True)
    content = models.TextField(blank=True)
    director = models.CharField(max_length=50, blank=True)
    follows = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers', blank=True)

    def __str__(self):
        # return f"{self.id} / {self.title}"
        return f"{self.title}"

class Comment(models.Model):
    content = models.CharField(max_length=140, blank=True)
    score = models.IntegerField(validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_comments', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name="movie_comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def _str__(self):
        return self.content

    
class QueryModel(models.Model):
    content = models.ForeignKey(Movie, on_delete=models.CASCADE)