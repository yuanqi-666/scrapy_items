# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ApicrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tool_name = scrapy.Field()
    tool_description = scrapy.Field()
    url = scrapy.Field()
    api_list = scrapy.Field()