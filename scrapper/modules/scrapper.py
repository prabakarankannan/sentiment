import logging
from scrapper.modules.get_href import get_href_links
from scrapper.modules.get_article import WebScraper
from scrapper.modules.get_tweet import ProcessTweet

from scrapper.models import TargetURL
from scrapper.modules.db_loader import save_article
from scrapper.modules.helpers import extract_domain_without_www, get_target_urls, get_target_keywords, get_project_details, save_file
from scrapper.modules.selenium_scrapper import SeleniumPageSourceScraper
from tqdm import tqdm
import multiprocessing
from multiprocessing import Pool


logging.basicConfig(level=logging.INFO)


def worker(target_url, article_obj):
    try:
        selenium_obj = SeleniumPageSourceScraper(url=target_url['url'], selector=target_url['selector'])
        all_href = selenium_obj.extract()

        for each_href in all_href:
            domain = extract_domain_without_www(each_href)

            # check if domain exist in target url
            check = TargetURL.objects.filter(domain=domain)
            if check.exists():
                article = article_obj.get_article(url=each_href)

                if article:
                    try:
                        print("saving article")
                        save_article(article)
                    except Exception as e:
                        logging.error(f'An error has occurred while saving article: {e}')
    except Exception as e:
        logging.error(f'An error has occurred: {e}')



def linear_news_scrape():
    target_urls = get_target_urls()
    target_keywords = get_target_keywords()
    article_obj = WebScraper(target_keywords=target_keywords)

    logging.info(f'target url found: {len(target_urls)}')

    for each in tqdm(target_urls):
        logging.info(f'main url --> {each}')

        worker(target_url=each, article_obj=article_obj)


def parallel_news_scrape():
    target_urls = get_target_urls()
    target_keywords = get_target_keywords()
    article_obj = WebScraper(target_keywords=target_keywords)

    logging.info(f'Target urls found: {len(target_urls)}')

    cpu_core = multiprocessing.cpu_count()
    logging.info(f'CPU cores: {cpu_core}')

    if cpu_core > 2:
        cpu_core = cpu_core - 2

    pool = multiprocessing.Pool(processes=cpu_core)

    # Combine target_urls and article_obj into a single iterable
    work_items = zip(target_urls, [article_obj] * len(target_urls))

    pool.starmap(worker, work_items)

    pool.close()
    pool.join()


def tweet_worker(project_name, keyword, state, process_tweete_obj):
    try:
        selenium_obj = SeleniumPageSourceScraper()
        all_tweets = selenium_obj.scrape_tweeter(keyword=keyword, near=state)
        save_file(data=all_tweets, is_tweet=True, project_name=project_name)
        for each_tweet in all_tweets:
            try:
                tweet = process_tweete_obj.get_tweets(tweet_obj=each_tweet)
                if tweet:
                    save_article(tweet)
            except Exception as e:
                logging.error(f'An error has occurred while saving article: {e}')
    except Exception as e:
        logging.error(f'An error has occurred: {e}')


def linear_tweet_scrape():
    projects = get_project_details()
    for each_project in projects:
        target_keywords = each_project.get("keywords")
        target_states = each_project.get("states")
        project_name = each_project.get("name")

        process_tweete_obj = ProcessTweet(target_keywords=each_project, target_states=target_states)

        for each_keyword in target_keywords:
            for each_state in target_states:
                tweet_worker(project_name=project_name, keyword=each_keyword, state=each_state, process_tweete_obj=process_tweete_obj)


def parallel_tweet_scrape():
    projects = get_project_details()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    for each_project in projects:
        target_keywords = each_project.get("keywords")
        target_states = each_project.get("states")
        project_name = each_project.get("name")

        process_tweete_obj = ProcessTweet(target_keywords=each_project, target_states=target_states)

        for each_keyword in target_keywords:
            for each_state in target_states:
                pool.apply_async(tweet_worker, args=(project_name, each_keyword, each_state, process_tweete_obj))

    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()

