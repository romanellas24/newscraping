#!/usr/bin/env python
from typing import Union

import dateparser
import pendulum
import scrapy
import json
from os import path
from datetime import datetime, timedelta
from datetime import date
import time
import urllib.request

from scrapy import Spider
from twisted.internet.defer import Deferred

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.servizitelevideo.rai.it/televideo/pub"
CATE_URL = f"http://www.servizitelevideo.rai.it/televideo/pub/solotesto.jsp?categoria="
ARCH_URLS = [
    f"{CATE_URL}Prima&pagina=103",
    f"{CATE_URL}Politica&pagina=120",
    f"{CATE_URL}Politica&pagina=130",
    f"{CATE_URL}Dal%20Mondo&pagina=150"
]

globEdition = []


class TelegetSpider(scrapy.Spider):
    cate_conv = {'0': "First_Page",
                 '1': "Undefinied",
                 '2': "Politics",
                 '3': "Economics",
                 '4': "Italy",
                 '5': "Abroad",
                 '6': "Cultures"}

    base_url = "https://www.servizitelevideo.rai.it/televideo/pub/solotesto.jsp?pagina="

    name = 'teleGet'
    allowed_domains = ["www.servizitelevideo.rai.it"]
    start_urls = ARCH_URLS
    timezone = "Europe/Rome"
    timeslot_day = ''
    timeslot_number = 0

    filename = None

    def stringFormat(self, s):
        return s.replace('\n', ' ').replace('\\', '').replace('  ', ' ').strip()

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/IT/Televideo"
            scraped_data_filepath = f"{scraped_data_dir}/{spider.filename}"
            with open(scraped_data_filepath, "a") as f:
                json.dump(globEdition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

        now = datetime.now()
        now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
        now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
        if self.filename is None:
            self.filename = f"{now_s}E{now_epoch}.json"

        content = response.css("pre")
        titleString = content.css("::text").getall()
        titleString = titleString[0:len(titleString) - 1]
        titles = []
        urls = []
        contents = []
        placed = []
        ranked = []

        edition = []
        i = 0
        for info in titleString:
            if i % 2 == 0:
                titles.append(self.stringFormat(info))
                ranked.append(int(i / 2))
            else:
                url = self.base_url + info
                urls.append(url)
                contents.append("")
                if url[len(url) - 1] == "0":
                    placed.append("First_Page")
                else:
                    placed.append(self.cate_conv[url[len(url) - 2]])
            i += 1

        j = 0

        for item in zip(titles, urls, contents, ranked, placed):
            j += 1
            yield scrapy.Request(item[1], callback=self.getFullContent,
                                 meta={'data': item, 'currelem': j, 'edition': edition, 'oldurl': response.request.url})

    def getFullContent(self, response):
        content = response.css("pre::text").get()
        if response.request.url[len(response.request.url) - 1] == "0":
            content = ""
        item = response.meta.get('data')
        print(item)
        try:
            content = content.replace("\n", "").replace("   ", " ").replace("  ", " ").replace("- ", "")
        except:
            content = ""
            pass
        scraped_info = {
            'title': item[0],
            'date_raw': date.today().strftime("%B %d, %Y"),
            'date': date.today().strftime("%Y-%m-%d"),
            'url': response.meta.get('oldurl'),
            'news_url': item[1],
            'content': content,
            'ranked': item[3],
            'placed': item[4],
            'epoch': time.time(),
            'language': 'IT',
            'source': "Televideo",
            'timeslot_day': self.timeslot_day,
            'timeslot_number': self.timeslot_number
        }

        response.meta.get('edition').append(scraped_info)
        global globEdition
        globEdition.append(scraped_info)


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