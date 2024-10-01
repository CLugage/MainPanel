from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InstanceForm(FlaskForm):
    plan_id = SelectField('Select Plan', coerce=int)
    submit = SubmitField('Create Instance')

class CreateInstanceForm(FlaskForm):
    plan_id = SelectField('Select Plan', coerce=int)
    submit = SubmitField('Create Instance')

