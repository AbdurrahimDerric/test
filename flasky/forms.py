from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,BooleanField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError
from flasky.Models import User
from flask_login import  current_user
from flask import redirect,url_for

class Regitration_form(FlaskForm):
    username = StringField('User Name', validators= [DataRequired(),Length(2,20)])
    email = StringField("Email", validators= [DataRequired(), Email()])
    password = PasswordField("Password", validators= [DataRequired()])
    confirm_password = PasswordField("Confirm Password",validators=[EqualTo("password")] )

    submit = SubmitField("Sign Up")

    def validate_username(self,username):
        user =  User.query.filter_by(username = username.data.lower()).first()
        if user:
            raise ValidationError("username taken!")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("Email taken!")



class Login_form(FlaskForm):
    email = StringField("Email", validators= [DataRequired(), Email()])
    password = PasswordField("Password", validators= [DataRequired()])

    remember = BooleanField('Remember Me')
    submit = SubmitField("login")

class Update_info_form(FlaskForm):
    username = StringField('User Name', validators= [DataRequired(),Length(2,20)])
    email = StringField("Email", validators= [DataRequired(), Email()])
    picture = FileField("Profile picture", validators=[FileAllowed(["jpg","png"])])
    submit = SubmitField("Update")

    def validate_username(self,username):
        username.data = username.data.lower()
        if username.data != current_user.username:
            user =  User.query.filter_by(username = username.data).first()
            if user:
                print("here")
                raise ValidationError("username taken!")


    def validate_email(self, email):
        if current_user.email != email.data:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("Email taken!")


class Post_form(FlaskForm):
    title = StringField("Title", validators= [DataRequired()])
    content = TextAreaField("Content", validators= [DataRequired()])

    submit = SubmitField("Post")

class Submit_form(FlaskForm):
    password = PasswordField("Password", validators= [DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField("Submit")

class Reset_request_form(FlaskForm):
    email = StringField("Email", validators= [DataRequired(), Email()])
    submit = SubmitField("Send")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user == None:
            raise ValidationError("No user with such email!")

class Reset_password_form(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Reset")
