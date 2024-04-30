##!/bash/sh
PATH=$PATH:/home/romanellas/venv/bin
export PATH
scrapy crawl teleGet
scrapy crawl postScrape
scrapy crawl dwGet
scrapy crawl abcGet
scrapy crawl cnnGet
scrapy crawl fr24rssGet
scrapy crawl agiGet
scrapy crawl ansaGet
scrapy crawl RioTimes
scrapy crawl SowetanLive
scrapy crawl ExpressoPt
scrapy crawl NewsComAu
scrapy crawl LosAngelesTimes
cd ../../..
git pull
git add .
git commit -m "flow_scrape"
git push origin main
