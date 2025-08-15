'''
Created on 25 Aug 2021

@author: jacklok
'''
from wtforms import validators
from trexlib.forms.base_forms import ValidationBaseForm
from flask_babel import gettext
from datetime import date
from trexlib.libs.wtforms.fields import CurrencyField, JSONField
from wtforms.fields.core import BooleanField, StringField
from wtforms.fields.html5 import DateField
from trexlib.libs.wtforms import validators as custom_validator

class PrepaidSetupForm(ValidationBaseForm):
    label                               = StringField('Label', [
                                            validators.DataRequired(message=gettext("Prepaid program label is required")),
                                            validators.Length(max=150)
                                            ]
                                            )
    start_date                          = DateField('Start Date', default=date.today, format='%d/%m/%Y')
    end_date                            = DateField('End Date', default=date.today, format='%d/%m/%Y')
    
    prepaid_settings_key                = StringField('Prepaid Settings key', [])
    is_lump_sum_prepaid                 = BooleanField('Having lump sum topup', [])
    is_multi_tier_prepaid               = BooleanField('Having multi tier topup', [])
    lump_sump_topup_amount              = CurrencyField('Lump sum topup amount',[
                                                custom_validator.RequiredIfOtherFieldValueIsTrue('is_lump_sum_prepaid',
                                                                    message=gettext('Lump sum topup amount is required')
                                                        )
                                            ])
    
    lump_sump_prepaid_amount            = CurrencyField('Lump sum prepaid amount',[
                                                custom_validator.RequiredIfOtherFieldValueIsTrue('is_lump_sum_prepaid',
                                                                    message=gettext('Lump sum prepaid amount is required')
                                                        )
                                            ])
                                        
    multitier_settings                  = JSONField('Multitier Prepaid Settings', [])
    
    
class PrepaidTopupForm(ValidationBaseForm):
    customer_key                        = StringField('Customer Key',[
                                                validators.DataRequired(message="Customer account is required"),
                                            ])
    topup_outlet                        = StringField('Topup Outlet',[
                                                validators.DataRequired(message="Topup Outlet is required"),
                                            ])
    
    prepaid_program                     = StringField('Prepaid program', [
                                            validators.DataRequired(message=gettext("Prepaid program is required")),
                                            ]
                                            )
    
    topup_amount                        = CurrencyField('Topup amount',[
                                                custom_validator.RequiredIfOtherFieldEmpty( 
                                                                    other_empty_field_name_list=['tier_topup_amount'],
                                                                    message=gettext('Topup amount is required'))
                                                        
                                            ])
    
    tier_topup_amount                   = CurrencyField('Tier Topup amount',[
                                                custom_validator.RequiredIfOtherFieldEmpty( 
                                                                    other_empty_field_name_list=['topup_amount'],
                                                                    message=gettext('Tier Topup amount is required'))
                                                        
                                            ])
    
    invoice_id                          = StringField('Invoice Id', [
                                                validators.Length(max=50)
                                            ]
                                            )
    
    remarks                             = StringField('Remarks', [
                                                validators.Length(max=500)
                                            ]
                                            )
    
class PrepaidRedeemSettingsForm(ValidationBaseForm):
    prepaid_redeem_settings_key         = StringField('Settings Key')
    label                               = StringField('Label', [
                                            validators.DataRequired(message=gettext("Prepaid redeem code label is required")),
                                            validators.Length(max=150)
                                            ]
                                            )
    assign_outlet_key                   = StringField(gettext('Assign Outlet'),[
                                                validators.InputRequired(message=gettext("Assign outlet is required")),
                                                
                                            ])
    device_activation_code              = StringField('Device Activation Code', [
                                            validators.Optional(),
                                            validators.Length(max=16)
                                            ]
                                            )