'''
Created on 2 Nov 2020

@author: jacklok
'''

from wtforms import IntegerField, validators
from trexlib.forms.base_forms import ValidationBaseForm

class PaymentForm(ValidationBaseForm):
    payment_amount      = IntegerField('Payment Amoiunt', [
                                        validators.DataRequired(message="Payment amount is required"),
                                        
                                        ]
                                        )
