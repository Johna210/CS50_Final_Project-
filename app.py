import os
import sqlite3

from flask import Flask, render_template, url_for, redirect, request, session
from cs50 import SQL
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask_wtf.csrf import CSRFProtect

from helpers import login_required

app = Flask(__name__)
SECRET_KEY = 'safddsgayfdsgfhjgs'
CSRF_ENABLED = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)
Session(app)

# Configure CS50 library to use SQLite database
# db = SQL("sqlite:///db/recipes.db")
db = SQL("sqlite:///db/recipes.db")


@app.route("/")
@login_required
def index():

    # get the current user logged in
    user_id = session["user_id"]
    return render_template("index.html")


@app.route("/login", methods=["Get", "Post"])
def login():
    session.clear()
    return render_template("login.html")


class RegistrationForm(FlaskForm):
    """A class to create a registration for that is easier to 
    validate and save on database."""
    email = StringField('Email', validators=[DataRequired(message="Email is required."),
                                             Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(
        message="Username is required."), Length(1, 64)])
    firstname = StringField('Firstname', validators=[DataRequired(
        message="Please enter the first name."), Length(1, 64)])
    lastname = StringField('Lastname', validators=[DataRequired(
        message="Please enter yout last name."), Length(1, 64)])

    password = PasswordField('Password', validators=[DataRequired(message="Fill the password."), Length(1, 64),
                                                     EqualTo('confirmation', message='Passwords must match.')])
    confirmation = PasswordField('confirmation', validators=[
        DataRequired(message="Confirm your password."), Length(1, 64)])

    submit = SubmitField('Register')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user."""

    form = RegistrationForm(request.form)
    errors = []
    # print(form.validate)

    if request.method == "POST" and form.validate():
        # Get user information and save them into variables.
        first_name = form.firstname.data
        last_name = form.lastname.data
        email = form.email.data
        user_name = form.username.data
        password = form.password.data

        # Encrypted password
        hased_pass = generate_password_hash(password)

        # check to see if the same username or email exists
        row = db.execute("SELECT * FROM users WHERE username = ?", user_name)
        row2 = db.execute("SELECT * FROM users WHERE email = ?", email)

        # Give respective errors if there are already taken username or email.
        if row or row2:
            if row:
                errors.append("Username already taken!")
            if row2:
                errors.append("Email already taken!")

            return render_template("register.html", form=form, errors=errors)

        # If its a new registration put the data in the database.
        db.execute(
            "INSERT INTO users(firstname,lastname,username,email,password) VALUES(?,?,?,?,?)",
            first_name, last_name, user_name, email, hased_pass)

        # After adding the user in the database log the user in
        session["user_id"] = row[0]["id"]
        # Redirect user to the login page
        return redirect("/login")

    # Helper function to display errors in the terminal
    # elif not form.validate():
    #     for field in form:

    #         if field.name == 'csrf_token':
    #             continue
    #         if field.errors:
    #             print(field.name, ':', field.errors)

    return render_template("register.html", form=form, errors=errors)
