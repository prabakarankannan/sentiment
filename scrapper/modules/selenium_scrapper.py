# import os
# import json
import random
import time
# import re
import threading
# from urllib.parse import urlparse
# from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
from webdriver_manager.firefox import GeckoDriverManager

# import asyncio
# from django.conf import settings
# import requests
from .VirtualDisplayCodeAndTranslate import SmartDisplayWithTranslate
from fake_useragent import UserAgent
import urllib3
from urllib.parse import urlencode

# Initialize a UserAgent object to generate random user agents
ua = UserAgent()


class SeleniumPageSourceScraper:
    def __init__(self, url=None, selector=None):
        self.driver = None
        self.url = url
        self.selector = selector
        self.href_links = []

    def setup_driver(self):
        # patcher = uc.Patcher()
        # patcher.auto()
        choice = random.choice([0,1])

        if choice:
            options = webdriver.ChromeOptions()
        else:
            options = webdriver.FirefoxOptions()

        options.add_argument("--disable-popup-blocking")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--start-maximized")
        options.page_load_strategy = 'eager'
        options.add_experimental_option(
            "prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False}
        )
        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        options.add_argument("--enable-javascript")
        chrome_prefs["profile.default_content_settings"] = {"images": 2}

        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            f'user-agent={random.choice([ua.random for _ in range(10)])}')  # Set the initial user agent

        ### Virtual display
        self.smt_dsp = SmartDisplayWithTranslate()

        urllib3.disable_warnings()  # Disable urllib3 warnings
        connection_pool_maxsize = 10  # Adjust the connection pool size as needed

        # Create a custom connection pool with a larger maxsize
        http = urllib3.PoolManager(num_pools=1, maxsize=connection_pool_maxsize)

        if choice:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

        driver.connection_pool = http

        driver.set_page_load_timeout(20)  # set timeout to 10 seconds
        self.driver = driver
        return driver

    def load_page(self):
        self.driver.get(self.url)
        print("GOT URL")

    def stop_loading(self):
        time.sleep(3)
        self.driver.find_element(By.XPATH, '//body').send_keys(Keys.ESCAPE)
        self.driver.execute_script("window.stop();")
        print("STOP executed")

    def load_more(self):
        try:
            load_more_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Load more')]")
            # If element found, click on it
            load_more_button.click()
            print("Clicked on 'Load more' button.")
        except NoSuchElementException:
            print("'Load more' button not found. Ignoring...")
            pass  # Or add any specific action you want to take if the button is not found

    def enable_infinite_scroll(self):
        try:
            time.sleep(random.randint(5,8))
            open_pref = self.driver.find_element(By.XPATH, "//a[@title='Preferences']")
            open_pref.click()
            time.sleep(random.randint(5,8))
            check_infinite = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Infinite scrolling')]")
            check_infinite.click()
            time.sleep(random.randint(1,3))
            check_infinite = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save preferences')]")
            check_infinite.click()
            time.sleep(random.randint(1,3))
            # If element found, click on it
            print("Infinite Scroll Enabled")
        except NoSuchElementException:
            print("Infinite button not found. Ignoring...")
            pass  # Or add any specific action you want to take if the button is not found

    def scroll_page(self):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        max_scroll = 30
        count = 0
        while True:
            count+=1
            if count == max_scroll:
                break
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(random.randint(2,4))

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            try:
                self.driver.find_element(By.XPATH, "//h2[contains(text(), 'No more')]")
                break
            except Exception as e:
                continue

    def mouse_movements(self):
        # Find a list of elements you want to choose from (e.g., all clickable links)
        elements = self.driver.find_elements(By.TAG_NAME, 'a')

        # Choose a random element from the list
        random_element = random.choice(elements)

        # Create an ActionChains object and move the mouse to the random element
        action = ActionChains(self.driver)
        action.move_to_element(random_element)
        # action.perform()

        # Add a delay to simulate the mouse movement
        time.sleep(random.uniform(1, 2))

    def accept_cookies(self):
        # Use a try-except block to handle the case where the pop-up doesn't exist
        try:
            # Find a button containing the word "Cookie" in its text
            accept_cookies_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Cookie')

            # Click on the button
            accept_cookies_button.click()
        except:
            # If no button with the text "Cookie" is found, or if the pop-up doesn't appear, this code block will be
            # executed.
            print("No 'Accept Cookies' button found or already accepted.")

    def extract_href_links(self):
        try:
            if self.selector:
                selected_element = self.driver.find_element(By.CSS_SELECTOR, self.selector)
                if selected_element:
                    # Find all href links within the selected element using Selenium
                    a_elements = selected_element.find_elements(By.TAG_NAME, 'a')
                    self.href_links = [a.get_attribute('href') for a in a_elements if 'http' in a.get_attribute('href')]
                else:
                    print(f"Element not found with the provided selector: {self.selector}")
            else:
                # If no selector is provided, search for href links in the whole page
                a_elements = self.driver.find_elements(By.TAG_NAME, 'a')
                self.href_links = [a.get_attribute('href') for a in a_elements if 'http' in a.get_attribute('href')]
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def extract(self):
        try:
            self.setup_driver()
            threading.Thread(target=self.load_page).start()
            threading.Thread(target=self.stop_loading).start()
            self.scroll_page()
            if random.choice([True, False]):
                self.mouse_movements()

            self.extract_href_links()  # Extract href links

            self.driver.delete_all_cookies()
            self.driver.close()
            self.driver.quit()

            try:
                self.smt_dsp.stopSmartDisplay()
            except:
                pass

            return self.href_links
        except Exception as e:
            print(e)
            try:
                self.smt_dsp.stopSmartDisplay()
            except:
                pass

    def scrape_tweeter(self, since=None, until=None, near=None, keyword=None):
        try:
            # https://nitter.net/search?f=tweets&q=modi&since=2023-11-13&until=2023-11-14&near=rajasthan
            base_url = "https://nitter.net/search"
            params = {
                "f": "tweets"
            }

            if since and until:
                params['since'] = since
                params['until'] = until
            else:
                # Get today's date
                today_date = datetime.now().strftime("%Y-%m-%d")

                # Get yesterday's date
                yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                params['since'] = yesterday_date
                params['until'] = today_date

            if near:
                params['near'] = near

            if keyword:
                params['q'] = keyword

            # Encode the parameters into a URL query string
            encoded_params = urlencode(params)

            # Construct the final URL by combining the base URL and the encoded parameters
            final_url = f"{base_url}?{encoded_params}"
            self.url = final_url

            self.setup_driver()
            self.load_page()
            self.enable_infinite_scroll()
            self.scroll_page()
            # Find all elements with class="timeline-item"
            timeline_items = self.driver.find_elements(By.XPATH, '//div[@class="timeline-item "]')

            # Define a list to store dictionaries
            data_list = []

            # Iterate through each timeline item and extract information
            for item in timeline_items:
                tweet_dict = {}

                try:
                    tweet_dict['author'] = item.find_element(By.XPATH,
                                                             './/div[@class="fullname-and-username"]/a').get_attribute(
                        'title')
                except Exception as e:
                    tweet_dict['author'] = None

                try:
                    tweet_dict['publication'] = item.find_element(By.XPATH,
                                                                  './/div[@class="fullname-and-username"]/a[@class="username"]').get_attribute(
                        'title')
                except Exception as e:
                    tweet_dict['publication'] = None

                try:
                    tweet_dict['date_publish'] = item.find_element(By.XPATH, './/span[@class="tweet-date"]/a').get_attribute(
                        'title')
                except Exception as e:
                    tweet_dict['date_publish'] = None

                try:
                    tweet_dict['source_content'] = item.find_element(By.XPATH,
                                                                     './/div[contains(@class, "tweet-content")]').text
                except Exception as e:
                    tweet_dict['source_content'] = None

                try:
                    tweet_dict['source_url'] = item.find_element(By.XPATH, './/a[@class="tweet-link"]').get_attribute(
                        'href')
                except Exception as e:
                    tweet_dict['source_url'] = None

                try:
                    tweet_dict['keywords'] = [keyword, ]
                except Exception as e:
                    tweet_dict['keywords'] = []

                try:
                    tweet_dict['states'] = near if near else []
                except Exception as e:
                    tweet_dict['states'] = []

                # Append the dictionary to the list
                data_list.append(tweet_dict)

            self.driver.delete_all_cookies()
            self.driver.close()
            self.driver.quit()
            print("scrapped ", len(data_list))

            try:
                self.smt_dsp.stopSmartDisplay()
            except:
                pass

            return data_list
        except Exception as e:
            print(e)

            try:
                self.smt_dsp.stopSmartDisplay()
            except:
                pass

