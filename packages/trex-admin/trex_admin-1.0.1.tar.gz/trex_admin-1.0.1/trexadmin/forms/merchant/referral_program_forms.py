'''
Created on 9 Apr 2024

@author: jacklok
'''

from wtforms import StringField, validators
from wtforms.fields.html5 import DateField
from trexlib.forms.base_forms import ValidationBaseForm
from datetime import date
from flask_babel import gettext
from wtforms.validators import Length
from wtforms.fields.simple import HiddenField

class ProgramBaseForm(ValidationBaseForm):
    
    program_key             = HiddenField('Program Key')

class ReferralProgramDetailsForm(ProgramBaseForm):
    label                    = StringField('Label', [
                                        validators.InputRequired(gettext('Program Label is required')),
                                        Length(max=100)
                                        ]
                                        )
    start_date              = DateField('Program Start Date', default=date.today, format='%d/%m/%Y')
    end_date                = DateField('Program End Date', default=date.today, format='%d/%m/%Y')
    desc                    = StringField('Description', [
                                        ]
                                        )
    
class ReferralProgramPromoteTextForm(ValidationBaseForm):
    promote_title           = StringField('Promote Title', [
                                        validators.InputRequired(gettext('Promote title is required')),
                                        Length(max=500)
                                        ]
                                        )
    promote_desc           = StringField('Promote Description', [
                                        validators.InputRequired(gettext('Promote Description is required')),
                                        Length(max=3000)
                                        ]
                                        )
    