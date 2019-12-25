from flask import render_template, url_for, flash, redirect, request
from pricechecker import app, db, bcrypt, webscraper
from pricechecker.forms import RegistrationForm, LoginForm, ItemForm, RefreshForm
from pricechecker.models import User, Item
from flask_login import login_user, logout_user, current_user, logout_user, login_required
from datetime import datetime
import urllib

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("pricechecker"))
    else:
        return redirect(url_for("about"))


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/announcements")
def announcements():
    return render_template("announcements.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Registered", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("pricechecker"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/pricechecker")
def pricechecker():
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("pricechecker_main.html")


@app.route("/pricechecker/checkitems", methods=["GET", "POST"])
@login_required
def pricechecker_checkitems():
    form = RefreshForm()
    cur_userid = current_user.get_id()
    items = Item.query.all()

    # Checking db items
    if form.validate_on_submit():
        for item in items:
            webscraper.set_to_url(item.url)
            cur_price = webscraper.get_item_price()
            last_price = item.prices[-1]

            if cur_price == last_price:
                price_change = 0
            else:
                price_change = webscraper.price_as_num(item.prices[-1]) - webscraper.price_as_num(cur_price)

            db_item = Item.query.filter_by(store=item.store, name=item.name).first()
            db_prices = db_item.prices
            db_times = db_item.price_times
            
            db_prices.append(cur_price)
            db_times.append(datetime.utcnow())

            db_item.prices = ["dummy"]
            db_item.price_times = ["dummyalso"]

            db.session.commit()
            db.session.refresh(db_item)

            db_item.prices = db_prices
            db_item.price_times = db_times
            db.session.commit()
        return redirect(url_for("pricechecker_checkitems"))

    send_nuds = []
    for item in items:
        cur_item = {}
        if str(cur_userid) in item.bought_by:
            cur_item["name"] = item.name
            cur_item["store"] = item.store
            cur_item["price"] = item.prices[-1]

            webscraper.set_to_url(item.url)
            cur_price = webscraper.get_item_price()
            last_price = item.prices[-1]

            if cur_price == last_price:
                price_change = 0
            else:
                price_change = webscraper.price_as_num(item.prices[-2]) - webscraper.price_as_num(item.prices[-1])
                
            cur_item["price_change"] = price_change
            cur_item["price_time"] = datetime.utcnow()
            send_nuds.append(cur_item)

    return render_template("pricechecker_checkitems.html", form=form, items=send_nuds)


@app.route("/pricechecker/additems", methods=["GET", "POST"])
@login_required
def pricechecker_additems():
    form = ItemForm()
    cur_userid = current_user.get_id()

    # Adding a new item to the db
    if form.validate_on_submit():
        url = form.url.data
        if webscraper.validate_url(url):
            item_store = webscraper.get_store_name(url)
            item_name = ''
            item_price = ''

            # Get the item's name and price
            if type(item_store) == str:
                webscraper.set_to_url(url)
                item_name = webscraper.get_item_name()
                item_price = webscraper.get_item_price()
                
                # Check if the item is already in our database
                db_item = Item.query.filter_by(store=item_store, name=item_name).first()
                if db_item:
                    item_list = db_item.bought_by
                    item_list.append(cur_userid)
                    db_item.bought_by = ["dummy"]
                    db.session.commit()
                    db.session.refresh(db_item)
                    db_item.bought_by = item_list
                    db.session.commit()

                    db_item.bought_by.append(cur_userid)
                    db.session.commit()
                else:
                    item = Item(name=item_name, url=url, store=item_store, prices=item_price, bought_by=cur_userid)
                    user = User.query.filter_by(id=cur_userid).first()
                    user.items.append(item_name)

                    db.session.add(item)
                    db.session.commit()
                return redirect(url_for("pricechecker_checkitems"))
            else:
                flash("Invalid Link", "danger")
        else:
            flash("Invalid Link", "danger")
            return redirect(url_for("announcements"))

    # Checking db items
    send_nuds = []
    items = Item.query.all()
    for item in items:
        cur_item = {}
        if str(cur_userid) in item.bought_by:
            cur_item["name"] = item.name
            cur_item["store"] = item.store
            cur_item["price"] = item.prices[-1]
            send_nuds.append(cur_item)

    return render_template("pricechecker_additems.html", form=form, items=send_nuds)

