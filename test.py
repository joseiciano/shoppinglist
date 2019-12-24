from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:AirportLady@22@127.0.0.1/users'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
    
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@app.route('/', methods=["Get"])
def get():
    return jsonify({ "msg": "Hello World"})
e = 
if __name__=="__main__":
    app.run(debug=True)
