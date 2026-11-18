from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError("An account with that email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    summary = StringField("Summary", validators=[DataRequired(), Length(max=300)])
    category = SelectField("Category", coerce=int, choices=[])
    tags = StringField("Tags", description="Separate tags with commas")
    content = TextAreaField("Content", validators=[DataRequired()])
    is_published = BooleanField("Publish now", default=True)
    submit = SubmitField("Save post")


class CommentForm(FlaskForm):
    body = TextAreaField("Join the conversation", validators=[DataRequired(), Length(min=2, max=2000)])
    submit = SubmitField("Post comment")
