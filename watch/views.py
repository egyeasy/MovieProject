from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import os, requests, json, random
from bs4 import BeautifulSoup
from datetime import datetime, date
from .models import Schedule, Movie
from .forms import SearchForm
from dal import autocomplete


# Create your views here.
def index(request):
    # index 배경 이미지 랜덤 선택
    background_image_cnt = 8
    background_num = random.randint(1, background_image_cnt)
    
    # 검색어 자동완성 Form
    form = SearchForm()
    
    # 찜한 영화가 스케쥴에 있는지
    zzim_ready = []
    if request.user.is_authenticated:
        zzimList = request.user.followers.all()
        today = datetime.now()
        print(today)
        max_date = Schedule.objects.all().order_by('-datetime')[0].datetime
        print("max date: ", max_date)
        #schedules = Schedule.objects.filter(datetime__range=(today, max_date))
        schedules = Schedule.objects.filter(datetime__date__gte=today)
        
        for zzim in zzimList:
            # 네이버 제목으로 바꿔
            for schedule in schedules:
                if zzim.title == schedule.title:
                    zzim_ready.append([zzim.title, schedule.datetime, schedule.channel])
    
    # 편성표 중 추천 영화 랜덤 선택
    schedules = Schedule.objects.all()
    recommend_schedule = 0
    recommend_movie = 0
    while not (recommend_schedule and recommend_movie):
        recommend_num = random.randint(schedules[0].id, schedules.order_by('-id')[0].id)
        recommend_schedule = Schedule.objects.get(pk=recommend_num)
        print(recommend_schedule)
        filter_list = Movie.objects.filter(title=recommend_schedule.title)
        if filter_list:
            recommend_movie = filter_list[0]
    context = {
        'zzim_ready' : zzim_ready,
        'background_url': f'image/index/{background_num}.jpg' if background_num == 2 or background_num == 3 else f'image/index/{background_num}.png',
        'recommend_schedule': recommend_schedule,
        'recommend_movie': recommend_movie,
        'recommend_datetime': recommend_schedule.datetime.strftime("%m/%d %a %H:%M"),
        'form': form,
    }
    return render(request, 'watch/index.html', context)
    


@login_required
def schedule(request):
    schedules = Schedule.objects.all().order_by('channel', 'datetime')
    
    
    
    context = {
        'schedules': schedules,
    }
    return render(request, 'watch/schedule.html', context)


# 'zzims/<str:user_name>/', views.zzim_list, name='zzim_list'
@login_required
def zzim_list(request, user_name):
    movies = Movie.objects.all()
    
    context = {
        'movies' : movies,
        # 'user_name' : user_name,
    }
    return render(request, 'watch/zzim_list.html', context)


@login_required
def mypage(request, user_name):
    
    return render(request, 'watch/mypage.html')


