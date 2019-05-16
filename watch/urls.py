from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'watch'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('zzims/', views.zzim_list, name='zzim_list'),
    path('mypage/', views.mypage, name='mypage'),
    path('movies/<int:movie_id>/', views.movie_detail, name="movie_detail"),
    path('search_movie/', views.search_movie, name="search_movie"),
    # path('make_schedule/', views.make_schedule, name='make_schedule'),
    path('make_movie/', views.make_movie, name='make_movie'),
    path('go_to/<str:movie_name>/', views.go_to, name="go_to"),
    path('movies/<int:movie_id>/create_comment/', views.create_comment, name="create_comment"),
    url(r'^movie-autocomplete/', views.MovieAutocomplete.as_view(), name='movie-autocomplete'),
    path('schedule/search/', views.search_schedule, name='search_schedule'),
]