import scrapy
from datetime import date
import time


class QuoteSpider(scrapy.Spider):
    name = "RioTimes"
    start_urls = [
        "https://www.riotimesonline.com/",
        "https://www.riotimesonline.com/latest-news/",
        "https://www.riotimesonline.com/brazil-news/category/brazil/",
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/",
        'https://www.riotimesonline.com/brazil-news/category/sao-paulo/business-sao-paulo/',
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/politics-sao-paulo/",
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/life-sao-paulo/",
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/entertainment-sao-paulo/",
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/art-culture-sao-paulo/",
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/travel-sao-paulo/",
        "https://www.riotimesonline.com/brazil-news/category/sao-paulo/in-depth-sao-paulo/"
    ]
    referred_link = ''
    ranked = 0

    def parse(self, response):
        for news in response.xpath("//a[@rel='bookmark' and not(contains(@class, 'td-image-wrap '))]"):
            link = news.xpath("./@href").get()
            self.referred_link = response.request.url
            yield response.follow(link, self.parseArticle)

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
            'url': self.referred_link,
            'news_url': news_url,
            'subtitle': '',
            'content': content,
            'ranked': self.ranked,
            'placed': 'Abroad',
            'epoch': timestamp,
            'language': 'EN',
            'source': 'Rio Times'
        }
