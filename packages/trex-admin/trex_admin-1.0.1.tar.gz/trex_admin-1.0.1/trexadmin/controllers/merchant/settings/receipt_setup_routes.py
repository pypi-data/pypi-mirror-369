'''
Created on 8 Mar 2022

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    ReceiptSetup
import json

receipt_setup_bp = Blueprint('receipt_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/receipt-setup')

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@receipt_setup_bp.context_processor
def receipt_setup_bp_inject_settings():
    
    return dict(
                
                )


@receipt_setup_bp.route('/', methods=['GET'])
@login_required
def receipt_setup(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="receipt_setup")
    receipt_setup               = None
    receipt_header_data_list    = None
    receipt_footer_data_list    = None
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        receipt_setup   = ReceiptSetup.get_by_merchant_acct(merchant_acct)
        if receipt_setup:
            receipt_header_data_list    = receipt_setup.receipt_header_settings
            receipt_footer_data_list    = receipt_setup.receipt_footer_settings
            
    
    return render_template('merchant/settings/manage_receipt/receipt_setup.html',
                           page_title                   = gettext('Receipt Setup'),
                           update_receipt_header_url    = url_for('receipt_setup_bp.update_receipt_header_data_post'),
                           update_receipt_footer_url    = url_for('receipt_setup_bp.update_receipt_footer_data_post'),
                           receipt_header_data_list     = receipt_header_data_list,
                           receipt_footer_data_list     = receipt_footer_data_list,
                           )
    
@receipt_setup_bp.route('/update-receipt-header-data', methods=['POST'])
@login_required
def update_receipt_header_data_post():
    receipt_header_data                 = request.form
    logged_in_merchant_user             = get_loggedin_merchant_user_account()
    header_data_list                    = receipt_header_data.getlist('header_data_list[]')
    db_client                           = create_db_client(caller_info="update_receipt_header_data_post")
    
    logger.debug('receipt_header_data=%s', receipt_header_data);
    logger.debug('header_data_list=%s', header_data_list);
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        receipt_setup   = ReceiptSetup.get_by_merchant_acct(merchant_acct)
        
        logger.debug('receipt_setup=%s', receipt_setup);
        
        if receipt_setup:
            ReceiptSetup.update(receipt_setup, receipt_header_settings=header_data_list, receipt_footer_settings = receipt_setup.receipt_footer_settings)
        else:
            receipt_setup = ReceiptSetup.create(merchant_acct, receipt_header_settings=header_data_list)
            
    if receipt_setup:
        return create_rest_message(gettext('Receipt header have been updated'), 
                                            status_code                 = StatusCode.OK,
                                            )
    else:
        return create_rest_message(gettext('Failed to update receipt header'), status_code=StatusCode.BAD_REQUEST) 
    
@receipt_setup_bp.route('/update-receipt-footer-data', methods=['POST'])
@login_required
def update_receipt_footer_data_post():
    receipt_footer_data                 = request.form
    logged_in_merchant_user             = get_loggedin_merchant_user_account()
    footer_data_list                    = json.loads(receipt_footer_data.get('footer_data_list[]'))
    db_client                           = create_db_client(caller_info="update_receipt_footer_data_post")
    
    logger.debug('footer_data_list=%s', footer_data_list);
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        receipt_setup   = ReceiptSetup.get_by_merchant_acct(merchant_acct)
        logger.debug('receipt_setup=%s', receipt_setup)
        
        if receipt_setup:
            logger.debug('Going to update receipt')
            ReceiptSetup.update(receipt_setup, receipt_footer_settings=footer_data_list, receipt_header_settings = receipt_setup.receipt_header_settings)
        else:
            logger.debug('Going to create receipt')
            receipt_setup = ReceiptSetup.create(merchant_acct, receipt_footer_settings=footer_data_list)
            
    if receipt_setup:
        return create_rest_message(gettext('Receipt footer have been updated'), 
                                            status_code                 = StatusCode.OK,
                                            )
    else:
        return create_rest_message(gettext('Failed to update receipt footer'), status_code=StatusCode.BAD_REQUEST)        