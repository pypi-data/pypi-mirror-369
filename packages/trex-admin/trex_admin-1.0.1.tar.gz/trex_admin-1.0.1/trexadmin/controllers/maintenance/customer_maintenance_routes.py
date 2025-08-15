'''
Created on 28 Dec 2022

@author: jacklok
'''

from flask import Blueprint, request, jsonify
from trexmodel.utils.model.model_util import create_db_client,\
    generate_transaction_id 
from trexadmin.libs.http import StatusCode, create_rest_message
import logging
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership
from trexmodel.models.datastore.helper.reward_transaction_helper import update_customer_entitled_voucher_summary,\
    update_customer_kpi_summary_from_transaction_list,\
    update_customer_memberships_list
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from flask_restful import Api
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexadmin.controllers.report.merchant import customer
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.membership_models import MerchantMembership
from datetime import datetime, timedelta
from trexmodel.models.datastore.program_models import MerchantScheduleProgram,\
    MerchantProgram
from trexadmin.controllers.merchant.reward_program.check_schedule_program_routes import execute_merchant_schedule_program_reward
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel import program_conf
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher,\
    CustomerEntitledTierRewardSummary
from trexprogram.reward_program.reward_program_factory import RewardProgramFactory
from trexmodel.models.datastore.customer_model_helpers import update_customer_entiteld_voucher_summary_with_customer_new_voucher,\
    update_reward_summary_with_new_reward
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawTicket
from trexadmin.helpers.delete_customer_helper import delete_customer
from trexmodel.models.datastore.message_models import Message
from trexmodel.models.datastore.message_model_helper import create_transaction_message,\
    create_redemption_message
from trexanalytics.bigquery_upstream_data_config import create_customer_membership_upstream_for_merchant,\
    create_merchant_registered_customer_upstream_for_merchant
from trexlib.libs.flask_wtf.request_wrapper import request_args
from trexlib.utils.common.date_util import convert_date_to_datetime

customer_maintenance_setup_bp = Blueprint('customer_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/customer')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

customer_maintenance_setup_bp_api = Api(customer_maintenance_setup_bp)


