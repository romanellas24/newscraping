#!/bash/sh
PATH=$PATH:/home/students/giuseppe.carrino2/.local/bin
export PATH
scrapy crawl zdfGet # OK
scrapy crawl rtsURLGet # OK
scrapy crawl rtsGet # OK
scrapy crawl pbsGet # OK
scrapy crawl frGet # OK
scrapy crawl 20Get
# scrapy crawl gr1url
# scrapy crawl gr1Get
cd ../../..
git add .
git commit -m "daily_checkout"
git push origin main
