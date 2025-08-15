'''
Created on 30 Dec 2022

@author: jacklok
'''

from flask import Blueprint, render_template, request, abort
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager, CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexmodel.models.datastore.model_decorators import model_transactional
from trexadmin.forms.merchant.loyalty_forms import LoyaltyDeviceSettingForm
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.crypto_util import decrypt_json, encrypt_json
from trexmodel.models.datastore.product_models import ProductCatalogue
from trexlib.libs.flask_wtf.request_wrapper import request_form, request_values

loyalty_device_setup_bp = Blueprint('loyalty_device_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/loyalty/device')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

'''
Blueprint settings here
'''


@loyalty_device_setup_bp.context_processor
def loyalty_device_setup_settings_bp_inject_settings():
    
    return dict(
                
                )


@loyalty_device_setup_bp.route('/', methods=['GET'])
@login_required
def loyalty_device_search(): 
    loyalty_device_settings_list           = []
    
    return render_template('merchant/loyalty/loyalty_device/manage_loyalty_device.html',
                           page_title                   = gettext('Program Device Setup'),
                           loyalty_device_settings_list = loyalty_device_settings_list,
                           loyalty_device_search_url    = url_for('loyalty_device_setup_bp.search_loyalty_device', limit=20, page_no=1),
                           add_loyalty_device_url       = url_for('loyalty_device_setup_bp.add_loyalty_device'),
                           loyalty_device_list_all_url  = url_for('loyalty_device_setup_bp.list_loyalty_device', limit=20, page_no=1),
                           )
    
@loyalty_device_setup_bp.route('/add', methods=['GET'])
@login_required
def add_loyalty_device(): 
    return render_template('merchant/loyalty/loyalty_device/loyalty_device_setting_details.html',
                           page_title                           = gettext('Loyalty Device Setting'),
                           update_loyalty_device_setting_url    = url_for('loyalty_device_setup_bp.add_loyalty_device_post'),
                           )
    
@loyalty_device_setup_bp.route('/edit/<loyalty_device_setting_key>', methods=['GET'])
@login_required
def edit_loyalty_device(loyalty_device_setting_key): 
    if is_not_empty(loyalty_device_setting_key):
        db_client       = create_db_client(caller_info="loyalty_device_setting_key")
        with db_client.context():
            loyalty_device_setting = LoyaltyDeviceSetting.fetch(loyalty_device_setting_key)
            loyalty_device_setting = loyalty_device_setting.to_dict()
        
        return render_template('merchant/loyalty/loyalty_device/loyalty_device_setting_details.html',
                               page_title                           = gettext('Loyalty Device Setting'),
                               update_loyalty_device_setting_url    = url_for('loyalty_device_setup_bp.add_loyalty_device_post'),
                               loyalty_device_setting               = loyalty_device_setting,
                               )
    else:
        return create_rest_message(gettext('Invalid data'), status_code=StatusCode.BAD_REQUEST)
             
    
@loyalty_device_setup_bp.route('/add', methods=['POST'])
@login_required
@request_form
def add_loyalty_device_post(request_form):  
    
    add_device_data                 = request_form
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    logger.debug('add_device_data=%s', add_device_data)
    
    device_setting_form = LoyaltyDeviceSettingForm(add_device_data)
    
    @model_transactional(desc='add_loyalty_device_post create transaction')
    def __start_transaction_to_create(device_name, merchant_acct, assign_outlet,
                                      enable_lock_screen,
                                      lock_screen_code,
                                      lock_screen_length_in_second,
                                      ):
        return LoyaltyDeviceSetting.create(device_name, merchant_acct, assign_outlet, 
                                           enable_lock_screen, 
                                           lock_screen_code, 
                                           lock_screen_length_in_second)
    
    @model_transactional(desc='add_loyalty_device_post update transaction')
    def __start_transaction_to_update(device_setting_key, device_name, assign_outlet,
                                      enable_lock_screen,
                                      lock_screen_code,
                                      lock_screen_length_in_second,
                                      ):
        return LoyaltyDeviceSetting.update(device_setting_key, device_name, assign_outlet,
                                           enable_lock_screen,
                                           lock_screen_code,
                                           lock_screen_length_in_second,
                                           )  
    
    try:
        if device_setting_form.validate():
            loyalty_device_setting_key = device_setting_form.loyalty_device_setting_key.data
            db_client       = create_db_client(caller_info="add_loyalty_device_post")
            with db_client.context():
                assign_outlet               = Outlet.fetch(device_setting_form.assign_outlet_key.data)
                
                device_name                 = device_setting_form.device_name.data
                enable_lock_screen          = device_setting_form.enable_lock_screen.data
                lock_screen_code            = device_setting_form.lock_screen_code.data
                lock_screen_length_in_second= device_setting_form.lock_screen_length_in_second.data
                
                if is_empty(loyalty_device_setting_key):
                    merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                    created_device_setting = __start_transaction_to_create(
                                                device_name, 
                                                merchant_acct, 
                                                assign_outlet,
                                                enable_lock_screen,
                                                lock_screen_code,
                                                lock_screen_length_in_second,
                                                )
                else:
                    updated_device_setting = __start_transaction_to_update(
                                                loyalty_device_setting_key, 
                                                device_name, 
                                                assign_outlet,
                                                enable_lock_screen,
                                                lock_screen_code,
                                                lock_screen_length_in_second,
                                                )
            
            if is_empty(loyalty_device_setting_key):
                if created_device_setting is None:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                else:
                    
                    return create_rest_message(gettext('Device setting have been created'), 
                                           status_code                  = StatusCode.OK, 
                                           loyalty_device_setting_key   = created_device_setting.key_in_str,
                                           activation_code              = created_device_setting.activation_code,
                                           )
                    
            else:
                if updated_device_setting is None:  
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
                else:
                    return create_rest_message(gettext('Device setting have been updated'), 
                                               status_code          = StatusCode.OK, 
                                               )
                    
        else:
            error_message = device_setting_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update loyalty device due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@loyalty_device_setup_bp.route('/search/page-size/<limit>/page/<page_no>', methods=['POST', 'GET'])
