'''
Created on 31 Mar 2021

@author: jacklok
'''

from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from trexlib.libs.wtforms.fields import OptionalDateTimeField, CurrencyField

class CustomerTransactionSearchForm(ValidationBaseForm):
    name                = StringField('Name', [
                                        validators.Optional(),
                                        validators.Length(min=3, max=300, message='Name length must be within 3 and 300 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'merchant_tagging', 'reference_code', 'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    email               = StringField('Email Address', [
                                        validators.Optional(),
                                        validators.Email("Please enter valid email address."),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['name', 'mobile_phone', 'merchant_tagging', 'reference_code', 
                                                         'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        
                                        ]
                                        )
    
    mobile_phone        = StringField('Mobile Phone', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['name', 'email', 'merchant_tagging', 'reference_code', 
                                                         'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        
                                        ]
                                        )
    
    merchant_tagging    = StringField('Tagging', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'reference_code', 
                                                         'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    
    reference_code                = StringField('Reference code', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'merchant_reference_code', 
                                                         'merchant_tagging', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(max=16, message="Reference code length must not more than 16 characters")
                                        ]
                                        )
    
    merchant_reference_code       = StringField('Member code', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'reference_code', 'merchant_tagging', 
                                                         'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(max=16, message="Member code length must not more than 16 characters")
                                        ]
                                        )
    
class CustomerTransactionDetailsForm(ValidationBaseForm):
    customer_key                    = StringField('Customer Key',[
                                                validators.DataRequired(message="Customer Key is required"),
                                            ])
    
    transact_outlet                 = StringField('Transact Outlet',[
                                                validators.DataRequired(message="Transact Outlet is required"),
                                            ])
    
    transact_amount                 = CurrencyField('Transact Amount',[
                                                validators.DataRequired(message="Transact Amount is required"),
                                            ])
    
    tax_amount                      = CurrencyField('Transact Tax Amount',[
                                                
                                            ])  
    
    invoice_id                      = StringField('Invoice No',[
                                                validators.Length(max=30, message="Invoice No length must not more than 30 characters")
                                            ])
    
    promotion_code                  = StringField('Promotion Code',[
                                                validators.Length(max=30, message="Promotion Code length must not more than 30 characters")
                                            ])
    
    remarks                         = StringField('Remarks',[
                                                validators.Length(max=300, message="Remarks length must not more than 300 characters")
                                            ])
    
    transact_datetime               = OptionalDateTimeField('Transact Datetime', format='%d/%m/%Y %H:%M')  
    
    
    
