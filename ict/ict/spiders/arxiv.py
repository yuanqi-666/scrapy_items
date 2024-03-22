import hashlib
from typing import Iterable
import requests
import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from ict.items import IctItem


class ArxivSpider(scrapy.Spider):
    name = "arxiv"
    allowed_domains = ["arxiv.org"]

    # start_urls = ["https://arxiv.org"]
    def start_requests(self) -> Iterable[Request]:
        # for i in range(1, 2):
        #     url = f"https://arxiv.org/list/astro-ph/24?skip={i * 50}&show=50"
        yield Request(url='https://arxiv.org/list/eess.SP/pastweek?show=125')

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        span_tags = soup.find_all('span', attrs={"class": "list-identifier"})
        for span in span_tags:
            url = 'https://arxiv.org' + span.find('a', attrs={"title": "Download PDF"}).get('href')
            print(url)
            response = requests.get(url)
            filename = hashlib.md5(url.encode()).hexdigest()
            if response.status_code == 200:
                with open(f'../pdf/{filename}.pdf', 'wb') as file:
                    file.write(response.content)
                print("PDF 下载成功！")
            else:
                print("下载失败，状态码：", response.status_code)
