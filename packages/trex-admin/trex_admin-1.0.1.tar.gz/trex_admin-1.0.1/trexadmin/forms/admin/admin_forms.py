'''
Created on 8 May 2020

@author: jacklok
'''
from wtforms import StringField, validators, PasswordField, BooleanField, SelectMultipleField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from trexlib.libs.wtforms.fields import IgnoreChoiceSelectMultipleField
from trexadmin.controllers.system.system_route_helpers import get_admin_permission_list

class AdminDetailsForm(ValidationBaseForm):
    admin_user_key      = StringField(gettext('Key'))
    name                = StringField(gettext('Full name'), [
                                        validators.DataRequired(message=gettext("Full name is required")),
                                        validators.Length(min=3, max=150, message=gettext('Full name length must be within 3 and 150 characters'))
                                        ]
                                        )
    email               = StringField(gettext('Email Address'), [
                                        validators.DataRequired(message=gettext("Email is required")),
                                        validators.Length(min=7, max=150, message=gettext("Emaill address length must be within 7 and 150 characters")),
                                        validators.Email(gettext("Please enter valid email address."))
                                        ]
                                        )
    
    
    
class AdminDetailsAddForm(AdminDetailsForm):
    password            = PasswordField(gettext('Password'), [
                                        validators.DataRequired(message=gettext("Password is required")),
                                        validators.EqualTo('confirm_password', message=gettext('Passwords must match'))
                                        ]
                                        )
    confirm_password    = PasswordField(gettext('Confirm Password'),[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )    

class AdminUserPermissionForm(ValidationBaseForm):
    admin_user_key           = StringField(gettext('Admin User Key'), [
                                        validators.DataRequired(message="Merchant user key is required")
                                    ])
    is_superuser             = BooleanField(gettext('Is superuser'), [])
    permission               = IgnoreChoiceSelectMultipleField(
                                    label=gettext('Permission'), 
                                    validators=[
                                            custom_validator.RequiredIfOtherFieldValueIsFalse('is_superuser', 
                                                                                              message="Permission is required"),
                                    ],
                                    choices=get_admin_permission_list(None)
                                    )
        
    