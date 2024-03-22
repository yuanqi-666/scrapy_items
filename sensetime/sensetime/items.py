# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SensetimeItem(scrapy.Item):
    content_html = scrapy.Field()
    data_source = scrapy.Field()
    data_url = scrapy.Field()
    crawler_tm = scrapy.Field()
    track_id = scrapy.Field()
    img_list = scrapy.Field()
    author = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    publish_time = scrapy.Field()
    source = scrapy.Field()


class ZhiWuBaiKE(scrapy.Item):
    content_html = scrapy.Field()
    data_source = scrapy.Field()
    data_url = scrapy.Field()
    crawler_tm = scrapy.Field()
    track_id = scrapy.Field()
    img_list = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
