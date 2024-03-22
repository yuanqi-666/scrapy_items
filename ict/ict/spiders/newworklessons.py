import hashlib

import jieba
import scrapy
from scrapy import Request
import json
from ict.items import IctItem
from newspaper import fulltext


class NewworklessonsSpider(scrapy.Spider):
    name = "newworklessons"
    allowed_domains = ["notes.networklessons.com"]
    start_urls = ["https://notes.networklessons.com/api/notes"]

    def parse(self, response, **kwargs):
        res_json = json.loads(response.text)['notes']
        for r_json in res_json:
            ict_item = IctItem()
            url = f"https://notes.networklessons.com/{r_json['slug']}"
            ict_item["id"] = hashlib.md5(url.encode()).hexdigest()
            ict_item["url"] = url
            ict_item["source"] = 'newworklessons'
            ict_item["title"] = r_json['name']
            ict_item["language"] = 'en'
            ict_item["pub_time"] = ''
            ict_item["reserved"] = {
                "keywords": r_json["tags"],
                "product_line": "思科课程百科",
                "source_catalogue": "思科课程百科"
            }
            yield Request(url, callback=self.request_page, cb_kwargs={"item": ict_item})

    def request_page(self, response, **kwargs):
        i_item = kwargs["item"]
        content = fulltext(response.text, 'en')
        to_num = len(list(jieba.cut(content)))
        i_item['content'] = content
        i_item["token_num"] = to_num
        yield i_item
