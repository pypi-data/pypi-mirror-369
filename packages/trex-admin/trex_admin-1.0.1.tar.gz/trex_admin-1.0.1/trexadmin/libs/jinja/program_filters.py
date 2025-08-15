'''
Created on 30 Mar 2021

@author: jacklok
'''
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_preferred_language, get_merchant_configured_currency_details
from trexadmin.controllers.system.system_routes import get_program_status_json, get_reward_base_json, get_reward_format_json,\
    get_reward_effective_type_json, get_reward_expiration_type_json,\
    get_giveaway_method_json, get_giveaway_system_condition_json,\
    get_entitle_reward_condition_list
from trexlib.utils.common.currency_util import format_currency as currency_formatting
from datetime import datetime
from trexadmin.controllers.system.system_route_helpers import get_reward_format_label,\
    get_redeem_reward_format_json, get_redemption_catalogue_status_json
import logging
from trexlib.utils.string_util import is_not_empty
from trexconf import program_conf

#logger = logging.getLogger('debug')
logger = logging.getLogger('target_debug')

def map_label_by_code(code_label_json, code):
    for rb in code_label_json:
        if rb.get('code')==code:
            return rb.get('label')

def program_completed_status_label(program_completed_status_code):
    if program_completed_status_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_program_status_json(preferred_language)
        return map_label_by_code(code_label_json, program_completed_status_code)
    else:
        return ''
    
def program_reward_base_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_reward_base_json(preferred_language)
        
        return map_label_by_code(code_label_json, code) or '-'
    else:
        return ''

def program_reward_format_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_reward_format_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''
    
def redeem_reward_format_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_redeem_reward_format_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''    

def program_giveaway_method_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_giveaway_method_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return gettext('System')    

def program_giveaway_system_condition_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_giveaway_system_condition_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''

def program_voucher_effective_type_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_reward_effective_type_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''

def program_voucher_expiration_type_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_reward_expiration_type_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''

def program_voucher_effective_value_label(voucher_settings):
    effective_type  = voucher_settings.get('effective_type')
    effective_date  = voucher_settings.get('effective_date')
    effective_value = voucher_settings.get('effective_value')
    
    if effective_type:
        if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY:
            return gettext('Effective after {effective_value} days').format(effective_value=effective_value)
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH:
            return gettext('Effective after {effective_value} months').format(effective_value=effective_value)
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK:
            return gettext('Effective after {effective_value} weeks').format(effective_value=effective_value)
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_IMMEDIATE:
            return gettext('Effective immediately').format(effective_value=effective_value)
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE:
            effective_date_in_date = datetime.strptime(effective_date, '%d-%m-%Y')
            return gettext('Effective on {effective_date}').format(effective_date=effective_date_in_date.strftime('%d %b %Y'))
    else:
        return '' 

def program_reward_expiration_value_label(reward_settings): 
    
    expiration_type  = reward_settings.get('expiration_type')
    expiration_date  = reward_settings.get('expiration_date')
    expiration_value = reward_settings.get('expiration_value')
    
    if expiration_type:
        if expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY:
            return gettext('Expired after {expiration_value} days').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH:
            return gettext('Expired after {expiration_value} months').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK:
            return gettext('Expired after {expiration_value} weeks').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR:
            return gettext('Expired after {expiration_value} years').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE:
            return gettext('Expired after {expiration_date}').format(expiration_date=expiration_date)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_END_OF_MONTH: 
            return gettext('Expired after end of month')
    else:
        return '' 

def birthday_reward_giveaway_details_filter(program):
    if program.get('program_settings') and program.get('program_settings').get('scheme'):
        if program.get('program_settings').get('scheme').get('giveaway_when') == program_conf.ADVANCE_IN_DAY:
            return gettext('In advance %s days' % (program.get('program_settings').get('scheme').get('advance_in_day') or 0))
        elif program.get('program_settings').get('scheme').get('giveaway_when') == program_conf.FIRST_DAY_OF_MONTH:
            return gettext('On first day of birthday month')
        elif program.get('program_settings').get('scheme').get('giveaway_when') == program_conf.ON_DOB_DATE:
            return gettext('On date of birth')
        

