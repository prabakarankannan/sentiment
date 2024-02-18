from scrapper.modules.scrapper import parallel_news_scrape, parallel_tweet_scrape
from scrapper.modules.helpers import resync_keyword, resync_people


def scrape_article():
    parallel_news_scrape()


def scrape_twitter():
    parallel_tweet_scrape()


def keyword_resync():
    resync_keyword()


def people_resync():
    resync_people()