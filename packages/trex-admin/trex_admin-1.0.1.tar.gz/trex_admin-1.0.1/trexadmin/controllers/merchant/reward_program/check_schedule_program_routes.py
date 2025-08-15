'''
Created on 15 Sep 2021

@author: jacklok
'''

from flask import Blueprint
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.flask.decorator.security_decorators import login_required,\
    service_header_authenticated
from trexlib.utils.log_util import get_tracelog
import logging
import trexmodel.program_conf as program_conf
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.program_models import MerchantScheduleProgram
from datetime import datetime, timedelta, date
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership
from trexmodel.models.datastore.helper.reward_transaction_helper import giveaway_birthday_reward_to_customer,\
    giveaway_membership_reward_to_customer
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.common.date_util import last_day_of_month
from trexmodel.models.datastore.membership_models import MerchantMembership
from dateutil.relativedelta import relativedelta
from trexlib.libs.flask_wtf.request_wrapper import request_values,\
    request_headers
import json
from trexlib.utils.google.cloud_tasks_util import create_task
from trexconf.conf import SYSTEM_TASK_SERVICE_CREDENTIAL_PATH,\
    SYSTEM_TASK_GCLOUD_PROJECT_ID, SYSTEM_TASK_GCLOUD_LOCATION,\
    SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL, SERVICE_HEADER_AUTHENTICATED_TOKEN
from trexconf import conf
from flask.json import jsonify
from trexadmin.conf import SERVICE_HEADER_AUTHENTICATED_PARAM

check_schedule_program_bp = Blueprint('check_schedule_program_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/reward-program/check-schedule-program/')


logger = logging.getLogger('target_debug')

SCHEDULE_CHECK_PAGINATION_SIZE = 200

'''
Blueprint settings here
'''
@check_schedule_program_bp.context_processor
def check_schedule_program_inject_settings():
    
    return dict(
                )

def filter_schedule_program(schedule_program_list):
    program_configuration_list  = []
    now                         = datetime.utcnow()
    today                       = now.today().date()
    
    for schedule_program in schedule_program_list:
        
        if today<=schedule_program.end_date and today>=schedule_program.start_date:
            program_configuration = schedule_program.program_configuration
            
            program_start_date  = datetime.strptime(program_configuration.get('start_date'), '%d-%m-%Y').date()
            program_end_date    = datetime.strptime(program_configuration.get('end_date'), '%d-%m-%Y').date()
            
            is_program_still_valid = today>=program_start_date and today<=program_end_date
            
            if is_program_still_valid:
                program_configuration_list.append(schedule_program.program_configuration)
                
    return program_configuration_list

def filter_birthday_program(schedule_program_list):
    program_configuration_list = filter_schedule_program(schedule_program_list)
    result = []
    for program_configuration in program_configuration_list:
            
        reward_base         = program_configuration.get('reward_base')
        logger.debug('reward_base=%s', reward_base)
        if reward_base == program_conf.REWARD_BASE_ON_BIRTHDAY:
            result.append(program_configuration)
            
    return result
    

def check_schedule_program(schedule_program_list):
    program_configuration_list  = filter_schedule_program(schedule_program_list)
            
    logger.info('program_configuration_list=%s', program_configuration_list)
    
    if program_configuration_list:

        for program_configuration in program_configuration_list:
            
            execute_merchant_schedule_program_reward(program_configuration)
                

