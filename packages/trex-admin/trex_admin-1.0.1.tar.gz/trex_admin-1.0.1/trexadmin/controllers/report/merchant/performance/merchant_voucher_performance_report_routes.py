'''
Created on 25 Nov 2024

@author: jacklok
'''
from flask import Blueprint, render_template, request, current_app
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager, CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask.helpers import url_for
from flask_babel import gettext
from datetime import datetime, date
from trexlib.libs.flask_wtf.request_wrapper import request_args
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexadmin.libs.flask.utils.flask_helper import get_merchant_configured_currency_details,\
    get_loggedin_merchant_user_account
from trexlib.utils.string_util import is_not_empty
from flask.globals import session
from trexconf.conf import APPLICATION_BASE_URL
from trexanalytics.helper.bigquery_fetch_helper import fetch_top_spender_data,\
    fetch_merchant_voucher_performance_data
from trexmodel.models.datastore.customer_models import Customer
from dateutil.relativedelta import relativedelta
from trexmodel.models.datastore.voucher_models import MerchantVoucher

merchant_voucher_performance_report_bp = Blueprint('merchant_voucher_performance_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/performance/voucher/')


logger = logging.getLogger('report')

'''
Blueprint settings here
'''
@merchant_voucher_performance_report_bp.context_processor
def merchant_voucher_performance_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_voucher_performance_report_bp.route('/daily', methods=['GET'])
@login_required
def merchant_voucher_daily_performance_report(): 
    logger.debug('---merchant_voucher_daily_performance_report---')
    
    return render_template('/report/merchant/performance/voucher/daily/merchant_voucher_daily_performance_report_enquiry.html', 
                           page_title                       = gettext('Voucher Daily Performance Report'),
                           page_url                         = url_for('merchant_voucher_performance_report_bp.merchant_voucher_daily_performance_report'),
                           merchant_top_spender_enquiry_url = url_for('merchant_voucher_performance_report_bp.show_merchant_voucher_daily_performance_report'),
                           )
    
@merchant_voucher_performance_report_bp.route('/monthly', methods=['GET'])
@login_required
def merchant_voucher_monthly_performance_report(): 
    logger.debug('---merchant_voucher_monthly_performance_report---')
    
    return render_template('/report/merchant/performance/voucher/monthly/merchant_voucher_daily_performance_report_enquiry.html', 
                           page_title                       = gettext('Voucher Monthly Performance Report'),
                           page_url                         = url_for('merchant_voucher_performance_report_bp.merchant_voucher_monthly_performance_report'),
                           merchant_top_spender_enquiry_url = url_for('merchant_voucher_performance_report_bp.show_merchant_top_spender_report'),
                           )    


@merchant_voucher_performance_report_bp.route('/date-range', methods=['GET'])
@login_required
def merchant_voucher_by_date_range_performance_report(): 
    logger.debug('---merchant_voucher_by_date_range_performance_report---')
    
    return render_template('/report/merchant/performance/voucher/date_range/merchant_voucher_date_range_performance_report_enquiry.html', 
                           page_title                       = gettext('Voucher Performance Report'),
                           page_url                         = url_for('merchant_voucher_performance_report_bp.merchant_voucher_by_date_range_performance_report'),
                           merchant_voucher_performance_enquiry_url = url_for('merchant_voucher_performance_report_bp.show_merchant_voucher_performance_by_date_range_report'),
                           )

@merchant_voucher_performance_report_bp.route('/daily-result', methods=['GET','POST'])
@request_args
def show_merchant_voucher_daily_performance_report(request_args): 
    logger.debug('---show_merchant_voucher_daily_performance_report---')
    
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
    
@merchant_voucher_performance_report_bp.route('/result-by-date-range', methods=['GET','POST'])
@request_args
def show_merchant_voucher_performance_by_date_range_report(request_args): 
    logger.debug('---show_merchant_voucher_performance_by_date_range_report---')
    voucher_key             = request_args.get('voucher_key')
    start_date_str          = request_args.get('start_date')
    end_date_str            = request_args.get('end_date')
    
    logger.debug('voucher_key=%s', voucher_key)
    logger.debug('start_date_str=%s', start_date_str)
    logger.debug('end_date_str=%s', end_date_str)
    
    start_date          = None
    end_date            = None
    account_code        = None
    voucher_result_list = []
    #report_data_path    = '/analytics/transaction/merchant-top-spender-by-date-range'
    
    try:
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        db_client = create_db_client(caller_info="show_merchant_voucher_performance_by_date_range_report")
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            account_code    = merchant_acct.account_code
            
            start_date                  = datetime.strptime(start_date_str, '%d/%m/%Y')
            end_date                    = datetime.strptime(end_date_str, '%d/%m/%Y')
        
        voucher_result_list = fetch_merchant_voucher_performance_data(
                                    start_date,
                                    end_date,
                                    account_code    = account_code,
                                    voucher_key     = voucher_key,
                                    
                                )
        
        logger.debug('voucher_result_list=%s', voucher_result_list)
        
        if voucher_result_list:
            if is_not_empty(voucher_key):
                voucher_keys_list = [voucher_key]
            else:
                voucher_keys_list = list(map(lambda x: x['voucher_key'], voucher_result_list))
            
            logger.debug('voucher_keys_list=%s', voucher_keys_list)
            
            with db_client.context():
                merchant_vouchers_list = MerchantVoucher.list_by_voucher_key_list(voucher_keys_list)
                logger.debug('voucher_keys_list=%s', voucher_keys_list)
                
                for voucher_result in voucher_result_list:
                    for merchant_voucher in merchant_vouchers_list:
                        merchant_voucher_key = merchant_voucher.key_in_str
                        
                        if voucher_result['voucher_key'] == merchant_voucher_key:
                            voucher_result['voucher_label'] = merchant_voucher.label
                            logger.debug('found match voucher key')
                            break
                            
        else:
            voucher_result_list = []
    except:
        logger.error('Failed to show voucher performance report due to %s', get_tracelog())
        
        
    return render_template('/report/merchant/performance/voucher/date_range/merchant_voucher_date_range_performance_report.html', 
                               start_date                   = start_date,
                               end_date                     = end_date,
                               voucher_result_list          = voucher_result_list,
                               
                               )    