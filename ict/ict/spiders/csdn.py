import hashlib
import json
from typing import Iterable

import jieba
import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from newspaper import fulltext
from ict.items import IctItem


class CsdnSpider(scrapy.Spider):
    name = "csdn"
    allowed_domains = ["so.csdn.net"]

    # start_urls = ["https://so.csdn.net"]
    def start_requests(self) -> Iterable[Request]:
        url = f"https://blog.csdn.net/m0_55407175/article/details/120566762"
        yield Request(url)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text)
        ict_item = IctItem()
        content = fulltext(response.text, 'zh')
        to_num = len(list(jieba.cut(content)))
        ict_item["id"] = hashlib.md5(response.url.encode()).hexdigest()
        ict_item["url"] = response.url
        ict_item["content"] = content
        ict_item["token_num"] = to_num
        ict_item["source"] = "CSDN"
        ict_item["title"] = content.title()