@login_required
@request_values
@request_form
def search_loyalty_device(request_values, request_form, limit, page_no):    
 
    logger.debug('---search_loyalty_device---')
    
    #encrypted_search_device_data  = request.args.get('encrypted_search_device_data')
    
    encrypted_search_device_data  = request_values.get('encrypted_search_device_data') or {}
    
    logger.debug('encrypted_search_device_data=%s', encrypted_search_device_data)
    
    if encrypted_search_device_data:
        search_device_data            = decrypt_json(encrypted_search_device_data)
        logger.debug('search_device_data from encrypted_search_loyalty_data=%s', search_device_data)
        assigned_outlet_key = search_device_data.get('assigned_outlet_key')
        
    else:
        assigned_outlet_key             = request_form.get('assigned_outlet_key')
        
        logger.debug('assigned_outlet_key=%s', assigned_outlet_key)
        
        search_device_data              = request_form
        encrypted_search_device_data    = encrypt_json(search_device_data)
         
    
        logger.debug('encrypted_search_device_data after encrypted=%s', encrypted_search_device_data)
    
    logger.debug('search_device_data=%s', search_device_data)
    logger.debug('assigned_outlet_key=%s', assigned_outlet_key)
    
    loyalty_device_setting_list = []
    
    logger.debug('page_no=%s', page_no)
    
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    
    db_client = create_db_client(caller_info="search_loyalty_device")
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            assigned_outlet = Outlet.fetch(assigned_outlet_key)
            logger.debug('assigned_outlet=%s', assigned_outlet)
            results, next_cursor    = LoyaltyDeviceSetting.list_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
            total_count             = LoyaltyDeviceSetting.count_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet)
            for r in results:
                loyalty_device_setting_list.append(r.to_dict())
                
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                                encrypted_search_device_data  = encrypted_search_device_data,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/loyalty/loyalty_device/loyalty_device_listing_content.html', 
                               loyalty_device_setting_list  = loyalty_device_setting_list,
                               end_point                    = 'loyalty_device_setup_bp.search_loyalty_device',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#loaylty_device_search_list_div',
                               
                               )
    except:
        logger.error('Fail to search loyalty device due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search loyalty device'), status_code=StatusCode.BAD_REQUEST)
        
    
@loyalty_device_setup_bp.route('/loyalty-device-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_loyalty_device(limit, page_no):
    logger.debug('---list_loyalty_device---')
    logger.debug('page_no=%s', page_no)
    
    cursor                          = request.args.get('cursor')
    previous_cursor                 = request.args.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    
    loyalty_device_setting_list            = []
    
    
    logger.debug('limit_int=%d', limit_int)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    try:
        db_client = create_db_client(caller_info="list_loyalty_device")
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            result,next_cursor  = LoyaltyDeviceSetting.list_by_merchant_account(merchant_acct, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
            total_count         = LoyaltyDeviceSetting.count_by_merchant_acct(merchant_acct)
            for r in result:
                loyalty_device_setting_list.append(r.to_dict())
                
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/loyalty/loyalty_device/loyalty_device_listing_content.html', 
                               loyalty_device_setting_list  = loyalty_device_setting_list,
                               end_point                    = 'loyalty_device_setup_bp.list_loyalty_device',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#loyalty_device_search_list_div',
                               )
        
    except:
        logger.error('Fail to list pos due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to list device'), status_code=StatusCode.BAD_REQUEST)
        
        
    
@loyalty_device_setup_bp.route('/<activation_code>', methods=['DELETE'])
@login_required
def delete_loyalty_device_post(activation_code):
    @model_transactional(desc='delete_loyalty_device_post')
    def __start_transaction(activation_code):
        return LoyaltyDeviceSetting.remove_by_activation_code(activation_code)  
    
    try:
        if is_not_empty(activation_code):
            
            db_client = create_db_client(caller_info="delete_loyalty_device_post")
            with db_client.context():
                __start_transaction(activation_code)
            
            
            return create_rest_message(gettext('Device setting have been deleted'), 
                                           status_code          = StatusCode.ACCEPTED
                                           )
                            
        else:
            return create_rest_message(gettext('Invalid data'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to delete loyalty device due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)            