@login_required
def movie_detail(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    context = {
        'movie': movie,
    }
    return render(request, 'watch/movie_detail.html',)


class MovieAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Movie.objects.none()

        qs = Movie.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


def search_movie(request):
    query = request.POST.search
    
    
    
    return redirect('watch:index')



def make_movie(request):
    failed_list = []
    # python file의 위치
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(table.prettify())
    
    # 목표 : 한 방송사가 한 행, 시간이 칼럼
    # date도 넣어주어야
    # db에 넣을 때 date, 방송사, 시간 - 영화 pair
    # '선샤인<1부>'같은건 링크 없으면 못 찾을 듯
    
    # 일주일치
    
    #### 채널 원래대로 다 넣어놓고, movie_title 구한 후 해당 movie_title이 없을 때 movie info 검색
    #### 영어 + 한글에서 한글 남겨둬야 할 수도...? 뭘 버려야 
    #### 유명한 시리즈물은 미리 DB에 넣어두어도 될 것 같다 -> 분노의 질주
    def make_schedule_for_seven_days():
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
        
        def cleanedTitle(Title):
            Title = Title.strip()
            flag = False
            for j in range(len(Title)):
                #[오스카4관왕]버드맨
                if Title[3] == '[':
                    # 뒤에 진짜 제목이 있어야 해
                    for jj in range(4, len(Title)-1):
                        if Title[jj] == ']':
                            flag = True
                            # [007시리즈]007카지노로얄 <3부>, 십의 자리까지 있는 부는 없겠지
                            # [영상미폭발] 알로하 <1부>
                            if Title[len(Title)-2:len(Title)]=='부>' and 49 <= ord(str(Title[len(Title)-3])) <= 57:
                                Title = '영화' + Title[jj+1:len(Title)-4]
                                break
                            else:
                                Title = '영화' + Title[jj+1:len(Title)]
                                break
                    # 바깥쪽 for문 깨기
                    if flag:
                        break
                # R.I.P.D.유령퇴치전담반 : 영어만 쓴다
                if 97 <= ord(Title[3]) <= 122 or 65 <= ord(Title[3]) <= 90:
                    end_point = 3
                    for jj in range(3, len(Title)):
                        # 숫자인 것도 넣어야, GP506
                        if 97 <= ord(Title[jj]) <= 122 or 65 <= ord(Title[jj]) <= 90 or  48 <= ord(Title[jj]) <= 56:
                            end_point = jj
                    Title = Title[:end_point+1]
                    break
                
                # 브이아이피(V.I.P)라고 치면 검색이 제대로 이루어지지 않아서 추가, 등등 괄호 빼버리기
                if Title[j] == '(':
                    Title = Title[:j]
                    break
                # '잭 리처2:네버 고 백'인데 이렇게 검색하면 잘 안 나와, 잭 리처:네버 고 백 이어야
                # 이렇게 하면 쥬라기 공원2가 망해 -> 그냥 잭 리처2, 쥬라기 공원2로만 검색한다
                # 시리즈물일 때, :이나 - 다음 부제 나올 때 부제 빼버려
                #  or Title[j+1] == '-' : 이거 조건에서 지워야지
                if 48 <= ord(str(Title[j])) <= 57 and j>0:
                    if j+1<len(Title)-1 and (Title[j+1] == ':'):
                        Title = Title[:j]
                        break
                    elif j+2 < len(Title)-1 and (Title[j+2] == ':'):
                        Title = Title[:j+1]            
                        break
    
                if (j+5 <= len(Title)-1) and Title[j:j+6] == '분노의 질주':
                    if j+5 == len(Title)-1:
                        Title = '분노의 질주1'
                        break
                    elif (48 > ord(str(Title[j+6])) or ord(str(Title[j+6])) > 57) and ('부>' in Title):
                        Title = '분노의 질주1'
                        break
                        
                if Title[j:] == '<1부>' or Title[j:] == '<2부>':
                    Title = Title[:j]
                    break
    
            print("cleaned Title :",Title)
            return Title
    
        # beautifulSoup으로 파싱한 것 인자로
        def movieInfo(searchTitle, searchMovie):
            # movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director
            ProductionYear = runnningTime = score = 0
            movieTitle = posterURL = genre = country = audience = content = director = ''
            # 마지막에 try, except
            box = searchMovie.find("div", class_="api_subject_bx _au_movie_info")
            try:
                movieTitle = box.find("div", class_="main_spot_wrap").find("h2", class_="movie_title").text
                if Movie.objects.filter(title=movieTitle):
                    return
                ProductionYear = box.find("span", class_="movie_sub_title").text
                # 오류대비
                is_year = False
                for i in range(len(ProductionYear)-1,-1,-1):
                    if 48 <= ord(str(ProductionYear[i])) <= 57:
                        is_year = True
                        ProductionYear = int(ProductionYear[i-3:i+1])
                        break
            except:
                 # 다음 : 쥬라기 공원 2 : 잃어버린 세계, naver : 쥬라기 공원 2 - 잃어버린 세계
                try:
                    movieTitle = box.find("div", class_="detail_info").find("strong", class_="title").text
                except:
                    # movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director
                    return
        
            unboxing = box.find("div", class_="main_info _lp_animation").find("div", class_="detail_info").dl
            print(movieTitle)
            posterURL = box.find("div", class_="main_info _lp_animation").a.img.get('src')
            
            
            ddPack = unboxing.find_all("dd")
            # span만 들어있다
            for i in range(len(ddPack)-1):
                print(ddPack[i])
            
            info = []
            for el in ddPack[0].find_all("span"):
                if el.text:
                    info.append(el.text)
            if len(info) ==3:
                genre = info[0]
                country = info[1]
                runningTime = int(info[2][:len(info[2])-1])
            else:
                genre = country = ""
                runningTime = None
            if ProductionYear == None:
                try:
                    ProductionYear = int(ddPack[1][:4])
                except:
                    ProductionYear = None
            try:
                score = float(ddPack[2].find("span", class_="star_count").text)
            except:
                score = None
            # 쥬라기 공원에 관객 수 없었어, 원래 0번째부터 있을 때 3번째에 있었는데
            # 별달리 특정할 수 있는 class가 없어서 이렇게 해본다.
            if len(ddPack) == 5: # 관객 수 있을 때
                audience = ddPack[3].text
                content = ddPack[4].find("span", class_="_text").text
            elif len(ddPack) == 4:
                audience = ""
                content = ddPack[3].find("span", class_="_text").text
            else:
                audience = ""
                content = box.find("div", class_="main_info _lp_animation").find("div", class_="detail_info").find("span", class_="_text").text
            try:
                director = searchMovie.find("ul", class_="api_list_scroll movie_list_scroll").find("li", class_="bx").find("strong", class_="name").text
            except: #잭 리처2:네버 고 백 버려
                director = ""
            print()
            print("제목:", movieTitle, "포스터:", posterURL, "제작연도:", ProductionYear, "장르:", genre)
            print("국가:", country, "상영시간:", runningTime, "평점:", score, "관객 수:", audience, "설명:", content, "감독:", director)
            print()
            if not Movie.objects.filter(title=movieTitle):
                Movie.objects.create(title=movieTitle, posterUrl=posterURL, productionYear=ProductionYear, genre=genre, \
                            country=country, runningTime=runningTime, score=score, audience=audience, content=content, director=director)
            
            return movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director
        
        def not_movie(td):
            title = td.dl.dd.find("span").text
            # 데어데블 10회
            for t in range(len(title)):
                if 48 <= ord(title[t]) <= 57 and t+1 < len(title) and title[t+1] == '회':
                    return True
    
        # DB에 현금사냥꾼, 캐리비안, RIPD movie Info 넣기
        # 잠시 ocn, cgv 을 빼놓는다.
        # 시간 순으로 들어간다(시간 -> 날짜 ), 가장 크게는 ocn, cgv, super_action, 스크린 순으로 크롤링된다. 
        # 분노의 질주 검색하면 아직 개봉하지 않은 영화 분노의 질주:홉스&쇼가 나와                             
        
        # 크롤링 실패한 영화
            
    
        for channel in ['ocn', 'cgv', 'super+action', '스크린']:
            source = requests.get('https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q={}+편성표'.format(channel)).text
            soup = BeautifulSoup(source, "html.parser")
    
            table = soup.find('table', class_="tbl")
            if channel == 'super+action':
                channel = 'super_action'
            for tr in table.tbody.find_all('tr'):
                hour = tr.th.text[:3]
                i = 0
                for td in tr.find_all('td'):
                    data[dayList[i]][channel][hour] = ''
                    if td.dl:  # 이 시간에 새롭게 시작하는 영화가 있으면
                        minute = td.dl.dt.text  # 몇 분 시작인지 구하고
                        # 링크가 달려있는지, 영화인지 확인
                        if td.dl.dd.a and "tv-program" not in td.dl.dd.a.get('href'):
                            title = td.dl.dd.a.text
                            # 1부, 2부 구별하고 저장
                            data[dayList[i]][channel][hour] = minute + ' ' + title
                            # 다음 영화 정보에서 title 가져다가 검색한다.
                            search = requests.get('https://search.daum.net/search' + td.dl.dd.a.get('href')).text
                            searchM = BeautifulSoup(search, "html.parser")
                            movieTitle = '영화 '+ searchM.find("div",{"id":"movieTitle"}).a.b.text
                            if '캐리비안의 해적 :' in movieTitle:
                                movieTitle = movieTitle[:8+3] + '-' + movieTitle[11+3:]
                            movieTitle = cleanedTitle(movieTitle)
                            search = requests.get('https://m.search.naver.com/search.naver?query={}'.format(movieTitle)).text
                            searchM = BeautifulSoup(search, "html.parser")
                            result = movieInfo(movieTitle, searchM)
                            if result:
                                movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director = result
                                print("익셉트 트라이",  channel, '날짜', dayList[i], '시간', hour, '분', minute, '타이틀편성표', titleInSchedule, '타이틀네이버', movieTitle)
                                this_datetime = datetime.strptime('2019 ' + ' '.join(dayList[i].split('.')) + hour + ' ' + minute, '%Y %m %d %H %M')
                                Schedule.objects.create(title=movieTitle, channel=channel, datetime=this_datetime)
    
                        # 링크가 있고 tv 프로그램인게 명백한 경우
                        elif td.dl.dd.a and "tv-program" in td.dl.dd.a.get('href'):
                            pass
                        # 데어데블 10회
                        elif not_movie(td):
                            pass
                        # 영화인지 본격적으로 체크
                        else:
                            # 영화를 붙일 때 성공률이 더 높다
                            titleInSchedule = "영화 " + td.dl.dd.find("span").text
                            # title은 영화인지 검사할 때 쓰는 키워드일뿐 편성표에 넣을 때는 titleInSchedule로 넣는다
                            title = titleInSchedule
    
                            if "감독판" in title:
                                for j in range(len(title)):
                                    if title[j:j+3] == "감독판":
                                        title = title[:j]
                                        print(title)
                                        break
                                title = cleanedTitle(title)
                                print(title)
                                data[dayList[i]][channel][hour] = minute + ' ' + title[3:]
                                search = requests.get('https://m.search.naver.com/search.naver?query={}'.format(title)).text
                                searchM = BeautifulSoup(search, "html.parser")
                                result = movieInfo(title, searchM)
                                if result:
                                    movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director = result
                                    print("감독판",  channel, '날짜', dayList[i], '시간', hour, '분', minute, '타이틀편성표', titleInSchedule, '타이틀네이버', movieTitle)
                                    this_datetime = datetime.strptime('2019 ' + ' '.join(dayList[i].split('.')) + hour + ' ' + minute, '%Y %m %d %H %M')
                                    Schedule.objects.create(title=movieTitle, channel=channel, datetime=this_datetime)
                            elif ("영화 바운티 헌터스: 현금사냥꾼" in title) or ("R.I.P.D" in title):
                                data[dayList[i]][channel][hour] = minute + ' ' + title[3:]
                                print("바운티 헌터스 익셉션", channel, '날짜', dayList[i], '시간', hour, '분', minute, '타이틀편성표', titleInSchedule)
                                this_datetime = datetime.strptime('2019 ' + ' '.join(dayList[i].split('.')) + hour + ' ' + minute, '%Y %m %d %H %M')
                                if "영화 바운티 헌터스: 현금사냥꾼" in title:
                                    Schedule.objects.create(title="바운티 헌터스: 현상금사냥꾼", channel=channel, datetime=this_datetime)
                                else:
                                    Schedule.objects.create(title="R.I.P.D. : 알.아이.피.디.", channel=channel, datetime=this_datetime)
                            else:
                                title = cleanedTitle(title)
                                temp = requests.get('https://m.search.naver.com/search.naver?query={}'.format(title)).text
                                temp2 = BeautifulSoup(temp, 'html.parser')
    
                                temp1 = requests.get('https://m.search.naver.com/search.naver?query={}'.format(title[3:])).text
                                temp22 = BeautifulSoup(temp1, 'html.parser')
                                # 검색했을 때 영화가 바로 뜨는 경우
                                try:
                                    # text가 있으면 영화인 것
                                    movie_title = temp2.find("div", class_="title_area _lp_load _lp_animation").find("h2", class_="movie_title").text
                                    print(11111111,title)
                                    data[dayList[i]][channel][hour] = minute + ' ' + titleInSchedule[3:]
                                    movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director = movieInfo(title, temp2)
                                    print("트라이", channel, '날짜', dayList[i], '시간', hour, '분', minute, '타이틀편성표', titleInSchedule, '타이틀네이버', movieTitle)
                                    this_datetime = datetime.strptime('2019 ' + ' '.join(dayList[i].split('.')) + hour + ' ' + minute, '%Y %m %d %H %M')
                                    Schedule.objects.create(title=movieTitle, channel=channel, datetime=this_datetime)
                                except:
                                    try:
                                        movie_title = temp22.find("div", class_="title_area _lp_load _lp_animation").find("h2", class_="movie_title").text
                                        print(22222222222, title[3:])
                                        data[dayList[i]][channel][hour] = minute + ' ' + titleInSchedule[3:]
                                        result = movieInfo(title[3:], temp22)
                                        if result:
                                            movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director = result
                                            print("익셉트 트라이", '날짜', dayList[i], channel, '시간', hour, '분', minute, '타이틀편성표', titleInSchedule, '타이틀네이버', movieTitle)
                                            this_datetime = datetime.strptime('2019 ' + ' '.join(dayList[i].split('.')) + hour + ' ' + minute, '%Y %m %d %H %M')
                                            Schedule.objects.create(title=movieTitle, channel=channel, datetime=this_datetime)
                                    except:
                                        try:
                                            is_movie = temp22.find("div", class_="api_subject_bx _au_movie_info").find("h2", class_="api_title").text
                                            print(33333, title[3:])
                                            if "영화" in is_movie:
                                                data[dayList[i]][channel][hour] = minute + ' ' + titleInSchedule[3:]
                                                result = movieInfo(title[3:], temp22)
                                                if result:
                                                    movieTitle, posterURL, ProductionYear, genre, country, runningTime, score, audience, content, director = result
                                                    print("익셉트 익셉트 트라이", channel, '날짜', dayList[i], '시간', hour, '분', minute, '타이틀편성표', titleInSchedule, '타이틀네이버', movieTitle)
                                                    this_datetime = datetime.strptime('2019 ' + ' '.join(dayList[i].split('.')) + hour + ' ' + minute, '%Y %m %d %H %M')
                                                    Schedule.objects.create(title=movieTitle, channel=channel, datetime=this_datetime)
                                                    
                                                    
                                        except:
                                            print("크롤링 실패한 영화입니다: ", title)
                                            failed_list.append(title)
                    i += 1
        return data
    data = make_schedule_for_seven_days()
    print(data)
    print("failed:", failed_list)
    
    # DB에 schedule 데이터 저장
    # for date, channel_item in data.items():
    #     for channel, day_item in channel_item.items():
    #         for start_hour, each_movie in day_item.items():
    #             if each_movie:
    #                 print("date", date, "channel", channel, "start_hour", start_hour, "each_movie", each_movie)
    #                 # print(hour)
    #                 # print(each_movie.split()[0])
    #                 splited_each_movie = each_movie.split()
    #                 start_minute = splited_each_movie[0]
    #                 splited_each_movie.pop(0)
    #                 title = ' '.join(splited_each_movie)
    #                 this_datetime = datetime.strptime('2019 ' + ' '.join(date.split('.')) + start_hour + ' ' + start_minute, '%Y %m %d %H %M')
    #                 Schedule.objects.create(movie=title, channel=channel, datetime=this_datetime)


    return redirect('watch:schedule')
    
    
    
    
    
# @login_required
# def make_schedule(request):
#     # python file의 위치
#     # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     # print(table.prettify())
    
#     # 목표 : 한 방송사가 한 행, 시간이 칼럼
#     # date도 넣어주어야
#     # db에 넣을 때 date, 방송사, 시간 - 영화 pair
#     # '선샤인<1부>'같은건 링크 없으면 못 찾을 듯
#     source = requests.get('https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q=cgv+편성표').text
#     soup = BeautifulSoup(source, "html.parser")
#     data = {}
    
#     Days = soup.find('div', class_="tbl_head head_type2")
#     dayList = []
#     for day in Days.find_all('span'):
#         # day.span.text하니까 여러 개가 뽑혀서 이렇게
#         if len(day.text) == 5:
#             # print(day, day.text)
#             data[day.text] = {'cgv':{}, 'ocn' : {}, 'super_action' : {}, '스크린': {}}
#             dayList.append(day.text)
    
#     def not_movie(td):
#         title = td.dl.dd.find("span").text
#         # 데어데블 10회
#         for t in range(len(title)):
#             if 48 <= ord(title[t]) <= 57 and t+1 < len(title) and title[t+1] == '회':
#                 return True
                                    
#     for channel in ['ocn', 'cgv', 'super+action', '스크린']:
#         source = requests.get('https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q={}+편성표'.format(channel)).text
#         soup = BeautifulSoup(source, "html.parser")
    
#         table = soup.find('table', class_="tbl")
#         if channel == 'super+action':
#             channel = 'super_action'
#         for tr in table.tbody.find_all('tr'):
#             hour = tr.th.text[:3]
#             i = 0
#             for td in tr.find_all('td'):
#                 data[dayList[i]][channel][hour] = ''
#                 if td.dl:  # 이 시간에 새롭게 시작하는 영화가 있으면
#                     minute = td.dl.dt.text  # 몇 분 시작인지 구하고
#                     # 링크가 달려있는지, 영화인지 확인
#                     if td.dl.dd.a and "tv-program" not in td.dl.dd.a.get('href'):
#                         title = td.dl.dd.a.text
#                         if len(title)>=4 and title[len(title)-4:] == '<1부>' or title[len(title)-4:] == '<2부>':
#                             title = title[:len(title)-4]
#                         data[dayList[i]][channel][hour] = minute + ' ' + title
#                     # 링크가 있고 tv 프로그램인게 명백한 경우
#                     elif td.dl.dd.a and "tv-program" in td.dl.dd.a.get('href'):
#                         pass
#                     # 데어데블 10회
#                     elif not_movie(td):
#                         pass
#                     # 영화인지 본격적으로 체크
#                     else:
#                         # 영화를 붙일 때 성공률이 더 높다
#                         titleInSchedule = "영화 " + td.dl.dd.find("span").text
#                         # title은 영화인지 검사할 때 쓰는 키워드일뿐 편성표에 넣을 때는 titleInSchedule로 넣는다
#                         title = titleInSchedule
#                         if "감독판" in title:
#                             data[dayList[i]][channel][hour] = minute + ' ' + title[3:]
#                         else:
#                             # 브이아이피(V.I.P)라고 치면 검색이 제대로 이루어지지 않아서 추가
#                             for j in range(len(title)):
#                                 #[오스카4관왕]버드맨
#                                 if title[3] == '[':
#                                     # 뒤에 진짜 제목이 있어야 해
#                                     for jj in range(4, len(title)-1):
#                                         if title[jj] == ']':
#                                             flag = True
#                                             # [007시리즈]007카지노로얄 <3부>, 십의 자리까지 있는 부는 없겠지
#                                             # [영상미폭발] 알로하 <1부>
#                                             if title[len(title)-2:len(title)]=='부>' and 49 <= ord(str(title[len(title)-3])) <= 57:
#                                                 title = '영화' + title[jj+1:len(title)-4]
#                                                 break
#                                             else:
#                                                 title = '영화' + title[jj+1:len(title)]
#                                                 break
#                                     # 바깥쪽 for문 깨기
#                                     if flag:
#                                         break
#                                 # R.I.P.D.유령퇴치전담반 : 영어만 쓴다
#                                 if 97 <= ord(title[3]) <= 122 or 65 <= ord(title[3]) <= 90:
#                                     end_point = 3
#                                     for jj in range(3, len(title)):
#                                         if 97 <= ord(title[jj]) <= 122 or 65 <= ord(title[jj]) <= 90:
#                                             end_point = jj
#                                     title = title[:end_point+1]
#                                     break
#                                 if title[j] == '(':
#                                     title = title[:j]
#                                     break
#                                 # 괄호 안의 영어만 없애고 싶을 때
#                                 # if 97 <= ord(title[j]) <= 122 or 65 <= ord(title[j]) <= 90:
#                                 #     title = title[:j-1]
#                                 #     break
#                                 if title[j:] == '<1부>' or title[j:] == '<2부>':
#                                     title = title[:j]
#                                     break
                            
#                             temp = requests.get('https://m.search.naver.com/search.naver?query={}'.format(title)).text
#                             temp2 = BeautifulSoup(temp, 'html.parser')
    
#                             temp1 = requests.get('https://m.search.naver.com/search.naver?query={}'.format(title[3:])).text
#                             temp22 = BeautifulSoup(temp1, 'html.parser')
#                             # 검색했을 때 영화가 바로 뜨는 경우
#                             # try:
#                                 # print(temp2)
#                                 # print(temp2.find("div", class_="title_area _lp_load _lp_animation"))
#                             try:
#                                 movie_title = temp2.find("div", class_="title_area _lp_load _lp_animation").find("h2", class_="movie_title").text
#                                 data[dayList[i]][channel][hour] = minute + ' ' + titleInSchedule[3:]
#                             except:
#                                 try:
#                                     movie_title = temp22.find("div", class_="title_area _lp_load _lp_animation").find("h2", class_="movie_title").text
#                                     data[dayList[i]][channel][hour] = minute + ' ' + titleInSchedule[3:]
#                                 except:
#                                     try:                                        
#                                         is_movie = temp22.find("div", class_="api_subject_bx _au_movie_info").find("h2", class_="api_title").text
#                                         if "영화" in is_movie:
#                                             data[dayList[i]][channel][hour] = minute + ' ' + titleInSchedule[3:]
#                                     except:
#                                         print(555555555, title)
    
#                 i += 1
    
#     print(data)
    
#     # with open(os.path.join(BASE_DIR, 'schedule.json'), 'w+', encoding="utf-8") as json_file:
#     #     # 화면에 직접 출력할 때는 dumps, file로 저장할 때는 dump
#     #     json.dump(data, json_file, ensure_ascii=False, indent="\t")
        
#     # DB에 schedule 데이터 저장
#     if not Schedule.objects.all():
#         for date, channel_item in data.items():
#             for channel, day_item in channel_item.items():
#                 for start_hour, each_movie in day_item.items():
#                     if each_movie:
#                         print("date", date, "channel", channel, "start_hour", start_hour, "each_movie", each_movie)
#                         # print(hour)
#                         # print(each_movie.split()[0])
#                         splited_each_movie = each_movie.split()
#                         start_minute = splited_each_movie[0]
#                         splited_each_movie.pop(0)
#                         title = ' '.join(splited_each_movie)
#                         this_datetime = datetime.strptime('2019 ' + ' '.join(date.split('.')) + start_hour + ' ' + start_minute, '%Y %m %d %H %M')
#                         Schedule.objects.create(title=title, channel=channel, datetime=this_datetime)

#     return redirect('watch:schedule')