def program_reward_limit_brief_filter(program):
    program_settings    = program.get('program_settings')
    
    if program_settings:
        reward_format       = program.get('reward_format')
        program_scheme      = program_settings.get('scheme')
        if program_scheme:
            reward_limit_type   = program_scheme.get('reward_limit_type')
            reward_limit_amount = program_scheme.get('reward_limit_amount')
            
            logger.debug('reward_limit_type=%reward_limit_type')
            logger.debug('reward_limit_amount=%reward_limit_amount')
            
            if reward_limit_type and reward_limit_amount:
                preferred_language  = get_preferred_language()
                reward_format_label = get_reward_format_label(reward_format, preferred_language)
                
                if reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_TRANSACTION:
                    return gettext('Limit %d %s per transation') % (reward_limit_amount, reward_format_label)
                elif reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_MONTH:
                    return gettext('Limit %d %s per month') % (reward_limit_amount, reward_format_label)
                elif reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_WEEK:
                    return gettext('Limit %d %s per week') % (reward_limit_amount, reward_format_label)
                elif reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_DAY:
                    return gettext('Limit %d %s per day') % (reward_limit_amount, reward_format_label) 
    
    return gettext('No Limit')
        
def program_reward_limit_type_label_filter(program):
    program_settings    = program.get('program_settings')
    
    if program_settings:
        reward_format       = program.get('reward_format')
        program_scheme      = program_settings.get('scheme')
        if program_scheme:
            reward_limit_type   = program_scheme.get('reward_limit_type')
            
            if reward_limit_type:
                preferred_language  = get_preferred_language()
                reward_format_label = get_reward_format_label(reward_format, preferred_language)
                
                if reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_MONTH:
                    return gettext('Month')
                elif reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_WEEK:
                    return gettext('Week')
                elif reward_limit_type==program_conf.REWARD_LIMIT_TYPE_BY_DAY:
                    return gettext('Day') 
    
    return gettext('No Limit')        
    
def program_reward_scheme_details(program):
    preferred_language  = get_preferred_language()
    program_settings    = program.get('program_settings')
    reward_base         = program.get('reward_base')
    spending_currency   = .0
    reward_amount       = 0
    reward_format       = None
    is_recurring_scheme = False
    
    if program_settings:
        
        reward_format       = program.get('reward_format')
        program_scheme      = program_settings.get('scheme')
        
        logger.debug('program_scheme=%s', program_scheme)
        
        if reward_base in  program_conf.SCHEME_BASED_PROGRAM or reward_base in (program_conf.REWARD_BASE_ON_GIVEAWAY):
            logger.debug('going to get scheme details')
            if is_not_empty(program_scheme):
                is_recurring_scheme = program_scheme.get('is_recurring_scheme')
                spending_currency   = program_scheme.get('spending_currency')
                reward_amount       = program_scheme.get('reward_amount')
        
        logger.debug('reward_amount=%s', reward_amount)
                
    if reward_format:    
        reward_format_label = get_reward_format_label(reward_format, preferred_language)
        
        currency_details                =  get_merchant_configured_currency_details()
        
        formatted_spending_currency     =  currency_formatting(spending_currency, 
                                                currency_label          = currency_details.get('currency_label'),
                                                floating_point          = currency_details.get('floating_point'),
                                                decimal_separator       = currency_details.get('decimal_separator'),
                                                thousand_separator      = currency_details.get('thousand_separator'),
                                                show_thousand_separator = True, 
                                                show_currency_label     = True)
        
        if reward_base in (program_conf.REWARD_BASE_ON_GIVEAWAY, program_conf.REWARD_BASE_ON_BIRTHDAY):
            
            
            if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                return gettext('Giveaway {reward_format_label}(s)').format(
                                                                                                reward_format_label         = reward_format_label
                                                                                                )
            else:
                
                return gettext('Giveaway {reward_amount} {reward_format_label}(s)').format(
                                                                                                reward_amount               = reward_amount,
                                                                                                reward_format_label         = reward_format_label,
                                                                                                )
                
        else:
            is_recurring_or_one_time = gettext('Recurring') 
            if not is_recurring_scheme:
                is_recurring_or_one_time = gettext('One Time')
            
            if reward_amount:
                return gettext('Entitle {reward_amount} {reward_format_label}(s) for every {formatted_spending_currency} spending ({is_recurring_or_one_time})').format(
                                                                                                reward_amount               = reward_amount,
                                                                                                reward_format_label         = reward_format_label,
                                                                                                formatted_spending_currency = formatted_spending_currency,
                                                                                                is_recurring_or_one_time    = is_recurring_or_one_time
                                                                                                ) 
            else:
                if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                    return gettext('Entitle {reward_format_label} for every {formatted_spending_currency} spending ({is_recurring_or_one_time})').format(
                                                                                                reward_format_label = reward_format_label,
                                                                                                formatted_spending_currency = formatted_spending_currency,
                                                                                                is_recurring_or_one_time    = is_recurring_or_one_time
                                                                                                    )
        
    else:
        return '-'

