#!/usr/bin/env python
import scrapy
from datetime import datetime, timedelta
import time
from os import path
import json
from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.spiegel.de"
RSS_URL = f"https://www.spiegel.de/ausland/index.rss"


class DwgetSpider(BaseScraper):
    name = 'dwGet'
    allowed_domains = [BASE_URL]
    start_urls = [RSS_URL]
    timezone = "Europe/Berlin"
    timeslot_day = ''
    timeslot_number = 0

    def dateFormatter(self, dates_raw):
        dates = []
        for raw_date in dates_raw:
            if raw_date == "":
                dates.append(datetime.now().strftime("%Y-%m-%d"))
            else:
                raw_date = raw_date[5:16]
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

        pass

    def getFullContent(self, response):
        fullcont = response.css(".RichText").css("p::text").getall()
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
            'placed': 'Abroad',
            'epoch': time.time(),
            'language': 'DE',
            'source': "Spiegel",
            'timeslot_day': self.timeslot_day,
            'timeslot_number': self.timeslot_number,
            'elapsed_hours_timeslot_end': self.elapsed_hours
        }

        response.meta.get('edition').append(scraped_info)

        if response.meta.get('currelem') == len(item):
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)

            base_name = f"{now_s}E{now_epoch}.json"
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/DE/Spiegel"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(response.meta.get('edition'), f, indent=4, ensure_ascii=False)
                f.write("\n")
