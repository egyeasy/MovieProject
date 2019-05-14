from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os, requests, json
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Schedule


# Create your views here.
@login_required
def index(request):
    return render(request, 'watch/index.html')


@login_required
def schedule(request):
    # 4. 4개 채널 편성표 크롤링
    # python file의 위치
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(table.prettify())

    # 목표 : 한 방송사가 한 행, 시간이 칼럼
    # date도 넣어주어야
    # db에 넣을 때 date, 방송사, 시간 - 영화 pair
    # '선샤인<1부>'같은건 링크 없으면 못 찾을 듯
    source = requests.get('https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q=cgv+편성표').text
    soup = BeautifulSoup(source, "html.parser")
    data = {}

    Days = soup.find('div', class_="tbl_head head_type2")
    dayList = []
    for day in Days.find_all('span'):
        # day.span.text하니까 여러 개가 뽑혀서 이렇게
        if len(day.text) == 5:
            # print(day, day.text)
            data[day.text] = {'cgv':{}, 'ocn' : {}, 'super_action' : {}, '스크린': {}}
            dayList.append(day.text)

    for channel in ['ocn', 'cgv', 'super+action', '스크린']:
        source = requests.get('https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q={}+편성표'.format(channel)).text
        soup = BeautifulSoup(source, "html.parser")

        table = soup.find('table', class_="tbl")
        if channel == 'super+action':
            channel = 'super_action'
        for tr in table.tbody.find_all('tr'):
            hour = tr.th.text[:3]
            # print(hour)
            i = 0
            for td in tr.find_all('td'):
                data[dayList[i]][channel][hour] = ''
                if td.dl:  # 이 시간에 새롭게 시작하는 영화가 있으면
                    minute = td.dl.dt.text  # 몇 분 시작인지 구하고
                    # 링크가 달려있는지, 영화인지 확인
                    if td.dl.dd.a and "tv-program" not in td.dl.dd.a.get('href'):
                        title = td.dl.dd.a.text
                        data[dayList[i]][channel][hour] = minute + ' ' + title
                i += 1
    print(data)
    
    # DB에 schedule 데이터 저장
    if not Schedule.objects.all():
        for date, channel_item in data.items():
            for channel, day_item in channel_item.items():
                for start_hour, each_movie in day_item.items():
                    if each_movie:
                        print("date", date, "channel", channel, "start_hour", start_hour, "each_movie", each_movie)
                        # print(hour)
                        # print(each_movie.split()[0])
                        splited_each_movie = each_movie.split()
                        start_minute = splited_each_movie[0]
                        splited_each_movie.pop(0)
                        title = ' '.join(splited_each_movie)
                        this_datetime = datetime.strptime('2019 ' + ' '.join(date.split('.')) + start_hour + ' ' + start_minute, '%Y %m %d %H %M')
                        Schedule.objects.create(title=title, channel=channel, datetime=this_datetime)
    
    context = {
        'data': data,
    }
    
    return render(request, 'watch/schedule.html', context)


@login_required
def zzim_list(request, user_name):
    
    return render(request, 'watch/zzim_list.html')


@login_required
def mypage(request, user_name):
    
    return render(request, 'watch/mypage.html')
    