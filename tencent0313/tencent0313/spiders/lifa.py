from typing import Iterable

import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from ..items import Tencent0313Item
from newspaper import fulltext


class LifaSpider(scrapy.Spider):
    name = "lifa"
    allowed_domains = ["www.legaldaily.com.cn"]

    # start_urls = ["https://www.legaldaily.com.cn"]
    def start_requests(self) -> Iterable[Request]:
        for i in range(2, 10):
            yield Request(url=f"http://www.legaldaily.com.cn/rdlf/node_34017_{i}.html")

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for tag in soup.find('div', attrs={"class": "content-one"}).find_all('li'):
            url = tag.find('a').get('href')
            yield Request(url, callback=self.download_page)

    def download_page(self, response):
        t_item = Tencent0313Item()
        t_item['content'] = fulltext(response.text, 'zh')
        t_item['html'] = response.text
        t_item['response'] = ''
        yield t_item
