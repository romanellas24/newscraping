from os import path
from typing import Union

from datetime import date, datetime, timedelta
import time
import dateparser
from scrapy import Spider
from twisted.internet.defer import Deferred
import json

from .BaseScraper import BaseScraper

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"


class NewsComAu(BaseScraper):
    name = "NewsComAu"
    timezone = "Australia/Canberra"

    start_urls = [
        "https://www.news.com.au/",
        'https://www.news.com.au/national/breaking-news', 'https://www.news.com.au/national/politics',
        'https://www.news.com.au/national/crime', 'https://www.news.com.au/national/courts-law',
        'https://www.news.com.au/national/nsw-act', 'https://www.news.com.au/national/queensland',
        'https://www.news.com.au/national/victoria', 'https://www.news.com.au/national/south-australia',
        'https://www.news.com.au/national/western-australia', 'https://www.news.com.au/national/northern-territory',
        'https://www.news.com.au/national/tasmania', 'https://www.news.com.au/national/weather',
        'https://www.news.com.au/world/breaking-news', 'https://www.news.com.au/world/pacific',
        'https://www.news.com.au/world/asia', 'https://www.news.com.au/world/north-america',
        'https://www.news.com.au/world/south-america',
        'https://www.news.com.au/world/africa', 'https://www.news.com.au/world/middle-east',
        'https://www.news.com.au/world/europe', 'https://www.news.com.au/world/coronavirus',
        'https://www.news.com.au/lifestyle/health',
        'https://www.news.com.au/lifestyle/fitness', 'https://www.news.com.au/lifestyle/parenting',
        'https://www.news.com.au/lifestyle/food', 'https://www.news.com.au/lifestyle/relationships',
        'https://www.news.com.au/lifestyle/fashion', 'https://www.news.com.au/lifestyle/beauty',
        'https://www.news.com.au/lifestyle/home', 'https://www.news.com.au/lifestyle/real-life',
        'https://www.news.com.au/lifestyle/video',
        'https://www.news.com.au/lifestyle/horoscopes', 'https://www.news.com.au/travel/travel-ideas',
        'https://www.news.com.au/travel/destinations', 'https://www.news.com.au/travel/travel-advice',
        'https://www.news.com.au/travel/australian-holidays', 'https://www.news.com.au/travel/video',
        'https://www.news.com.au/entertainment/celebrity-life',
        'https://www.news.com.au/entertainment/celebrity-style', 'https://www.news.com.au/entertainment/tv',
        'https://www.news.com.au/entertainment/movies', 'https://www.news.com.au/entertainment/music',
        'https://www.news.com.au/entertainment/books-magazines', 'https://www.news.com.au/entertainment/awards',
        'https://www.news.com.au/entertainment/video', 'https://www.news.com.au/technology/online',
        'https://www.news.com.au/technology/gadgets', 'https://www.news.com.au/technology/home-entertainment',
        'https://www.news.com.au/technology/gaming', 'https://www.news.com.au/technology/science',
        'https://www.news.com.au/technology/environment', 'https://www.news.com.au/technology/innovation',
        'https://www.news.com.au/technology/motoring', 'https://www.news.com.au/technology/video',
        'https://www.news.com.au/finance/work', 'https://www.news.com.au/finance/business',
        'https://www.news.com.au/finance/money', 'https://www.news.com.au/finance/economy',
        'https://www.news.com.au/finance/real-estate',
        'https://www.news.com.au/finance/markets', 'https://www.news.com.au/finance/superannuation',
        'https://www.news.com.au/sport/afl', 'https://www.news.com.au/sport/nrl',
        'https://www.news.com.au/sport/cricket', 'https://www.news.com.au/sport/tennis',
        'https://www.news.com.au/sport/motorsport', 'https://www.news.com.au/sport/sports-life',
        'https://www.news.com.au/sport/american-sports', 'https://www.news.com.au/sport/olympics',
        'https://www.news.com.au/sport/football',
        'https://www.news.com.au/sport/boxing', 'https://www.news.com.au/sport/ufc',
        'https://www.news.com.au/sport/golf', 'https://www.news.com.au/sport/basketball',
        'https://www.news.com.au/sport/rugby', 'https://www.news.com.au/sport/superracing',
        'https://www.news.com.au/sport/cycling', 'https://www.news.com.au/sport/more-sports',
        'https://www.news.com.au/sport/video', 'https://www.news.com.au/checkout/sales-and-deals',
        'https://www.news.com.au/checkout/tech',
        'https://www.news.com.au/checkout/fashion-and-accessories', 'https://www.news.com.au/checkout/beauty',
        'https://www.news.com.au/checkout/home-and-garden', 'https://www.news.com.au/checkout/life',
        'https://www.news.com.au/checkout/health-and-wellbeing', 'https://www.news.com.au/coupons',
    ]
    referred_link = ''
    ranked = 0
    edition = []
    captured = []

    def parse(self, response):
        super().parse(response)
        a = response.css("h3.navigation_title::text").getall()
        article_links = response.css("a.storyblock_title_link::attr(href)").getall()
        for article in article_links:
            if article not in self.captured and "www.news.com.au" in article:
                self.captured.append(article)
                yield response.follow(article, self.parseArticle, meta={'parent': response.url})

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/EN/NewsComAu"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.css("#story-headline::text").get()
        today = date.today()
        date_raw = response.css("#publish-date::text").get()
        if isinstance(date_raw, str) == False:
            pass
        date_parsed = dateparser.parse(date_raw)
        if date_parsed.date() != today:
            pass
        news_url = response.request.url
        content_paragraph = response.css('#story-primary p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()
        subtitle = response.css('#story-intro::text').get()

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            if p_content != None:
                content = content + p_content + "\n"

        new = {
            'title': title,
            'date_raw': date_raw,  # Directly from the document
            'date': today,
            'url': parent_url,
            'news_url': news_url,
            'subtitle': subtitle,
            'content': content,
            'ranked': self.ranked,
            'placed': 'Abroad',
            'epoch': timestamp,
            'language': 'EN',
            'source': 'NewsComAu',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)
