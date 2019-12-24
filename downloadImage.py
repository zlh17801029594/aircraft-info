#!/usr/bin/env python 
# _*_ coding:utf-8 _*_
import re, urllib.parse, requests, os, time, random


def get_pic_urls(one_page_url):
    """获取单个翻页的所有图片的urls+当前翻页的下一翻页的url"""
    if not one_page_url:
        print('请求url为空, 结束')
        return [], ''
    try:
        html = requests.get(one_page_url).text
    except Exception as e:
        print(e)
        return [], ''
    pic_urls = re.findall('"objURL":"(.*?)",', html, re.S)
    next_urls = re.findall(re.compile(r'<a href="(.*)" class="n">下一页</a>'), html, flags=0)
    next_url = 'http://image.baidu.com' + next_urls[0] if next_urls else ''
    return pic_urls, next_url


def down_pic(pic_urls):
    """给出图片链接列表, 下载所有图片"""
    path = "images"
    if not os.path.exists(path):
        os.makedirs(path)
    for i, pic_url in enumerate(pic_urls):
        random_time = random.randint(0,3)
        print('随机延时[%s]s' % str(random_time))
        time.sleep(random_time)
        try:
            pic = requests.get(pic_url, timeout=15)
            string = path + '/' + str(i + 1) + '.jpg'
            with open(string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第%d张图片: %s' % (i + 1, str(pic_url)))
        except Exception as e:
            print(e)
            print('下载第%d张图片时失败: %s' % (i + 1, str(pic_url)))
            continue


if __name__ == '__main__':
    keyword = '罗宾'  # 关键词, 改为你想输入的词即可, 相当于在百度图片里搜索一样
    url_init_first = r'http://image.baidu.com/search/flip?tn=baiduimage&ipn=r' \
                     r'&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1497491098685_R&pv=&ic=0&nc=1&z=&se=1' \
                     r'&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&ctd=1497491098685%5E00_1519X735&word='
    url_init = url_init_first + urllib.parse.quote(keyword, safe='/')
    all_pic_urls = []
    next_url = url_init
    page_count = 1  # 累计翻页数
    while 1:
        print(next_url)
        print('第%s页' % page_count)
        pic_urls, next_url = get_pic_urls(next_url)
        all_pic_urls.extend(pic_urls)
        if next_url == '':
            break
        page_count += 1
    pic_urls = list(set(all_pic_urls))
    print('找到相关图片%d张' % len(pic_urls))
    down_pic(pic_urls)