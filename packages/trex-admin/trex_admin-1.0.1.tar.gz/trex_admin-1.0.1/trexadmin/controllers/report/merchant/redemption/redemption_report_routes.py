'''
Created on 7 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask.helpers import url_for
from flask_babel import gettext
from datetime import datetime, date
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexadmin.bigquery.transaction_query_executor import query_redemption_monthly_by_outlet
from trexmodel import program_conf
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexlib.utils.string_util import str_to_bool

merchant_redemption_report_bp = Blueprint('merchant_redemption_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/redemption/')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@merchant_redemption_report_bp.context_processor
def merchant_rewarding_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_redemption_report_bp.route('/redemption-daily-report', methods=['GET'])
@login_required
def merchant_redemption_daily_report(): 
    logger.debug('---merchant_redemption_daily_report---')
    
    
    return render_template('/report/merchant/redemption/redemption_daily_report/redemption_daily_report_enquiry.html', 
                           page_title                   = gettext('Redemption Daily Report'),
                           page_url                     = url_for('merchant_redemption_report_bp.merchant_redemption_daily_report'),
                           redemption_daily_enquiry_url = url_for('merchant_redemption_report_bp.list_redemption_daily_transaction', page_no=1, limit=10),
                           
                           )
    

@merchant_redemption_report_bp.route('/redemption-daily-report/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_redemption_daily_transaction(limit, page_no): 
    logger.debug('---list_redemption_daily_transaction---')
    
    logger.debug('page_no=%s', page_no)
    
    outlet_key                  = request.args.get('redeem_outlet')
    enquiry_date_str            = request.args.get('enquiry_date')
    cursor                      = request.args.get('cursor')
    previous_cursor             = request.args.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    start                       = request.args.get('start')
    
    is_start_page               = str_to_bool(start)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    customer_redemption_list    = []
    next_cursor                 = None
    outlet_name                 = None
    
    logger.debug('list_redemption_daily_transaction: outlet_key=%s', outlet_key)
    logger.debug('list_redemption_daily_transaction: enquiry_date_str=%s', enquiry_date_str)
    logger.debug('list_redemption_daily_transaction: cursor=%s', cursor)
    logger.debug('list_redemption_daily_transaction: page_no_int=%d', page_no_int)
    logger.debug('list_redemption_daily_transaction: limit_int=%d', limit_int)
    logger.debug('list_redemption_daily_transaction: is_start_page=%d', is_start_page)
    
    try:
        db_client = create_db_client(caller_info="list_customer_transaction")
        try:
            with db_client.context():
                redeemed_outlet             = Outlet.fetch(outlet_key)
                outlet_name                 = redeemed_outlet.name
                enquiry_date                = datetime.strptime(enquiry_date_str, '%d/%m/%Y')
                
                logger.debug('list_redemption_daily_transaction: enquiry_date=%s', enquiry_date)
                
                (result, next_cursor)       = CustomerRedemption.list_redemption_by_date(enquiry_date, including_reverted_transaction=False, redeemed_outlet=redeemed_outlet, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                total_count                 = CustomerRedemption.count_redemption_by_date(enquiry_date, including_reverted_transaction=False, redeemed_outlet=redeemed_outlet)
                
                for r in result:
                    customer_redemption_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_redemption_daily_transaction: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  redeem_outlet                 = outlet_key,
                                  enquiry_date                  = enquiry_date_str,
                                  )
        pages       = pager.get_pages()
        
        target_template = '/report/merchant/redemption/redemption_daily_report/daily_redemption_listing.html'
        if is_start_page==False:
            target_template = '/report/merchant/redemption/redemption_daily_report/daily_redemption_listing_content.html'
        
        
        return render_template(target_template, 
                               customer_redemption_list     = customer_redemption_list,
                               end_point                    = 'merchant_redemption_report_bp.list_redemption_daily_transaction',
                               pager                        = pager,
                               pages                        = pages,
                               rewarding_outlet             = outlet_key,
                               enquiry_date                 = enquiry_date_str,
                               pagination_target_selector   = '#redemption_daily_transaction_div',
                               outlet_name                  = outlet_name,
                               )
    
    except:
        logger.error('Fail to list reward daily transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
    
@merchant_redemption_report_bp.route('/reward-monthly-report', methods=['GET'])
@login_required
def merchant_redemption_monthly_report(): 
    logger.debug('---merchant_redemption_monthly_report---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_redemption_monthly_report")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        start_joined_year       = merchant_acct.plan_start_date.year
    
    today       = datetime.today()
    this_year   = today.year
    year_range_list =  []
    for year in range(start_joined_year, this_year+1):
        year_range_list.append(year)
    
    sorted_year_range_list = sorted(year_range_list, reverse=True)
    year_range_list = sorted_year_range_list
        
    return render_template('/report/merchant/redemption/redemption_monthly_report/redemption_monthly_report_enquiry.html', 
                           page_title                   = gettext('Redemption Monthly Report'),
                           page_url                     = url_for('merchant_redemption_report_bp.merchant_redemption_monthly_report'),
                           reward_monthly_enquiry_url   = url_for('merchant_redemption_report_bp.list_redemption_monthly_transaction'),
                           year_range_list              = year_range_list,
                           )
    

@merchant_redemption_report_bp.route('/redemption-monthly-report/query', methods=['GET'])
@login_required
def list_redemption_monthly_transaction(): 
    logger.debug('---list_redemption_monthly_transaction---')
    
    
    outlet_key                  = request.args.get('redeem_outlet')
    enquiry_month_str           = request.args.get('enquiry_month')
    enquiry_year_str            = request.args.get('enquiry_year')
    
    
    logger.debug('list_redemption_monthly_transaction: outlet_key=%s', outlet_key)
    logger.debug('list_redemption_monthly_transaction: enquiry_month_str=%s', enquiry_month_str)
    logger.debug('list_redemption_monthly_transaction: enquiry_year_str=%s', enquiry_year_str)
    
    month_int       = int(enquiry_month_str)
    year_int        = int(enquiry_year_str)
    
    enquiry_date    = date(year_int, month_int, 1) 
    
    try:
        db_client = create_db_client(caller_info="list_redemption_monthly_transaction")
        try:
            with db_client.context():
                redeem_outlet       = Outlet.fetch(outlet_key)
                outlet_name         = redeem_outlet.name
                
                
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        
        
        monthly_redemption_data             =  query_redemption_monthly_by_outlet(redeem_outlet, month_int, year_int)
        
        monthly_redemption_summary          = {}
        sum_of_redemption_summary           = {}
        
        for redemption_data in monthly_redemption_data:
            rewdeemed_date       = redemption_data.get('redeemedDate')
            reward_format       = redemption_data.get('rewardFormat')
            sum_redeemed_amount   = redemption_data.get('sumRedeemedAmount')
            voucher_key         = redemption_data.get('voucherKey')
            
            daily_redemption_summary      = monthly_redemption_summary.get(rewdeemed_date)
            
            if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                if sum_of_redemption_summary.get('vouchers'):
                    voucher_summary = sum_of_redemption_summary['vouchers']
                    
                    voucher_sum = voucher_summary.get(voucher_key)
                    if voucher_sum:
                        voucher_summary[voucher_key] += int(sum_redeemed_amount)
                    else:
                        voucher_summary[voucher_key] = int(sum_redeemed_amount)
                else:
                    voucher_summary = {
                                        voucher_key : int(sum_redeemed_amount)
                                        }
                
                sum_of_redemption_summary['vouchers'] = voucher_summary 
            else:
                
                if sum_of_redemption_summary.get(reward_format):
                    sum_of_redemption_summary[reward_format] += sum_redeemed_amount
                else:
                    sum_of_redemption_summary[reward_format] = sum_redeemed_amount
                
            if daily_redemption_summary:
                if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                    if daily_redemption_summary.get('vouchers'):
                        voucher_summary = daily_redemption_summary['vouchers']
                        
                        if voucher_summary:
                            voucher_sum = voucher_summary.get(voucher_key)
                            if voucher_sum:
                                voucher_summary[voucher_key] += int(sum_redeemed_amount)
                            else:
                                voucher_summary[voucher_key] = int(sum_redeemed_amount)
                        else:
                            voucher_summary[voucher_key] = int(sum_redeemed_amount)
                            
                        
                    else:
                        voucher_summary = {
                                            voucher_key : int(sum_redeemed_amount)
                                            }
                        daily_redemption_summary['vouchers'] = voucher_summary
                        
                       
                        
                    
                else:
                    if daily_redemption_summary.get(reward_format):
                        daily_redemption_summary[reward_format] += sum_redeemed_amount
                    else:
                        daily_redemption_summary[reward_format] = sum_redeemed_amount
                        
                    
            else:
                if reward_format==program_conf.REWARD_FORMAT_VOUCHER:
                    sum_redeemed_amount = int(sum_redeemed_amount)
                    daily_redemption_summary = {
                                                    'vouchers'          : {
                                                                            voucher_key       : sum_redeemed_amount
                                                                        }
                                                    }
                else:
                    daily_redemption_summary = {
                                                reward_format     : sum_redeemed_amount,
                                                
                                                }
                    
                monthly_redemption_summary[rewdeemed_date] = daily_redemption_summary
        
        monthly_redemption_summary_final    = {}
        
        for d, s in monthly_redemption_summary.items():
            monthly_redemption_summary_final[datetime.strptime(d, '%Y-%m-%d').date()] = s
        
                
        logger.debug('monthly_redemption_data = %s', monthly_redemption_data)
        
        
        
        return render_template('/report/merchant/redemption/redemption_monthly_report/monthly_redemption_listing.html', 
                           page_title                   = gettext('Redemption Monthly Report'),
                           monthly_redemption_summary   = monthly_redemption_summary_final,
                           enquiry_date                 = enquiry_date,
                           outlet_name                  = outlet_name,
                           sum_of_redemption_summary    = sum_of_redemption_summary,
                           
                           )
        
    
    except:
        logger.error('Fail to list redemption monthly transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)           
