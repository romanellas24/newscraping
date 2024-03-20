#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime
from datetime import date
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
ARCH_URL = f"https://www.france24.com/en/archives/2024/03/"
MONTH = f"-March-2024"
BASE_URL = f"https://www.france24.com/en"
DOMAIN = "france24.com"


class FrgetSpider(scrapy.Spider):
    name = 'frGet'
    urls= []
    tod= date.today().strftime("%d")
    #for i in range(1, 31):
    urls.append(ARCH_URL + str(tod) + MONTH)
    allowed_domains = [DOMAIN]
    start_urls = urls

    def parse(self, response):
        news= response.css(".o-archive-day__list").css("li")
        titles= []
        urls= []
        raw_dates= []
        dates= []
        rankeds= []
        act_date= datetime.strptime(response.url[45:], "%d-%B-%Y")
        i= 0
        for new in news:
            titles.append(new.xpath("./a/h2/text()").get())
            urls.append("https://www.france24.com" + new.css("a::attr(href)").get())
            raw_dates.append(act_date.strftime("%B %d, %Y"))
            dates.append(act_date.strftime("%Y-%m-%d"))
            rankeds.append(i)
            i+=1
        
        edition= []
        for item in zip(titles, raw_dates, dates, urls, rankeds):
            scraped_info = {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.request.url,
                'news_url': item[3],
                'content': "",
                'ranked': item[4],
                'placed': "First_Page",
                'epoch': time.time(),
                'language': "EN",
                'source': "France24"                
            }
            edition.append(scraped_info)
        
        base_name = f"{str(edition[0]['date'])}.json"
        scraped_data_dir = f"{PROJ_DIR}/collectedNews/edition/EN/France24"
        scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
        with open(scraped_data_filepath, "w") as f:
            json.dump(edition, f, indent= 4, ensure_ascii=False)
            f.write("\n")
        
