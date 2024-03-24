#!/usr/bin/env python
from datetime import datetime
from datetime import date
import time
from os import path
import json
from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
ARCH_URL = f"https://www.france24.com/en/archives/2024/03/"
MONTH = f"-March-2024"
BASE_URL = f"https://www.france24.com/en"
DOMAIN = "france24.com"


class FrgetSpider(BaseScraper):
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
        super().parse(response)

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
                'timeslot_number': self.timeslot_number,
                'elapsed_hours_timeslot_end': self.elapsed_hours
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/EN/France24"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
