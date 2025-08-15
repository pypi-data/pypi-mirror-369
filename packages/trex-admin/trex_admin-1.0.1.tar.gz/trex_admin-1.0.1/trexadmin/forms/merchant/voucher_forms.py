'''
Created on 10 Mar 2021

@author: jacklok
'''
from wtforms import StringField, validators, IntegerField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from wtforms.fields.core import FloatField
from flask_babel import gettext
from wtforms.fields.simple import HiddenField
from trexmodel import program_conf

class VoucherForm(ValidationBaseForm):
    voucher_key             = StringField('Voucher Key')


class VoucherBaseForm(VoucherForm):
    voucher_label           = StringField('Voucher Label', [
                                        validators.InputRequired(gettext('Voucher label is required'))
                                        ]
                                        )
    
    voucher_type            = StringField('Voucher Type', [
                                        validators.InputRequired(gettext('Voucher type is required'))
                                        ]
                                        )
    
    desc                    = StringField('Voucher Description', [
                                        
                                        ]
                                        )
    
    terms_and_conditions    = StringField('Voucher Terms & Conditions', [
                                        
                                        ]
                                        )
    
    redeem_limit_type    = StringField('Redeem Limit Type', [
                                        validators.InputRequired(gettext('Redeem Limit Type is required'))
                                        ]
                                        )
    
    redeem_limit_count   = IntegerField('Redeem Limit Count', [
                                        ]
                                        )
    

class VoucherConfigurationForm(VoucherForm):
    voucher_key             = HiddenField('Voucher Key', [
                                        ]
                                        )
    
    voucher_type            = HiddenField('Voucher Type', [
                                        ]
                                        )
    
    cash_amount             = FloatField('Cash Amount', [
                                        custom_validator.RequiredIf(gettext('Cash Amount is required'), 
                                                                                    voucher_type=program_conf.VOUCHER_REWARD_TYPE_CASH)
                                        ]
                                        )
    
    discount_rate           = FloatField('Discount Rate', [
                                        custom_validator.RequiredIf(gettext('Discount Rate is required'), 
                                                                                    voucher_type=program_conf.VOUCHER_REWARD_TYPE_DISCOUNT),
                                        validators.NumberRange(min=0, max=100),
                                        ]
                                        )
    
    product_category        = StringField('Product Category', [
                                        custom_validator.RequiredIf(gettext('Product Category is required'), 
                                                                                    voucher_type=program_conf.VOUCHER_REWARD_TYPE_PRODUCT)
                                        ]
                                        )
    
    product_sku             = StringField('Product SKU', [
                                        custom_validator.RequiredIf(gettext('Product SKU is required'), 
                                                                                    voucher_type=program_conf.VOUCHER_REWARD_TYPE_PRODUCT)
                                        ]
                                        )
    
    min_sales_amount        = FloatField('Minimum Sales Amount', [
                                        
                                        ]
                                        )
    
    product_price           = FloatField('Product Price', [
                                        
                                        ]
                                        )
    
    max_quantity             = IntegerField('Maximum quantity', [
                                        ]
                                        )
    
    
    
    
    
    
    
    
