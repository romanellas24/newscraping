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

class Brasil247(BaseScraper):
    name = "Brasil247"
    timezone = "America/Sao_Paulo"

    start_urls = [
        "https://www.brasil247.com/",
        'https://www.brasil247.com/equipe/brasil247', 'https://www.brasil247.com/info/faq',
        'https://www.brasil247.com/info/politica-de-privacidade', 'https://www.brasil247.com/compliance',
        'https://www.brasil247.com/editoriais247',
        'https://www.brasil247.com/poder', 'https://www.brasil247.com/brasil', 'https://www.brasil247.com/mundo',
        'https://www.brasil247.com/economia', 'https://www.brasil247.com/midia', 'https://www.brasil247.com/cultura',
        'https://www.brasil247.com/empreender', 'https://www.brasil247.com/reindustrializacao',
        'https://www.brasil247.com/saude', 'https://www.brasil247.com/esporte',
        'https://www.brasil247.com/americalatina', 'https://www.brasil247.com/meioambiente',
        'https://www.brasil247.com/agro',
        'https://www.brasil247.com/geral', 'https://www.brasil247.com/entrevistas',
        'https://www.brasil247.com/chargista', 'https://www.brasil247.com/tanostrends',
        'https://www.brasil247.com/ideias',
        'https://www.brasil247.com/tag/enchentes', 'https://www.brasil247.com/tag/lula',
        'https://www.brasil247.com/tag/bolsonaro', 'https://www.brasil247.com/tag/alexandre-de-moraes',
        'https://www.brasil247.com/tag/israel', 'https://www.brasil247.com/tag/russia',
        'https://www.brasil247.com/tag/argentina',
        'https://www.brasil247.com/tabela-brasileirao-ligas-e-campeonatos',
        'https://www.brasil247.com/regionais/brasilia', 'https://www.brasil247.com/regionais/nordeste',
        'https://www.brasil247.com/regionais/sudeste',
        'https://www.brasil247.com/regionais/sul', 'https://www.brasil247.com/ultimas-noticias',
        'https://www.brasil247.com/colunistas', 'https://www.brasil247.com/editoriais247',
        'https://www.brasil247.com/equipe/brasil247',
        'https://www.brasil247.com/equipe/produtos-247', 'https://www.brasil247.com/editoriais247',
        'https://www.brasil247.com/games', 'https://www.brasil247.com/sites',
        'https://www.brasil247.com/sites/apostas', 'https://www.brasil247.com/sites/cassino',
        'https://www.brasil247.com/games', 'https://www.brasil247.com/colunistas',
        'https://www.brasil247.com/editoriais247', 'https://www.brasil247.com/saude',
        'https://www.brasil247.com/esporte',
        'https://www.brasil247.com/americalatina', 'https://www.brasil247.com/meioambiente',
        'https://www.brasil247.com/agro',
        'https://www.brasil247.com/geral', 'https://www.brasil247.com/equipe/produtos-247',
        'https://www.brasil247.com/entrevistas', 'https://www.brasil247.com/chargista',
        'https://www.brasil247.com/tanostrends', 'https://www.brasil247.com/ideias',
        'https://www.brasil247.com/revista', 'https://www.brasil247.com/tag/enchentes',
        'https://www.brasil247.com/tag/lula', 'https://www.brasil247.com/tag/alexandre-de-moraes',
        'https://www.brasil247.com/tag/bolsonaro', 'https://www.brasil247.com/tag/israel',
        'https://www.brasil247.com/tag/russia', 'https://www.brasil247.com/tag/argentina',
        'https://www.brasil247.com/regionais/nordeste', 'https://www.brasil247.com/regionais/sul',
        'https://www.brasil247.com/regionais/sudeste',
        'https://www.brasil247.com/poder', 'https://www.brasil247.com/brasil', 'https://www.brasil247.com/mundo',
        'https://www.brasil247.com/economia', 'https://www.brasil247.com/midia',
        'https://www.brasil247.com/cultura', 'https://www.brasil247.com/empreender',
        'https://www.brasil247.com/reindustrializacao', 'https://www.brasil247.com/ultimas-noticias',
    ]

    referred_link = ''
    ranked = 0
    edition = []
    captured = []
    home_page = []
    base_url = "www.brasil247.com"
    base_http = "https://www.brasil247.com"

    def parse(self, response):
        super().parse(response)
        article_links = response.xpath("//a[@data-tb-link='true']/@href").getall()
        article_links_2 = response.xpath("//a[@data-tb-link='false']/@href").getall()
        article_links.extend(article_links_2)
        for article in article_links:
            if article not in self.captured and "https://" not in article and article not in self.start_urls:
                self.captured.append(article)
                article = f"{self.base_http}{article}"
                if self.start_urls[0] == response.url:
                    self.home_page.append(article)
                yield response.follow(article, self.parseArticle, meta={'parent': response.url})

    def close(spider: Spider, reason: str) -> Union[Deferred, None]:
        if reason == 'finished':
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
            base_name = f"{now_s}E{now_epoch}.json"
            for new in spider.edition:
                new['date'] = str(new['date'])
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/PT/Brasil247"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "w") as f:
                json.dump(spider.edition, f, indent=4, ensure_ascii=False)
                f.write("\n")
        return spider.close(spider, reason)

    def parseArticle(self, response):
        parent_url = response.meta['parent']
        title = response.css("h1.article__headline::text").get()
        today = date.today()
        date_raw = response.xpath("//time[@class = 'article__time']/@datetime").get()
        if isinstance(date_raw, str) == False:
            pass
        news_url = response.request.url
        content_paragraph = response.xpath('//div[@data-cy="articleBody"]/p')
        content = ''
        self.ranked = self.ranked + 1
        timestamp = time.time()
        subtitle = response.css('p.article__lead::text').get()

        for p in content_paragraph:
            p_content = p.xpath('./text()').get()
            if p_content != None:
                content = content + p_content + "\n"

        if news_url in self.home_page:
            parent_url = self.start_urls[0]

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
            'language': 'PT',
            'source': 'Brasil247',
            'local_time': self.calculate_local_time(),
            'timezone': self.timezone,
            'scraping_time': datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
        }
        self.edition.append(new)
