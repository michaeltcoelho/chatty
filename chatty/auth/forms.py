import re

from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Length, Regexp


class BaseAuthForm(Form):

    username = StringField('Username', validators=[
        InputRequired(),
        Length(min=3, max=16),
        Regexp('[a-z]{3,16}', re.IGNORECASE)
    ])
    password = PasswordField('Password', validators=[
        InputRequired(),
        Length(min=6, max=255)
    ])

class RegisterForm(BaseAuthForm):

    confirm = PasswordField('Confirm password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must be equal')
    ])

class LoginForm(BaseAuthForm):
    pass
    
