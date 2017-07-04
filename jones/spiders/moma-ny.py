# -*- coding: utf-8 -*-

import re
import urlparse

import scrapy

from .base import BaseArtworkSpider


class MomaSpider(BaseArtworkSpider):
    name = 'moma'
    allowed_domains = ['moma.org']

    def __init__(self, category=None, *a, **kw):
        super(MomaSpider, self).__init__(category, *a, **kw)

        self.current_page = 1
        self.url_template = (
            'http://www.moma.org/collection/works?locale=en'
            '&classifications=&page={page}')

        self.start_urls = (
            self.url_template.format(page=self.current_page),
        )

    def parse_dept_name(self, response):
        dept_name = response.xpath(
            '//dt[contains(., "Department")]/following-sibling::dd/text()')
        dept_name = dept_name.extract_first().strip()

        return dept_name

    def parse_artist_name(self, response):
        name = response.xpath(
            '//div[contains(@class, "short-caption")]/h2/a/text()')
        name = name.extract()

        return [n.strip() for n in name]

    def parse_artist_url(self, response):
        artist_url = response.xpath(
            '//div[contains(@class, "short-caption")]/h2/a/@href')
        artist_url = [
            urlparse.urljoin(response.url, fragment)
            for fragment
            in artist_url.extract()
        ]

        return artist_url

    def parse_title(self, response):
        title = response.xpath(
            '//div[contains(@class, "short-caption")]/h1//text()')
        title = ''.join(title.extract()).strip()

        return title

    def parse_year(self, response):
        year = response.css(
            '.collection .layout-wrapper .short-caption h3::text')

        return year.extract_first().strip()

    def parse_medium(self, response):
        medium = response.xpath(
            '//dt[contains(., "Medium")]/following-sibling::dd/text()')
        medium = medium.extract_first()

        if medium:
            return medium.strip()

        return medium

    def parse_thumbnail(self, response):
        return ''

    def parse_on_display(self, response):
        return not u'is not on view' in response.text

    def parse_accession_no(self, response):
        a_no = response.xpath(
            '//dt[contains(., "Object number")]/following-sibling::dd/text()')
        a_no = a_no.extract_first().strip()

        return a_no

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

        if has_more:
            self.current_page += 1
            self.logger.info('Requesting next page: '
                             + str(self.current_page))
            yield scrapy.Request(
                self.url_template.format(page=self.current_page),
                callback=self.parse)
