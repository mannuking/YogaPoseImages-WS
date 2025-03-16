import scrapy

class YogaPoseImage(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    pose_name = scrapy.Field()
    pose_name_hindi = scrapy.Field()
    image_id = scrapy.Field() 
