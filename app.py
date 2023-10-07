import os
import sqlite3
import json

from flask import Flask, render_template, url_for, redirect, request, session
from cs50 import SQL
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from flask_wtf.csrf import CSRFProtect

from helpers import login_required, RegistrationForm, generate, search_by_id, search_by_category, search_by_origin, search_by_name

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


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    # get the current user logged in
    user_id = session["user_id"]

    # Fetch daily recipes from the database
    today = date.today()

    row = db.execute("SELECT * FROM daily_recipes WHERE date = ?", today)
    if row:
        # if on the same date take the recipes saved in the database and display.
        recipes = row[0]["recipes"]
        meals = json.loads(recipes)
    else:
        # Get six recipes for the homepage
        meals = []
        for _ in range(6):
            new_meal = generate()
            if new_meal in meals:
                new_meal = generate()

            meals.append(new_meal)
            meals_json = json.dumps(meals)

        db.execute(
            "INSERT INTO daily_recipes(date,recipes) VALUES(?,?)", today, meals_json)

    return render_template("index.html", meals=meals)


@app.route("/login", methods=["Get", "Post"])
def login():

    session.clear()

    errors = []
    if request.method == "POST":
        # Take email from the form
        email = request.form.get("email")
        # Query the reuslts of the user from the database
        row = db.execute("SELECT * FROM users WHERE email = ?", email)

        user_id = row[0]["id"]
        print(user_id)
        session["user_id"] = user_id

        if len(row) > 0 and row[0]["email"] == email:

            # First check if the password entered by the user is correct
            password = request.form.get("password")
            if check_password_hash(row[0]["password"], password):
                # Remember which user has logged in
                session["user_id"] = row[0]["id"]
                return redirect("/")

            # if the password entered is not correct
            else:
                errors.append("Incorrect password entered!")
                return render_template("login.html", errors=errors)

        else:
            errors.append("Account doesn't exist")
            return render_template("login.html", errors=errors)

    else:
        return render_template("login.html")


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
        # session["user_id"] = row[0]["id"]
        # Redirect user to the login page
        return redirect("/login")

    """ Helper function to display errors in the terminal """
    # elif not form.validate():
    #     for field in form:

    #         if field.name == 'csrf_token':
    #             continue
    #         if field.errors:
    #             print(field.name, ':', field.errors)

    return render_template("register.html", form=form, errors=errors)


@app.route("/recipe", methods=["POST", "GET"])
@login_required
def recipe():

    if request.method == "POST":

        # Format the data that will be saved in the data base
        meal = {
            "id": session["meal_info"]["id"],
            "meal": session["meal_info"]["meal"],
            "category": session["meal_info"]["category"],
            "origin": session["meal_info"]["origin"],
            "img": session["meal_info"]["img_source"]
        }

        # To save in the databse with the format
        meals_json = json.dumps(meal)

        row = db.execute(
            "SELECT * FROM favourites WHERE user_id=?;", session["user_id"])

        # Check to see if the user have any favourites and to check if the recipe is already saved.
        if row:
            if row[0]["meal_id"] == meal["id"]:
                pass

            else:
                db.execute(
                    "INSERT INTO favourites(user_id,meal_info,meal_id) VALUES(?,?,?)", session["user_id"], meals_json, meal["id"])

        else:
            db.execute(
                "INSERT INTO favourites(user_id,meal_info,meal_id) VALUES(?,?,?)", session["user_id"], meals_json, meal["id"])

        return redirect("/favourites")
    # get the meal id
    meal_id = request.args.get("id")
    meal = search_by_id(meal_id)

    if meal:
        session["meal_info"] = meal
    return render_template("recipe.html", meal=meal)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    # categories and origins found on the mealdb
    categories = ['Beef', 'Breakfast', 'Chicken', 'Dessert', 'Goat', 'Lamb',
                  'Miscellaneous', 'Pasta', 'Pork', 'Seafood', 'Side', 'Starter', 'Vegetarian', 'Vegan']
    origins = ['American', 'British', 'Canadian', 'Chinese', 'Croatian', 'Dutch', 'Egyptian', 'Filipino', 'French', 'Greek', 'Indian', 'Irish', 'Italian', 'Jamaican',
               'Japanese', 'Kenyan', 'Malaysian', 'Mexican', 'Moroccan', 'Polish', 'Portuguese', 'Russian', 'Spanish', 'Thai', 'Tunisian', 'Turkish', 'Unknown', 'Vietnamese']

    meals = []

    if request.method == "POST":
        # If the user searched the reciepe by name
        if request.form.get("food"):
            # Get the name of food searched
            try:
                food_name = request.form.get("food")
                meals = search_by_name(food_name)
            except:
                pass

    # If either category or origin is clicked
    category = request.args.get("category")
    origin = request.args.get("area")

    # If the user clicked any category
    if category:
        meals = search_by_category(category)
    # Or if the user clicked on any country
    if origin:
        meals = search_by_origin(origin)

    return render_template("search.html", categories=categories, origins=origins, meals=meals)


@app.route("/favourites", methods=["GET", "POST"])
@login_required
def favourites():
    """First fetch the data from the db by using the user_id."""

    user_id = session["user_id"]
    row = db.execute("SELECT * FROM favourites WHERE user_id = ?", user_id)

    favourites = []

    for i in row:
        meal = json.loads(i["meal_info"])
        favourites.append(meal)

    meal_id = request.args.get("id")

    if meal_id:
        # If there is a delete button entered delete it from the list and from the database.
        for i in favourites:
            if i["id"] == meal_id:
                favourites.remove(i)

            db.execute("DELETE FROM favourites WHERE user_id=? AND meal_id=?;",
                       session["user_id"], meal_id)

    return render_template("favourites.html", favourites=favourites)


if __name__ == '__main__':
    app.run(debug=True)
