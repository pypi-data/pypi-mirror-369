'''
Created on 22 Jul 2025

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
from trexlib.utils.string_util import str_to_bool, is_empty, is_not_empty
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexmodel.models.datastore.partnership_models import PartnershipRewardTransaction
from trexmodel.models.datastore.rating_models import TransactionRating,\
    OutletRatingResult
from trexadmin.libs.jinja.rating_filters import restaurant_rating_type_label_filter,\
    retail_rating_type_label_filter
from trexmodel.models.datastore.user_models import User

merchant_rating_report_bp = Blueprint('merchant_rating_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/merchant/rating/')


#logger = logging.getLogger('report')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@merchant_rating_report_bp.context_processor
def merchant_rating_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name                    = "merchant",
                reviewed_transaction_user_details_url   = url_for('merchant_rating_report_bp.read_reviewed_transaction_user_details'),
                )

@merchant_rating_report_bp.app_template_filter()
def restaurant_rating_type_label(code):
    return restaurant_rating_type_label_filter(code)

@merchant_rating_report_bp.app_template_filter()
def retail_rating_type_label(code):
    return retail_rating_type_label_filter(code)

def rating_result_with_label(rating_result, industry):
    rating_with_label_dict = {}
    if industry=='fb':
        for rating_type, rating_value in rating_result.items():
            rating_with_label_dict[restaurant_rating_type_label_filter(rating_type)] = f"{rating_value:.1f}"
            
    elif industry=='rt':
        for rating_type, rating_value in rating_result.items():
            rating_with_label_dict[retail_rating_type_label_filter(rating_type)] = f"{rating_value:.1f}"
    
    
    return rating_with_label_dict

@merchant_rating_report_bp.route('/outlet-rating-report', methods=['GET'])
@login_required
def merchant_outlet_daily_rating_report(): 
    logger.debug('---merchant_outlet_rating_report---')
    
    
    return render_template('/report/merchant/rating/outlet_daily_report/rating_daily_report_enquiry.html', 
                           page_title                       = gettext('Outlet Daily Report'),
                           page_url                         = url_for('merchant_rating_report_bp.merchant_outlet_daily_rating_report'),
                           outlet_rating_daily_enquiry_url  = url_for('merchant_rating_report_bp.list_outlet_daily_rating_transaction', page_no=1, limit=10),
                           )
    

@merchant_rating_report_bp.route('/reviewed-user-details', methods=['GET'])
@login_required
@request_values
def read_reviewed_transaction_user_details(request_values): 
    logger.debug('---read_reviewed_transaction_user_details---')
    user_acct_key = request_values.get('user_acct_key')
    if is_not_empty(user_acct_key):
        try:
            db_client = create_db_client(caller_info="list_outlet_daily_rating_transaction")
            
            with db_client.context():
                user_acct = User.fetch(user_acct_key)
            
            if user_acct:
                user_acct = user_acct.to_dict(
                                    dict_properties=[
                                                    'name','email','mobile_phone', 'gender', 'birth_date', 
                                                    'reference_code', 
                                                    'created_datetime','address',
                                                    ]
                        )
                
                return render_template('/report/merchant/rating/outlet_daily_report/user_acct_details.html', 
                               user_acct    = user_acct,
                               )
            else:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
        except:
            logger.error('Fail to list partnership daily transaction due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
        
        
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@merchant_rating_report_bp.route('/partnership-daily-report/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_outlet_daily_rating_transaction(request_values, limit, page_no): 
    logger.debug('---list_outlet_daily_rating_transaction---')
    
    logger.debug('request_values=%s', request_values)
    logger.debug('page_no=%s', page_no)
    
    outlet_key                  = request_values.get('outlet_key')
    enquiry_date_str            = request_values.get('enquiry_date')
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    start                       = request_values.get('start')
    
    is_start_page               = str_to_bool(start)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    transaction_rating_list     = []
    next_cursor                 = None
    
    logger.debug('list_outlet_daily_rating_transaction: outlet_key=%s', outlet_key)
    logger.debug('list_outlet_daily_rating_transaction: enquiry_date_str=%s', enquiry_date_str)
    logger.debug('list_outlet_daily_rating_transaction: cursor=%s', cursor)
    logger.debug('list_outlet_daily_rating_transaction: page_no_int=%d', page_no_int)
    logger.debug('list_outlet_daily_rating_transaction: limit_int=%d', limit_int)
    logger.debug('list_outlet_daily_rating_transaction: is_start_page=%d', is_start_page)
    
    try:
        db_client = create_db_client(caller_info="list_outlet_daily_rating_transaction")
        try:
            with db_client.context():
                outlet                      = Outlet.fetch(outlet_key)
                
                enquiry_date                = datetime.strptime(enquiry_date_str, '%d/%m/%Y')
                
                logger.debug('list_outlet_daily_rating_transaction: enquiry_date=%s', enquiry_date)
                
                (result, next_cursor)       = TransactionRating.list_transaction_by_date(enquiry_date, outlet=outlet, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                
                for r in result:
                    rating_result = rating_result_with_label(r.rating_result, r.industry)
                    transaction_rating_dict = r.to_dict()
                    transaction_rating_dict['rating_result'] = rating_result
                    transaction_rating_dict['user_acct_key'] = r.user_acct_key
                    transaction_rating_list.append(transaction_rating_dict)
                    
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_outlet_daily_rating_transaction: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor           = next_cursor, 
                                  previous_cursor       = previous_cursor, 
                                  current_cursor        = cursor,
                                  outlet_key            = outlet_key,
                                  enquiry_date          = enquiry_date_str,
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('/report/merchant/rating/outlet_daily_report/daily_transaction_listing.html', 
                               transaction_rating_list                  = transaction_rating_list,
                               end_point                                = 'merchant_rating_report_bp.list_outlet_daily_rating_transaction',
                               pager                                    = pager,
                               pages                                    = pages,
                               enquiry_date                             = enquiry_date_str,
                               pagination_target_selector               = '#outlet_rating_daily_transaction_div',
                               outlet_name                              = outlet.name,
                               currency_details                         = get_merchant_configured_currency_details(),
                               
                               )
    
    except:
        logger.error('Fail to list partnership daily transaction due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   

@merchant_rating_report_bp.route('/all-outlet-rating-report', methods=['GET'])
@login_required
def merchant_all_outlet_rating_result_report(): 
    logger.debug('---merchant_all_outlet_rating_result_report---')
    
    
    return render_template('/report/merchant/rating/outlet_rating/all_outlet_rating_result_report_enquiry.html', 
                           page_title                               = gettext('All Outlet Rating Result Report'),
                           page_url                                 = url_for('merchant_rating_report_bp.merchant_all_outlet_rating_result_report'),
                           all_outlet_rating_result_enquiry_url     = url_for('merchant_rating_report_bp.merchant_generate_all_outlet_rating_report'),
                           )

@merchant_rating_report_bp.route('/generate-all-outlet-rating-report', methods=['GET'])
@login_required
def merchant_generate_all_outlet_rating_report(): 
    logger.debug('---merchant_generate_all_outlet_rating_report---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="merchant_generate_all_outlet_rating_report")
    all_outlet_rating_result_list = []
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result              = OutletRatingResult.list_by_merchant_acct(merchant_acct)
        
        for r in result:
            outlet_rating_result_with_label = rating_result_with_label(r.rating_result, merchant_acct.industry)
            all_outlet_rating_result_list.append({
                                                'outlet_key'        : r.outlet_key,
                                                'rating_result'     : outlet_rating_result_with_label,
                                                'modified_datetime' : r.modified_datetime,
                                                })
    
        
    return render_template('/report/merchant/rating/outlet_rating/all_outlet_rating_result_report.html', 
                           page_title                       = gettext('All Outlet Rating Result Report'),
                           page_url                         = url_for('merchant_rating_report_bp.merchant_generate_all_outlet_rating_report'),
                           all_outlet_rating_result_list    = all_outlet_rating_result_list,
                           enquiry_date                     = datetime.now(),
                           )
    

 
