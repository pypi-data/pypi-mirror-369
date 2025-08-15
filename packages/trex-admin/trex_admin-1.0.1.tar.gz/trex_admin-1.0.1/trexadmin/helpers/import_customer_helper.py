'''
Created on 4 Oct 2023

@author: jacklok
'''
from trexmodel.models.datastore.customer_models import Customer
from trexlib.utils.string_util import is_not_empty, is_empty
from datetime import datetime
from trexmodel.models.datastore.merchant_models import Outlet
from trexmodel.models.datastore.user_models import User
import hashlib
import logging
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexprogram.reward_program.reward_program_factory import RewardProgramFactory
from trexmodel.models.datastore.helper.reward_transaction_helper import update_customer_kpi_summary_and_transact_summary
from trexmodel.models.datastore.program_models import MerchantProgram
from trexlib.utils.log_util import get_tracelog
from trexmodel.conf import GENDER_MALE_CODE, GENDER_FEMALE_CODE,\
    GENDER_UNKNOWN_CODE
from trexanalytics.bigquery_upstream_data_config import create_merchant_registered_customer_upstream_for_merchant,\
    create_registered_customer_upstream_for_system
from trexmodel.models.datastore.import_models import ImportFailedCustomerData,\
    ImportDuplicatedCustomerData
from trexconf import conf

logger = logging.getLogger('helper')

def create_customer_from_import_file_data(customer_import_data, merchant_acct):
    
    logger.debug('customer_import_data=%s', customer_import_data)
    
    email                   = customer_import_data.get('email')
    mobile_phone            = customer_import_data.get('mobile_phone')
    registered_outlet_key   = customer_import_data.get('registered_outlet')
    birth_date              = customer_import_data.get('birth_date')
    password                = customer_import_data.get('default_password')
    gender                  = customer_import_data.get('gender') 
    
    
    is_email_used               = False
    is_mobile_phone_used        = False
    created_user_acct           = None
    created_customer            = None
    registered_outlet           = None
                
    if is_empty(gender):
        gender = conf.GENDER_UNKNOWN_CODE
        
    if is_not_empty(birth_date):
        birth_date = datetime.strptime(birth_date, '%d/%m/%Y')    
    
    if is_not_empty(registered_outlet_key):
        registered_outlet = Outlet.fetch(registered_outlet_key)
        
    
    if is_not_empty(email):
        created_user_acct = User.get_by_email(email)
        if created_user_acct:    
            
            is_email_used = True
            
    
    if created_user_acct is None:
        if is_not_empty(mobile_phone):
            mobile_phone = mobile_phone.replace(" ", "")
            created_user_acct = User.get_by_mobile_phone(mobile_phone)
            
            #if created_user_acct and created_user_acct.is_mobile_phone_verified:
            if created_user_acct:
                is_mobile_phone_used = True    
    
    logger.info('is_email_used=%s, is_mobile_phone_used=%s', is_email_used, is_mobile_phone_used)
    
    
    if is_email_used:
        created_customer = Customer.get_by_email(email, merchant_acct=merchant_acct)
    
    if created_customer is None:    
        if is_mobile_phone_used:
            created_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
    
    if created_customer is not None:
        logger.info('The customer is exist, where %s', customer_import_data)
        return None
        
    md5_hashed_password =  hashlib.md5(password.encode('utf-8')).hexdigest()
    
    if is_email_used or is_mobile_phone_used:
        if created_customer is None:   
            created_user_acct = User.update(created_user_acct,
                                            name                    = customer_import_data.get('name'), 
                                            email                   = email, 
                                            gender                  = gender,
                                            birth_date              = birth_date,
                                            mobile_phone            = mobile_phone, 
                                            password                = md5_hashed_password,
                                            is_email_verified       = True,
                                            is_mobile_phone_verified= True,
                                            )     
            try:
                created_customer        = Customer.create_from_user(registered_outlet, created_user_acct, 
                                                                    customer_import_data.get('member_card_no'))
                
                create_merchant_registered_customer_upstream_for_merchant(created_customer)
                create_registered_customer_upstream_for_system(created_customer)
            except:
                logger.error('Failed to create customer due to %s', get_tracelog())
                ImportFailedCustomerData.create(merchant_acct, customer_import_data)
        else:
            logger.warn('Duplicated customer = %s', customer_import_data)
            ImportDuplicatedCustomerData.create(merchant_acct, customer_import_data)
    else:
        try:
            created_customer        = Customer.create( 
                                            outlet                  = registered_outlet, 
                                            name                    = customer_import_data.get('name'), 
                                            email                   = email, 
                                            gender                  = gender,
                                            birth_date              = birth_date,
                                            mobile_phone            = mobile_phone, 
                                            merchant_reference_code = customer_import_data.get('member_card_no'), 
                                            password                = md5_hashed_password,
                                            is_email_verified       = True,
                                            is_mobile_phone_verified= True,
                                            )
            
            create_merchant_registered_customer_upstream_for_merchant(created_customer)
            create_registered_customer_upstream_for_system(created_customer)
        except:
            logger.error('Failed to create customer due to %s', get_tracelog())
            ImportFailedCustomerData.create(merchant_acct, customer_import_data)
        
    return created_customer