@request_headers
def execute_merchant_schedule_program_reward(program_configuration, request_headers):
    logger.debug('request_headers=%s', request_headers)
    reward_base         = program_configuration.get('reward_base')
    headers = {
                SERVICE_HEADER_AUTHENTICATED_PARAM: request_headers.get(SERVICE_HEADER_AUTHENTICATED_PARAM, SERVICE_HEADER_AUTHENTICATED_TOKEN)
            }  
    logger.debug('-----------------------------------------------')
    logger.debug('headers=%s', headers)
    logger.debug('reward_base=%s', reward_base)
        
    if reward_base == program_conf.REWARD_BASE_ON_BIRTHDAY:
        #giveaway_birthday_reward_to_all_customer(program_configuration, today)
        task_url = '/merchant/reward-program/check-schedule-program/birthday-reward-program'
        task_url = '%s%s' % (conf.SYSTEM_BASE_URL, task_url)
        
        queue_name = 'schedule-birthday'
        payload = {
                    'program_configuration': json.dumps(program_configuration)
                    }
        create_task(task_url, queue_name, payload=payload, 
                in_seconds      = 1, 
                http_method     = 'POST',
                credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                location        = SYSTEM_TASK_GCLOUD_LOCATION,
                service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL,
                headers         = headers,
                )
    
    elif reward_base == program_conf.REWARD_BASE_ON_GIVEAWAY:    
        #giveaway_reward_schedule_program(program_configuration, today)
        task_url = '/merchant/reward-program/check-schedule-program/giveaway-reward-program'
        program_settings            = program_configuration.get('program_settings', {})
        giveaway_system_settings    = program_settings.get('giveaway_system_settings', {})
        giveaway_memberships        = giveaway_system_settings.get('giveaway_memberships', {})
        
        logger.debug('program_settings=%s', program_settings)
        logger.debug('giveaway_memberships=%s', giveaway_memberships)
        
        if is_not_empty(giveaway_memberships):
            task_url = '/merchant/reward-program/check-schedule-program/giveaway-membership-reward-program'
            logger.debug('---> going to giveaway for membership')
        
        task_url = '%s%s' % (conf.SYSTEM_BASE_URL, task_url)
        queue_name = 'schedule-giveaway'
        payload = {
                    'program_configuration': json.dumps(program_configuration)
                    }
        
        logger.info('task_url=%s', task_url)
        logger.info('queue_name=%s', queue_name)
        logger.info('payload=%s', payload)
        
        create_task(task_url, queue_name, payload=payload, 
                in_seconds      = 1, 
                http_method     = 'POST',
                credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                location        = SYSTEM_TASK_GCLOUD_LOCATION,
                service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL,
                headers         = headers,
                )
                  

def giveaway_membership_reward_program(program_configuration, schedule_date):            
    program_settings            = program_configuration.get('program_settings')
    giveaway_system_settings    = program_settings.get('giveaway_system_settings')
    
    logger.debug('program_settings=%s', program_settings)
    logger.debug('giveaway_system_settings=%s', giveaway_system_settings)
        
    if is_not_empty(giveaway_system_settings):
        giveaway_system_condition = giveaway_system_settings.get('giveaway_system_condition')
        if giveaway_system_condition == program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR:
            #going to giveaway for membership year reward
            logger.info('going to giveaway reward based on membership year')
            full_one_year_date          = schedule_date - relativedelta(days=1, years=1)
            
            logger.debug('full_one_year_date=%s', full_one_year_date)
            
            giveaway_membership_reward_to_all_customer(program_configuration, full_one_year_date)
        
def giveaway_birthday_reward_program(program_configuration, schedule_date):            
    program_settings            = program_configuration.get('program_settings')
    giveaway_system_settings    = program_settings.get('giveaway_system_settings')
    
    logger.debug('program_settings=%s', program_settings)
    logger.debug('giveaway_system_settings=%s', giveaway_system_settings)
        
    if is_not_empty(giveaway_system_settings):
        giveaway_system_condition = giveaway_system_settings.get('giveaway_system_condition')
        logger.debug('giveaway_system_condition=%s', giveaway_system_condition)
        
        if giveaway_system_condition == program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR:
            #going to giveaway for membership year reward
            logger.info('going to giveaway reward based on membership year')
            full_one_year_date          = schedule_date - relativedelta(days=1, years=1)
            
            logger.debug('full_one_year_date=%s', full_one_year_date)
            
            giveaway_membership_reward_to_all_customer(program_configuration, full_one_year_date)
    
    
@check_schedule_program_bp.route('/daily', methods=['GET'])
#@service_header_authenticated
def check_daily_schedule_program():
    db_client = create_db_client(caller_info="check_daily_schedule_program")
    try:
        with db_client.context():
            schedule_program_list = MerchantScheduleProgram.list_daily_schedule_program()
            
            logger.info('schedule_program_list=%s', schedule_program_list)
        
            if schedule_program_list:
                check_schedule_program(schedule_program_list)
    except:
        logger.error('Fail to check daily schedule program due to %s', get_tracelog())
        
    return 'Trigger checking'

