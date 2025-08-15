'''
Created on 16 Dec 2020

@author: jacklok
'''

from flask import request, current_app, abort, session, Response
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantUser
import jinja2, logging
from flask_login import current_user
from trexadmin.libs.jinja.common_filters import is_common_member_filter
from trexlib.utils.string_util import is_empty, is_not_empty
from trexconf.conf import DEFAULT_GMT_HOURS

logger = logging.getLogger('helper')

def get_preferred_language():
    preferred_languag = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    return preferred_languag

def get_merchant_configured_currency_details():
    return session.get('currency_details') or current_app.config.get('DEFAULT_CURRENCY_DETAILS')

def remove_signin_session():
    if session.get('logged_in_user_id'):
        del session['logged_in_user_id']
    if session.get('is_super_user'):
        del session['is_super_user']
    if session.get('is_admin_user'):
        del session['is_admin_user']
    if session.get('was_once_logged_in'):
        del session['was_once_logged_in']
    if session.get('logged_in_user_activated'):
        del session['logged_in_user_activated']
    if session.get('user_type'):
        del session['user_type']
    if session.get('permission'):
        del session['permission']
    if session.get('is_merchant_user'):
        del session['is_merchant_user']
    if session.get('merchant_acct_details'):
        del session['merchant_acct_details']
    if session.get('currency_details'):
        del session['currency_details']    
            
        
        
def get_loggedin_merchant_user_account():
    
    logged_in_merchant_user = session.get('logged_in_user')
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    return logged_in_merchant_user

def is_merchant_user():
    
    _is_merchant_user    = session.get('is_merchant_user')
    logger.debug('_is_merchant_user=%s', _is_merchant_user)
    
    return _is_merchant_user

def user_type():
    
    _user_type    = session.get('user_type')
    logger.debug('_user_type=%s', _user_type)
    
    return _user_type

def was_once_logged_in():
    
    _was_once_logged_in    = session.get('was_once_logged_in')
    logger.debug('_was_once_logged_in=%s', _was_once_logged_in)
    
    return _was_once_logged_in

def check_is_menu_accessable(menu_config, blueprint):
    if current_user:
        logger.debug('%s: is_menu_accessable: current_user.is_super_user=%s', blueprint, current_user.is_super_user)
        logger.debug('%s: is_menu_accessable: current_user.is_admin_user=%s', blueprint, current_user.is_admin_user)
        logger.debug('%s: is_menu_accessable: current_user.is_merchant_user=%s', blueprint, current_user.is_merchant_user)
        logger.debug('%s: is_menu_accessable: current_user.permission=%s', blueprint, current_user.permission)
        
        logger.debug('%s: is_menu_accessable: menu_config=%s', blueprint, menu_config)
        
        if current_user.is_super_user:
            return True
        
        elif current_user.is_merchant_user or current_user.is_admin_user:
            if current_user.is_merchant_user and current_user.is_admin_user:
                proceed_to_permission_checking = __is_product_accessable(menu_config)
                
                logger.debug('proceed_to_permission_checking after product package checking=%s', proceed_to_permission_checking)
                
                if proceed_to_permission_checking:
                    proceed_to_permission_checking = __is_loyalty_package_accessable(menu_config)
                
                logger.debug('proceed_to_permission_checking after loyalty package checking=%s', proceed_to_permission_checking)
                
                return proceed_to_permission_checking
            else:
                
                proceed_to_permission_checking = __is_product_accessable(menu_config)
                
                logger.debug('proceed_to_permission_checking after product package checking=%s', proceed_to_permission_checking)
                
                if proceed_to_permission_checking:
                    proceed_to_permission_checking = __is_loyalty_package_accessable(menu_config)
                
                logger.debug('proceed_to_permission_checking after loyalty package checking=%s', proceed_to_permission_checking)
                
                if proceed_to_permission_checking:
                    if current_user.permission:
                        logger.debug('current_user.permission.granted_access=%s', current_user.permission.get('granted_access'))
                        logger.debug('menu_config.permission=%s', menu_config.get('permission'))
                        
                        if menu_config.get('permission'):
                            is_accessable = is_common_member_filter(
                                                                    current_user.permission.get('granted_access'), 
                                                                    menu_config.get('permission')
                                                                    )
                            
                            
                            logger.debug('is_accessable=%s', is_accessable)
                            
                            return is_accessable
                        else:
                            return True
                    else:
                        return False
                else:
                    return False
    else:
        return False    

