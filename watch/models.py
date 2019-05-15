from django.db import models
from django.conf import settings


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
    productionYear = models.IntegerField(default=0)
    genre = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    runningTime = models.IntegerField(default=0)
    # 10점만점
    score = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    # 1.6만명, 단위가 만 명이라능
    audience = models.CharField(max_length=20, blank=True)
    content = models.TextField(blank=True)
    director = models.CharField(max_length=50, blank=True)
    follows = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers', blank=True)
    
    def __str__(self):
        # return f"{self.id} / {self.title}"
        return f"{self.id} / {self.title} / {self.productionYear} / {self.genre} / {self.country} / {self.runningTime} / {self.score} / {self.audience} / {self.director}"


class SearchQuery(models.Model):
    content = models.CharField(max_length=50)
    