@customer_maintenance_setup_bp.route('/customer-key/<customer_key>/outlet-key/<outlet_key>/program-key/<program_key>/start-date/<start_date>/end-date/<end_date>/test-reward-redeem', methods=['get'])
def test_custsomer_new_reward_transaction(customer_key, outlet_key, program_key, start_date, end_date):
    db_client   = create_db_client(caller_info="test_custsomer_new_reward_transaction")
    start_date  = datetime.strptime(start_date, '%d-%m-%Y')
    end_date    = datetime.strptime(end_date, '%d-%m-%Y')
    
    customer    = None
    reward_format = None
    transact_datetime = datetime.utcnow()
    program_configuration_list = []
    final_redeemed_items_list = []
    
    with db_client.context():
        customer                    = Customer.fetch(customer_key)
        transact_outlet             = Outlet.fetch(outlet_key)
        merchant_acct               = transact_outlet.merchant_acct_entity
        reward_program              = MerchantProgram.fetch(program_key)
        program_configuration       = reward_program.to_configuration()
        program_configuration_list.append(program_configuration)
        reward_format               = reward_program.reward_format
        
    redeem_transaction_id = generate_transaction_id(prefix='r')
    
    def __start_read_reward_transaction():
        if reward_format == program_conf.REWARD_FORMAT_POINT:
            result = CustomerPointReward.list_valid(customer, limit=10000)
        elif reward_format == program_conf.REWARD_FORMAT_STAMP:
            result = CustomerStampReward.list_valid(customer, limit=10000)
            
        logger.debug('result=%s', result)
    
    def __start_redeem_transaction(__total_redeemed_amount, cursor):
        if reward_format == program_conf.REWARD_FORMAT_POINT:
            (result, next_cursor) = CustomerPointReward.list_by_valid_with_cursor(customer, limit=50, start_cursor=cursor)
        elif reward_format == program_conf.REWARD_FORMAT_STAMP:
            (result, next_cursor) = CustomerStampReward.list_by_valid_with_cursor(customer, limit=50, start_cursor=cursor)
            
        if result:
                 
            redeemed_items_list = []
            transaction_id_list = []
            for r in result:
                redeemed_amount                     = .0
                reward_balance_before_redeem        = r.reward_balance
                
                logger.debug('__start_redeem: reward_balance_before_redeem before=%s',  reward_balance_before_redeem)
                logger.debug('__start_redeem: __total_redeemed_amount before=%s',  __total_redeemed_amount)
                
                if reward_balance_before_redeem>0:
                    
                    if reward_balance_before_redeem<__total_redeemed_amount:
                        logger.debug('__start_redeem: redeem partial amount from redeem amount')
                        redeemed_amount = reward_balance_before_redeem
                        __total_redeemed_amount -=reward_balance_before_redeem
                        r.update_used_reward_amount(reward_balance_before_redeem)
                        reward_balance_before_redeem = 0
                        
                    else:
                        logger.debug('__start_redeem: redeem remaining balance from redeem amount')
                        redeemed_amount = __total_redeemed_amount
                        r.update_used_reward_amount(__total_redeemed_amount)
                        reward_balance_before_redeem -= __total_redeemed_amount
                        __total_redeemed_amount = 0
                     
                    
                    logger.debug('__start_redeem: __total_redeemed_amount=%s',  __total_redeemed_amount)
                    logger.debug('__start_redeem: reward_balance_before_redeem after =%s',  reward_balance_before_redeem)
                    
                    transaction_id_list.append(r.transaction_id)
                
                    #record customer CustomerPointReward/CustomerStampReward key and used_reward_amount
                    redeemed_items_list.append({
                                                'key'      : r.key_in_str, 
                                                'amount'   : redeemed_amount,
                                                
                                                })
                    
                    if __total_redeemed_amount<=0:
                        break
                else:
                    logger.debug('__start_redeem reward balance is ZERO')
            
            logger.debug('after finished reading reward') 
            
            transaction_id_list = set(transaction_id_list) 
            for transaction_id in transaction_id_list:
                CustomerTransaction.update_transaction_reward_have_been_redeemed(transaction_id, redeem_transaction_id)
            
            return (__total_redeemed_amount, next_cursor,  redeemed_items_list)
        else:
            raise Exception('Reward not found')
    
    #@model_transactional(desc='test_reward_transaction')    
    def __start_transaction():
        reward_transaction          = CustomerTransaction.create_manual_transaction(
                                           customer, 
                                           transact_outlet      = transact_outlet,
                                           
                                           remarks              = 'Testing',
                                           
                                           transact_datetime    = transact_datetime,
                                           )
        
        give_reward_status =  RewardProgramFactory(merchant_acct).get_giveaway_reward(customer, 
                                                            reward_transaction, 
                                                            program_configuration_list=program_configuration_list, 
                                                            reward_set=1,
                                                            create_upstream=False)
        logger.debug('give_reward_status=%s', give_reward_status)
        if give_reward_status:
            total_redeemed_amount = 3
            
            logger.debug('reward_transaction transaction_id=%s', reward_transaction.transaction_id)
            __start_read_reward_transaction()
            '''
            (total_redeemed_amount, next_cursor,  redeemed_items_list) = __start_redeem_transaction(total_redeemed_amount, None)
            logger.debug('After 1st redeem: total_redeemed_amount=%s, next_cursor=%s, redeemed_items_list=%s', total_redeemed_amount, next_cursor, redeemed_items_list)
            
            if is_not_empty(redeemed_items_list):
                final_redeemed_items_list.extend(redeemed_items_list)
            '''
                
            '''
            (total_redeemed_amount, next_cursor,  redeemed_items_list) = __start_redeem_transaction(total_redeemed_amount, next_cursor)
            
            logger.debug('After 2nd redeem: total_redeemed_amount=%s, next_cursor=%s, redeemed_items_list=%s', total_redeemed_amount, next_cursor, redeemed_items_list)
            
            if is_not_empty(redeemed_items_list):
                final_redeemed_items_list.extend(redeemed_items_list)
            (total_redeemed_amount, next_cursor,  redeemed_items_list) = __start_redeem_transaction(total_redeemed_amount, next_cursor)
            
            logger.debug('After 3rd redeem: total_redeemed_amount=%s, next_cursor=%s, redeemed_items_list=%s', total_redeemed_amount, next_cursor, redeemed_items_list)
            
            if is_not_empty(redeemed_items_list):
                final_redeemed_items_list.extend(redeemed_items_list)
            '''
            '''    
            if is_empty(next_cursor) and total_redeemed_amount>0:
                raise Exception('Failed to redeem')
            '''    
        else:
            raise Exception('Failed to give reward')
        
        if True:
            raise Exception('Completed Testing')
    
    with db_client.context():           
        __start_transaction()
        
    return jsonify(final_redeemed_items_list)    

@customer_maintenance_setup_bp.route('/customer-key/<customer_key>/delete', methods=['DELETE'])
def delete_custsomer(customer_key):
    db_client   = create_db_client(caller_info="delete_custsomer")
    is_deleted  = False
    with db_client.context():
        customer = Customer.fetch(customer_key)
        
        if customer:
            customer.delete()
            is_deleted = True
    
    return jsonify({
            'is_deleted'    : is_deleted,
            'date_time'     : datetime.now(),
            })        

@customer_maintenance_setup_bp.route('/customer-key/<customer_key>/reward-format/<reward_format>/start-date/<start_date>/end-date/<end_date>/accumulated-reward-summary', methods=['get'])
def show_custsomer_reward_summary(customer_key, start_date, end_date, reward_format):
    db_client   = create_db_client(caller_info="show_custsomer_reward_summary")
    start_date  = datetime.strptime(start_date, '%d-%m-%Y')
    end_date    = datetime.strptime(end_date, '%d-%m-%Y')
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        
        tansaction_list = CustomerTransaction.list_customer_transaction_by_transact_datetime(customer, 
                                                                               transact_datetime_from   = start_date, 
                                                                               transact_datetime_to     = end_date)
    accumulated_reward_summary = {}
    for transaction in tansaction_list:
        if transaction.is_revert == False:
            transaction_reward_summary = transaction.entitled_reward_summary
            if transaction_reward_summary:
                target_reward_summary = transaction_reward_summary.get(reward_format)
                if target_reward_summary:
                    reward_amount = accumulated_reward_summary.get(reward_format) or .0
                    reward_amount+= target_reward_summary.get('amount')
                    accumulated_reward_summary[reward_format] = reward_amount
    
    return jsonify(accumulated_reward_summary)                