def program_expiration_details(program):
    program_settings    = program.get('program_settings')
    reward_format       = program.get('reward_format')
    expiration_label    = ''
    
    if reward_format == program_conf.REWARD_FORMAT_VOUCHER:
        expiration_label = gettext('Based on voucher expiration settings')
    
    elif program_settings:
        program_scheme_configuration = program_settings.get('scheme')
        
        if program_scheme_configuration:
            expiration_type     = program_scheme_configuration.get('expiration_type')
            expiration_value    = program_scheme_configuration.get('expiration_value')
            expiration_date     = program_scheme_configuration.get('expiration_date')
            
            if expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE:
                expiration_label = gettext('Expired after {expiration_value}').format(expiration_value=expiration_date)
            elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR:
                expiration_label = gettext('Expired after {expiration_value} year(s)').format(expiration_value=expiration_value)
            elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH:
                expiration_label = gettext('Expired after {expiration_value} month(s)').format(expiration_value=expiration_value)
            elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK:
                expiration_label = gettext('Expired after {expiration_value} week(s)').format(expiration_value=expiration_value)
            elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY:
                expiration_label = gettext('Expired after {expiration_value} day(s)').format(expiration_value=expiration_value)
        
    return expiration_label

def expiration_settings_details_filter(expiration_settings):
    expiration_label    = ''
    if expiration_settings:
        expiration_type     = expiration_settings.get('expiration_type')
        expiration_value    = expiration_settings.get('expiration_value')
        expiration_date     = expiration_settings.get('expiration_date')
        
        if expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE:
            expiration_label = gettext('Expired after {expiration_value}').format(expiration_value=expiration_date)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR:
            expiration_label = gettext('Expired after {expiration_value} year(s)').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH:
            expiration_label = gettext('Expired after {expiration_value} month(s)').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK:
            expiration_label = gettext('Expired after {expiration_value} week(s)').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY:
            expiration_label = gettext('Expired after {expiration_value} day(s)').format(expiration_value=expiration_value)
            
        
    return expiration_label

def effective_settings_details_filter(effective_settings):
    effective_label    = ''
    
    effective_type     = effective_settings.get('effective_type')
    effective_value    = effective_settings.get('effective_value')
    effective_date     = effective_settings.get('effective_date')
    
    if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE:
        effective_label = gettext('Effective on {effective_date}').format(effective_date=effective_date)
    elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_IMMEDIATE:
        effective_label = gettext('Effective immediately')
    elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH:
        effective_label = gettext('Effective after {effective_value} month(s)').format(effective_value=effective_value)
    elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK:
        effective_label = gettext('Effective after {effective_value} week(s)').format(effective_value=effective_value)
    elif effective_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY:
        effective_label = gettext('Effective after {effective_value} day(s)').format(effective_value=effective_value)
        
    return effective_label

def membership_expiration_details_filter(membership):
    expiration_label    = ''
    expiration_type     = membership.get('expiration_type')
    
    if expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_NO_EXPIRY:
        expiration_label = gettext('No expiry')
    
    else:
        expiration_value    = membership.get('expiration_value')
        expiration_date     = membership.get('expiration_date')
        
        if expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_SPECIFIC_DATE:
            expiration_label = gettext('Expired after {expiration_value}').format(expiration_value=expiration_date)
        elif expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_YEAR:
            expiration_label = gettext('Expired after {expiration_value} year(s)').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_MONTH:
            expiration_label = gettext('Expired after {expiration_value} month(s)').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_WEEK:
            expiration_label = gettext('Expired after {expiration_value} week(s)').format(expiration_value=expiration_value)
        elif expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_DAY: 
            expiration_label = gettext('Expired after {expiration_value} day(s)').format(expiration_value=expiration_value)    
        
    return expiration_label

