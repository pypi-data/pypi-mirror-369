'''
Created on 17 Sep 2021

@author: jacklok
'''

from flask import Blueprint, request, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging, jinja2
from trexlib.utils.string_util import is_empty, is_not_empty
from flask.helpers import url_for
from trexconf import conf
from trexmodel import program_conf
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
from trexmodel.models.datastore.program_models import MerchantTierRewardProgram
from trexadmin.forms.merchant.program_forms import TierRewardProgramDetailsForm,\
    DefineTierRewardProgramTierForm, AddProgramRewardForm,\
    DefineTierRewardProgramRewardForm, ProgramExclusivityForm
from trexadmin.controllers.merchant.reward_program.reward_program_setup_routes import get_program_voucher_listing,\
    get_configured_tags_list
from trexmodel.program_conf import is_tier_reward_program_current_status_reach
from trexadmin.libs.jinja.program_filters import program_completed_status_label as program_completed_status_label_filter,\
    get_entitle_reward_condition_label
from trexadmin.libs.jinja.program_filters import \
        program_reward_expiration_value_label as program_voucher_expiration_value_label_filter, \
        program_voucher_effective_value_label as program_voucher_effective_value_label_filter, \
        program_voucher_effective_type_label as program_voucher_effective_type_label_filter, \
        program_reward_format_label as program_reward_format_label_filter
        
tier_reward_program_setup_bp = Blueprint('tier_reward_program_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/tier-reward-program/')


logger = logging.getLogger('controller')


@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_completed_status_label(context, program_completed_status_code):
    return program_completed_status_label_filter(program_completed_status_code)


@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def unlock_reward_condition_label(context, unlock_reward_condition_code):
    return get_entitle_reward_condition_label(unlock_reward_condition_code)

@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_tier_label(context, tier_index, program_tier_settings_list):
    if program_tier_settings_list:
        for tier_setting in program_tier_settings_list:
            if tier_setting.get('tier_index') == tier_index:
                return tier_setting.get('tier_label')


@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_voucher_effective_type_label(context, code):
    return program_voucher_effective_type_label_filter(code)
    
@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_voucher_expiration_type_label(context, code):
    return program_voucher_expiration_type_label(code)   
    
@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_voucher_effective_value_label(context, voucher_settings):
    return program_voucher_effective_value_label_filter(voucher_settings)        
    
@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_voucher_expiration_value_label(context, voucher_settings):
    return program_voucher_expiration_value_label_filter(voucher_settings)    

@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def program_reward_format_label(context, code):
    return program_reward_format_label_filter(code)


@jinja2.contextfilter
@tier_reward_program_setup_bp.app_template_filter()
def action_after_unlock_tier_desc(context, tier_setting):
    action_after_unlock = tier_setting.get('action_after_unlock')
    if action_after_unlock== program_conf.ACTION_AFTER_UNLOCK_TIER_NO_ACTION or action_after_unlock is None:
        return gettext('No action')
    elif action_after_unlock== program_conf.ACTION_AFTER_UNLOCK_TIER_CONSUME_REWARD:
        consume_reward_format = tier_setting.get('consume_reward_format')
        consume_reward_amount = tier_setting.get('consume_reward_amount')
        if consume_reward_format==program_conf.REWARD_FORMAT_POINT:
            return gettext('Consume %d point') % int(consume_reward_amount)
        elif consume_reward_format==program_conf.REWARD_FORMAT_STAMP:
            return gettext('Consume %d stamp') % int(consume_reward_amount)


@tier_reward_program_setup_bp.context_processor
def tier_reward_setup_bp_settings_bp_inject_settings():
    
    return dict(
                TIER_REWARD_PROGRAM_STATUS_PROGRAM_BASE             = program_conf.PROGRAM_STATUS_PROGRAM_BASE,
                TIER_REWARD_PROGRAM_STATUS_DEFINE_TIER              = program_conf.PROGRAM_STATUS_DEFINE_TIER,
                TIER_REWARD_PROGRAM_STATUS_DEFINE_REWARD            = program_conf.PROGRAM_STATUS_DEFINE_REWARD,
                TIER_REWARD_PROGRAM_STATUS_EXCLUSIVITY              = program_conf.PROGRAM_STATUS_EXCLUSIVITY,
                TIER_REWARD_PROGRAM_STATUS_REVIEW                   = program_conf.PROGRAM_STATUS_REVIEW,
                TIER_REWARD_PROGRAM_STATUS_PUBLISH                  = program_conf.PROGRAM_STATUS_PUBLISH,
                )

    