def __is_product_accessable(menu_config):
    is_accessable               = False
    subscribed_product_package  = None
    merchant_acct_details       = session.get('merchant_acct_details')
    menu_access_code            = menu_config.get('product_code')
    
    logger.debug('menu_access_code=%s', menu_access_code)
    logger.debug('merchant_acct_details=%s', merchant_acct_details)
                
    if is_not_empty(menu_access_code):
        if merchant_acct_details:
            account_plan = merchant_acct_details.get('account_plan') 
            if account_plan:
                subscribed_product_package = account_plan.get('product_package')
            
            logger.debug('subscribed_product_package=%s', subscribed_product_package)
            
            if subscribed_product_package:
                if isinstance(menu_access_code, tuple):
                    
                    for m in menu_access_code:
                        if m in subscribed_product_package:
                            is_accessable = True
                            break
                else:
                    if menu_access_code in subscribed_product_package:
                        is_accessable = True
                    
    else:
        is_accessable = True
    
    return is_accessable 

def get_merchant_gmt_hour():
    merchant_acct_details       = session.get('merchant_acct_details')
    logger.info('merchant_acct_details=%s', merchant_acct_details)
    if merchant_acct_details:
        return merchant_acct_details.get('gmt_hour', DEFAULT_GMT_HOURS)
    else:
        return DEFAULT_GMT_HOURS
    
def get_merchant_account_plan():
    merchant_acct_details       = session.get('merchant_acct_details')
    logger.info('merchant_acct_details=%s', merchant_acct_details)
    if merchant_acct_details:
        return merchant_acct_details.get('account_plan', {})
    else:
        return {}    

def __is_loyalty_package_accessable(menu_config):
    is_accessable               = False
    subscribed_loyalty_package  = None
    merchant_acct_details       = session.get('merchant_acct_details')
    menu_access_code            = menu_config.get('loyalty_package')
    
    logger.debug('menu_access_code=%s', menu_access_code)
                
    if is_not_empty(menu_access_code):
        if merchant_acct_details:
            account_plan = merchant_acct_details.get('account_plan') 
            if account_plan:
                subscribed_loyalty_package = merchant_acct_details.get('account_plan').get('loyalty_package')
        
        logger.debug('subscribed_loyalty_package=%s', subscribed_loyalty_package)
        
        if subscribed_loyalty_package:
            
            if subscribed_loyalty_package in menu_access_code:
                is_accessable = True
    else:
        is_accessable = True
    
    return is_accessable 

def __is_point_of_sales_package_accessable(menu_config):
    is_accessable           = False
    merchant_acct_details   = session.get('merchant_acct_details')
    menu_access_code        = menu_config.get('point_of_sales_package')
    
    logger.debug('menu_access_code=%s', menu_access_code)
                
    if is_not_empty(menu_access_code):
        
        subscribed_point_of_sales_package = merchant_acct_details.get('account_plan').get('point_of_sales_package')
        
        logger.debug('subscribed_point_of_sales_package=%s', subscribed_point_of_sales_package)
        
        if subscribed_point_of_sales_package in menu_access_code:
            is_accessable = True
    else:
        is_accessable = True
    
    return is_accessable 
    
    
def output_html(content, code=200, headers=None):
    resp = Response(content, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp

def convert_list_to_string(list_to_convert, default=''):
    str_value = ''
    if is_not_empty(list_to_convert):
        for l in list_to_convert:
            if is_empty(str_value):
                str_value = l
            else:
                str_value = '%s,%s' % (str_value, l) 
    else:
        return default        
    return str_value


    
        