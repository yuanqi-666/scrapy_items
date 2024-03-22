import json
from typing import Iterable

import jieba
import scrapy
from newspaper import fulltext
from scrapy import Request

from ..items import IctItem


class IctPageSpider(scrapy.Spider):
    name = "ict_page"
    allowed_domains = ["www.cww.net.cn"]

    # start_urls = ["https://www.cww.net.cn/index.jsp"]

    def start_requests(self) -> Iterable[Request]:
        for page_index in range(1, 50):
            url = f'http://www.cww.net.cn/web/news/articleinfo/selctArticleListBycolumnId.json?columnId=2603&page={page_index}&size=30'
            yield Request(url)

    def parse(self, response, **kwargs):
        json_d = json.loads(response.text)["data"]["rows"]
        for j in json_d:
            ict_item = IctItem()
            url = f"http://www.cww.net.cn/article?id={j['idno']}"
            ict_item["title"] = j["articleTitle"]
            ict_item["id"] = j["idno"]
            ict_item["source"] = "通信世界网"
            ict_item["url"] = url
            ict_item["language"] = 'zh'
            # ict_item["pub_time"] = json_d['createTime']
            ict_item["reserved"] = {
                "keywords": json_d[0]["keyWordd"].split(','),
                "product_line": "数据通信",
                "source_catalogue": "新闻"
            }
            yield Request(url=url, callback=self.parse_content, cb_kwargs={"ict_item": ict_item})

    def parse_content(self, response, **kwargs):
        ict_item = kwargs['ict_item']
        content = fulltext(response.text, 'zh')
        ict_item["content"] = content
        ict_item["token_num"] = len(list(jieba.cut(content)))
        yield ict_item
