from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from watch.models import Movie

# Create your views here.
def signup(request):
    # 회원가입 시키기
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('watch:index')
    # 회원가입 폼 보여주기
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login(request):
    if request.method == "POST":
        # 실제 로그인(세션에 유저 정보를 넣는다.)
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
        return redirect('watch:index')
    else:
        # 유저로부터 username과 비밀번호를 받는다.
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('watch:index')

# 'zzims/<str:user_name>/', views.zzim_list, name='zzim_list'
@login_required
def follow(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if movie in request.user.followers.all():
        request.user.followers.remove(movie)
    else:
        request.user.followers.add(movie)
    return redirect('watch:zzim_list', request.user.username)