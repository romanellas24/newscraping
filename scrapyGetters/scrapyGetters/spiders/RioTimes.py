from os import path
from typing import Union

import scrapy
from datetime import date, datetime, timedelta
import time
import dateparser
from scrapy import Spider
from twisted.internet.defer import Deferred
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"

class RioTimes(scrapy.Spider):
    name = "RioTimes"

    start_urls = [
        "https://www.riotimesonline.com/"
    ]
    referred_link = ''
    ranked = 0
    edition = []

    def parse(self, response):
        for news in response.xpath("//a[@rel='bookmark' and not(contains(@class, 'td-image-wrap '))]"):
            link = news.xpath("./@href").get()
            self.referred_link = response.url
            yield response.follow(link, self.parseArticle, meta={'parent': response.url})

        if response.url == "https://www.riotimesonline.com/":
            # Scrape other pages only if we are on main one
            for subpage in response.xpath("//ul[@id = 'menu-header-main-menu-2']//a"):
                subpage_link = subpage.xpath("./@href").get()
                self.referred_link = subpage_link
                yield response.follow(subpage_link, self.parse)

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/BR/RioTimes"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

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
            'source': 'Rio Times'
        }
        self.edition.append(new)
