# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZubshopItem(scrapy.Item):
    url = scrapy.Field()
    breadcrumbs = scrapy.Field()
    name = scrapy.Field()
    product_code = scrapy.Field()
    maker = scrapy.Field()
    description = scrapy.Field()
    current_price = scrapy.Field()
    old_price = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    img = scrapy.Field()
