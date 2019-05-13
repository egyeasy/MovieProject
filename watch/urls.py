from django.urls import path
from . import views

app_name = 'watch'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('zzims/<str:user_name>/', views.zzim_list, name='zzim_list'),
    path('mypage/<str:user_name>/', views.mypage, name='mypage'),
]