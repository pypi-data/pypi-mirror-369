'''
Created on 7 Apr 2021

@author: jacklok
'''
from wtforms import StringField, IntegerField, validators
from wtforms.fields.html5 import DateField
from wtforms.widgets import html5 as h5widgets
from trexlib.forms.base_forms import ValidationBaseForm
from flask_babel import gettext
from trexlib.libs.wtforms import validators as custom_validator
from trexlib.libs.wtforms.fields import CurrencyField
from trexmodel import program_conf

class MembershipForm(ValidationBaseForm):
    membership_key              = StringField('Membership Key')
    label                       = StringField('Membership Label', [
                                        validators.InputRequired(gettext('Membership label is required'))
                                        ]
                                        )
    
    desc                        = StringField('Description', [
                                        validators.Length(max=1000, message='Description length must be within 1000 characters'),
                                        ]
                                        )
    
    terms_and_conditions        = StringField('Terms and conditions', [
                                        validators.Length(max=5000, message='Terms and conditions length must be within 5000 characters'),
                                        ]
                                        )
    
class BasicMembershipForm(ValidationBaseForm):
    membership_key                  = StringField('Membership Key')
    label                           = StringField('Membership Label', [
                                        validators.InputRequired(gettext('Membership label is required'))
                                        ]
                                        )
    
    desc                            = StringField('Membership Description', [
                                        
                                        ]
                                        )
    terms_and_conditions            = StringField('Terms and conditions', [
                                        
                                        ]
                                        )
    
    discount_rate                   = IntegerField('Discount Rate', [
                                        ],
                                        default=0,     
                                        widget=h5widgets.NumberInput(min=0, max=100, step=10)
                                        ) 
    
    expiration_type      = StringField('Expiration Type', [
                                            validators.InputRequired(gettext('Membership expiration type is required'))
                                            ])
    
    expiration_date      = DateField('Expiration Date', [
                                            custom_validator.RequiredIf(gettext('Membership Expiration Date is required'), 
                                                                    expiration_type=program_conf.MEMBERSHIP_EXPIRATION_TYPE_SPECIFIC_DATE)
                                            ],
                                            format='%d/%m/%Y')
    
    expiration_value     = IntegerField('Expiration Value', [
                                                custom_validator.RequiredIf(gettext('Membership Expiration length is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_YEAR,
                                                                                        program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_WEEK,
                                                                                        program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_DAY,
                                                                                    )
                                                                    )
                                        ],
                                        default=0,     
                                        ) 
    
       
    
    
class TierMembershipForm(BasicMembershipForm):   
    entitle_qualification_type      = StringField('Entitle Qualification', [
                                                    validators.InputRequired(gettext('Membership Entitle Qualificatio is required'))
                                                    ])
    
    entitle_qualification_value     = CurrencyField('Membership Entitle Qualificatio Value', [
                                                    custom_validator.RequiredIf(gettext('Membership Entitle Qualificatio value is required'),
                                                                          entitle_qualification_type = program_conf.MEMBERSHIP_REQUIRED_ENTITLE_QUALIFICATION_VALUE
                                                                          )
                                                    ]) 
    
    
    upgrade_expiry_type             = StringField('Membership Upgrade Expiry', [
                                                    validators.InputRequired(gettext('Membership upgrade expiry is required'))
                                                    ])
    
    
    