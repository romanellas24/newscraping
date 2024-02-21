import scrapy
class QuoteSpider(scrapy.Spider):
    name = "RioTimes"
    start_urls = [
        "https://www.riotimesonline.com/latest-news/",
    ]

    def parse(self, response):
        for news in response.xpath("//a[@rel='bookmark' and not(contains(@class, 'td-image-wrap '))]"):
            yield {
                "link": news.xpath("./@href").get(),
                "title": news.xpath("./@title").get(),
            }
        """
        next_page = response.css('li.next a::attr("href")').get()
        if(next_page is not None):
            yield response.follow(next_page, self.parse)
            """
