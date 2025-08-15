'''
Created on 19 Feb 2021

@author: jacklok
'''
import logging

from flask import Blueprint, render_template, request, current_app, session, abort
from flask.helpers import url_for
from flask.json import jsonify
from flask_babel import gettext
import jinja2
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.string_util import is_not_empty, is_empty
from trexconf import program_conf as program_conf
from trexmodel.models.datastore.program_models import MerchantAcct, \
    MerchantProgram
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.jinja.program_filters import expiration_settings_details_filter, effective_settings_details_filter,\
        program_reward_scheme_details as program_reward_scheme_details_filter, \
        program_reward_expiration_value_label as program_voucher_expiration_value_label_filter, \
        program_voucher_effective_value_label as program_voucher_effective_value_label_filter, \
        program_voucher_effective_type_label as program_voucher_effective_type_label_filter, \
        program_reward_format_label as program_reward_format_label_filter, \
        program_reward_base_label as program_reward_base_label_filter, \
        program_completed_status_label as program_completed_status_label_filter, membership_expiration_details_filter,\
        program_giveaway_method_label as program_giveaway_method_label_filter, program_giveaway_system_condition_label as program_giveaway_system_condition_label_filter,\
    birthday_reward_giveaway_details_filter, program_reward_limit_brief_filter,\
    program_reward_limit_type_label_filter
    
from trexadmin.forms.merchant.program_forms import ProgramDetailsForm, ProgramVoucherRewardForm, ProgramExclusivityForm, ProgramBasicRewardDetailsForm,\
    ProgramVoucherRewardDetailsForm, PrepaidDetailsForm 
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account, get_merchant_configured_currency_details, convert_list_to_string
from trexadmin.libs.http import StatusCode, create_rest_message
from trexmodel.program_conf import is_program_current_status_reach
from trexadmin.controllers.system.system_route_helpers import get_reward_format_json
from trexlib.utils.common.currency_util import format_currency as currency_formatting
import json
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.merchant_models import MerchantTagging,\
    MerchantUser
from trexlib.utils.common.common_util import sort_list
from trexlib.utils.string_util import random_string
from trexmodel.models.datastore.membership_models import MerchantMembership,\
    MerchantTierMembership
from trexconf.conf import AGE_TIME_FIVE_MINUTE, AGE_TIME_ONE_HOUR
from _datetime import timedelta
from trexmodel.models.datastore.merchant_promotion_models import MerchantPromotionCode

reward_program_setup_bp = Blueprint('reward_program_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/reward-program/program-setup/')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@reward_program_setup_bp.context_processor
def reward_program_setup_bp_inject_settings():
    
    return dict(
               PROGRAM_STATUS_PROGRAM_BASE          = program_conf.PROGRAM_STATUS_PROGRAM_BASE,
               PROGRAM_STATUS_REWARD_SCHEME         = program_conf.PROGRAM_STATUS_REWARD_SCHEME,
               PROGRAM_STATUS_REWARD_EXCLUSIVITY    = program_conf.PROGRAM_STATUS_EXCLUSIVITY,
               PROGRAM_STATUS_MEMBERSHIP_ENTITLEMENT= program_conf.PROGRAM_STATUS_EXCLUSIVITY, 
               PROGRAM_STATUS_REVIEW                = program_conf.PROGRAM_STATUS_REVIEW,
               PROGRAM_STATUS_PUBLISH               = program_conf.PROGRAM_STATUS_PUBLISH,
               
               POINT_FORMAT_LABEL                   = gettext('Point'),
               STAMP_FORMAT_LABEL                   = gettext('Stamp'),
               VOUCHER_FORMAT_LABEL                 = gettext('Voucher'), 
               
               REWARD_BASE_ON_GIVEAWAY              = program_conf.REWARD_BASE_ON_GIVEAWAY,
               REWARD_BASE_ON_PROMOTION_SPENDING    = program_conf.REWARD_BASE_ON_PROMOTION_SPENDING,
               REWARD_BASE_ON_BIRTHDAY              = program_conf.REWARD_BASE_ON_BIRTHDAY,
               
               REWARD_FORMAT_SET                    = program_conf.REWARD_FORMAT_SET,
               BASIC_TYPE_REWARD_FORMAT             = program_conf.BASIC_TYPE_REWARD_FORMAT,
               
               FREQUENCY_AND_TIME_BASED_PROGRAM     = program_conf.FREQUENCY_AND_TIME_BASED_PROGRAM,
               SPENDING_BASED_PROGRAM               = program_conf.SPENDING_BASED_PROGRAM,
               
               ADVANCE_IN_DAY                       = program_conf.ADVANCE_IN_DAY,
               
               REWARD_LIMIT_TYPE_NO_LIMIT               = program_conf.REWARD_LIMIT_TYPE_NO_LIMIT,
               REWARD_LIMIT_TYPE_LIMIT_BY_MONTH         = program_conf.REWARD_LIMIT_TYPE_BY_MONTH,
               REWARD_LIMIT_TYPE_LIMIT_BY_WEEK          = program_conf.REWARD_LIMIT_TYPE_BY_WEEK,
               REWARD_LIMIT_TYPE_LIMIT_BY_DAY           = program_conf.REWARD_LIMIT_TYPE_BY_DAY,
               REWARD_LIMIT_TYPE_LIMIT_BY_TRANSACTION   = program_conf.REWARD_LIMIT_TYPE_BY_TRANSACTION,
               
               LOYALTY_PACKAGE_LITE                 = program_conf.LOYALTY_PACKAGE_LITE,
               
                )


@reward_program_setup_bp.app_template_filter()
def program_completed_status_label(program_completed_status_code):
    return program_completed_status_label_filter(program_completed_status_code)

@reward_program_setup_bp.app_template_filter()
def program_reward_base_label(code):
    return program_reward_base_label_filter(code)
    
@reward_program_setup_bp.app_template_filter()
def program_reward_format_label(code):
    return program_reward_format_label_filter(code)

@reward_program_setup_bp.app_template_filter()
def program_giveaway_method_label(code):
    return program_giveaway_method_label_filter(code)

@reward_program_setup_bp.app_template_filter()
def program_giveaway_system_condition_label(code):
    return program_giveaway_system_condition_label_filter(code)
    
@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def program_voucher_effective_type_label(context, code):
    return program_voucher_effective_type_label_filter(code)
    
@reward_program_setup_bp.app_template_filter()
def program_voucher_expiration_type_label(code):
    return program_voucher_expiration_type_label(code)   
    
@reward_program_setup_bp.app_template_filter()
def program_voucher_effective_value_label(voucher_settings):
    return program_voucher_effective_value_label_filter(voucher_settings)        
    