@customer_maintenance_setup_bp.route('/customer-key/<customer_key>/list-customer-membership', methods=['get'])
def list_customer_membership(customer_key):
    if is_not_empty(customer_key):
        db_client = create_db_client(caller_info="list_customer_membership")
        customer_membership_final_list = []
        with db_client.context():
            customer = Customer.fetch(customer_key)
            merchant_acct = customer.registered_merchant_acct
            customer_memberhips_list = CustomerMembership.list_active_by_customer(customer)
            
            merchant_memberships_list = MerchantMembership.list_by_merchant_acct(merchant_acct)
            
            #if customer.tier_membership:
                
            
            for cm in customer_memberhips_list:
                for mm in merchant_memberships_list:
                    if mm.key_in_str == cm.merchant_membership_key:
                        customer_membership_data = {
                                                        'key'           : cm.key_in_str,
                                                        'label'         : mm.label,
                                                        'entitled_date' : cm.joined_date.strftime('%d-%m-%Y'),
                                                        'expiry_date'   : cm.expiry_date.strftime('%d-%m-%Y'),
                                                        }
                        
                        if cm.renewed_date is not None:
                            customer_membership_data['renewed_date'] = cm.renewed_date.strftime('%d-%m-%Y'),
                        
                        customer_membership_final_list.append(customer_membership_data)
                        break
        
    
        return jsonify(customer_membership_final_list)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  


@customer_maintenance_setup_bp.route('/list-customer-by-merchant-membership-and-joined-date/merchant-membership/<merchant_membership_key>/joined-date/<entitled_date>/limit/<limit>', methods=['get'])
def list_customer_by_merchant_membership_and_joined_date(merchant_membership_key, entitled_date, limit):
    db_client = create_db_client(caller_info="list_customer_by_merchant_membership_and_entitled_date")
    customers_list = []
    with db_client.context():
        merchant_membership = MerchantMembership.fetch(merchant_membership_key)
        entitled_date = datetime.strptime(entitled_date, '%d-%m-%Y').date()
        
        merchant_memberships_list = [merchant_membership]
        
        result = CustomerMembership.list_merchant_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=int(limit))
        if result:
            for r in result:
                customers_list.append(r.customer.to_dict())  
    
    
    
    return jsonify(customers_list) 

@customer_maintenance_setup_bp.route('/trigger-merchant-schedule-program/merchant-schedule-program/<merchant_schedule_program_key>/schedule-date/<schedule_date>', methods=['get'])
def trigger_merchant_schedule_program(merchant_schedule_program_key, schedule_date):
    db_client = create_db_client(caller_info="trigger_merchant_schedule_program")
    schedule_date = datetime.strptime(schedule_date, '%d-%m-%Y')
    with db_client.context():
        merchant_schedule_program = MerchantScheduleProgram.fetch(merchant_schedule_program_key)
        if merchant_schedule_program:
            program_configuration = merchant_schedule_program.program_configuration
            if program_configuration:
                execute_merchant_schedule_program_reward(program_configuration, schedule_date)
    
    
    executed_datetime = datetime.now()
    return '%s' % executed_datetime, 200

@customer_maintenance_setup_bp.route('/revert-merchant-schedule-program/merchant-schedule-program/<merchant_schedule_program_key>/customer/<customer_key>/schedule-year/<schedule_year>', methods=['get'])
def revert_merchant_schedule_program(merchant_schedule_program_key, customer_key, schedule_year):
    db_client       = create_db_client(caller_info="revert_merchant_schedule_program")
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        merchant_schedule_program = MerchantScheduleProgram.fetch(merchant_schedule_program_key)
        if merchant_schedule_program:
            program_configuration = merchant_schedule_program.program_configuration
            program_key = program_configuration.get('program_key')
            Customer.revert_customer_entitled_membership_reward_summary(customer, program_key, schedule_year) 
        
    
    executed_datetime = datetime.now()
    return '%s' % executed_datetime, 200

@customer_maintenance_setup_bp.route('/list-redeemed-voucher-by-passed-date-range/merchant-voucher/<merchant_voucher_key>/customer/<customer_key>/passed-days/<passed_day_count>', methods=['get'])
def list_entitled_voucher_by_passed_date_range(merchant_voucher_key, customer_key, passed_day_count):
    logger.debug('passed_day_count=%s', passed_day_count)
    
    db_client = create_db_client(caller_info="list_entitled_voucher_by_passed_date_range")
    count = 0
    with db_client.context():
        customer = Customer.fetch(customer_key)
        merchant_voucher = MerchantVoucher.fetch(merchant_voucher_key)
        if customer and merchant_voucher:
            voucher_label = merchant_voucher.label
            '''
            found_result = CustomerEntitledVoucher.list_redeemed_by_merchant_voucher(customer, merchant_voucher, passed_day_count=int(passed_day_count))
            if found_result:
                count = len(found_result)
            ''' 
            count = CustomerEntitledVoucher.count_redeemed_by_merchant_voucher(customer, merchant_voucher, passed_day_count=int(passed_day_count))
    
    
    result = {
            'voucher_label'     : voucher_label,
            'coun'              : count,
            }
    
    return jsonify(result)

