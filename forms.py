from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class SignupForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirmation = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

class LoginForm(FlaskForm):
  username = StringField("username", validators=[DataRequired()])
  password = PasswordField("password", validators=[DataRequired()])

class AddHouseForm(FlaskForm):
  houseName = StringField(label="House Name", validators=[DataRequired()])
  houseAddress = StringField(label="House Address", validators=[DataRequired()])
  houseRooms = IntegerField(label="Number Of Rooms", validators=[DataRequired()])
  houseBeds = IntegerField(label="Number Of Beds", validators=[DataRequired()])
