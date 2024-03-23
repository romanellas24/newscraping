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
DOMAIN = "zdf.de"
BASE_URL = f"https://www.zdf.de/nachrichten/heute-19-uhr/"
NINETEEN_ENDING = "-heute-sendung-19-uhr-100.html"


# QUESTO SCRIPT VA USATO SOLO DOPO (CIRCA) LE 20, PRIMA L'EDIZIONE NON VIENE TROVATA NEL SITO CAUSANDO UN CRASH (nello script "letsScrape" è tutto controllato)

class ZdfgetSpider(scrapy.Spider):
    name = 'zdfGet'
    today = datetime.today().strftime("%y%m%d")
    allowed_domains = [DOMAIN]
    # start_urls = [f"{BASE_URL}{today}{NINETEEN_ENDING}"]
    start_urls = [BASE_URL]
    timezone = "Europe/Berlin"
    timeslot_day = ''
    timeslot_number = 0

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

        # Pick the second element because there is the eng version
        mainTitle = response.xpath("(//h3[@class = 'item-title teaser-title'])[1]")
        link = mainTitle.xpath("./a/@href").get()
        link = response.url + link
        yield response.follow(link, callback=self.parse_sub_page)

    def parse_sub_page(self, response):
        box = response.css(".details")
        box_titles = box.css(".item-description::text").get()
        titles = box_titles.split(";")

        box_dates = box.css(".teaser-info::text").getall()
        date = box_dates[1]

        url = response.url

        ranks = []
        contents = []
        for i in range(0, len(titles)):
            returning = ""
            tcont = titles[i].split("-")
            if len(tcont) > 1:
                tcont = tcont[1:len(tcont)]
                for cont in tcont:
                    returning += cont + ""
            contents.append(returning)
            ranks.append(i)

        edition = []
        for item in zip(titles, contents, ranks):
            scraped_info = {
                'title': item[0].replace("\n", "").strip(),
                'date_raw': datetime.strptime(date, "%d.%m.%Y").strftime("%B %d, %Y"),
                'date': datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d"),
                'url': response.request.url,
                'news_url': url,
                'content': item[1],
                'ranked': item[2],
                'placed': "First_Page",
                'epoch': time.time(),
                'langauge': "DE",
                'source': "Zdf",
                'timeslot_day': self.timeslot_day,
                'timeslot_number': self.timeslot_number
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/DE/Zdf"
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
            return [dt.now() - timedelta(days=1), 8]

    def previousTimeSlot(self, day, timeslot_no: int):
        timeslot_no = timeslot_no - 1
        if timeslot_no == 0:
            timeslot_no = 8
            day = day - timedelta(days=1)
        return [day, timeslot_no]
