from os import path
from typing import Union

from datetime import date, datetime, timedelta
import time
from scrapy import Spider
from twisted.internet.defer import Deferred
import json

from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"


class LosAngelesTimes(BaseScraper):
    name = "LosAngelesTimes"
    timezone = "America/Los_Angeles"
    timeslot_day = ''
    timeslot_number = 0

    start_urls = [
        "https://www.latimes.com/",
        "https://www.latimes.com/california",
        "https://www.latimes.com/topic/california-law-politics",
        "https://www.latimes.com/topic/earthquakes",
        "https://www.latimes.com/topic/education",
        "https://www.latimes.com/topic/fires",
        "https://www.latimes.com/homeless-housing",
        "https://www.latimes.com/california/latino-life",
        "https://www.latimes.com/california/orange-county",
        "https://www.latimes.com/socal/daily-pilot/",
        "https://www.latimes.com/entertainment-arts",
        "https://www.latimes.com/entertainment-arts/movies",
        "https://www.latimes.com/entertainment-arts/tv",
        "https://www.latimes.com/entertainment-arts/awards",
        "https://www.latimes.com/entertainment-arts/music",
        "https://www.latimes.com/entertainment-arts/business",
        "https://www.latimes.com/topic/arts",
        "https://www.latimes.com/entertainment-arts/books",
        "https://www.latimes.com/topic/theater",
        "https://www.latimes.com/topic/museums",
        "https://www.latimes.com/topic/comedy",
        "https://www.latimes.com/topic/behold",
        "https://www.latimes.com/topic/hero-complex",
        "https://www.latimes.com/entertainment-arts/movies",
        "https://www.latimes.com/entertainment-arts/tv",
        "https://www.latimes.com/entertainment-arts/awards",
        "https://www.latimes.com/entertainment-arts/music",
        "https://www.latimes.com/entertainment-arts/business",
        "https://www.latimes.com/topic/arts",
        "https://www.latimes.com/entertainment-arts/books",
        "https://www.latimes.com/topic/theater",
        "https://www.latimes.com/topic/museums",
        "https://www.latimes.com/topic/comedy",
        "https://www.latimes.com/topic/behold",
        "https://www.latimes.com/topic/hero-complex",
        "https://www.latimes.com/business",
        "https://www.latimes.com/business/technology",
        "https://www.latimes.com/business/real-estate",
        "https://www.latimes.com/entertainment-arts/business",
        "https://www.latimes.com/business/autos",
        "https://www.latimes.com/sports",
        "https://www.latimes.com/sports/soccer",
        "https://www.latimes.com/food",
        "https://www.latimes.com/environment",
        "https://www.latimes.com/topic/global-warming",
        "https://www.latimes.com/opinion",
        "https://www.latimes.com/politics"
    ]
    base_url = "https://www.latimes.com/"
    referred_link = ''
    ranked = 0
    edition = []
    captured = []
    home_page = []

    def parse(self, response):
        super().parse(response)

        articles = response.css("h2.promo-title a.link::attr(href)").getall()
        for article_link in articles:
            if response.url == self.start_urls[0] and response.url not in self.home_page:
                self.home_page.append(article_link)

            if self.base_url in article_link and article_link not in self.captured:
                self.captured.append(article_link)
                yield response.follow(article_link, self.parseArticle, meta={'parent': response.url})

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/EN/LosAngelesTimes"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.css("h1.headline::text").get()
        if title is None:
            return
        today = date.today()
        date_raw = response.css("time.published-date::attr(datetime)").get()
        news_url = response.request.url
        content_paragraph = response.xpath('//div[contains(@data-element, "story-body")]//p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            if isinstance(p_content, str) == False or p_content is None:
                continue
            content = content + "\n" + p_content

        if news_url in self.home_page:
            parent_url = self.start_urls[0]

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
            'source': 'LosAngelesTimes',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)
