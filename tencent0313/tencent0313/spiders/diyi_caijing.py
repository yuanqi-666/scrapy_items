import json
from typing import Iterable

import scrapy
from scrapy import Request
from ..items import Tencent0313Item
from newspaper import fulltext


class DiyiCaijingSpider(scrapy.Spider):
    name = "diyi-caijing"
    allowed_domains = ["www.yicai.com"]

    # start_urls = ["https://www.yicai.com/news/"]
    def start_requests(self) -> Iterable[Request]:
        for i in range(1, 20):
            yield Request(url=f'https://www.yicai.com/api/ajax/getjuhelist?action=news&page={i}&pagesize=25')

    def parse(self, response, **kwargs):
        response_json = json.loads(response.text)
        for js in response_json:
            diyi_item = Tencent0313Item()
            page_url = "https://www.yicai.com" + js['url']
            diyi_item['response'] = js
            yield Request(page_url, callback=self.filter_page_content, cb_kwargs={"item": diyi_item})

    def filter_page_content(self, response, **kwargs):
        d_item = kwargs["item"]
        content = fulltext(response.text, 'zh')
        d_item['content'] = content
        d_item['html'] = response.text
        yield d_item
