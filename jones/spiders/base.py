# -*- coding: utf-8 -*-

import urlparse

import scrapy

from ..items import ArtworkItem, ArtworkLoader


__all__ = ('BaseArtworkSpider', )

class BaseArtworkSpider(scrapy.Spider):
    def parse_dept_name(self, response):
        raise NotImplementedError('parse_dept_name not implemented')

    def parse_artist_name(self, response):
        raise NotImplementedError('parse_artist_name not implemented')

    def parse_artist_url(self, response):
        raise NotImplementedError('parse_artist_url not implemented')

    def parse_title(self, response):
        raise NotImplementedError('parse_title not implemented')

    def parse_year(self, response):
        raise NotImplementedError('parse_year not implemented')

    def parse_medium(self, response):
        raise NotImplementedError('parse_medium not implemented')

    def parse_thumbnail(self, response):
        raise NotImplementedError('parse_thumbnail not implemented')

    def parse_on_display(self, response):
        raise NotImplementedError('parse_on_display not implemented')

    def parse_accession_no(self, response):
        raise NotImplementedError('parse_accession_no not implemented')

    def get_page_selectors(self, response):
        raise NotImplementedError('get_page_selectors not implemented')

    def get_artwork_detail_selector(self, response):
        raise NotImplementedError(
            'get_artwork_detail_selector not implemented')

    def parse_artwork(self, response):
        """Extracts information from an artwork detail page
        """

        loader = ArtworkLoader(item=ArtworkItem(), response=response)

        # create a url version free of search query noise
        url_bits = urlparse.urlparse(response.url)
        url_bits = url_bits._replace(query='')
        clean_url = urlparse.urlunparse(url_bits)

        loader.add_value('museum_code', self.name)
        loader.add_value('url', clean_url)

        loader.add_value('dept_name', self.parse_dept_name(response))
        loader.add_value('artist_name', self.parse_artist_name(response))
        loader.add_value('artist_url', self.parse_artist_url(response))
        loader.add_value('title', self.parse_title(response))
        loader.add_value('year', self.parse_year(response))
        loader.add_value('medium', self.parse_medium(response))
        loader.add_value('thumbnail', self.parse_thumbnail(response))
        loader.add_value('on_display', self.parse_on_display(response))
        loader.add_value('accession_no', self.parse_accession_no(response))

        item = loader.load_item()

        yield item

    def parse(self, response):
        """Extracts artworks from ARTIC search results pages
        """

        artwork_detail_selector = self.get_artwork_detail_selector(response)

        # scrape all artworks on this page
        for artwork_url in response.css(ARTWORK_DETAIL_SELECTOR).extract():
            artwork_url = urlparse.urljoin(response.url, artwork_url)
            self.logger.debug('Requesting artwork detail: ' + artwork_url)
            yield scrapy.Request(artwork_url, callback=self.parse_artwork)

        # if there's a next page, grab the next page
        for page_selector in self.get_page_selectors(response):
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
