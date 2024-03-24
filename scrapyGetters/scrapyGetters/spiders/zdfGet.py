#!/usr/bin/env python
from datetime import datetime
import time
from os import path
import json
from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
DOMAIN = "zdf.de"
BASE_URL = f"https://www.zdf.de/nachrichten/heute-19-uhr/"
NINETEEN_ENDING = "-heute-sendung-19-uhr-100.html"


# QUESTO SCRIPT VA USATO SOLO DOPO (CIRCA) LE 20, PRIMA L'EDIZIONE NON VIENE TROVATA NEL SITO CAUSANDO UN CRASH (nello script "letsScrape" è tutto controllato)

class ZdfgetSpider(BaseScraper):
    name = 'zdfGet'
    today = datetime.today().strftime("%y%m%d")
    allowed_domains = [DOMAIN]
    # start_urls = [f"{BASE_URL}{today}{NINETEEN_ENDING}"]
    start_urls = [BASE_URL]
    timezone = "Europe/Berlin"
    timeslot_day = ''
    timeslot_number = 0

    def parse(self, response):
        super().parse(response)

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
                'timeslot_number': self.timeslot_number,
                'elapsed_hours_timeslot_end': self.elapsed_hours
            }
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/DE/Zdf"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")