@check_schedule_program_bp.route('/daily/show', methods=['GET'])
def show_daily_schedule_program():
    db_client = create_db_client(caller_info="show_daily_schedule_program")
    result = []
    try:
        with db_client.context():
            schedule_program_list = MerchantScheduleProgram.list_daily_schedule_program()
            
            logger.info('schedule_program_list=%s', schedule_program_list)
        
            if schedule_program_list:
                for program in schedule_program_list:
                    result.append(program.to_dict())
                    
    except:
        logger.error('Fail to check daily schedule program due to %s', get_tracelog())
        
    return jsonify({
                'programs': result,
                }
            )
    
@check_schedule_program_bp.route('/daily/birthday-program/show', methods=['GET'])
def show_birthday_schedule_program():
    db_client = create_db_client(caller_info="show_birthday_schedule_program")
    result = []
    try:
        with db_client.context():
            schedule_program_list = MerchantScheduleProgram.list_daily_schedule_program()
            
            logger.info('schedule_program_list=%s', schedule_program_list)
        
            if schedule_program_list:
                birthday_program_configuration_list = filter_birthday_program(schedule_program_list)
                for program in birthday_program_configuration_list:
                    result.append(program)
                    
    except:
        logger.error('Fail to check daily schedule program due to %s', get_tracelog())
        
    return jsonify({
                'programs': result,
                'count': len(result),
                }
            )    

@check_schedule_program_bp.route('/birthday-reward-program', methods=['POST'])
#@service_header_authenticated
@request_values
def execute_birthday_reward_program(request_values):
    logger.debug('--execute_birthday_reward_program--')
    program_configuration_in_str = request_values.get('program_configuration')
    
    logger.debug('program_configuration_in_str=%s', program_configuration_in_str)
    
    if program_configuration_in_str:
        program_configuration = json.loads(program_configuration_in_str)
        now                         = datetime.utcnow()
        #today                       = now.date()
        
        logger.debug('program_configuration=%s', program_configuration)
        
        db_client = create_db_client(caller_info="execute_birthday_reward_program")
        try:
            with db_client.context():
                giveaway_birthday_reward_to_all_customer(program_configuration, now)
                
        except:
            logger.error('Fail to execute scheduled birthday reward program due to %s', get_tracelog())
            
    return 'triggered execute_birthday_reward_program'
    
@check_schedule_program_bp.route('/giveaway-reward-program', methods=['POST'])
#@service_header_authenticated
@request_values
def execute_giveaway_reward_program(request_values):
    program_configuration_in_str = request_values.get('program_configuration')
    if program_configuration_in_str:
        program_configuration = json.loads(program_configuration_in_str)
        now                         = datetime.utcnow()
        today                       = now.date() 
        db_client = create_db_client(caller_info="execute_giveaway_reward_program")
        try:
            with db_client.context():
                #TODO
                #giveaway_birthday_reward_to_all_customer(program_configuration, today)
                pass
                
        except:
            logger.error('Fail to execute scheduled giveaway reward program due to %s', get_tracelog())
            
    return 'triggered execute_giveaway_reward_program'  

@check_schedule_program_bp.route('/giveaway-membership-reward-program', methods=['POST'])
#@service_header_authenticated
@request_values
def execute_giveaway_membership_reward_program(request_values):
    program_configuration_in_str = request_values.get('program_configuration')
    if program_configuration_in_str:
        program_configuration = json.loads(program_configuration_in_str)
        now                         = datetime.utcnow()
        today                       = now.date() 
        db_client = create_db_client(caller_info="execute_giveaway_membership_reward_program")
        try:
            with db_client.context():
                giveaway_membership_reward_program(program_configuration, today)
                
        except:
            logger.error('Fail to execute scheduled giveaway reward program due to %s', get_tracelog())
            
    return 'triggered execute_giveaway_reward_program'    

