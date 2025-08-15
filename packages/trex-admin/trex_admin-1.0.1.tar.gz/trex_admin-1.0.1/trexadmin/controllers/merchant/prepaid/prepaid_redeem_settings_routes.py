'''
Created on 23 Jan 2024

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager, CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty, random_string
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser, Outlet
from trexadmin.forms.merchant.prepaid_forms import PrepaidSetupForm,\
    PrepaidRedeemSettingsForm
from trexmodel.models.datastore.prepaid_models import PrepaidRedeemSettings
from trexlib.utils.crypto_util import decrypt_json, encrypt_json
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexmodel.models.datastore.model_decorators import model_transactional


prepaid_redeem_settings_bp = Blueprint('prepaid_redeem_settings_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/prepaid/redeem')

logger = logging.getLogger('controller')


'''
Blueprint settings here
'''


@prepaid_redeem_settings_bp.context_processor
def prepaid_redeem_settings_bp_inject_settings():
    
    return dict(
                
                )

@prepaid_redeem_settings_bp.route('/', methods=['GET'])
@login_required
def search_prepaid_redeem_settings(): 
    prepaid_redeem_settings_list    = []
    
    return render_template('merchant/loyalty/prepaid/redeem/manage_prepaid_redeem_settings.html',
                           page_title                   = gettext('Prepaid Redeem Code Setup'),
                           prepaid_redeem_settings_list = prepaid_redeem_settings_list,
                           prepaid_redeem_settings_search_url    = url_for('prepaid_redeem_settings_bp.search_prepaid_redeem_settings_post', limit=20, page_no=1),
                           add_prepaid_redeem_settings_url       = url_for('prepaid_redeem_settings_bp.add_prepaid_redeem_settings'),
                           prepaid_redeem_settings_list_all_url  = url_for('prepaid_redeem_settings_bp.list_prepaid_redeem_settings', limit=20, page_no=1),
                           
                           )
    
@prepaid_redeem_settings_bp.route('/add', methods=['GET'])
@login_required
def add_prepaid_redeem_settings(): 
    return render_template('merchant/loyalty/prepaid/redeem/prepaid_redeem_settings_details.html',
                           page_title                           = gettext('Prepaid Redeem Code'),
                           update_prepaid_redeem_settings_url   = url_for('prepaid_redeem_settings_bp.add_prepaid_redeem_settings_post'),
                           )

@prepaid_redeem_settings_bp.route('/add', methods=['POST'])
@login_required
def add_prepaid_redeem_settings_post():  
    
    prepaid_redeem_settings_data    = request.form
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    logger.debug('prepaid_redeem_settings_bp=%s', prepaid_redeem_settings_bp)
    
    prepaid_redeem_settings_form = PrepaidRedeemSettingsForm(prepaid_redeem_settings_data)
    
    @model_transactional(desc='add_prepaid_redeem_settings_post create transaction')
    def __start_transaction_to_create(label, merchant_acct, assign_outlet, device_activation_code, created_by):
        return PrepaidRedeemSettings.create(merchant_acct, label, assign_outlet, device_activation_code=device_activation_code, created_by=created_by)
    
    @model_transactional(desc='add_prepaid_redeem_settings_post update transaction')
    def __start_transaction_to_update(prepaid_redeem_settings_key, label, assign_outlet, device_activation_code, modified_by):
        return PrepaidRedeemSettings.update(prepaid_redeem_settings_key, label, assign_outlet, device_activation_code=device_activation_code, modified_by=modified_by)  
    
    try:
        if prepaid_redeem_settings_form.validate():
            prepaid_redeem_settings_key = prepaid_redeem_settings_form.prepaid_redeem_settings_key.data
            db_client       = create_db_client(caller_info="add_prepaid_redeem_settings_post")
            device_activation_code = prepaid_redeem_settings_form.device_activation_code.data
            with db_client.context():
                assign_outlet       = Outlet.fetch(prepaid_redeem_settings_form.assign_outlet_key.data)
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                label               = prepaid_redeem_settings_form.label.data
                
                logger.debug('assign_outlet name=%s', assign_outlet.name)
                
                if is_empty(prepaid_redeem_settings_key):
                    merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                    created_prepaid_redeem_settings = __start_transaction_to_create(label, merchant_acct, assign_outlet, device_activation_code, merchant_user)
                else:
                    updated_prepaid_redeem_settings = __start_transaction_to_update(prepaid_redeem_settings_key, label, assign_outlet, device_activation_code, merchant_user)
            
            if is_empty(prepaid_redeem_settings_key):
                if created_prepaid_redeem_settings is None:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                else:
                    logger.debug('After created/update prepaid redeem settings, prepaid_redeem_settings_key=%s', prepaid_redeem_settings_key)
                    return create_rest_message(gettext('Prepaid redeem code have been created'), 
                                           status_code                  = StatusCode.OK, 
                                           prepaid_redeem_settings_key  = created_prepaid_redeem_settings.key_in_str,
                                           redeem_code                  = created_prepaid_redeem_settings.redeem_code,
                                           )
                    
            else:
                if updated_prepaid_redeem_settings is None:  
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
                else:
                    return create_rest_message(gettext('Prepaid redeem code have been updated'), 
                                               status_code          = StatusCode.OK, 
                                               )
                    
        else:
            error_message = prepaid_redeem_settings_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update prepaid redeem code due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@prepaid_redeem_settings_bp.route('/search/page-size/<limit>/page/<page_no>', methods=['POST', 'GET'])
@login_required
def search_prepaid_redeem_settings_post(limit, page_no):    
 
    logger.debug('---search_prepaid_redeem_settings_post---')
    assigned_outlet_key  = request.form.get('assigned_outlet_key')
    
    logger.debug('assigned_outlet_key=%s', assigned_outlet_key)
    encrypted_search_settings_data  = request.args.get('encrypted_search_settings_data')
    
    logger.debug('encrypted_search_settings_data=%s', encrypted_search_settings_data)
    
    if encrypted_search_settings_data:
        search_settings_data            = decrypt_json(encrypted_search_settings_data)
        logger.debug('search_device_data from encrypted_search_loyalty_data=%s', search_settings_data)
        assigned_outlet_key = search_settings_data.get('assigned_outlet_key')
        
    else:
        search_settings_data             = request.form
        encrypted_search_settings_data   = encrypt_json(search_settings_data) 
    
        logger.debug('encrypted_search_settings_data after encrypted=%s', encrypted_search_settings_data)
    
    logger.debug('search_settings_data=%s', search_settings_data)
    logger.debug('assigned_outlet_key=%s', assigned_outlet_key)
    
    prepaid_redeem_settings_list = []
    
    logger.debug('page_no=%s', page_no)
    
    cursor                      = request.args.get('cursor')
    previous_cursor             = request.args.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    
    db_client = create_db_client(caller_info="search_prepaid_redeem_settings_post")
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            assigned_outlet = Outlet.fetch(assigned_outlet_key)
            logger.debug('assigned_outlet=%s', assigned_outlet)
            results, next_cursor    = PrepaidRedeemSettings.list_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
            total_count             = PrepaidRedeemSettings.count_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet)
            for r in results:
                prepaid_redeem_settings_list.append(r.to_dict())
                
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                                encrypted_search_settings_data  = encrypted_search_settings_data,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/loyalty/prepaid/redeem/prepaid_redeem_settings_listing_content.html', 
                               prepaid_redeem_settings_list = prepaid_redeem_settings_list,
                               end_point                    = 'prepaid_redeem_settings_bp.search_prepaid_redeem_settings',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#prepaid_redeem_settings_search_list_div',
                               
                               )
    except:
        logger.error('Fail to search prepaid redeem settings due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search prepaid redeem settings'), status_code=StatusCode.BAD_REQUEST)
        
@prepaid_redeem_settings_bp.route('/loyalty-device-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_prepaid_redeem_settings(limit, page_no):
    logger.debug('---list_prepaid_redeem_settings---')
    logger.debug('page_no=%s', page_no)
    
    cursor                          = request.args.get('cursor')
    previous_cursor                 = request.args.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    
    prepaid_redeem_settings_list            = []
    
    
    logger.debug('limit_int=%d', limit_int)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    try:
        db_client = create_db_client(caller_info="list_prepaid_redeem_settings")
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            result,next_cursor  = PrepaidRedeemSettings.list_by_merchant_account(merchant_acct, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
            total_count         = PrepaidRedeemSettings.count_by_merchant_acct(merchant_acct)
            for r in result:
                prepaid_redeem_settings_list.append(r.to_dict())
                
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/loyalty/prepaid/redeem/prepaid_redeem_settings_listing_content.html', 
                               prepaid_redeem_settings_list  = prepaid_redeem_settings_list,
                               end_point                    = 'prepaid_redeem_settings_bp.list_prepaid_redeem_settings',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#prepaid_redeem_settings_search_list_div',
                               )
        
    except:
        logger.error('Fail to list prepaid redeem settings due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to list prepaid redeem settings'), status_code=StatusCode.BAD_REQUEST)
    
@prepaid_redeem_settings_bp.route('/<prepaid_redeem_settings_key>', methods=['GET'])
@login_required
def edit_prepaid_redeem_settings(prepaid_redeem_settings_key): 
    db_client = create_db_client(caller_info="edit_prepaid_redeem_settings")
    with db_client.context():
        prepaid_redeem_settings = PrepaidRedeemSettings.fetch(prepaid_redeem_settings_key)
        if prepaid_redeem_settings:
            prepaid_redeem_settings = prepaid_redeem_settings.to_dict()
        
            
    return render_template('merchant/loyalty/prepaid/redeem/prepaid_redeem_settings_details.html',
                           page_title                           = gettext('Edit Prepaid Redeem Code'),
                           prepaid_redeem_settings              = prepaid_redeem_settings,
                           update_prepaid_redeem_settings_url   = url_for('prepaid_redeem_settings_bp.add_prepaid_redeem_settings_post'),
                           )               


@prepaid_redeem_settings_bp.route('/<prepaid_redeem_settings_key>', methods=['DELETE'])
@login_required
def delete_prepaid_redeem_settings_delete(prepaid_redeem_settings_key):
    @model_transactional(desc='delete_prepaid_redeem_settings_delete')
    def __start_transaction(prepaid_redeem_settings_key):
        return PrepaidRedeemSettings.remove(prepaid_redeem_settings_key)
    
    try:
        if is_not_empty(prepaid_redeem_settings_key):
            
            db_client = create_db_client(caller_info="delete_prepaid_redeem_settings_delete")
            with db_client.context():
                __start_transaction(prepaid_redeem_settings_key)
            
            
            return create_rest_message(gettext('Prepaid redeem code have been deleted'), 
                                           status_code          = StatusCode.ACCEPTED
                                           )
                            
        else:
            return create_rest_message(gettext('Invalid data'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to delete prepaid redeem settings due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@prepaid_redeem_settings_bp.route('/<prepaid_redeem_settings_key>/redeem-qr-code', methods=['GET'])
@login_required
def view_prepaid_redeem_code(prepaid_redeem_settings_key):
    db_client = create_db_client(caller_info="view_prepaid_redeem_code")
    with db_client.context():
        prepaid_redeem_settings = PrepaidRedeemSettings.fetch(prepaid_redeem_settings_key)
        if prepaid_redeem_settings:
            prepaid_redeem_settings = prepaid_redeem_settings.to_dict()
            
    return render_template('merchant/loyalty/prepaid/redeem/prepaid_redeem_qr_code.html', 
                               prepaid_redeem_settings  = prepaid_redeem_settings,
                               image_filename           = 'prepaid-redeem-qr-code-%s' % random_string(6),
                               )
      