'''
Created on 6 Jul 2021

@author: jacklok
'''

from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
import jinja2

merchant_manage_integration_bp = Blueprint('merchant_manage_integration_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/settings/integration')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@merchant_manage_integration_bp.context_processor
def merchant_manage_integration_bp_inject_settings():
    
    return dict(
                
                )


@merchant_manage_integration_bp.route('/', methods=['GET'])
@login_required
def manage_integration_index(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_integration_index")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
    return render_template('merchant/settings/manage_integration/merchant_manage_integration.html',
                           page_title           = gettext('Manage Integration'),
                           page_url             = url_for('merchant_manage_integration_bp.manage_integration_index'),
                           reset_api_key_url    = url_for('merchant_manage_integration_bp.reset_api_key_post'),
                           acct_id              = merchant_acct.key_in_str,
                           api_key              = merchant_acct.api_key,
                           show_tips            = True,
                           )
    
@merchant_manage_integration_bp.route('/reset-api-key', methods=['POST'])
@login_required
def reset_api_key_post():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="reset_api_key")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        new_api_key     = merchant_acct.update_api_key()
    
    return create_rest_message(gettext('Api key have been reseted'),  status_code=StatusCode.OK, api_key=new_api_key)   
