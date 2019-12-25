import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from webscrapper.webscrape import URLCleaner, WebScraper


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("MYSQL")
app.config["SECRET_KEY"] = os.environ.get("SECRET")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

stores = [store.lower().strip() for store in os.environ.get("STORES").split(',')]
url_manager = URLCleaner(stores)
webscraper = WebScraper(request.headers.get)

from pricechecker import routes
