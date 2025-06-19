import scrapy
import re
from zubshop.items import ZubshopItem

class ZubshopSpiderSpider(scrapy.Spider):
    name = "zubshop_spider"
    allowed_domains = ["zubshop.ru"]
    start_urls = ["https://zubshop.ru/index.php?route=extension/module/brainyfilter/filter"]

    def parse(self, response):
        page_number = '1'
        self.logger.info("Парсинг страницы №%s", page_number)

        product_links = response.xpath('//div[@class="caption"]/h4/a/@href').getall()
        self.logger.info("Найдено %d товаров на странице %s", len(product_links), page_number)

        for link in product_links:
            yield response.follow(link, callback=self.parse_item)

        pagination_links = response.xpath('//ul[@class="pagination"]//a/@href').getall()
        for page_url in pagination_links:
            yield response.follow(page_url, callback=self.parse_page)

    def parse_page(self, response):
        page_number = response.url.split('&page=')[-1] if '&page=' in response.url else '1'
        self.logger.info("Парсинг страницы №%s", page_number)

        product_links = response.xpath('//div[@class="caption"]/h4/a/@href').getall()
        self.logger.info("Найдено %d товаров на странице %s", len(product_links), page_number)

        for link in product_links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response):
        self.logger.info("Парсинг товара: %s", response.url)
        
        item = ZubshopItem()
        item['url'] = response.url

        breadcrumbs = []
        for breadcrumb in response.xpath('//ul[@class="breadcrumb"]/li'):
            text = breadcrumb.xpath('.//span[@itemprop="title"]/text()').get()
            if text:
                breadcrumbs.append(text.strip())
        item['breadcrumbs'] = breadcrumbs[:-1]

        item['name'] = response.xpath('//h1[@itemprop="name"]/text()').get()
        item['product_code'] = response.xpath('//span[@itemprop="mpn"]/text()').get()
        item['maker'] = response.xpath('//span[@itemprop="brand"]/text()').get()

        description_text = response.xpath('//div[@id="tab-description"]//text()').getall()
        item['description'] = '\n'.join([text.strip() for text in description_text])

        discount_price = response.xpath('//span[@class="real"]/text()').get()
        old_price = response.xpath('//span[@class="price-old"]/text()').get()

        if discount_price:
            discount_match = re.search(r'\d+', discount_price.replace(' ', '').replace('р.', ''))
            if discount_match:
                item['current_price'] = discount_match.group(0)

        if old_price:
            old_match = re.search(r'\d+', old_price.replace(' ', '').replace('р.', ''))
            if old_match:
                item['old_price'] = old_match.group(0)

        rating = response.xpath('//meta[@itemprop="ratingValue"]/@content').get()
        rating_value = float(rating) if rating else None
        item['rating'] = rating_value if rating_value != 0 else None

        reviews_text = response.xpath('//span[@itemprop="reviewCount"]/text()').get()
        match = re.search(r'\d+', reviews_text)
        item['reviews_count'] = int(match.group(0))
        item['img'] = response.xpath('//img[@itemprop="image"]/@src').get()

        yield item
