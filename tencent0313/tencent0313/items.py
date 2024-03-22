# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Tencent0313Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    response = scrapy.Field()
    content = scrapy.Field()
    html = scrapy.Field()
