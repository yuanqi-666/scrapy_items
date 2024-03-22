import scrapy

from bs4 import BeautifulSoup
from ..items import JubenItem


class JubenTextSpider(scrapy.Spider):
    name = "juben-text"
    allowed_domains = ["m.juben.pro"]
    start_urls = ["https://m.juben.pro/Free/"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        li_tags = soup.find('ul', attrs={"class": "artlist"}).find_all('li')
        for li in li_tags:
            j_item = JubenItem()
            j_item['title'] = li.find('a').text
            url = li.find('a').get('href')
            j_item['url'] = url
            j_item['author'] = li.find_all('font')[-1].text
            yield scrapy.Request(url="https://m.juben.pro" + url, callback=self.download_page,
                                 cb_kwargs={'item': j_item})

    def download_page(self, response, **kwargs):
        j = kwargs['item']
        s = BeautifulSoup(response.text, 'lxml')
        j['info'] = s.find('div', attrs={"id": "tab1_div_0"}).text
        j['content'] = s.find('div', attrs={"id": "tab1_div_1"}).text
        yield j
