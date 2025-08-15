'''
Created on 24 May 2021

@author: jacklok
'''

from wtforms import StringField, validators, DateTimeField, IntegerField
from trexlib.forms.base_forms import ValidationBaseForm
from flask_babel import gettext
from trexlib.libs.wtforms.fields import OptionalDateTimeField

class GiveawayRewardForm(ValidationBaseForm):
    customer_key                   = StringField(gettext('Customer Key'),[
                                                validators.DataRequired(message=gettext("Customer Key is required")),
                                            ])
    
    giveaway_reward_program        = StringField(gettext('Giveaway Program'), [
                                        validators.DataRequired(message=gettext("Giveaway Program is required")),
                                        ]
                                        )
    reward_set_count               = IntegerField(gettext('Reward Set Count'), [
                                        validators.DataRequired(message=gettext("Reward Set Count is required")),
                                        
                                        ]
                                        )
    
    giveaway_outlet             = StringField(gettext('Giveaway Outlet'), [
                                        validators.DataRequired(message=gettext("Giveaway Outlet is required")),
                                        
                                        ]
                                        )
    
    giveaway_reward_datetime       = OptionalDateTimeField(gettext('Giveaway Reward Datetime'), format='%d/%m/%Y %H:%M')
    
    remarks                         = StringField('Remarks',[
                                                validators.Length(max=300, message="Remarks length must not more than 300 characters")
                                            ])
