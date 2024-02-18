import requests
from bs4 import BeautifulSoup
from scrapper.modules.selenium_scrapper import SeleniumPageSourceScraper


def get_href_links(url, selector=None):
    try:
        # Define a user-agent header to mimic a web browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # Send an HTTP GET request with headers to the URL
        # response = requests.get(url, headers=headers)

        # Check if the request was successful
        # if response.status_code != 200:
        #     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        #     return []

        scrapper_obj = SeleniumPageSourceScraper(url=url, selector=selector)
        response = scrapper_obj.extract()

        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response, 'html.parser')

        # If an element_path is provided, select that element
        if selector:
            selected_element = soup.select_one(selector)
            if selected_element:
                # Find all href links within the selected element
                href_links = [a['href'] for a in selected_element.find_all('a', href=True) if 'http' in a['href']]
            else:
                print(f"Element not found with the provided element_path: {selector}")
                return []
        else:
            # If no element_path is provided, search for href links in the whole body
            href_links = [a['href'] for a in soup.find_all('a', href=True)]

        return href_links

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []