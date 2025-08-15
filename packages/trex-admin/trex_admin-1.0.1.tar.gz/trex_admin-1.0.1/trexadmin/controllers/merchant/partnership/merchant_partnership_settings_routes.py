'''
Created on 6 May 2025

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexmodel.models.datastore.partnership_models import PartnershipSettings
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexlib.utils.string_util import boolify

merchant_partnership_settings_bp = Blueprint('merchant_partnership_settings_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/partnership/settings')

logger = logging.getLogger('target_debug')


'''
Blueprint settings here
'''


@merchant_partnership_settings_bp.context_processor
def merchant_partnership_settings_bp_bp_inject_settings():
    
    return dict(
                )
    
@merchant_partnership_settings_bp.route('/', methods=['GET'])
@login_required
def merchant_partnership_settings(): 
    currency_details = get_merchant_configured_currency_details()
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="merchant_partnership_settings")

    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        partnership_settings = PartnershipSettings.get_by_merchant_acct(merchant_acct)
        
        logger.debug('partnership_settings=%s', partnership_settings)
        
        if partnership_settings:
            partnership_settings = partnership_settings.to_dict()
        else:
            partnership_settings = {
                                    'is_enabled': False,
                                    'point_worth_value_in_currency': 1,
                                    }
            
    logger.debug('partnership_settings=%s', partnership_settings)
    
    return render_template('merchant/partnership/settings/merchant_partnership_settings.html',
                           page_title = gettext('Partnership Settings'),
                           currency_details = currency_details,
                           post_url = url_for('merchant_partnership_settings_bp.merchant_partnership_settings_post'),
                           **partnership_settings,
                           )
    
@merchant_partnership_settings_bp.route('/', methods=['POST'])
@login_required
@request_values
def merchant_partnership_settings_post(request_values): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    is_enabled                      = request_values.get('is_enabled')
    point_worth_value_in_currency   = request_values.get('point_worth_value_in_currency')
    
    
    
    db_client = create_db_client(caller_info="merchant_partnership_settings")

    with db_client.context():
        is_enabled = boolify(is_enabled)
        point_worth_value_in_currency = float(point_worth_value_in_currency)
        
        logger.debug('is_enabled=%s', is_enabled)
        logger.debug('point_worth_value_in_currency=%s', point_worth_value_in_currency)
        
        merchant_acct   = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
        
        PartnershipSettings.create(merchant_acct, is_enabled=is_enabled, point_worth_value_in_currency=point_worth_value_in_currency)
        
    
    return create_rest_message(status_code=StatusCode.OK,)   
    