@check_schedule_program_bp.route('/beginning-of-month', methods=['GET'])
#@service_header_authenticated
def check_beginning_of_month_schedule_program():
    db_client = create_db_client(caller_info="check_beginning_of_month_schedule_program")
    try:
        with db_client.context():
            schedule_program_list = MerchantScheduleProgram.list_beginning_of_month_schedule_program()
        
            if schedule_program_list:
                check_schedule_program(schedule_program_list)
    except:
        logger.error('Fail to check beginning of month schedule program due to %s', get_tracelog())
        
    return 'Trigger checking'

@check_schedule_program_bp.route('/friday', methods=['GET'])
#@service_header_authenticated
def check_friday_schedule_program():
    db_client = create_db_client(caller_info="check_friday_schedule_program")
    try:
        with db_client.context():
            schedule_program_list = MerchantScheduleProgram.list_friday_schedule_program()
        
            if schedule_program_list:
                check_schedule_program(schedule_program_list)
    except:
        logger.error('Fail to check friday schedule program due to %s', get_tracelog())
        
    return 'Trigger checking'

@check_schedule_program_bp.route('/monday', methods=['GET'])
#@service_header_authenticated
def check_monday_schedule_program():
    db_client = create_db_client(caller_info="check_monday_schedule_program")
    try:
        with db_client.context():
            schedule_program_list = MerchantScheduleProgram.list_beginning_of_week_schedule_program()
        
            if schedule_program_list:
                check_schedule_program(schedule_program_list)
    except:
        logger.error('Fail to check begining of week schedule program due to %s', get_tracelog())
        
    return 'Trigger checking'

    
def list_merchant_customer_by_birth_date_based_on_program_configuration(merchant_acct, program_configuration, transact_date, start_cursor=None):
    program_settings        = program_configuration.get('program_settings')
    giveaway_when           = program_settings.get('scheme').get('giveaway_when')
    found_customers_list    = []
    next_cursor             = None
    
    if  giveaway_when == program_conf.ADVANCE_IN_DAY:
        checking_date           = transact_date + timedelta(days=int(program_configuration.get('program_settings').get('scheme').get('advance_in_day')))   
        checking_date_of_birth  = checking_date.strftime('%d/%m')    
        
        (found_customers_list, next_cursor)    = Customer.list_merchant_customer_by_date_of_birth(merchant_acct, 
                                                                                                  checking_date_of_birth, 
                                                                                                  limit                 = SCHEDULE_CHECK_PAGINATION_SIZE, 
                                                                                                  return_with_cursor    = True,
                                                                                                  start_cursor          = start_cursor,
                                                                                                  )
         
        
    elif  giveaway_when == program_conf.FIRST_DAY_OF_MONTH:
        checking_date_start             = date(transact_date.year, transact_date.month, 1) 
        checking_date_end               = date(transact_date.year, transact_date.month, last_day_of_month(checking_date_start).day)   
        
        (found_customers_list, next_cursor)    = Customer.list_merchant_customer_by_date_of_birth_thru_date_range(merchant_acct, 
                                                                                                                  date_range_start      = checking_date_start,
                                                                                                                  date_range_end        = checking_date_end, 
                                                                                                                  limit                 = SCHEDULE_CHECK_PAGINATION_SIZE, 
                                                                                                                  return_with_cursor    = True,
                                                                                                                  start_cursor          = start_cursor,
                                                                                                                  )
    return (found_customers_list, next_cursor)

