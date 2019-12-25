import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("MYSQL")
db = SQLAlchemy(app)

stores = [store.lower().strip() for store in os.environ.get("STORES").split(',')]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    items = db.Column(db.PickleType)

    def __repr__(self):
        return '<User %r>' % self.username
    
    def __init__(self, username, email, items):
        self.username = username
        self.email = email
        self.items = items

# class Items(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     item_name = db.Column(db.String(100), unique=False, nullable=False)

# class Buyer_Tracker(db.Model):
#     id = db.Column(db.Integer, primary_key=True)


@app.route('/', methods=["Get"])
def get():
    return jsonify({ "User-Agent": request.headers.get("User-Agent")})

if __name__=="__main__":
    app.run(debug=True)
