'''
Created on 7 Jan 2021

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
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexadmin.bigquery.transaction_query_executor import query_reward_monthly_by_outlet
from flask.json import jsonify
from trexmodel import program_conf
from trexlib.utils.string_util import str_to_bool, is_empty

merchant_rewarding_report_bp = Blueprint('merchant_rewarding_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/rewarding/')


logger = logging.getLogger('report')

'''
Blueprint settings here
'''
@merchant_rewarding_report_bp.context_processor
def merchant_rewarding_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_rewarding_report_bp.route('/reward-daily-report', methods=['GET'])
@login_required
def merchant_reward_daily_report(): 
    logger.debug('---merchant_reward_daily_report---')
    
    
    return render_template('/report/merchant/rewarding/reward_daily_report/reward_daily_report_enquiry.html', 
                           page_title               = gettext('Rewarding Daily Report'),
                           page_url                 = url_for('merchant_rewarding_report_bp.merchant_reward_daily_report'),
                           reward_daily_enquiry_url = url_for('merchant_rewarding_report_bp.list_reward_daily_transaction', page_no=1, limit=10),
                           )
    

@merchant_rewarding_report_bp.route('/reward-daily-report/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_reward_daily_transaction(limit, page_no): 
    logger.debug('---list_reward_daily_transaction---')
    
    logger.debug('page_no=%s', page_no)
    
    outlet_key                  = request.args.get('rewarding_outlet')
    enquiry_date_str            = request.args.get('enquiry_date')
    cursor                      = request.args.get('cursor')
    previous_cursor             = request.args.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    start                       = request.args.get('start')
    
    is_start_page               = str_to_bool(start)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    customer_transaction_list   = []
    next_cursor                 = None
    outlet_name                 = None
    
    logger.debug('list_reward_daily_transaction: outlet_key=%s', outlet_key)
    logger.debug('list_reward_daily_transaction: enquiry_date_str=%s', enquiry_date_str)
    logger.debug('list_reward_daily_transaction: cursor=%s', cursor)
    logger.debug('list_reward_daily_transaction: page_no_int=%d', page_no_int)
    logger.debug('list_reward_daily_transaction: limit_int=%d', limit_int)
    logger.debug('list_redemption_daily_transaction: is_start_page=%d', is_start_page)
    
    try:
        db_client = create_db_client(caller_info="list_reward_daily_transaction")
        try:
            with db_client.context():
                transact_outlet             = Outlet.fetch(outlet_key)
                outlet_name                 = transact_outlet.name
                enquiry_date                = datetime.strptime(enquiry_date_str, '%d/%m/%Y')
                
                logger.debug('list_reward_daily_transaction: enquiry_date=%s', enquiry_date)
                
                (result, next_cursor)       = CustomerTransaction.list_transaction_by_date(enquiry_date, including_reverted_transaction=False, transact_outlet=transact_outlet, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                total_count                 = CustomerTransaction.count_transaction_by_date(enquiry_date, including_reverted_transaction=False, transact_outlet=transact_outlet)
                
                for r in result:
                    customer_transaction_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_reward_daily_transaction: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  rewarding_outlet              = outlet_key,
                                  enquiry_date                  = enquiry_date_str,
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('/report/merchant/rewarding/reward_daily_report/daily_transaction_listing.html', 
                               customer_transaction_list    = customer_transaction_list,
                               end_point                    = 'merchant_rewarding_report_bp.list_reward_daily_transaction',
                               pager                        = pager,
                               pages                        = pages,
                               rewarding_outlet             = outlet_key,
                               enquiry_date                 = enquiry_date_str,
                               pagination_target_selector   = '#reward_daily_transaction_div',
                               outlet_name                  = outlet_name,
                               currency_details             = get_merchant_configured_currency_details(),
                               
                               )
    
    except:
        logger.error('Fail to list reward daily transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
    
@merchant_rewarding_report_bp.route('/reward-monthly-report', methods=['GET'])
@login_required
def merchant_reward_monthly_report(): 
    logger.debug('---merchant_reward_monthly_report---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_reward_monthly_report")
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
        
    return render_template('/report/merchant/rewarding/reward_monthly_report/reward_monthly_report_enquiry.html', 
                           page_title                   = gettext('Reward Monthly Report'),
                           page_url                     = url_for('merchant_rewarding_report_bp.merchant_reward_monthly_report'),
                           reward_monthly_enquiry_url   = url_for('merchant_rewarding_report_bp.list_reward_monthly_transaction'),
                           year_range_list              = year_range_list,
                           )
    

@merchant_rewarding_report_bp.route('/reward-monthly-report/query', methods=['GET'])
@login_required
def list_reward_monthly_transaction(): 
    logger.debug('---list_reward_monthly_transaction---')
    
    
    outlet_key                  = request.args.get('rewarding_outlet')
    enquiry_month_str           = request.args.get('enquiry_month')
    enquiry_year_str            = request.args.get('enquiry_year')
    
    
    logger.debug('list_reward_daily_transaction: outlet_key=%s', outlet_key)
    logger.debug('list_reward_daily_transaction: enquiry_month_str=%s', enquiry_month_str)
    logger.debug('list_reward_daily_transaction: enquiry_year_str=%s', enquiry_year_str)
    
    month_int       = int(enquiry_month_str)
    year_int        = int(enquiry_year_str)
    
    enquiry_date    = date(year_int, month_int, 1) 
    
    try:
        db_client = create_db_client(caller_info="list_reward_monthly_transaction")
        try:
            with db_client.context():
                rewarding_outlet    = Outlet.fetch(outlet_key)
                outlet_name         = rewarding_outlet.name
                
                
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        
        
        monthly_reward_data     =  query_reward_monthly_by_outlet(rewarding_outlet, month_int, year_int)
        
        monthly_reward_summary      = {}
        sum_of_reward_summary       = {}
        total_transact_amount       = 0
        
        for reward_data in monthly_reward_data:
            
            logger.debug('reward_data=%s', reward_data)
            
            rewarded_date           = reward_data.get('RewardedDate')
            transaction_id          = reward_data.get('TransactionId')
            reward_format           = reward_data.get('RewardFormat')
            voucher_key             = reward_data.get('RewardFormatKey')
            reward_amount           = reward_data.get('TotalRewardAmount')
            transact_amount         = reward_data.get('TransactAmount')
            
            date_reward_summary                 = monthly_reward_summary.get(rewarded_date, {'reward_details':{}})
            transact_amount_by_date             = date_reward_summary.get('transact_amount', 0)
            sale_amount_by_transaction_id       = date_reward_summary.get(transaction_id, 0)
            
            
            logger.debug('going to handle daily reward, start: ------------------')
            logger.debug('date_reward_summary=%s', date_reward_summary)
            logger.debug('transact_amount_by_date=%s', transact_amount_by_date)
            logger.debug('sale_amount_by_transaction_id=%s', sale_amount_by_transaction_id)
            logger.debug('total_transact_amount=%s', total_transact_amount)
            
            if sale_amount_by_transaction_id == 0:
                date_reward_summary[transaction_id] = transact_amount
                transact_amount_by_date +=transact_amount
                total_transact_amount   +=transact_amount
                date_reward_summary['transact_amount'] = transact_amount_by_date
            else:
                logger.debug('ignore because the transaction amount have been recorded')
            
            if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                date_voucher_summary =  date_reward_summary.get('reward_details').get('vouchers', {})
                
                voucher_amount_by_voucher_key = date_voucher_summary.get(voucher_key, 0)
                if voucher_amount_by_voucher_key==0:
                    date_voucher_summary[voucher_key] = reward_amount
                else:
                    date_voucher_summary[voucher_key] += reward_amount
                
                date_reward_summary['reward_details']['vouchers'] = date_voucher_summary
            else:
                
                reward_amount_by_format = date_reward_summary.get('reward_details').get(reward_format, 0)
                
                if reward_amount_by_format ==0:
                    date_reward_summary['reward_details'][reward_format] = reward_amount
                else:
                    date_reward_summary['reward_details'][reward_format] += reward_amount
            
            monthly_reward_summary[rewarded_date] = date_reward_summary
            
            if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                voucher_summary_from_sum = sum_of_reward_summary.get('vouchers', {})
                
                voucher_amount_by_voucher_key = voucher_summary_from_sum.get(voucher_key, 0)
                
                if voucher_amount_by_voucher_key==0:
                    voucher_summary_from_sum[voucher_key] = reward_amount
                else:
                    voucher_summary_from_sum[voucher_key] += reward_amount
                    
                sum_of_reward_summary['vouchers'] = voucher_summary_from_sum
            else:
                reward_amount_from_sum = sum_of_reward_summary.get(reward_format, 0)
                if reward_amount_from_sum==0:
                    reward_amount_from_sum = reward_amount
                else:
                    reward_amount_from_sum += reward_amount
                
                sum_of_reward_summary[reward_format] = reward_amount_from_sum
            
            
                
        monthly_reward_summary_final    = {}
        #monthly_transact_summary_final  = {}
        
        for d, s in monthly_reward_summary.items():
            monthly_reward_summary_final[datetime.strptime(d, '%Y-%m-%d').date()]   = s
        '''
        for d, s in monthly_transact_summary.items():
            monthly_transact_summary_final[datetime.strptime(d, '%Y-%m-%d').date()] = s
        '''
                
        logger.debug('monthly_reward_summary_final = %s', monthly_reward_summary_final)
        
        #return jsonify(monthly_reward_summary)
        return render_template('/report/merchant/rewarding/reward_monthly_report/monthly_rewarding_listing.html', 
                           page_title                   = gettext('Reward Monthly Report'),
                           monthly_reward_summary       = monthly_reward_summary_final,
                           sum_of_reward_summary        = sum_of_reward_summary,
                           total_transact_amount        = total_transact_amount,
                           enquiry_date                 = enquiry_date,
                           outlet_name                  = outlet_name,
                           currency_details             = get_merchant_configured_currency_details(),
                           
                           )
    
    except:
        logger.error('Fail to list reward monthly transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)           