@tier_reward_program_setup_bp.route('/', methods=['GET'])
@login_required
def manage_tier_reward():
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    tier_reward_program_list    = []
    db_client = create_db_client(caller_info="manage_tier_reward")
    try:
        with db_client.context(): 
            merchant_acct                   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            __tier_reward_program_list      = MerchantTierRewardProgram.list_by_merchant_acct(merchant_acct)
            if __tier_reward_program_list:
                for tier_reward_program in __tier_reward_program_list:
                    tier_reward_program_list.append(tier_reward_program.to_dict())
                        
            
    except:
        logger.error('Fail to show manage tier reward program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/tier_reward_program/manage_tier_reward_program.html',
                           page_title                       = gettext('Tier Reward Program Setup'),
                           tier_reward_program_list         = tier_reward_program_list,
                           )


@tier_reward_program_setup_bp.route('/list', methods=['GET'])
@login_required
def tier_reward_program_listing_content():
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    tier_reward_program_list    = []
    db_client = create_db_client(caller_info="tier_reward_program_listing_content")
    try:
        with db_client.context(): 
            merchant_acct                   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            __tier_reward_program_list      = MerchantTierRewardProgram.list_by_merchant_acct(merchant_acct)
            if __tier_reward_program_list:
                for tier_reward_program in __tier_reward_program_list:
                    tier_reward_program_list.append(tier_reward_program.to_dict())
                        
            
    except:
        logger.error('Fail to show manage prepaid program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/tier_reward_program/tier_reward_program_listing_content.html',
                           page_title                       = gettext('Tier Reward Program Setup'),
                           tier_reward_program_list         = tier_reward_program_list,
                           )

@tier_reward_program_setup_bp.route('/create', methods=['GET'])
@login_required
def create_tier_reward_program():
    currency_details            = get_merchant_configured_currency_details()
    
    return render_template('merchant/loyalty/tier_reward_program/create_tier_reward_program.html',
                            page_title                                       = gettext('Tier Reward Program Setting'),
                            
                            define_program_base_url                          = url_for('tier_reward_program_setup_bp.define_program_base_post'),
                            define_program_tier_url                          = url_for('tier_reward_program_setup_bp.define_program_tier_post'),
                            define_program_reward_url                        = url_for('tier_reward_program_setup_bp.define_program_reward_post'),
                            define_program_exclusivity_url                   = url_for('tier_reward_program_setup_bp.define_program_exclusivity_post'),
                            show_define_program_reward_url                   = url_for('tier_reward_program_setup_bp.define_program_reward'),
                            
                            show_program_review_url                          = url_for('tier_reward_program_setup_bp.show_program_review'),
                            publish_program_url                              = url_for('tier_reward_program_setup_bp.publish_program_post'),
                            
                            configured_tag_list                             = get_configured_tags_list(),
                            
                            currency_details                                 = currency_details,
                           )

@tier_reward_program_setup_bp.route('/<program_key>/program-reward/<reward_index>', methods=['DELETE'])
@login_required
def remove_program_reward_post(program_key, reward_index):
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client               = create_db_client(caller_info="remove_program_reward_post")
        
    if is_not_empty(program_key):
        try:
            with db_client.context():
                program             = MerchantTierRewardProgram.fetch(program_key)
                if program:
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    MerchantTierRewardProgram.remove_program_reward(program, reward_index, modified_by=merchant_user)
                    
                    return create_rest_message(status_code=StatusCode.NO_CONTENT)
                    
        except:
            logger.error('Fail to remove tier reward program reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to remove program reward'), status_code=StatusCode.BAD_REQUEST)
                        
