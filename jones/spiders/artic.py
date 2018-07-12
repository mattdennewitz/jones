# -*- coding: utf-8 -*-

from urllib import parse as urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ArtworkItem


ARTWORK_DETAIL_SELECTOR = 'div.results-item-container .details a::attr(href)'

ON_DISPLAY_SELECTOR = """
boolean(
    //div[@id="tombstone" and not(contains(., "Not on Display"))]
)
""".strip()

PAGE_SELECTORS = (
    'div.pager > a.pager-next::attr(href)',
    'div.pager > a.pager-last::attr(href)',
)

class ArticSpider(scrapy.Spider):
    name = 'artic'
    allowed_domains = ['artic.edu']
    start_urls = (
        'http://www.artic.edu/aic/collections/artwork-search/results/all',
    )

    def parse_artwork(self, response):
        """Extracts information from an artwork detail page
        """

        # create a url version free of search query noise
        url_bits = urlparse.urlparse(response.url)
        url_bits = url_bits._replace(query='')
        clean_url = urlparse.urlunparse(url_bits)

        loader = ItemLoader(item=ArtworkItem(), response=response)
        loader.add_value('museum_code', self.name)
        loader.add_value('url', clean_url)
        loader.add_xpath('artist_name',
                         '//div[@id="tombstone"]/p[1]/a/text()[1]')

        artist_url = response.xpath('//div[@id="tombstone"]/p[1]/a/@href')
        artist_url = urlparse.urljoin(response.url, artist_url.extract()[0])
        loader.add_value('artist_url', artist_url)

        loader.add_css('title', '#tombstone span:nth-of-type(1)::text')
        loader.add_xpath('thumbnail',
                         '//div[@id="artwork-image"]/a/img/@src')
        loader.add_xpath('on_display', ON_DISPLAY_SELECTOR)
        item = loader.load_item()

        self.logger.info('Scraped ' + item['title'][0])

        yield item

    def parse(self, response):
        """Extracts artworks from ARTIC search results pages
        """

        # scrape all artworks on this page
        for artwork_url in response.css(ARTWORK_DETAIL_SELECTOR).extract():
            artwork_url = urlparse.urljoin(response.url, artwork_url)
            self.logger.info('Requesting artwork detail: ' + artwork_url)
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
