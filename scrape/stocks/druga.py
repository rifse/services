#!/home/admin/envs_py/bsoup/bin/python3.8

import json
import requests
import time
from bs4 import BeautifulSoup

link = "https://finviz.com/screener.ashx?v=150&f=cap_smallover,idx_sp500&ft=4&c=0,1,2,6,7,10,11,13,14,45,65"
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"}
page = requests.get(link, headers=headers)
# print(page.status_code)
# print(page.content)

soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())

