##!/bash/sh
#PATH=$PATH:/home/joseph/.local/bin
#export PATH
scrapy crawl teleGet
scrapy crawl postScrape
scrapy crawl dwGet
scrapy crawl abcGet
scrapy crawl cnnGet
scrapy crawl fr24rssGet
scrapy crawl agiGet
scrapy crawl ansaGet
cd ../../..
git pull
git add .
git commit -m "checkout"
git push origin main