@customer_maintenance_setup_bp.route('/list-customer-reward-point-balance-transaction/customer/<customer_key>', methods=['get'])
def list_customer_reward_point_balance_transaction(customer_key):
    logger.debug('customer_key=%s', customer_key)
    
    db_client = create_db_client(caller_info="list_customer_reward_point_balance_transaction")
    count = 0
    transactions_list = []
    total_reward_balance = .0
    
    customer_reward_summary = {}
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        (result, next_cursor) = CustomerPointReward.list_by_valid_with_cursor(customer, limit=100)
        logger.debug('next_cursor=%s', next_cursor)
        logger.debug('transaction count=%s', len(result))
        
        if result:
            for r in result:
                reward_balance              = r.reward_balance
                transaction_reward_summary  = r.to_reward_summary()
                customer_reward_summary     = update_reward_summary_with_new_reward(customer_reward_summary, transaction_reward_summary)
                total_reward_balance    +=reward_balance
                
                transactions_list.append({
                    'transaction_id': r.transaction_id,
                    'reward_balance': reward_balance,
                    'expiry_date'   : r.expiry_date,
                    })
            
    
    
    result = {
            'transactions_list'         : transactions_list,
            'total_reward_balance'      : total_reward_balance,
            'customer_reward_summary'   : customer_reward_summary,
            }
    
    return jsonify(result)

@customer_maintenance_setup_bp.route('/list-customer-stamp-balance-transaction/customer/<customer_key>', methods=['get'])
def list_customer_stamp_balance_transaction(customer_key):
    logger.debug('customer_key=%s', customer_key)
    
    db_client = create_db_client(caller_info="list_customer_stamp_balance_transaction")
    count = 0
    transactions_list = []
    total_reward_balance = .0
    
    customer_reward_summary = {}
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        (result, next_cursor) = CustomerStampReward.list_by_valid_with_cursor(customer, limit=100)
        logger.debug('next_cursor=%s', next_cursor)
        logger.debug('transaction count=%s', len(result))
        
        if result:
            for r in result:
                reward_balance              = r.reward_balance
                transaction_reward_summary  = r.to_reward_summary()
                customer_reward_summary     = update_reward_summary_with_new_reward(customer_reward_summary, transaction_reward_summary)
                total_reward_balance    +=reward_balance
                
                transactions_list.append({
                    'transaction_id': r.transaction_id,
                    'reward_balance': reward_balance,
                    'expiry_date'   : r.expiry_date,
                    'status'        : r.status
                    })
            
    
    
    result = {
            'transactions_list'         : transactions_list,
            'total_reward_balance'      : total_reward_balance,
            'customer_reward_summary'   : customer_reward_summary,
            }
    
    return jsonify(result)


@customer_maintenance_setup_bp.route('/update-customer-reward-summary/customer/<customer_key>', methods=['get'])
@request_args
def update_customer_reward_summary(request_args, customer_key):
    checking_date = request_args.get('checking_date')
    
    logger.debug('checking_date=%s', checking_date)
    
    if is_not_empty(checking_date):
        checking_date = datetime.strptime(checking_date, '%d-%m-%Y').date()
    else:
        checking_date = datetime.utcnow().date() - timedelta(days=1)
    
    end_datetime = datetime.now()    
    
    db_client = create_db_client(caller_info="update_customer_reward_summary")
    
    customer_reward_summary = {}
    transactions_list       = []
    total_point_balance     = .0
    total_stamp_balance     = .0
    today                   = datetime.today().date()
    
    def _start_update(result, customer_reward_summary, transactions_list, total_reward_balance):
            
        for r in result:
            reward_balance              = r.reward_balance
            transaction_reward_summary  = r.to_reward_summary()
            customer_reward_summary     = update_reward_summary_with_new_reward(customer_reward_summary, transaction_reward_summary, checking_date=checking_date)
            
            total_reward_balance    +=reward_balance
        
            transactions_list.append({
                'transaction_id'    : r.transaction_id,
                'reward_balance'    : reward_balance,
                'expiry_date'       : datetime.strftime(r.expiry_date, '%d-%m-%Y'),
                'transact_datetime' : datetime.strftime(r.rewarded_datetime, '%d-%m-%Y %H:%M:%s'),
                'reward_format'     : r.reward_format,
                'is_expired'        : r.expiry_date<today,
                })
        return (customer_reward_summary, transactions_list, total_reward_balance)
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        (result, next_cursor) = CustomerStampReward.list_by_valid_with_cursor(customer, limit=100, expiry_date=checking_date)
        logger.debug('next_cursor=%s', next_cursor)
        logger.debug('transaction count=%s', len(result))
        
        while is_not_empty(next_cursor):
                
            if result:
                (customer_reward_summary, transactions_list, total_stamp_balance) = _start_update(result, customer_reward_summary, transactions_list, total_stamp_balance)
                
            (result, next_cursor) = CustomerStampReward.list_by_valid_with_cursor(customer, limit=100, start_cursor=next_cursor, expiry_date=checking_date)
            
            logger.debug('result=%s, type of is %s', result, type(result))
            logger.debug('next_cursor=%s, type of is %s', next_cursor, type(next_cursor))
                                
        if result:
            (customer_reward_summary, transactions_list, total_stamp_balance) = _start_update(result, customer_reward_summary, transactions_list, total_stamp_balance)
            
        (result, next_cursor) = CustomerPointReward.list_by_valid_with_cursor(customer, limit=100)
        logger.debug('next_cursor=%s', next_cursor)
        logger.debug('transaction count=%s', len(result))
        
        while is_not_empty(next_cursor):
                
            if result:
                (customer_reward_summary, transactions_list, total_point_balance) = _start_update(result, customer_reward_summary, transactions_list, total_point_balance)
                
            (result, next_cursor) = CustomerPointReward.list_by_valid_with_cursor(customer, limit=100, start_cursor=next_cursor)
            
            logger.debug('result=%s, type of is %s', result, type(result))
            logger.debug('next_cursor=%s, type of is %s', next_cursor, type(next_cursor))
                                
        if result:
            (customer_reward_summary, transactions_list, total_point_balance) = _start_update(result, customer_reward_summary, transactions_list, total_point_balance)
        
        
        
        customer.reward_summary = customer_reward_summary
        customer.put()
            
    result = {
            'transactions_list'         : transactions_list,
            'total_stamp_balance'       : total_stamp_balance,
            'total_point_balance'       : total_point_balance,
            'customer_reward_summary'   : customer_reward_summary,
            }
    
    return jsonify(result)    
            
