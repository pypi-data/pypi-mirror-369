'''
Created on 28 May 2021

@author: jacklok
'''
from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from trexlib.libs.wtforms.fields import OptionalDateTimeField
from trexmodel import program_conf
from wtforms.fields.core import FloatField

class RedeemRewardForm(ValidationBaseForm):
    customer_key                    = StringField(gettext('Customer Key'),[
                                                validators.InputRequired(message=gettext("Customer Key is required")),
                                            ])
    
    reward_format                   = StringField(gettext('Reward Type'),[
                                                validators.InputRequired(message=gettext("Reward Type is required")),
                                            ])
    
    redeem_voucher                  = StringField(
                                        label=gettext('Redeem Voucher'), 
                                        validators = [
                                                        custom_validator.RequiredIf(gettext('Redeem Voucher is required'), 
                                                                    reward_format=program_conf.REWARD_FORMAT_VOUCHER)
                                                    ]
                                        )
    redeem_amount                   = FloatField(gettext('Redeem Amount'), [
                                        custom_validator.RequiredIf(gettext('Redeem amount is required'), 
                                                                    reward_format=[
                                                                                    program_conf.REWARD_FORMAT_POINT,
                                                                                    program_conf.REWARD_FORMAT_STAMP
                                                                                    ])
                                        
                                        ]
                                        )
    
    redeemed_outlet                 = StringField(gettext('Redeem Outlet'), [
                                        validators.InputRequired(message=gettext("Redeem Outlet is required")),
                                        
                                        ]
                                        )
    
    redeemed_datetime               = OptionalDateTimeField(gettext('Redeem Datetime'), format='%d/%m/%Y %H:%M')
    #redeemed_datetime               = DateTimeField(gettext('Redeem Datetime'), format='%d/%m/%Y %H:%M')
    
    remarks                         = StringField('Remarks',[
                                                validators.Optional(),
                                                validators.Length(max=1000, message="Remarks length must not more than 1000 characters")
                                            ])
    
    invoice_id                      = StringField('Invoice Id',[
                                                validators.Optional(),
                                                validators.Length(max=30, message="Invoice Id length must not more than 30 characters")
                                            ])
