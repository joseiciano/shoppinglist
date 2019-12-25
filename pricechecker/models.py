from pricechecker import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    items = db.Column(db.PickleType(), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.items = []

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    url = db.Column(db.String(512), unique=True, nullable=False)
    store = db.Column(db.String(512), nullable=False)
    prices = db.Column(db.PickleType(), nullable=False)
    price_times = db.Column(db.PickleType(), nullable=False)
    bought_by = db.Column(db.PickleType(), nullable=False)

    def __init__(self, name, url, store, prices, bought_by):
        self.name = name
        self.url = url
        self.store = store
        self.prices = [prices]
        self.price_times = [datetime.utcnow()]
        self.bought_by = [bought_by]

    def __repr__(self):
        return f"Item('{self.name}')"

