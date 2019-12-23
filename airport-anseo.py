#!/usr/bin/env python 
# _*_ coding:utf-8 _*_
import urllib.request
import re
import os
from bs4 import BeautifulSoup as bs

def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    page.close()
    return html

