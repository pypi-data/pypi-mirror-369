'''
Created on 23 Aug 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
from trexweb.utils.common.http_response_util import MINE_TYPE_JSON
import json
from trexadmin.forms.merchant.prepaid_forms import PrepaidSetupForm
from trexmodel.models.datastore.prepaid_models import PrepaidSettings


prepaid_setup_bp = Blueprint('prepaid_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/prepaid/program')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

'''
Blueprint settings here
'''


@prepaid_setup_bp.context_processor
def prepaid_setup_settings_bp_inject_settings():
    
    return dict(
                
                )

@prepaid_setup_bp.route('/', methods=['GET'])
@login_required
def manage_prepaid(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    currency_details            = get_merchant_configured_currency_details()
    prepaid_settings_list       = []
    db_client = create_db_client(caller_info="manage_prepaid")
    try:
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            __prepaid_settings_list   = PrepaidSettings.list_by_merchant_acct(merchant_acct)
            if __prepaid_settings_list:
                for prepaid_settings in __prepaid_settings_list:
                    prepaid_settings_list.append(prepaid_settings.to_dict())
                        
            
    except:
        logger.error('Fail to show manage prepaid program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/prepaid/program/manage_prepaid_program.html',
                           page_title                       = gettext('Prepaid Cash Setup'),
                           prepaid_settings_list            = prepaid_settings_list,
                           currency_details                 = currency_details,
                           )

@prepaid_setup_bp.route('/prepaid-program-listing-content', methods=['GET'])
@login_required
def prepaid_listing_content(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    currency_details            = get_merchant_configured_currency_details()
    prepaid_settings_list       = []
    db_client = create_db_client(caller_info="prepaid_setup")
    try:
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            __prepaid_settings_list   = PrepaidSettings.list_by_merchant_acct(merchant_acct)
            if __prepaid_settings_list:
                for prepaid_settings in __prepaid_settings_list:
                    prepaid_settings_list.append(prepaid_settings.to_dict())
                        
            
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/prepaid/prepaid_listing.html',
                           page_title                       = gettext('Prepaid Cash Setup'),
                           prepaid_settings_list            = prepaid_settings_list,
                           currency_details                 = currency_details,
                           )

@prepaid_setup_bp.route('/prepaid-program-settings', methods=['GET'])
@login_required
def create_prepaid(): 
    currency_details            = get_merchant_configured_currency_details()
    
    return render_template('merchant/loyalty/prepaid/program/prepaid_program_settings_details.html',
                           page_title                       = gettext('Prepaid Setup'),
                           prepaid_setup_url                = url_for('prepaid_setup_bp.prepaid_setup_post'),
                           currency_details                 = currency_details,
                           )
    
@prepaid_setup_bp.route('/prepaid-program-settings', methods=['POST','PUT'])
@login_required
def prepaid_setup_post(): 
    
    prepaid_setup_data      = request.form
    prepaid_setup_form      = PrepaidSetupForm(prepaid_setup_data)
    prepaid_settings_key    = prepaid_setup_form.prepaid_settings_key.data
    
    logger.debug('prepaid_setup_data=%s', prepaid_setup_data)
    
    try:
        if prepaid_setup_form.validate():
            
            lump_sum_settings       = {}
            multitier_settings      = {}
            is_new_setup            = False
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            
            is_lump_sum_prepaid         = prepaid_setup_form.is_lump_sum_prepaid.data
            is_multi_tier_prepaid       = prepaid_setup_form.is_multi_tier_prepaid.data
            
            logger.debug('is_lump_sum_prepaid=%s', is_lump_sum_prepaid)
            logger.debug('is_multi_tier_prepaid=%s', is_multi_tier_prepaid)
            
            #if is_lump_sum_prepaid:
            lump_sump_topup_amount      = prepaid_setup_form.lump_sump_topup_amount.data
            lump_sump_prepaid_amount    = prepaid_setup_form.lump_sump_prepaid_amount.data
                
            logger.debug('lump_sump_topup_amount=%s', lump_sump_topup_amount)
            logger.debug('lump_sump_prepaid_amount=%s', lump_sump_prepaid_amount)
            
            lump_sum_settings = {
                                'topup_amount'      : float(lump_sump_topup_amount),
                                'prepaid_amount'    : float(lump_sump_prepaid_amount),
                                }
            
            logger.debug('lump_sum_settings=%s', lump_sum_settings)
            
            #if is_multi_tier_prepaid:
            multitier_settings      = prepaid_setup_form.multitier_settings.data
                
            
            logger.debug('multitier_settings=%s', multitier_settings)    
            
            db_client = create_db_client(caller_info="prepaid_setup_post")
            
            with db_client.context():
                merchant_user = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_acct = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                if is_not_empty(prepaid_settings_key):
                    logger.debug('going to update prepaid settings')
                    
                    prepaid_settings    = PrepaidSettings.fetch(prepaid_settings_key)
                    
                    if prepaid_settings:
                    
                        prepaid_settings    = PrepaidSettings.update(prepaid_settings, 
                                                                    prepaid_setup_form.label.data,
                                                                    prepaid_setup_form.start_date.data,
                                                                    prepaid_setup_form.end_date.data, 
                                                                    is_multi_tier_prepaid    = prepaid_setup_form.is_multi_tier_prepaid.data, 
                                                                    is_lump_sum_prepaid      = prepaid_setup_form.is_lump_sum_prepaid.data, 
                                                                    lump_sum_settings        = lump_sum_settings, 
                                                                    multitier_settings       = multitier_settings, 
                                                                    modified_by              = merchant_user
                                                                   )
                    
                    
                else:
                    logger.debug('going to create prepaid settings')
                    
                    prepaid_settings    = PrepaidSettings.create(merchant_acct, 
                                                                    prepaid_setup_form.label.data,
                                                                    prepaid_setup_form.start_date.data,
                                                                    prepaid_setup_form.end_date.data,
                                                                    is_multi_tier_prepaid    = prepaid_setup_form.is_multi_tier_prepaid.data, 
                                                                    is_lump_sum_prepaid      = prepaid_setup_form.is_lump_sum_prepaid.data, 
                                                                    lump_sum_settings        = lump_sum_settings, 
                                                                    multitier_settings       = multitier_settings, 
                                                                    created_by               = merchant_user
                                                                   )
                
                    is_new_setup = True
            
            logger.debug('is_new_setup=%s', is_new_setup)
            
            if prepaid_settings is None:
                logger.debug('prepaid_settings is None')
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                if is_new_setup:
                    
                    return create_rest_message(status_code  = StatusCode.OK, 
                                           prepaid_settings_key = prepaid_settings.key_in_str,
                                           )
                else:
                    return create_rest_message(status_code=StatusCode.OK)
            
                    
        else:
            error_message = prepaid_setup_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update prepaid settings due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@prepaid_setup_bp.route('/prepaid-program-settings/<prepaid_key>', methods=['GET'])
@login_required
def edit_prepaid(prepaid_key):
    currency_details            = get_merchant_configured_currency_details()
    
    db_client = create_db_client(caller_info="prepaid_setup")
    try:
        with db_client.context():
            prepaid_settings    = PrepaidSettings.fetch(prepaid_key)
            if prepaid_settings:
                prepaid_settings = prepaid_settings.to_dict()
                        
            
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/prepaid/program/prepaid_program_settings_details.html',
                           page_title                       = gettext('Prepaid Cash Setting'),
                           prepaid_setup_url                = url_for('prepaid_setup_bp.prepaid_setup_post'),
                           prepaid_settings                 = prepaid_settings,
                           currency_details                 = currency_details,
                           multitier_settings               = prepaid_settings.get('multitier_settings') if prepaid_settings.get('multitier_settings') else {},
                           )


@prepaid_setup_bp.route('/enable-prepaid-program/<prepaid_key>', methods=['POST','GET'])
@login_required
def enable_prepaid(prepaid_key): 
    return enable_or_disable_prepaid(prepaid_key, True)

@prepaid_setup_bp.route('/disable-prepaid-program/<prepaid_key>', methods=['POST','GET'])
@login_required
def disable_prepaid(prepaid_key): 
    return enable_or_disable_prepaid(prepaid_key, False)
    
def enable_or_disable_prepaid(prepaid_key, to_enable): 
    
    db_client               = create_db_client(caller_info="enable_or_disable_prepaid")
    
    try:
        with db_client.context():
            if is_empty(prepaid_key):
                return create_rest_message(gettext('Invaid prepaid data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                prepaid_settings = PrepaidSettings.fetch(prepaid_key)
                if prepaid_settings:
                    if to_enable:
                        PrepaidSettings.enable(prepaid_settings)
                        logger.debug('Prepaid program have been enabled')
                    else:
                        PrepaidSettings.disable(prepaid_settings)
                        logger.debug('Prepaid program have been disabled')
                    
        if prepaid_settings is None:
            return create_rest_message(gettext('Invalid prepaid program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update prepaid program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update prepaid program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@prepaid_setup_bp.route('/archive-prepaid-program/<prepaid_key>', methods=['POST','GET'])
@login_required
def archive_prepaid(prepaid_key): 
    
    logger.debug('---archive_prepaid---')
    
    db_client   = create_db_client(caller_info="archive_prepaid")
    
    try:
        with db_client.context():
            if is_empty(prepaid_key):
                return create_rest_message(gettext('Invaid prepaid data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                prepaid_settings = PrepaidSettings.fetch(prepaid_key)
                if prepaid_settings:
                    PrepaidSettings.archive(prepaid_settings) 
                    logger.debug('Prepaid program have been archived')
                    
        if prepaid_settings is None:
            return create_rest_message(gettext('Invalid prepaid program'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to archive prepaid program due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive prepaid program'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)