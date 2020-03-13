#!/usr/bin/env python 
# _*_ coding:utf-8 _*_

import requests
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
from fake_useragent import UserAgent
import time,random
ua = UserAgent()


def get_html(url):
    headers = {'User-Agent': ua.random}
    random_time = random.randint(1, 2)
    time.sleep(random_time)
    try:
        r = requests.get(url, timeout=15, headers=headers)
        #内容编码
        r.encoding = r.apparent_encoding
        html = r.text
        return html
    except Exception as e:
        print("获取页面[%s]失败,失败原因[%s]" % (url, str(e)))
        return None


if __name__ == '__main__':
    url = 'http://airport.anseo.cn/c-usa__page-{}'
    #url = 'https://www.flightradar24.com/data/airports'
    total = 100
    count = 0
    for i in range(1,total):
        data = get_html(url.format(i))
        if data:
            count = count + 1
    print('请求%s次，成功%s次' % (total-1, count))
    #print(data)