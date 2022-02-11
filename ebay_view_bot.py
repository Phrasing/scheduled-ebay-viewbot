import requests
from bs4 import BeautifulSoup
import re
import time
import numpy as np
import logging
import threading
import time

VIEWS_TO_ADD = 5
VIEW_COOLDOWN = 60 * 10

def scrape_html(url):
    try:
        r = requests.get(url)
    except:
        return scrape_html(url)
    return r.text

def add_views(item_url):
    for i in range(VIEWS_TO_ADD):
        try:
            r=requests.get(item_url)
        except:
            continue
    logging.info("Done adding views to %s", item_url)

def find_all_listings(document):
    links=[]
    soup = BeautifulSoup(document,'html.parser')
    for link in soup.find_all('a', attrs={'href':re.compile("^https://")}):
        l = link.get('href').split('?', 1)[0]
        if "itm" in l:
           links.append(link.get('href').split('?', 1)[0])
    return np.array(list(dict.fromkeys(links)))

def viewbot_all_listings(ebay_user_catalog):
    document = scrape_html(ebay_user_catalog)
    links = find_all_listings(document)
    for link in links:
        logging.info("Viewing %s", link)
        add_views(link)

def scheduled_viewbot(ebay_user_catalog):
    while True:
        logging.info("Adding views to active listings")
        viewbot_all_listings(ebay_user_catalog)
        time.sleep(VIEW_COOLDOWN)

def check_for_new_listings(original_links, ebay_user_catalog):
    document = scrape_html(ebay_user_catalog)
    links = find_all_listings(document)
    if not np.array_equal(links, original_links):
       return links
    else:
       return np.array([])

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    username = input('Enter eBay Username: ')
    ebay_user_catalog = "https://www.ebay.com/sch/" + username + "/m.html?_nkw=&_armrs=1&_from=&_ipg=1000&rt=nc&_dmd=2"

    document = scrape_html(ebay_user_catalog)
    original_links = find_all_listings(document)
    t = threading.Thread(target=scheduled_viewbot, args=(ebay_user_catalog,))
    t.start()
    while True:
        result=check_for_new_listings(original_links, ebay_user_catalog)
        if result.size > 0:
           diff=np.setdiff1d(result, original_links)
           if diff.size > 0:
              for link in diff:
                 logging.info("Adding views to new listing %s", link)
                 add_views(link)
              original_links = result
        time.sleep(1)
        logging.info("Checking for new listings")
    t.detach()