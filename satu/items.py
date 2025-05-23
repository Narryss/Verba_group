# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SatuItem(scrapy.Item):
    url = scrapy.Field()
    product_name = scrapy.Field()
    img = scrapy.Field()
    availability = scrapy.Field()
    current_price = scrapy.Field()
    old_price = scrapy.Field()
    product_count = scrapy.Field()
    product_rating = scrapy.Field()
    reviews_count = scrapy.Field()
    reviews = scrapy.Field()
    sellers = scrapy.Field()
    description = scrapy.Field()
    attributes = scrapy.Field()