def create_import_transaction(customer, transact_outlet=None, remarks='Customer Import', 
                            transact_by=None, transact_datetime=None):
    
    logger.debug('---create_import_transaction---')
    
    
    customer_transaction = CustomerTransaction.create_system_transaction(
                                       customer, 
                                       transact_outlet      = transact_outlet,
                                       
                                       transact_amount      = .0, 
                                       tax_amount           = .0,
                                       
                                       remarks              = remarks,
                                       
                                       transact_by          = transact_by,
                                       
                                       transact_datetime    = transact_datetime,
                                       
                                       is_sales_transaction = False,
                                       
                                       )
    return customer_transaction

def giveaway_import_reward_to_customer(customer_acct, transaction_details, program_configuration_list=None, 
                                       reward_set=1):
    merchant_acct                   = transaction_details.transact_merchant_acct
    program_configuration_list      = merchant_acct.program_configuration_list if program_configuration_list is None else program_configuration_list
    
    give_reward_status =  RewardProgramFactory(merchant_acct).get_giveaway_reward(customer_acct, 
                                                            transaction_details, 
                                                            program_configuration_list=program_configuration_list, 
                                                            reward_set=reward_set)
    
    return give_reward_status

#@model_transactional(desc='create_import_customer')
def create_import_customer(customer_import_data, merchant_acct):
    try:
        gender = customer_import_data['gender']
            
        if gender in ('Male', 'male', 'm'):
            customer_import_data['gender'] = GENDER_MALE_CODE
        elif gender in ('Female', 'female', 'f'):
            customer_import_data['gender'] = GENDER_FEMALE_CODE
        else:
            customer_import_data['gender'] = GENDER_UNKNOWN_CODE
            
        created_customer             = create_customer_from_import_file_data(customer_import_data, merchant_acct)
        if created_customer is None:
            logger.info('failed to create customer email=%s, mobile_phone=%s', customer_import_data['email'], customer_import_data['mobile_phone'])
            
        else:
        
            prepaid_cash_amount          = customer_import_data.get('prepaid_cash')
            point_amount                 = customer_import_data.get('point')
            stamp_amount                 = customer_import_data.get('stamp')
            
            prepaid_cash_program         = customer_import_data.get('prepaid_cash_program')
            point_program                = customer_import_data.get('point_program')
            stamp_program                = customer_import_data.get('stamp_program')
            
            registered_outlet            = customer_import_data.get('registered_outlet')
            
            transact_datetime            = datetime.utcnow()
            
            is_prepaid_cash_available   = False
            is_point_available          = False
            is_stamp_available          = False
            
            if is_not_empty(prepaid_cash_program):
                if is_not_empty(prepaid_cash_amount):
                    prepaid_cash_amount = float(prepaid_cash_amount)
                    is_prepaid_cash_available = True
                
            if is_not_empty(point_program):    
                if is_not_empty(point_amount):
                    point_amount = float(point_amount)
                    is_point_available = True
                
            if is_not_empty(stamp_program):    
                if is_not_empty(stamp_amount):
                    stamp_amount = int(float(stamp_amount))  
                    is_stamp_available = True      
                    
            
            logger.debug('is_prepaid_cash_available=%s', is_prepaid_cash_available)
            logger.debug('is_point_available=%s', is_point_available)
            logger.debug('is_stamp_available=%s', is_stamp_available)
            
            logger.debug('prepaid_cash_amount=%s', prepaid_cash_amount)
            logger.debug('point_amount=%s', point_amount)
            logger.debug('stamp_amount=%s', stamp_amount)
            
            if is_prepaid_cash_available or is_point_available or is_stamp_available:
                registered_outlet = Outlet.fetch(registered_outlet)
                
                import_reward_transaction_details   = create_import_transaction(created_customer, 
                                                                                transact_outlet=registered_outlet,
                                                                                transact_datetime=transact_datetime,
                                                                                )
                
                logger.debug('import_reward_transaction_details=%s', import_reward_transaction_details)
                
                if is_prepaid_cash_available:
                    prepaid_cash_program = MerchantProgram.fetch(prepaid_cash_program)
                    
                    giveaway_import_reward_to_customer(created_customer, import_reward_transaction_details, 
                                                       [prepaid_cash_program.to_configuration()],
                                                       reward_set = prepaid_cash_amount
                                                       )
                    
                if is_point_available:
                    point_program = MerchantProgram.fetch(point_program)
                    
                    giveaway_import_reward_to_customer(created_customer, import_reward_transaction_details, 
                                                       [point_program.to_configuration()],
                                                       reward_set = point_amount
                                                       )
                    
                if is_stamp_available:
                    stamp_program = MerchantProgram.fetch(stamp_program)
                    
                    giveaway_import_reward_to_customer(created_customer, import_reward_transaction_details, 
                                                       [stamp_program.to_configuration()],
                                                       reward_set = stamp_amount
                                                       )        
                    
                    
                update_customer_kpi_summary_and_transact_summary(created_customer, import_reward_transaction_details)    
    except:
        logger.error('Failed to create customer due to %s', get_tracelog())
