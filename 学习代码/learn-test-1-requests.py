#!/usr/bin/env python 
# _*_ coding:utf-8 _*_

import requests


def get_html(url):
    try:
        r = requests.get(url, timeout=15)
        #内容编码
        r.encoding = r.apparent_encoding
        html = r.text
        return html
    except Exception as e:
        print("获取页面[%s]失败,失败原因[%s]" % (url, str(e)))
        return None


if __name__ == '__main__':
    #url = 'http://airport.anseo.cn/c-china'
    url = 'https://www.flightradar24.com/data/airports'
    data = get_html(url)
    print(data)