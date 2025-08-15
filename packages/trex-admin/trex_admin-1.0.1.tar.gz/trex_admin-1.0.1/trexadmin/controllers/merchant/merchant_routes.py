'''
Created on 10 Dec 2020

@author: jacklok
'''

from flask import Blueprint, render_template, abort
from trexadmin.libs.flask.decorator.security_decorators import login_required, account_activated
from trexadmin.menu.merchant import merchant_menu 
from trexadmin.libs.flask.utils.flask_helper import check_is_menu_accessable, get_loggedin_merchant_user_account, get_preferred_language,\
    is_merchant_user, was_once_logged_in, user_type
from flask_babel import gettext
from flask.helpers import url_for
import logging
import jinja2
import calendar
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.analytics_conf import MERCHANT_CUSTOMER_GROWTH_CHART_DATA_URL, MERCHANT_SALES_GROWTH_CHART_DATA_URL,\
    MERCHANT_CUSTOMER_COUNT_BY_DATE_RANGE_DATA_URL,\
    MERCHANT_TRANSACTION_COUNT_YEARLY_DATE_RANGE_DATA_URL,\
    MERCHANT_CUSTOMER_GENDER_BY_DATE_RANGE_DATA_URL,\
    MERCHANT_CUSTOMER_AGE_GROUP_BY_DATE_RANGE_DATA_URL,\
    MERCHANT_SALES_AMOUNT_BY_DATE_RANGE_DATA_URL
from datetime import datetime, timedelta
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.common.date_util import last_day_of_month
from datetime import date
from trexmodel.models.datastore.merchant_models import MerchantAcct
from werkzeug.utils import redirect
from trexlib.libs.flask_wtf.request_wrapper import request_values

merchant_bp = Blueprint('merchant_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant')

#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@merchant_bp.context_processor
def merchant_bp_inject_settings():
    return {
            
            }


@jinja2.contextfilter
@merchant_bp.app_template_filter()
def is_menu_accessable(context, menu_config):
    return check_is_menu_accessable(menu_config, 'merchant_bp')

@merchant_bp.route('/dashboard')
@account_activated
@login_required
def dashboard_page(): 
    
    return prepare_dashboard('merchant/dashboard/merchant_dashboard_index.html')

@merchant_bp.route('/guide')
def guide_page(): 
    
    return render_template(
                    'merchant/help/merchant_guide_page.html', 
                    page_title    = gettext('Guide'),
                    )             

    
@merchant_bp.route('/dashboard-content')
def dashboard_content(): 
    
    return prepare_dashboard('merchant/dashboard/merchant_dashboard.html', show_page_title=False, show_menu_config=False)                
    

