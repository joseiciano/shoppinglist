
import datetime
import smtplib
import pymongo
import bcrypt
from pymongo import MongoClient
from webscrape import WebScraper

class PriceChecker:
    cluster, db, collection, user, scrapper, itemsChanged = None, None, None, None, None, None

    def __init__(self, mCluster):
        self.cluster = MongoClient(mCluster)
        self.db = self.cluster["itemStorage"]
        self.scrapper = WebScraper()
        self.itemsChanged = list()

    # Set a specific collection within the database
    def setCollection(self, collection):
        self.collection = self.db[collection]

    # Checks if a user already exists, returning True if yes
    def checkIfRegistered(self, email, first, last):
        user = self.collection.find_one({"email": email})
        if (user):
            print("Email already registered")
            return True
        user = self.collection.find_one({"first_name": first, "last_name": last})
        if (user):
           print("Name already registered")
           return True
        return False

    # Checks if a user gave valid information upon signing in
    def checkSignIn(self, email, password):
        user = self.collection.find_one({"email": email})
        if (not user):
            print("No such user exists")
            return False
        hashed = bytes(user["password"])

        if (bcrypt.hashpw(password.encode("utf-8"), hashed) == hashed):
            self.user = email
            return True
        return False
    
    # Adds a new user to the db storage
    def adduser(self, first, last, email, password):
        newuser = {"first_name": first, "last_name": last, "email": email, "password": password, "items": []}
        self.collection.insert_one(newuser)
        
    # Add a new item to our db
    def add(self, URL):
        self.scrapper.setDataFromURL(URL)
        item = {
            "_id": self.collection.count_documents({}) + 1,
            "title": self.scrapper.getTitle("productTitle"),
            "price": [self.scrapper.getPrice("priceblock_ourprice")],
            "priceAsNum": [self.scrapper.getPriceAsNum("priceblock_ourprice")],
            "priceChange": [0],
            "date": [str(datetime.date.today())],
            "url": URL
        }

        exists = self.collection.find_one({"email": self.user, "items": {"$elemMatch": {"url": URL}}})
        # Only add to the DB if it is not in it already
        if (exists):
            print(f'{item["title"]} is already under watch')
        else:
            self.collection.update_one({"email": self.user}, {"$push": {"items": item}})
            print(f'{item["title"]} added under watch')

    # self.sendMail(item)

    # Check and update all the prices of every item in our DB
    def checkAll(self):
        useritems = self.collection.find_one({"email": self.user})
        if not useritems:
            return

        for item in useritems['items']:
            self.scrapper.setDataFromURL(item["url"])
            curPrice = self.scrapper.getPrice("priceblock_ourprice")

            # Only update when there"s a pricechange
            lastPrice = item["price"][-1]
            if (curPrice != lastPrice):
                curPriceAsNum = self.scrapper.getPriceAsNum("priceblock_ourprice")
                curDate = str(datetime.date.today())

                # Change the price of the item with our new item in the DB
                self.collection.update_one({"email": self.user, "items": {"$elemMatch": {"title": item["title"]}}}, {
                    "$push": {"price": curPrice, "priceAsNum": curPriceAsNum, "date": curDate}
                })

                # Note if the item increased or decreased in price, and by how much
                if (curPrice > lastPrice):
                    msg = f'{item["title"]} increased in price by ${curPrice - lastPrice}. URL = {item["url"]}'
                else:
                    msg = f'{item["title"]} decreased in price by ${lastPrice - curPrice}. URL = {item["url"]}'
                self.itemsChanged.append(msg)
            else:
                print(f'{item["title"]} has not changed in price')


    # Query the data, checking previous prices
    def query(self):
        useritems = self.collection.find_one({"email": self.user})
        if not useritems:
            print("Your list is empty")
            return
        
        for item in useritems["items"]:
            print(f'{item["title"]}: {item["price"][-1]}')

    # Removes an item from the db
    def remove(self):
        useritems = self.collection.find_one({"email": self.user})
        if not useritems:
            return

        choice = -1
        while (choice == -1):
            counter = 1
            arr = list()
            for item in useritems["items"]:
                print(f'{counter}. {item["title"]}')
                arr.append(item["title"])
                counter += 1
            print(f'0. Go back to main menu')

            # Empty list of items, can't delete anymore
            if (len(arr) == 0):
                print("No more items to delete")
                break

            choice = input("Enter the number of the item you want to delete")
        
            # User gave something that wasn't a number or in our range, so we gotta re-ask
            redo = False
            for char in choice:
                if (not char.isdigit()):
                    print("Invalid option")
                    redo = True
            if (redo or int(choice) < 0 or int(choice) > counter):
                choice = -1
                continue

            self.collection.update_one({"email": self.user}, {"$pull": {"title": arr[int(choice)+1]}})
            arr.pop(int(choice)+1)
        

    # # Lists the items in our db
    # def listitems(self):
    #     useritems = 

    # Insert all items from a list into our DB
    def insertAll(self):
        # Currently, just open a text file with a list and adds all of them
        with open("amazon.txt", "r") as f:
            for line in f:
                self.add(line.strip())

    # # Reset the user"s DB storage
    def reset(self):
        self.collection.delete_many({})

    def sendMail(self, msgtype):
        senderemail, senderpass, recipient = None, None, None

        # sender is supposed to be db admin
        # recipient is user
        # email.txt should be formatted as follows, and strictly as follows
        # # (your email)
        # # (your pass)
        with open("email.txt", "r") as f:
            senderemail = f.readline().strip()
            senderpass = f.readline().strip()
        recipient = self.user

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(senderemail, senderpass)

        if (msgtype == "updated"):
            subject = f"{len(self.itemsChanged)} items changed in price"
            body = ""
            for link in self.itemsChanged:
                body += link + "\n"
        else:
            subject = f'{msgtype["title"]} added'
            body = f'{msgtype["title"]} is now under watch. URL: {msgtype["url"]}'

        msg = f'Subject: {subject}\n\n{body}'
        server.sendmail(
            senderemail,
            recipient,
            msg
        )
        print("Sent mail")
        server.quit()