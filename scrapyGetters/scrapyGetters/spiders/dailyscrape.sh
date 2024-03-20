#!/bash/sh
PATH=$PATH:/home/students/giuseppe.carrino2/.local/bin
export PATH
scrapy crawl zdfGet
scrapy crawl rtsURLGet
scrapy crawl rtsGet
scrapy crawl pbsGet
scrapy crawl frGet
scrapy crawl 20Get
# scrapy crawl gr1url
# scrapy crawl gr1Get
cd ../../..
git add .
git commit -m "daily_checkout"
git push origin main
