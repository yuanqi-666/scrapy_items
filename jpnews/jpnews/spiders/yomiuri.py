import scrapy
import newspaper
from ..items import JpnewsItem
from bs4 import BeautifulSoup


class YomiuriSpider(scrapy.Spider):
    name = "yomiuri"
    allowed_domains = ["www.yomiuri.co.jp"]
    start_urls = ["https://www.yomiuri.co.jp/news/"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        art_tags = soup.find_all('article', attrs={"class": "news-top-latest__list-item"})
        for art in art_tags:
            url = art.find('h3').find('a').get('href')
            yield scrapy.Request(url, callback=self.download_page)

    def download_page(self, response):
        j = JpnewsItem()
        j['content'] = newspaper.fulltext(response.text, 'ja')
        j['url'] = response.url
        yield j