@tier_reward_program_setup_bp.route('/program-reward', methods=['POST'])
@login_required
def add_program_reward_post():
    program_reward_settings_data    = request.form
    program_reward_settings_form    = AddProgramRewardForm(program_reward_settings_data)
    
    logger.debug('program_reward_settings_data=%s', program_reward_settings_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = program_reward_settings_form.program_key.data
    
    logger.debug('program_key=%s', program_key)
    
    if program_reward_settings_form.validate():
    
        db_client               = create_db_client(caller_info="add_program_reward_post")
        
        if is_not_empty(program_key):
            try:
                with db_client.context():
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    program             = MerchantTierRewardProgram.fetch(program_key)
                    if program:
                        MerchantTierRewardProgram.add_program_reward(program, 
                                                                     tier_index             = program_reward_settings_form.program_tier.data, 
                                                                     merchant_voucher_key   = program_reward_settings_form.voucher_key.data, 
                                                                     voucher_amount         = program_reward_settings_form.voucher_amount.data,
                                                                     use_online             = program_reward_settings_form.use_online.data, 
                                                                     use_in_store           = program_reward_settings_form.use_in_store.data, 
                                                                     effective_type         = program_reward_settings_form.effective_type.data,
                                                                     effective_value        = program_reward_settings_form.effective_value.data,
                                                                     effective_date         = program_reward_settings_form.effective_date.data,
                                                                     expiration_type        = program_reward_settings_form.expiration_type.data,
                                                                     expiration_value       = program_reward_settings_form.expiration_value.data,
                                                                     expiration_date        = program_reward_settings_form.expiration_date.data,
                                                                     modified_by            = merchant_user
                                                                     )
                        
                
                return create_rest_message(gettext('Added program reward successfully'),status_code=StatusCode.CREATED)
            
            except:
                logger.error('Fail to add tier reward program reward due to %s', get_tracelog())
                return create_rest_message(gettext('Failed to add program reward'), status_code=StatusCode.BAD_REQUEST)
        
        else:
            logger.warn('program_key is empty')
            return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
        
    else:
        error_message = program_reward_settings_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)  

@tier_reward_program_setup_bp.route('/define-program-reward', methods=['GET'])
@login_required
def define_program_reward():
    program_key                     = request.args.get('program_key')
    program_reward_settings_list    = []
    program_tier_settings_list      = []
    db_client = create_db_client(caller_info="define_program_reward")
    try:
        with db_client.context(): 
            program                         = MerchantTierRewardProgram.fetch(program_key)
            if program:
                program_details              = program.to_dict()
                program_reward_settings_list = program.program_rewards
                program_tier_settings_list   = program.program_tiers
                
                logger.debug('program=%s', program)
                
                        
            
    except:
        logger.error('Fail to show manage prepaid program due to %s', get_tracelog())
        
    return render_template('merchant/loyalty/tier_reward_program/define_tier_reward_program_reward_input_content.html',
                            program                         = program_details,
                            add_program_reward_url          = url_for('tier_reward_program_setup_bp.add_program_reward_post'),
                            reload_program_reward_url       = url_for('tier_reward_program_setup_bp.show_program_reward_listing', program_key=program_key),
                            reward_format                   = program.reward_format,
                            program_tier_settings_list      = program_tier_settings_list,
                            program_reward_settings_list    = program_reward_settings_list,
                           )

@tier_reward_program_setup_bp.route('/show-program-reward-listing', methods=['GET'])
@login_required
def show_program_reward_listing():
    program_key                     = request.args.get('program_key')
    program_reward_settings_list    = []
    program_tier_settings_list      = []
    db_client = create_db_client(caller_info="show_program_reward_listing")
    try:
        with db_client.context(): 
            program                         = MerchantTierRewardProgram.fetch(program_key)
            if program:
                program_reward_settings_list = program.program_rewards
                program_tier_settings_list   = program.program_tiers
                
                        
            
    except:
        logger.error('Fail to show manage prepaid program due to %s', get_tracelog())
        
    return render_template('merchant/loyalty/tier_reward_program/tier_reward_program_reward_listing_content.html',
                            reward_format                   = program.reward_format,
                            program_tier_settings_list      = program_tier_settings_list,
                            program_reward_settings_list    = program_reward_settings_list,
                            program_key                     = program_key,
                           )

