# -*- coding: utf-8 -*-

import scrapy


class ArtworkItem(scrapy.Item):
    museum_code = scrapy.Field()
    artist_name = scrapy.Field()
    artist_url = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    thumbnail = scrapy.Field()
    on_display = scrapy.Field()
    year = scrapy.Field()
    medium = scrapy.Field()
