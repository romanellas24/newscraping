#!/usr/bin/env python
import dateparser
import pendulum
import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime
import datetime
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"https://www.pbs.org/newshour/show/"
DOMAIN_URL = f"www.pbs.org"


class PbsgetSpider(scrapy.Spider):
    timezone = "America/New_York"
    timeslot_day = ''
    timeslot_number = 0

    name = 'pbsGet'
    toD = datetime.datetime.today()
    delta = datetime.timedelta(1)
    toD -= delta
    url = toD.strftime("%B-%-d-%Y")
    print(url)
    isWeek = toD.weekday()
    # different urls for weekdays and weekends
    if isWeek < 5:
        searchurl = BASE_URL + str(url) + "-pbs-newshour-full-episode"
    else:
        searchurl = BASE_URL + str(url) + "-pbs-newshour-weekend-full-episode"

    allowed_domains = [DOMAIN_URL]
    start_urls = [searchurl.lower()]

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

        ddate = datetime.datetime.strptime(response.css(".video-single__title--large").css("span::text").get(),
                                           "%B %d, %Y")
        date_raw = ddate.strftime("%B %d, %Y")
        date = ddate.strftime("%Y-%m-%d")
        content = response.css(".playlist").css("li")
        titles = []
        durations = []
        urls = []
        rankeds = []
        i = 0
        for new in content:
            titles.append(new.css(".playlist__title::text").get())
            durations.append(new.css(".playlist__duration::text").get())
            urls.append(new.css("a::attr(href)").get())
            rankeds.append(i)
            i += 1

        edition = []
        for item in zip(titles, urls, durations, rankeds):
            scraped_info = {
                'title': item[0],
                'date_raw': date_raw,
                'date': date,
                'url': response.request.url,
                'news_url': item[1],
                'duration': item[2],
                'ranked': item[3],
                'epoch': time.time(),
                'language': "EN",
                'source': "PBS",
                'timeslot_day': self.timeslot_day,
                'timeslot_number': self.timeslot_number
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/EN/PBS"
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
        if hour in [23, 24]:
            return [day, 8]
        if hour == 1:
            return [dt.now() - datetime.timedelta(days=1), 8]

    def previousTimeSlot(self, day, timeslot_no: int):
        timeslot_no = timeslot_no - 1
        if timeslot_no == 0:
            timeslot_no = 8
            day - datetime.timedelta(days=1)
        return [day, timeslot_no]
