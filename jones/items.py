# -*- coding: utf-8 -*-

import scrapy


class Artist(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class ArtworkItem(scrapy.Item):
    museum_code = scrapy.Field() # e.g., "artic"
    accession_no = scrapy.Field()
    artist = scrapy.Field() # `Artist` instance
    title = scrapy.Field()
    url = scrapy.Field()
    thumbnail = scrapy.Field()
    on_display = scrapy.Field()
    year = scrapy.Field()
    medium = scrapy.Field()
