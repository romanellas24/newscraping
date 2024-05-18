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
        "https://www.sowetanlive.co.za/",
        "https://www.sowetanlive.co.za/news/south-africa/",
        "https://www.sowetanlive.co.za/news/africa/",
        "https://www.sowetanlive.co.za/news/world/",
        "https://www.sowetanlive.co.za/group/State_Capture/",
        "https://www.sowetanlive.co.za/sport/soccer/",
        "https://www.sowetanlive.co.za/sport/boxing/",
        "https://www.sowetanlive.co.za/sport/cricket/",
        "https://www.sowetanlive.co.za/sport/rugby/",
        "https://www.sowetanlive.co.za/entertainment/",
        "https://www.sowetanlive.co.za/pic-of-the-day/",
        "https://www.sowetanlive.co.za/opinion/columnists/",
        "https://www.sowetanlive.co.za/opinion/letters/",
        "https://www.sowetanlive.co.za/opinion/",
        "https://www.sowetanlive.co.za/s-mag/",
        "https://www.sowetanlive.co.za/s-mag/culture/",
        "https://www.sowetanlive.co.za/s-mag/fashion-beauty/",
        "https://www.sowetanlive.co.za/s-mag/food-drink/",
        "https://www.sowetanlive.co.za/s-mag/wellness/",
        "https://www.sowetanlive.co.za/s-mag/living/",
        "https://www.sowetanlive.co.za/business/",
        "https://www.sowetanlive.co.za/business/money/"
    ]
    referred_link = ''
    ranked = 0
    edition = []
    captured_news = []
    timeslot_day = ''
    timeslot_number = 0
    home_page = []

    def parse(self, response):
        super().parse(response)
        start_url = "https://www.sowetanlive.co.za"
        article_links = response.xpath("//a[contains(@aria-label, 'article')]/@href").getall()
        for article_link in article_links:
            link = f"{start_url}{article_link}"
            if response.url == self.start_urls[0] and response.url not in self.home_page:
                self.home_page.append(link)
            if link not in self.captured_news:
                self.captured_news.append(link)
                yield response.follow(link, self.parseArticle, meta={'parent': response.url})

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
        title = response.css("h1.article-title span::text").get()
        date_raw = response.css("span.article-pub-date::text").get()
        date_raw = dateparser.parse(date_raw.strip())
        date_raw = str(date_raw)
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
            'source': 'SowetanLive',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)
