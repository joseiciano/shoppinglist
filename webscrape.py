import requests
from bs4 import BeautifulSoup

class WebScraper:
    page, soup, headers = None, None, None

    def __init__(self):
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}

    # Sets our webscraper with a specific URL link
    def setDataFromURL(self, URL):
        self.page = requests.get(URL, headers=self.headers)
        soup1 = BeautifulSoup(self.page.content, 'html.parser')
        self.soup = BeautifulSoup(soup1.prettify(), "html.parser")

    # Gets and returns the title of the item specified in the current page
    def getTitle(self, divID):
        return self.soup.find(id=divID).get_text().strip()

    # Gets and returns the price of the item specified in the current page
    def getPrice(self, divID):
        return self.soup.find(id=divID).get_text().strip()

    # Gets and returns (as a float) the price of the item specified
    def getPriceAsNum(self, divID):
        price = self.getPrice(divID)
        return float(price[1:7])

