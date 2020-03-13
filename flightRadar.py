#!/usr/bin/env python 
# _*_ coding:utf-8 _*_

import os
import requests
from bs4 import BeautifulSoup as bs
import random, time, datetime
import pymysql
from fake_useragent import UserAgent
ua = UserAgent()# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}

log_path = 'log-flightradar'
err_log = 'err.txt'
abnormal_log = 'abnormal.txt'
info_log = 'info.txt'
sql_err_log = 'err.sql.txt'
db = pymysql.connect("192.168.243.121", "root", "a1d#c3c#r4o9o9t%", "aims")
cursor = db.cursor()


def get_html(url):
    headers = {'User-Agent': ua.random}
    random_time = random.randint(1, 2)
    time.sleep(random_time)
    try:
        r = requests.get(url, timeout=15, headers=headers)
        r.encoding = r.apparent_encoding
        html = r.text
        return html
    except Exception as e:
        print("获取页面[%s]失败,失败原因[%s]" % (url, str(e)))
        with open(log_path + '/' + err_log, 'a', encoding='utf-8') as error_file:
            print("获取页面[%s]失败,失败原因[%s]" % (url, str(e)), file=error_file)
        return None


def get_country_list(base_url):
    html = get_html(base_url)
    if html:
        soup = bs(html, 'html.parser')
        tbody = soup.find('table', id='tbl-datatable').find('tbody')
        trs = tbody.find_all(has_tile_and_href)
        country_list = []
        for i in range(1, len(trs)):
            country_dict = {}
            tds = trs[i].find_all('td')
            country_dict['country_en_name'] = tds[2].a.string.strip()
            country_dict['url'] = tds[2].a['href']
            country_dict['count'] = tds[3].span.string.strip().split(' ', 1)[0]
            country_list.append(country_dict)
        return country_list
    else:
        return []

def get_country_airport_info(country_url):
    html = get_html(country_url)
    if html:
        soup = bs(html, 'html.parser')
        table = soup.find('table', id='tbl-datatable')
        if table:
            trs = table.find('tbody').find_all(has_tile_and_href)
            airport_list = []
            for i in range(1, len(trs)):
                airport_dict = {}
                tds = trs[i].find_all('td')
                airport_dict['href'] = tds[1].a['href']
                details = iter_to_list(tds[1].a.stripped_strings)
                airport_dict['en_name'] = details[0]
                codes = details[1][1:len(details[1])-1].split('/', 1)
                try:
                    airport_dict['iata'] = codes[0]
                    airport_dict['icao'] = codes[1]
                except IndexError as e:
                    print("[%s]三码四码不正常，%s" % (airport_dict['en_name'], codes))
                    with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                        print("[%s]三码四码不正常，%s" % (airport_dict['en_name'], codes), file=abnormal_file)
                airport_list.append(airport_dict)
            return airport_list
        else:
            print("页面[%s]不正常" % (country_url))
            with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                print("页面[%s]不正常" % (country_url), file=abnormal_file)
            return []
    else:
        return []


def has_tile_and_href(tag):
    return tag.name == 'tr' and not tag.has_attr('id') and not tag.has_attr('class')


def iter_to_list(iter):
    temp_list = []
    for item in iter:
        temp_list.append(item.strip())
    return temp_list


def save_airport_info(airport_dict):
    country_en_name = airport_dict['country_en_name']
    sql = 'insert into aircraft_info_global_flightradar(iata, icao, en_name, country_en_name, details_url, region, update_time) ' \
          'value({},{},{},{},{},{},{})'.format(
        repr(airport_dict['iata']) if airport_dict['iata'] else None,
        repr(airport_dict['icao']) if airport_dict['icao'] else None,
        repr(airport_dict['en_name']) if airport_dict['en_name'] else None,
        repr(airport_dict['country_en_name']) if airport_dict['country_en_name'] else None,
        repr(airport_dict['href']) if airport_dict['href'] else None,
        # 中国/外国
        repr('中国') if country_en_name == 'China' or country_en_name == 'Hong Kong' or country_en_name == 'Macao' or country_en_name == 'Taiwan' else repr('外国'),
        # 插入时间
        # datetime.datetime.fromtimestamp(time.time())
        repr(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        db.rollback()
        print("执行SQL[%s]失败,失败原因[%s]" % (sql, str(e)))
        with open(log_path + '/' + sql_err_log, 'a', encoding='utf-8') as sql_error_file:
            print("执行SQL[%s]失败,失败原因[%s]" % (sql, str(e)), file=sql_error_file)


if __name__ == '__main__':
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    base_url = 'https://www.flightradar24.com/data/airports'
    # 获取country_url集合
    country_list = get_country_list(base_url)
    # 获取所有航班信息
    for country_dict in country_list:
        country_en_name = country_dict['country_en_name']
        # 统计country机场数
        count = country_dict['count']
        airport_list = get_country_airport_info(country_dict['url'])
        if int(count) != len(airport_list):
            print("[%s](%s)机场个数缺失 预计[%s]，实际[%d]" % (country_en_name, country_dict['url'], count, len(airport_list)))
            with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                print("[%s](%s)机场个数缺失 预计[%s]，实际[%d]" % (country_en_name, country_dict['url'], count, len(airport_list)), file=abnormal_file)
        country_dict['airport_info'] = airport_list
    # 将航班信息存入数据库
    for country_dict in country_list:
        for airport_dict in country_dict['airport_info']:
            airport_dict['country_en_name'] = country_dict['country_en_name']
            save_airport_info(airport_dict)