from os import path
from typing import Union

from datetime import date, datetime, timedelta
import time
import dateparser
from scrapy import Spider
from twisted.internet.defer import Deferred
import json

from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"


class NineNews(BaseScraper):
    name = "9News"
    timezone = "Australia/Sydney"

    start_urls = [
        "https://www.9news.com.au/",
        "https://www.9news.com.au/finance",
        "https://www.9news.com.au/world",
        "https://www.9news.com.au/politics",
        "https://www.9news.com.au/tech",

    ]

    referred_link = ''
    ranked = 0
    edition = []
    captured = []
    home_page = []
    base_url = "www.9news.com.au"
    base_http = "https://www.9news.com.au"

    def parse(self, response):
        super().parse(response)
        total_links = []
        article_links = response.css("a.takeover__link::attr(href)").getall()
        for article in article_links:
            total_links.append(article)

        article_links = response.css("a.story__link::attr(href)").getall()
        for article in article_links:
            total_links.append(article)

        article_links = response.css("a.story__headline__link::attr(href)").getall()
        for article in article_links:
            total_links.append(article)

        for article in total_links:
            if self.base_http in article and article not in self.start_urls:
                if self.start_urls[0] == response.url:
                    self.home_page.append(article)

                if article not in self.captured:
                    self.captured.append(article)
                    yield response.follow(article, self.parseArticle, meta={'parent': response.url})

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/EN/9News"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.css("h1.article__headline::text").get()
        today = date.today()
        date_raw = response.xpath("//time[@class = 'text--byline']/@datetime").get()
        if isinstance(date_raw, str) == False:
            pass
        news_url = response.request.url
        content_paragraph = response.css('div.article__body-croppable div.block-content span')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()
        subtitle = ""

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            if p_content != None:
                content = content + p_content + "\n"

        if news_url in self.home_page:
            parent_url = self.start_urls[0]

        if news_url in self.home_page:
            parent_url = self.start_urls[0]

        new = {
            'title': title,
            'date_raw': date_raw,  # Directly from the document
            'date': today,
            'url': parent_url,
            'news_url': news_url,
            'subtitle': subtitle,
            'content': content,
            'ranked': self.ranked,
            'placed': 'Abroad',
            'epoch': timestamp,
            'language': 'EN',
            'source': '9News',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)
