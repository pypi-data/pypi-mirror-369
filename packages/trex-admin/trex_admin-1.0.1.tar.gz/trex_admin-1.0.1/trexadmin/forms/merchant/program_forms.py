'''
Created on 26 Feb 2021

@author: jacklok
'''

from wtforms import StringField, validators, BooleanField, IntegerField
from wtforms.fields.html5 import DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from trexlib.forms.common.common_forms import CheckBoxField, CustomDateField,\
    CustomIntegerField
from datetime import date
from wtforms.fields.core import FloatField
from flask_babel import gettext
from trexconf import program_conf
from trexlib.libs.wtforms.fields import IgnoreChoiceSelectMultipleField,\
    IgnoreChoiceSelectField, JSONField, CurrencyField
from wtforms.validators import Length
from wtforms.fields.simple import HiddenField

class ProgramBaseForm(ValidationBaseForm):
    
    program_key             = HiddenField('Program Key')
    
    

class ProgramRewardBaseForm(ValidationBaseForm):
    reward_base             = StringField('Reward base', [
                                        validators.InputRequired(gettext('Program base is required'))
                                        ]
                                        )
    
class ProgramDetailsForm(ProgramBaseForm):
    reward_base             = StringField('Reward base', [
                                        validators.InputRequired(gettext('Program base is required'))
                                        ]
                                        )
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
    reward_format           = StringField('Program Format', [
                                        validators.InputRequired(gettext('Program format is required'))
                                        ]
                                        )
    
    

class ProgramRewardFormatForm(ProgramBaseForm):
    reward_format           = StringField('Program Format', [
                                        validators.InputRequired(gettext('Program format is required'))
                                        ]
                                        )


class BirthdayRewardInputForm():
    giveaway_birthday_reward_when                   = IgnoreChoiceSelectField(label=gettext('Brithday Reward giveaway when input'), 
                                                                          validators = [
                                                                                        custom_validator.RequiredIf( 
                                                                                            message=gettext('Brithday Reward giveaway when input is required'),
                                                                                            reward_base=(
                                                                                                program_conf.REWARD_BASE_ON_BIRTHDAY
                                                                                                )
                                                                                            )
                                                                                        ]
                                                                    )
    
    giveaway_birthday_reward_advance_in_day         = StringField('No of day in advance', [
                                                         custom_validator.RequiredIf(gettext('No of day in advance is required'), 
                                                                                    giveaway_birthday_reward_when=program_conf.ADVANCE_IN_DAY)
                                                        ]
                                                        )
    
    birthday_wish_as_remarks                        = StringField('Birthday wish as remarks', [
                                                            Length(max=500)
                                                        ]
                                                        )
                        
    

class ProgramGiveawayConditionForm(ProgramBaseForm, BirthdayRewardInputForm, ProgramRewardBaseForm):
    giveaway_method          = StringField('Giveaway Method', [
                                        custom_validator.RequiredIf(gettext('Giveaway method is required'),
                                                                reward_base=(
                                                                        program_conf.REWARD_BASE_ON_GIVEAWAY
                                                                        )
                                                ),
                                        
                                        ]
                                        ) 
    
    giveaway_system_condition  = StringField('Giveaway Condition', [
                                         custom_validator.RequiredIf(gettext('Giveaway condition is required'), 
                                                                    
                                                                    giveaway_method=(
                                                                        program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM
                                                                        )
                                                                    )
                                                                    
                                        ]
                                        )
    
    giveaway_system_condition_value  = StringField('Year of Membership', [
                                         custom_validator.RequiredIf(gettext('Year of Membership is required'), 
                                                                    giveaway_method=program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR)
                                        ]
                                        )
    
    giveaway_system_condition_membership_key        = IgnoreChoiceSelectMultipleField(label=gettext('Basic Membership'), 
                                                                          validators = [
                                                                                        custom_validator.RequiredIfConditionFieldAndOtherFieldsValueIsEmpty( 
                                                                                            other_empty_field_name_list=['giveaway_system_condition_tier_membership_key'],
                                                                                            message=gettext('Either Basic Membership or Tier Membership is required'),
                                                                                            giveaway_method=(
                                                                                                program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM
                                                                                                
                                                                                            ),
                                                                                            giveaway_system_condition=(
                                                                                                program_conf.GIVEAWAY_SYSTEM_CONDITION_NEW_MEMBERSHIP,
                                                                                                program_conf.GIVEAWAY_SYSTEM_CONDITION_RENEW_MEMBERSHIP,
                                                                                                program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR,
                                                                                                )
                                                                                            )
                                                                                        ]
                                                                    )
    
    giveaway_system_condition_tier_membership_key  = IgnoreChoiceSelectMultipleField(label=gettext('Tier Membership'), 
                                                                         validators=[
                                                                                    custom_validator.RequiredIfConditionFieldAndOtherFieldsValueIsEmpty( 
                                                                                        other_empty_field_name_list=['giveaway_system_condition_membership_key'],
                                                                                        message=gettext('Either Basic Membership or Tier Membership is required'),
                                                                                        giveaway_method=(
                                                                                                program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM
                                                                                                
                                                                                            ),
                                                                                        giveaway_system_condition=(
                                                                                            program_conf.GIVEAWAY_SYSTEM_CONDITION_NEW_MEMBERSHIP,
                                                                                            program_conf.GIVEAWAY_SYSTEM_CONDITION_RENEW_MEMBERSHIP,
                                                                                            program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR,
                                                                                            )
                                                                                    )
                                                                                    ]
                                                                    )

