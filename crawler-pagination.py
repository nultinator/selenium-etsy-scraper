import os
import csv
import json
import logging
from urllib.parse import urlencode
import concurrent.futures
from selenium import webdriver
from time import sleep
from dataclasses import dataclass, field, fields, asdict

API_KEY = ""

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    API_KEY = config["api_key"]


## Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_search_results(keyword, location, page_number, retries=3):
    formatted_keyword = keyword.replace(" ", "+")
    url = f"https://www.etsy.com/search?q={formatted_keyword}&ref=pagination&page={page_number+1}"
    tries = 0
    success = False
    
    while tries <= retries and not success:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        prefs = {
            "profile.managed_default_content_settings.javascript": 2,
            "profile.managed_default_content_settings.stylesheets": 2
            }
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            logger.info(f"Successfully pinged {url}")

            content = driver.page_source
            script_tag_begin_index = content.find('"itemListElement"')
            script_tag_end_index = content.find('"numberOfItems"')

            json_string = "{"+ content[script_tag_begin_index:script_tag_end_index-1] + "}"
            json_data = json.loads(json_string)
            list_elements = json_data["itemListElement"]

            for element in list_elements:
                print(element)

            logger.info(f"Successfully parsed data from: {url}")
            success = True
        
                    
        except Exception as e:
            logger.error(f"An error occurred while processing page {url}: {e}")
            logger.info(f"Retrying request for page: {url}, retries left {retries-tries}")
            tries+=1
        
        finally:
            driver.quit()

    if not success:
        raise Exception(f"Max Retries exceeded: {retries}")




def start_scrape(keyword, pages, location, retries=3):
    for page in range(pages):
        scrape_search_results(keyword, location, page, retries=retries)



if __name__ == "__main__":

    MAX_RETRIES = 3
    MAX_THREADS = 5
    PAGES = 1
    LOCATION = "us"

    logger.info(f"Crawl starting...")

    ## INPUT ---> List of keywords to scrape
    keyword_list = ["coffee mug"]
    aggregate_files = []

    ## Job Processes
    for keyword in keyword_list:
        filename = keyword.replace(" ", "-")

        start_scrape(keyword, PAGES, LOCATION, retries=MAX_RETRIES)
        
    logger.info(f"Crawl complete.")