'''
Created on 8 May 2025

@author: jacklok
'''
from wtforms import StringField, validators, BooleanField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from trexlib.libs.wtforms import fields as custom_fields
from datetime import date
from flask_babel import gettext
from wtforms.fields.core import IntegerField, FloatField
from wtforms.fields.simple import HiddenField

class MerchantPartnerForm(ValidationBaseForm):
    partnership_key             = HiddenField('Partnership Key')


class MerchantPartnerDefineForm(MerchantPartnerForm):
    partner_merchant_key        = HiddenField('Merchant Acct Key')
    partner_company_name        = StringField('Merchant name')
    partner_account_code        = StringField('Account Code', [
                                        validators.Length(max=19, message='Account code length must be within 19 characters'),
                                        validators.DataRequired(message="Account Code is required"),
                                        ]
                                        )
    start_date                  = DateField('Start Date',default=date.today, format='%d/%m/%Y')
    end_date                    = DateField('End Date',default=date.today, format='%d/%m/%Y')
    
    desc                        = StringField('Description', [
                                                    validators.Optional(),
                                                    validators.Length(max=1000, message='Description length must be within 1000 characters'),
                                                    ])   
    
class MerchantPartnerConfigurationForm(MerchantPartnerForm):
    redemption_catalogue_list   = StringField(
                                        label=gettext('Redemptin Catalogue'), 
                                        validators = [
                                                        validators.DataRequired(message="Redemptin Catalogue is required"),
                                                    ]
                                        )
    limit_redeem                = BooleanField('Limit redeem')
    
