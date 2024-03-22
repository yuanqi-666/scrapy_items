import scrapy


class IctItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    language = scrapy.Field()
    pub_time = scrapy.Field()
    content = scrapy.Field()
    token_num = scrapy.Field()
    reserved = scrapy.Field()
    # reserved = {
    # "keywords":["xx","yy","zz"], # 关键词
    # "product_line":str,          # 产品线分类——数据通信/无线/光/云核心网/数据存储/计算
    # "source_catalogue":str # 来源分类——新闻/博客/社媒/百科/知识库/产品文档/论坛社区/协议标准/专利/论文/书籍
    # }
