# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PubmedItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    author = scrapy.Field()
    intro = scrapy.Field()
    xueke = scrapy.Field()
    create_time = scrapy.Field()
    doi = scrapy.Field()
    pdf_name = scrapy.Field()
