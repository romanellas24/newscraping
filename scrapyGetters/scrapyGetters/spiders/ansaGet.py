#!/usr/bin/env python
import scrapy
from datetime import datetime, timedelta
import time
from os import path
import json
import os
import errno
from .BaseScraper import BaseScraper

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


class AnsagetSpider(BaseScraper):
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
        super().parse(response)

        articles = response.css("item")
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
            'local_time': self.calculate_local_time()
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
