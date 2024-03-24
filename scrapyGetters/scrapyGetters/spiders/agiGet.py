#!/usr/bin/env python
from datetime import datetime, timedelta
import time
from os import path
import json
import os
import errno
from .BaseScraper import BaseScraper

NOW = datetime.now()
NOW_S = NOW.strftime("%Y-%m-%dT%H.%M.%S")
NOW_EPOCH = (NOW - datetime(1970, 1, 1)) / timedelta(seconds=1)
BASE_NAME = f"{NOW_S}E{NOW_EPOCH}.json"

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.agi.it"
RSS_URLS = ["https://www.agi.it/estero/rss",
            "https://www.agi.it/politica/rss",
            "https://www.agi.it/cronaca/rss",
            ]

CATE_DICT = {"https://www.agi.it/estero/rss": "Esteri",
             "https://www.agi.it/economia/rss": "Economia",
             "https://www.agi.it/politica/rss": "Politica",
             "https://www.agi.it/cronaca/rss": "Cronaca",
             "https://www.agi.it/cultura/rss": "Cultura",
             "https://www.agi.it/sport/rss": "Sport",
             "https://www.agi.it/innovazione/rss": "Tecnologia",
             "https://www.agi.it/lifestyle/rss": "Lifestyle"
             }


class AgigetSpider(BaseScraper):
    name = 'agiGet'
    allowed_domains = [BASE_URL]
    start_urls = RSS_URLS
    timezone = "Europe/Rome"
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
        dates_raw = []
        urls = []
        contents = []

        for article in articles:
            titles.append(article.css("title::text").get())
            contents.append(
                article.css("description::text").get().replace("<p>", "").replace("<strong>", "").replace("</p>",
                                                                                                          "").replace(
                    "</strong", ""))
            dates_raw.append(article.css("pubDate::text").get())
            urls.append(article.css("link::text").get())

        dates = self.dateFormatter(dates_raw)

        edition = []
        i = 0
        for item in zip(titles, dates_raw, dates, urls, contents):
            i += 1
            scraped_info = {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.request.url,
                'news_url': item[3],
                'subtitle': "",
                "content": item[4],
                'ranked': i,
                'placed': CATE_DICT[response.request.url],
                'epoch': time.time(),
                'language': 'IT',
                'source': "AGI",
                'timeslot_day': self.timeslot_day,
                'timeslot_number': self.timeslot_number,
                'elapsed_hours_timeslot_end': self.elapsed_hours
            }
            edition.append(scraped_info)

        scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/IT/AGI_{CATE_DICT[response.request.url]}"
        global BASE_NAME
        scraped_data_filepath = f"{scraped_data_dir}/{BASE_NAME}"
        if not os.path.exists(os.path.dirname(scraped_data_filepath)):
            try:
                os.makedirs(os.path.dirname(scraped_data_filepath))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
        pass
