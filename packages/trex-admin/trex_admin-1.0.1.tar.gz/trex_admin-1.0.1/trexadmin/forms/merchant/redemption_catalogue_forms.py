'''
Created on 5 Dec 2023

@author: jacklok
'''

from wtforms import StringField, validators, IntegerField
from wtforms.fields.html5 import DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from datetime import date
from wtforms.fields.core import FloatField
from flask_babel import gettext
from trexmodel import program_conf
from trexlib.forms.common.common_forms import CheckBoxField, CustomDateField,\
    CustomIntegerField

class RedemptionCatalogueForm(ValidationBaseForm):
    redemption_catalogue_key             = StringField('Catalogue Key')


class DefineRedemptionCatalogueForm(RedemptionCatalogueForm):
    label                   = StringField('Label', [
                                        validators.InputRequired(gettext('Label is required'))
                                        ]
                                        )
    
    desc                    = StringField('Description', [
                                        
                                        ]
                                        )
    
    start_date              = DateField('Program Start Date', default=date.today, format='%d/%m/%Y'
                                        )
    end_date                = DateField('Program End Date', default=date.today, format='%d/%m/%Y'
                                        )
    
    redeem_reward_format    = StringField('Redeem Reward Format', [
                                        validators.InputRequired(gettext('Redeem Reward Format is required'))
                                        ]
                                        )

class RedemptionCatalogueItemForm(RedemptionCatalogueForm):
    voucher_index             = StringField('Catalogue Item index')    
    
class RedemptionCatalogueItemDetailsForm(RedemptionCatalogueItemForm):
    voucher_key             = StringField('Voucher', [
                                        validators.InputRequired(gettext('Voucher is required'))
                                        ]
                                        )
    
    voucher_amount          = IntegerField('Voucher amount', [
                                        validators.InputRequired(gettext('Voucher amount is required'))
                                        ]
                                        )
    
    redeem_reward_amount    = FloatField('Redeem reward amount', [
                                        validators.InputRequired(gettext('Redeem reward amount is required'))
                                        ]
                                        )
    
    use_online              = CheckBoxField('Is Use Online', [
                                        ], default=False
                                        )
    
    use_in_store            = CheckBoxField('Is Use In Store', [
                                        ], default=False
                                        ) 
    
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Voucher expiration type is required'))
                                        ])
    
    expiration_date        = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = IntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ])
    
    effective_type          = StringField('Effective Type', [
                                        validators.InputRequired(gettext('Voucher effective type is required'))
                                        ])
    
    effective_date          = CustomDateField('Effective Date', [
                                        custom_validator.RequiredIf(gettext('Effective Date is required'), 
                                                                    effective_type=program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    effective_value         = CustomIntegerField('Effective Value', [
                                        custom_validator.RequiredIf(gettext('Effective value is required'), 
                                                                    effective_type=(
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK,
                                                                                    )
                                                                    )
                                        ])
    



class RedemptionCatalogueExclusivityForm(RedemptionCatalogueForm):
    partner_exclusive                   = CheckBoxField('Partner Exclusive', [
                                        ], default=False
                                        )
    
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
