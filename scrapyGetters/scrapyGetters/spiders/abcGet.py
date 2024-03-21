#!/usr/bin/env python

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector
from datetime import datetime, timedelta
import time
from os import path
import json

SCRIPTS_DIR = path.dirname(__file__)
PROJ_DIR = f"{SCRIPTS_DIR}/../../../"
BASE_URL = f"www.abc.es"
RSS_URL = f"https://{BASE_URL}/rss/feeds/abc_Internacional.xml"

class AbcgetSpider(scrapy.Spider):
    name = 'abcGet'
    allowed_domains = [BASE_URL]
    start_urls = [RSS_URL]

    def dateFormatter(self, dates_raw):
        dates= []
        for raw_date in dates_raw:
            if raw_date == "":
                dates.append(datetime.now().strftime("%Y-%m-%d"))
            else:
                raw_date = raw_date[5:16]
                todate = datetime.strptime(raw_date, "%d %b %Y")
                dates.append(todate.strftime("%Y-%m-%d"))
        return dates

    def parse(self, response):
        articles = response.css("item")

        titles= []
        content= []
        dates_raw= []
        urls= []

        first= True
        for article in articles: 
            if not first:
                titles.append(article.css("title::text").get())
                if article.css("description::text").get():
                    subtitle = article.css("description::text").extract_first()
                    if ">" in subtitle:
                        toDel = subtitle.find(">")
                        subtitle= subtitle[toDel+1:]
                    content.append(subtitle)
                else:
                    content.append("")
                if article.css("pubDate::text").get():
                    dates_raw.append(article.css("pubDate::text").get())
                else:
                    dates_raw.append("")
                urls.append(article.css("link::text").get())
            first= False

        dates= self.dateFormatter(dates_raw)

        edition= []
        i= 0
        for item in zip(titles, dates_raw, dates, urls, content):
            i+=1
            yield scrapy.Request(item[3], callback= self.getFullContent, meta= {'data': item, 'currelem': i, 'edition': edition, 'oldurl': response.request.url})
        
        pass

    def getFullContent(self, response):
        r = response
        fullsubtitle = response.css(".voc-subtitle::text").getall()
        subtitle= ''.join(fullsubtitle)
        fullcontent = r.xpath("//*[@class = 'voc-p']/text()").get()
        content = ''.join(fullcontent)

        item = response.meta.get('data')
        scraped_info = {
                'title': item[0],
                'date_raw': item[1],
                'date': item[2],
                'url': response.meta.get('oldurl'),
                'news_url': item[3],
                'subtitle': subtitle,
                'content': content,
                'ranked': response.meta.get('currelem'),
                'placed': 'Abroad',
                'epoch': time.time(),
                'language': 'ES',
                'source': "ABC"
            }

        response.meta.get('edition').append(scraped_info)

        if response.meta.get('currelem') == len(item):
            now = datetime.now()
            now_s = now.strftime("%Y-%m-%dT%H.%M.%S")
            now_epoch = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)

            base_name = f"{now_s}E{now_epoch}.json"
            scraped_data_dir = f"{PROJ_DIR}/collectedNews/flow/ES/ABC"
            scraped_data_filepath = f"{scraped_data_dir}/{base_name}"
            with open(scraped_data_filepath, "a") as f:
                json.dump(response.meta.get('edition'), f, indent= 4, ensure_ascii=False)
                f.write("\n")