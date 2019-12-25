import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
load_dotenv()

    
class WebScraper:
    page, soup, headers, stores = None, None, None, None

    def __init__(self, agent, stores):
        self.headers = {"User-Agent": agent}
        self.stores = stores

    # Checks if a given URL actually exists
    def validate_url(self, url):
        try:
            result = requests.get(url)
            return result.status_code
        except any as e:
            return None

    # Sets our webscraper with a specific URL link
    def set_to_url(self, url):
        self.page = requests.get(url, headers=self.headers)
        soup_middleman = BeautifulSoup(self.page.content, "html.parser")
        self.soup = BeautifulSoup(soup_middleman.prettify(), "html.parser")
    
    # Gets and returns the title of the item specified in the current page
    def get_item_name(self):
        retval = self.soup.find(id="productTitle").get_text().strip()
        return retval
    
    # Gets and returns the price of the item specified in the current page
    def get_item_price(self):
        retval = self.soup.find(id='priceblock_dealprice')
        if not retval:
            retval = self.soup.find(id='priceblock_ourprice')
        retval = retval.get_text().strip()
        retval = retval[1:7]
        return retval

    # Converts a given string price to integer
    def price_as_num(self, string):
        return float(string)
        
    # Gets the name of the store from a url
    def get_store_name(self, url):
        store_name = [store for store in self.stores if store in url]
        if len(store_name) == 0:
            return None
        return store_name[0]

# div = 'price-group'
# url = 'https://www.walmart.com/ip/Nerf-Rival-Phantom-Corps-Helios-XVIII-700-Blaster-with-7-Rival-Rounds/185600999'
# scraper = WebScraper(os.environ.get("USER_AGENT"), ['walmart'])
# scraper.set_to_url(url)
# print(scraper.get_item_price)