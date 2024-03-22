source /home/romanellas/venv/bin/activate &&
cd /mediam/mc/Thesis/Newscraping/scrapyGetters/scrapyGetters/spiders &&
git pull &&
bash dailyscrape.sh &&
bash flowscrape.sh &&
deactivate
