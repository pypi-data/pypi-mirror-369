'''
Created on 5 Jul 2022

@author: jacklok
'''

from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from wtforms.fields.simple import PasswordField

class ResetUserPasswordForm(ValidationBaseForm):
    reset_password_token    = StringField('Reset password Token', [
                                        validators.DataRequired(message="Reset password token is required"),
                                        ]
                                        )    
    
    password                = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password        = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )