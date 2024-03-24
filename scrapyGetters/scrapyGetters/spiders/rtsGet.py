#!/usr/bin/env python
import pendulum
import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime, timedelta
import time
from os import path
import json
import dateparser

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"rts.ch"


class RtsgetSpider(scrapy.Spider):
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
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

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
                'timeslot_day': self.timeslot_day,
                'timeslot_number': self.timeslot_number
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/FR/RTS"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
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