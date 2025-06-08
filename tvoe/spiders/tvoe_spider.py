import scrapy
from scrapy.spiders import CrawlSpider
from openpyxl import Workbook
from tvoe.items import TvoeItem

class TvoeSpiderSpider(CrawlSpider):
    name = "tvoe_spider"
    allowed_domains = ["tvoe.ru"]
    start_urls = ["https://tvoe.ru/"]

    def parse_start_url(self, response):
        men_link = response.xpath('.//a[contains(text(), "Мужчинам")]/@href').get()
        if men_link:
            yield response.follow(men_link, callback=self.parse_category)

        women_link = response.xpath('.//a[contains(text(), "Женщинам")]/@href').get()
        if women_link:
            yield response.follow(women_link, callback=self.parse_category)

    def parse_category(self, response):
        product_links = response.xpath('//div[@class="product-list"]'
                                       '//div[contains(@class, "product-list__product-wrapper")]'
                                       '//a[@class="product__image-link"]/@href').getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_item)

        pagination_links = response.xpath('//div[@class="pagination"]//a[@class="pagination__list-item"]/@href').getall()
        for link in pagination_links:
            yield response.follow(link, callback=self.parse_category)

    def parse_item(self, response):
        item = TvoeItem()

        price_item = response.xpath('.//div[@class="product-detail__prices"]')

        item['url'] = response.url

        breadcrumbs = []
        for breadcrumb in response.xpath('//div[@class="breadcrumbs breadcrumbs--product-detail"]'
                                         '//a[@class="breadcrumbs__item-link"]'):
            breadcrumb_text = breadcrumb.xpath('.//span[@class="breadcrumbs__item-text"]/text()').get()
            if breadcrumb_text:
                breadcrumbs.append(breadcrumb_text.strip())
        item['breadcrumbs'] = ' / '.join(breadcrumbs)

        item['name'] = response.xpath('.//div[@class="product-detail"]'
                                      '//h1[@class="product-detail__title"]/text()').get()

        item['description'] = response.xpath('.//div[@class="product-detail"]'
                                             '//div[@class="product-detail__description text-b11"]/text()').get()

        discount_price = price_item.xpath('.//span[@class="product-detail__price product-detail__price--discount"]'
                                          '/text()').get()
        if discount_price:
            item["current_price"] = discount_price.strip()
        else:
            regular_price = price_item.xpath('.//span[@class="product-detail__price"]/text()').get()
            item["current_price"] = regular_price.strip() if regular_price else None

        old_price = price_item.xpath('.//span[@class="product-detail__price product-detail__price--old"]'
                                     '/text()').get()
        item["old_price"] = old_price.strip() if old_price else None

        attributes = []
        for attribute in response.xpath('.//div[@class="product-detail__attribute"]'):
            attribute_name = attribute.xpath('.//span[@class="product-detail__attribute-t"]/text()').get()
            attribute_value = attribute.xpath('.//span[@class="product-detail__attribute-d"]/text()').get()
            if attribute_name and attribute_value:
                attributes.append({
                    'name': attribute_name.strip(),
                    'value': attribute_value.strip()
                })
        item['attributes'] = attributes

        images = []
        for img in response.xpath('.//div[@class="product-detail__gallery-inner"]//img'):
            img_url = img.xpath('@src').get()
            if img_url:
                images.append(img_url.strip())

        item['images'] = images

        yield item
