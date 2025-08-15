'''
Created on 7 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager, CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask.helpers import url_for
from flask_babel import gettext
from datetime import datetime, date
from trexmodel.models.datastore.transaction_models import SalesTransaction
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexadmin.bigquery.transaction_query_executor import query_sales_monthly_by_outlet,\
    query_outlet_sales_monthly_by_transact_date
from trexlib.utils.string_util import str_to_bool
from trexlib.libs.flask_wtf.request_wrapper import request_values

merchant_sales_report_bp = Blueprint('merchant_sales_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/sales/')


#logger = logging.getLogger('report')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@merchant_sales_report_bp.context_processor
def merchant_sales_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_sales_report_bp.route('/sales-daily-report', methods=['GET'])
@login_required
def merchant_sales_daily_report(): 
    logger.debug('---merchant_sales_daily_report---')
    
    
    return render_template('/report/merchant/sales/sales_daily_report/sales_daily_report_enquiry.html', 
                           page_title               = gettext('Sales Daily Report'),
                           page_url                 = url_for('merchant_sales_report_bp.merchant_sales_daily_report'),
                           sales_daily_enquiry_url  = url_for('merchant_sales_report_bp.list_sales_daily_transaction', page_no=1, limit=10),
                           )
    

@merchant_sales_report_bp.route('/sales-daily-report/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_sales_daily_transaction(request_values, limit, page_no): 
    logger.debug('---request_values---')
    
    logger.debug('page_no=%s', page_no)
    
    outlet_key                  = request_values.get('sales_outlet')
    enquiry_date_str            = request_values.get('enquiry_date')
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    start                       = request_values.get('start')
    
    is_start_page               = str_to_bool(start)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    sales_transaction_list      = []
    next_cursor                 = None
    outlet_name                 = None
    
    logger.debug('outlet_key=%s', outlet_key)
    logger.debug('enquiry_date_str=%s', enquiry_date_str)
    logger.debug('cursor=%s', cursor)
    logger.debug('page_no_int=%d', page_no_int)
    logger.debug('limit_int=%d', limit_int)
    logger.debug('is_start_page=%d', is_start_page)
    
    try:
        db_client = create_db_client(caller_info="list_sales_daily_transaction")
        try:
            with db_client.context():
                transact_outlet             = Outlet.fetch(outlet_key)
                outlet_name                 = transact_outlet.name
                enquiry_date                = datetime.strptime(enquiry_date_str, '%d/%m/%Y')
                
                logger.debug('enquiry_date=%s', enquiry_date)
                
                (result, next_cursor)       = SalesTransaction.list_transaction_by_date(enquiry_date, including_reverted_transaction=False, transact_outlet=transact_outlet, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                total_count                 = SalesTransaction.count_transaction_by_date(enquiry_date, including_reverted_transaction=False, transact_outlet=transact_outlet)
                
                for r in result:
                    logger.debug('transaction id=%s', r.transaction_id)
                    sales_transaction_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  sales_outlet                  = outlet_key,
                                  enquiry_date                  = enquiry_date_str,
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('/report/merchant/sales/sales_daily_report/sales_daily_transaction_listing.html', 
                               sales_transaction_list       = sales_transaction_list,
                               end_point                    = 'merchant_sales_report_bp.list_sales_daily_transaction',
                               pager                        = pager,
                               pages                        = pages,
                               sales_outlet                 = outlet_key,
                               enquiry_date                 = enquiry_date_str,
                               pagination_target_selector   = '#sales_daily_transaction_div',
                               outlet_name                  = outlet_name,
                               currency_details             = get_merchant_configured_currency_details(),
                               
                               )
    
    except:
        logger.error('Fail to list sales daily transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
    
@merchant_sales_report_bp.route('/sales-monthly-report', methods=['GET'])
@login_required
def merchant_sales_monthly_report(): 
    logger.debug('---merchant_sales_monthly_report---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_sales_monthly_report")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        start_joined_year       = merchant_acct.plan_start_date.year
    
    today       = datetime.today()
    this_year   = today.year
    year_range_list =  []
    for year in range(start_joined_year, this_year+1):
        year_range_list.append(year)
    
    sorted_year_range_list = sorted(year_range_list , reverse=True)
    year_range_list = sorted_year_range_list
        
    return render_template('/report/merchant/sales/sales_monthly_report/sales_monthly_report_enquiry.html', 
                           page_title                   = gettext('Sales Monthly Report'),
                           page_url                     = url_for('merchant_sales_report_bp.merchant_sales_monthly_report'),
                           sales_monthly_enquiry_url    = url_for('merchant_sales_report_bp.list_sales_monthly_transaction'),
                           year_range_list              = year_range_list,
                           )
    

@merchant_sales_report_bp.route('/sales-monthly-report/query', methods=['GET'])
@login_required
@request_values
def list_sales_monthly_transaction(request_values): 
    logger.debug('---list_sales_monthly_transaction---')
    
    
    outlet_key                  = request_values.get('sales_outlet')
    enquiry_month_str           = request_values.get('enquiry_month')
    enquiry_year_str            = request_values.get('enquiry_year')
    
    
    logger.debug('outlet_key=%s', outlet_key)
    logger.debug('enquiry_month_str=%s', enquiry_month_str)
    logger.debug('enquiry_year_str=%s', enquiry_year_str)
    
    month_int       = int(enquiry_month_str)
    year_int        = int(enquiry_year_str)
    sales_outlet    = None
    enquiry_date    = date(year_int, month_int, 1) 
    
    try:
        db_client = create_db_client(caller_info="list_sales_monthly_transaction")
        try:
            with db_client.context():
                sales_outlet        = Outlet.get_or_read_from_cache(outlet_key)
                outlet_name         = sales_outlet.name
                
                
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        
        
        monthly_sales_data     =  query_outlet_sales_monthly_by_transact_date(sales_outlet, month_int, year_int)
        
        monthly_sales_summary      = {}
        total_transact_amount      = 0
        
        for sales_data in monthly_sales_data:
            
            logger.debug('sales_data=%s', sales_data)
            
            transact_date           = sales_data.get('TransactDate')
            transact_amount         = sales_data.get('TotalTransactAmount')
            
            total_transact_amount+=transact_amount
            
            logger.debug('transact_date=%s', transact_date)
            logger.debug('transact_amount=%s', transact_amount)
            
            monthly_sales_summary[transact_date] = {'transact_amount': transact_amount}
            
            
                
        monthly_sales_summary_final    = {}
        
        for d, s in monthly_sales_summary.items():
            monthly_sales_summary_final[datetime.strptime(d, '%Y-%m-%d').date()]   = s
        '''
        for d, s in monthly_transact_summary.items():
            monthly_transact_summary_final[datetime.strptime(d, '%Y-%m-%d').date()] = s
        '''
                
        logger.debug('monthly_sales_summary_final = %s', monthly_sales_summary_final)
        
        return render_template('/report/merchant/sales/sales_monthly_report/sales_monthly_listing.html', 
                           page_title                   = gettext('Sales Monthly Report'),
                           monthly_sales_summary        = monthly_sales_summary_final,
                           total_transact_amount        = total_transact_amount,
                           enquiry_date                 = enquiry_date,
                           outlet_name                  = outlet_name,
                           currency_details             = get_merchant_configured_currency_details(),
                           
                           )
    
    except:
        logger.error('Fail to list sales monthly transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@merchant_sales_report_bp.route('/sales-monthly-report-by-outlet', methods=['GET'])
@login_required
def merchant_sales_monthly_report_by_outlet(): 
    logger.debug('---merchant_sales_monthly_report_by_outlet---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_sales_monthly_report_by_outlet")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        start_joined_year       = merchant_acct.plan_start_date.year
    
    today       = datetime.today()
    this_year   = today.year
    year_range_list =  []
    for year in range(start_joined_year, this_year+1):
        year_range_list.append(year)
    
    sorted_year_range_list = sorted(year_range_list , reverse=True)
    year_range_list = sorted_year_range_list
        
    return render_template('/report/merchant/sales/sales_monthly_report_by_outlet/sales_monthly_report_by_outlet_enquiry.html', 
                           page_title                   = gettext('Sales Monthly Report By Outlet'),
                           page_url                     = url_for('merchant_sales_report_bp.merchant_sales_monthly_report_by_outlet'),
                           sales_monthly_enquiry_url    = url_for('merchant_sales_report_bp.list_sales_monthly_transaction_by_outlet'),
                           year_range_list              = year_range_list,
                           )           

@merchant_sales_report_bp.route('/sales-monthly-report-by-outlet/query', methods=['GET'])
@login_required
@request_values
def list_sales_monthly_transaction_by_outlet(request_values): 
    logger.debug('---list_sales_monthly_transaction_by_outlet---')
    
    
    outlet_key                  = request_values.get('sales_outlet')
    enquiry_month_str           = request_values.get('enquiry_month')
    enquiry_year_str            = request_values.get('enquiry_year')
    
    
    logger.debug('outlet_key=%s', outlet_key)
    logger.debug('enquiry_month_str=%s', enquiry_month_str)
    logger.debug('enquiry_year_str=%s', enquiry_year_str)
    
    month_int       = int(enquiry_month_str)
    year_int        = int(enquiry_year_str)
    enquiry_date    = date(year_int, month_int, 1) 
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_sales_monthly_report_by_outlet")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
    
    try:
        monthly_sales_data     =  query_sales_monthly_by_outlet(merchant_acct, month_int, year_int)
        
        monthly_sales_summary      = {}
        total_transact_amount      = 0
        
        for sales_data in monthly_sales_data:
            
            logger.debug('sales_data=%s', sales_data)
            
            transact_outlet_key     = sales_data.get('TransactOutlet')
            transact_amount         = sales_data.get('TotalTransactAmount')
            
            total_transact_amount+=transact_amount
            
            logger.debug('transact_outlet_key=%s', transact_outlet_key)
            logger.debug('transact_amount=%s', transact_amount)
            
            monthly_sales_summary[transact_outlet_key] = {'transact_amount': transact_amount}
            
            
                
        monthly_sales_summary_final    = {}
        with db_client.context():
            outlet_list = Outlet.list_by_merchant_acct(merchant_acct)
            
        for outlet in outlet_list:
            for d, s in monthly_sales_summary.items():
                if d==outlet.key_in_str:
                    monthly_sales_summary_final[outlet.name]   = s
                
        logger.debug('monthly_sales_summary_final = %s', monthly_sales_summary_final)
        
        return render_template('/report/merchant/sales/sales_monthly_report_by_outlet/sales_monthly_listing_by_outlet.html', 
                           page_title                   = gettext('Sales Monthly Report'),
                           monthly_sales_summary        = monthly_sales_summary_final,
                           total_transact_amount        = total_transact_amount,
                           enquiry_date                 = enquiry_date,
                           currency_details             = get_merchant_configured_currency_details(),
                           
                           )
    
    except:
        logger.error('Fail to list sales monthly transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 