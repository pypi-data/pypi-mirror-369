'''
Created on 25 Oct 2023

@author: jacklok
'''
from functools import wraps
import logging
from trexlib.utils.log_util import get_tracelog
from trexadmin.libs.http import create_rest_message, StatusCode
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantAcct

logger = logging.getLogger('decorator')

def __get_merchant_account():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_acct_key = logged_in_merchant_user.get('merchant_acct_key')
    db_client = create_db_client( caller_info="__get_merchant_account")
    with db_client.context():
        merchant_acct   = MerchantAcct.fetch(merchant_acct_key)
    return merchant_acct
    

def account_package_is_allow(f, feature_code):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        merchant_acct = __get_merchant_account()
        
        logger.debug('==================================================')
        logger.debug('account_package=%s', merchant_acct.account_package)
        logger.debug('feature_code=%s', feature_code)
        
        logger.debug('==================================================')
        
        if is_not_empty(activation_code) and is_not_empty(device_id):
            device_settings = None
            try:
                db_client = create_db_client(caller_info="search_customer")
                if 'loyalty' == device_type:
                    with db_client.context():
                        device_settings = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
                elif 'pos' == device_type:
                    with db_client.context():
                        device_settings = POSSetting.get_by_activation_code(activation_code)
                
                if device_settings is not None:
                    if device_settings.device_id != device_id:
                        return create_rest_message('Device is not activated or it is deactivated already', status_code=StatusCode.BAD_REQUEST)
                    
                    return f(*args, **kwargs)
                
                return create_rest_message('Device is not activated or it is deactivated already', status_code=StatusCode.BAD_REQUEST)
                
            except:
                logger.error('failed due to %s ', get_tracelog())
                #return ("Failed to check device authorization", 401)
                return create_rest_message('Failed to check device authorization', status_code=StatusCode.BAD_REQUEST)
            
            

    return decorated_function
