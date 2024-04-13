#!/usr/bin/env python
from datetime import datetime
import datetime
import time
from os import path
import json
from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"https://www.pbs.org/newshour/show/"
DOMAIN_URL = f"www.pbs.org"


class PbsgetSpider(BaseScraper):
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
        super().parse(response)

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
                'local_time': self.calculate_local_time(),
                'timezone': self.timezone,
                'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/EN/PBS"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