@customer_maintenance_setup_bp.route('/update-customer-entitled-voucher-summary/<customer_key>', methods=['get'])
def update_entitled_voucher_summary(customer_key):
    db_client = create_db_client(caller_info="update_entitled_voucher_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            update_customer_entitled_voucher_summary(customer)
    
    
    
    result = {
            'voucher_summary'   : customer.entitled_voucher_summary,
            }
    
    return jsonify(result)

@customer_maintenance_setup_bp.route('/flush-customer-entitled-lucky-draw-summary/<customer_key>', methods=['get'])
def flush_entitled_lucky_draw_summary(customer_key):
    db_client = create_db_client(caller_info="update_entitled_lucky_draw_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            customer.entitled_lucky_draw_ticket_summary = {}
            customer.put()
    
    
    
    return "Flushed", 200

@customer_maintenance_setup_bp.route('/update-customer-entitled-lucky-draw-summary/<customer_key>', methods=['get'])
def update_entitled_lucky_draw_summary(customer_key):
    db_client = create_db_client(caller_info="update_entitled_lucky_draw_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            #merchant_acct = customer.registered_merchant_acct
            
            lucky_draw_tickets_list = LuckyDrawTicket.list_by_customer_acct(customer)
            logger.info('ticket count=%d', lucky_draw_tickets_list)
            Customer.update_tickets_list_into_lucky_draw_ticket_summary(customer, lucky_draw_tickets_list)
            
    return "Updated", 200

@customer_maintenance_setup_bp.route('/update-all-customer-entitled-lucky-draw-summary', methods=['get'])
def update_all_customer_entitled_lucky_draw_summary():
    db_client = create_db_client(caller_info="update_all_customer_entitled_lucky_draw_summary")
    update_count = 0
    with db_client.context():
        customers = Customer.list_all(limit=1000)
        
        for customer in customers:
            lucky_draw_tickets_list = LuckyDrawTicket.list_by_customer_acct(customer)
            
            Customer.update_tickets_list_into_lucky_draw_ticket_summary(customer, lucky_draw_tickets_list)
            update_count+=1
            
    return "Updated %d" % update_count, 200

@customer_maintenance_setup_bp.route('/update-customer-membership/<customer_key>', methods=['get'])
def update_customer_membership_get(customer_key):
    db_client = create_db_client(caller_info="update_customer_membership")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            update_customer_memberships_list(customer)
    
    
    if customer:
        result = {
            'membership'   : customer.memberships_list,
            }
    
        return jsonify(result)
    else:
        return "Invalid customer", 400 

@customer_maintenance_setup_bp.route('/update-all-message', methods=['get'])
def update_all_message():
    db_client = create_db_client(caller_info="update_all_message")
    update_count = 0
    with db_client.context():
        messages_list = Message.list_all(limit=1000)
        
        for message in messages_list:
            logger.debug('message.message_category=%s', message.message_category)
            if message.title=='Transaction Reward':
                customer_transaction = message.customer_transaction_entity
                message.message_content = create_transaction_message(customer_transaction)
            elif message.title=='Redemption':
                customer_redemption = message.customer_redemption_entity
                message.message_content = create_redemption_message(customer_redemption)
                
            elif message.title=='Redemption Catalogue Reward':
                customer_redemption = message.customer_redemption_entity
                message.message_content = create_redemption_message(customer_redemption)    
            
            logger.debug('message =%s', message)
            
            
            message.put()
            
            update_count+=1
            
            logger.debug('message.message_content=%s', message.message_content)
            
    return "Updated %d" % update_count, 200

@customer_maintenance_setup_bp.route('/customer-entitled-voucher-summary/<customer_key>', methods=['get'])
def read_entitled_voucher_summary(customer_key):
    db_client = create_db_client(caller_info="update_entitled_voucher_summary")
    entitled_voucher_summary = {}
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            entitled_voucher_summary = customer.entitled_voucher_summary
    
    
    
    result = {
            'voucher_summary'   : entitled_voucher_summary,
            }
    
    return jsonify(result)

@customer_maintenance_setup_bp.route('/revert-removed-customer-voucher/<redeem_code>', methods=['get'])
def revert_removed_customer_voucher(redeem_code):
    db_client = create_db_client(caller_info="revert_removed_customer_voucher")
    entitled_voucher_summary = {}
    with db_client.context():
        customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
        if customer_voucher:
            customer_voucher.status = program_conf.REWARD_STATUS_VALID
            customer_voucher.put()
            
            customer = customer_voucher.entitled_customer_acct
            customer.update_after_added_voucher(customer_voucher)
            entitled_voucher_summary = customer.entitled_voucher_summary
    
    
    result = {
            'voucher_summary'   : entitled_voucher_summary,
            }
    
    return jsonify(result) 

@customer_maintenance_setup_bp.route('/reupdate-customer-voucher/customer/<customer_key>', methods=['get'])
def reupdate_customer_voucher(customer_key):
    db_client = create_db_client(caller_info="reupdate_customer_voucher")
    entitled_voucher_summary = {}
    with db_client.context():
        customer = Customer.fetch(customer_key)
        customer_vouchers_list    = CustomerEntitledVoucher.list_by_customer(customer)
        if customer_vouchers_list:
            
            for customer_voucher in customer_vouchers_list:
                update_customer_entiteld_voucher_summary_with_customer_new_voucher(entitled_voucher_summary, customer_voucher)
            
            
            customer.entitled_voucher_summary = entitled_voucher_summary
            customer.put()    
    
    return jsonify(entitled_voucher_summary) 

@customer_maintenance_setup_bp.route('/update-customer-lucky-draw-ticket-image/customer/<customer_key>', methods=['get'])
def update_customer_lucky_draw_ticket_image(customer_key):
    db_client = create_db_client(caller_info="update_customer_lucky_draw_ticket_image")
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        entitled_lucky_draw_ticket_summary    = customer.entitled_lucky_draw_ticket_summary
        if entitled_lucky_draw_ticket_summary:
            tickets_list = entitled_lucky_draw_ticket_summary.get('tickets')
            for ticket in tickets_list:
                drawed_details = ticket.get('drawed_details')
                drawed_details['ticket_image_url'] = 'https://backofficedev.augmigo.com/static/app/assets/img/program/lucky_draw_ticket_default-min.png'
                
            
            
        customer.entitled_lucky_draw_ticket_summary = entitled_lucky_draw_ticket_summary
        customer.put()    
    
    return jsonify(entitled_lucky_draw_ticket_summary) 

@customer_maintenance_setup_bp.route('/customer-lucky-draw-ticket-image/customer/<customer_key>', methods=['get'])
def read_customer_lucky_draw_ticket(customer_key):
    db_client = create_db_client(caller_info="update_customer_lucky_draw_ticket_image")
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        entitled_lucky_draw_ticket_summary    = customer.entitled_lucky_draw_ticket_summary
            
    
    return jsonify(entitled_lucky_draw_ticket_summary) 


@customer_maintenance_setup_bp.route('/customer-transaction/transaction-key/<transaction_key>', methods=['get'])
def read_customer_transaction(transaction_key):
    db_client = create_db_client(caller_info="read_customer_transaction")
    customer_transaction = {}
    with db_client.context():
        customer_transaction = CustomerTransaction.fetch(transaction_key)
        if customer_transaction:
            excluded_dict_properties=[
                                    'transact_customer_acct',
                                    'transact_merchant_acct',
                                    'transact_outlet_details',
                                    ]
            customer_transaction = customer_transaction.to_dict(excluded_dict_properties=excluded_dict_properties)
    
    
    
    return jsonify(customer_transaction) 


@customer_maintenance_setup_bp.route('/customer-redemption/redemption-key/<redemption_key>', methods=['get'])
def read_customer_redemption(redemption_key):
    db_client = create_db_client(caller_info="read_customer_transaction")
    with db_client.context():
        customer_redemption = CustomerRedemption.fetch(redemption_key)
        if customer_redemption:
            excluded_dict_properties=[
                                    'redeemed_merchant_acct',
                                    'redeemed_customer_acct',
                                    'redeemed_outlet_details',
                                    ]
            customer_redemption = customer_redemption.to_dict(excluded_dict_properties=excluded_dict_properties)
    
    
    
    return jsonify(customer_redemption) 


@customer_maintenance_setup_bp.route('/customer-details/customer-key/<customer_key>', methods=['get'])
def read_customer_details(customer_key):
    db_client = create_db_client(caller_info="read_customer_details")
    
    with db_client.context():
        customer_details = Customer.fetch(customer_key)
        if customer_details:
            excluded_dict_properties=[
                                    'registered_merchant_acct',
                                    
                                    ]
            customer_details = customer_details.to_dict(excluded_dict_properties=excluded_dict_properties)
    
        else:
            customer_details = {}    
    
    return jsonify(customer_details)


class TriggerResetCustomerKPI(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/customer/init-reset-customer-kpi'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        customer_key=request.args.get('customer_key')
        return {
                'customer_key': customer_key,
            }    
    
class InitResetCustomerKPI(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        customer_key = kwargs.get('customer_key')
        
        
        db_client = create_db_client(caller_info="InitResetCustomerKPI")
    
        with db_client.context():
            customer_details = Customer.fetch(customer_key)
            
        
            count = CustomerTransaction.count_valid_customer_transaction(customer_details)
        
        return count
    
    def get_task_batch_size(self):
        return 20
    
    def get_task_url(self):
        return '/maint/customer/reset-customer-kpi'
    
    def get_task_queue(self):
        return 'test'
    
    
class ExecuteResetCustomerKPI(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        customer_key    = kwargs.get('customer_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: customer_key=%s task_index=%d, offset=%d, limit=%d', customer_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteResetCustomerKPI")
    
        with db_client.context():
            customer_details = Customer.fetch(customer_key)
            
            if customer_details:
                if task_index==1:
                    customer_details.kpi_summary=None
                
                (result, next_cursor) = CustomerTransaction.list_valid_customer_transaction(customer_details, 
                                                                                            limit=20,
                                                                                            start_cursor=start_cursor, return_with_cursor=True)
                logger.debug('=================>>>>>> ExecuteResetCustomerKPI debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    
                    update_customer_kpi_summary_from_transaction_list(customer_details, result)
                    
                    logger.debug('ExecuteResetCustomerKPI debug: customer_details.kpi_summary=%s', customer_details.kpi_summary)
                
                '''
                for r in result:
                    logger.debug('transaction_id=%s transact_amount=%s', r.transaction_id, r.transact_amount)
                '''
        
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/customer/reset-customer-kpi' 
    
class TriggerUpdateCustomerTransaaction(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/customer/init-update-customer-transation'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        return {
                
            }    
    
class InitUpdateCustomerTransaaction(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        
        
        db_client = create_db_client(caller_info="InitUpdateCustomerTransaaction")
    
        with db_client.context():
            count = CustomerTransaction.count()

        return count
    
    def get_task_batch_size(self):
        return 20
    
    def get_task_url(self):
        return '/maint/customer/update-customer-transation'
    
    def get_task_queue(self):
        return 'test'
    
    
class ExecuteUpdateCustomerTransaaction(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteUpdateCustomerTransaaction")
        merchant_voucher_dict = {}
        
        with db_client.context():
            (result, next_cursor) = CustomerTransaction.list(limit=20,
                                                            start_cursor=start_cursor, return_with_cursor=True)
            
            logger.debug('=================>>>>>> ExecuteUpdateCustomerTransaaction debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            if result:
                for customer_transaction in result:
                    if customer_transaction.entitled_voucher_summary:
                        entitled_voucher_summary = customer_transaction.entitled_voucher_summary
                        for voucher_key, voucher_details in customer_transaction.entitled_voucher_summary.items():
                            if voucher_details.get('label') is None:
                                logger.debug('ExecuteUpdateCustomerTransaaction debug: required to update')
                                merchant_voucher = merchant_voucher_dict.get(voucher_key)
                                if merchant_voucher is None:
                                    merchant_voucher = MerchantVoucher.fetch(voucher_key)
                                    merchant_voucher_dict[voucher_key] = merchant_voucher
                                    
                                if merchant_voucher:
                                    entitled_voucher_summary[voucher_key]['key']        = voucher_details.get('voucher_key')
                                    entitled_voucher_summary[voucher_key]['image_url']  = merchant_voucher.image_public_url
                                    entitled_voucher_summary[voucher_key]['label']      = merchant_voucher.label
                                
                                
                            else:
                                logger.debug('ExecuteUpdateCustomerTransaaction debug: updated')
                        
                        customer_transaction.entitled_voucher_summary = entitled_voucher_summary
                        customer_transaction.put()
                        logger.debug('=================>>>>>> ExecuteUpdateCustomerTransaaction debug: entitled_voucher_summary=%s', entitled_voucher_summary)
                                
                    else:
                        logger.debug('ExecuteUpdateCustomerTransaaction debug: not voucher entitlement')
            
                
                
        
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/customer/update-customer-transation'    
    
class TriggerCreateCustomerUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/customer/init-create-customer-upstream'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        return {
                
            }    
    
class InitCreateCustomerUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        
        
        db_client = create_db_client(caller_info="InitCreateCustomerUpstream")
    
        with db_client.context():
            count = Customer.count()

        return count
    
    def get_task_batch_size(self):
        return 20
    
    def get_task_url(self):
        return '/maint/customer/create-customer-upstream'
    
    def get_task_queue(self):
        return 'test'
    
    
class ExecuteCreateCustomerUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateCustomerUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                #(result, next_cursor) = Customer.list(limit=20, start_cursor=start_cursor, return_with_cursor=True)
                if merchant_acct:
                    (result, next_cursor) = Customer.list_merchant_customer(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            else:
                (result, next_cursor) = Customer.list(limit=20, start_cursor=start_cursor, return_with_cursor=True)
            
            logger.debug('=================>>>>>> ExecuteUpdateCustomerTransaaction debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            if result:
                for customer_acct in result:
                    create_merchant_registered_customer_upstream_for_merchant(customer_acct)
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/customer/create-customer-upstream'         
    
    
class TriggerImportCustomerMembershipUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/customer/init-import-customer-membership-upstream'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        merchant_key=request.args.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
    
class InitImportCustomerMembershipUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitResetCustomerMembership")
    
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_key)
            count = Customer.count_merchant_customer(merchant_acct)
        
        return count
    
    def get_task_batch_size(self):
        return 20
    
    def get_task_url(self):
        return '/maint/customer/import-customer-membership-upstream'
    
    def get_task_queue(self):
        return 'test'
    
    
    def get_data_payload(self):
        merchant_key=request.get_json().get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteImportCustomerMembershipUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteResetCustomerKPI")
    
        with db_client.context():
            merchant_acct               = MerchantAcct.fetch(merchant_key)
            (result, next_cursor)       = Customer.list_merchant_customer(merchant_acct, offset, limit, start_cursor, return_with_cursor=True)
            
            if result:
                
                for customer_details in result:
                    customer_membership_list = CustomerMembership.list_by_customer(customer_details)
                    for customer_membership in customer_membership_list: 
                        create_customer_membership_upstream_for_merchant(customer_membership)
                    
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/customer/import-customer-membership-upstream' 

    def get_data_payload(self):
        merchant_key=request.get_json().get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
        

        
class TriggerClearCustomer(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/customer/init-clear-customer'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        merchant_key=request.args.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
    
class InitClearCustomer(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitResetCustomerMembership")
    
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_key)
            count = Customer.count_merchant_customer(merchant_acct)
        
        return count
    
    def get_task_batch_size(self):
        return 1
    
    def get_task_url(self):
        return '/maint/customer/clear-customer'
    
    def get_task_queue(self):
        return 'test'
    
    
    def get_data_payload(self):
        merchant_key=request.get_json().get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteClearCustomer(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteResetCustomerKPI")
    
        with db_client.context():
            merchant_acct               = MerchantAcct.fetch(merchant_key)
            (result, next_cursor)       = Customer.list_merchant_customer(merchant_acct, offset, limit, start_cursor, return_with_cursor=True)
            
            if result:
                
                for customer_details in result:
                    
                    delete_customer(customer_details)
                    
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/customer/clear-customer' 

    def get_data_payload(self):
        merchant_key=request.get_json().get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }        


class TriggerUpdateCustomer(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/customer/init-update-customer'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        return {
            }    
    
class InitUpdateCustomer(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        
        
        db_client = create_db_client(caller_info="InitUpdateCustomer")
    
        with db_client.context():
            count = Customer.count()
        
        logger.debug('total customer count=%s', count)
        
        return count
    
    def get_task_batch_size(self):
        return 20
    
    def get_task_url(self):
        return '/maint/customer/update-customer'
    
    def get_task_queue(self):
        return 'test'
    
    
class ExecuteUpdateCustomer(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteResetCustomerKPI")
    
        with db_client.context():
            (result, next_cursor) = Customer.list_all(offset=offset, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
            for customer in result:
                user_acct = customer.registered_user_acct
                logger.debug('user_acct=%s', user_acct)
                if user_acct:
                    customer.referral_code = user_acct.referral_code  
                    customer.put()
                
                    
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/customer/update-customer' 

@customer_maintenance_setup_bp.route('/<customer_key>/delete', methods=['get'])
def delete_customer_get(customer_key):
    db_client = create_db_client(caller_info="delete_customer")
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            delete_customer(customer)
            
    return 'Deleted when %s' % datetime.now(), 200

@customer_maintenance_setup_bp.route('/<customer_key>/flush-tier-reward', methods=['get'])
def flush_customer_tier_reward(customer_key):
    db_client = create_db_client(caller_info="flush_customer_tier_reward")
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            CustomerEntitledTierRewardSummary.delete_all_by_customer(customer)
            
    return 'Deleted customer tier reward summary when %s' % datetime.now(), 200
    

@customer_maintenance_setup_bp.route('/<customer_key>/create-membership-upstream', methods=['get'])
def create_customer_membership_upstream(customer_key):
    db_client = create_db_client(caller_info="create_customer_membership_upstream")
    with db_client.context():
        customer_acct = Customer.fetch(customer_key)
        customer_membership_list = CustomerMembership.list_by_customer(customer_acct)
        for customer_membership in customer_membership_list: 
            create_customer_membership_upstream_for_merchant(customer_membership)
        
    return jsonify(customer_acct.memberships_list)  
    
customer_maintenance_setup_bp_api.add_resource(TriggerResetCustomerKPI,   '/trigger-reset-customer-kpi')
customer_maintenance_setup_bp_api.add_resource(InitResetCustomerKPI,   '/init-reset-customer-kpi')
customer_maintenance_setup_bp_api.add_resource(ExecuteResetCustomerKPI,   '/reset-customer-kpi')

customer_maintenance_setup_bp_api.add_resource(TriggerImportCustomerMembershipUpstream,   '/trigger-import-customer-membership-upstream')
customer_maintenance_setup_bp_api.add_resource(InitImportCustomerMembershipUpstream,   '/init-import-customer-membership-upstream')
customer_maintenance_setup_bp_api.add_resource(ExecuteImportCustomerMembershipUpstream,   '/import-customer-membership-upstream')

customer_maintenance_setup_bp_api.add_resource(TriggerUpdateCustomerTransaaction,   '/trigger-update-customer-transation')
customer_maintenance_setup_bp_api.add_resource(InitUpdateCustomerTransaaction,   '/init-update-customer-transation')
customer_maintenance_setup_bp_api.add_resource(ExecuteUpdateCustomerTransaaction,   '/update-customer-transation')

customer_maintenance_setup_bp_api.add_resource(TriggerCreateCustomerUpstream,   '/trigger-create-customer-upstream')
customer_maintenance_setup_bp_api.add_resource(InitCreateCustomerUpstream,   '/init-create-customer-upstream')
customer_maintenance_setup_bp_api.add_resource(ExecuteCreateCustomerUpstream,   '/create-customer-upstream')

customer_maintenance_setup_bp_api.add_resource(TriggerClearCustomer,   '/trigger-clear-customer')
customer_maintenance_setup_bp_api.add_resource(InitClearCustomer,   '/init-clear-customer')
customer_maintenance_setup_bp_api.add_resource(ExecuteClearCustomer,   '/clear-customer')

customer_maintenance_setup_bp_api.add_resource(TriggerUpdateCustomer,   '/trigger-update-customer')
customer_maintenance_setup_bp_api.add_resource(InitUpdateCustomer,   '/init-update-customer')
customer_maintenance_setup_bp_api.add_resource(ExecuteUpdateCustomer,   '/update-customer')


