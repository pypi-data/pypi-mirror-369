'''
Created on 8 Jan 2024

@author: jacklok
'''
from wtforms import StringField, validators, DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from datetime import date

class PushNotificationSetupForm(ValidationBaseForm):
    title                        = StringField('Title',[
                                                validators.DataRequired(message="Title is required"),
                                                validators.Length(max=65, message="Title length must not more than 65 characters")
                                            ])
    
    desc                         = StringField('Description',[
                                                validators.DataRequired(message="Description is required"),
                                                validators.Length(max=240, message="Description length must not more than 240 characters")
                                            ])
    
    send_mode                   = StringField('Send Mode',[
                                                validators.DataRequired(message="Send Mode is required"),
                                            ])
    
    schedule_date                = DateField('Schedule Date', default=date.today, format='%d/%m/%Y',validators=[
                                                custom_validator.RequiredIf(message=gettext("Schedule Date is required"),
                                                                      send_mode=(
                                                                                        'send_schedule',
                                                                                    )
                                                                      ),
                                                
                                            ])
    
    schedule_time                = StringField('Schedule Time',validators=[
                                                custom_validator.RequiredIf(message=gettext("Schedule Time is required"),
                                                                      send_mode=(
                                                                                        'send_schedule',
                                                                                    )
                                                                      ),
                                                
                                            ])
    
    content_type                   = StringField('Content Type',[
                                                validators.Optional(),
                                            ])
    
    action_link                   = StringField('External Link',[
                                                validators.Optional(),
                                                validators.Length(max=500, message="External link length must not more than 500 characters")
                                            ])
    
    text_content                  = StringField('Text Message',[
                                                validators.Optional(),
                                                validators.Length(max=1000, message="Text Message length must not more than 1000 characters")
                                            ])
    
    image_content                 = StringField('Image Content',[
                                                validators.Optional(),
                                            ])
    