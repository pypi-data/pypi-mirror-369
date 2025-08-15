'''
Created on 5 Sep 2024

@author: jacklok
'''

from wtforms import StringField, validators, DateField
from trexlib.forms.base_forms import ValidationBaseForm
from flask_babel import gettext
from datetime import date

class MerchantNewsForm(ValidationBaseForm):
    merchant_news_key             = StringField('News Key')


class MerchantNewsSetupForm(MerchantNewsForm):
    label                        = StringField(gettext('Label'),[
                                                validators.DataRequired(message=gettext("Label is required")),
                                                validators.Length(max=200, message=gettext("Label length must not more than 200 characters"))
                                            ])
    
    desc                         = StringField(gettext('Description'),[
                                                validators.Length(max=500, message=gettext("Description length must not more than 500 characters"))
                                            ])
    
    news_text                    = StringField(gettext('Content'),[
                                                validators.Length(max=2000, message=gettext("Content length must not more than 2000 characters"))
                                            ])
    
    start_date                  = DateField(gettext('Start Date'), default=date.today, format='%d/%m/%Y',validators=[
                                                validators.DataRequired(message=gettext("Start Date is required")),
                                            ])
    
    end_date                    = DateField(gettext('End Date'), default=date.today, format='%d/%m/%Y',validators=[
                                                validators.DataRequired(message=gettext("End Date is required")),
                                            ])
