from os import path
from typing import Union

import scrapy
from datetime import date, datetime, timedelta
import time
import dateparser
from scrapy import Spider
from twisted.internet.defer import Deferred
import json
import pendulum

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"


class SowetanLive(scrapy.Spider):
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
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

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
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/ZA/SowetanLive"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def calculateLocalTimeSlot(self):
        pen = pendulum.now()
        return pen.in_timezone(self.timezone).to_datetime_string()

    def calculateTimeSlot(self, dt: str):
        dt = dateparser.parse(dt)
        day = dt.date()
        hour = dt.hour
        if hour in [2, 3, 4]:
            return [day, 1]
        if hour in [5, 6, 7]:
            return [day, 2]
        if hour in [8, 9, 10]:
            return [day, 3]
        if hour in [11, 12, 13]:
            return [day, 4]
        if hour in [14, 15, 16]:
            return [day, 5]
        if hour in [17, 18, 19]:
            return [day, 6]
        if hour in [20, 21, 22]:
            return [day, 7]
        if hour in [23, 24]:
            return [day, 8]
        if hour == 1:
            return [dt.now() - timedelta(days=1), 8]

    def previousTimeSlot(self, day, timeslot_no: int):
        timeslot_no = timeslot_no - 1
        if timeslot_no == 0:
            timeslot_no = 8
            day = day - timedelta(days=1)
        return [day, timeslot_no]

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
            'timeslot_number': self.timeslot_number
        }
        self.edition.append(new)
