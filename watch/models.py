from django.db import models


# Create your models here.
class Schedule(models.Model):
    title = models.CharField(max_length=50)
    datetime = models.DateTimeField()
    channel = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.title} / {self.channel} / {self.datetime}"