'''
Created on 31 Mar 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client 
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.merchant_models import Outlet
from trexadmin.forms.merchant.customer_transaction_forms import CustomerTransactionDetailsForm
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantUser
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexadmin.libs.jinja.common_filters import pretty_datetime_filter
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.controllers.system.system_route_helpers import get_currency_config
import jinja2
from trexadmin.libs.jinja.program_filters import program_reward_format_label as program_reward_format_label_filter
from trexadmin.libs.flask.pagination import CursorPager
from trexlib.utils.common.currency_util import format_currency as currency_formatting
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account, get_merchant_configured_currency_details
from trexmodel.models.datastore.helper.reward_transaction_helper import revert_transaction, create_reward_transaction
from datetime import timedelta, datetime
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_transaction_upstream_for_merchant
from trexmodel.models.datastore.model_decorators import model_transactional
from trexlib.utils.string_util import is_not_empty


merchant_customer_transaction_bp = Blueprint('merchant_customer_transaction_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/customer-transaction')


logger = logging.getLogger('debug')

'''
@jinja2.contextfilter
@merchant_customer_transaction_bp.app_template_filter()
def pretty_datetime(context, datetime_str):
    return pretty_datetime_filter(context, datetime_str)
'''

@jinja2.contextfilter
@merchant_customer_transaction_bp.app_template_filter()
def format_currency_with_currency_label(context, value_2_format):
    currency_details = get_merchant_configured_currency_details()
    return currency_formatting(value_2_format, 
                        currency_label=currency_details.get('currency_label'),
                        floating_point=currency_details.get('floating_point'),
                        decimal_separator=currency_details.get('decimal_separator'),
                        thousand_separator=currency_details.get('thousand_separator'),
                        show_thousand_separator=True, 
                        show_currency_label = True)    



@jinja2.contextfilter
@merchant_customer_transaction_bp.app_template_filter()
def program_reward_format_label(context, code):
    return program_reward_format_label_filter(code)

'''
Blueprint settings here
'''
@merchant_customer_transaction_bp.context_processor
def merchant_customer_transaction_bp_inject_settings():
    
    return dict(
                )
    
@merchant_customer_transaction_bp.route('/', methods=['GET'])
@login_required
def customer_transaction_search(): 
    logger.debug('---manage_customer---')
    
    
    return render_template('merchant/crm/customer_transaction/customer_transaction_index.html', 
                           page_title           = gettext('Customer Transaction'),
                           page_url             = url_for('merchant_customer_transaction_bp.customer_transaction_search'),
                           
                           )    
    
@merchant_customer_transaction_bp.route('/customer-transaction/<customer_key>', methods=['GET'])
@login_required
def enter_customer_transaction(customer_key): 
    logger.debug('---enter_customer_transaction---')
    
    db_client = create_db_client(caller_info="enter_customer_transaction")
    
    with db_client.context():
        customer        = Customer.fetch(customer_key)
        merchant_acct   = customer.registered_merchant_acct
        currency_code   = merchant_acct.currency_code
        customer_details= customer.to_dict()
    
    currency_details    = get_currency_config(currency_code)    
    
    return render_template('merchant/crm/customer_transaction/customer_transaction_details.html', 
                           page_title               = gettext('Enter Customer Transaction'),
                           customer                 = customer_details,
                           currency_details         = currency_details,
                           post_url                 = url_for('merchant_customer_transaction_bp.enter_customer_transaction_post'),
                           ) 


    
@merchant_customer_transaction_bp.route('/customer-transaction', methods=['post'])
def enter_customer_transaction_post():
    logger.debug('--- submit enter_customer_transaction_post ---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    customer_transaction_details_data = request.form
    
    logger.debug('customer_transaction_details_data=%s', customer_transaction_details_data)
    
    customer_transaction_details_form = CustomerTransactionDetailsForm(customer_transaction_details_data)
    customer_key = customer_transaction_details_form.customer_key.data
    
    logger.debug('customer_key=%s', customer_key)
    
    try:
        db_client = create_db_client(caller_info="enter_customer_transaction_post")
        
        invoice_id          = customer_transaction_details_form.invoice_id.data
        promotion_code      = customer_transaction_details_form.promotion_code.data
        transact_amount     = customer_transaction_details_form.transact_amount.data
        
        logger.debug('transact_amount=%s', transact_amount)
        logger.debug('invoice_id=%s', invoice_id)
        logger.debug('promotion_code=%s', promotion_code)
        
        
        
        if is_not_empty(invoice_id):
            with db_client.context():
                check_transaction_by_invoice_id = CustomerTransaction.get_by_invoice_id(invoice_id, promotion_code=promotion_code)
            
            if check_transaction_by_invoice_id:
                return create_rest_message(gettext('The transaction have been submitted') , status_code=StatusCode.BAD_REQUEST)
        
        if customer_transaction_details_form.validate():
            
            transact_datetime_in_gmt    = customer_transaction_details_form.transact_datetime.data
            
            logger.debug('transact_datetime_in_gmt b4=%s', transact_datetime_in_gmt)
            
            with db_client.context():   
                customer = Customer.fetch(customer_key)
                if customer:
                    merchant_acct = customer.registered_merchant_acct
                    
                    transact_outlet = Outlet.fetch(customer_transaction_details_form.transact_outlet.data)
                logger.debug('customer=%s', customer)
                
            
            if customer is None:
                return create_rest_message(gettext('Invalid customer data'), status_code=StatusCode.BAD_REQUEST)
            
            
            transact_datetime = None
            now               = datetime.utcnow()
                
            if transact_datetime_in_gmt:
                transact_datetime    =  transact_datetime_in_gmt - timedelta(hours=merchant_acct.gmt_hour)
                
                logger.debug('transact_datetime after=%s', transact_datetime)
                
                if transact_datetime > now:
                    return create_rest_message(gettext('Transact datetime cannot be future'), status_code=StatusCode.BAD_REQUEST)
            else:
                transact_datetime   = now
            
               
                
            with db_client.context():
                logger.debug('going to call give_reward_transaction')
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                
                create_reward_transaction(customer, 
                                        transact_outlet     = transact_outlet, 
                                        sales_amount        = float(customer_transaction_details_form.transact_amount.data),
                                        tax_amount          = float(customer_transaction_details_form.tax_amount.data),
                                        invoice_id          = customer_transaction_details_form.invoice_id.data,
                                        remarks             = customer_transaction_details_form.remarks.data,
                                        transact_by         = merchant_user,
                                        transact_datetime   = transact_datetime,
                                        promotion_code      = promotion_code,
                                        )
                #__start_transaction_for_customer_transaction(transact_outlet, customer_transaction_details_form, logged_in_merchant_user, transact_datetime)
                    
            
            return create_rest_message(gettext('Customer transaction have been created'), status_code=StatusCode.OK)
                
                
        else:
            error_message = customer_transaction_details_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to create customer transaction due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to create customer transaction'), status_code=StatusCode.BAD_REQUEST)  
    
@merchant_customer_transaction_bp.route('/customer-transaction/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_customer_transaction(limit, page_no): 
    logger.debug('---list_customer_transaction---')
    
    logger.debug('page_no=%s', page_no)
    
    customer_key                = request.args.get('customer_key')
    cursor                      = request.args.get('cursor')
    previous_cursor             = request.args.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    customer_transaction_list   = []
    next_cursor                 = None
    
    logger.debug('list_customer_transaction: customer_key=%s', customer_key)
    logger.debug('list_customer_transaction: cursor=%s', cursor)
    logger.debug('list_customer_transaction: limit_int=%d', limit_int)
    
    try:
        db_client = create_db_client(caller_info="list_customer_transaction")
        try:
            with db_client.context():
                customer                    = Customer.fetch(customer_key)
                (result, next_cursor)       = CustomerTransaction.list_customer_transaction(customer, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                total_count                 = CustomerTransaction.count_customer_transaction(customer)
                
                for r in result:
                    customer_transaction_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_customer_transaction: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  customer_key                  = customer_key
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('merchant/crm/customer_transaction/customer_transaction_listing.html', 
                               customer_transaction_list    = customer_transaction_list,
                               end_point                    = 'merchant_customer_transaction_bp.list_customer_transaction',
                               pager                        = pager,
                               pages                        = pages,
                               customer_key                 = customer_key,
                               pagination_target_selector   = '#customer_transaction_listing_div',
                               
                               )
    
    except:
        logger.error('Fail to list customer due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    
@merchant_customer_transaction_bp.route('/revert-transaction/<transaction_key>', methods=['post'])
def revert_transaction_post(transaction_key):
    logger.debug('--- submit revert_transaction_post ---')
    
    logger.debug('transaction_key=%s', transaction_key)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    try:
        db_client       = create_db_client(caller_info="revert_transaction_post")
        revert_status   = False
        
        reverted_datetime   = datetime.utcnow()
        
        with db_client.context():   
            customer_transction = CustomerTransaction.fetch(transaction_key)
            customer_transction.reverted_datetime = reverted_datetime
            
            
            logger.debug('revert_transaction_post: reverted_datetime=%s', reverted_datetime)
            
            if customer_transction:
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                revert_status = __revert_customer_transaction(customer_transction, merchant_user, reverted_datetime)
                
                logger.debug('revert_status=%s', revert_status)
            
            if revert_status:
                create_merchant_customer_transaction_upstream_for_merchant(customer_transction, Reverted=True)
                
        if revert_status:
            return create_rest_message(gettext('Customer transaction have been reverted'),
                                                reverted_datetime_text = pretty_datetime_filter(None, reverted_datetime), 
                                                status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext('Failed to revert transaction'), status_code=StatusCode.BAD_REQUEST)
        
        if customer_transction is None:
            return create_rest_message(gettext('Invalid transaction key'), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext('Customer transaction have been reverted successfully'), status_code=StatusCode.OK)
            
    except:
        logger.error('Fail to revert customer transaction due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to revert customer transaction'), status_code=StatusCode.BAD_REQUEST)    
    
@model_transactional(desc="__revert_customer_transaction")
def __revert_customer_transaction(customer_transction, reverted_by, reverted_datetime):     
    customer_acct = customer_transction.transact_customer_acct   
    return revert_transaction(customer_transction, customer_acct, reverted_by, reverted_datetime=reverted_datetime)    
