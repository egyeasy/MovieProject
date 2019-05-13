from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    
    return render(request, 'watch/index.html')


def schedule(request):
    # 4. 4개 채널 편성표 크롤링
def find_movie(query_movie):
    # python file의 위치
def zzims
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


def zzim_list(request):
    pass


def mypage(request, user_name):
    pass
    