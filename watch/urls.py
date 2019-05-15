from django.urls import path
from . import views

app_name = 'watch'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('zzims/<str:user_name>/', views.zzim_list, name='zzim_list'),
    path('mypage/<str:user_name>/', views.mypage, name='mypage'),
    path('movies/<int:movie_id>/', views.movie_detail, name="movie_detail"),
    path('make_schedule/', views.make_schedule, name='make_schedule'),
    path('make_movie/', views.make_movie, name='make_movie'),
]