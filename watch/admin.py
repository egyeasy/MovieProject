from django.contrib import admin
from .models import Schedule, Movie, Comment
from .forms import SearchForm

# Register your models here.
admin.site.register(Schedule)
admin.site.register(Movie)
admin.site.register(Comment)