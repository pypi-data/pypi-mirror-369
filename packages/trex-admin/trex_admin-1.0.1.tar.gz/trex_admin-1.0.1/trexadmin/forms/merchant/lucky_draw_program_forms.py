'''
Created on 26 Feb 2021

@author: jacklok
'''

from wtforms import StringField, validators, BooleanField, IntegerField
from wtforms.fields.html5 import DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from datetime import date
from wtforms.fields.core import FloatField
from flask_babel import gettext
from trexmodel import program_conf
from wtforms.validators import Length
from wtforms.fields.simple import HiddenField

class LuckyDrawProgramBaseForm(ValidationBaseForm):
    program_key             = HiddenField('Program Key')
    testing                 = HiddenField('Testing')    
    
class LuckyDrawProgramDetailsForm(LuckyDrawProgramBaseForm):
    label                    = StringField('Label', [
                                        validators.InputRequired(gettext('Program Label is required')),
                                        Length(max=100)
                                        ]
                                        )
    start_date              = DateField('Program Start Date', default=date.today, format='%d/%m/%Y')
    end_date                = DateField('Program End Date', default=date.today, format='%d/%m/%Y')
    desc                    = StringField('Description', [
                                        ]
                                        )

class LuckyDrawProgramConditionForm(LuckyDrawProgramBaseForm):
    is_recurring_scheme     = BooleanField('Is Recurring Scheme indicator', [
                                        validators.InputRequired(gettext('Is recurring Scheme indicator is required')),
                                        ],
                                        false_values=('False', 'false', 'off')
                                        )  
    spending_currency       = FloatField('Spending Currency', [
                                        validators.InputRequired(gettext('Spending Currency is required')),
                                        ]
                                        )  
    
    entry_limit_type       = StringField('Ticket Limit', [
                                        validators.InputRequired(gettext('Ticket limit is required')),
                                        ])
    
    ticket_limit_amount     = IntegerField('Maximum ticket amount', [
                                        custom_validator.RequiredIf(gettext('Maximum ticket amount is required'), 
                                                                    ticket_limit_type=(
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_MONTH,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_WEEK,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_DAY,
                                                                                )
                                                                    )
                                        ])
    
class LuckyDrawProgramSettingsForm(LuckyDrawProgramBaseForm):
    one_per_transaction     = BooleanField('One per Transaction indicator', [
                                        validators.InputRequired(gettext('One per transaction indicator is required')),
                                        ],
                                        false_values=('False', 'false', 'off')
                                        )  
    
    spending_currency       = FloatField('Spending Currency', [
                                        validators.InputRequired(gettext('Spending Currency is required')),
                                        ]
                                        )  
    
    ticket_limit_type       = StringField('Ticket Limit', [
                                        validators.InputRequired(gettext('Ticket limit is required')),
                                        ])
    
    ticket_limit_amount     = IntegerField('Maximum ticket amount', [
                                        custom_validator.RequiredIf(gettext('Maximum ticket amount is required'), 
                                                                    ticket_limit_type=(
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_MONTH,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_WEEK,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_DAY,
                                                                                )
                                                                    )
                                        ])    
    ticket_expiry_date_length_in_day    = IntegerField(gettext('Length of ticket expiry date in day'),[
                                                validators.InputRequired(message=gettext("Length of ticket expiry date in day is required")),
                                                
                                            ])
    
class LuckyDrawProgramExclusivityForm(LuckyDrawProgramBaseForm):
    
    tags_list                           = StringField('Tagging', [
                                        ])
    
    membership_key                      = StringField(
                                            label='Membership', 
                                                validators=[
                                        
                                                ]
                                            )
    
    tier_membership_key                 = StringField(
                                            label='Tier Membership', 
                                            validators=[
                                        
                                            ]
                                            )    
    
    


