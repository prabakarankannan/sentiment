from scrapper.modules.scrapper import parallel_news_scrape, parallel_tweet_scrape
from scrapper.modules.helpers import resync_keyword, resync_people
import time
import json
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def scrape_article():
    parallel_news_scrape()


def scrape_twitter(username: str, passwd: str, keyword: str) -> str:
    # parallel_tweet_scrape()

    def twitter_login(username: str, passwd: str, keyword: str) -> str:
        driver = selenium.webdriver.Firefox()

        url = f"https://twitter.com/search?q={keyword}&src=recent_search_click&f=live"
        driver.get(url)

        input_username = WebDriverWait(driver, 15).until(ec.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
        input_username.send_keys(username)
        input_username.send_keys(selenium.webdriver.Keys.ENTER)

        input_passwd = WebDriverWait(driver, 15).until(ec.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
        input_passwd.send_keys(passwd)
        input_passwd.send_keys(selenium.webdriver.Keys.ENTER)

        time.sleep(5)

        try:
            res = tweet_scrape(driver)
        except Exception as e:
            print(e)

        driver.quit()
        
        return json.dumps(res)

    def tweet_scrape(driver: selenium.webdriver.firefox) -> str:
        tweet_data = dict()
        index = 0

        utils = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
        while True:
            for _ in utils:       
                tweet = driver.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                tweet_data[f"tweet{index}"] = tweet
                index += 1

            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(3)

            utils = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            if len(tweet_data) > 5:
                break      
        
        return json.dumps(tweet_data)
    
    twitter_login()


def keyword_resync():
    resync_keyword()


def people_resync():
    resync_people()