@request_values
def prepare_dashboard(template_path, request_values, show_page_title=True, show_menu_config=True):
    
    try:
        logged_in_is_merchant_user  = is_merchant_user()
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        today                       = datetime.today()
        enquiry_date                = request_values.get('enquiry_date', today.strftime('%d-%m-%Y'))
        
        logger.debug('dashboard_page: enquiry_date=%s', enquiry_date)
        logger.debug('dashboard_page: logged_in_is_merchant_user=%s', logged_in_is_merchant_user)
    
        if logged_in_is_merchant_user:
            menu_config  = merchant_menu.menu_items
        else:
            menu_config  = []
            
        application_logo_url        = None
        
        if logged_in_merchant_user is None:
            abort(400)
        
        db_client                   = create_db_client(caller_info="dashboard_page")
        merchant_company_name       = None
        enquiry_date                = datetime.strptime(enquiry_date, '%d-%m-%Y')
        
        
        
        start_joined_year           = enquiry_date.year
        
            
        with db_client.context():
            
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        if merchant_acct:
            account_code            = merchant_acct.account_code
            merchant_key            = merchant_acct.key_in_str
            start_joined_year       = merchant_acct.plan_start_date.year
            merchant_company_name   = merchant_acct.company_name
            
            if merchant_acct.logo_public_url:
                application_logo_url    = merchant_acct.logo_public_url
                
    
            this_year   = enquiry_date.year
            year_range_list =  []
            
            for year in range(start_joined_year, this_year+1):
                year_range_list.append(year)
            
            sorted_year_range_list = sorted(year_range_list, reverse=True)
            year_range_list = sorted_year_range_list
                
            given_date                  = datetime.today().date()
            first_date_of_year          = date(given_date.year, 1, 1)
            
            first_date_of_month         = given_date - timedelta(days = int(given_date.strftime("%d"))-1)
            last_date_of_month          = last_day_of_month(given_date)
            
            merchant_plan_start_date    = merchant_acct.plan_start_date
            
            monthly_new_customer_count_chart_data_url   = MERCHANT_CUSTOMER_COUNT_BY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_month.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d')
            monthly_sales_amount_chart_data_url         = MERCHANT_SALES_AMOUNT_BY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_month.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d')
            monthly_transaction_amount_data_url         = MERCHANT_TRANSACTION_COUNT_YEARLY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_month.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d')
            
            
            logger.debug('dashboard_page: monthly_new_customer_count_chart_data_url=%s', monthly_new_customer_count_chart_data_url)
            logger.debug('dashboard_page: monthly_sales_amount_chart_data_url=%s', monthly_sales_amount_chart_data_url)
            logger.debug('dashboard_page: monthly_transaction_amount_data_url=%s', monthly_transaction_amount_data_url)
            
            return render_template(template_path, 
                                   page_title                       = gettext('Dashboard') if show_page_title else None,
                                   menu_config                      = menu_config if show_menu_config else None,
                                   #page_url                         = url_for('merchant_bp.dashboard_content') if show_page_title else None,
                                   application_logo_url             = application_logo_url,
                                   merchant_key                     = merchant_key,
                                   merchant_company_name            = merchant_company_name,
                                   
                                   year                             = enquiry_date.year,
                                   month                            = enquiry_date.month,
                                   enquiry_date                     = enquiry_date, 
                                   year_range_list                  = year_range_list,
                                   get_stat_details_url             = url_for('merchant_analytic_bp.get_merchant_stat_details'),
                                   
                                   #stat widget data url
                                   monthly_new_customer_count_chart_data_url    = monthly_new_customer_count_chart_data_url,
                                   monthly_sales_amount_chart_data_url          = monthly_sales_amount_chart_data_url,
                                   monthly_transaction_amount_data_url          = monthly_transaction_amount_data_url,
                                   
                                   monthly_new_customer_count_by_enquiry_date   = url_for('merchant_bp.new_customer_count_by_enquiry_date'),
                                   monthly_sales_amount_by_enquiry_date         = url_for('merchant_bp.sales_amount_by_enquiry_date'),
                                   monthly_transaction_amount_by_enquiry_date   = url_for('merchant_bp.transaction_amount_by_enquiry_date'),
                                   new_customer_growth_by_enquiry_year          = url_for('merchant_bp.new_customer_growth_by_enquiry_year'),
                                   
                                   #dashboard stat widget data url
                                   customer_growth_chart_data_url   = MERCHANT_CUSTOMER_GROWTH_CHART_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_year.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   customer_gender_data_url         = MERCHANT_CUSTOMER_GENDER_BY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+merchant_plan_start_date.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   customer_age_group_data_url      = MERCHANT_CUSTOMER_AGE_GROUP_BY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+merchant_plan_start_date.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   
                                   sales_growth_chart_data_url      = MERCHANT_SALES_GROWTH_CHART_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_month.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   sales_growth_chart_data_base_url = MERCHANT_SALES_GROWTH_CHART_DATA_URL+"?account_code="+account_code
                                   
                                   )
        else:
            _was_once_logged_in  = was_once_logged_in()
        
            
            if _was_once_logged_in:
                _user_type = user_type()
                
                logger.debug('_user_type=%s', _user_type)
                
                if _user_type == 'admin':
                    return redirect(url_for('admin_bp.dashboard_page'))
            else:
                return redirect(url_for('security_bp.merchant_signin_page'))
            
    except:
        logger.error('Failed due to %s', get_tracelog())
        
        abort(400)

@request_values
def stat_widget(template_path, request_values):
    try:
        logged_in_is_merchant_user      = is_merchant_user()
        today                           = datetime.today()
        enquiry_date                    = request_values.get('enquiry_date', today.strftime('%d-%m-%Y'))
        
        logger.debug('dashboard_page: enquiry_date=%s', enquiry_date)
    
        if logged_in_is_merchant_user:
            menu_config  = merchant_menu.menu_items
        else:
            menu_config  = []
            
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        
        if logged_in_merchant_user is None:
            abort(400)
        
        db_client                   = create_db_client(caller_info="dashboard_page")
        
        
            
        with db_client.context():
            
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        if merchant_acct:
            account_code    = merchant_acct.account_code
            
            if merchant_acct.logo_public_url:
                start_joined_year       = merchant_acct.plan_start_date.year
    
            today       = datetime.today()
            this_year   = today.year
            year_range_list =  []
            
            for year in range(start_joined_year, this_year+1):
                year_range_list.append(year)
            
            sorted_year_range_list = sorted(year_range_list, reverse=True)
            year_range_list = sorted_year_range_list
                
            given_date                  = datetime.today().date()
            first_date_of_year          = date(given_date.year, 1, 1)
            
            first_date_of_month         = given_date - timedelta(days = int(given_date.strftime("%d"))-1)
            last_date_of_month          = last_day_of_month(given_date)
            
            merchant_plan_start_date    = merchant_acct.plan_start_date
            
            now = datetime.now()
            
        return render_template(template_path, 
                                   year                             = now.year,
                                   month                            = now.month,
                                   year_range_list                  = year_range_list,
                                   
                                   customer_growth_chart_data_url   = MERCHANT_CUSTOMER_GROWTH_CHART_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_year.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),  
                                   customer_gender_data_url         = MERCHANT_CUSTOMER_GENDER_BY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+merchant_plan_start_date.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   customer_age_group_data_url      = MERCHANT_CUSTOMER_AGE_GROUP_BY_DATE_RANGE_DATA_URL+"?account_code="+account_code+'&date_range_from='+merchant_plan_start_date.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   
                                   sales_growth_chart_data_url      = MERCHANT_SALES_GROWTH_CHART_DATA_URL+"?account_code="+account_code+'&date_range_from='+first_date_of_month.strftime('%Y%m%d')+'&date_range_to='+last_date_of_month.strftime('%Y%m%d'),
                                   sales_growth_chart_data_base_url = MERCHANT_SALES_GROWTH_CHART_DATA_URL+"?account_code="+account_code,
                                   show_full                        = True,    
                                   )
     
    except:
        logger.error('Failed due to %s', get_tracelog())
        
        abort(400)
        
