from os import path
from typing import Union

from datetime import date, datetime, timedelta
import time
from scrapy import Spider
from twisted.internet.defer import Deferred
import json
from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"


class ExpressoPt(BaseScraper):
    name = "ExpressoPt"
    timezone = "Europe/Lisbon"
    timeslot_day = ''
    timeslot_number = 0

    start_urls = [
        "https://expresso.pt/",
        "https://expresso.pt/ultimas",
        "https://expresso.pt/50-anos-25-de-abril",
        "https://expresso.pt/economia",
    ]
    base_url = "https://expresso.pt"
    referred_link = ''
    ranked = 0
    edition = []
    captured_titles = []

    def parse(self, response):
        super().parse(response)
        news_links = response.css("h2.title a::attr(href)").getall()
        for news_link in news_links:
            if "http" not in news_link and news_link not in self.captured_titles:
                self.captured_titles.append(news_link)
                news_link = f"{self.base_url}{news_link}"
                yield response.follow(news_link, self.parseArticle, meta={'parent': response.url})

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/PT/ExpressoPt"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.css("h1.title::text").get()
        date_raw = datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        today = date.today()
        news_url = response.request.url
        content_paragraph = response.css('#article-body-1 p::text').getall()
        content = " ".join(content_paragraph)
        content = content.strip()
        subtitle = response.css('p.g-article-lead::text').get()
        self.ranked = self.ranked + 1
        timestamp = time.time()

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
            'language': 'PT',
            'source': 'ExpressoPt',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)
