#!/usr/bin/env python 
# _*_ coding:utf-8 _*_

import os
import requests
from bs4 import BeautifulSoup as bs
import random, time, datetime
import pymysql
from fake_useragent import UserAgent
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
ua = UserAgent()
log_path = 'log-flightradar-aircraft'
err_log = 'err.txt'
abnormal_log = 'abnormal.txt'
info_log = 'info.txt'
sql_err_log = 'err.sql.txt'
db = pymysql.connect("192.168.243.121", "root", "a1d#c3c#r4o9o9t%", "aims")
cursor = db.cursor()

base_url = 'https://www.flightradar24.com'


def get_html(url):
    headers = {'User-Agent': ua.random}
    random_time = random.randint(3, 5)
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


def save_aircraft_flight_info(aircraft_flight_dict):
    sql = 'insert into aircraft_flight_info(flight_num, type_code, aircraft, airline, mode_s, msn, code12, code13, code22, code23, details_url, update_time) ' \
          'value({},{},{},{},{},{},{},{},{},{},{},{})'.format(
        repr(aircraft_flight_dict['flight_num']) if aircraft_flight_dict['flight_num'] else 'null',
        repr(aircraft_flight_dict['type_code']) if aircraft_flight_dict['type_code'] else 'null',
        repr(aircraft_flight_dict['aircraft']) if aircraft_flight_dict.get('aircraft') else 'null',
        repr(aircraft_flight_dict['airline']) if aircraft_flight_dict['airline'] else 'null',
        repr(aircraft_flight_dict['mode_s']) if aircraft_flight_dict.get('mode_s') else 'null',
        repr(aircraft_flight_dict['msn']) if aircraft_flight_dict['msn'] else 'null',
        repr(aircraft_flight_dict['code12']) if aircraft_flight_dict.get('code12') else 'null',
        repr(aircraft_flight_dict['code13']) if aircraft_flight_dict.get('code13') else 'null',
        repr(aircraft_flight_dict['code22']) if aircraft_flight_dict.get('code22') else 'null',
        repr(aircraft_flight_dict['code23']) if aircraft_flight_dict.get('code23') else 'null',
        repr(aircraft_flight_dict['href']) if aircraft_flight_dict['href'] else None,
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


def get_aircraft_type_url_list(url):
    html = get_html(url)
    if html:
        soup = bs(html, 'html.parser')
        trs = soup.find('table', class_='table table-condensed data-table').find('tbody').find_all('tr', class_='border-top')
        url_list = []
        for tr in trs:
            url_list.append(base_url + tr.a['href'])
        return url_list
    else:
        return []


def get_aircraft_flight_list(url):
    html = get_html(url)
    if html:
        soup = bs(html, 'html.parser')
        table = soup.find('table', class_='table table-condensed table-hover data-table')
        if table:
            trs = table.tbody.find_all('tr')
            aircraft_flight_list = []
            for tr in trs:
                aircraft_flight_dict = {}
                tds = tr.find_all('td')
                aircraft_flight_dict['msn'] = tds[0].string.strip() if tds[0].string else None
                aircraft_flight_dict['type_code'] = tds[1].string.strip() if tds[1].string else None
                aircraft_flight_dict['flight_num'] = tds[2].string.strip() if tds[2].string else None
                aircraft_flight_dict['href'] = base_url + tds[2].a['href']
                aircraft_flight_dict['airline'] = tds[3].text.strip() if tds[3].text else None
                aircraft_flight_list.append(aircraft_flight_dict)
            return aircraft_flight_list
        else:
            print("页面[%s]不正常" % (url))
            with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                print("页面[%s]不正常" % (url), file=abnormal_file)
            return []
    else:
        return []


def get_aircraft_flight_info(aircraft_flight_dict):
    url = aircraft_flight_dict['href']
    html = get_html(url)
    if html:
        soup = bs(html, 'html.parser')
        div = soup.find('div', class_='col-md-6 n-p')
        if div:
            div = div.find('div', id='cnt-aircraft-info')
            div1 = div.find('div', class_='col-xs-5 n-p')
            div2 = div.find('div', class_='col-xs-7')
            div1_children = div1.find_all('div', recursive=False)
            aircraft = div1_children[0].span.string
            aircraft_flight_dict['aircraft'] = aircraft.strip() if aircraft else None
            div2_1 = div2.find('div', class_='col-sm-5 n-p')
            div2_2 = div2.find('div', class_='col-sm-7 n-p')
            div2_1_children = div2_1.find_all('div', recursive=False)
            code1 = div2_1_children[1].span.string.strip()
            code2 = div2_1_children[2].span.string.strip()
            if code1 != '-':
                code1s = code1.split('/', 1)
                try:
                    aircraft_flight_dict['code12'] = code1s[0].strip() if code1s[0] else None
                    aircraft_flight_dict['code13'] = code1s[1].strip() if code1s[1] else None
                except IndexError as e:
                    print("第一类[%s]二码三码不正常，%s" % (url, code1s))
                    with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                        print("第一类[%s]二码三码不正常，%s" % (url, code1s), file=abnormal_file)
            if code2 != '-':
                code2s = code2.split('/', 1)
                try:
                    aircraft_flight_dict['code22'] = code2s[0].strip() if code2s[0] else None
                    aircraft_flight_dict['code23'] = code2s[1].strip() if code2s[1] else None
                except IndexError as e:
                    print("第二类[%s]二码三码不正常，%s" % (url, code2s))
                    with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                        print("第二类[%s]二码三码不正常，%s" % (url, code2s), file=abnormal_file)
            div2_2_children = div2_2.find_all('div', recursive=False)
            mode_s = div2_2_children[0].span.string
            aircraft_flight_dict['mode_s'] = mode_s.strip() if mode_s else None
        else:
            print("页面[%s]不正常,flight_num[%s]详情信息需要补充" % (url, aircraft_flight_dict['flight_num']))
            with open(log_path + '/' + abnormal_log, 'a', encoding='utf-8') as abnormal_file:
                print("页面[%s]不正常,flight_num[%s]详情信息需要补充" % (url, aircraft_flight_dict['flight_num']), file=abnormal_file)
    else:
        return


if __name__ == '__main__':
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    aircraft_url = 'https://www.flightradar24.com/data/aircraft'
    aircraft_url_list = get_aircraft_type_url_list(aircraft_url)
    aircraft_flight_list_all = []
    for aircraft_url in aircraft_url_list:
        aircraft_flight_list = get_aircraft_flight_list(aircraft_url)
        aircraft_flight_list_all.extend(aircraft_flight_list)
    # flag = False
    for aircraft_flight_dict in aircraft_flight_list_all:
        # if aircraft_flight_dict['href'] == 'https://www.flightradar24.com/data/aircraft/vt-sum':
        #     flag = True
        #     print('断点继续：https://www.flightradar24.com/data/aircraft/vt-sum==[%s]' % aircraft_flight_dict)
        # if flag:
        if aircraft_flight_dict['flight_num'] in ['1321','1320','142806','142805'
,'142804','142803','84-0048','84-0047']:
            print('正在爬取[%s]' % aircraft_flight_dict['flight_num'])
            get_aircraft_flight_info(aircraft_flight_dict)
            # 将航班信息存入数据库
            save_aircraft_flight_info(aircraft_flight_dict)