# _*_ encoding: utf-8 _*_
"""
 @File Name: sougou
 @Author:    Chenny
 @email:     15927299723@163.com
 @date:      2018/12/10
 @software:  PyCharm
"""

import requests
from lxml import etree
import time
import random
import os


def get_html(url, headers):
    """
    get html code
    """
    time.sleep(random.randint(0, 3))
    response = requests.get(url, headers=headers)
    html = response.content.decode('utf8', 'ignore')
    return html


def get_cate_urls(url, headers):
    """
    get category url
    """
    page_html = get_html(url, headers)
    html = etree.HTML(page_html)
    cate_urls = html.xpath('//div[@id="dict_nav_list"]//li/a/@href')
    cate_urls = ['https://pinyin.sogou.com' + u + '/' for u in cate_urls]
    return cate_urls


def get_page_urls(url, headers):
    """
    get each page url for current category
    """
    page_html = get_html(url, headers)
    html = etree.HTML(page_html)
    num_page = html.xpath('//div[@id="dict_page_list"]//li//a/text()')[-2]
    page_urls = [url + 'default/' + str(i) for i in range(1, int(num_page) + 1)]
    return page_urls


def get_item_urls(url, headers):
    """
    get item url for current category
    """
    page_urls = get_page_urls(url, headers)
    item_urls, item_names = [], []
    for url in page_urls:
        page_html = get_html(url, headers)
        html = etree.HTML(page_html)
        urls = html.xpath('//div[@id="dict_detail_list"]//div[@class="dict_dl_btn"]/a/@href')
        names = html.xpath('//div[@id="dict_detail_list"]//div[@class="detail_title"]/a/text()')
        item_urls += urls
        item_names += names
    return item_urls, item_names


def download_item(url, headers, save_path):
    """
    download vocabulary
    """
    response = requests.get(url, headers=headers)
    with open(save_path, "wb") as f:
        f.write(response.content)


def main(base_url, headers, main_dir):
    cate_urls = get_cate_urls(base_url, headers)
    w = 0
    for i, cate_url in enumerate(cate_urls):
        try:
            cate_dir = main_dir + str(i) + '/'
            if not os.path.exists(cate_dir): os.makedirs(cate_dir)
            # page_urls = get_page_urls(cate_url, headers)
            # for page_url in page_urls:
            item_urls, item_names = get_item_urls(cate_url, headers)
            for j, item in enumerate(zip(item_urls, item_names)):
                try:
                    save_path = cate_dir + item[1]
                    download_item(item[0], headers, save_path)
                    print(item[1], 'was saved!')
                except:
                    w += 1
                    print('wrong ' + 'str(w):' + str(i) + '-' + str(j))
                    continue
            print(str(i), 'was finnished!')
        except:
            continue


if __name__ == '__main__':
    base_url = 'https://pinyin.sogou.com/dict/cate/index/'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    }
    main_dir = 'data/'
    main(base_url, headers, main_dir)
