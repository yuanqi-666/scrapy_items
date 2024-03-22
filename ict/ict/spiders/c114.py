import hashlib
from typing import Iterable

import jieba
import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from ict.items import IctItem
from newspaper import fulltext


class C114Spider(scrapy.Spider):
    name = "c114"
    allowed_domains = ["www.dvbcn.com"]
    start_urls = ["https://www.dvbcn.com"]

    def start_requests(self) -> Iterable[Request]:
        for i in range(1, 25):
            url = f"http://www.dvbcn.com/news/5g/page/{i}"
            yield Request(
                url
            )

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        div_tags = soup.find_all('div', attrs={"class": "mod-b mod-art"})
        for div in div_tags:
            ict_item = IctItem()
            url = div.find('h2').find('a').get('href')
            ict_item["url"] = url
            ict_item["title"] = div.find('h2').find('a').text
            ict_item["id"] = hashlib.md5(url.encode()).hexdigest()
            ict_item["source"] = 'C114通信百科'
            ict_item["language"] = 'zh'
            ict_item["pub_time"] = div.find('span', attrs={"class": "time"}).text
            ict_item["reserved"] = {
                "keywords": [],
                "product_line": "广电网",
                "source_catalogue": "5G宽带"
            }
            yield Request(url, callback=self.request_page, cb_kwargs={"item": ict_item})

    def request_page(self, response, **kwargs):
        i_item = kwargs['item']
        content = fulltext(response.text,'zh')
        to_num = len(list(jieba.cut(content)))
        i_item['content'] = content
        i_item['token_num'] = to_num
        yield i_item
