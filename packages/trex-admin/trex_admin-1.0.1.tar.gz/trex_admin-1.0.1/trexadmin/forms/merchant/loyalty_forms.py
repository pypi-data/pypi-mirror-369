'''
Created on 30 Dec 2022

@author: jacklok
'''

from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from flask_babel import gettext
from trexlib.libs.wtforms import validators as custom_validator
from wtforms.fields.core import BooleanField, IntegerField




class LoyaltyDeviceSettingForm(ValidationBaseForm):
    loyalty_device_setting_key              = StringField('Device Key')
    device_name                             = StringField(gettext('Device name'),[
                                                validators.InputRequired(message=gettext("Device name is required")),
                                                validators.Length(max=100, message="Device name length must not more than 100 characters")
                                            ])
    enable_lock_screen                      = BooleanField('Enable lock screen', [
                                                ],
                                                false_values=('False', 'false', 'off')
                                                )
    lock_screen_code                        = StringField(gettext('Lock screen code'),[
                                                custom_validator.RequiredIf(gettext('Lock screen code is required'), 
                                                                    enable_lock_screen=True
                                                                    ),
                                                validators.Length(max=12, message="Lock screen code length must not more than 12 characters")
                                            ])
    
    lock_screen_length_in_second            = IntegerField('Inactive in second to lock', [
                                                custom_validator.RequiredIf(gettext('Inactive in second to lock is required'), 
                                                                    enable_lock_screen=True
                                                                    )
                                        ])
    
    assign_outlet_key                      = StringField(gettext('Assign Outlet'),[
                                                validators.InputRequired(message=gettext("Assign outlet is required")),
                                                
                                            ])
