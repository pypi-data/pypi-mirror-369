from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from wtforms.fields.simple import HiddenField
from flask_babel import gettext


class LuckyDrawSetupForm(ValidationBaseForm):
    lucky_draw_key             = HiddenField('Lucky Draw Key')
    

    label                      = StringField('Name of Draw', [
                                        validators.InputRequired(gettext('Name of Draw is required'))
                                        ]
                                        )    
