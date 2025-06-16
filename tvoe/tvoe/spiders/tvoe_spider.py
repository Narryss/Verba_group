import scrapy
from scrapy.spiders import CrawlSpider
from tvoe.items import TvoeItem

class TvoeSpiderSpider(CrawlSpider):
    name = "tvoe_spider"
    allowed_domains = ["tvoe.ru"]
    start_urls = ["https://tvoe.ru/"]

    def parse_start_url(self, response):
        self.logger.info("Парсинг стартовой страницы: %s", response.url)
        
        men_link = response.xpath('.//a[contains(text(), "Мужчинам")]/@href').get()
        if men_link:
            yield response.follow(men_link, callback=self.parse_category)

        women_link = response.xpath('.//a[contains(text(), "Женщинам")]/@href').get()
        if women_link:
            yield response.follow(women_link, callback=self.parse_category)

    def parse_category(self, response):
        self.logger.info("Парсинг категории: %s", response.url)
        
        product_links = response.xpath('//component[contains(@class, "product__title")]/@link').getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_item)

        page_numbers = response.xpath('//a[@class="pagination__list-item"]/text()').getall()
        try:
            last_page = int(page_numbers[-1]) if page_numbers else 1
        except ValueError:
            last_page = 1

        base_url = response.url.split('?')[0]
        for page in range(2, last_page + 1):
            page_url = f"{base_url}?page={page}"
            yield response.follow(page_url, callback=self.parse_page)

     def parse_page(self, response):
        self.logger.info("Парсинг страницы пагинации: %s", response.url)
         
        product_links = response.xpath('//component[contains(@class, "product__title")]/@link').getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_item)   

    def parse_item(self, response):
        item = TvoeItem()

        item['url'] = response.url

        breadcrumbs = []
        for breadcrumb in response.xpath('//div[contains(@class, "breadcrumbs__item")]'):
            breadcrumb_text = breadcrumb.xpath('.//span[@class="breadcrumbs__item-text"]/text()').get()
            if breadcrumb_text:
                breadcrumbs.append(breadcrumb_text.strip())
        unique_breadcrumbs = list(dict.fromkeys(breadcrumbs))
        item['breadcrumbs'] = unique_breadcrumbs

        item['name'] = response.xpath('.//div[@class="product-detail"]'
                                      '//h1[@class="product-detail__title"]/text()').get()

        item['description'] = response.xpath('.//div[@class="product-detail"]'
                                             '//div[@class="product-detail__description text-b11"]/text()').get()

        discount_price = response.xpath('.//span[@class="product-detail__price product-detail__price--discount"]'
                                          '/text()').get()
        if discount_price:
            item["current_price"] = discount_price.replace('\xa0', '').strip()
        else:
            regular_price = response.xpath('.//span[@class="product-detail__price"]/text()').get()
            item["current_price"] = regular_price.replace('\xa0', '').strip() if regular_price else None

        old_price = response.xpath('.//span[@class="product-detail__price product-detail__price--old"]'
                                     '/text()').get()
        item["old_price"] = old_price.replace('\xa0', '').strip() if old_price else None

        attributes = []
        attributes_block = response.xpath('//div[@class="product-detail__attribute"]')
        for attribute in attributes_block:
            attribute_name = attribute.xpath('./span[contains(@class, "product-detail__attribute-t")]/text()').get()
            attribute_value = attribute.xpath('./span[contains(@class, "product-detail__attribute-d")]/text()').get()
            if attribute_name and attribute_value:
                attributes.append({
                    'name': attribute_name.strip().rstrip(':'),
                    'value': attribute_value.strip()
                })
        item['attributes'] = attributes

        images = response.xpath('.//img[contains(@class,"product-detail__image")]/@src').getall()
        item['images'] = images

        yield item
