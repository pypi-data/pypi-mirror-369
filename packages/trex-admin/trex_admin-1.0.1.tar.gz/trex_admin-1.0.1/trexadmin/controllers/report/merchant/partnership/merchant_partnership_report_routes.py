'''
Created on 21 May 2025

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
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexadmin.bigquery.transaction_query_executor import query_reward_monthly_by_outlet,\
    query_partnership_transaction_monthly_by_partner_merchant
from flask.json import jsonify
from trexmodel import program_conf
from trexlib.utils.string_util import str_to_bool, is_empty
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexmodel.models.datastore.partnership_models import PartnershipRewardTransaction

merchant_partnership_report_bp = Blueprint('merchant_partnership_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/partnership/')


#logger = logging.getLogger('report')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@merchant_partnership_report_bp.context_processor
def merchant_partnership_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                )

@merchant_partnership_report_bp.route('/partnership-daily-report', methods=['GET'])
@login_required
def merchant_partnership_daily_report(): 
    logger.debug('---merchant_partnership_daily_report---')
    
    
    return render_template('/report/merchant/partnership/partnership_daily_report/partnership_daily_report_enquiry.html', 
                           page_title                       = gettext('Partnership Daily Report'),
                           page_url                         = url_for('merchant_partnership_report_bp.merchant_partnership_daily_report'),
                           partnership_daily_enquiry_url    = url_for('merchant_partnership_report_bp.list_partnership_daily_transaction', page_no=1, limit=10),
                           )
    

@merchant_partnership_report_bp.route('/partnership-daily-report/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_partnership_daily_transaction(request_values, limit, page_no): 
    logger.debug('---list_partnership_daily_transaction---')
    
    logger.debug('request_values=%s', request_values)
    logger.debug('page_no=%s', page_no)
    
    partner_merchant_key        = request_values.get('partner_merchant_key')
    enquiry_date_str            = request_values.get('enquiry_date')
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    start                       = request_values.get('start')
    
    is_start_page               = str_to_bool(start)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    partnership_transaction_list= []
    next_cursor                 = None
    
    logger.debug('list_partnership_daily_transaction: partner_merchant_key=%s', partner_merchant_key)
    logger.debug('list_partnership_daily_transaction: enquiry_date_str=%s', enquiry_date_str)
    logger.debug('list_partnership_daily_transaction: cursor=%s', cursor)
    logger.debug('list_partnership_daily_transaction: page_no_int=%d', page_no_int)
    logger.debug('list_partnership_daily_transaction: limit_int=%d', limit_int)
    logger.debug('list_partnership_daily_transaction: is_start_page=%d', is_start_page)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    try:
        db_client = create_db_client(caller_info="list_reward_daily_transaction")
        try:
            with db_client.context():
                merchant_acct               = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                partner_merchant_acct       = MerchantAcct.fetch(partner_merchant_key)
                
                enquiry_date                = datetime.strptime(enquiry_date_str, '%d/%m/%Y')
                
                logger.debug('list_reward_daily_transaction: enquiry_date=%s', enquiry_date)
                
                (result, next_cursor)       = PartnershipRewardTransaction.list_transaction_by_date(enquiry_date, merchant_acct=merchant_acct, partner_merchant_acct=partner_merchant_acct, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                
                for r in result:
                    partnership_transaction_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_reward_daily_transaction: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  partner_merchant_key          = partner_merchant_key,
                                  enquiry_date                  = enquiry_date_str,
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('/report/merchant/partnership/partnership_daily_report/daily_transaction_listing.html', 
                               partnership_transaction_list = partnership_transaction_list,
                               end_point                    = 'merchant_partnership_report_bp.list_partnership_daily_transaction',
                               pager                        = pager,
                               pages                        = pages,
                               partner_merchant_key         = partner_merchant_key,
                               enquiry_date                 = enquiry_date_str,
                               pagination_target_selector   = '#partnership_daily_transaction_div',
                               partner_merchant_name        = partner_merchant_acct.brand_name,
                               currency_details             = get_merchant_configured_currency_details(),
                               
                               )
    
    except:
        logger.error('Fail to list partnership daily transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   

@merchant_partnership_report_bp.route('/partnership-monthly-report', methods=['GET'])
@login_required
def merchant_partnership_monthly_report(): 
    logger.debug('---merchant_partnership_monthly_report---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_partnership_monthly_report")
    with db_client.context():
        merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        start_joined_year       = merchant_acct.plan_start_date.year
    
    today       = datetime.today()
    this_year   = today.year
    year_range_list =  []
    for year in range(start_joined_year, this_year+1):
        year_range_list.append(year)
    
    sorted_year_range_list = sorted(year_range_list , reverse=True)
    year_range_list = sorted_year_range_list
        
    return render_template('/report/merchant/partnership/partnership_monthly_report/partnership_monthly_report_enquiry.html', 
                           page_title                       = gettext('Partnership Monthly Report'),
                           page_url                         = url_for('merchant_partnership_report_bp.merchant_partnership_monthly_report'),
                           partnership_monthly_enquiry_url  = url_for('merchant_partnership_report_bp.list_partnership_monthly_transaction'),
                           year_range_list                  = year_range_list,
                           )
    

@merchant_partnership_report_bp.route('/partnership-monthly-report/query', methods=['GET'])
@login_required
@request_values
def list_partnership_monthly_transaction(request_values): 
    logger.debug('---list_partnership_monthly_transaction---')
    
    
    partner_merchant_key        = request_values.get('partner_merchant_key')
    enquiry_month_str           = request_values.get('enquiry_month')
    enquiry_year_str            = request_values.get('enquiry_year')
    
    
    logger.debug('list_partnership_monthly_transaction: partner_merchant_key=%s', partner_merchant_key)
    logger.debug('list_partnership_monthly_transaction: enquiry_month_str=%s', enquiry_month_str)
    logger.debug('list_partnership_monthly_transaction: enquiry_year_str=%s', enquiry_year_str)
    
    month_int       = int(enquiry_month_str)
    year_int        = int(enquiry_year_str)
    
    enquiry_date    = date(year_int, month_int, 1) 
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    try:
        db_client = create_db_client(caller_info="list_reward_monthly_transaction")
        try:
            with db_client.context():
                merchant_acct               = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                partner_merchant_acct       = MerchantAcct.fetch(partner_merchant_key)
                
                
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        
        
        monthly_transaction_data     =  query_partnership_transaction_monthly_by_partner_merchant(merchant_acct, partner_merchant_acct, month_int, year_int)
        
        monthly_transaction_summary     = {}
        sum_of_point_amount             = 0
        sum_of_transaction_count        = 0
        
        for transaction_data in monthly_transaction_data:
            
            logger.debug('transaction_data=%s', transaction_data)
            
            transact_date                   = transaction_data.get('TransactDate')
            transaction_count               = transaction_data.get('TransactionCount')
            total_transact_point_amount     = transaction_data.get('SumTotalTransactPointAmount')
            
            sum_of_point_amount +=total_transact_point_amount
            sum_of_transaction_count+=transaction_count
            
            monthly_transaction_summary[transact_date] = {
                                                        'transaction_count': transaction_count, 
                                                        'total_transact_point_amount': total_transact_point_amount,
                                                        }
                        
            
                
        return render_template('/report/merchant/partnership/partnership_monthly_report/monthly_transaction_listing.html', 
                           page_title                   = gettext('Partnership Monthly Report'),
                           monthly_transaction_summary  = monthly_transaction_summary,
                           sum_of_point_amount          = sum_of_point_amount,
                           sum_of_transaction_count     = sum_of_transaction_count,
                           enquiry_date                 = enquiry_date,
                           partner_merchant_name        = partner_merchant_acct.brand_name,
                           currency_details             = get_merchant_configured_currency_details(),
                           
                           )
    
    except:
        logger.error('Fail to list reward monthly transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)           

