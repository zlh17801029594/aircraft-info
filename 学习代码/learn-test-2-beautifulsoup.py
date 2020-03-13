#!/usr/bin/env python 
# _*_ coding:utf-8 _*_

import requests
from bs4 import BeautifulSoup as bs


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


def iter_to_list(iter):
    temp_list = []
    for item in iter:
        temp_list.append(item.strip())
    return temp_list


def get_airport_list(country_url):
    airport_list = []
    # 测试
    # country_url = 'http://airport.anseo.cn/c-burundi'
    next_url = country_url
    country_url_list = []
    for i in range(1, 10):
      country_url_list.append((country_url + '__page-{}').format(i))
    for next_url in country_url_list:
        html = get_html(next_url)
        if html:
            soup = bs(html, 'html.parser')
            data_div = soup.find('div', class_='aw-mod aw-topic-list')
            if data_div:
                data_trs = data_div.find('table', class_='ts-sorter table-bordered').find('tbody').find_all('tr', recursive=False)
                for data_tr in data_trs:
                    airport_dict = {}
                    data_tds = data_tr.find_all('td', recursive=False)
                    city_name = iter_to_list(data_tds[0].a.strings)
                    airport_dict['city_ch_name'] = city_name[0]
                    airport_dict['city_en_name'] = city_name[1]
                    airport_dict['details_url'] = data_tds[1].a['href']
                    airport_name = iter_to_list(data_tds[1].a.strings)
                    airport_dict['airport_ch_name'] = airport_name[0]
                    airport_dict['airport_en_name'] = airport_name[1]
                    airport_dict['iata'] = data_tds[2].a.string
                    airport_dict['icao'] = data_tds[3].a.string
                    #输出机场信息
                    print(airport_dict)
                    airport_list.append(airport_dict)
            else:
                print("页面[%s]加载不完整" % (next_url))
    return airport_list


if __name__ == '__main__':
    first_url = 'http://airport.anseo.cn/c-china'
    get_airport_list(first_url)