# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TvoeItem(scrapy.Item):
    url = scrapy.Field()
    breadcrumbs = scrapy.Field()
    name = scrapy.Field()
    product_code = scrapy.Field()
    description = scrapy.Field()
    current_price = scrapy.Field()
    old_price = scrapy.Field()
    attributes = scrapy.Field()
    images = scrapy.Field()
