#!/home/admin/envs_py/bsoup/bin/python3.8

import json
import requests
import time
from bs4 import BeautifulSoup

link_base = 'https://www.fmf.uni-lj.si'
link_aggr = '/sl/obvestila/agregator/161/zaposlitveni-oglasi/?page='
page_num = 1
# page = requests.get(link_base + link_aggr + str(page_num))
# print(page.content)
vacancies = {}

while True:
    page = requests.get(link_base + link_aggr + str(page_num))
    if page.status_code != 200 or page_num > 8:
        break
    else:
        page_num += 1

    soup = BeautifulSoup(page.content, 'html.parser')
    content_raw = soup.find_all('div', class_="news-aggregator-listing")[0]
    content = content_raw.find_all('a')
    
    try:
        for x in content:
            link_ = x['href']
            name = link_.split('/')[4]
            vacancies[name] = {
                    'link': link_base + link_,
                    'description': x.find('div', class_='news__item-blurb').string
                    }
    except AttributeError:
        print(f'page_num = {page_num}, got an AttributeError!')

print(vacancies)
with open('dataTrial_03', 'w') as output:
    json.dump(vacancies, output)
        # time.sleep(0.5)
# with open('dataTrial_02', 'w') as output:
#     # output.write(soup.prettify())
#     # print(soup.ul)
# 
#     content = soup.find_all('div', class_="news-aggregator-listing")
#     # content1 = soup.ul.find_all('div', class_="news-aggregator-listing")
#     # print(content1)
#     # content2 = soup.ul.find_all('div', class_="news\-aggregator\-listing")
#     # print(content2)
#     output.write(content.prettify())

# print(f'content type = {type(content)}')

# print(content)
