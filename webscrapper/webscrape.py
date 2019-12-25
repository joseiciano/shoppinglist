import requests
from bs4 import BeautifulSoup
import urllib


class URLCleaner:
    stores = None

    def __init__(self, stores):
        self.stores = stores
    
    def validate_url(self, url):
        try:
            result = urllib.request.urlopen(url)
            return result == 200
        except urllib.request.HTTPError as e:
            return -1
        
    def get_store_name(self, url):
        store_name = [store for store in stores if store in url]
        if len(store_name) == 0:
            return -1
        return store_name[0]

    
class WebScraper:
    page, soup, headers = None, None, None

    def __init__(self, agent):
        self.headers = {"User-Agent": agent}

    # Sets our webscraper with a specific URL link
    def set_to_url(self, url):
        self.page = requests.get(url, headers=self.headers)
        soup_middleman = BeautifulSoup(self.page.content, "html.parser")
        self.soup = BeautifulSoup(soup_middleman.prettify(), "html.parser")
    
    # Gets and returns the title of the item specified in the current page
    def get_item_name(self, div_id):
        return self.soup.find(id=div_id).get_text().strip()
    
    # Gets and returns the price of the item specified in the current page
    def get_item_price(self, divID):
        return self.soup.find(id=divID).get_text().strip()

    # Gets and returns (as a float) the price of the item specified
    def get_item_price_as_num(self, divID):
        price = self.getPrice(divID)
        return float(price[1:7])
