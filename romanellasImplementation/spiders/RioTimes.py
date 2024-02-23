import scrapy
from datetime import date


class QuoteSpider(scrapy.Spider):
    name = "RioTimes"
    start_urls = [
        "https://www.riotimesonline.com/latest-news/",
    ]
    referred_link = ''

    def parse(self, response):
        for news in response.xpath("//a[@rel='bookmark' and not(contains(@class, 'td-image-wrap '))]"):
            self.referred_link = response.request.url
            link = news.xpath("./@href").get()
            yield response.follow(link, self.parseArticle)

    def parseArticle(self, response):
        title = response.xpath("//h1[@class = 'tdb-title-text']/text()").get()
        today = date.today()
        date_raw = response.xpath("//div[@class = 'tdb-block-inner td-fix-index']/time/@datetime").get()
        news_url = response.request.url
        content_paragraph = response.xpath('//*[contains(@class, "tdb_single_content")]//p')
        content = ''
        for p in  content_paragraph:
            if not p.xpath('.//a[@href="#login"]'):
                content = content + p.xpath('./text()').get() #TODO: FIX


        yield {
            'title': title,
            'date_raw': date_raw,
            'date': today,
            'url': self.referred_link,
            'news_url': news_url,
            'subtitle': '',
            'content': content_paragraph
        }