@tier_reward_program_setup_bp.route('/define-program-reward', methods=['POST'])
@login_required
def define_program_reward_post():
    program_reward_settings_data = request.form
    program_reward_settings_form = DefineTierRewardProgramRewardForm(program_reward_settings_data)
    
    logger.debug('program_reward_settings_form=%s', program_reward_settings_form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = program_reward_settings_form.program_key.data
    
    logger.debug('program_key=%s', program_key)
    
    is_all_tier_reward_defined = True 
    
    if program_reward_settings_form.validate():
    
        db_client               = create_db_client(caller_info="define_program_reward_post")
        
        if is_not_empty(program_key):
            try:
                with db_client.context():
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    program             = MerchantTierRewardProgram.fetch(program_key)
                    if program:
                        program_rewards = program.program_rewards
                        if is_not_empty(program_rewards):
                            
                            program_tiers = program.program_tiers
                            for tier_setting in program_tiers:
                                if is_empty(tier_setting.get('reward_items')):
                                    is_all_tier_reward_defined=False
                                    break
                                
                            if is_all_tier_reward_defined:
                                MerchantTierRewardProgram.update_program_reward_settings(program, modified_by=merchant_user)
                
                if is_not_empty(program_rewards):
                    if is_all_tier_reward_defined: 
                        return create_rest_message(status_code=StatusCode.OK)
                    else:
                        return create_rest_message(gettext('Some tier did not define reward'), status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message(gettext('Please define program reward'), status_code=StatusCode.BAD_REQUEST)
            
            except:
                logger.error('Fail to define tier reward program reward settings due to %s', get_tracelog())
                return create_rest_message(gettext('Failed to define program reward'), status_code=StatusCode.BAD_REQUEST)
        
        else:
            logger.warn('program_key is empty')
            return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
        
    else:
        error_message = program_reward_settings_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST) 
    
@tier_reward_program_setup_bp.route('/define-program-tier', methods=['POST'])
@login_required
def define_program_tier_post():
    program_tier_settings_data = request.form
    program_tier_settings_form = DefineTierRewardProgramTierForm(program_tier_settings_data)
    
    logger.debug('program_tier_settings_data=%s', program_tier_settings_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = program_tier_settings_form.program_key.data
    
    logger.debug('program_key=%s', program_key)
    
    if program_tier_settings_form.validate():
    
        db_client               = create_db_client(caller_info="define_program_tier_post")
        
        if is_not_empty(program_key):
            invalid_unlock_condition  = False
            try:
                with db_client.context():
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    program             = MerchantTierRewardProgram.fetch(program_key)
                    if program:
                        program_tier_settings = program_tier_settings_form.program_tier_settings.data
                        #check program tier settings
                        selected_unlock_conditin = None
                        for tier_setting in program_tier_settings:
                            if selected_unlock_conditin is None:
                                selected_unlock_conditin = tier_setting.get('unlock_condition')
                                
                            elif selected_unlock_conditin:
                                if selected_unlock_conditin!=tier_setting.get('unlock_condition'):
                                    logger.warn('unlock condition must be same for each tier')
                                    invalid_unlock_condition = True
                                    break
                            
                        logger.debug('program_tier_settings=%s', program_tier_settings)
                        if invalid_unlock_condition == False:    
                            MerchantTierRewardProgram.update_program_tier_settings(program, program_tier_settings, modified_by=merchant_user)
                
                #TODO: might change to support multiple unlock condition in future 
                if invalid_unlock_condition:
                    return create_rest_message(gettext('Unlock tier condition must be same'), status_code=StatusCode.BAD_REQUEST)
                else:
                    if program:
                        return create_rest_message(status_code=StatusCode.NO_CONTENT)
                    else:
                        return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
            
            except:
                logger.error('Fail to define tier reward program tier settings due to %s', get_tracelog())
                return create_rest_message(gettext('Failed to define tier reward program tier settings'), status_code=StatusCode.BAD_REQUEST)
        
        else:
            logger.warn('program_key is empty')
            return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
        
    else:
        error_message = program_tier_settings_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)  

@tier_reward_program_setup_bp.route('/define-program-exclusivity', methods=['POST'])
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
                    program = MerchantTierRewardProgram.fetch(program_key)
                    if program:
                        
                        tags_list = program_exclusivity_form.tags_list.data
                        if is_not_empty(tags_list):
                            tags_list = tags_list.split(',')
                            
                            tags_list = [x for x in tags_list if x]
                            
                        membership_key_list = program_exclusivity_form.membership_key.data
                        if is_not_empty(membership_key_list):
                            membership_key_list = membership_key_list.split(',')
                            
                            membership_key_list = [x for x in membership_key_list if x]
                            
                        tier_membership_key_list = program_exclusivity_form.tier_membership_key.data
                        if is_not_empty(tier_membership_key_list):
                            tier_membership_key_list = tier_membership_key_list.split(',')       
                            
                            tier_membership_key_list = [x for x in tier_membership_key_list if x] 
                        
                        exclusivity_configuration = {
                                                    'tags'              : tags_list,
                                                    'memberships'       : membership_key_list,
                                                    'tier_memberships'  : tier_membership_key_list,
                                                    }
                        
                        logger.debug('exclusivity_configuration=%s', exclusivity_configuration)
                        
                        logger.debug('program.completed_status=%s', program.completed_status)
                        
                        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                        MerchantTierRewardProgram.update_prorgram_exclusivity_data(program, 
                                                                         exclusivity_configuration  = exclusivity_configuration, 
                                                                         modified_by                = merchant_user
                                                                         )
                        
                except:
                    logger.error('Failed to update exclusivity due to %s', get_tracelog())
                    
        if program:
            return create_rest_message(status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
            
            
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)


@tier_reward_program_setup_bp.route('/show-program-review', methods=['GET'])
@login_required
def show_program_review():
    logger.debug('---show_program_review---')
    
    program_key             = request.args.get('program_key')
    program_voucher_list    = get_program_voucher_listing(program_key)
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="show_program_review")
    try:
        
        with db_client.context():
            program = MerchantTierRewardProgram.fetch(program_key)
            program = program.to_dict()
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/tier_reward_program/tier_reward_program_review_content.html', 
                           program                  = program,
                           program_voucher_list     = program_voucher_list,
                           )

