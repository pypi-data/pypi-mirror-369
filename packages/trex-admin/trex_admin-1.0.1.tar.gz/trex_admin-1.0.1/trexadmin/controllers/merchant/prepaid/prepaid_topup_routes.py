'''
Created on 2 Sep 2021

@author: jacklok
'''

from flask import Blueprint, render_template, request, abort
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser, Outlet

from trexadmin.forms.merchant.prepaid_forms import PrepaidTopupForm
from trexmodel.models.datastore.prepaid_models import PrepaidSettings
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.helper.reward_transaction_helper import create_topup_prepaid_transaction
from trexadmin.libs.jinja.common_filters import format_currency_with_currency_label_filter

prepaid_topup_bp = Blueprint('prepaid_topup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/prepaid/topup')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@prepaid_topup_bp.context_processor
def prepaid_topup_settings_bp_inject_settings():
    
    return dict(
                
                )

@prepaid_topup_bp.route('/<customer_key>', methods=['GET'])
@login_required
def enter_prepaid_topup(customer_key): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    currency_details            = get_merchant_configured_currency_details()
    prepaid_program_available   = False
    prepaid_program_list        = []
    db_client = create_db_client(caller_info="enter_prepaid_topup")
    try:
        with db_client.context():
            merchant_acct      = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            customer           = Customer.fetch(customer_key)   
            
            if customer:
                customer = customer.to_dict()
                
        if customer is None:
            abort(StatusCode.BAD_REQUEST)                     
        
        if merchant_acct.prepaid_configuration and merchant_acct.prepaid_configuration.get('count')>0:
            prepaid_program_available = True
            prepaid_program_list = merchant_acct.prepaid_configuration.get('programs')
            '''
            for program in merchant_acct.prepaid_configuration.get('programs'):
                prepaid_program_list.append({
                                            'program_key'   : program.get('program_key'),
                                            'label'         : program.get('label'),
                                            })
            '''
    except:
        logger.error('Fail to show manage prepaid program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/prepaid/topup/topup_prepaid.html',
                           page_title                       = gettext('Topup Prepaid'),
                           customer                         = customer,
                           prepaid_program_list             = prepaid_program_list,
                           currency_details                 = currency_details,
                           post_url                         = url_for('prepaid_topup_bp.enter_prepaid_topup_post'),
                           prepaid_program_available        = prepaid_program_available,
                           )
    
@prepaid_topup_bp.route('/', methods=['post'])
def enter_prepaid_topup_post():
    logger.debug('--- submit enter_prepaid_topup_post ---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    topup_prepaid_data      = request.form 
    prepaid_topup_form      = PrepaidTopupForm(topup_prepaid_data)  
    prepaid_summary         = {}
    currency_details        = get_merchant_configured_currency_details()
    logger.debug('topup_prepaid_data=%s', topup_prepaid_data)
    
    try:
        if prepaid_topup_form.validate():
            db_client = create_db_client(caller_info="prepaid_setup_post")
            topup_success = False
            
            topup_amount        = prepaid_topup_form.topup_amount.data
            tier_topup_amount   = prepaid_topup_form.tier_topup_amount.data
            
            topup_amount        = topup_amount or tier_topup_amount
            topup_amount        = float(topup_amount)
            
            if topup_amount<=0:
                return create_rest_message(gettext('Topup amount is required'), status_code=StatusCode.BAD_REQUEST)
            
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                customer_acct       = Customer.fetch(prepaid_topup_form.customer_key.data)
                prepaid_program     = PrepaidSettings.fetch(prepaid_topup_form.prepaid_program.data)
                topup_outlet        = Outlet.fetch(prepaid_topup_form.topup_outlet.data)
                invoice_id          = prepaid_topup_form.invoice_id.data
                remarks             = prepaid_topup_form.remarks.data
                
                if customer_acct and prepaid_program:
                    
                    (customer_transaction, prepaid_summary) = create_topup_prepaid_transaction(customer_acct, prepaid_program, 
                                                                                                topup_amount=topup_amount, 
                                                                                                topup_outlet=topup_outlet, 
                                                                                                topup_by=merchant_user, 
                                                                                                invoice_id=invoice_id, 
                                                                                                remarks = remarks)
                    topup_success = True
                
                    
            if topup_success:
                prepaid_amount = prepaid_summary.get('amount')
                formatted_prepaid_amount = format_currency_with_currency_label_filter(prepaid_amount, currency_details=currency_details)
                
                return create_rest_message(gettext('Topup prepaid successfully, customer total prepaid amount is %s' % formatted_prepaid_amount), status_code=StatusCode.OK)
            else:
                return create_rest_message(gettext('Failed to topup prepaid'), status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = prepaid_topup_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to topup prepaid due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
     
