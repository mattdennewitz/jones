# -*- coding: utf-8 -*-

import urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ArtworkItem


class MomaSpider(scrapy.Spider):
    name = 'moma'
    allowed_domains = ['moma.org']
    # start_urls = (
    #     'http://www.moma.org/collection/works?locale=en&classifications=&page=1',
    # )

    def __init__(self, category=None, *a, **kw):
        super(MomaSpider, self).__init__(category, *a, **kw)

        self.current_page = 1
        self.url_template = (
            'http://www.moma.org/collection/works?locale=en'
            '&classifications=&page={page}')

        self.start_urls = (
            self.url_template.format(page=self.current_page),
        )

    def get_start_urls(self):
        raise Exception('start urls')

    def parse_artwork(self, response):
        loader = ItemLoader(item=ArtworkItem(), response=response)
        loader.add_value('museum_code', 'moma')
        loader.add_css('artist_name', '.short-caption span a::text')

        artist_url = response.css(
            '.short-caption span a::attr(href)').extract()
        artist_url = urlparse.urljoin(response.url, artist_url[0])
        loader.add_value('artist_url', artist_url)

        loader.add_css('title', '.short-caption span.title p::text')
        loader.add_value('url', response.url)

        # thumbnails :/

        loader.add_xpath('on_display', """
            boolean(
                //div[contains(@class, "on-view") and not(contains(., "Not on view"))]
            )
        """.strip())

        loader.add_css('year', '.short-caption .date::text')

        medium = response.xpath(
            '//dl/dt[@class="label" and text()="Medium"]/following-sibling::dd[@class="text"]/text()')
        medium = medium.extract()
        if len(medium) > 0:
            loader.add_value('medium', medium[0])

        item = loader.load_item()

        yield item

    def parse(self, response):
        # scrape artwork on page
        artworks = response.css('.tile-container a.link--tile::attr(href)')
        for artwork_url in artworks.extract():
            artwork_url = urlparse.urljoin(response.url, artwork_url)
            self.logger.info('Requesting artwork detail: ' + artwork_url)
            yield scrapy.Request(artwork_url, callback=self.parse_artwork)

        has_more = response.xpath(
            'boolean(//button[@data-more-results-bottom-button])').extract()
        has_more = bool(int(has_more[0]))

        if has_more and self.current_page < 5:
            self.current_page += 1
            self.logger.info('Requesting next page: '
                             + str(self.current_page))
            yield scrapy.Request(
                self.url_template.format(page=self.current_page),
                callback=self.parse)
