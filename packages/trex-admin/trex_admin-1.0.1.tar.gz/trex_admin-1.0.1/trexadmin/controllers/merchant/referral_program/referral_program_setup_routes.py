'''
Created on 8 Apr 2024

@author: jacklok
'''

from flask import Blueprint, render_template, request, abort
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty, random_string
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.program_conf import is_referral_program_current_status_reach
import trexmodel.program_conf as program_conf
from trexlib.utils.common.common_util import sort_list

import jinja2, json
from flask.json import jsonify
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
    
from trexconf import conf
from trexmodel.models.datastore.referral_program_model import MerchantReferralProgram
from trexadmin.forms.merchant.referral_program_forms import ReferralProgramDetailsForm
from trexadmin.forms.merchant.program_forms import ProgramVoucherRewardForm,\
    ProgramPointRewardForm, ProgramStampRewardForm, ProgramPrepaidRewardForm
from trexadmin.libs.jinja.program_filters import program_reward_expiration_value_label as program_reward_expiration_value_label_filter

referral_program_setup_bp = Blueprint('referral_program_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/referral-program/program-setup')


logger = logging.getLogger('controller')


@jinja2.contextfilter
@referral_program_setup_bp.app_template_filter()
def program_reward_expiration_value_label(context, reward_settings):
    return program_reward_expiration_value_label_filter(reward_settings)

'''
Blueprint settings here
'''
@referral_program_setup_bp.context_processor
def referral_program_setup_bp_inject_settings():
    
    return dict(
               PROGRAM_STATUS_PROGRAM_BASE                  = program_conf.PROGRAM_STATUS_PROGRAM_BASE,
               PROGRAM_STATUS_DEFINE_REFERRER_REWARD        = program_conf.PROGRAM_STATUS_DEFINE_REFERRER_REWARD,
               PROGRAM_STATUS_DEFINE_REFEREE_REWARD         = program_conf.PROGRAM_STATUS_DEFINE_REFEREE_REWARD,
               PROGRAM_STATUS_DEFINE_PROMOTE_TEXT           = program_conf.PROGRAM_STATUS_DEFINE_PROMOTE_TEXT, 
               PROGRAM_STATUS_UPLOAD_MATERIAL               = program_conf.PROGRAM_STATUS_UPLOAD_MATERIAL,
               PROGRAM_STATUS_REVIEW                        = program_conf.PROGRAM_STATUS_REVIEW,
               PROGRAM_STATUS_PUBLISH                       = program_conf.PROGRAM_STATUS_PUBLISH,
               
               REFERRAL_PROGRAM_STATUS                      = program_conf.REFERRAL_PROGRAM_STATUS,
               
               REWARD_FORMAT_PREPAID                        = program_conf.REWARD_FORMAT_PREPAID,
               REWARD_FORMAT_POINT                          = program_conf.REWARD_FORMAT_POINT,
               REWARD_FORMAT_STAMP                          = program_conf.REWARD_FORMAT_STAMP,
               REWARD_FORMAT_VOUCHER                        = program_conf.REWARD_FORMAT_VOUCHER,
               
               REFERRAL_PROGRAM_DEFAULT_PROMOTE_IMAGE_URL   = conf.REFERRAL_DEFAULT_PROMOTE_IMAGE,
                              
               )
    

@referral_program_setup_bp.route('/', methods=['GET'])
@login_required
def referral_programs_listing(): 
    logger.debug('---referral_programs_listing---')
    
    return latest_program_listing(
                                'merchant/loyalty/referral_program/program_setup/program_overview.html',
                                ) 


