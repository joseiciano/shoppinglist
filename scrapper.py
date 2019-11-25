import requests
from bs4 import BeautifulSoup
import datetime
import smtplib
import pymongo
from pymongo import MongoClient


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

    # Gets the title of the item specified in the current page
    def getTitle(self, divID):
        title = self.soup.find(id=divID).get_text()
        return title.strip()

    # Gets the price of the item specified in the current page
    def getPrice(self, divID):
        price = self.soup.find(id=divID).get_text()
        return price

    # Gets the price of the item specified, returns as a float
    def getPriceAsNum(self, divID):
        price = self.getPrice(divID)
        return float(price[1:7])


class PriceChecker:
    cluster, db, collection, scrapper, itemsChanged = None, None, None, None, None

    def __init__(self, mCluster):
        self.cluster = MongoClient(mCluster)
        self.db = self.cluster["itemStorage"]
        self.scrapper = WebScraper()
        self.itemsChanged = list()

    # Set a specific collection within the database
    def setCollection(self, collection):
        self.collection = self.db[collection]

    # Add a new item to our db
    def add(self, URL):
        self.scrapper.setDataFromURL(URL)
        item = {
            "_id": self.collection.count_documents({}) + 1,
            "title": self.scrapper.getTitle("productTitle"),
            "price": [self.scrapper.getPrice("priceblock_dealprice")],
            "priceAsNum": [self.scrapper.getPriceAsNum("priceblock_dealprice")],
            "priceChange": [0],
            "date": [],
            "url": URL
        }

        exists = self.collection.find_one({'url': item["url"]})
        if not exists:
            self.collection.insert_one(item)

            curDate = str(datetime.date.today())
            self.collection.update_one({'url': item['url']}, {
                                       "$push": {"date": curDate}})

            self.sendMail(item)

    # Edit an item in our db
    def update(self, title):
        item = self.collection.find_one({'title': title})
        if not item:
            return

        self.scrapper.setDataFromURL(item["url"])
        curPrice = self.scrapper.getPrice("priceblock_dealprice")

        # Only update when there's a pricechange
        lastPrice = item["price"][-1]
        if (curPrice != lastPrice):
            curPriceAsNum = self.scrapper.getPriceAsNum("priceblock_dealprice")
            curPriceChange = curPriceAsNum - item["priceAsNum"][-1]
            curDate = str(datetime.date.today())

            self.collection.update_one({"title": title}, {
                "$push": {"price": curPrice, "priceAsNum": curPriceAsNum, "date": curDate}
            })

            if (curPrice > lastPrice):
                msg = f"{title} increased in price by ${curPrice - lastPrice}. URL = {item['url']}"
            else:
                msg = f"{title} decreased in price by ${lastPrice - curPrice}. URL = {item['url']}"
            self.itemsChanged.append(msg)
        else:
            print(f"{title} has not changed in price")

    # Check and update all the prices of every item in our DB
    def checkAll(self):
        items = self.collection.find({})

        # Check the price for all items in our db
        for item in items:
            self.update(item["title"])

        # Send a mail if any changed in price, otherwise do nothing
        if (len(self.itemsChanged) > 0):
            self.sendMail('updated')

        # Reset list for next iteration
        self.itemsChanged = list()

    # Insert all items from a list into our DB
    def insertAll(self):
        with open("amazon.txt", "r") as f:
            for line in f:
                self.add(line.strip())

    # Reset the DB
    def reset(self):
        self.collection.delete_many({})

    def sendMail(self, msgtype):
        senderemail, senderpass, recipient = None, None, None

        # email.txt should be formatted as follows, and strictly as follows
        # (your email)
        # (your pass)
        # (who you wanna send to's email)
        with open("email.txt", "r") as f:
            senderemail = f.readline().strip()
            senderpass = f.readline().strip()
            recipient = f.readline().strip()

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(senderemail, senderpass)

        if (msgtype == "updated"):
            subject = f"{len(self.itemsChanged)} items changed in price"
            body = ""
            for link in self.itemsChanged:
                body += link + "\n"
        else:
            subject = f"{msgtype['title']} added"
            body = f"{msgtype['title']} is now under watch. URL: {msgtype['url']}"

        msg = f"Subject: {subject}\n\n{body}"
        server.sendmail(
            senderemail,
            recipient,
            msg
        )
        print("Sent mail")
        server.quit()


def main():
    mongoCollection = "Amazon"
    mongoCluster = ""
    with open("cluster.txt", "r") as f:
        mongoCluster = f.readline().strip()

    checker = PriceChecker(mongoCluster)
    checker.setCollection(mongoCollection)
    checker.reset()
    checker.insertAll()


if __name__ == '__main__':
    main()
