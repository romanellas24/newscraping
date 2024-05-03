#!/usr/bin/env python
from os import path
import json
from datetime import date, datetime, timedelta
import time
import dateparser
from typing import Union

from defer import Deferred
from scrapy import Spider

from .BaseScraper import BaseScraper

NOW = datetime.now()
NOW_S = NOW.strftime("%Y-%m-%dT%H.%M.%S")
NOW_EPOCH = (NOW - datetime(1970, 1, 1)) / timedelta(seconds=1)
BASE_NAME = f"{NOW_S}E{NOW_EPOCH}.json"

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.agi.it"


class AgiHomePageSpider(BaseScraper):
    name = 'AgiHomePage'
    allowed_domains = [BASE_URL]
    start_urls = [
        "https://www.agi.it/"
    ]
    timezone = "Europe/Rome"
    timeslot_day = ''
    timeslot_number = 0
    edition = []
    captured = []

    def parse(self, response):
        super().parse(response)
        article_links = response.css("a.sequenceContainerTag::attr(href)").getall()
        for article in article_links:
            if article not in self.captured and "www.agi.it" in article:
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
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/IT/AGI"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.css("h1::text").get()
        today = date.today()
        date_raw = response.css("time.pubdate::text").get()
        if isinstance(date_raw, str) == False:
            pass
        date_parsed = dateparser.parse(date_raw)
        if date_parsed.date() != today:
            pass
        news_url = response.request.url
        content_paragraph = response.css('article p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()
        subtitle = response.css('div.fieldContainerTag::text').get()

        for p in content_paragraph:
            p_content = p.xpath(".//text()[2]").get()
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
            'language': 'IT',
            'source': 'AgiHomePage',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)