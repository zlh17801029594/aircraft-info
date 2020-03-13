#!/usr/bin/env python 
# _*_ coding:utf-8 _*_
import requests
import os
import re
from bs4 import BeautifulSoup as bs
import pymysql
import time, random, datetime
db = pymysql.connect("192.168.243.121", "root", "a1d#c3c#r4o9o9t%", "aims")
cursor = db.cursor()

log_path = 'log1'
err_log = 'err.txt'
abnormal_log = 'abnormal.txt'
info_log = 'info.txt'
sql_err_log = 'err.sql.txt'
# dict_csv = 'dict.csv'

def get_html(url):
    # random_time = random.randint(3, 5)
    # time.sleep(random_time)
    try:
        r = requests.get(url, timeout=15)
        r.encoding = r.apparent_encoding
        html = r.text
        return html
    except Exception as e:
        print("获取页面[%s]失败,失败原因[%s]" % (url, str(e)))
        with open(log_path + '/' + err_log, 'a', encoding='utf-8') as error_file:
            print("获取页面[%s]失败,失败原因[%s]" % (url, str(e)), file=error_file)
        return None


def get_continent_list(url):
    html = get_html(url)
    if html:
        soup = bs(html, 'html.parser')
        regions = soup.find('div', id='regions-list')
        head_list = regions.find('ul', class_='nav-tabs').find_all('li', recursive=False)
        head_dict = {}
        for item in head_list:
            head_dict[item.a['id']] = item.a.string
        body_list = regions.find('div', class_='mod-body').find_all('div', recursive=False)
        # 洲
        continent_list = []
        for item in body_list:
            country_temp_list = item.find('ul').find_all('li', recursive=False)
            country_list = []
            for item1 in country_temp_list:
                country_dict = {}
                country_name = item1.a.string.split('(', 1)
                country_dict['ch_name'] = country_name[0]
                if country_name[1]:
                    country_dict['en_name'] = country_name[1][:len(country_name[1])-1]
                country_dict['href'] = item1.a['href']
                country_list.append(country_dict)
            continent_dict = {}
            continent_name = item['id'].split('-')[0]
            continent_dict['ch_name'] = head_dict[continent_name]
            continent_dict['en_name'] = continent_name
            continent_dict['country'] = country_list
            continent_list.append(continent_dict)
        return continent_list
    else:
        return []


def save_aircraft(base_url, continent_list):
    for continent in continent_list:
        continent_ch_name = continent['ch_name']
        continent_en_name = continent['en_name']
        for country in continent['country']:
            country_ch_name = country['ch_name']
            country_en_name = country['en_name']
            country_url = base_url + country['href'] if country['href'] else None
            if country_en_name == 'China':
                country_url_list = ['http://airport.anseo.cn/c-china__page-{}'.format(str(i)) for i in range(3, 10)]
            elif country_en_name == 'Chile':
                country_url_list = ['http://airport.anseo.cn/c-chile__page-{}'.format(str(i)) for i in range(7, 17)]
            elif country_en_name == 'United States':
                country_url_list = ['http://airport.anseo.cn/c-usa__page-{}'.format(str(i)) for i in range(69, 745)]
            else:
                continue
            aircraft_list = get_aircraft_list(country['ch_name'], country_url_list)
            for aircraft in aircraft_list:
                sql = 'insert into aircraft_info_global(iata, icao, ch_name, en_name, city_ch_name, city_en_name, country_ch_name, country_en_name, region, continent_ch_name, continent_en_name, details_url, update_time) ' \
                      'value("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                    aircraft['iata'] if aircraft['iata'] else None,
                    aircraft['icao'] if aircraft['icao'] else None,
                    aircraft['airport_ch_name'] if aircraft['airport_ch_name'] else None,
                    aircraft['airport_en_name'] if aircraft['airport_en_name'] else None,
                    aircraft['city_ch_name'] if aircraft['city_ch_name'] else None,
                    aircraft['city_en_name'] if aircraft['city_en_name'] else None,
                    country_ch_name if country_ch_name else None,
                    country_en_name if country_en_name else None,
                    # 中国/外国
                    '中国' if '中国' in country_ch_name else '外国',
                    continent_ch_name if continent_ch_name else None,
                    continent_en_name if continent_en_name else None,
                    aircraft['details_url'] if aircraft['details_url'] else None,
                    # 插入时间
                    # datetime.datetime.fromtimestamp(time.time())
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                try:
                    cursor.execute(sql)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print("执行SQL[%s]失败,失败原因[%s]" % (sql, str(e)))
                    with open(log_path + '/' + sql_err_log, 'a', encoding='utf-8') as sql_error_file:
                        print("执行SQL[%s]失败,失败原因[%s]" % (sql, str(e)), file=sql_error_file)
                    continue



def iter_to_list(iter):
    temp_list = []
    for item in iter:
        temp_list.append(item.strip())
    return temp_list


def get_aircraft_list(country_ch_name, country_url_list):
    aircraft_list = []
    for next_url in country_url_list:
        html = get_html(next_url)
        if html:
            soup = bs(html, 'html.parser')
            data_div = soup.find('div', class_='aw-mod aw-topic-list')
            if data_div:
                data_trs = data_div.find('table', class_='ts-sorter table-bordered').find('tbody').find_all('tr', recursive=False)
                for data_tr in data_trs:
                    aircraft_dict = {}
                    data_tds = data_tr.find_all('td', recursive=False)
                    city_name = iter_to_list(data_tds[0].a.strings)
                    aircraft_dict['city_ch_name'] = city_name[0]
                    aircraft_dict['city_en_name'] = city_name[1]
                    aircraft_dict['details_url'] = data_tds[1].a['href']
                    airport_name = iter_to_list(data_tds[1].a.strings)
                    aircraft_dict['airport_ch_name'] = airport_name[0]
                    aircraft_dict['airport_en_name'] = airport_name[1]
                    aircraft_dict['iata'] = data_tds[2].a.string
                    aircraft_dict['icao'] = data_tds[3].a.string
                    aircraft_list.append(aircraft_dict)
            else:
                print("页面[%s]不正常" % (next_url))
                with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                    print("页面[%s]不正常" % (next_url), file=abnormal_file)
                continue
        else:
            continue
    print("已完整获取[%s]的所有机场信息，机场[%d]个" % (country_ch_name, len(aircraft_list)))
    with open(log_path + '/' + info_log, 'a', encoding='utf-8') as info_file:
        print("已完整获取[%s]的所有机场信息，机场[%d]个" % (country_ch_name, len(aircraft_list)), file=info_file)
    return aircraft_list


if __name__ == '__main__':
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    base_url = 'http://airport.anseo.cn'
    save_aircraft(base_url, get_continent_list(base_url))

