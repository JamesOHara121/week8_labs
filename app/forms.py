from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField, SelectField, DateField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Student
from app import db
import sqlalchemy as sa


class TopicForm(FlaskForm):
    topic = StringField("Topic", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddGroupForm(FlaskForm):
    group_name = StringField("Group name", validators=[DataRequired()])
    topic = SelectField("Select a topic")
    submit = SubmitField("Create group")


class ManageGroupForm(FlaskForm):
    group_name = StringField("Group name", validators=[DataRequired()])
    add_student = StringField("Add a student to the group")
    remove_student = SelectField("Remove a student from the group", choices=[("None", "--Select--")])
    submit = SubmitField("Save changes")


class BookingForm(FlaskForm):
    group = SelectField("Select a group", choices=[])
    venue = SelectField("Select a venue", choices=[])
    date = DateField("Date", format='%Y-%m-%d')
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(Student).where(
            Student.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(Student).where(
            Student.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')