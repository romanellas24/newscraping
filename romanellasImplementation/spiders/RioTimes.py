import scrapy
from datetime import date
import time

from scrapy import Request


class QuoteSpider(scrapy.Spider):
    name = "RioTimes"

    start_urls = [
        "https://www.riotimesonline.com/"
    ]
    referred_link = ''
    ranked = 0

    def parse(self, response):
        for news in response.xpath("//a[@rel='bookmark' and not(contains(@class, 'td-image-wrap '))]"):
            link = news.xpath("./@href").get()
            self.referred_link = response.url
            yield response.follow(link, self.parseArticle)

        if response.url == "https://www.riotimesonline.com/":
            # Scrape other pages only if we are on main one
            for subpage in response.xpath("//ul[@id = 'menu-header-main-menu-2']//a"):
                subpage_link = subpage.xpath("./@href").get()
                self.referred_link = subpage_link
                yield response.follow(subpage_link, self.parse)

    def parseArticle(self, response):
        title = response.xpath("//h1[@class = 'tdb-title-text']/text()").get()
        today = date.today()
        date_raw = response.xpath("//div[@class = 'tdb-block-inner td-fix-index']/time/@datetime").get()
        news_url = response.request.url
        content_paragraph = response.xpath('//*[contains(@class, "tdb_single_content")]//p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            p_content = p_content.replace('To read the full NEWS and much more,', '')
            content = content + "\n" + p_content

        yield {
            'title': title,
            'date_raw': date_raw,
            'date': today,
            'url': 'https://www.riotimesonline.com/',
            'news_url': news_url,
            'subtitle': '',
            'content': content,
            'ranked': self.ranked,
            'placed': 'Abroad',
            'epoch': timestamp,
            'language': 'EN',
            'source': 'Rio Times'
        }
