'''
Created on 4 Mar 2022

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
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.pos_models import RoundingSetup
from trexadmin.forms.merchant.pos_forms import RoundingSetupForm

rounding_setup_bp = Blueprint('rounding_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/rounding-setup')

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@rounding_setup_bp.context_processor
def rouding_setup_bp_setup_settings_bp_inject_settings():
    
    return dict(
                
                )


@rounding_setup_bp.route('/', methods=['GET'])
@login_required
def rounding_setup(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="rounding_setup")
    
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        rounding_setup      = RoundingSetup.get_by_merchant_acct(merchant_acct)
        if rounding_setup:
            rounding_setup = rounding_setup.to_dict()
    
    return render_template('merchant/pos/rounding_setup/rounding_setup.html',
                           page_title                   = gettext('Rounding Setup'),
                           submit_rounding_setup_url    = url_for('rounding_setup_bp.update_rounding_setup_post'),
                           rounding_setup               = rounding_setup,
                           )
    
@rounding_setup_bp.route('/add', methods=['POST'])
@login_required
def update_rounding_setup_post():
    rounding_setup_data      = request.form
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    logger.debug('rounding_setup_data=%s', rounding_setup_data)  
    db_client                   = create_db_client(caller_info="rouding_setup")
    
    rounding_setup_form = RoundingSetupForm(rounding_setup_data)
    if rounding_setup_form.validate():
        rounding_interval   = rounding_setup_form.rounding_interval.data
        rounding_rule       = rounding_setup_form.rounding_rule.data
        
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            rounding_setup      = RoundingSetup.get_by_merchant_acct(merchant_acct)
            
            logger.debug('rounding_setup=%s', rounding_setup)
            
            if rounding_setup is None:
                logger.debug('Going to create rounding setup');
                rounding_setup = RoundingSetup.create(rounding_interval, rounding_rule, merchant_acct)
            else:
                logger.debug('Going to update rounding setup');
                RoundingSetup.update(rounding_setup, rounding_interval, rounding_rule)
    else:
        error_message = rounding_setup_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)  
    
    return create_rest_message(gettext('Rounding setup have been updated'), 
                                                status_code             = StatusCode.OK,
                                                )