def giveaway_method_label_fitler(giveaway_method):
    if giveaway_method == program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_AUTO:
        return gettext('Auto')
    elif giveaway_method == program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_MANUAL:
        return gettext('Manual')

def membership_entitle_qualification_details_filter(membership):
    entitle_qualification_label    = ''
    entitle_qualification_type     = membership.get('entitle_qualification_type')
    
    entitle_qualification_value    = membership.get('entitle_qualification_value')
    
    currency_details                =  get_merchant_configured_currency_details()
        
    if entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_SPENDING_AMOUNT:
        
        formatted_spending_currency     =  currency_formatting(entitle_qualification_value, 
                                                currency_label          = currency_details.get('currency_label'),
                                                floating_point          = currency_details.get('floating_point'),
                                                decimal_separator       = currency_details.get('decimal_separator'),
                                                thousand_separator      = currency_details.get('thousand_separator'),
                                                show_thousand_separator = True, 
                                                show_currency_label     = True)
        
        entitle_qualification_label = gettext('Entitle when accumulated spending {entitle_qualification_value}').format(entitle_qualification_value=formatted_spending_currency)
    
    elif entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_POINT_AMOUNT:
        
        formatted_value     =  currency_formatting(entitle_qualification_value, 
                                                currency_label          = currency_details.get('currency_label'),
                                                floating_point          = currency_details.get('floating_point'),
                                                decimal_separator       = currency_details.get('decimal_separator'),
                                                thousand_separator      = currency_details.get('thousand_separator'),
                                                show_thousand_separator = True, 
                                                show_currency_label     = False)
        
        entitle_qualification_label = gettext('Entitle when accumulated {entitle_qualification_value} point(s)').format(entitle_qualification_value=formatted_value)
    
    elif entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_STAMP_AMOUNT: 
        
        formatted_value     =  currency_formatting(entitle_qualification_value, 
                                                currency_label          = currency_details.get('currency_label'),
                                                floating_point          = currency_details.get('floating_point'),
                                                decimal_separator       = currency_details.get('decimal_separator'),
                                                thousand_separator      = currency_details.get('thousand_separator'),
                                                show_thousand_separator = True, 
                                                show_currency_label     = False)
        
        entitle_qualification_label = gettext('Entitle when accumulated {entitle_qualification_value} stamp(s)').format(entitle_qualification_value=formatted_value)
    elif entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_AUTO_ASSIGN:
        entitle_qualification_label = gettext('Auto Assign')
        
    '''
    elif entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_SPENDING_AMOUNT:
        
        formatted_spending_currency     =  currency_formatting(entitle_qualification_value, 
                                                currency_label          = currency_details.get('currency_label'),
                                                floating_point          = currency_details.get('floating_point'),
                                                decimal_separator       = currency_details.get('decimal_separator'),
                                                thousand_separator      = currency_details.get('thousand_separator'),
                                                show_thousand_separator = True, 
                                                show_currency_label     = True)
        
        entitle_qualification_label = gettext('Entitle when spending exceeded {entitle_qualification_value} in single receipt').format(entitle_qualification_value=formatted_spending_currency)

    
    elif entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_RELOAD_AMOUNT:
        formatted_spending_currency     =  currency_formatting(entitle_qualification_value, 
                                                currency_label          = currency_details.get('currency_label'),
                                                floating_point          = currency_details.get('floating_point'),
                                                decimal_separator       = currency_details.get('decimal_separator'),
                                                thousand_separator      = currency_details.get('thousand_separator'),
                                                show_thousand_separator = True, 
                                                show_currency_label     = True)
        
        entitle_qualification_label = gettext('Entitle when reloaded exceed {entitle_qualification_value} in single transaction').format(entitle_qualification_value=formatted_spending_currency)
    '''    
    return entitle_qualification_label

def get_entitle_reward_condition_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_entitle_reward_condition_list(preferred_language)
        
        return map_label_by_code(code_label_json, code) or '-'
    else:
        return ''
    
def redemption_catalogue_completed_status_label(program_completed_status_code):
    if program_completed_status_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_redemption_catalogue_status_json(preferred_language)
        return map_label_by_code(code_label_json, program_completed_status_code)
    else:
        return ''