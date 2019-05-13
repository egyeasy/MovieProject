# -*- coding: utf-8 -*-
from django.shortcuts import render
# Create your views here.
import requests
import time
import json
import urllib.request
from datetime import datetime
# 무조건 7개 날짜씩
# 날짜별로 matrix 만들기, 행은 채널, 칼럼은 시간
month = datetime.today().month
day = datetime.today().day
url = 'https://search.daum.net/search?nil_suggest=btn&w=tot&DA=SBC&q='+str(month)+'월+'+str(day)+'일+케이블+영화_편성표'
