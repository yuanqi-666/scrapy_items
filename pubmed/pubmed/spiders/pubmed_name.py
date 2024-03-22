import hashlib

import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from pubmed.items import PubmedItem


class PubmedNameSpider(scrapy.Spider):
    name = "pubmed-name"
    allowed_domains = ["pubmed.ncbi.nlm.nih.gov"]

    # start_urls = ["https://pubmed.ncbi.nlm.nih.gov"]

    def start_requests(self):
        for i in range(1, 9583):
            url = f"https://pubmed.ncbi.nlm.nih.gov/?term=c&filter=simsearch2.ffrft&filter=lang.english&filter=years.2023-2023&timeline=expanded&page={i}"
            yield Request(url=url)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")
        article_tags = soup.find_all('article', attrs={"class": "full-docsum"})
        for article_tag in article_tags:
            pubmed_item = PubmedItem()
            url = 'https://pubmed.ncbi.nlm.nih.gov/' + article_tag.find('a', attrs={"class": "docsum-title"}).get(
                'href')
            pubmed_item['title'] = article_tag.find('a', attrs={"class": "docsum-title"}).text.replace(' ', '').replace(
                '\n', '')
            pubmed_item['id'] = hashlib.md5(url.encode()).hexdigest()
            pubmed_item['author'] = article_tag.find('span',
                                                     attrs={"class": "docsum-authors full-authors"}).text.replace(
                ' ', '').replace('\n', '')
            pubmed_item['intro'] = article_tag.find('div', attrs={"class": "full-view-snippet"}).text
            pubmed_item['xueke'] = '医学-丙型'
            yield Request(url=url, cb_kwargs={'item': pubmed_item}, callback=self.download_page)

    def download_page(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")
        pubmeb_i = kwargs.get('item')
        try:
            pubmeb_i['create_time'] = soup.find('span', attrs={"class": "cit"}).text
        except:
            pubmeb_i['create_time'] = ''
        try:
            pubmeb_i['doi'] = soup.find('span', attrs={"class": "identifier doi"}).text.replace('\n', '').replace(' ',
                                                                                                                  '')
        except:
            pubmeb_i['doi'] = ' '
        yield pubmeb_i
