import os
import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session, jsonify
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError


def login_required(f):
    """A function to check wether a user is loogged in or not"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


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


def generate():
    """Generate some random recipes from the mealdb api."""
    url = "https://www.themealdb.com/api/json/v1/1/random.php"

    # Contact api
    response = requests.get(url)
    # response.raise_for_status()
    if response.status_code == 200:
        body = response.content
        # A Dictionaary holding every needed info on the meal
        info = json.loads(body)

        # A variable to save every ingredients with their measures
        ingredients = {}
        count = 1
        ingredient = info["meals"][0]

        # Loop through the json file until every igredient is found
        for i in ingredient:
            if i == f"strIngredient{count}":
                # If it's null or epmpty there is no more ingredient
                if ingredient[i] == None or ingredient[i] == "":
                    break
                else:
                    ingredients[ingredient[i]
                                ] = ingredient[f"strMeasure{count}"]
                count += 1

        # return only the needed vlaues precisely for the website.
        final = {
            "id": ingredient["idMeal"],
            "meal": ingredient["strMeal"],
            "category": ingredient["strCategory"],
            "origin": ingredient["strArea"],
            "instructions": ingredient["strInstructions"],
            "img_source": ingredient["strMealThumb"],
            "tags": ingredient["strTags"],
            "youtube": ingredient["strYoutube"],
            "source": ingredient["strSource"],
            "ingredients": ingredients
        }

        return final

    else:
        # Return an error message
        return jsonify({'error': 'Failed to get data from MealDB API.'})


def search_by_id(id):
    # api link
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}"

    # Contact api
    response = requests.get(url)

    # response.raise_for_status()
    if response.status_code == 200:
        body = response.content
        # A Dictionaary holding every needed info on the meal
        info = json.loads(body)

        # A variable to save every ingredients with their measures
        ingredients = {}
        count = 1
        ingredient = info["meals"][0]

        # Loop through the json file until every igredient is found
        for i in ingredient:
            if i == f"strIngredient{count}":
                # If it's null or epmpty there is no more ingredient
                if ingredient[i] == None or ingredient[i] == "":
                    break
                else:
                    ingredients[ingredient[i]
                                ] = ingredient[f"strMeasure{count}"]
                count += 1

        # return only the needed
        final = {
            "id": ingredient["idMeal"],
            "meal": ingredient["strMeal"],
            "category": ingredient["strCategory"],
            "origin": ingredient["strArea"],
            "instructions": ingredient["strInstructions"],
            "img_source": ingredient["strMealThumb"],
            "tags": ingredient["strTags"],
            "youtube": ingredient["strYoutube"],
            "source": ingredient["strSource"],
            "ingredients": ingredients
        }

        return final
    else:
        # Return an error message
        return jsonify({'error': 'Failed to get data from MealDB API.'})


def search_by_category(category):
    """A function for searching categories."""
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"

    # Contact api
    response = requests.get(url)

    # response.raise_for_status()
    if response.status_code == 200:
        body = response.content
        # A Dictionaary holding every needed info on the meal
        info = json.loads(body)
        meals = []

        for meal in info["meals"]:
            meals.append(meal)

        return meals
    else:
        # Return an error message
        return jsonify({'error': 'Failed to get data from MealDB API.'})


def search_by_origin(origin):
    """A function for searching categories."""
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?a={origin}"

    # Contact api
    response = requests.get(url)

    # response.raise_for_status()
    if response.status_code == 200:
        body = response.content
        # A Dictionaary holding every needed info on the meal
        info = json.loads(body)
        meals = []

        for meal in info["meals"]:
            meals.append(meal)

        return meals
    else:
        # Return an error message
        return jsonify({'error': 'Failed to get data from MealDB API.'})


def lists():
    url = "https://www.themealdb.com/api/json/v1/1/list.php?c=list"

    # Contact api
    response = requests.get(url)

    # response.raise_for_status()
    if response.status_code == 200:
        body = response.content
        # A Dictionaary holding every needed info on the meal
        info = json.loads(body)
        categories = []

        for category in info["meals"]:
            categories.append(category["strCategory"])

        return categories
    else:
        # Return an error message
        return jsonify({'error': 'Failed to get data from MealDB API.'})


def countries():
    url = "https://www.themealdb.com/api/json/v1/1/list.php?a=list"

    # Contact api
    response = requests.get(url)

    # response.raise_for_status()
    if response.status_code == 200:
        body = response.content
        # A Dictionaary holding every needed info on the meal
        info = json.loads(body)
        countries = []

        for country in info["meals"]:
            countries.append(country["strArea"])

        print(countries)

    else:
        # Return an error message
        return jsonify({'error': 'Failed to get data from MealDB API.'})
