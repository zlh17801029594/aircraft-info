#!/usr/bin/env python 
# _*_ coding:utf-8 _*_
import re, sys, urllib.parse, requests, os


def get_onepage_urls(onepageurl):
    '''
    获取当前页面所有图片的url 和 下一页的url
    '''
    if not onepageurl:
        print('已经是最后一页！')
        return [], ''
    try:
        html = requests.get(onepageurl).text
    except Exception as e:
        print(e)
        pic_urls = []
        next_url = ''
        return pic_urls, next_url
    pic_urls = re.findall('"objURL":"(.*?)",', html, re.S)

    next_urls = re.findall(re.compile(r'下一页'), html, flags=0)
    print(next_urls)
    next_url = 'http://image.baidu.com ' + next_urls[0] if next_urls else ''
    return pic_urls, next_url


def down_pic(pic_urls):
    '''
    通过图片链接列表，下载所有的图片
    '''
    path = "images"
    if (os.path.exists(path) == False):
        os.makedirs(path)
    for i, pic_url in enumerate(pic_urls):
        try:
            pic = requests.get(pic_url, timeout=15)
            string = path + "/" + str(i + 1) + '.jpg'
            with open(string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第  %s 张图片 ：%s' % (str(i + 1), str(pic_url)))
        except Exception as e:
            print('下载第  %s 张图片时失败：%s' % (str(i + 1), str(pic_url)))
            print(e)
            continue


if __name__ == '__main__':
    keyword = '罗宾'  # 你想输入的关键词
    url_init_first = r'http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1497491098685_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word= '
    url_init = url_init_first + urllib.parse.quote(keyword, safe='/')
    all_pic_urls = []
    onepage_urls, next_url = get_onepage_urls(url_init)
    all_pic_urls.extend(onepage_urls)

    next_count = 0  # 初始化翻页数
    while 1:
        onepage_urls, next_url = get_onepage_urls(next_url)
        next_count += 1
        print('第  %s页' % next_count)
        if next_url == '' and onepage_urls == []:
            break
        all_pic_urls.extend(onepage_urls)
    down_pic(list(set(all_pic_urls)))