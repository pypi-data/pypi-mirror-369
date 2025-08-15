'''
Created on 17 Oct 2024

@author: jacklok
'''
from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask.helpers import url_for
from flask_babel import gettext
from datetime import datetime, date
from trexlib.libs.flask_wtf.request_wrapper import request_args
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexlib.utils.string_util import is_not_empty
from trexanalytics.helper.bigquery_fetch_helper import fetch_top_spender_data
from trexmodel.models.datastore.customer_models import Customer

merchant_spender_performance_report_bp = Blueprint('merchant_spender_performance_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/performance/spender/')


logger = logging.getLogger('report')

'''
Blueprint settings here
'''
@merchant_spender_performance_report_bp.context_processor
def merchant_spender_performance_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_spender_performance_report_bp.route('/top-spender', methods=['GET'])
@login_required
def merchant_top_spender_report(): 
    logger.debug('---merchant_top_spender_report---')
    
    return render_template('/report/merchant/performance/top_spender/merchant_top_spender_report_enquiry.html', 
                           page_title                       = gettext('Top Spender Report'),
                           page_url                         = url_for('merchant_spender_performance_report_bp.merchant_top_spender_report'),
                           merchant_top_spender_enquiry_url = url_for('merchant_spender_performance_report_bp.show_merchant_top_spender_report'),
                           )
    
    
@merchant_spender_performance_report_bp.route('/top-spender-result', methods=['GET','POST'])
@request_args
def show_merchant_top_spender_report(request_args): 
    logger.debug('---show_merchant_top_spender_report---')
    
    outlet_key              = request_args.get('outlet_key')
    start_date_str          = request_args.get('start_date')
    end_date_str            = request_args.get('end_date')
    min_total_spending_amount  = request_args.get('min_total_spending_amount')
    min_total_visit_amount  = request_args.get('min_total_visit_amount')
    max_record              = request_args.get('max_record')
    
    logger.debug('show_merchant_top_spender_report: outlet_key=%s', outlet_key)
    logger.debug('show_merchant_top_spender_report: start_date_str=%s', start_date_str)
    logger.debug('show_merchant_top_spender_report: end_date_str=%s', end_date_str)
    logger.debug('show_merchant_top_spender_report: min_total_spending_amount=%s', min_total_spending_amount)
    logger.debug('show_merchant_top_spender_report: min_total_visit_amount=%s', min_total_visit_amount)
    logger.debug('show_merchant_top_spender_report: max_record=%s', max_record)
    
    start_date          = None
    end_date            = None
    transact_outlet     = None
    account_code        = None
    #report_data_path    = '/analytics/transaction/merchant-top-spender-by-date-range'
    
    if is_not_empty(min_total_spending_amount):
        min_total_spending_amount = float(min_total_spending_amount)
        
    if is_not_empty(min_total_visit_amount):
        min_total_visit_amount = int(min_total_visit_amount)        
    
    try:
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        db_client = create_db_client(caller_info="show_merchant_top_spender_report")
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            account_code    = merchant_acct.account_code
            if is_not_empty(outlet_key):
                transact_outlet     = Outlet.fetch(outlet_key)
                outlet_name         = transact_outlet.name
                #report_data_path    = '/analytics/transaction/merchant-outlet-top-spender-by-date-range'
                
            start_date                  = datetime.strptime(start_date_str, '%d/%m/%Y')
            end_date                    = datetime.strptime(end_date_str, '%d/%m/%Y')
        
        spending_details_list = fetch_top_spender_data(
                                    datetime.strftime(start_date, '%Y%m%d'),
                                    datetime.strftime(end_date, '%Y%m%d'),
                                    limit                       = int(max_record),
                                    account_code                = account_code,
                                    outlet_key                  = outlet_key,
                                    min_total_spending_amount   = min_total_spending_amount,
                                    min_total_visit_amount      = min_total_visit_amount,
                                )
        if spending_details_list:
            customer_dict_properties = [
                                        'name', 'reference_code', 'mobile_phone', 'email', 'birth_date',
                                        ]
            customer_keys_list = list(map(lambda x: x['customerKey'], spending_details_list))
            
            logger.debug('customer_keys_list=%s', customer_keys_list)
            
            with db_client.context():
                customer_details_list = Customer.list_by_customer_key_list(customer_keys_list)
                logger.debug('customer_details_list=%s', customer_details_list)
                for spending_details in spending_details_list:
                    for customer_details in customer_details_list:
                        if spending_details['customerKey'] == customer_details.key_in_str:
                            spending_details['customer_details'] = customer_details.to_dict(dict_properties=customer_dict_properties)
                            logger.debug('found match customer key')
                            break
        
    except:
        logger.error('Failed to show top spender report due to %s', get_tracelog())
        
        
    return render_template('/report/merchant/performance/top_spender/merchant_top_spender_report.html', 
                               outlet_key                   = outlet_key,
                               start_date                   = start_date,
                               end_date                     = end_date,
                               outlet_name                  = outlet_name if transact_outlet else None,
                               #account_code                 = account_code,
                               #report_data_url              = '%s%s'% (APPLICATION_BASE_URL, report_data_path),
                               spending_details_list        = spending_details_list,
                               #currency_details             = get_merchant_configured_currency_details(),
                               
                               )
    

    