def list_merchant_customer_by_membership_based_on_program_configuration(program_configuration, transact_date, start_cursor=None):
    program_settings            = program_configuration.get('program_settings')
    giveaway_system_settings    = program_settings.get('giveaway_system_settings')
    giveaway_memberships        = giveaway_system_settings.get('giveaway_memberships')
    
    limit                       = 50
    merchant_memberships_list   = []
    
    for membership_key in giveaway_memberships:
        merchant_membership = MerchantMembership.fetch(membership_key)
        merchant_memberships_list.append(merchant_membership)
    
    logger.debug('list_merchant_customer_by_membership_based_on_program_configuration debug: transact_date=%s', transact_date)
    
    (active_memberships_list, next_cursor) =  CustomerMembership.list_active_merchant_membership_by_entitled_date(merchant_memberships_list, transact_date, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
    
    customers_list = []
    for r in active_memberships_list:
        customers_list.append(r.customer)
    
    return (customers_list, next_cursor)
    
        
def giveaway_birthday_reward_to_all_customer(program_configuration, schedule_date):
    program_desc            = program_configuration.get('desc')
    merchant_acct           = MerchantAcct.fetch(program_configuration.get('merchant_acct_key'))
    
    logger.debug('program_configuration=%s', program_configuration)
    
    logger.debug('**************************** %s *************************************', program_desc)
    
    (found_customers_list, next_cursor) = list_merchant_customer_by_birth_date_based_on_program_configuration(merchant_acct, program_configuration, schedule_date)
    
    
        
    while (found_customers_list is not None and len(found_customers_list)>0):    
        
        logger.debug('found_customers_list length=%s', len(found_customers_list))
        
        for customer in found_customers_list:
            giveaway_birthday_reward_to_customer(customer, program_configuration, schedule_date, merchant_acct)
            
        if is_not_empty(next_cursor):  
            logger.debug('------------------------ next pagination list by cursor=%s', next_cursor)      
            
            (found_customers_list, next_cursor) = list_merchant_customer_by_birth_date_based_on_program_configuration(merchant_acct, program_configuration, schedule_date, start_cursor = next_cursor)
            
            
            logger.debug('while: next_cursor=%s', next_cursor)
            logger.debug('while: found_customers_list=%s', found_customers_list)
            
            
        else:
            found_customers_list = None
            
def giveaway_membership_reward_to_all_customer(program_configuration, transact_date):
    program_desc            = program_configuration.get('desc')
    merchant_acct           = MerchantAcct.fetch(program_configuration.get('merchant_acct_key'))
    logger.debug('program_configuration=%s', program_configuration)
    
    logger.debug('**************************** %s *************************************', program_desc)
    logger.debug('transact_date=%s', transact_date)
    (found_customers_list, next_cursor) = list_merchant_customer_by_membership_based_on_program_configuration(program_configuration, transact_date)
    
    logger.debug('found_customers_list length=%s', len(found_customers_list))
    
        
    while (found_customers_list is not None and len(found_customers_list)>0):    
        
        
        
        for customer in found_customers_list: 
            giveaway_membership_reward_to_customer(customer, program_configuration, transact_date, merchant_acct)
            
        if is_not_empty(next_cursor):  
            logger.debug('------------------------ next pagination list by cursor=%s', next_cursor)      
            
            (found_customers_list, next_cursor) = list_merchant_customer_by_membership_based_on_program_configuration(program_configuration, transact_date, start_cursor = next_cursor)
            
            
            logger.debug('while: next_cursor=%s', next_cursor)
            logger.debug('while: found_customers_list=%s', found_customers_list)
            
            
        else:
            found_customers_list = None 
            
def giveaway_reward_to_all_customer(program_configuration, transact_date):
    program_desc            = program_configuration.get('desc')
    merchant_acct           = MerchantAcct.fetch(program_configuration.get('merchant_acct_key'))
    logger.debug('program_configuration=%s', program_configuration)
    
    logger.debug('**************************** %s *************************************', program_desc)
    
    (found_customers_list, next_cursor) = list_merchant_customer_by_membership_based_on_program_configuration(program_configuration, transact_date)
    
    
        
    while (found_customers_list is not None and len(found_customers_list)>0):    
        
        logger.debug('found_customers_list length=%s', len(found_customers_list))
        
        for customer in found_customers_list: 
            giveaway_membership_reward_to_customer(customer, program_configuration, transact_date, merchant_acct)
            
        if is_not_empty(next_cursor):  
            logger.debug('------------------------ next pagination list by cursor=%s', next_cursor)      
            
            (found_customers_list, next_cursor) = list_merchant_customer_by_membership_based_on_program_configuration(program_configuration, transact_date, start_cursor = next_cursor)
            
            
            logger.debug('while: next_cursor=%s', next_cursor)
            logger.debug('while: found_customers_list=%s', found_customers_list)
            
            
        else:
            found_customers_list = None                        

