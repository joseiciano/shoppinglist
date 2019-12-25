from flask import render_template, url_for, flash, redirect, request
from pricechecker import app, db, bcrypt, url_manager, webscraper
from pricechecker.forms import RegistrationForm, LoginForm, ItemForm
from pricechecker.models import User, Item
from flask_login import login_user, logout_user, current_user, logout_user, login_required
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
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/pricechecker")
def pricechecker():
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("pricechecker_main.html")


@app.route("/pricechecker/additem", methods=["GET", "POST"])
@login_required
def pricechecker_additem():
    return render_template("pricechecker_additem.html", form=ItemForm())


@app.route("/pricechecker/checkitems", methods=["GET", "POST"])
@login_required
def pricechecker_checkitems():
    form = ItemForm()

    if form.validate_on_submit():
        url = form.url.data
        if url_manager.validate_url(url):
            store = url_manager.get_store_name(url)

            if type(store) == str:

            else:
                flash("Invalid Link", "danger")
        else:
            flash("Invalid Link", "danger")

    return render_template("pricechecker_checkitems.html", form=form)