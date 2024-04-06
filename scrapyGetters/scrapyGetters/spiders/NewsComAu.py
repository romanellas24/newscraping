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

class RioTimes(BaseScraper):
    name = "NewsComAu"
    timezone = "Australia/Canberra"

    start_urls = [
        "https://www.news.com.au/content-feeds/latest-news-national/",
        "https://www.news.com.au/content-feeds/latest-news-world/",
        "https://www.news.com.au/content-feeds/latest-news-lifestyle/",
        "https://www.news.com.au/content-feeds/latest-news-travel/",
        "https://www.news.com.au/content-feeds/latest-news-entertainment/",
        "https://www.news.com.au/content-feeds/latest-news-technology/",
        "https://www.news.com.au/content-feeds/latest-news-finance/",
        "https://www.news.com.au/content-feeds/latest-news-sport/"
    ]
    referred_link = ''
    ranked = 0
    edition = []

    def parse(self, response):
        super().parse(response)

        for news in response.css("channel > item"):
            link = news.css("link::text").get()
            title = news.css("title::text").get()
            date_raw = response.css("pubDate::text").get()
            date_raw = str(dateparser.parse(date_raw).date())
            self.referred_link = response.url
            yield response.follow(link, self.parseArticle, meta={'parent': response.url,
                                                                 'title': title,
                                                                 'date_raw': date_raw})

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/EN/NewsComAu"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        #TODO : CONTINUE HERE
        parent_url = response.meta['parent']
        title = response.css("#story-headline::text").get()
        today = date.today()
        date_raw = response.css("#publish-date::text").get()
        date_parsed = dateparser.parse(date_raw)
        if date_parsed.date() != today:
            pass
        news_url = response.request.url
        content_paragraph = response.css('#story-primary p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()
        subtitle = response.css('#story-intro::text').get()

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            if p_content != None:
                content = content + p_content + "\n"

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
            'source': 'NewsComAu',
            'local_time': self.calculate_local_time()
        }
        self.edition.append(new)
