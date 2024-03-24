#!/usr/bin/env python
import dateparser
import pendulum
import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime, timedelta
from datetime import date
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
ARCH_URL = f"https://www.france24.com/en/archives/2024/03/"
MONTH = f"-March-2024"
BASE_URL = f"https://www.france24.com/en"
DOMAIN = "france24.com"


class FrgetSpider(scrapy.Spider):
    name = 'frGet'
    urls = []
    tod = date.today().strftime("%d")
    urls.append(ARCH_URL + str(tod) + MONTH)
    allowed_domains = [DOMAIN]
    start_urls = urls
    timezone = "Europe/Paris"
    timeslot_day = ''
    timeslot_number = 0

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

        news = response.css(".o-archive-day__list").css("li")
        titles = []
        urls = []
        raw_dates = []
        dates = []
        rankeds = []
        act_date = datetime.strptime(response.url[45:], "%d-%B-%Y")
        i = 0
        for new in news:
            titles.append(new.xpath("./a/h2/text()").get())
            urls.append("https://www.france24.com" + new.css("a::attr(href)").get())
            raw_dates.append(act_date.strftime("%B %d, %Y"))
            dates.append(act_date.strftime("%Y-%m-%d"))
            rankeds.append(i)
            i += 1

        edition = []
        for item in zip(titles, raw_dates, dates, urls, rankeds):
            scraped_info = {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.request.url,
                'news_url': item[3],
                'content': "",
                'ranked': item[4],
                'placed': "First_Page",
                'epoch': time.time(),
                'language': "EN",
                'source': "France24",
                'timeslot_day': self.timeslot_day,
                'timeslot_number': self.timeslot_number
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/EN/France24"
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
