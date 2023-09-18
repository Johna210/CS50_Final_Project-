import os

from flask import Flask, render_template, url_for, redirect,request, session
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 library to use SQLite database
db = SQL("sqlite:///db/recipes.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["Get","Post"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")