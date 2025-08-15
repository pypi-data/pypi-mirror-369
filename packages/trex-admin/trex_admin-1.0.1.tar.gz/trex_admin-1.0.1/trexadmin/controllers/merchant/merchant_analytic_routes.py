'''
Created on 4 Feb 2021

@author: jacklok
'''

from flask import Blueprint, jsonify
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct
from flask.helpers import url_for
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
import jinja2
from trexmodel.models.datastore.customer_models import Customer

merchant_analytic_bp = Blueprint('merchant_analytic_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/analytic')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@merchant_analytic_bp.context_processor
def merchant_analytic_bp_inject_settings():
    
    return dict(
                
                
                )

@merchant_analytic_bp.route('/stat-details', methods=['GET'])
@login_required
def get_merchant_stat_details(): 
    logger.debug('---get_merchant_stat_details---')
    
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="get_merchant_stat_details")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        stat_details = merchant_acct.get_stat_details()
        
        
        
        if stat_details is None:
            total_customer_count    = Customer.count_merchant_customer(merchant_acct)
            total_sales             = 0
            total_transaction       = 0
            stat_details = {
                            'total_customer_count'  : total_customer_count,
                            'total_sales'           : total_sales,
                            'total_transaction'     : total_transaction,
                            
                            }
            merchant_acct.update_stat_details(stat_details)
        else:
            stat_details['merchant_name'] = merchant_acct.company_name
            stat_details['merchant_key'] = merchant_acct.key_in_str
    
    return jsonify(stat_details), 200
