import hashlib
from typing import Iterable

import jieba
import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from ict.items import IctItem
from newspaper import fulltext


class JuniperSpider(scrapy.Spider):
    name = "juniper"
    allowed_domains = ["community.juniper.net"]
    start_urls = ["https://community.juniper.net"]

    def start_requests(self) -> Iterable[Request]:
        for i in range(1, 50):
            url = f"https://community.juniper.net/higherlogic/internal/facetedsearch/searchpartial?s=IPsec&cs=null&expanded-categories=undefined&p={i}&st=Relevance&micrositegroupkey=70929212-4d30-4fbb-b1c3-d2b727b1f304&executesearch=True&communityscope=Self&_=1709713306247"
            yield Request(url)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        div_tags = soup.find_all('div', attrs={"class": "row fs-result-row"})
        for div in div_tags:
            ict_item = IctItem()
            url = div.find('h3').find('a').get('href')
            ict_item['id'] = hashlib.md5(url.encode()).hexdigest()
            ict_item['url'] = url
            ict_item['title'] = div.find('h3').find('a').get('title')
            ict_item['source'] = 'juniper'
            ict_item['language'] = 'en'
            ict_item['pub_time'] = div.find('div', attrs={"class": "meta-content-date"}).text
            ict_item["reserved"] = {
                "keywords": ['ipsec'],
                "product_line": "",
                "source_catalogue": "论坛社区"
            }
            yield Request(url, callback=self.requests_page, cb_kwargs={"item": ict_item})

    def requests_page(self, response, **kwargs):
        i_item = kwargs['item']
        content = fulltext(response.text, 'en')
        to_num = len(list(jieba.cut(content)))
        i_item['content'] = content
        i_item['token_num'] = to_num
        yield i_item