@tier_reward_program_setup_bp.route('/publish-program', methods=['POST'])
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
                
                program = MerchantTierRewardProgram.fetch(program_key)
                if program:
                    MerchantTierRewardProgram.publish_program(program)
                    
        if program:
            return create_rest_message(status_code=StatusCode.OK)
        
        else:
            return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
            
            
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@tier_reward_program_setup_bp.route('/archive-program', methods=['POST','GET'])
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
                
                program = MerchantTierRewardProgram.fetch(program_key)
                if program:
                    MerchantTierRewardProgram.archive_program(program)
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to archive merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@tier_reward_program_setup_bp.route('/enable/<program_key>', methods=['POST','GET'])
@login_required
def enable_program(program_key):
    return enable_or_disable_program(program_key, True)

@tier_reward_program_setup_bp.route('/disable/<program_key>', methods=['POST','GET'])
@login_required
def disable_program(program_key):
    return enable_or_disable_program(program_key, False)


def enable_or_disable_program(program_key, to_enable): 
    
    logger.debug('program_key=%s', program_key)
    db_client               = create_db_client(caller_info="enable_or_disable_program")
    
    try:
        with db_client.context():
            if is_empty(program_key):
                return create_rest_message(gettext('Invaid program data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                logged_in_merchant_user = get_loggedin_merchant_user_account()
                merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                program                 = MerchantTierRewardProgram.fetch(program_key)
                if program:
                    if to_enable:
                        MerchantTierRewardProgram.enable(program, modified_by=merchant_user) 
                        logger.debug('Program have been enabled')
                    else:
                        MerchantTierRewardProgram.disable(program, modified_by=merchant_user)
                        logger.debug('Program have been disabled')
                else:
                    logger.warn('program is not found')
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)
    

@tier_reward_program_setup_bp.route('/create', methods=['POST'])
@login_required
def define_program_base_post():
    logger.debug('---define_program_base_post---')
    
    program_details_data = request.form
    program_details_form = TierRewardProgramDetailsForm(program_details_data)
    
    logger.debug('program_details_data=%s', program_details_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key = program_details_form.program_key.data
    
    logger.debug('program_key=%s', program_key)
    
    if program_details_form.validate():
    
        db_client               = create_db_client(caller_info="define_program_base_post")
        try:
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                if is_empty(program_key):
                    logger.debug('Going to create merchant tier reward program')
                    
                    merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                    program             = MerchantTierRewardProgram.create(merchant_acct, 
                                                             label             = program_details_form.program_label.data,
                                                             desc              = program_details_form.desc.data,
                                                             reward_format     = program_details_form.reward_format.data,
                                                             is_tier_recycle   = program_details_form.is_tier_recycle.data,
                                                             is_show_progress  = program_details_form.is_show_progress.data,
                                                             
                                                             start_date        = program_details_form.start_date.data,
                                                             end_date          = program_details_form.end_date.data,
                                                             created_by        = merchant_user,
                                                             )
                    
                    program_key         = program.key_in_str
                    
                    return create_rest_message(status_code=StatusCode.CREATED, 
                                    program_key    = program_key,
                                    )
                    
                else:
                    logger.debug('Going to update merchant tier reward program')
                    program = MerchantTierRewardProgram.fetch(program_key)
                    if program:
                        
                        MerchantTierRewardProgram.update(
                                                         program,
                                                         label             = program_details_form.program_label.data,
                                                         desc              = program_details_form.desc.data,
                                                         reward_format     = program_details_form.reward_format.data,
                                                         is_tier_recycle   = program_details_form.is_tier_recycle.data,
                                                         is_show_progress  = program_details_form.is_show_progress.data,
                                                         
                                                         start_date        = program_details_form.start_date.data,
                                                         end_date          = program_details_form.end_date.data,
                                                         modified_by       = merchant_user,
                                                        )
                        
                        return create_rest_message(status_code=StatusCode.OK,
                                                   program_key  = program_key,
                                                   )
                    else:
                        return create_rest_message(gettext('Invalid program data'), status_code=StatusCode.BAD_REQUEST)
                    
        
        except:
            logger.error('Fail to create merchant program due to %s', get_tracelog())
            if is_empty(program_key):
                return create_rest_message(gettext('Failed to create merchant program'), status_code=StatusCode.BAD_REQUEST)
            else:
                return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        
        
    else:
        error_message = program_details_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)    

@tier_reward_program_setup_bp.route('/view-program/<program_key>', methods=['GET'])
@login_required
def view_program(program_key): 
    logger.debug('---view_program---')
    program                 = None
    
    if is_not_empty(program_key):
        db_client           =  create_db_client(caller_info="view_program")
        currency_details    = get_merchant_configured_currency_details()
        try:
            with db_client.context():
                program                         = MerchantTierRewardProgram.fetch(program_key)
                program_reward_settings_list    = program.program_rewards
                program_details                 = program.to_dict()
            
            return render_template('merchant/loyalty/tier_reward_program/view_tier_reward_program.html',
                           is_view_program                              = True,
                           program                                      = program_details,
                           
                           reward_format                                = program_details.get('reward_format'),
                           program_reward_settings_list                 = program_reward_settings_list,
                           program_tier_settings_list                   = program_details.get('program_settings').get('tiers'),
                           
                           exclusive_tags_list                          = program.exclusive_tags_list,
                           exclusive_membership_list                    = program.exclusive_memberships_list,
                           exclusive_tier_membership_list               = program.exclusive_tier_memberships_list,
                            
                           configured_tag_list                          = get_configured_tags_list(),
                           
                           currency_details                             = currency_details,
                           )
                
        except:
            logger.error('Fail to view merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to view merchant program'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to view merchant program'), status_code=StatusCode.BAD_REQUEST)

@tier_reward_program_setup_bp.route('/edit-program/<program_key>', methods=['GET'])
@login_required
def edit_program(program_key): 
    logger.debug('---edit_program---')
    program                         = None
    
    if is_not_empty(program_key):
        
        currency_details    = get_merchant_configured_currency_details()
        db_client           = create_db_client(caller_info="edit_program")
        try:
            with db_client.context():
                program = MerchantTierRewardProgram.fetch(program_key) 
                program_reward_settings_list = program.program_rewards
                program_details = program.to_dict()
                
                
            is_tier_reward_program_review_step = program_conf.is_valid_to_update_tier_reward_program_status(program_conf.PROGRAM_STATUS_PUBLISH, program.completed_status)
            
            
             
            return render_template('merchant/loyalty/tier_reward_program/create_tier_reward_program.html',
                            define_program_base_url                          = url_for('tier_reward_program_setup_bp.define_program_base_post'),
                            define_program_tier_url                          = url_for('tier_reward_program_setup_bp.define_program_tier_post'),
                            add_program_reward_url                           = url_for('tier_reward_program_setup_bp.add_program_reward_post'),   
                            define_program_reward_url                        = url_for('tier_reward_program_setup_bp.define_program_reward_post'),
                            define_program_exclusivity_url                   = url_for('tier_reward_program_setup_bp.define_program_exclusivity_post'),
                            show_define_program_reward_url                   = url_for('tier_reward_program_setup_bp.define_program_reward'),
                            
                            reload_program_reward_url                        = url_for('tier_reward_program_setup_bp.show_program_reward_listing', program_key=program_key),
                            
                            show_program_review_url                          = url_for('tier_reward_program_setup_bp.show_program_review'),
                            publish_program_url                              = url_for('tier_reward_program_setup_bp.publish_program_post'),
                            
                            TIER_REWARD_PROGRAM_STATUS_PROGRAM_BASE_COMPLETED           = True,
                            TIER_REWARD_PROGRAM_STATUS_DEFINE_TIER_COMPLETED            = is_tier_reward_program_current_status_reach(program_conf.PROGRAM_STATUS_DEFINE_TIER, program.completed_status),
                            TIER_REWARD_PROGRAM_STATUS_DEFINE_REWARD_COMPLETED          = is_tier_reward_program_current_status_reach(program_conf.PROGRAM_STATUS_DEFINE_REWARD, program.completed_status),
                            TIER_REWARD_PROGRAM_STATUS_EXCLUSIVITY_COMPLETED            = is_tier_reward_program_current_status_reach(program_conf.PROGRAM_STATUS_EXCLUSIVITY, program.completed_status),
                            
                            TIER_REWARD_PROGRAM_STATUS_REVIEW_COMPLETED                 = is_tier_reward_program_current_status_reach(program_conf.PROGRAM_STATUS_REVIEW, program.completed_status),
                            TIER_REWARD_PROGRAM_STATUS_PUBLISH_COMPLETED                = is_tier_reward_program_current_status_reach(program_conf.PROGRAM_STATUS_PUBLISH, program.completed_status),
                            
                            program                                      = program_details,
                            reward_format                                = program_details.get('reward_format'),
                            program_reward_settings_list                 = program_reward_settings_list,
                            program_tier_settings_list                   = program_details.get('program_settings').get('tiers'),
                            
                            program_completed_status                     = program.completed_status,
                            is_program_review_step                       = is_tier_reward_program_review_step,
                            is_edit_program                              = True,
                            
                            
                            program_key                                  = program_key,
                           
                            exclusive_tags_list                          = program.exclusive_tags_list,
                            exclusive_membership_list                    = program.exclusive_memberships_list,
                            exclusive_tier_membership_list               = program.exclusive_tier_memberships_list,
                            
                            configured_tag_list                          = get_configured_tags_list(), 
                            
                            currency_details                             = currency_details,
                           
                           )
                
        except:
            logger.error('Fail to read merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        
    else:
        return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
    
    
@tier_reward_program_setup_bp.route('/define-program-reward', methods=['GET'])
@login_required
def define_program_tier_reward():
    program_key                 = request.args.get('program_key')
    program_tier_settings_list  = []
    db_client                   = create_db_client(caller_info="define_program_tier_reward")
    try:
        with db_client.context(): 
            program                     = MerchantTierRewardProgram.fetch(program_key)
            program_tier_settings_list  = program.program_settings.get('tiers') 
            
    except:
        logger.error('Fail to show manage prepaid program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/tier_reward_program/define_tier_reward_program_reward_content.html',
                           program_tier_settings_list         = program_tier_settings_list,
                           )    
    