class ProgramRewardDetailsBaseForm(ProgramBaseForm, ProgramRewardBaseForm):
    is_recurring_scheme     = BooleanField('Is Recurring Scheme indicator', [
                                        custom_validator.RequiredIf(gettext('Is recurring Scheme indicator is required'), 
                                                                    reward_base=(
                                                                                program_conf.REWARD_BASE_ON_SPENDING,
                                                                                
                                                                                )
                                                                    )
                                        
                                        ],
                                        false_values=('False', 'false', 'off')
                                        )  
    spending_currency       = CurrencyField('Spending Currency', [
                                        custom_validator.RequiredIf(gettext('Spending Currency is required'), 
                                                                    reward_base=(
                                                                                program_conf.REWARD_BASE_ON_SPENDING,
                                                                                
                                                                                )
                                                                    )
                                        ]
                                        )  
    
    reward_limit_type       = StringField('Reward Limit', [
                                        custom_validator.RequiredIf(gettext('Is recurring Scheme indicator is required'), 
                                                                    reward_base=(
                                                                                program_conf.REWARD_BASE_ON_SPENDING,
                                                                                
                                                                                )
                                                                    )
                                        ])
    
    reward_limit_amount     = CurrencyField('Maximum Reward amount', [
                                        custom_validator.RequiredIf(gettext('Maximum Reward amount is required'), 
                                                                    reward_limit_type=(
                                                                        
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_MONTH,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_WEEK,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_DAY,
                                                                                program_conf.REWARD_LIMIT_TYPE_BY_TRANSACTION, 
                                                                                )
                                                                    )
                                        ])
    
    
class ProgramPrepaidRewardForm(ProgramBaseForm):
    prepaid_amount          = CurrencyField('Prepaid Amount', [
                                        validators.InputRequired(gettext('Prepaid amount is required'))
                                        ])
    
class ProgramPointRewardForm(ProgramBaseForm):
    point_amount            = CurrencyField('Point Amount', [
                                        validators.InputRequired(gettext('Point amount is required'))
                                        ])  
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Point expiration type is required'))
                                        ])
    
    expiration_date         = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = CustomIntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ], default=0) 
    
class ProgramStampRewardForm(ProgramBaseForm):
    stamp_amount            = IntegerField('Stamp Amount', [
                                        validators.InputRequired(gettext('Stamp amount is required'))
                                        ])  
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Stamp expiration type is required'))
                                        ])
    
    expiration_date        = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = CustomIntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ], default=0)      