def latest_program_listing(template_name, show_page_title=True): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    referral_programs_list = []
    
    db_client = create_db_client(caller_info="latest_program_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
                __referral_programs_list  = sort_list(MerchantReferralProgram.list_by_merchant_account(merchant_acct), 'created_datetime', reverse_order=True)
            
            for mp in __referral_programs_list:
                referral_programs_list.append(mp.to_dict())
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    logger.debug('referral_programs_list=%s', referral_programs_list)
    
    return render_template(template_name, 
                           page_title                   = gettext('Referral Program Overview') if show_page_title else None,
                           page_url                     = url_for('referral_program_setup_bp.referral_programs_listing') if show_page_title else None,
                           latest_program_listing_url   = url_for('referral_program_setup_bp.show_latest_program_listing'),
                           archived_program_listing_url = url_for('referral_program_setup_bp.archived_program_listing'),
                           referral_programs_list       = referral_programs_list,
                           ) 
    
@referral_program_setup_bp.route('/latest-program-listing', methods=['GET'])
@login_required
def show_latest_program_listing(): 
    
    return latest_program_listing(
                                'merchant/loyalty/referral_program/program_setup/latest_program_listing_content.html', 
                                show_page_title=False
                                )   
    
@referral_program_setup_bp.route('/archived-program', methods=['GET'])
@login_required
def archived_program_listing(): 
    logger.debug('---archived_program_listing---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_programs_list = []
    
    db_client = create_db_client(caller_info="archived_program_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
         
                __merchant_programs_list  = sort_list(MerchantReferralProgram.list_archived_by_merchant_account(merchant_acct), 'created_datetime', reverse_order=True)
            
            for mp in __merchant_programs_list:
                merchant_programs_list.append(mp.to_dict())
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
    
    
    return render_template('merchant/loyalty/referral_program/program_setup/archived_program.html',
                           merchant_programs_list   = merchant_programs_list,
                           )     

@referral_program_setup_bp.route('/define-program-base', methods=['POST'])
@login_required
def define_program_base_post(): 
    logger.debug('---define_program_base_post---')
    
    program_base_data   = request.form
    program_base_form   = ReferralProgramDetailsForm(program_base_data)
    logger.debug('referral program_base_data=%s', program_base_data)
    
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
                    program             = MerchantReferralProgram.create(merchant_acct, 
                                                             label                  = program_base_form.label.data,
                                                             desc                   = program_base_form.desc.data,
                                                             start_date             = program_base_form.start_date.data,
                                                             end_date               = program_base_form.end_date.data,
                                                             created_by             = merchant_user,
                                                             loyalty_package        = merchant_acct.loyalty_package,
                                                             default_promote_image  = conf.REFERRAL_DEFAULT_PROMOTE_IMAGE
                                                             )
                    
                    program_key         = program.key_in_str
                    return create_rest_message(status_code=StatusCode.CREATED, 
                                    program_key                             = program_key,
                                    )
                else:
                    
                    program = MerchantReferralProgram.fetch(program_key)
                    if program: 
                        MerchantReferralProgram.update_program_base_data(program, 
                                                                  label                 = program_base_form.label.data,
                                                                  desc                  = program_base_form.desc.data,
                                                                  start_date            = program_base_form.start_date.data,
                                                                  end_date              = program_base_form.end_date.data,
                                                                  modified_by           = merchant_user,
                                                                  default_promote_image = conf.REFERRAL_DEFAULT_PROMOTE_IMAGE
                                                                  )
                        
                        return create_rest_message(status_code=StatusCode.OK, 
                                                    program_key  = program_key,
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

@referral_program_setup_bp.route('/define-referrer-reward-details', methods=['POST'])
@login_required
def define_referrer_reward_details_post(): 
    logger.debug('---define_referrer_reward_details_post---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    program_key             = request.form.get('program_key') or request.args.get('program_key')
    db_client               = create_db_client(caller_info="define_referrer_reward_details_post")
    
    logger.debug('define_referrer_reward_details_post debug: program_key=%s', program_key)
        
    try:
        with db_client.context():
            merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            program = MerchantReferralProgram.fetch(program_key)
            if program: 
                MerchantReferralProgram.define_referrer_reward(program, modified_by = merchant_user
                                                              )
                    
                return create_rest_message(status_code=StatusCode.OK)
            else:
                return create_rest_message(gettext('Invalid program'),status_code=StatusCode.BAD_REQUEST)
                                        
    except:
        logger.error('Fail to define program referrer reward due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to create merchant program'), status_code=StatusCode.BAD_REQUEST)
    
@referral_program_setup_bp.route('/define-referee-reward-details', methods=['POST'])
@login_required
def define_referee_reward_details_post(): 
    logger.debug('---define_referee_reward_details_post---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    program_key             = request.form.get('program_key') or request.args.get('program_key')
    db_client               = create_db_client(caller_info="define_referee_reward_details_post")
    
    logger.debug('define_referee_reward_details_post debug: program_key=%s', program_key)
        
    try:
        with db_client.context():
            merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            program = MerchantReferralProgram.fetch(program_key)
            if program: 
                MerchantReferralProgram.define_referee_reward(program, modified_by = merchant_user
                                                              )
                    
                return create_rest_message(status_code=StatusCode.OK)
                                        
    except:
        logger.error('Fail to define program referee reward due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to create merchant program'), status_code=StatusCode.BAD_REQUEST)
    

@referral_program_setup_bp.route('/show-program-review', methods=['GET'])
@login_required
def show_program_review(): 
    logger.debug('---show_program_review---')
    
    program_key             = request.form.get('program_key') or request.args.get('program_key')
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="show_program_review")
    try:
        
        with db_client.context():
            program = MerchantReferralProgram.fetch(program_key)
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/program_setup/program_review_content.html', 
                           program                  = program.to_dict(),
                           )



@referral_program_setup_bp.route('/show-referrer-program-reward-listing', methods=['GET'])
@login_required
def show_referrer_program_reward_listing(): 
    logger.debug('---show_referrer_program_reward_listing---')
    
    program_key             = request.form.get('program_key') or request.args.get('program_key')
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="show_referrer_program_reward_listing")
    try:
        
        with db_client.context():
            program                             = MerchantReferralProgram.fetch(program_key)
            referrer_program_reward_list        = get_referrer_program_reward_listing(program)
            
            
    except:
        logger.error('Fail to get program referrer due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/program_setup/reward_details_input/program_referral_reward_listing_content.html', 
                           program                              = program.to_dict(),
                           program_reward_list                  = referrer_program_reward_list,
                           program_key                          = program_key,
                           show_listing_only                    = True,
                           remove_program_reward_delete_url     = url_for('referral_program_setup_bp.remove_referrer_program_reward_delete'),
                           )
    
@referral_program_setup_bp.route('/show-referee-program-reward-listing', methods=['GET'])
@login_required
def show_referee_program_reward_listing(): 
    logger.debug('---show_referrer_program_reward_listing---')
    
    program_key             = request.form.get('program_key') or request.args.get('program_key')
    
    logger.debug('program_key=%s', program_key)
    
    db_client = create_db_client(caller_info="show_referrer_program_reward_listing")
    try:
        
        with db_client.context():
            program     = MerchantReferralProgram.fetch(program_key)
            referee_program_reward_list    = get_referee_program_reward_listing(program)
            
            
    except:
        logger.error('Fail to get program referee voucher due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/program_setup/reward_details_input/program_referral_reward_listing_content.html', 
                           program                          = program.to_dict(),
                           program_reward_list              = referee_program_reward_list,
                           program_key                      = program_key,
                           show_listing_only                = True,
                           remove_program_reward_delete_url = url_for('referral_program_setup_bp.remove_referee_program_reward_delete'),
                           )    

def get_referrer_program_reward_listing(program): 
    logger.debug('---get_referrer_program_reward_listing---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    program_reward_list = []
    
    added_program_reward_list      = program.program_settings.get('referrer_reward_items') or []
            
            
    for program_reward in added_program_reward_list:
        if program_reward.get('reward_type') == 'point':
            program_reward_list.append(__contruct_point_json(program_reward))
        elif program_reward.get('reward_type') == 'stamp':
            program_reward_list.append(__contruct_stamp_json(program_reward))
        elif program_reward.get('reward_type') == 'prepaid':
            program_reward_list.append(__contruct_prepaid_json(program_reward))
        elif program_reward.get('reward_type') == 'voucher':
            program_reward_list.append(__contruct_voucher_json(program_reward))
    
    return program_reward_list

def get_referee_program_reward_listing(program): 
    logger.debug('---get_referee_program_reward_listing---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    program_reward_list = []
    
    added_program_reward_list      = program.program_settings.get('referee_reward_items') or []
            
            
    for program_reward in added_program_reward_list:
        if program_reward.get('reward_type') == 'point':
            program_reward_list.append(__contruct_point_json(program_reward))
        elif program_reward.get('reward_type') == 'stamp':
            program_reward_list.append(__contruct_stamp_json(program_reward))
        elif program_reward.get('reward_type') == 'prepaid':
            program_reward_list.append(__contruct_prepaid_json(program_reward))
        elif program_reward.get('reward_type') == 'voucher':
            program_reward_list.append(__contruct_voucher_json(program_reward))
    
    return program_reward_list

def __contruct_point_json(reward):
    return {
                            "reward_index"      : reward.get('reward_index'),
                            "reward_type"       : reward.get('reward_type'),
                            "point_amount"      : reward.get('point_amount'),
                            "expiration_type"   : reward.get('expiration_type'),
                            "expiration_date"   : reward.get('expiration_date'),
                            "expiration_value"  : reward.get('expiration_value'),
                            }
    
def __contruct_stamp_json(reward):
    return {
                            "reward_index"      : reward.get('reward_index'),
                            "reward_type"       : reward.get('reward_type'),
                            "stamp_amount"      : reward.get('stamp_amount'),
                            "expiration_type"   : reward.get('expiration_type'),
                            "expiration_date"   : reward.get('expiration_date'),
                            "expiration_value"  : reward.get('expiration_value'),
                            } 
    
def __contruct_prepaid_json(reward):
    return {
                            "reward_index"      : reward.get('reward_index'),
                            "reward_type"       : reward.get('reward_type'),
                            "prepaid_amount"    : reward.get('prepaid_amount'),
                            }        
    
def __contruct_voucher_json(reward):
    return {
                            "reward_index"      : reward.get('reward_index'),
                            "reward_type"       : reward.get('reward_type'),
                            "voucher_key"       : reward.get('voucher_key'),
                            "voucher_amount"    : reward.get('voucher_amount'),
                            "use_online"        : reward.get('use_online'),
                            "use_in_store"      : reward.get('use_in_store'),
                            "effective_type"    : reward.get('effective_type'),
                            "effective_date"    : reward.get('effective_date'),
                            "effective_value"   : reward.get('effective_value'),
                            "expiration_type"   : reward.get('expiration_type'),
                            "expiration_date"   : reward.get('expiration_date'),
                            "expiration_value"  : reward.get('expiration_value'),
                            }    

@referral_program_setup_bp.route('/publish-program', methods=['POST','GET'])
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
                
                program = MerchantReferralProgram.fetch(program_key)
                if program:
                    MerchantReferralProgram.publish_program(program)
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@referral_program_setup_bp.route('/create-program', methods=['GET'])
@login_required
def create_program(): 
    logger.debug('---create_program---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client               = create_db_client(caller_info="create_program")
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
    
    return render_template('merchant/loyalty/referral_program/program_setup/create_program.html',
                           define_program_base              = url_for('referral_program_setup_bp.define_program_base_post'),
                           define_referrer_reward           = url_for('referral_program_setup_bp.define_referrer_reward_details_post'),
                           define_referee_reward            = url_for('referral_program_setup_bp.define_referee_reward_details_post'),
                           
                           show_program_review              = url_for('referral_program_setup_bp.show_program_review'),
                           publish_program                  = url_for('referral_program_setup_bp.publish_program_post'),
                           
                           add_referrer_program_point_reward_post_url       = url_for('referral_program_setup_bp.add_referrer_program_point_reward_post'),
                           add_referrer_program_stamp_reward_post_url       = url_for('referral_program_setup_bp.add_referrer_program_stamp_reward_post'),
                           add_referrer_prepaid_reward_post_url             = url_for('referral_program_setup_bp.add_referrer_program_stamp_reward_post'),
                           add_referrer_program_voucher_reward_post_url     = url_for('referral_program_setup_bp.add_referrer_program_voucher_reward_post'),
                           
                           remove_referrer_program_reward_delete_url        = url_for('referral_program_setup_bp.remove_referrer_program_reward_delete'),
                           remove_referee_program_reward_delete_url         = url_for('referral_program_setup_bp.remove_referee_program_reward_delete'),
                           
                           loyalty_package                  = merchant_acct.loyalty_package,
                           #reward_base_list     = reward_base_list,
                           )

   
@referral_program_setup_bp.route('/program-review-content/<program_key>', methods=['GET'])
@login_required
def program_review_content(program_key): 
    logger.debug('---program_review_content---')
    
    db_client               = create_db_client(caller_info="program_review_content")
    with db_client.context():
        program         = MerchantReferralProgram.fetch(program_key)
        program_details = program.to_dict()
        referrer_program_reward_list       = get_referrer_program_reward_listing(program)
        referee_program_reward_list        = get_referee_program_reward_listing(program)
        
        
    
    return render_template('merchant/loyalty/referral_program/program_setup/program_review_content.html',
                           publish_program                  = url_for('referral_program_setup_bp.publish_program_post'),
                           program                          = program_details,
                           program_key                      = program_key,
                           referrer_program_reward_list     = referrer_program_reward_list,
                           referee_program_reward_list      = referee_program_reward_list,
                           )            

@referral_program_setup_bp.route('/edit-program/<program_key>', methods=['GET'])
@login_required
def edit_program(program_key): 
    logger.debug('---edit_program---')
    program                         = None
    
    program_details                 = None
    if is_not_empty(program_key):
        db_client = create_db_client(caller_info="edit_program")
            
        try:
            with db_client.context():
                program         = MerchantReferralProgram.fetch(program_key)
                program_details = program.to_dict()
                referrer_program_reward_list       = get_referrer_program_reward_listing(program)
                referee_program_reward_list        = get_referee_program_reward_listing(program)
                
                
            is_program_review_step = program_conf.is_valid_to_update_referral_program_status(program_conf.PROGRAM_STATUS_PUBLISH, program.completed_status)
             
            return render_template('merchant/loyalty/referral_program/program_setup/create_program.html',
                           define_program_base              = url_for('referral_program_setup_bp.define_program_base_post'),
                           define_referrer_reward           = url_for('referral_program_setup_bp.define_referrer_reward_details_post'),
                           define_referee_reward            = url_for('referral_program_setup_bp.define_referee_reward_details_post'),
                           show_program_review              = url_for('referral_program_setup_bp.show_program_review'),
                           publish_program                  = url_for('referral_program_setup_bp.publish_program_post'),
                           
                           remove_referrer_program_reward_delete_url        = url_for('referral_program_setup_bp.remove_referrer_program_reward_delete'),
                           remove_referee_program_reward_delete_url         = url_for('referral_program_setup_bp.remove_referee_program_reward_delete'),
                           
                           PROGRAM_STATUS_PROGRAM_BASE_COMPLETED            = True,
                           PROGRAM_STATUS_DEFINE_REFERRER_REWARD_COMPLETED  = is_referral_program_current_status_reach(program_conf.PROGRAM_STATUS_DEFINE_REFERRER_REWARD, program.completed_status),
                           PROGRAM_STATUS_DEFINE_REFEREE_REWARD_COMPLETED   = is_referral_program_current_status_reach(program_conf.PROGRAM_STATUS_DEFINE_REFEREE_REWARD, program.completed_status),
                           PROGRAM_STATUS_PUBLISH_COMPLETED                 = is_referral_program_current_status_reach(program_conf.PROGRAM_STATUS_PUBLISH, program.completed_status),
                           
                           
                           program                                      = program_details,
                           program_completed_status                     = program.completed_status,
                           is_program_review_step                       = is_program_review_step,
                           is_edit_program                              = True,
                           program_key                                  = program_key,
                           
                           referrer_program_reward_list                 = referrer_program_reward_list,
                           referee_program_reward_list                  = referee_program_reward_list,
                           
                           loyalty_package                              = program.loyalty_package,
                           )
                
        except:
            logger.error('Fail to read merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        
    else:
        return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)

@referral_program_setup_bp.route('/view-program/<program_key>', methods=['GET'])
@login_required
def view_program(program_key): 
    logger.debug('---view_program---')
    program                         = None
    
    if is_not_empty(program_key):
        db_client = create_db_client(caller_info="is_view_program")
            
        try:
            with db_client.context():
                program         = MerchantReferralProgram.fetch(program_key)
                program_details = program.to_dict()
                referrer_program_reward_list       = get_referrer_program_reward_listing(program)
                referee_program_reward_list        = get_referee_program_reward_listing(program)
                
                
             
            return render_template('merchant/loyalty/referral_program/program_setup/view_program.html',
                           show_program_review              = url_for('referral_program_setup_bp.show_program_review'),
                           
                           PROGRAM_STATUS_PROGRAM_BASE_COMPLETED            = True,
                           PROGRAM_STATUS_DEFINE_REFERRER_REWARD_COMPLETED  = True,
                           PROGRAM_STATUS_DEFINE_REFEREE_REWARD_COMPLETED   = True,
                           PROGRAM_STATUS_PUBLISH_COMPLETED                 = True,
                           
                           referrer_program_reward_list                 = referrer_program_reward_list,
                           referee_program_reward_list                  = referee_program_reward_list,
                           
                           program                                      = program_details,
                           program_completed_status                     = program.completed_status,
                           is_program_review_step                       = False,
                           is_edit_program                              = False,
                           is_view_program                              = True,
                           program_key                                  = program_key,
                           loyalty_package                              = program.loyalty_package,
                           )
                
        except:
            logger.error('Fail to read merchant program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)
        
        
    else:
        return create_rest_message(gettext('Failed to read merchant program'), status_code=StatusCode.BAD_REQUEST)

def __create_program_point_reward_configuration(reward_form): 
    logger.debug('---__create_program_point_reward_configuration---')
    
    add_reward_configuration = {
                            'reward_index'          : random_string(10),
                            'reward_type'           : program_conf.REWARD_FORMAT_POINT,
                            'point_amount'          : float(reward_form.point_amount.data),
                            
                            'expiration_type'       : reward_form.expiration_type.data,
                            'expiration_date'       : reward_form.expiration_date.data,
                            'expiration_value'      : reward_form.expiration_value.data,    
                        }
    
    return add_reward_configuration

def __create_program_stamp_reward_configuration(reward_form): 
    logger.debug('---__create_program_stamp_reward_configuration---')
    
    add_reward_configuration = {
                            'reward_index'          : random_string(10),
                            'reward_type'           : program_conf.REWARD_FORMAT_STAMP,
                            'stamp_amount'          : reward_form.stamp_amount.data,
                            
                            'expiration_type'       : reward_form.expiration_type.data,
                            'expiration_date'       : reward_form.expiration_date.data,
                            'expiration_value'      : reward_form.expiration_value.data,    
                        }
    
    return add_reward_configuration

def __create_program_prepaid_reward_configuration(reward_form): 
    logger.debug('---__create_program_stamp_reward_configuration---')
    
    add_reward_configuration = {
                            'reward_index'          : random_string(10),
                            'reward_type'           : program_conf.REWARD_FORMAT_PREPAID,
                            'prepaid_amount'        : float(reward_form.prepaid_amount.data),
                            
                        }
    
    return add_reward_configuration

def __create_program_voucher_reward_configuration(voucher_reward_form): 
    logger.debug('---__create_program_voucher_reward_configuration---')
    
    effective_date = voucher_reward_form.effective_date.data
    if is_not_empty(effective_date):
        effective_date = effective_date.strftime('%d-%m-%Y')
    
    add_voucher_configuration = {
                            'reward_index'          : random_string(10),
                            'reward_type'           : program_conf.REWARD_FORMAT_VOUCHER,
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
    
    return add_voucher_configuration

@referral_program_setup_bp.route('/add-referrer-program-point-reward', methods=['POST'])
@login_required
def add_referrer_program_point_reward_post(): 
    logger.debug('---add_referrer_program_point_reward_post---')
    reward_form = ProgramPointRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = reward_form.program_key.data
    
    logger.debug('add_referrer_program_point_reward_post: program_key=%s', program_key)
    logger.debug('add_referrer_program_point_reward_post: request.form=%s', request.form)
    
    
    if reward_form.validate():
        add_reward_configuration = __create_program_point_reward_configuration(reward_form)
        
        db_client       = create_db_client(caller_info="add_referrer_program_point_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referrer_program_reward(merchant_program, add_reward_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add program point reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referrer-program-stamp-reward', methods=['POST'])
@login_required
def add_referrer_program_stamp_reward_post(): 
    logger.debug('---add_referrer_program_stamp_reward_post---')
    reward_form = ProgramStampRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = reward_form.program_key.data
    
    logger.debug('add_referrer_program_stamp_reward_post: program_key=%s', program_key)
    logger.debug('add_referrer_program_stamp_reward_post: request.form=%s', request.form)
    
    
    if reward_form.validate():
        add_reward_configuration = __create_program_stamp_reward_configuration(reward_form)
        
        db_client       = create_db_client(caller_info="add_referrer_program_stamp_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referrer_program_reward(merchant_program, add_reward_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add program stamp reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referrer-program-prepaid-reward', methods=['POST'])
@login_required
def add_referrer_program_prepaid_reward_post(): 
    logger.debug('---add_referrer_program_prepaid_reward_post---')
    reward_form = ProgramPrepaidRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = reward_form.program_key.data
    
    logger.debug('add_referrer_program_prepaid_reward_post: program_key=%s', program_key)
    logger.debug('add_referrer_program_prepaid_reward_post: request.form=%s', request.form)
    
    
    if reward_form.validate():
        add_reward_configuration = __create_program_prepaid_reward_configuration(reward_form)
        
        db_client       = create_db_client(caller_info="add_referrer_program_prepaid_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referrer_program_reward(merchant_program, add_reward_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add program prepaid reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referrer-program-voucher-reward', methods=['POST'])
@login_required
def add_referrer_program_voucher_reward_post(): 
    logger.debug('---add_referrer_program_voucher_reward_post---')
    voucher_reward_form = ProgramVoucherRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = voucher_reward_form.program_key.data
    
    logger.debug('add_referrer_program_voucher_reward_post: program_key=%s', program_key)
    logger.debug('add_referrer_program_voucher_reward_post: request.form=%s', request.form)
    
    
    if voucher_reward_form.validate():
        add_voucher_configuration = __create_program_voucher_reward_configuration(voucher_reward_form)
        
        db_client       = create_db_client(caller_info="add_referrer_program_voucher_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referrer_program_reward(merchant_program, add_voucher_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add giveaway voucher into program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = voucher_reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referee-program-point-reward', methods=['POST'])
@login_required
def add_referee_program_point_reward_post(): 
    logger.debug('---add_referee_program_point_reward_post---')
    reward_form = ProgramPointRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = reward_form.program_key.data
    
    logger.debug('add_referee_program_point_reward_post: program_key=%s', program_key)
    logger.debug('add_referee_program_point_reward_post: request.form=%s', request.form)
    
    
    if reward_form.validate():
        add_reward_configuration = __create_program_point_reward_configuration(reward_form)
        
        db_client       = create_db_client(caller_info="add_referee_program_point_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referee_program_reward(merchant_program, add_reward_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add program point reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referee-program-stamp-reward', methods=['POST'])
@login_required
def add_referee_program_stamp_reward_post(): 
    logger.debug('---add_referee_program_stamp_reward_post---')
    reward_form = ProgramStampRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = reward_form.program_key.data
    
    logger.debug('add_referee_program_stamp_reward_post: program_key=%s', program_key)
    logger.debug('add_referee_program_stamp_reward_post: request.form=%s', request.form)
    
    
    if reward_form.validate():
        add_reward_configuration = __create_program_stamp_reward_configuration(reward_form)
        
        db_client       = create_db_client(caller_info="add_referee_program_stamp_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referee_program_reward(merchant_program, add_reward_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add program stamp reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referee-program-prepaid-reward', methods=['POST'])
@login_required
def add_referee_program_prepaid_reward_post(): 
    logger.debug('---add_referee_program_prepaid_reward_post---')
    reward_form = ProgramPrepaidRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = reward_form.program_key.data
    
    logger.debug('add_referee_program_prepaid_reward_post: program_key=%s', program_key)
    logger.debug('add_referee_program_prepaid_reward_post: request.form=%s', request.form)
    
    
    if reward_form.validate():
        add_reward_configuration = __create_program_prepaid_reward_configuration(reward_form)
        
        db_client       = create_db_client(caller_info="add_referee_program_prepaid_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referee_program_reward(merchant_program, add_reward_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add program prepaid reward due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add reward into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/add-referee-program-voucher-reward', methods=['POST'])
@login_required
def add_referee_program_voucher_reward_post(): 
    logger.debug('---add_referee_program_voucher_reward_post---')
    voucher_reward_form = ProgramVoucherRewardForm(request.form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    program_key     = voucher_reward_form.program_key.data
    
    logger.debug('add_referee_program_voucher_reward_post: program_key=%s', program_key)
    logger.debug('add_referee_program_voucher_reward_post: request.form=%s', request.form)
    
    
    if voucher_reward_form.validate():
        add_voucher_configuration = __create_program_voucher_reward_configuration(voucher_reward_form)
        
        db_client       = create_db_client(caller_info="add_referrer_program_voucher_reward_post")
        
        try:
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_program    = MerchantReferralProgram.fetch(program_key)
                MerchantReferralProgram.add_referee_program_reward(merchant_program, add_voucher_configuration, modified_by=merchant_user)
                
        except:
            logger.error('Fail to add giveaway voucher into program due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add voucher into program'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = voucher_reward_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
    return create_rest_message(status_code=StatusCode.OK)

@referral_program_setup_bp.route('/remove-referrer-program-reward', methods=['DELETE'])
@login_required
def remove_referrer_program_reward_delete(): 
    logger.debug('---remove_referrer_program_reward_delete---')
    
    reward_index    = request.args.get('reward_index')
    program_key     = request.args.get('program_key')
    
    logger.debug('remove_referrer_program_reward_delete: program_key=%s', program_key)
    logger.debug('remove_referrer_program_reward_delete: reward_index=%s', reward_index)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="remove_referrer_program_reward_delete")
    try:
        
        with db_client.context():
            merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            program = MerchantReferralProgram.fetch(program_key)
            
            MerchantReferralProgram.remove_referrer_program_reward(program, reward_index, modified_by=merchant_user)
            
        return create_rest_message(status_code=StatusCode.OK)
            
    except:
        logger.error('Fail to remove program referrer reward due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to remove reward'), status_code=StatusCode.BAD_REQUEST)
    
@referral_program_setup_bp.route('/remove-referee-program-reward', methods=['DELETE'])
@login_required
def remove_referee_program_reward_delete(): 
    logger.debug('---remove_referee_program_reward_delete---')
    
    reward_index    = request.args.get('reward_index')
    program_key     = request.args.get('program_key')
    
    logger.debug('remove_referee_program_reward_delete: program_key=%s', program_key)
    logger.debug('remove_referee_program_reward_delete: reward_index=%s', reward_index)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="remove_referee_program_reward_delete")
    try:
        
        with db_client.context():
            merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            program = MerchantReferralProgram.fetch(program_key)
            
            MerchantReferralProgram.remove_referee_program_reward(program, reward_index, modified_by=merchant_user)
            
        return create_rest_message(status_code=StatusCode.OK)
            
    except:
        logger.error('Fail to remove program voucher due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to remove voucher'), status_code=StatusCode.BAD_REQUEST)    

@referral_program_setup_bp.route('/archive-program', methods=['POST','GET'])
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
                
                program = MerchantReferralProgram.fetch(program_key)
                if program:
                    MerchantReferralProgram.archive_program(program)
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to archive merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@referral_program_setup_bp.route('/enable-program/<program_key>', methods=['POST','GET'])
@login_required
def enable_program(program_key): 
    return enable_or_disable_program(program_key, True)

@referral_program_setup_bp.route('/disable-program/<program_key>', methods=['POST','GET'])
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
                
                program = MerchantReferralProgram.fetch(program_key)
                if program:
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    if to_enable:
                        MerchantReferralProgram.enable(program, modified_by=merchant_user)
                        logger.debug('Program have been enabled')
                    else:
                        MerchantReferralProgram.disable(program)
                        logger.debug('Program have been disabled')
                else:
                    logger.warn('program is not found')
                    
        if program is None:
            return create_rest_message(gettext('Invalid merchant program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update merchant program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update merchant program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@referral_program_setup_bp.route('/show-program-configuration', methods=['GET'])
@login_required
def show_program_configuration(): 
    logger.debug('---show_program_configuration---')
    
    program_key = request.args.get('program_key')
    
    program_configuration = {}
    
    db_client = create_db_client(caller_info="show_program_configuration")
    try:
        
        with db_client.context():
            program = MerchantReferralProgram.fetch(program_key)
            program_configuration = program.to_configuration()
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
       

    return jsonify(program_configuration)

@referral_program_setup_bp.route('/show-program-configuration', methods=['GET'])
@login_required
def flush_merchant_referral_program_settings(): 
    logger.debug('---show_program_configuration---')
    
    program_key = request.args.get('program_key')
    
    program_configuration = {}
    
    db_client = create_db_client(caller_info="show_program_configuration")
    try:
        
        with db_client.context():
            program = MerchantReferralProgram.fetch(program_key)
            program_configuration = program.to_configuration()
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
       

    return jsonify(program_configuration)

