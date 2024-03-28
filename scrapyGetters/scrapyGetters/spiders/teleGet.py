#!/usr/bin/env python
from typing import Union

import scrapy
import json
from os import path
from datetime import datetime, timedelta
from datetime import date
import time

from scrapy import Spider
from twisted.internet.defer import Deferred
from .BaseScraper import BaseScraper

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


class TelegetSpider(BaseScraper):
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
        super().parse(response)

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
            'local_time': self.calculate_local_time()
        }

        response.meta.get('edition').append(scraped_info)
        global globEdition
        globEdition.append(scraped_info)
