#!/bash/sh
PATH=$PATH:/home/joseph/.local/bin
export PATH
scrapy crawl teleGet # Ok
scrapy crawl postScrape # Ok
scrapy crawl dwGet # Ok
scrapy crawl abcGet
scrapy crawl cnnGet
scrapy crawl fr24rssGet
scrapy crawl agiGet
scrapy crawl ansaGet
cd ../../..
git add .
git commit -m "checkout"
git push origin main
