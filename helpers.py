import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
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
