from datetime import datetime
from pricechecker import db, login_manager
from flask_login import UserMixin

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
    name = db.Column(db.String(200), nullable=False)
    store = db.Column(db.String(200), nullable=False)
    item_prices = db.Column(db.PickleType(), nullable=False)
    item_price_times = db.Column(db.PickleType(), nullable=False)
    bought_by = db.Column(db.PickleType(), nullable=False)

    def __init__(self, name, store, cur_price, cur_price_time, bought_by):
        self.name = name
        self.store = store
        self.item_prices = [cur_price]
        self.item_price_times = [cur_price_time]
        self.bought_by = [bought_by]

    def __repr__(self):
        return f"Item('{self.item_name}')"

