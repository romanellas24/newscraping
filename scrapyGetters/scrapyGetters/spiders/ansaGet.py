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
import os
import errno

NOW = datetime.now()
NOW_S = NOW.strftime("%Y-%m-%dT%H.%M.%S")
NOW_EPOCH = (NOW - datetime(1970, 1, 1)) / timedelta(seconds=1)
BASE_NAME = f"{NOW_S}E{NOW_EPOCH}.json"

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.ansa.it"
RSS_URLS = ["https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
            "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml",
            "https://www.ansa.it/sito/notizie/politica/politica_rss.xml",
            ]

CATE_DICT = {"https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml": "Esteri",
             "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml": "Cronaca",
             "https://www.ansa.it/sito/notizie/politica/politica_rss.xml": "Politica",
             "https://www.ansa.it/sito/notizie/economia/economia_rss.xml": "Economia",
             "https://www.ansa.it/sito/notizie/sport/calcio/calcio_rss.xml": "Calcio",
             "https://www.ansa.it/sito/notizie/sport/sport_rss.xml": "Sport",
             "https://www.ansa.it/sito/notizie/cultura/cinema/cinema_rss.xml": "Cinema",
             "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml": "Top_News",
             "https://www.ansa.it/sito/notizie/cultura/cultura_rss.xml": "Cultura",
             "https://www.ansa.it/sito/ansait_rss.xml": "Ultim'ora"}


class AnsagetSpider(scrapy.Spider):
    name = 'ansaGet'
    allowed_domains = [BASE_URL]
    start_urls = RSS_URLS
    timezone = "Europe/Rome"
    timeslot_day = ''
    timeslot_number = 0

    def dateFormatter(self, dates_raw):
        dates = []
        for raw_date in dates_raw:
            if raw_date == "":
                dates.append(datetime.now().strftime("%Y-%m-%d"))
            else:
                raw_date = raw_date[5:16]
                if raw_date[len(raw_date) - 1] == ' ':
                    raw_date = raw_date[:len(raw_date) - 1]
                todate = datetime.strptime(raw_date, "%d %b %Y")
                dates.append(todate.strftime("%Y-%m-%d"))
        return dates

    def parse(self, response):
        articles = response.css("item")
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

        titles = []
        subtitles = []
        dates_raw = []
        urls = []

        for article in articles:
            titles.append(article.css("title::text").get())
            subtitles.append(article.css("description::text").get())
            dates_raw.append(article.css("pubDate::text").get())
            urls.append(article.css("link::text").get())

        dates = self.dateFormatter(dates_raw)

        edition = []
        i = 0
        for item in zip(titles, dates_raw, dates, urls, subtitles):
            i += 1
            yield scrapy.Request(item[3], callback=self.getFullContent,
                                 meta={'data': item, 'currelem': i, 'edition': edition, 'oldurl': response.request.url})

    def getFullContent(self, response):
        fullcont = response.css(".news-txt").css("p::text").getall()
        content = ''.join(fullcont)

        item = response.meta.get('data')
        scraped_info = {
            'title': item[0],
            'date_raw': item[1],
            'date': item[2],
            'url': response.meta.get('oldurl'),
            'news_url': item[3],
            'subtitle': item[4],
            'content': content,
            'ranked': response.meta.get('currelem'),
            'placed': CATE_DICT[response.meta.get('oldurl')],
            'epoch': time.time(),
            'language': 'IT',
            'source': 'ANSA',
            'timeslot_day': self.timeslot_day,
            'timeslot_number': self.timeslot_number
        }

        response.meta.get('edition').append(scraped_info)

        if response.meta.get('currelem') == len(item):
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/IT/ANSA_{CATE_DICT[response.meta.get('oldurl')]}"
            global BASE_NAME
            scraped_data_filepath = f"{scraped_data_dir}/{BASE_NAME}"
            if not os.path.exists(os.path.dirname(scraped_data_filepath)):
                try:
                    os.makedirs(os.path.dirname(scraped_data_filepath))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            with open(scraped_data_filepath, "w") as f:
                json.dump(response.meta.get('edition'), f, indent=4, ensure_ascii=False)
                f.write("\n")

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