class ProgramVoucherRewardForm(ProgramBaseForm):
    voucher_key             = StringField('Voucher Key', [
                                        validators.InputRequired(gettext('Voucher data is required'))
                                        ])
    voucher_amount          = IntegerField('Voucher Amount', [
                                        validators.InputRequired(gettext('Voucher amount is required'))
                                        ])
    
    use_online              = CheckBoxField('Is Use Online', [
                                        ], default=False
                                        )
    
    use_in_store            = CheckBoxField('Is Use In Store', [
                                        ], default=False
                                        )
    
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Voucher expiration type is required'))
                                        ])
    
    expiration_date        = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = CustomIntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ], default=0)
    
    effective_type          = StringField('Effective Type', [
                                        validators.InputRequired(gettext('Voucher effective type is required'))
                                        ])
    
    effective_date        = CustomDateField('Effective Date', [
                                        custom_validator.RequiredIf(gettext('Effective Date is required'), 
                                                                    effective_type=program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    effective_value        = CustomIntegerField('Effective Value', [
                                        custom_validator.RequiredIf(gettext('Effective value is required'), 
                                                                    effective_type=(
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK,
                                                                                    )
                                                                    )
                                        ], default=1)
    
class LuckyDrawProgramBasicRewardDetailsForm(ProgramBaseForm):
    reward_amount           = IntegerField('Reward amount', [
                                        
                                        ]
                                        )    
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Voucher expiration type is required'))
                                        ])
    
    expiration_date         = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = IntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ])
    
class LuckyDrawProgramPrepaidDetailsForm(ProgramBaseForm):
    reward_amount           = FloatField('Reward amount', [
                                        
                                        ]
                                        )
    
class LuckyDrawProgramMessageForm(ProgramBaseForm):
    text         = StringField('Message text', [
                                        validators.InputRequired(gettext('Message text is required'))
                                        ])        

class ProgramLimitToDateInputForm():
    limit_to_specific_day     = BooleanField('Limit to specified day', [
                                        ],
                                        false_values=('False', 'false', 'off')
                                        )
    
    specified_days_list       = StringField('Specified day', [
                                        custom_validator.RequiredIf(gettext('Specified day is required'), 
                                                                    limit_to_specific_day=True
                                                                    )
                                        ])
    
    limit_to_specific_date_of_month     = BooleanField('Limit to specified date of month', [
                                        ],
                                        false_values=('False', 'false', 'off')
                                        )
    
    specified_dates_of_month_list       = StringField('Specified date of month', [
                                        custom_validator.RequiredIf(gettext('Specified date of month is required'), 
                                                                    limit_to_specific_date_of_month=True
                                                                    )
                                        ])
    

class ProgramBasicRewardDetailsForm(ProgramRewardDetailsBaseForm, ProgramGiveawayConditionForm, ProgramLimitToDateInputForm):
    reward_amount           = CurrencyField('Reward amount', [
                                        
                                        ]
                                        )    
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Reward expiration type is required'))
                                        ])
    
    expiration_date         = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = IntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ])
    
    
    
class PrepaidDetailsForm(ProgramRewardDetailsBaseForm, ProgramGiveawayConditionForm, BirthdayRewardInputForm, ProgramLimitToDateInputForm):
    reward_amount           = FloatField('Prepaid amount', [
                                        
                                        ]
                                        )    
    
    
class ProgramVoucherRewardDetailsForm(ProgramRewardDetailsBaseForm, ProgramGiveawayConditionForm, BirthdayRewardInputForm, ProgramLimitToDateInputForm):
    pass

class ProgramExclusivityForm(ProgramBaseForm):
    giveaway_system_condition           = StringField('Giveaway Condition', [
                                            validators.InputRequired(gettext('Giveaway Condition is required'))
                                        ])
    
    giveaway_system_condition_value     = StringField('Giveaway Condition', [
                                            custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    giveaway_system_condition=(
                                                                                        program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR,
                                                                                        
                                                                                    )
                                                                    )
                                        
                                        ])
    
    tags_list                           = StringField('Tagging', [
                                        ])
    
    promotion_codes_list                = StringField('Promotion Codes', [
                                        ])
    
    membership_key                      = StringField(
                                            label='Membership', 
                                                validators=[
                                        
                                                ]
                                            )
    
    tier_membership_key                 = StringField(
                                            label='Tier Membership', 
                                            validators=[
                                        
                                            ]
                                            )