@request_values
def redirect_stat_widget_by_enquiry_month_year(widget_base_url, request_values):
    try:
        today                           = datetime.today()
        enquiry_year                    = request_values.get('year', today.strftime('%Y'))
        enquiry_month                   = request_values.get('month', today.strftime('%m'))
        
        logger.debug('enquiry_year=%s', enquiry_year)
        logger.debug('enquiry_month=%s', enquiry_month)
    
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        
        if logged_in_merchant_user is None:
            abort(400)
        
        db_client                   = create_db_client(caller_info="redirect_stat_widget_by_enquiry_month_year")
        
        with db_client.context():
            
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        if merchant_acct:
            account_code    = merchant_acct.account_code
            
            date_range_from = '{year}{month}01'.format(year=enquiry_year, month=str(enquiry_month).zfill(2))
            date_range_from_date = datetime.strptime(date_range_from, '%Y%m%d')
            
            last_day = calendar.monthrange(date_range_from_date.year, date_range_from_date.month)[1]
            
            date_range_to   = date_range_from_date.replace(day=last_day).strftime('%Y%m%d')
        
        target_url = widget_base_url +"?account_code="+account_code+'&date_range_from='+date_range_from+'&date_range_to='+date_range_to
        logger.debug('target_url=%s', target_url)
        
        return redirect(target_url)
     
    except:
        logger.error('Failed due to %s', get_tracelog())
        
        abort(400)
        
@request_values
def redirect_stat_widget_by_enquiry_year(widget_base_url, request_values):
    try:
        today                           = datetime.today()
        enquiry_year                    = request_values.get('year', today.strftime('%Y'))
        
        logger.debug('enquiry_year=%s', enquiry_year)
        
        logged_in_merchant_user     = get_loggedin_merchant_user_account()
        
        if logged_in_merchant_user is None:
            abort(400)
        
        db_client                   = create_db_client(caller_info="redirect_stat_widget_by_enquiry_month_year")
        
        with db_client.context():
            
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        if merchant_acct:
            account_code    = merchant_acct.account_code
            
            date_range_from = '{year}0101'.format(year=enquiry_year)
            date_range_to= '{year}1231'.format(year=enquiry_year)
                    
        target_url = widget_base_url +"?account_code="+account_code+'&date_range_from='+date_range_from+'&date_range_to='+date_range_to
        logger.debug('target_url=%s', target_url)
        
        return redirect(target_url)
     
    except:
        logger.error('Failed due to %s', get_tracelog())
        
        abort(400)
            
@merchant_bp.route('/gender-group-stat')
@account_activated
@login_required
def gender_group_stat():
    
    return stat_widget('merchant/dashboard/merchant_gender_group_stat_widget.html') 

@merchant_bp.route('/age-group-stat')
@account_activated
@login_required
def age_group_stat():
    
    return stat_widget('merchant/dashboard/merchant_age_group_stat_widget.html') 


@merchant_bp.route('/monthly-new-customer-count-by-enquiry-date')
@account_activated
@login_required
def new_customer_count_by_enquiry_date():
    return redirect_stat_widget_by_enquiry_month_year(MERCHANT_CUSTOMER_COUNT_BY_DATE_RANGE_DATA_URL)

@merchant_bp.route('/monthly-new-customer-growth-by-enquiry-year')
@account_activated
@login_required
def new_customer_growth_by_enquiry_year():
    return redirect_stat_widget_by_enquiry_year(MERCHANT_CUSTOMER_GROWTH_CHART_DATA_URL)

@merchant_bp.route('/monthly-sales-amount-by-enquiry-date')
@account_activated
@login_required
def sales_amount_by_enquiry_date():
    return redirect_stat_widget_by_enquiry_month_year(MERCHANT_SALES_AMOUNT_BY_DATE_RANGE_DATA_URL) 

@merchant_bp.route('/monthly-transaction-amount-by-enquiry-date')
@account_activated
@login_required
def transaction_amount_by_enquiry_date():
    return redirect_stat_widget_by_enquiry_month_year(MERCHANT_TRANSACTION_COUNT_YEARLY_DATE_RANGE_DATA_URL) 


#@merchant_bp.route('/<merchant_account_key>/logo-url')
#def merchant_logo_url(merchant_account_key):
    
    