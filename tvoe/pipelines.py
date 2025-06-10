# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook

class ExcelExportPipeline:
    def __init__(self):
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = "Tvoe Products"

        headers = ["URL", "Breadcrumbs", "Name", "Description", "Current Price", "Old Price", "Attributes", "Images"]
        self.sheet.append(headers)

    def process_item(self, item, spider):
        attributes_str = '; '.join([f"{attr['name']}: {attr['value']}" for attr in item.get('attributes', [])])
        images_str = '; '.join(item.get('images', []))

        row = [
            item.get("url"),
            item.get("breadcrumbs"),
            item.get("name"),
            item.get("description"),
            item.get("current_price"),
            item.get("old_price"),
            attributes_str,
            images_str
        ]
        self.sheet.append(row)

        return item

    def close_spider(self, spider):
        self.workbook.save("tvoe_products.xlsx")
