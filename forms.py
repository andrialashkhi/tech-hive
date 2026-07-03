from datetime import date

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, EmailField, DateField, SelectField,
                      SubmitField, TextAreaField, FloatField, IntegerField, BooleanField)
from wtforms.validators import DataRequired, Optional, EqualTo, Length, Email, NumberRange, ValidationError

from models import User, CATEGORIES


class RegisterForm(FlaskForm):
    username = StringField("Enter Username",
                            validators=[DataRequired(message="Username is required"),
                                        Length(min=4, max=32, message="Username must be between 4 and 32 characters")])

    email = EmailField("Enter Email", validators=[DataRequired(message="Email is required"),
                                                    Email(message="Enter a valid email address")])

    password = PasswordField("Create Password", validators=[
        DataRequired(message="Password is required"),
        Length(min=8, max=64, message="Password must be at least 8 characters")])

    repeat_password = PasswordField("Repeat Password", validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")])

    birthday = DateField("Birthday", validators=[DataRequired(message="Birthday is required")])

    submit = SubmitField("Create Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("That username is already taken")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("An account with that email already exists")

    def validate_birthday(self, field):
        if field.data:
            age = (date.today() - field.data).days // 365
            if age < 13:
                raise ValidationError("You must be at least 13 years old to register")
            if field.data > date.today():
                raise ValidationError("Birthday cannot be in the future")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")
    submit = SubmitField("Log In")


class OrderForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    product = SelectField("Product", choices=[], coerce=int)
    quantity = IntegerField("Quantity", default=1, validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField("Place Order")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    image = StringField("Image filename or URL", validators=[DataRequired()])
    category = SelectField("Category", choices=[(c, c) for c in CATEGORIES], validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock", default=0, validators=[DataRequired(), NumberRange(min=0)])
    featured = BooleanField("Feature on homepage")
    submit = SubmitField("Save Product")


class EditProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    image = StringField("Image filename or URL", validators=[Optional()])
    category = SelectField("Category", choices=[(c, c) for c in CATEGORIES], validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    featured = BooleanField("Feature on homepage")
    submit = SubmitField("Update Product")


class NewsletterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Subscribe")


class OrderStatusForm(FlaskForm):
    status = SelectField("Status", choices=[])
    submit = SubmitField("Update")
