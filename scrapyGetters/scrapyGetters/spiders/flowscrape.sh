#!/bash/sh
PATH=$PATH:/home/joseph/.local/bin
export PATH
scrapy crawl teleGet # Ok
scrapy crawl postScrape # Ok
scrapy crawl dwGet # Ok
scrapy crawl abcGet # OK
scrapy crawl cnnGet # OK
scrapy crawl fr24rssGet # OK
scrapy crawl agiGet # OK
scrapy crawl ansaGet
cd ../../..
git add .
git commit -m "checkout"
git push origin main
