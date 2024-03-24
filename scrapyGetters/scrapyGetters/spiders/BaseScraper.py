from os import path

import pendulum
import scrapy
from datetime import date, timedelta
import time
import dateparser

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"

class BaseScraper(scrapy.Spider):
    timezone = ""
    timeslot_day = ''
    timeslot_number = 0
    referred_link = ''
    ranked = 0
    edition = []

    def parse(self, response):
        [day, timeslot_no] = self.calculateTimeSlot(self.calculateLocalTimeSlot())
        [day, timeslot_no] = self.previousTimeSlot(day, timeslot_no)
        self.timeslot_day = day.strftime("%Y-%m-%d")
        self.timeslot_number = timeslot_no

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

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.xpath("//h1[@class = 'tdb-title-text']/text()").get()
        today = date.today()
        date_raw = response.xpath("//div[@class = 'tdb-block-inner td-fix-index']/time/@datetime").get()
        date_parsed = dateparser.parse(date_raw)
        if date_parsed.date() != today:
            pass
        news_url = response.request.url
        content_paragraph = response.xpath('//*[contains(@class, "tdb_single_content")]//p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            p_content = p_content.replace('To read the full NEWS and much more,', '')
            content = content + "\n" + p_content

        new = {
            'title': title,
            'date_raw': date_raw,  # Directly from the document
            'date': today,
            'url': parent_url,
            'news_url': news_url,
            'subtitle': '',
            'content': content,
            'ranked': self.ranked,
            'placed': 'Abroad',
            'epoch': timestamp,
            'language': 'EN',
            'source': 'Rio Times',
            'timeslot_day': self.timeslot_day,
            'timeslot_number': self.timeslot_number
        }
        self.edition.append(new)
