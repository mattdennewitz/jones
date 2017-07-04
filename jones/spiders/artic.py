# -*- coding: utf-8 -*-

import re
import urlparse

import scrapy

from ..items import ArtworkItem, ArtworkLoader
from .base import BaseArtworkSpider


ARTWORK_DETAIL_SELECTOR = 'div.results-item-container .details a::attr(href)'

ON_DISPLAY_SELECTOR = """
boolean(
    //div[@id="tombstone" and not(contains(., "Not on Display"))]
)
""".strip()

ACCESSION_RE = re.compile(r'(\d{4}\.\d+)')

PAGE_SELECTORS = (
    'div.pager > a.pager-next::attr(href)',
    'div.pager > a.pager-last::attr(href)',
)

class ArticSpider(BaseArtworkSpider):
    name = 'artic'
    allowed_domains = ['artic.edu']
    start_urls = (
        'http://www.artic.edu/aic/collections/artwork-search/results/all',
    )

    def parse_dept_name(self, response):
        dept_name = (response
                     .xpath('//p[@id="dept-gallery"]//text()')
                     .extract_first()
                     .splitlines())

        return dept_name[0].strip()

    def parse_artist_name(self, response):
        names = response.xpath('//div[@id="tombstone"]/p[1]/a/text()[1]')

        return names.extract()

    def parse_artist_url(self, response):
        artist_url = response.xpath('//div[@id="tombstone"]/p[1]/a/@href')
        artist_url = [
            urlparse.urljoin(response.url, fragment)
            for fragment
            in artist_url.extract()
        ]

        return artist_url

    def parse_title(self, response):
        title = response.css('#tombstone span:nth-of-type(1)::text')

        return title.extract_first()

    def parse_year(self, response):
        year = response.css('#tombstone p:nth-of-type(2)::text')
        year = year.extract_first().strip()

        return year

    def parse_medium(self, response):
        tombstone = response.xpath('//div[@id="tombstone"]/p[3]/text()')
        lines = filter(lambda l: l.strip(), tombstone.extract_first().splitlines())
        first_line = lines[0].strip()

        if ' x ' in first_line:
            # no description given, probably the measurements?
            self.logger.debug('Found dimensions in first line of tombstone')
            return ''

        if ACCESSION_RE.search(first_line) is not None:
            # bequeathment line, probably?
            self.logger.debug(
                'Found accession info in first line of tombstone')
            return ''

        self.logger.debug('Found medium <{}>'.format(first_line))

        return first_line

    def parse_thumbnail(self, response):
        thumbnail_url = response.xpath(
            '//div[@id="artwork-image"]/a/img/@src')

        return thumbnail_url.extract_first()

    def parse_on_display(self, response):
        on_display = response.xpath(ON_DISPLAY_SELECTOR)

        return on_display.extract_first()

    def parse_accession_no(self, response):
        matches = ACCESSION_RE.search(response.body)

        if matches is None:
            return None

        return matches.group(1)

    def get_page_selectors(self, response):
        return PAGE_SELECTORS

    def get_artwork_detail_selector(self, response):
        return ARTWORK_DETAIL_SELECTOR

    def parse(self, response):
        """Extracts artworks from ARTIC search results pages
        """

        # scrape all artworks on this page
        for artwork_url in response.css(ARTWORK_DETAIL_SELECTOR).extract():
            artwork_url = urlparse.urljoin(response.url, artwork_url)
            self.logger.debug('Requesting artwork detail: ' + artwork_url)
            yield scrapy.Request(artwork_url, callback=self.parse_artwork)

        # if there's a next page, grab the next page
        for page_selector in PAGE_SELECTORS:
            pager = response.css(page_selector).extract()

            if len(pager) == 0:
                self.logger.warning('Skipping selector '
                                    + page_selector
                                    + ' with 0 results')
                continue

            for url in pager:
                url = urlparse.urljoin(response.url, url)

                self.logger.info('Requesting next page: ' + url)

                yield scrapy.Request(url, callback=self.parse)

            break