@reward_program_setup_bp.app_template_filter()
def program_voucher_expiration_value_label(voucher_settings):
    return program_voucher_expiration_value_label_filter(voucher_settings)    

@reward_program_setup_bp.app_template_filter()
def birthday_reward_giveaway_details(program):
    return birthday_reward_giveaway_details_filter(program)

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def list_to_string(context, list_to_convert, default='-'):
    return convert_list_to_string(list_to_convert, default=default)    

@reward_program_setup_bp.app_template_filter()
def format_currency_without_currency_label(value_2_format):
    currency_details = get_merchant_configured_currency_details()
    return currency_formatting(value_2_format, 
                        currency_label=currency_details.get('currency_label'),
                        floating_point=currency_details.get('floating_point'),
                        decimal_separator=currency_details.get('decimal_separator'),
                        thousand_separator=currency_details.get('thousand_separator'),
                        show_thousand_separator=True, 
                        show_currency_label = False)
    
@reward_program_setup_bp.app_template_filter()
def format_currency_with_currency_label(value_2_format):
    currency_details = get_merchant_configured_currency_details()
    return currency_formatting(value_2_format, 
                        currency_label=currency_details.get('currency_label'),
                        floating_point=currency_details.get('floating_point'),
                        decimal_separator=currency_details.get('decimal_separator'),
                        thousand_separator=currency_details.get('thousand_separator'),
                        show_thousand_separator=True, 
                        show_currency_label = True)    

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def program_reward_scheme_details(context, program):
    return program_reward_scheme_details_filter(program)

'''
@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def program_expiration_details(context, program):
    return program_expiration_details_filter(program)
'''

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def effective_settings_details(context, effective_settings):
    return effective_settings_details_filter(effective_settings)


@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def expiration_settings_details(context, expiration_settings):
    return expiration_settings_details_filter(expiration_settings)

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def program_exclusivity_details(context, program):
    pass

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def membership_expiration_details(context, membership):
    return membership_expiration_details_filter(membership)

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def program_reward_limit_brief(context, program):
    return program_reward_limit_brief_filter(program)

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def program_reward_limit_type_label(context, program):
    return program_reward_limit_type_label_filter(program)

@jinja2.contextfilter
@reward_program_setup_bp.app_template_filter()
def check_program_is_effective(context, program, merchant_acct):
    today = (datetime.utcnow() + timedelta(hours=merchant_acct.get('gmt_hour')))
    end_date = datetime.strptime(program.get('end_date'), '%d/%m/%Y')
    return end_date>=today

def get_configured_tags_list():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="get_configured_tags_list")
    configured_tag_list = []
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        merchant_tag_list   = MerchantTagging.list_by_merchant_account(merchant_acct)
    
    for t in merchant_tag_list:
        configured_tag_list.append(t.label)
        
    return configured_tag_list

def get_configured_promotion_codes_list():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="get_configured_promotion_codes_list")
    configured_promotion_code_list = []
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        merchant_promotion_codes_list   = MerchantPromotionCode.list_by_merchant_account(merchant_acct)
    
    for t in merchant_promotion_codes_list:
        configured_promotion_code_list.append(t.label)
        
    return configured_promotion_code_list
    

@reward_program_setup_bp.route('/', methods=['GET'])
@login_required
def program_index(): 
    return latest_program_listing('merchant/loyalty/reward_program/program_setup/program_overview.html')
    

@reward_program_setup_bp.route('/latest-program-listing', methods=['GET'])
@login_required
def show_latest_program_listing(): 
    return latest_program_listing('merchant/loyalty/reward_program/program_setup/latest_program_content.html', show_page_title=False)