class TierRewardProgramDetailsForm(ProgramBaseForm):
    program_label           = StringField('Label', [
                                            Length(max=300)
                                        ]
                                        )
    
    reward_format           = StringField('Reward Format', [
                                        validators.InputRequired(gettext('Reward format is required'))
                                        ]
                                        )
    
    start_date              = DateField('Program Start Date', default=date.today, format='%d/%m/%Y')
    end_date                = DateField('Program End Date', default=date.today, format='%d/%m/%Y')
    desc                    = StringField('Description', [
                                            Length(max=500)
                                        ]
                                        )
    is_tier_recycle         = BooleanField('Is Tier Recycle indicator', [
                                        ]
                                        )
    
    is_show_progress        = BooleanField('Show Tier Reward Progress', [
                                        ]
                                        )


class DefineTierRewardProgramTierForm(ProgramBaseForm):
    program_tier_settings                  = JSONField('Program Tier Settings', [])
    
class DefineTierRewardProgramRewardForm(ProgramBaseForm):
    pass    

class AddProgramTierForm(ProgramBaseForm):
    tier_label                      = StringField('Tier Label', [
                                            validators.InputRequired(gettext('Tier label is required')),
                                            Length(max=300)
                                        ]
                                        )
    
    unlock_tier_message             = StringField('Unlock tier message', [
                                            validators.InputRequired(gettext('Unlock tier message is required')),
                                            Length(max=500)
                                        ]
                                        )
    
    unlock_tier_condition           = StringField('Unlock tier condition', [
                                            validators.InputRequired(gettext('Unlock tier condition is required')),
                                        ]
                                        )
    
    unlock_tier_condition_value     = IntegerField('Unlock tier condition value', [
                                            validators.InputRequired(gettext('Unlock tier condition value is required')),
                                        ]
                                        )
    

class AddProgramRewardForm(ProgramBaseForm):    
    program_tier                      = StringField('Program Tier', [
                                            validators.InputRequired(gettext('Program Tier is required')),
                                            Length(max=300)
                                        ]
                                        )
    
    reward_format           = HiddenField('Reward Format', [
                                        ]
                                        )
    
    voucher_key             = StringField('Data Key', [
                                        custom_validator.RequiredIf(gettext('Vourcher data is required'), 
                                                                    reward_format=(
                                                                                        program_conf.REWARD_FORMAT_VOUCHER
                                                                                    )
                                                                    )
                                        ])
    voucher_amount          = IntegerField('Voucher Amount', [
                                        custom_validator.RequiredIf(gettext('Voucher amount is required'), 
                                                                    reward_format=(
                                                                                        program_conf.REWARD_FORMAT_VOUCHER
                                                                                    )
                                                                    )
                                        ])
    
    use_online              = CheckBoxField('Is Use Online', [
                                        custom_validator.RequiredIf(gettext('Voucher amount is required'), 
                                                                    reward_format=(
                                                                                        program_conf.REWARD_FORMAT_VOUCHER
                                                                                    )
                                                                    )
                                            
                                        ], default=False
                                        )
    
    use_in_store            = CheckBoxField('Is Use In Store', [
                                        custom_validator.RequiredIf(gettext('Voucher amount is required'), 
                                                                    reward_format=(
                                                                                        program_conf.REWARD_FORMAT_VOUCHER
                                                                                    )
                                                                    )
        
                                        ], default=False
                                        )
    
    expiration_type         = StringField('Expiration Type', [
                                        validators.InputRequired(gettext('Voucher expiration type is required'))
                                        ])
    
    expiration_date        = CustomDateField('Expiration Date', [
                                        custom_validator.RequiredIf(gettext('Expiration Date is required'), 
                                                                    expiration_type=program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    expiration_value        = IntegerField('Expiration Value', [
                                        custom_validator.RequiredIf(gettext('Expiration value is required'), 
                                                                    expiration_type=(
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR
                                                                                    )
                                                                    )
                                        ])
    
    effective_type          = StringField('Effective Type', [
                                        validators.InputRequired(gettext('Voucher effective type is required'))
                                        ])
    
    effective_date        = CustomDateField('Effective Date', [
                                        custom_validator.RequiredIf(gettext('Effective Date is required'), 
                                                                    effective_type=program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE)
                                        ],
                                        format='%d/%m/%Y')
    
    effective_value        = CustomIntegerField('Effective Value', [
                                        custom_validator.RequiredIf(gettext('Effective value is required'), 
                                                                    effective_type=(
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH,
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY,
                                                                                        program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK,
                                                                                    )
                                                                    )
                                        ])