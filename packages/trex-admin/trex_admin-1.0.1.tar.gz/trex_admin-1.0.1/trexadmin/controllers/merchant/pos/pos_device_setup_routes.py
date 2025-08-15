'''
Created on 25 Aug 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.models.datastore.pos_models import POSSetting
from trexmodel.models.datastore.model_decorators import model_transactional
from trexadmin.forms.merchant.pos_forms import POSSettingForm
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.crypto_util import decrypt_json, encrypt_json
from trexlib.libs.flask_wtf.request_wrapper import request_form, request_values

pos_device_setup_bp = Blueprint('pos_device_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/device')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

'''
Blueprint settings here
'''


@pos_device_setup_bp.context_processor
def pos_setup_settings_bp_inject_settings():
    
    return dict(
                
                )


@pos_device_setup_bp.route('/', methods=['GET'])
@login_required
def pos_device_search(): 
    pos_settings_list           = []
    
    return render_template('merchant/pos/pos_device/manage_pos_device.html',
                           page_title                   = gettext('POS Device Setup'),
                           pos_settings_list            = pos_settings_list,
                           pos_search_url               = url_for('pos_device_setup_bp.search_pos_device', limit=20, page_no=1),
                           add_pos_url                  = url_for('pos_device_setup_bp.add_pos_device'),
                           pos_list_all_url             = url_for('pos_device_setup_bp.list_pos_device', limit=20, page_no=1),
                           )
    
@pos_device_setup_bp.route('/add', methods=['GET'])
@login_required
def add_pos_device(): 
    return render_template('merchant/pos/pos_device/pos_device_setting_details.html',
                           page_title                   = gettext('POS Device'),
                           update_pos_setting_url       = url_for('pos_device_setup_bp.add_pos_device_post'),
                           )
    
@pos_device_setup_bp.route('/edit/<pos_setting_key>', methods=['GET'])
@login_required
def edit_pos_device(pos_setting_key): 
    if is_not_empty(pos_setting_key):
        db_client       = create_db_client(caller_info="edit_pos")
        with db_client.context():
            pos_setting = POSSetting.fetch(pos_setting_key)
            pos_setting = pos_setting.to_dict()
        
        return render_template('merchant/pos/pos_device/pos_device_setting_details.html',
                               page_title                   = gettext('POS Device'),
                               update_pos_setting_url       = url_for('pos_device_setup_bp.add_pos_device_post'),
                               pos_setting                  = pos_setting,
                               )
    else:
        return create_rest_message(gettext('Invalid data'), status_code=StatusCode.BAD_REQUEST)
             
    
@pos_device_setup_bp.route('/add', methods=['POST'])
@login_required
@request_form
def add_pos_device_post(request_form):  
    
    add_pos_data                = request_form
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    logger.debug('add_pos_device_post=%s', add_pos_data)
    
    pos_setting_form = POSSettingForm(add_pos_data)
    
    @model_transactional(desc='add_pos_device_post create transaction')
    def __start_transaction_to_create(device_name, merchant_acct, assign_outlet):
        return POSSetting.create(device_name, merchant_acct, assign_outlet)
    
    @model_transactional(desc='add_pos_device_post update transaction')
    def __start_transaction_to_update(pos_setting_key, device_name, assign_outlet):
        return POSSetting.update(pos_setting_key, device_name, assign_outlet)  
    
    try:
        if pos_setting_form.validate():
            pos_setting_key = pos_setting_form.pos_setting_key.data
            db_client       = create_db_client(caller_info="add_pos_post")
            with db_client.context():
                assign_outlet           = Outlet.fetch(pos_setting_form.assign_outlet_key.data)
                
                device_name                = pos_setting_form.device_name.data
                
                if is_empty(pos_setting_key):
                    merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                    created_pos_setting = __start_transaction_to_create(device_name, merchant_acct, assign_outlet)
                else:
                    updated_pos_setting = __start_transaction_to_update(pos_setting_key, device_name, assign_outlet)
            
            if is_empty(pos_setting_key):
                if created_pos_setting is None:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                else:
                    if created_pos_setting:
                        return create_rest_message(gettext('POS device setting have been created'), 
                                               status_code          = StatusCode.OK, 
                                               pos_setting_key      = created_pos_setting.key_in_str,
                                               activation_code      = created_pos_setting.activation_code,
                                               )
                    else:
                        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                if updated_pos_setting is None:  
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
                else:
                    return create_rest_message(gettext('POS device setting have been updated'), 
                                               status_code          = StatusCode.OK, 
                                               )
                    
        else:
            error_message = pos_setting_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update POS device due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@pos_device_setup_bp.route('/search/page-size/<limit>/page/<page_no>', methods=['POST', 'GET'])
@login_required
@request_values
@request_form
def search_pos_device(request_values, request_form, limit, page_no):    
 
    logger.debug('---search_pos---')
    
    
    
    encrypted_search_pos_data  = request_values.get('encrypted_search_pos_data')
    
    logger.debug('encrypted_search_pos_data=%s', encrypted_search_pos_data)
    
    if encrypted_search_pos_data:
        search_pos_data            = decrypt_json(encrypted_search_pos_data)
        logger.debug('search_pos_data from encrypted_search_pos_data=%s', search_pos_data)
        assigned_outlet_key = search_pos_data.get('assigned_outlet_key')
        
    else:
        assigned_outlet_key         = request_form.get('assigned_outlet_key')
        search_pos_data            = request_form
        encrypted_search_pos_data  = encrypt_json(search_pos_data) 
    
        logger.debug('encrypted_search_pos_data after encrypted=%s', encrypted_search_pos_data)
    
    logger.debug('search_pos_data=%s', search_pos_data)
    logger.debug('assigned_outlet_key=%s', assigned_outlet_key)
    
    pos_setting_list            = []
    
    logger.debug('page_no=%s', page_no)
    
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    
    db_client = create_db_client(caller_info="search_pos")
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            assigned_outlet = Outlet.fetch(assigned_outlet_key)
            logger.debug('assigned_outlet=%s', assigned_outlet)
            results, next_cursor    = POSSetting.list_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
            total_count             = POSSetting.count_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet)
            for r in results:
                pos_setting_list.append(r.to_dict())
                
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                                encrypted_search_pos_data       = encrypted_search_pos_data,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/pos/pos_device/pos_device_listing_content.html', 
                               pos_setting_list                = pos_setting_list,
                               end_point                    = 'pos_device_setup_bp.search_pos_device',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#pos_search_list_div',
                               
                               )
    except:
        logger.error('Fail to search pos due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search POS device setting'), status_code=StatusCode.BAD_REQUEST)
        
    
@pos_device_setup_bp.route('/pos-device-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_pos_device(request_values, limit, page_no):
    logger.debug('---list_pos_device---')
    logger.debug('page_no=%s', page_no)
    
    cursor                          = request_values.get('cursor')
    previous_cursor                 = request_values.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    pos_setting_list            = []
    db_client = create_db_client(caller_info="list_pos")
    
    logger.debug('limit_int=%d', limit_int)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    try:
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            result,next_cursor  = POSSetting.list_by_merchant_account(merchant_acct, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
            total_count         = POSSetting.count_by_merchant_acct(merchant_acct)
            for r in result:
                pos_setting_list.append(r.to_dict())
                
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/pos/pos_device/pos_device_listing_content.html', 
                               pos_setting_list                = pos_setting_list,
                               end_point                    = 'pos_device_setup_bp.list_pos_device',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#pos_search_list_div',
                               )
        
    except:
        logger.error('Fail to list pos due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to list POS device setting'), status_code=StatusCode.BAD_REQUEST)
        
        
    
@pos_device_setup_bp.route('/<activation_code>', methods=['DELETE'])
@login_required
def delete_pos_device_post(activation_code):
    @model_transactional(desc='delete_pos_device_post transaction')
    def __start_transaction(activation_code):
        return POSSetting.remove_by_activation_code(activation_code)  
    
    try:
        if is_not_empty(activation_code):
            
            db_client = create_db_client(caller_info="delete_pos_device_post")
            with db_client.context():
                __start_transaction(activation_code)
            
            
            return create_rest_message(gettext('POS device setting have been deleted'), 
                                           status_code          = StatusCode.ACCEPTED
                                           )
                            
        else:
            return create_rest_message(gettext('Invalid data'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to add POS device due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)            