def latest_program_listing(template_name, show_page_title=True): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_programs_list = []
    
    db_client = create_db_client(caller_info="latest_program_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                __merchant_programs_list  = sort_list(MerchantProgram.list_by_merchant_account(merchant_acct), 'created_datetime', reverse_order=True)
                
                merchant_acct = merchant_acct.to_dict()
                
            for mp in __merchant_programs_list:
                merchant_programs_list.append(mp.to_dict())
                
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template(template_name, 
                           page_title                   = gettext('Program Overview') if show_page_title else None,
                           page_url                     = url_for('reward_program_setup_bp.program_index') if show_page_title else None,
                           latest_program_listing_url   = url_for('reward_program_setup_bp.show_latest_program_listing'),
                           archived_program_listing_url = url_for('reward_program_setup_bp.archived_program_listing'),
                           merchant_programs_list       = merchant_programs_list,
                           merchant_acct                = merchant_acct,
                           )    

@reward_program_setup_bp.route('/archived-program', methods=['GET'])
@login_required
def archived_program_listing(): 
    logger.debug('---archived_program_listing---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_programs_list = []
    
    db_client = create_db_client(caller_info="archived_program_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
                __merchant_programs_list  = sort_list(MerchantProgram.list_archived_by_merchant_account(merchant_acct), 'created_datetime', reverse_order=True)
            
            for mp in __merchant_programs_list:
                merchant_programs_list.append(mp.to_dict())
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
    
    
    return render_template('merchant/loyalty/reward_program/program_setup/archived_program.html',
                           merchant_programs_list   = merchant_programs_list,
                           )

@reward_program_setup_bp.route('/create-program', methods=['GET'])
@login_required
def create_program(): 
    logger.debug('---create_program---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client               = create_db_client(caller_info="create_program")
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
    
    return render_template('merchant/loyalty/reward_program/program_setup/create_program.html',
                           define_program_base              = url_for('reward_program_setup_bp.define_program_base_post'),
                           #define_reward_format             = url_for('reward_program_setup_bp.define_program_reward_format_post'),
                           #define_reward_scheme             = url_for('reward_program_setup_bp.define_program_reward_scheme_post'),
                           define_program_exclusivity       = url_for('reward_program_setup_bp.define_program_exclusivity_post'),
                           show_program_exclusivity         = url_for('reward_program_setup_bp.show_program_exclusivity'),
                           show_program_review              = url_for('reward_program_setup_bp.show_program_review'),
                           publish_program                  = url_for('reward_program_setup_bp.publish_program_post'),
                           
                           configured_tag_list              = get_configured_tags_list(),
                           configured_promotion_code_list   = get_configured_promotion_codes_list(),
                           loyalty_package                  = merchant_acct.loyalty_package,
                           #reward_base_list     = reward_base_list,
                           )

def __get_reward_format_label(reward_format, selected_language):
    
    
    data_list = get_reward_format_json(selected_language)
    
    for d in data_list:
        if d.get('code') == reward_format:
            return d.get('label')
    
    
@reward_program_setup_bp.route('/switch-reward-details-input/<program_key>', methods=['GET'])
@login_required
def switch_reward_details_input(program_key): 
    selected_language = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    
    logger.debug('---switch_reward_details_input---')
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="switch_reward_type_scheme_input")
    
    try:
        with db_client.context():
            program = MerchantProgram.fetch(program_key)
            program_details = program.to_dict()
            
    except:
        logger.error('Fail to read merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
                
    
    
    
    template_name                   = None
    reward_base                     = program.reward_base
    reward_format                   = program.reward_format
    REWARD_FORMAT_LABEL             = __get_reward_format_label(reward_format, selected_language)
    
    define_reward_details_post_url  = url_for('reward_program_setup_bp.define_program_{reward_format}_details_post'.format(reward_format=reward_format))
    
    logger.debug('reward_base=%s', reward_base)
    logger.debug('reward_format=%s', reward_format)
    
    if reward_base in (program_conf.REWARD_BASE_ON_BIRTHDAY, program_conf.REWARD_BASE_ON_GIVEAWAY):
        if reward_format in program_conf.BASIC_TYPE_REWARD_FORMAT:
            template_name                   = 'merchant/loyalty/reward_program/program_setup/reward_details_input/giveaway_basic_reward_type_input_content.html'
        else:
            template_name                   = 'merchant/loyalty/reward_program/program_setup/reward_details_input/giveaway_{reward_format}_reward_details_input_content.html'.format(reward_format=reward_format)
    else:
        if reward_format in program_conf.BASIC_TYPE_REWARD_FORMAT:
            if reward_format in program_conf.REWARD_FORMAT_VOUCHER:
                template_name                   = 'merchant/loyalty/reward_program/program_setup/reward_details_input/{reward_format}_reward_details_input_content.html'.format(reward_format=reward_format)
            else:
                template_name                   = 'merchant/loyalty/reward_program/program_setup/reward_details_input/basic_type_reward_details_input_content.html'
        else:
            template_name                   = 'merchant/loyalty/reward_program/program_setup/reward_details_input/basic_type_reward_details_input_content.html'.format(reward_format=reward_format)
    
    program_voucher_list = None
    
    
    if program.reward_format == program_conf.REWARD_FORMAT_VOUCHER:
        program_voucher_list = get_program_voucher_listing(program_key)
        
    if program_details.get('specified_days_list') is None:
        program_details['specified_days_list'] = []
        
    if program_details.get('specified_dates_of_month_list') is None:
        program_details['specified_dates_of_month_list'] = []        
    
    return render_template(
                           template_name,
                           define_reward_details                        = define_reward_details_post_url,
                           REWARD_FORMAT_LABEL                          = REWARD_FORMAT_LABEL,
                           add_program_voucher_reward                   = url_for('reward_program_setup_bp.add_program_voucher_reward_post'),
                           program                                      = program_details,
                           program_voucher_list                         = program_voucher_list,
                           define_program_point_scheme                  = url_for('reward_program_setup_bp.define_program_point_details_post'),
                           define_program_prepaid_scheme                = url_for('reward_program_setup_bp.define_program_prepaid_details_post'),
                           define_program_stamp_scheme                  = url_for('reward_program_setup_bp.define_program_stamp_details_post'),
                           define_program_birthday_scheme               = url_for('reward_program_setup_bp.define_program_birthday_details_post'),
                           
                           define_program_voucher_scheme                = url_for('reward_program_setup_bp.define_program_voucher_details_post'),
                           program_key                                  = program_key,
                           
                           
                           )    
    
@reward_program_setup_bp.route('/edit-program/<program_key>', methods=['GET'])
@login_required
def edit_program(program_key): 
    logger.debug('---edit_program---')
    program                         = None
    reward_format                   = None
    program_voucher_list            = []
    program_tier_membership_list    = []
    program_details                 = None
    if is_not_empty(program_key):
        
        logged_in_merchant_user = get_loggedin_merchant_user_account()
    
        db_client               = create_db_client(caller_info="create_program")
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        db_client = create_db_client(caller_info="edit_program")
            
        try:
            with db_client.context():
                program         = MerchantProgram.fetch(program_key)
                program_details = program.to_dict()
                
                if program_details.get('specified_days_list') is None:
                    program_details['specified_days_list'] = []
                    
                if program_details.get('specified_dates_of_month_list') is None:
                    program_details['specified_dates_of_month_list'] = []
                
                logger.debug('program_details=%s', program_details)
                
                if program:
                    reward_format = program.reward_format
                
            is_program_review_step = program_conf.is_valid_to_update_program_status(program_conf.PROGRAM_STATUS_PUBLISH, program.completed_status)
             
            if program.reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                program_voucher_list = get_program_voucher_listing(program_key) 
            
            logger.debug('program_voucher_list=%s', program_voucher_list)
                
            define_reward_details_post_url  = url_for('reward_program_setup_bp.define_program_{reward_format}_details_post'.format(reward_format=reward_format))  
                
            return render_template('merchant/loyalty/reward_program/program_setup/create_program.html',
                           define_program_base                          = url_for('reward_program_setup_bp.define_program_base_post'),
                           define_reward_details                        = define_reward_details_post_url,
                           define_reward_scheme                         = url_for('reward_program_setup_bp.define_program_{reward_format}_details_post'.format(reward_format=reward_format)) if reward_format else None,
                           show_program_exclusivity                     = url_for('reward_program_setup_bp.show_program_exclusivity'),
                           show_program_review                          = url_for('reward_program_setup_bp.show_program_review'),
                           define_program_exclusivity                   = url_for('reward_program_setup_bp.define_program_exclusivity_post'),
                           publish_program                              = url_for('reward_program_setup_bp.publish_program_post'),
                           
                           add_program_voucher_reward                   = url_for('reward_program_setup_bp.add_program_voucher_reward_post'),
                           
                           define_program_point_scheme                  = url_for('reward_program_setup_bp.define_program_point_details_post'),
                           define_program_prepaid_scheme                = url_for('reward_program_setup_bp.define_program_prepaid_details_post'),
                           define_program_stamp_scheme                  = url_for('reward_program_setup_bp.define_program_stamp_details_post'),
                           define_program_voucher_scheme                = url_for('reward_program_setup_bp.define_program_voucher_details_post'),
                           
                           PROGRAM_STATUS_PROGRAM_BASE_COMPLETED        = True,
                           PROGRAM_STATUS_REWARD_SCHEME_COMPLETED       = is_program_current_status_reach(program_conf.PROGRAM_STATUS_REWARD_SCHEME, program.completed_status),
                           PROGRAM_STATUS_REWARD_EXCELUSIVITY_COMPLETED = is_program_current_status_reach(program_conf.PROGRAM_STATUS_EXCLUSIVITY, program.completed_status),
                           #PROGRAM_STATUS_REVIEW_COMPLETED              = is_program_current_status_reach(program_conf.PROGRAM_STATUS_REVIEW, program.completed_status),
                           PROGRAM_STATUS_PUBLISH_COMPLETED             = is_program_current_status_reach(program_conf.PROGRAM_STATUS_PUBLISH, program.completed_status),
                           
                           program                                      = program_details,
                           program_completed_status                     = program.completed_status,
                           is_program_review_step                       = is_program_review_step,
                           is_edit_program                              = True,
                           program_voucher_list                         = program_voucher_list,
                           program_tier_membership_list                 = program_tier_membership_list,
                           program_key                                  = program_key,
                           
                           exclusive_tags_list                          = program.exclusive_tags_list,
                           exclusive_membership_list                    = program.exclusive_memberships_list,
                           exclusive_tier_membership_list               = program.exclusive_tier_memberships_list,
                           exclusive_promotion_codes_list               = program.exclusive_promotion_codes_list,
                           configured_tag_list                          = get_configured_tags_list(),
                           configured_promotion_code_list               = get_configured_promotion_codes_list(),
                           
                           loyalty_package                              = merchant_acct.loyalty_package,
                           
                           )
                
        except:
            logger.error('Fail to read merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        
    else:
        return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
    
@reward_program_setup_bp.route('/view-program/<program_key>', methods=['GET'])
@login_required
def view_program(program_key): 
    logger.debug('---view_program---')
    program                 = None
    program_voucher_list    = []
    if is_not_empty(program_key):
        db_client = create_db_client(caller_info="view_program")
        #logged_in_merchant_user = get_loggedin_merchant_user_account()
        try:
            with db_client.context():
                program         = MerchantProgram.fetch(program_key)
                program_details = program.to_dict()
                if program_details.get('specified_days_list') is None:
                    program_details['specified_days_list'] = []
                
                if program_details.get('specified_dates_of_month_list') is None:
                    program_details['specified_dates_of_month_list'] = []
            
            if program and program.reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                program_voucher_list = get_program_voucher_listing(program_key)
                
            return render_template('merchant/loyalty/reward_program/program_setup/view_program.html',
                           is_view_program                  = True,
                           program                          = program_details,
                           program_voucher_list             = program_voucher_list,
                           exclusive_tags_list              = program.exclusive_tags_list,
                           configured_tag_list              = get_configured_tags_list(),
                           loyalty_package                  = program.loyalty_package,
                           )
                
        except:
            logger.error('Fail to view merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to view merchant program'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to view merchant program'), status_code=StatusCode.BAD_REQUEST)    
    
        

@reward_program_setup_bp.route('/define-program-base', methods=['POST'])
@login_required
def define_program_base_post(): 
    logger.debug('---define_program_base_post---')
    
    program_base_data   = request.form
    program_base_form   = ProgramDetailsForm(program_base_data)
    logger.debug('program_base_data=%s', program_base_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = program_base_form.program_key.data
    
    logger.debug('program_key=%s', program_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if program_base_form.validate():
    
        db_client               = create_db_client(caller_info="define_program_base_post")
        
        try:
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                if is_empty(program_key):
                    
                    merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                    program             = MerchantProgram.create(merchant_acct, 
                                                             label                                          = program_base_form.label.data,
                                                             reward_base                                    = program_base_form.reward_base.data,
                                                             reward_format                                  = program_base_form.reward_format.data,
                                                             
                                                             desc                                           = program_base_form.desc.data,
                                                             start_date                                     = program_base_form.start_date.data,
                                                             end_date                                       = program_base_form.end_date.data,
                                                             created_by                                     = merchant_user,
                                                             loyalty_package                                = merchant_acct.loyalty_package,
                                                             )
                    
                    program_key         = program.key_in_str
                    return create_rest_message(status_code=StatusCode.CREATED, 
                                    program_key                             = program_key,
                                    )
                else:
                    
                    program = MerchantProgram.fetch(program_key)
                    if program:
                        MerchantProgram.update_program_base_data(program, 
                                                                  label                                             = program_base_form.label.data,
                                                                  reward_base                                       = program_base_form.reward_base.data,
                                                                  reward_format                                     = program_base_form.reward_format.data,
                                                                  desc                                              = program_base_form.desc.data,
                                                                  start_date                                        = program_base_form.start_date.data,
                                                                  end_date                                          = program_base_form.end_date.data,
                                                                  modified_by                                       = merchant_user
                                                                  )
                        
                        return create_rest_message(status_code=StatusCode.OK, 
                                    program_key                             = program_key,
                                    )
                    else:
                        return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
                        
        except:
            logger.error('Fail to create merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to create merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        
        
    else:
        error_message = program_base_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
    
@reward_program_setup_bp.route('/define-program-point-scheme', methods=['POST'])
@login_required
def define_program_point_details_post():
    return define_program_basic_reward_type_details_post()

'''    
@reward_program_setup_bp.route('/define-program-prepaid-scheme', methods=['POST'])
@login_required
def define_program_prepaid_details_post():
    return define_program_basic_reward_type_details_post()
'''

@reward_program_setup_bp.route('/define-program-stamp-scheme', methods=['POST'])
@login_required
def define_program_stamp_details_post():
    return define_program_basic_reward_type_details_post()
    
@reward_program_setup_bp.route('/define-program-birthday-scheme', methods=['POST'])
@login_required
def define_program_birthday_details_post():
    return define_program_basic_reward_type_details_post()

@reward_program_setup_bp.route('/define-program-voucher-scheme', methods=['POST'])
@login_required
def define_program_voucher_details_post():
    
    logger.debug('---define_program_voucher_details_post---')
    
    reward_details_data = request.form
    reward_details_form = ProgramVoucherRewardDetailsForm(reward_details_data)
    
    logger.debug('******************* reward_details_data=%s', reward_details_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = reward_details_form.program_key.data
    
    logger.debug('program_key=%s', program_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    logger.debug('giveaway_system_condition_membership_key='+convert_list_to_string(reward_details_form.giveaway_system_condition_membership_key.data))
    logger.debug('giveaway_system_condition_tier_membership_key='+convert_list_to_string(reward_details_form.giveaway_system_condition_tier_membership_key.data))
    
    if reward_details_form.validate():
        
        db_client               = create_db_client(caller_info="define_program_voucher_details_post")
        
        giveaway_birthday_reward_when               = reward_details_form.giveaway_birthday_reward_when.data
        giveaway_birthday_reward_advance_in_day     = reward_details_form.giveaway_birthday_reward_advance_in_day.data or 0
        birthday_wish_as_remarks                    = reward_details_form.birthday_wish_as_remarks.data
        
        limit_to_specific_day           = reward_details_form.limit_to_specific_day.data
        specified_days_list             = reward_details_form.specified_days_list.data
        
        limit_to_specific_date_of_month = reward_details_form.limit_to_specific_date_of_month.data
        specified_dates_of_month_list   = reward_details_form.specified_dates_of_month_list.data
        
        reward_limit_type = reward_details_form.reward_limit_type.data
        reward_limit_amount = reward_details_form.reward_limit_amount.data
        
        logger.debug('reward_limit_type=%s', reward_limit_type)
        logger.debug('reward_limit_amount=%s', reward_limit_amount)
        
        logger.debug('giveaway_birthday_reward_when=%s', giveaway_birthday_reward_when)
        logger.debug('giveaway_birthday_reward_advance_in_day=%s', giveaway_birthday_reward_advance_in_day)
        logger.debug('birthday_wish_as_remarks=%s', birthday_wish_as_remarks)
        
        logger.debug('specified_days_list=%s', specified_days_list)
        logger.debug('limit_to_specific_day=%s', limit_to_specific_day)
        
        logger.debug('specified_dates_of_month_list=%s', specified_dates_of_month_list)
        logger.debug('limit_to_specific_date_of_month=%s', limit_to_specific_date_of_month)
        
        try:
            with db_client.context():
                if is_empty(program_key):
                    return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                    
                else:
                    
                    program = MerchantProgram.fetch(program_key)
                    if program:
                        if program.reward_base in (program_conf.REWARD_BASE_ON_SPENDING, program_conf.REWARD_BASE_ON_PROMOTION_SPENDING) :
                            
                            reward_scheme_configuration = {
                                    'spending_currency'                 : float(reward_details_form.spending_currency.data),
                                    'is_recurring_scheme'               : reward_details_form.is_recurring_scheme.data,
                                    'giveaway_when'                     : giveaway_birthday_reward_when,
                                    'advance_in_day'                    : giveaway_birthday_reward_advance_in_day,
                                    'limit_to_specific_day'             : limit_to_specific_day,
                                    'specified_days_list'               : specified_days_list.split(','),
                                    'limit_to_specific_date_of_month'   : limit_to_specific_date_of_month,
                                    'specified_dates_of_month_list'     : specified_dates_of_month_list.split(','),
                                    'reward_limit_type'                 : reward_limit_type,
                                    'reward_limit_amount'               : float(reward_limit_amount),
                                }
                        elif program.reward_base == program_conf.REWARD_BASE_ON_BIRTHDAY:
                            reward_scheme_configuration = {
                                    'is_recurring_scheme'       : reward_details_form.is_recurring_scheme.data,
                                    'giveaway_when'             : giveaway_birthday_reward_when,
                                    'advance_in_day'            : giveaway_birthday_reward_advance_in_day,
                                }    
                        else:
                            reward_scheme_configuration = {}
                            
                        logger.debug('define_program_voucher_details_post: program.reward_items=%s', program.reward_items)
                        
                        logger.debug('reward_details_form.giveaway_system_condition_membership_key.data=%s', reward_details_form.giveaway_system_condition_membership_key.data)
                        
                        is_reward_items_defined = is_not_empty(program.reward_items)
                        if is_reward_items_defined:
                        
                            merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                            MerchantProgram.update_prorgram_reward_details_data(program, 
                                                  reward_scheme_configuration                    = reward_scheme_configuration,
                                                  giveaway_method                                = reward_details_form.giveaway_method.data,
                                                  giveaway_system_condition                      = reward_details_form.giveaway_system_condition.data,
                                                  giveaway_system_condition_membership_key       = reward_details_form.giveaway_system_condition_membership_key.data,
                                                  giveaway_system_condition_tier_membership_key  = reward_details_form.giveaway_system_condition_tier_membership_key.data,
                                                  modified_by                                    = merchant_user,
                                                  remarks                                        = birthday_wish_as_remarks,
                                                  
                                                  )
            logger.debug('program.completed_status=%s', program.completed_status)
                        
            if program is None:
                return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
            elif is_reward_items_defined==False:
                return create_rest_message(gettext('Missing reward item'), status_code=StatusCode.BAD_REQUEST)
                
                
        except:
            logger.error('Fail to update merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    prgoram_key                             = program_key,
                                    )
    else:
        error_message = reward_details_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)        
    
def define_program_basic_reward_type_details_post():     
    
    logger.debug('---define_program_basic_reward_type_details_post---')
    
    reward_details_data = request.form
    reward_details_form = ProgramBasicRewardDetailsForm(reward_details_data)
    
    logger.debug('reward_details_data=%s', reward_details_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = reward_details_form.program_key.data
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    logger.debug('program_key=%s', program_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    
    if reward_details_form.validate():
        
        giveaway_system_condition_membership_key = convert_list_to_string(reward_details_form.giveaway_system_condition_membership_key.data)
        giveaway_system_condition_tier_membership_key = convert_list_to_string(reward_details_form.giveaway_system_condition_tier_membership_key.data)
        
        logger.debug('giveaway_system_condition_membership_key='+ giveaway_system_condition_membership_key)
        logger.debug('giveaway_system_condition_tier_membership_key='+giveaway_system_condition_tier_membership_key)
        
        expiration_type                 = reward_details_form.expiration_type.data
        expiration_date                 = reward_details_form.expiration_date.data
        expiration_value                = reward_details_form.expiration_value.data
        
        limit_to_specific_day           = reward_details_form.limit_to_specific_day.data
        specified_days_list             = reward_details_form.specified_days_list.data
        
        limit_to_specific_date_of_month = reward_details_form.limit_to_specific_date_of_month.data
        specified_dates_of_month_list   = reward_details_form.specified_dates_of_month_list.data
        
        logger.debug('specified_days_list=%s', specified_days_list)
        logger.debug('limit_to_specific_day=%s', limit_to_specific_day)
        
        logger.debug('specified_dates_of_month_list=%s', specified_dates_of_month_list)
        logger.debug('limit_to_specific_date_of_month=%s', limit_to_specific_date_of_month)
        
        reward_limit_type = reward_details_form.reward_limit_type.data
        reward_limit_amount = reward_details_form.reward_limit_amount.data
        
        logger.debug('reward_limit_type=%s', reward_limit_type)
        logger.debug('reward_limit_amount=%s', reward_limit_amount)
        
        giveaway_birthday_reward_when               = reward_details_form.giveaway_birthday_reward_when.data
        giveaway_birthday_reward_advance_in_day     = reward_details_form.giveaway_birthday_reward_advance_in_day.data or 0
        
        logger.debug('giveaway_birthday_reward_when=%s', giveaway_birthday_reward_when)
        logger.debug('giveaway_birthday_reward_advance_in_day=%s', giveaway_birthday_reward_advance_in_day)
        
        if expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE:
            expiration_date     = expiration_date.strftime('%d/%m/%Y')
            expiration_value    = None
        else:
            expiration_date    = None
            
        
        reward_scheme_configuration = {
                                'is_recurring_scheme'               : reward_details_form.is_recurring_scheme.data,
                                'spending_currency'                 : float(reward_details_form.spending_currency.data),
                                'reward_amount'                     : float(reward_details_form.reward_amount.data),
                                'expiration_type'                   : expiration_type,
                                'expiration_date'                   : expiration_date,
                                'expiration_value'                  : expiration_value,
                                'giveaway_when'                     : giveaway_birthday_reward_when,
                                'advance_in_day'                    : giveaway_birthday_reward_advance_in_day,
                                'reward_limit_type'                 : reward_limit_type,
                                'reward_limit_amount'               : float(reward_limit_amount),
                                'limit_to_specific_day'             : limit_to_specific_day,
                                'specified_days_list'               : specified_days_list.split(','),
                                'limit_to_specific_date_of_month'   : limit_to_specific_date_of_month,
                                'specified_dates_of_month_list'     : specified_dates_of_month_list.split(','),
                                
                            }
        
        db_client               = create_db_client(caller_info="define_program_basic_reward_type_details_post")
        
        try:
            with db_client.context():
                if is_empty(program_key):
                    return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                    
                else:
                    
                    program = MerchantProgram.fetch(program_key)
                    if program:
                        logger.debug('reward_scheme_configuration to be updated =%s', reward_scheme_configuration)
                        
                        merchant_user = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                        MerchantProgram.update_prorgram_reward_details_data(program, 
                                              reward_scheme_configuration                    = reward_scheme_configuration,
                                              giveaway_method                                = reward_details_form.giveaway_method.data,
                                              giveaway_system_condition                      = reward_details_form.giveaway_system_condition.data,
                                              giveaway_system_condition_value                = reward_details_form.giveaway_system_condition_value.data,
                                              giveaway_system_condition_membership_key       = giveaway_system_condition_membership_key,
                                              #giveaway_system_condition_membership_key       = reward_details_form.giveaway_system_condition_membership_key.data,
                                              giveaway_system_condition_tier_membership_key  = giveaway_system_condition_tier_membership_key,
                                              #giveaway_system_condition_tier_membership_key  = reward_details_form.giveaway_system_condition_tier_membership_key.data,
                                              modified_by                   = merchant_user,
                                              
                                              )
                            
            logger.debug('program.completed_status=%s', program.completed_status)
                        
            if program is None:
                return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to update merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    prgoram_key                             = program_key,
                                    )
    else:
        error_message = reward_details_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)

@reward_program_setup_bp.route('/define-program-prepaid-scheme', methods=['POST'])
@login_required    
def define_program_prepaid_details_post():     
    
    
    logger.debug('---define_program_prepaid_details_post---')
    
    reward_details_data = request.form
    reward_details_form = PrepaidDetailsForm(reward_details_data)
    
    logger.debug('reward_details_data=%s', reward_details_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = reward_details_form.program_key.data
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    logger.debug('program_key=%s', program_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    
    if reward_details_form.validate():
        
        logger.debug('giveaway_system_condition_membership_key='+ convert_list_to_string(reward_details_form.giveaway_system_condition_membership_key.data))
        logger.debug('giveaway_system_condition_tier_membership_key='+convert_list_to_string(reward_details_form.giveaway_system_condition_tier_membership_key.data))
        
        giveaway_birthday_reward_when               = reward_details_form.giveaway_birthday_reward_when.data
        giveaway_birthday_reward_advance_in_day     = reward_details_form.giveaway_birthday_reward_advance_in_day.data or 0
        
        logger.debug('giveaway_birthday_reward_when=%s', giveaway_birthday_reward_when)
        logger.debug('giveaway_birthday_reward_advance_in_day=%s', giveaway_birthday_reward_advance_in_day)
        
        limit_to_specific_day           = reward_details_form.limit_to_specific_day.data
        specified_days_list             = reward_details_form.specified_days_list.data
        
        limit_to_specific_date_of_month = reward_details_form.limit_to_specific_date_of_month.data
        specified_dates_of_month_list   = reward_details_form.specified_dates_of_month_list.data
        
        logger.debug('specified_days_list=%s', specified_days_list)
        logger.debug('limit_to_specific_day=%s', limit_to_specific_day)
        
        logger.debug('specified_dates_of_month_list=%s', specified_dates_of_month_list)
        logger.debug('limit_to_specific_date_of_month=%s', limit_to_specific_date_of_month)
        
        reward_limit_type = reward_details_form.reward_limit_type.data
        reward_limit_amount = reward_details_form.reward_limit_amount.data
        
        logger.debug('reward_limit_type=%s', reward_limit_type)
        logger.debug('reward_limit_amount=%s', reward_limit_amount)
        
        reward_scheme_configuration = {
                                'is_recurring_scheme'               : reward_details_form.is_recurring_scheme.data,
                                'spending_currency'                 : float(reward_details_form.spending_currency.data),
                                'reward_amount'                     : float(reward_details_form.reward_amount.data),
                                'giveaway_when'                     : giveaway_birthday_reward_when,
                                'advance_in_day'                    : giveaway_birthday_reward_advance_in_day,
                                'reward_limit_type'                 : reward_limit_type,
                                'reward_limit_amount'               : float(reward_limit_amount),
                                'limit_to_specific_day'             : limit_to_specific_day,
                                'specified_days_list'               : specified_days_list.split(','),
                                'limit_to_specific_date_of_month'   : limit_to_specific_date_of_month,
                                'specified_dates_of_month_list'     : specified_dates_of_month_list.split(','),
                                
                            }
        
        db_client               = create_db_client(caller_info="define_program_reward_scheme_post")
        try:
            with db_client.context():
                if is_empty(program_key):
                    return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                    
                else:
                    
                    program = MerchantProgram.fetch(program_key)
                    if program:
                        logger.debug('reward_scheme_configuration to be updated =%s', reward_scheme_configuration)
                        
                        merchant_user = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                        MerchantProgram.update_prorgram_reward_details_data(program, 
                                              reward_scheme_configuration                    = reward_scheme_configuration,
                                              giveaway_method                                = reward_details_form.giveaway_method.data,
                                              giveaway_system_condition                      = reward_details_form.giveaway_system_condition.data,
                                              giveaway_system_condition_value                = reward_details_form.giveaway_system_condition_value.data,
                                              giveaway_system_condition_membership_key       = reward_details_form.giveaway_system_condition_membership_key.data,
                                              giveaway_system_condition_tier_membership_key  = reward_details_form.giveaway_system_condition_tier_membership_key.data,
                                              modified_by                   = merchant_user,
                                              
                                              )
                            
            logger.debug('program.completed_status=%s', program.completed_status)
                        
            if program is None:
                return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to update merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    prgoram_key                             = program_key,
                                    )
    else:
        error_message = reward_details_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)    
    

@reward_program_setup_bp.route('/show-program-exclusivity', methods=['GET'])
@login_required
def show_program_exclusivity(): 
    logger.debug('---show_program_exclusivity---')
    
    program_key             = request.args.get('program_key')
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="show_program_exclusivity")
    try:
        
        with db_client.context():
            program = MerchantProgram.fetch(program_key)
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/reward_program/program_setup/program_reward_exclusivity_content.html', 
                           program                      = program.to_dict(),
                           define_program_exclusivity   = url_for('reward_program_setup_bp.define_program_exclusivity_post'),
                           )
    
@reward_program_setup_bp.route('/show-program-review', methods=['GET'])
@login_required
def show_program_review(): 
    logger.debug('---show_program_review---')
    
    program_key             = request.args.get('program_key')
    program_voucher_list    = get_program_voucher_listing(program_key)
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="show_program_review")
    try:
        
        with db_client.context():
            program = MerchantProgram.fetch(program_key)
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/reward_program/program_setup/program_review_content.html', 
                           program                  = program.to_dict(),
                           program_voucher_list     = program_voucher_list,
                           )

@reward_program_setup_bp.route('/define-program-exclusivity', methods=['POST'])
@login_required
def define_program_exclusivity_post(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_exclusivity_data = request.form
    program_exclusivity_form = ProgramExclusivityForm(program_exclusivity_data)
    
    logger.debug('define_program_exclusivity_post: program_exclusivity_data=%s', program_exclusivity_data)
    
    program_key = program_exclusivity_form.program_key.data
    
    db_client                   = create_db_client(caller_info="define_program_exclusivity_post")
    try:
        with db_client.context():
            if is_empty(program_key):
                return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                try:
                    program = MerchantProgram.fetch(program_key)
                    if program:
                        reward_base = program.reward_base
                        
                        
                        if reward_base!=program_conf.REWARD_BASE_ON_GIVEAWAY:
                            tags_list = program_exclusivity_form.tags_list.data
                            if is_not_empty(tags_list):
                                tags_list = tags_list.split(',')
                                
                                tags_list = [x for x in tags_list if x]
                                
                            promotion_codes_list = program_exclusivity_form.promotion_codes_list.data
                            if is_not_empty(promotion_codes_list):
                                promotion_codes_list = promotion_codes_list.split(',')
                                
                                promotion_codes_list = [x for x in promotion_codes_list if x]    
                                
                            membership_key_list = program_exclusivity_form.membership_key.data
                            if is_not_empty(membership_key_list):
                                membership_key_list = membership_key_list.split(',')
                                
                                membership_key_list = [x for x in membership_key_list if x]
                                
                            tier_membership_key_list = program_exclusivity_form.tier_membership_key.data
                            if is_not_empty(tier_membership_key_list):
                                tier_membership_key_list = tier_membership_key_list.split(',')       
                                
                                tier_membership_key_list = [x for x in tier_membership_key_list if x] 
                            
                            
                            if reward_base==program_conf.REWARD_BASE_ON_PROMOTION_SPENDING:
                                if is_empty(promotion_codes_list):
                                    return create_rest_message(gettext('Promotion code is required'), status_code=StatusCode.BAD_REQUEST)
                                    
                            
                            exclusivity_configuration = {
                                                        'tags'              : tags_list,
                                                        'memberships'       : membership_key_list,
                                                        'tier_memberships'  : tier_membership_key_list,
                                                        'promotion_codes'   : promotion_codes_list,
                                                        }
                            
                            
                        else:
                            exclusivity_configuration = {
                                                        'tags'              : [],
                                                        'memberships'       : [],
                                                        'tier_memberships'  : [],
                                                        'promotion_codes'   : [],
                                                        }
                        
                        logger.debug('exclusivity_configuration=%s', exclusivity_configuration)
                        
                        logger.debug('program.completed_status=%s', program.completed_status)
                        
                        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                        MerchantProgram.update_prorgram_exclusivity_data(program, 
                                                                         exclusivity_configuration=exclusivity_configuration, 
                                                                         modified_by=merchant_user)
                except:
                    logger.error('Failed to update exclusivity due to %s', get_tracelog())
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@reward_program_setup_bp.route('/publish-program', methods=['POST','GET'])
@login_required
def publish_program_post(): 
    program_key = request.form.get('program_key') or request.args.get('program_key')

    logger.debug('program_key=%s', program_key)
    
    db_client               = create_db_client(caller_info="publish_program_post")
    try:
        with db_client.context():
            if is_empty(program_key):
                return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                program = MerchantProgram.fetch(program_key)
                if program:
                    MerchantProgram.publish_program(program)
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@reward_program_setup_bp.route('/archive-program', methods=['POST','GET'])
@login_required
def archive_program_post(): 
    
    logger.debug('---archieve_program_post---')
    
    program_key = request.args.get('program_key')
    
    logger.debug('program_key=%s', program_key)
    
    db_client               = create_db_client(caller_info="archive_program_post")
    try:
        with db_client.context():
            if is_empty(program_key):
                return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                program = MerchantProgram.fetch(program_key)
                if program:
                    MerchantProgram.archive_program(program)
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to archive merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)


@reward_program_setup_bp.route('/enable-program/<program_key>', methods=['POST','GET'])
@login_required
def enable_program(program_key): 
    return enable_or_disable_program(program_key, True)

@reward_program_setup_bp.route('/disable-program/<program_key>', methods=['POST','GET'])
@login_required
def disable_program(program_key): 
    return enable_or_disable_program(program_key, False)
    
def enable_or_disable_program(program_key, to_enable): 
    
    logger.debug('program_key=%s', program_key)
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client               = create_db_client(caller_info="enable_or_disable_program")
    
    try:
        with db_client.context():
            if is_empty(program_key):
                return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                program = MerchantProgram.fetch(program_key)
                if program:
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    if to_enable:
                        MerchantProgram.enable(program, modified_by=merchant_user)
                        logger.debug('Program have been enabled')
                    else:
                        MerchantProgram.disable(program)
                        logger.debug('Program have been disabled')
                else:
                    logger.warn('program is not found')
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@reward_program_setup_bp.route('/flush-dirty-program/<merchant_acct_key>', methods=['GET'])
@login_required
def flush_dirty_program(merchant_acct_key): 
    logger.debug('---flush_dirty_program---')
    
    db_client = create_db_client(caller_info="flush_dirty_program")
    published_program_configuration = []
    try:
        
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_acct_key)
            merchant_acct.flush_dirty_program_configuration()
            published_program_configuration = merchant_acct.published_program_configuration
            
    except:
        logger.error('Fail to get merchant published program due to %s', get_tracelog())
           
    
    return jsonify(published_program_configuration)

@reward_program_setup_bp.route('/add-program-voucher-reward', methods=['POST'])
@login_required
def add_program_voucher_reward_post(): 
    logger.debug('---add_program_voucher_reward_post---')
    voucher_reward_form = ProgramVoucherRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = voucher_reward_form.program_key.data
    
    logger.debug('add_program_voucher_reward_post: program_key=%s', program_key)
    logger.debug('add_program_voucher_reward_post: request.form=%s', request.form)
    
    
    if voucher_reward_form.validate():
        
        effective_date = voucher_reward_form.effective_date.data
        if is_not_empty(effective_date):
            effective_date = effective_date.strftime('%d-%m-%Y')
        
        add_voucher_configuration = {
                                'voucher_index'         : random_string(10),
                                'voucher_key'           : voucher_reward_form.voucher_key.data,
                                'voucher_amount'        : voucher_reward_form.voucher_amount.data,
                                
                                'use_online'            : voucher_reward_form.use_online.data,
                                'use_in_store'          : voucher_reward_form.use_in_store.data,
                                
                                'effective_type'        : voucher_reward_form.effective_type.data,
                                'effective_date'        : effective_date,
                                'effective_value'       : voucher_reward_form.effective_value.data,
                                
                                'expiration_type'       : voucher_reward_form.expiration_type.data,
                                'expiration_date'       : voucher_reward_form.expiration_date.data,
                                'expiration_value'      : voucher_reward_form.expiration_value.data,    
                            }
    
        db_client       = create_db_client(caller_info="add_program_voucher_reward_post")
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program = MerchantProgram.fetch(program_key)
                MerchantProgram.add_program_voucher(merchant_program, add_voucher_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add giveaway voucher into program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add voucher into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = voucher_reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@reward_program_setup_bp.route('/remove-program-voucher', methods=['DELETE'])
@login_required
def remove_program_voucher_post(): 
    logger.debug('---remove_program_voucher_from_program_post---')
    
    program_key     = request.args.get('program_key')
    voucher_index   = request.args.get('voucher_index')
    
    logger.debug('remove_program_voucher_from_program_post: program_key=%s', program_key)
    logger.debug('remove_program_voucher_from_program_post: voucher_index=%s', voucher_index)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="remove_program_voucher_post")
    try:
        
        with db_client.context():
            merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            program = MerchantProgram.fetch(program_key)
            
            MerchantProgram.remove_program_voucher(program, voucher_index, modified_by=merchant_user)
            
        return create_rest_message(status_code=StatusCode.OK)
            
    except:
        logger.error('Fail to add giveaway voucher into program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to remove voucher'), status_code=StatusCode.BAD_REQUEST)   
    
    

@reward_program_setup_bp.route('/list-published-voucher-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_publish_voucher_json():
    logging.debug('---list_publish_voucher_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    db_client = create_db_client(caller_info="program_key")
    try:
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            published_vouchers_list = MerchantVoucher.list_published_by_merchant_account(merchant_acct)
            for voucher in published_vouchers_list:
                data_list.append({
                                "code"      : voucher.key_in_str,
                                "label"     : voucher.label,
                                'image_url' : voucher.image_public_url,
                                })
        
    except:
        logger.error('Fail to list published voucher due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_FIVE_MINUTE,
                                  )
    
    return resp  

@reward_program_setup_bp.route('/list-membership-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_membership_json():
    logging.debug('---list_membership_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    db_client = create_db_client(caller_info="program_key")
    try:
        
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            membership_list         = MerchantMembership.list_by_merchant_acct(merchant_acct)
            for membership in membership_list:
                data_list.append({
                                "code"  : membership.key_in_str,
                                "label" : membership.label,
                                })
        
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp 

@reward_program_setup_bp.route('/list-tier-membership-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_tier_membership_json():
    logging.debug('---list_tier_membership_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    db_client = create_db_client(caller_info="list_tier_membership_json")
    try:
        
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            membership_list         = MerchantTierMembership.list_by_merchant_acct(merchant_acct)
            
            for membership in membership_list:
                data_list.append({
                                "code"  : membership.key_in_str,
                                "label" : membership.label,
                                })
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp      

@reward_program_setup_bp.route('/program-voucher-listing/<program_key>', methods=['GET'])
@login_required
def show_program_voucher_listing(program_key):
    program_voucher_list = get_program_voucher_listing(program_key)
    logger.debug('program_voucher_list=%s', program_voucher_list)
    return render_template('merchant/loyalty/reward_program/program_setup/reward_details_input/program_giveaway_voucher_listing_content.html',
                           program_voucher_list     = program_voucher_list,
                           program_key              = program_key,
                           )
def get_program_voucher_listing(program_key): 
    logger.debug('---program_voucher_listing---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    program_voucher_list = []
    db_client = create_db_client(caller_info="program_voucher_listing")
    try:
        with db_client.context():
            program                         = MerchantProgram.fetch(program_key)
            added_program_voucher_list      = program.program_settings.get('reward_items') or []
            
            
            for av in added_program_voucher_list:
                program_voucher_list.append({
                                    "voucher_index"     : av.get('voucher_index'),
                                    "voucher_key"       : av.get('voucher_key'),
                                    "amount"            : av.get('voucher_amount'),
                                    "use_online"        : av.get('use_online'),
                                    "use_in_store"      : av.get('use_in_store'),
                                    "effective_type"    : av.get('effective_type'),
                                    "effective_date"    : av.get('effective_date'),
                                    "effective_value"   : av.get('effective_value'),
                                    "expiration_type"   : av.get('expiration_type'),
                                    "expiration_date"   : av.get('expiration_date'),
                                    "expiration_value"  : av.get('expiration_value'),
                                    })
                        
        
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
    
    return program_voucher_list

@reward_program_setup_bp.route('/show-program-configuration', methods=['GET'])
@login_required
def show_program_configuration(): 
    logger.debug('---show_program_configuration---')
    
    program_key = request.args.get('program_key')
    
    program_configuration = {}
    
    db_client = create_db_client(caller_info="show_program_configuration")
    try:
        
        with db_client.context():
            program = MerchantProgram.fetch(program_key)
            program_configuration = program.to_configuration()
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
       

    return jsonify(program_configuration)
    
    
@reward_program_setup_bp.route('/show-all-program-configuration', methods=['GET'])
@login_required
def show_all_program_configuration(): 
    logger.debug('---show_all_program_configuration---')
    
    db_client = create_db_client(caller_info="show_program_configuration")
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    if logged_in_merchant_user is None:
        raise abort(401)
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        all_published_program_configuration = merchant_acct.published_program_configuration    
    
    return jsonify(all_published_program_configuration)    
        