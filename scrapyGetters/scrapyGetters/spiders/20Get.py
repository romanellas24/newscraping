#!/usr/bin/env python
from datetime import datetime
import time
from os import path
import json
from scrapy.crawler import CrawlerProcess
import vcr
from urllib.request import urlopen
from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
ARCH_URL = "https://www.tagesschau.de/multimedia/video/videoarchiv2.html"
BASE_URL = "https://www.tagesschau.de"
DOMAIN = "tagesschau.de"


class A20getSpider(BaseScraper):
    name = '20Get'
    allowed_domains = [DOMAIN]
    start_urls = [ARCH_URL]
    timezone = "Europe/Berlin"
    timeslot_day = ''
    timeslot_number = 0

    def check20Tagess(self, box) -> bool:
        if (box.css(".teaser-right__headline").css("span::text").get() == "tagesschau"
                and box.css(".teaser-right__date::text").get()[13:18] == "20:00"):
            return True
        else:
            return False

    def parse(self, response):
        super().parse(response)

        boxes = response.css(".copytext-element-wrapper__vertical-only")
        toRet = []
        for box in boxes:
            box = box.css(".teaser-right")
            if len(box) == 0:
                continue
            if self.check20Tagess(box[0]):
                toRet.append(box)

        for box in toRet:
            following_link = box.css(".teaser-right__link").xpath('@href').extract()[0]
            following_link = BASE_URL + following_link
            yield response.follow(following_link, callback=self.parse_sub_page, meta={'parent': response.url})

    def parse_sub_page(self, response):
        titles = response.css('.mediaplayer-subline__details p::text').get().split(",")
        parent_url = response.meta['parent']
        contents = ""
        findUrl = response.request.url
        findDate = str(response.css(".multimediahead__date::text").get())[7:17]
        dates = datetime.strptime(findDate, "%d.%m.%Y").strftime("%B %d, %Y")
        edition = []
        i = 0
        for title in titles:
            scraped_info = {
                'title': title.strip(),
                'date_raw': dates,
                'date': datetime.strptime(dates, "%B %d, %Y").strftime("%Y-%m-%d"),
                'url': parent_url,
                'url_news': findUrl,
                'content': contents,
                'ranked': str(i),
                'epoch': time.time(),
                'language': "DE",
                'source': "Tagesschau",
                'timeslot_day': self.timeslot_day,
                'timeslot_number': self.timeslot_number,
                'elapsed_hours_timeslot_end': self.elapsed_hours,
                'local_time': self.calculate_local_time()
            }
            i += 1
            edition.append(scraped_info)

        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/DE/Tagesschau"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent=4, ensure_ascii=False)
            f.write("\n")

        global testdir
        testdir = f"{scraped_data_filepath}"


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })

    process.crawl(A20getSpider)
    process.start()
    f = open(testdir)
    response = json.load(f)
    f.close()
    with vcr.use_cassette('fixtures/vcr_cassettes/Tagesschau.yaml'):
        myres = urlopen(ARCH_URL).read()
        if len(myres) > 0:
            assert 0 < len(response)
            assert response[0]['title'] is not None
            for thisresp in response:
                assert str.encode(thisresp['title']) in myres
                assert thisresp['url_news'] is not None
