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


class RioTimes(BaseScraper):
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
        'https://www.news.com.au/national/nsw-act/politics', 'https://www.news.com.au/national/nsw-act/crime',
        'https://www.news.com.au/national/nsw-act/courts-law',
        'https://www.news.com.au/national/queensland/politics', 'https://www.news.com.au/national/queensland/crime',
        'https://www.news.com.au/national/queensland/courts-law',
        'https://www.news.com.au/national/victoria/politics', 'https://www.news.com.au/national/victoria/crime',
        'https://www.news.com.au/national/victoria/courts-law',
        'https://www.news.com.au/world/north-america/us-politics', 'https://www.news.com.au/world/europe/uk-politics',
        'https://www.news.com.au/world/coronavirus/australia',
        'https://www.news.com.au/world/coronavirus/global', 'https://www.news.com.au/world/coronavirus/economy',
        'https://www.news.com.au/world/coronavirus/health',
        'https://www.news.com.au/world/coronavirus/closures',
        'https://www.news.com.au/lifestyle/health/health-problems',
        'https://www.news.com.au/lifestyle/health/mental-health',
        'https://www.news.com.au/lifestyle/health/wellbeing', 'https://www.news.com.au/lifestyle/health/diet',
        'https://www.news.com.au/lifestyle/fitness/inspiration',
        'https://www.news.com.au/lifestyle/fitness/weight-loss', 'https://www.news.com.au/lifestyle/fitness/exercise',
        'https://www.news.com.au/lifestyle/parenting/pregnancy',
        'https://www.news.com.au/lifestyle/parenting/babies', 'https://www.news.com.au/lifestyle/parenting/kids',
        'https://www.news.com.au/lifestyle/parenting/teens',
        'https://www.news.com.au/lifestyle/parenting/school-life', 'https://www.news.com.au/lifestyle/food/eat',
        'https://www.news.com.au/lifestyle/food/drink',
        'https://www.news.com.au/lifestyle/food/restaurants-bars',
        'https://www.news.com.au/lifestyle/food/food-warnings',
        'https://www.news.com.au/lifestyle/relationships/dating',
        'https://www.news.com.au/lifestyle/relationships/sex',
        'https://www.news.com.au/lifestyle/relationships/the-sealed-section',
        'https://www.news.com.au/lifestyle/relationships/marriage',
        'https://www.news.com.au/lifestyle/relationships/family-friends',
        'https://www.news.com.au/lifestyle/fashion/fashion-shows',
        'https://www.news.com.au/lifestyle/fashion/designers',
        'https://www.news.com.au/lifestyle/fashion/fashion-trends',
        'https://www.news.com.au/lifestyle/fashion/celebrity', 'https://www.news.com.au/lifestyle/beauty/face-body',
        'https://www.news.com.au/lifestyle/beauty/cosmetic-surgery',
        'https://www.news.com.au/lifestyle/home/interiors', 'https://www.news.com.au/lifestyle/home/outdoors',
        'https://www.news.com.au/lifestyle/home/diy', 'https://www.news.com.au/lifestyle/home/pets',
        'https://www.news.com.au/lifestyle/real-life/true-stories',
        'https://www.news.com.au/lifestyle/real-life/good-news',
        'https://www.news.com.au/lifestyle/real-life/news-life',
        'https://www.news.com.au/travel/travel-ideas/cruises', 'https://www.news.com.au/travel/travel-ideas/luxury',
        'https://www.news.com.au/travel/travel-ideas/adventure',
        'https://www.news.com.au/travel/travel-ideas/short-breaks',
        'https://www.news.com.au/travel/travel-ideas/ski-snow',
        'https://www.news.com.au/travel/travel-ideas/road-trips',
        'https://www.news.com.au/travel/travel-ideas/food-drink', 'https://www.news.com.au/travel/destinations/pacific',
        'https://www.news.com.au/travel/destinations/asia',
        'https://www.news.com.au/travel/destinations/north-america',
        'https://www.news.com.au/travel/destinations/europe', 'https://www.news.com.au/travel/destinations/new-zealand',
        'https://www.news.com.au/travel/destinations/africa', 'https://www.news.com.au/travel/destinations/middle-east',
        'https://www.news.com.au/travel/destinations/central-america',
        'https://www.news.com.au/travel/destinations/south-america',
        'https://www.news.com.au/travel/travel-advice/tips-tricks',
        'https://www.news.com.au/travel/travel-advice/flights',
        'https://www.news.com.au/travel/travel-advice/accommodation',
        'https://www.news.com.au/travel/travel-advice/money', 'https://www.news.com.au/travel/travel-advice/airports',
        'https://www.news.com.au/travel/australian-holidays/nsw-act',
        'https://www.news.com.au/travel/australian-holidays/northern-territory',
        'https://www.news.com.au/travel/australian-holidays/queensland',
        'https://www.news.com.au/travel/australian-holidays/south-australia',
        'https://www.news.com.au/travel/australian-holidays/tasmania',
        'https://www.news.com.au/travel/australian-holidays/victoria',
        'https://www.news.com.au/travel/australian-holidays/western-australia',
        'https://www.news.com.au/entertainment/celebrity-life/hook-ups-break-ups',
        'https://www.news.com.au/entertainment/celebrity-life/celebrity-photos',
        'https://www.news.com.au/entertainment/celebrity-life/celebrity-kids',
        'https://www.news.com.au/entertainment/celebrity-life/celebrity-deaths',
        'https://www.news.com.au/entertainment/celebrity-life/royals',
        'https://www.news.com.au/entertainment/celebrity-style/red-carpet',
        'https://www.news.com.au/entertainment/tv/tv-shows', 'https://www.news.com.au/entertainment/tv/reality-tv',
        'https://www.news.com.au/entertainment/tv/streaming', 'https://www.news.com.au/entertainment/tv/radio',
        'https://www.news.com.au/entertainment/tv/morning-shows',
        'https://www.news.com.au/entertainment/tv/current-affairs',
        'https://www.news.com.au/entertainment/tv/flashback',
        'https://www.news.com.au/entertainment/movies/upcoming-movies',
        'https://www.news.com.au/entertainment/movies/new-movies',
        'https://www.news.com.au/entertainment/movies/movie-reviews',
        'https://www.news.com.au/entertainment/music/music-festivals',
        'https://www.news.com.au/entertainment/music/tours',
        'https://www.news.com.au/entertainment/books-magazines/books',
        'https://www.news.com.au/entertainment/books-magazines/magazines',
        'https://www.news.com.au/entertainment/awards/oscars',
        'https://www.news.com.au/entertainment/awards/golden-globes',
        'https://www.news.com.au/entertainment/awards/grammys', 'https://www.news.com.au/entertainment/awards/arias',
        'https://www.news.com.au/entertainment/awards/logies', 'https://www.news.com.au/entertainment/awards/emmys',
        'https://www.news.com.au/technology/online/social',
        'https://www.news.com.au/technology/online/security', 'https://www.news.com.au/technology/online/internet',
        'https://www.news.com.au/technology/online/hacking',
        'https://www.news.com.au/technology/gadgets/mobile-phones',
        'https://www.news.com.au/technology/gadgets/tablets', 'https://www.news.com.au/technology/gadgets/cameras',
        'https://www.news.com.au/technology/gadgets/wearables',
        'https://www.news.com.au/technology/home-entertainment/tv',
        'https://www.news.com.au/technology/home-entertainment/computers',
        'https://www.news.com.au/technology/home-entertainment/audio',
        'https://www.news.com.au/technology/science/space', 'https://www.news.com.au/technology/science/archaeology',
        'https://www.news.com.au/technology/science/human-body',
        'https://www.news.com.au/technology/science/animals',
        'https://www.news.com.au/technology/environment/climate-change',
        'https://www.news.com.au/technology/environment/sustainability',
        'https://www.news.com.au/technology/environment/natural-wonders',
        'https://www.news.com.au/technology/innovation/inventions',
        'https://www.news.com.au/technology/innovation/design',
        'https://www.news.com.au/technology/motoring/motoring-news',
        'https://www.news.com.au/technology/motoring/new-cars', 'https://www.news.com.au/technology/motoring/luxury',
        'https://www.news.com.au/technology/motoring/hitech',
        'https://www.news.com.au/technology/motoring/car-advice',
        'https://www.news.com.au/technology/motoring/on-the-road', 'https://www.news.com.au/finance/work/at-work',
        'https://www.news.com.au/finance/work/careers', 'https://www.news.com.au/finance/work/leaders',
        'https://www.news.com.au/finance/business/breaking-news',
        'https://www.news.com.au/finance/business/technology', 'https://www.news.com.au/finance/business/banking',
        'https://www.news.com.au/finance/business/travel',
        'https://www.news.com.au/finance/business/retail', 'https://www.news.com.au/finance/business/manufacturing',
        'https://www.news.com.au/finance/business/media',
        'https://www.news.com.au/finance/business/other-industries', 'https://www.news.com.au/finance/money/costs',
        'https://www.news.com.au/finance/money/investing',
        'https://www.news.com.au/finance/money/budgeting', 'https://www.news.com.au/finance/money/wealth',
        'https://www.news.com.au/finance/money/tax',
        'https://www.news.com.au/finance/economy/australian-economy',
        'https://www.news.com.au/finance/economy/world-economy',
        'https://www.news.com.au/finance/economy/interest-rates',
        'https://www.news.com.au/finance/economy/federal-budget', 'https://www.news.com.au/finance/real-estate/selling',
        'https://www.news.com.au/finance/real-estate/buying',
        'https://www.news.com.au/finance/real-estate/renting', 'https://www.news.com.au/finance/real-estate/sydney-nsw',
        'https://www.news.com.au/finance/real-estate/melbourne-vic',
        'https://www.news.com.au/finance/real-estate/adelaide-sa',
        'https://www.news.com.au/finance/real-estate/perth-wa',
        'https://www.news.com.au/finance/markets/australian-markets',
        'https://www.news.com.au/finance/markets/world-markets',
        'https://www.news.com.au/finance/markets/australian-dollar',
        'https://www.news.com.au/topics/cricket-live-scores',
        'https://www.news.com.au/sport/motorsport/formula-one', 'https://www.news.com.au/sport/motorsport/v8-supercars',
        'https://www.news.com.au/sport/motorsport/moto-gp',
        'https://www.news.com.au/sport/sports-life/champions', 'https://www.news.com.au/sport/sports-life/history',
        'https://www.news.com.au/sport/nfl', 'https://www.news.com.au/sport/football/a-league',
        'https://www.news.com.au/sport/football/epl', 'https://www.news.com.au/sport/basketball/nba',
        'https://www.news.com.au/sport/rugby/wallabies', 'https://www.news.com.au/sport/superracing/expert-opinion',
        'https://www.news.com.au/sport/superracing/tips', 'https://www.news.com.au/sport/superracing/nsw-racing',
        'https://www.news.com.au/sport/superracing/vic-racing',
        'https://www.news.com.au/sport/superracing/sa-racing', 'https://www.news.com.au/sport/superracing/qld-racing',
        'https://www.news.com.au/sport/superracing/wa-racing',
        'https://www.news.com.au/sport/superracing/punters-life'
    ]
    referred_link = ''
    ranked = 0
    edition = []
    captured = []

    def parse(self, response):
        super().parse(response)
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
