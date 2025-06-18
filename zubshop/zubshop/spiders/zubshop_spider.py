import scrapy
from zubshop.items import ZubshopItem

class ZubshopSpiderSpider(scrapy.Spider):
    name = "zubshop_spider"
    allowed_domains = ["zubshop.ru"]
    start_urls = ["https://zubshop.ru/index.php?route=extension/module/brainyfilter/filter"]

    def parse(self, response):
        page_number = '1'
        self.logger.info(f"Парсинг страницы №{page_number}")

        product_links = response.xpath('//div[@class="caption"]/h4/a/@href').getall()
        self.logger.info(f"Найдено {len(product_links)} товаров на странице {page_number}")

        for link in product_links:
            yield response.follow(link, callback=self.parse_ite)

        pagination_links = response.xpath('//ul[@class="pagination"]//a/@href').getall()
        for page_url in pagination_links:
            yield response.follow(page_url, callback=self.parse_page)

    def parse_page(self, response):
        page_number = response.url.split('&page=')[-1] if '&page=' in response.url else '1'
        self.logger.info(f"Парсинг страницы №{page_number}")

        product_links = response.xpath('//div[@class="caption"]/h4/a/@href').getall()
        self.logger.info(f"Найдено {len(product_links)} товаров на странице {page_number}")

        for link in product_links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response):
        item = ZubshopItem()
        item['url'] = response.url

        breadcrumbs = []
        for breadcrumb in response.xpath('//ul[@class="breadcrumb"]/li'):
            text = breadcrumb.xpath('.//span[@itemprop="title"]/text()').get()
            if text:
                breadcrumbs.append(text.strip())
        item['breadcrumbs'] = breadcrumbs

        item['name'] = response.xpath('//h1[@itemprop="name"]/text()').get()
        item['product_code'] = response.xpath('//span[@itemprop="mpn"]/text()').get()
        item['maker'] = response.xpath('//span[@itemprop="brand"]/text()').get()

        description_text = response.xpath('string(//div[@id="tab-description"])').get()
        item['description'] = description_text.strip() if description_text else None

        discount_price = response.xpath('//span[@class="real"]/text()').get()
        old_price = response.xpath('//span[@class="price-old"]/text()').get()

        item['current_price'] = discount_price.replace('.00', '').replace('р.', '').replace(' ', '').strip() if discount_price else None
        item['old_price'] = old_price.replace('.00', '').replace('р.', '').replace(' ', '').strip() if old_price else None

        item['rating'] = response.xpath('//meta[@itemprop="ratingValue"]/@content').get()
        item['reviews_count'] = response.xpath('//span[@itemprop="reviewCount"]/text()').get()
        item['img'] = response.xpath('//img[@itemprop="image"]/@src').get()

        yield item
