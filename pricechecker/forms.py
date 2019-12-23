from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequited, Length, Email, EqualTo, ValidationError
from pricechecker.models import User