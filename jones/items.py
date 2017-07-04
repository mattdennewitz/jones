# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


def to_boolean(value):
    if not value:
        return False

    return bool(int(value))


class ArtworkLoader(ItemLoader):
    pass


class ArtworkItem(scrapy.Item):
    museum_code = scrapy.Field(output_processor=TakeFirst())
    dept_name = scrapy.Field(output_processor=TakeFirst()) # where is the item on display?
    artist_name = scrapy.Field() # some museums list multiple artists
    artist_url = scrapy.Field() # ...and so there may be multiple artist urls
    title = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    year = scrapy.Field(output_processor=TakeFirst())
    medium = scrapy.Field(output_processor=TakeFirst())
    thumbnail = scrapy.Field(output_processor=TakeFirst())
    on_display = scrapy.Field(input_processor=MapCompose(to_boolean),
                              output_processor=TakeFirst())
    accession_no = scrapy.Field(output_processor=TakeFirst())
