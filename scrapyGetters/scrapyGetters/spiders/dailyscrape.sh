#!/bash/sh
PATH=$PATH:PATH=$PATH:/home/romanellas/venv/bin
export PATH

# Edition scrapers
scrapy crawl zdfGet
scrapy crawl rtsURLGet
scrapy crawl rtsGet
scrapy crawl pbsGet
scrapy crawl frGet
scrapy crawl 20Get

# scrapy crawl gr1url
# scrapy crawl gr1Get
cd ../../..
git pull
git add .
git commit -m "daily_scrape"
git push origin main
