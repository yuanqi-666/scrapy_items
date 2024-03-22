import math
from typing import Iterable

import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from ..items import JpnewsItem


class NovelupSpider(scrapy.Spider):
    name = "novelup"
    allowed_domains = ["novelup.plus"]

    # start_urls = ["https://novelup.plus/ranking/high-fantasy/millennium"]
    def start_requests(self) -> Iterable[Request]:
        for i in range(2,7):
            url = f"https://novelup.plus/ranking/high-fantasy/millennium?p={i}"
            yield Request(url=url)
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        p_tags = soup.find_all('p', attrs={"class": "story_name"})
        for p in p_tags:
            url = p.find('a').get("href")
            yield scrapy.Request(url=url, callback=self.from_to_info_page)

    def from_to_info_page(self, response):
        info_soup = BeautifulSoup(response.text, 'lxml')
        to_num = info_soup.find('p', attrs={"class": "total_episode_num"}).text.split('：')[-1][:-1].replace(',', '')
        to_page = math.ceil(int(to_num) / 100)
        for i in range(1, to_page + 1):
            yield scrapy.Request(response.url + f'?p={i}', callback=self.download_page)

    def download_page(self, response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        div_tags = page_soup.find_all("div", attrs={"class": "episode_link episode_show_visited"})
        for div in div_tags:
            url = div.find('a').get('href')
            yield scrapy.Request(url, callback=self.d_content)

    def d_content(self, response):
        d_soup = BeautifulSoup(response.text, 'lxml')
        j = JpnewsItem()
        j['content'] = d_soup.find('div', attrs={"id": "js-scroll-area"}).text
        yield j
