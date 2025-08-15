'''
Created on 14 Sep 2023

@author: jacklok
'''
from wtforms import StringField, PasswordField, validators
from trexlib.forms.base_forms import ValidationBaseForm
 

class UserSigninForm(ValidationBaseForm):
    email            = StringField('SignIn email', [
                                        validators.DataRequired(message="SignIn email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    password                = PasswordField('Password', [
                                        validators.InputRequired(),
                                        ]
                                        )