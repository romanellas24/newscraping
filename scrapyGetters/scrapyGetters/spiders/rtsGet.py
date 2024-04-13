#!/usr/bin/env python
from .BaseScraper import BaseScraper
import time
from os import path
import json
import dateparser

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"rts.ch"


class RtsgetSpider(BaseScraper):
    name = 'rtsGet'
    f = open("rtsurls.txt", "r+")
    toGetUrls = f.read()
    toGetUrls = toGetUrls.split("\n")
    toGetUrls = list(dict.fromkeys(toGetUrls))
    allowed_domains = [BASE_URL]
    print(toGetUrls)
    start_urls = toGetUrls
    timezone = "Europe/Paris"
    timeslot_day = ''
    timeslot_number = 0

    def parse(self, response):
        super().parse(response)

        chapters = response.css(".audio-chapter-list").css("ul").css("li")
        todate = response.css(".timeframe").css("span")
        descriptive_date = todate[1].css("::text").get()
        # Cleaning date to prevent dateparse exceptions
        descriptive_date = descriptive_date.replace("Episode d'", "")
        descriptive_date = descriptive_date.replace("Episode du", "")
        todate = dateparser.parse(descriptive_date, locales=['fr']).date()
        chapters = chapters[1:len(chapters)]
        titles = []
        dates_raw = []
        dates = []
        urls = []
        rankeds = []
        durations = []
        i = 0
        for chapter in chapters:
            urls.append("https://www." + BASE_URL + chapter.css("a::attr(href)").get())
            titles.append(chapter.css(".title::text").get())
            durations.append(chapter.css(".duration::text").get())
            dates_raw.append(todate.strftime("%B %d, %Y"))
            dates.append(todate.strftime("%Y-%m-%d"))
            rankeds.append(i)
            i += 1

        edition = []
        for item in zip(titles, dates_raw, dates, urls, durations, rankeds):
            scraped_info = {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.request.url,
                'news_url': item[3],
                'duration': item[4],
                'ranked': item[5],
                'epoch': time.time(),
                'language': "FR",
                'source': "RTS",
                'local_time': self.calculate_local_time(),
                'timezone': self.timezone,
                'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/FR/RTS"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
