import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from webscrapper.webscrape import WebScraper

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("MYSQL")
app.config["SECRET_KEY"] = os.environ.get("SECRET")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

stores = [store.lower().strip() for store in os.environ.get("STORES").split(',')]
user_agent = os.environ.get("USER_AGENT")
webscraper = WebScraper(user_agent, stores)

# webscraper.set_to_url("https://www.amazon.com/JUNO-Co-Microfiber-Latex-Free-Foundations/dp/B07JFPZ7JL/ref=br_msw_pdt-2?_encoding=UTF8&smid=A2NDMQ1CNSKX52&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=&pf_rd_r=HX19WQXPX4J13FGEW88M&pf_rd_t=36701&pf_rd_p=b4a0cbde-899a-4d17-83a6-51dc0f437596&pf_rd_i=desktop")
# print(webscraper.soup)
# print("\n\n\n")
from pricechecker import routes