@merchant_spender_performance_report_bp.route('/non-active', methods=['GET'])
@login_required
def merchant_last_active_report(): 
    logger.debug('---merchant_last_active_report---')
    
    return render_template('/report/merchant/performance/last_active/merchant_last_active_customer_report_enquiry.html', 
                           page_title                                   = gettext('Last Active Customer Report'),
                           page_url                                     = url_for('merchant_spender_performance_report_bp.merchant_last_active_report'),
                           merchant_last_active_customer_enquiry_url    = url_for('merchant_spender_performance_report_bp.show_merchant_last_active_customer_report'),
                           )    
    
    
@merchant_spender_performance_report_bp.route('/non-active-customer-result', methods=['GET','POST'])
#@login_required
@request_args
def show_merchant_last_active_customer_report(request_args): 
    logger.debug('---show_merchant_last_active_customer_report---')
    
    last_active_date_since   = request_args.get('last_active_date_since')
    last_active_date_end     = request_args.get('last_active_date_end')
    max_record              = request_args.get('max_record')
    show_customer_details   = True
    
    
    logger.debug('show_merchant_last_active_customer_report: last_active_date_since=%s', last_active_date_since)
    logger.debug('show_merchant_last_active_customer_report: last_active_date_end=%s', last_active_date_end)
    logger.debug('show_merchant_last_active_customer_report: max_record=%s', max_record)
    
    last_active_date_since                  = datetime.strptime(last_active_date_since, '%d/%m/%Y')
    last_active_date_end                    = datetime.strptime(last_active_date_end, '%d/%m/%Y')
    
    logger.debug('show_merchant_last_active_customer_report: last_active_date_since=%s', last_active_date_since)
    logger.debug('show_merchant_last_active_customer_report: last_active_date_end=%s', last_active_date_end)
    
    customers_dict_list = []
    total_count = 0
    try:
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        db_client = create_db_client(caller_info="show_merchant_non_active_customer_report")
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if show_customer_details:
                customer_dict_properties = [
                                        'name', 'reference_code', 'mobile_phone', 'email', 'birth_date',
                                        'last_transact_datetime',
                                        ]
                customers_list = Customer.list_last_active_customer_by_range(merchant_acct, 
                                                       last_active_date_since, 
                                                       last_active_date_end,)
                for customer in customers_list:
                    customers_dict_list.append(customer.to_dict(dict_properties=customer_dict_properties))
            else:
                total_count = Customer.count_last_active_customer_by_range(merchant_acct, 
                                                       last_active_date_since, 
                                                       last_active_date_end,)
            
        
    except:
        logger.error('Failed to show non active report due to %s', get_tracelog())
        
        
    return render_template('/report/merchant/performance/last_active/merchant_last_active_customer_report.html', 
                               spending_details_list        = customers_dict_list,
                               total_count                  = total_count,
                               show_customer_details        = show_customer_details,
                               )        
    
    