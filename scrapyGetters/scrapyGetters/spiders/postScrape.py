#!/usr/bin/env python
import dateparser
import pendulum
import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime, timedelta
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.ilpost.it"
DOMAIN = "ilpost.it"
ARCH_URLS = [f"https://{BASE_URL}/mondo/"]

place_dict = {'https://www.ilpost.it/': "First_Page",
              'https://www.ilpost.it/mondo/': "Abroad",
              'https://www.ilpost.it/politica/': "Politics",
              'https://www.ilpost.it/economia/': "Economics"}


class PostscrapeSpider(scrapy.Spider):
    name = 'postScrape'
    allowed_domains = [DOMAIN]
    start_urls = ARCH_URLS
    edition = []
    timezone = "Europe/Rome"
    timeslot_day = ''
    timeslot_number = 0

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no


        articles = response.css("#main-content").css("article")
        titles = []
        dates_raw = []
        dates = []
        urls = []
        contents = []
        placeds = []
        rankeds = []

        i = 0
        for article in articles:
            tourl = article.xpath('./div/a/@href').get()
            urls.append(tourl)
            try:
                todate = datetime.strptime(tourl[22:32], "%Y/%m/%d")
            except:
                todate = datetime.now()
            dates.append(todate.strftime("%Y-%m-%d"))
            dates_raw.append(todate.strftime("%B %d, %Y"))
            info = article.css(".entry-content")
            titles.append(article.xpath('./div/a/h2/text()').get())
            contents.append(article.xpath('./div/a/p/text()').get())
            placeds.append(place_dict[response.url])
            rankeds.append(i)
            i += 1

        self.edition = []
        i = 0
        for item in zip(titles, dates_raw, dates, urls, contents, rankeds, placeds):
            i += 1
            yield scrapy.Request(item[3], callback=self.getFullContent,
                                 meta={'data': item, 'currelem': i, 'oldurl': response.request.url})

    def getFullContent(self, response):
        fullcont = response.css("#singleBody").css("p::text").getall()
        content = ''.join(fullcont)

        item = response.meta.get('data')
        scraped_info = {
            'title': item[0],
            'date_raw': item[1],
            'date': item[2],
            'url': response.meta.get('oldurl'),
            'news_url': item[3],
            'subtitle': (item[4] if item[4] is not None else ""),
            'content': content,
            'ranked': item[5],
            'placed': item[6],
            'epoch': time.time(),
            'language': 'IT',
            'source': "ilPost",
            'timeslot_day': self.timeslot_day,
            'timeslot_number': self.timeslot_number
        }

        self.edition.append(scraped_info)

    def close(spider, reason):
        now = datetime.now()
        now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
        now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)

        base_name = f"{now_s}E{now_epoch}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/IT/ilPost"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "a") as f:
            json.dump(spider.edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
        return super().close(spider, reason)

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
        if hour == 23:
            return [day, 8]
        if hour in [0, 1]:
            return [dt.now() - timedelta(days=1), 8]

    def previousTimeSlot(self, day, timeslot_no: int):
        timeslot_no = timeslot_no - 1
        if timeslot_no == 0:
            timeslot_no = 8
            day = day - timedelta(days=1)
        return [day, timeslot_no]
