# -*- coding: utf-8 -*-

"""
Columbus Museum of Art

All collections: https://www.columbusmuseum.org/embark-collection/pages/POR1/
"""

import re
import urlparse

import scrapy

from ..items import ArtworkItem, ArtworkLoader
from .base import BaseArtworkSpider


ARTWORK_DETAIL_SELECTOR = """
//div[@class="portfolioItemDetails"]/a[contains(@title, "Display Object")]/@href
"""

ON_DISPLAY_SELECTOR = """
boolean(
    //ul[contains(@class, "portfolioList")]/li/a/div[contains(., "On View")]
)
""".strip()

PAGE_SELECTORS = (
    'div.pageNav a.pageNav-next::attr(href)',
    'div.pageNav a.pageNav-last::attr(href)',
)

class ColumbusMOASpider(BaseArtworkSpider):
    name = 'colsmoa'
    allowed_domains = ['columbusmuseum.org']

    # hard-coding the collections
    start_urls = (
        'https://www.columbusmuseum.org/embark-collection/pages/Prt32175?sid=2518&x=4885541',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt31597?sid=2518&x=4885542',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt31604?sid=2518&x=4885543',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt32170?sid=2518&x=4885544',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt32310?sid=2518&x=4885545',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt31599?sid=2518&x=4885546',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt31602?sid=2518&x=4886036',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt31598?sid=2518&x=4886037',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt31603?sid=2518&x=4886038',
        'https://www.columbusmuseum.org/embark-collection/pages/Prt32196?sid=2518&x=4886039',
    )

    def parse_dept_name(self, response):
        return ''

    def parse_artist_name(self, response):
        names = response.css('.basicdetails .artistinfo .name a::text')

        return names.extract()

    def parse_artist_url(self, response):
        artist_url = response.css('.basicdetails .artistinfo .name a::attr(href)')

        artist_url = [
            urlparse.urljoin(response.url, fragment)
            for fragment
            in artist_url.extract()
        ]

        return artist_url

    def parse_title(self, response):
        title = response.css('.basicdetails h1.datename .name::text')

        return title.extract_first().strip()

    def parse_year(self, response):
        year = response.css('.basicdetails h1.datename .date::text')
        year = year.extract_first().strip()

        return year

    def parse_medium(self, response):
        year = response.css('.basicdetails div.medium::text')
        year = year.extract_first().strip()

        return year

    def parse_thumbnail(self, response):
        thumbnail_url = response.css('.photoCell a.photo::attr(href)')

        return thumbnail_url.extract_first()

    def parse_on_display(self, response):
        on_display = response.xpath(ON_DISPLAY_SELECTOR)

        return on_display.extract_first()

    def parse_accession_no(self, response):
        accession_no = response.css('.basicdetails .accession::text')

        return accession_no.extract_first().strip()

    def get_page_selectors(self, response):
        return PAGE_SELECTORS

    def get_artwork_detail_selector(self, response):
        return ARTWORK_DETAIL_SELECTOR

    def get_artwork_urls(self, response):
        artwork_detail_selector = self.get_artwork_detail_selector(response)

        return response.xpath(artwork_detail_selector).extract()

    # def parse(self, response):
    #     """Extracts artworks from ARTIC search results pages
    #     """

    #     # scrape all artworks on this page
    #     for artwork_url in self.get_artwork_urls(response):
    #         artwork_url = urlparse.urljoin(response.url, artwork_url)
    #         self.logger.debug('Requesting artwork detail: ' + artwork_url)
    #         # yield scrapy.Request(artwork_url, callback=self.parse_artwork)
