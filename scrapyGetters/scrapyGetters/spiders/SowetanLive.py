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


class SowetanLive(BaseScraper):
    name = "SowetanLive"
    timezone = "Africa/Johannesburg"

    start_urls = [
        "https://www.sowetanlive.co.za/rss/?publication=sowetan-live"
    ]
    referred_link = ''
    ranked = 0
    edition = []
    timeslot_day = ''
    timeslot_number = 0

    def parse(self, response):
        super().parse(response)

        for news in response.css("channel > item"):
            link = news.css("link:nth-child(2)::text").get()
            title = news.css("title::text").get()
            date_raw = news.css("pubDate::text").get()
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
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/EN/SowetanLive"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.meta['title']
        date_raw = response.meta['date_raw']
        today = date.today()
        news_url = response.request.url
        content_paragraph = response.css('.text > p::text').getall()
        content = " ".join(content_paragraph)
        content = content.strip()
        if content == '':
            content_paragraph = response.css('.text > p > span::text').getall()
            content = " ".join(content_paragraph)
            content = content.strip()
        subtitle = response.css('div.image-text > .description::text').get()
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
            'language': 'EN',
            'source': 'SowetanLive',
            'timeslot_day': self.timeslot_day,
            'timeslot_number': self.timeslot_number,
            'elapsed_hours_timeslot_end': self.elapsed_hours
        }
        self.edition.append(new)
