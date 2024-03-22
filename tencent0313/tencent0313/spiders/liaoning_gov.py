from typing import Iterable

import scrapy
from bs4 import BeautifulSoup
from newspaper import fulltext
from scrapy import Request

from ..items import Tencent0313Item


class LiaoningGovSpider(scrapy.Spider):
    name = "liaoning-gov"
    allowed_domains = ["www.ln.gov.cn"]

    # start_urls = ["https://www.ln.gov.cn"]
    def start_requests(self) -> Iterable[Request]:
        for i in range(1, 25):
            yield Request(url=f'https://www.ln.gov.cn/web/ywdt/zymtkln/5b93cb3c-{i}.shtml')

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        li_tags = soup.find('div', attrs={"class": "modcontent"}).find_all('li')
        for li in li_tags:
            page_url = "https://www.ln.gov.cn/" + li.find('a').get('href')
            yield Request(page_url, callback=self.download_page)

    def download_page(self, response, **kwargs):
        t_item = Tencent0313Item()
        t_item['content'] = fulltext(response.text, 'zh')
        t_item['html'] = response.text
        t_item['response'] = {}
        yield t_item
