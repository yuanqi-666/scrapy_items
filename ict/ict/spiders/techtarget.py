import hashlib
from typing import Iterable

import jieba
import scrapy
from bs4 import BeautifulSoup
from newspaper import fulltext
from scrapy import Request

from ict.items import IctItem


class TechtargetSpider(scrapy.Spider):
    name = "techtarget"
    allowed_domains = ["searchnetworking.techtarget.com.cn"]

    def start_requests(self) -> Iterable[Request]:
        for i in range(1, 30):
            url = f"https://searchnetworking.techtarget.com.cn/news/page/{i}/"
            yield Request(url=url)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        li_tags = soup.find('ul', attrs={"class": "newslist"}).find_all('li')
        for li in li_tags:
            ict_item = IctItem()
            ict_item["title"] = li.find('a').get('title')
            ict_item["pub_time"] = li.find('span').text.replace(' ','')
            url = li.find('a').get('href')
            ict_item["url"] = url
            ict_item["source"] = "techtarget"
            ict_item["id"] = hashlib.md5(url.encode()).hexdigest()
            ict_item["language"] = 'zh'
            ict_item["reserved"] = {
                "keywords": [],
                "product_line": "网络",
                "source_catalogue": "新闻"
            }
            yield Request(url, callback=self.request_page, cb_kwargs={"item": ict_item})

    def request_page(self, response, **kwargs):
        i_item = kwargs['item']
        content = fulltext(response.text, 'zh')
        to_num = len(list(jieba.cut(content)))
        i_item["content"] = content
        i_item["token_num"] = to_num
        yield i_item
