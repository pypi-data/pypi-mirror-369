'''
Created on 20 May 2021

@author: jacklok
'''
from google.cloud import ndb
from flask import Blueprint, render_template, url_for, request, jsonify, abort
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.string_util import is_empty, is_not_empty
from trexmodel.utils.model.model_util import create_db_client
#from trexmodel import conf as model_conf, program_conf
import logging
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher, CustomerEntitledReward,\
    CustomerEntitledTierRewardSummary
from trexmodel.models.datastore.customer_model_helpers import update_reward_summary_with_new_reward
from trexprogram.reward_program.reward_program_factory import sort_entitled_voucher_summary
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership, CustomerTierMembership
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
from trexmodel.models.datastore.program_models import MerchantProgram,\
    MerchantTierRewardProgram
from trexmodel.models.datastore.membership_models import MerchantMembership,\
    MerchantTierMembership
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexmodel.models.datastore.ndb_models import BaseNModel
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexmodel.models.datastore.helper.reward_transaction_helper import update_transaction_all_entitled_reward_summary,\
    update_customer_all_entitled_reward_summary,\
    update_customer_entitled_reward_summary, update_customer_prepaid_summary,\
    update_customer_entitled_voucher_summary
from trexlib.utils.common.date_util import to_day_of_year
from datetime import datetime
from dateutil.relativedelta import relativedelta
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from dns.rdataclass import NONE
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexconf import program_conf, conf

dev_tools_bp = Blueprint('dev_tools_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/debug'
                     )

logger = logging.getLogger('debug')

'''
Blueprint settings here
'''
@dev_tools_bp.context_processor
def debug_tools_bp_inject_settings():
    return dict(
                side_menu_group_name    = "debug"
                )

@dev_tools_bp.route('/', methods=['GET'])
@dev_tools_bp.route('/dev-tools', methods=['GET'])
def show_dev_tools():
    return render_template("debug/dev_tools.html", 
                           #merchant program
                           show_program_configuration_url                                   = url_for('reward_program_setup_bp.show_program_configuration'),
                           
                           #certain merchant
                           show_merchant_details_url                                        = url_for('dev_tools_bp.show_merchant_acct_details'),
                           update_merchant_published_program_configuration_url              = url_for('dev_tools_bp.update_merchant_published_progam'),
                           
                           #all merchant
                           update_all_merchants_published_program_configuration_url         = url_for('dev_tools_bp.update_all_merchants_published_progam'),
                           
                           #certain customer
                           update_customer_all_reward_summary_url                           = url_for('dev_tools_bp.update_customer_all_reward_summary'),
                           update_customer_entitled_reward_summary_url                      = url_for('dev_tools_bp.submit_update_customer_entitled_reward_summary'),
                           update_customer_entitled_voucher_summary_url                     = url_for('dev_tools_bp.submit_update_customer_entitled_voucher_summary'),
                           update_customer_prepaid_summary_url                              = url_for('dev_tools_bp.submit_update_customer_prepaid_summary'),
                           show_customer_all_reward_summary_url                             = url_for('dev_tools_bp.show_customer_all_reward_summary'),
                           flush_customer_all_transaction_url                               = url_for('dev_tools_bp.flush_customer_all_transaction'),
                           flush_merchant_all_transaction_url                               = url_for('dev_tools_bp.flush_merchant_all_transaction'),
                           flush_merchant_all_customer_url                                  = url_for('dev_tools_bp.flush_merchant_all_customer'),
                           
                           #all customers
                           update_all_customer_entitled_voucher_summary_url                 = url_for('dev_tools_bp.update_all_customer_entitled_voucher_summary'),
                           update_all_customer_all_reward_summary_url                       = url_for('dev_tools_bp.update_all_customer_all_reward_summary'),
                           flush_all_customers_reward_and_voucher_summary_url               = url_for('dev_tools_bp.flush_all_customers_reward_and_voucher_summary'),
                           flush_and_update_all_customers_entitled_voucher_summary_url      = url_for('dev_tools_bp.update_all_customers_entitled_voucher_summary'),
                           
                           flush_and_update_transaction_reward_summary_url                  = url_for('dev_tools_bp.flush_and_update_transaction_reward_summary'),
                           
                           show_upstream_data_url                                           = url_for('dev_tools_bp.read_upstream_data_content'),
                           read_model_content_url                                           = url_for('dev_tools_bp.read_model_data_content'),
                           flush_all_transaction_and_reward_url                             = url_for('dev_tools_bp.flush_all_transaction_and_reward'),
                           
                           show_full                                                        = True,
                           )
    
    
def update_transaction_reward_summary(customer_transaction):
    db_client = create_db_client(caller_info="update_transaction_reward_summary")
    
    transaction_id      = customer_transaction.transaction_id
    
    with db_client.context():
        
        entitled_vouchers_list          = CustomerEntitledVoucher.list_by_transaction_id(transaction_id)
        
        entitled_point_details_list     = CustomerPointReward.list_by_transaction_id(transaction_id)
        
        entitled_stamp_details_list     = CustomerStampReward.list_by_transaction_id(transaction_id)      
        
        entitled_reward_summary         = {}
        entitled_voucher_summary        = {}
        
        for reward in  entitled_point_details_list:
            entiteld_reward_details = reward.to_reward_summary()
            entitled_reward_summary = update_reward_summary_with_new_reward(entitled_reward_summary, entiteld_reward_details)
            
        for reward in  entitled_stamp_details_list:
            entiteld_reward_details = reward.to_reward_summary()
            entitled_reward_summary = update_reward_summary_with_new_reward(entitled_reward_summary, entiteld_reward_details)
         
        logger.debug('entitled_reward_summary=%s', entitled_reward_summary) 
            
        for v in entitled_vouchers_list:
            voucher_key         = str(v.entitled_voucher_key, 'utf-8')
            effective_date      = v.effective_date
            expiry_date         = v.expiry_date
            effective_date_str  = effective_date.strftime('%d-%m-%Y')
            expiry_date_str     = expiry_date.strftime('%d-%m-%Y') 
            
            voucher_summary_key = voucher_key + '|' + effective_date_str + '|' + expiry_date_str
            
            voucher_item_details = entitled_voucher_summary.get(voucher_summary_key)
            if voucher_item_details:
                entitled_voucher_summary[voucher_summary_key]['amount'] += 1
            else:
                entitled_voucher_summary[voucher_summary_key] = {
                                                                    'voucher_key'   : voucher_key,
                                                                    'effective_date': effective_date_str,
                                                                    'expiry_date'   : expiry_date_str,
                                                                    'amount'        : 1,
                                                                }
        
        if entitled_voucher_summary:
            entitled_voucher_summary = sort_entitled_voucher_summary(entitled_voucher_summary)
        
        customer_transaction.entitled_reward_summary    = entitled_reward_summary
        customer_transaction.entitled_voucher_summary   = entitled_voucher_summary
        
        customer_transaction.put()
        
        transaction_details = customer_transaction.to_dict()
    
    return transaction_details


@dev_tools_bp.route('/flush-and-update-transaction-reward-summary', methods=['get'])
@request_values
def flush_and_update_transaction_reward_summary(request_values):
    transaction_id = request_values.get('transaction_id')
    logger.debug('--- submit flush_and_update_transaction_reward_summary ---')
    logger.debug('transaction_id=%s', transaction_id)
    db_client = create_db_client(caller_info="flush_and_update_transaction_reward_summary")
    
    with db_client.context():
        customer_transaction    = update_transaction_all_entitled_reward_summary(transaction_id)
        transaction_details     = customer_transaction.to_dict()
    
    return jsonify(transaction_details)   

@dev_tools_bp.route('/flush-and-update-all-transaction-reward-summary', methods=['get'])
def flush_and_update_all_transaction_reward_summary():
    logger.debug('--- submit flush_and_update_all_transaction_reward_summary ---')
    
    db_client = create_db_client(caller_info="flush_and_update_all_transaction_reward_summary")
    
    with db_client.context():
        customer_transactions_list    = CustomerTransaction.list_all()
    
    
    for ct in customer_transactions_list:
        update_transaction_reward_summary(ct)
    
    return '',200

@dev_tools_bp.route('/update-all-transaction', methods=['get'])
def update_all_transaction():
    logger.debug('--- update_all_transaction ---')
    
    db_client = create_db_client(caller_info="update_all_transaction")
    
    with db_client.context():
        customer_transactions_list    = CustomerTransaction.list_all()
    
    
        for ct in customer_transactions_list:
            ct.transact_timestamp = datetime.timestamp(ct.transact_datetime)
            ct.put()
    
    return 'Done',200

@dev_tools_bp.route('/update-merchant-published-voucher/<merchant_acct_key>', methods=['get'])
def update_merchant_published_voucher(merchant_acct_key):
    logger.debug('--- update_merchant_published_voucher ---')
    
    db_client = create_db_client(caller_info="update_all_transaction")
    
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(merchant_acct_key)
        published_vouchers_list = MerchantVoucher.list_latest_by_merchant_account(merchant_acct)
        
        merchant_published_voucher_configuration_list = []
    
        for voucher in published_vouchers_list:
            voucher_configuration = voucher.to_voucher_configuration()
            merchant_published_voucher_configuration_list.append(voucher_configuration)
        
        merchant_acct.published_voucher_configuration = {
                                                'vouchers'  : merchant_published_voucher_configuration_list,
                                                'count'     : len(merchant_published_voucher_configuration_list),
                                                }     
        merchant_acct.put()
        
    return 'Done',200

@dev_tools_bp.route('/show-merchant-published-voucher/<merchant_acct_key>', methods=['get'])
def show_merchant_published_voucher(merchant_acct_key):
    logger.debug('--- update_merchant_published_voucher ---')
    
    db_client = create_db_client(caller_info="update_all_transaction")
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(merchant_acct_key)
        published_vouchers_configuration = merchant_acct.published_voucher_configuration
        
    return jsonify(published_vouchers_configuration)

@dev_tools_bp.route('/show-merchant-tier-reward-tiers/<program_key>', methods=['get'])
def show_merchant_tier_reward_tiers(program_key):
    logger.debug('--- show_merchant_tier_reward_tiers ---')
    
    db_client = create_db_client(caller_info="update_all_transaction")
    tier_settings_list = []
    with db_client.context():
        program = MerchantTierRewardProgram.fetch(program_key)
        if program:
            tier_settings_list = program.program_tiers
        
        
    return jsonify(tier_settings_list)

@dev_tools_bp.route('/list-customer-transaction-by-transact-daterange/<customer_key>', methods=['get'])
@request_values
def list_transaction_by_transact_daterange(request_values, customer_key):
    logger.debug('--- submit list_transaction_by_transact_daterange ---')
    
    db_client = create_db_client(caller_info="list_transaction_by_transact_daterange")
    
    customer_transactions_list = []
    
    with db_client.context():
        daterange_type      = request_values.get('daterange_type')
        daterange_value     = request_values.get('daterange_value') or 1
        now                 = datetime.utcnow()
        if is_not_empty(customer_key):
            customer_acct = Customer.fetch(customer_key)
            if customer_acct:
                transact_timestamp_to = datetime.timestamp(now)
                
                daterange_value = int(daterange_value,10)
                
                if daterange_type == program_conf.REWARD_LIMIT_TYPE_BY_MONTH:
                    transact_timestamp_from = datetime.timestamp(now - relativedelta(months=daterange_value))
                elif daterange_type == program_conf.REWARD_LIMIT_TYPE_BY_WEEK:
                    transact_timestamp_from = datetime.timestamp(now - relativedelta(weeks=daterange_value))
                elif daterange_type == program_conf.REWARD_LIMIT_TYPE_BY_DAY:
                    transact_timestamp_from = datetime.timestamp(now - relativedelta(days=daterange_value))     
                
                result    = CustomerTransaction.list_customer_transaction_by_transact_timestamp(customer_acct, transact_timestamp_from, transact_timestamp_to)
                
                for r in result:
                    customer_transactions_list.append(r.to_dict())
    
        
    
    return jsonify(customer_transactions_list)


@dev_tools_bp.route('/flush-all-transaction-and-rewards', methods=['get'])
def flush_all_transaction_and_reward():
    logger.debug('--- submit flush_all_transaction_and_reward ---')
    
    db_client = create_db_client(caller_info="flush_all_transaction_and_reward")
    
    with db_client.context():
        customer_transactions_list      = CustomerTransaction.list_all()
        entitled_point_details_list     = CustomerPointReward.list_all()
        entitled_stamp_details_list     = CustomerStampReward.list_all()
        entitled_voucher_list           = CustomerEntitledReward.list_all()
        
        transaction_count       = len(customer_transactions_list)
        point_reward_count      = len(entitled_point_details_list)
        stamp_reward_count      = len(entitled_stamp_details_list)
        voucher_reward_count    = len(entitled_voucher_list)
        
        #for t in customer_transactions_list:
        #    t.delete()
    
        #for reward in  entitled_point_details_list:
        #    reward.delete()
            
        #for reward in  entitled_stamp_details_list:
        #    reward.delete()
            
        #for voucher in  entitled_stamp_details_list:
        #    voucher.delete()    
        if customer_transactions_list:    
            ndb.delete_multi(customer_transactions_list)
        
        if entitled_point_details_list:    
            ndb.delete_multi(entitled_point_details_list)
            
        if entitled_stamp_details_list:    
            ndb.delete_multi(entitled_stamp_details_list)
            
        if entitled_voucher_list:    
            ndb.delete_multi(entitled_voucher_list)            
    
    return 'flushed %d transactions, %d point rewards, %d stamp rewards, %d vouchers'%(transaction_count, point_reward_count, stamp_reward_count, voucher_reward_count)  ,200

@dev_tools_bp.route('/flush-all-transaction-and-rewards/<customer_key>', methods=['get'])
def flush_all_transaction_and_reward_for_customer(customer_key):
    logger.debug('--- submit flush_all_transaction_and_reward ---')
    
    db_client = create_db_client(caller_info="flush_all_transaction_and_reward")
    
    with db_client.context():
        customer_acct   = Customer.fetch(customer_key)
        customer_transactions_list      = CustomerTransaction.list_customer_transaction(customer_acct, limit=99999)
        entitled_point_details_list     = CustomerPointReward.list_all_by_customer(customer_acct)
        entitled_stamp_details_list     = CustomerStampReward.list_all_by_customer(customer_acct)
        entitled_voucher_list           = CustomerEntitledVoucher.list_all_by_customer(customer_acct)
        #prepaid_list                    = CustomerPrepaidReward.list_all_by_customer(customer_acct)
        
        transaction_count       = len(customer_transactions_list)
        point_reward_count      = len(entitled_point_details_list)
        stamp_reward_count      = len(entitled_stamp_details_list)
        voucher_reward_count    = len(entitled_voucher_list)
        
        if customer_transactions_list:  
            for t in customer_transactions_list:  
                t.delete()
        
        if entitled_point_details_list:    
            for t in entitled_point_details_list:  
                t.delete()
            
        if entitled_stamp_details_list:    
            for t in entitled_stamp_details_list:  
                t.delete()
            
        if entitled_voucher_list:    
            for t in entitled_voucher_list:  
                t.delete()            
    
    return 'flushed %d transactions, %d point rewards, %d stamp rewards, %d vouchers'%(transaction_count, point_reward_count, stamp_reward_count, voucher_reward_count)  ,200     

@dev_tools_bp.route('/show-customer-all-reward-summary', methods=['get'])
@request_values
def show_customer_all_reward_summary(request_values):
    
    logger.debug('--- submit show_customer_entitled_reward ---')
    
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="show_customer_entitled_reward")
    
    with db_client.context():
        customer    = Customer.fetch(customer_key)
        
    
    return jsonify(
                    {
                    'reward_summary'            : customer.reward_summary,
                    'prepaid_summary'           : customer.prepaid_summary,
                    'entitled_voucher_summary'  : customer.entitled_voucher_summary
                    }
                )


@dev_tools_bp.route('/update-all-customer-all-reward-summary', methods=['get'])
def update_all_customer_all_reward_summary():
    logger.debug('--- submit update_all_customer_all_reward_summary ---')
    
    
    
    db_client = create_db_client(caller_info="update_all_customer_all_reward_summary")
    
    with db_client.context():
        customer_list = Customer.list_all()
        for customer in customer_list:
            if customer:
                update_customer_all_entitled_reward_summary(customer)
    
    return 'Done', 200


@dev_tools_bp.route('/update-all-customer-all-reward-summary', methods=['get'])
@request_values
def update_all_customer_reward_summary(request_values):
    logger.debug('--- submit update_customer_all_reward_summary ---')
    
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="update_customer_all_reward_summary")
    
    with db_client.context():
        customer    = Customer.fetch(customer_key)
        if customer:
            update_customer_all_entitled_reward_summary(customer)
    
    if customer:    
        return jsonify({
                        'reward_summary'            : customer.reward_summary,
                        'prepaid_summary'           : customer.prepaid_summary,
                        'entitled_voucher_summary'  : customer.entitled_voucher_summary,
                        }) 
    else:
        return 'Invalid customer key', 400
    
@dev_tools_bp.route('/update-customer-entitled-voucher-summary', methods=['get'])
@request_values
def update_a_customer_entitled_voucher_summary(request_values):
    logger.debug('--- submit update_a_customer_entitled_voucher_summary ---')
    
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="update_a_customer_entitled_voucher_summary")
    
    with db_client.context():
        customer    = Customer.fetch(customer_key)
        if customer:
            update_customer_entitled_reward_summary(customer)
    
    if customer:    
        return jsonify({
                        'entitled_voucher_summary'  : customer.entitled_voucher_summary,
                        }) 
    else:
        return 'Invalid customer key', 400    
    
@dev_tools_bp.route('/update-customer-all-reward-summary', methods=['get'])
@request_values
def update_customer_all_reward_summary(request_values):
    logger.debug('--- submit update_customer_all_reward_summary ---')
    
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="update_customer_all_reward_summary")
    
    with db_client.context():
        customer    = Customer.fetch(customer_key)
        if customer:
            update_customer_all_entitled_reward_summary(customer)
    
    if customer:    
        return jsonify({
                        'reward_summary'            : customer.reward_summary,
                        'prepaid_summary'           : customer.prepaid_summary,
                        'entitled_voucher_summary'  : customer.entitled_voucher_summary,
                        }) 
    else:
        return 'Invalid customer key', 400  
    
@dev_tools_bp.route('/update-customer-entitled-reward-summary', methods=['get'])
@request_values
def submit_update_customer_entitled_reward_summary(request_values):
    logger.debug('--- submit update_customer_all_reward_summary ---')
    
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="update_customer_entitled_reward_summary")
    
    with db_client.context():
        customer    = Customer.fetch(customer_key)
        if customer:
            update_customer_entitled_reward_summary(customer)
    
    if customer:    
        return jsonify({
                        'reward_summary'            : customer.reward_summary,
                        
                        }) 
    else:
        return 'Invalid customer key', 400 
    
@dev_tools_bp.route('/update-customer-prepaid-summary', methods=['get'])
@request_values
def submit_update_customer_prepaid_summary(request_values):
    logger.debug('--- submit_update_customer_prepaid_summary ---')
    
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="submit_update_customer_prepaid_summary")
    
    with db_client.context():
        customer    = Customer.fetch(customer_key)
        if customer:
            update_customer_prepaid_summary(customer)
    
    if customer:    
        return jsonify({
                        'reward_summary'            : customer.prepaid_summary,
                        
                        }) 
    else:
        return 'Invalid customer key', 400            

@dev_tools_bp.route('/update-customer-entitled-voucher-summary', methods=['get'])
@request_values
def submit_update_customer_entitled_voucher_summary(request_values):
    logger.debug('--- submit update_customer_entitled_voucher_summary ---')
    
    customer_key = request_values.get('customer_key')
    db_client = create_db_client(caller_info="update_customer_entitled_voucher_summary")
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
    
        update_customer_entitled_voucher_summary(customer)
    
    if customer:    
        return jsonify({
                        'entitled_voucher_summary'            : customer.entitled_voucher_summary,
                        
                        }) 
    
    else:
        return 'Invalid customer key', 400



@dev_tools_bp.route('/flush-and-update-all-customers-entitled-voucher-summary', methods=['get'])
def update_all_customers_entitled_voucher_summary():
    logger.debug('--- submit update_all_customers_entitled_voucher_summary ---')
    
    db_client = create_db_client(caller_info="update_all_customers_entitled_voucher_summary")
    
    with db_client.context():
        customers_list    = Customer.list_all()
    
        for customer in customers_list:
            CustomerEntitledVoucher.update_customer_entiteld_voucher_summary(customer)
    
    return 'Flushed successfully',200 

@dev_tools_bp.route('/flush-all-customer-reward-summary', methods=['get'])
def flush_all_customer_reward_summary():
    logger.debug('--- submit flush_all_customer_reward_summary ---')
    
    db_client = create_db_client(caller_info="flush_all_customer_reward_summary")
    
    with db_client.context():
        customers_list      = Customer.list_all()
        customers_count     = len(customers_list)
        logger.debug('customer count=%d', customers_count)
        for c in customers_list:
            c.reward_summary = {}
            c.put() 
    
    return 'Flushed %d successfully' % customers_count, 200 

@dev_tools_bp.route('/flush-all-customer-entitled-voucher-summary', methods=['get'])
def flush_all_customer_entitled_voucher_summary():
    logger.debug('--- submit flush_all_customer_entitled_voucher_summary ---')
    
    db_client = create_db_client(caller_info="flush_all_customer_entitled_voucher_summary")
    
    with db_client.context():
        customers_list      = Customer.list_all()
        customers_count     = len(customers_list)
        logger.debug('customer count=%d', customers_count)
        for c in customers_list:
            c.entitled_voucher_summary = {}
            c.put() 
    
    return 'Flushed %d successfully' % customers_count, 200 

@dev_tools_bp.route('/flush-all-customers-reward-and-voucher-summary', methods=['get'])
def flush_all_customers_reward_and_voucher_summary():
    logger.debug('--- submit flush_all_customers_reward_and_voucher_summary ---')
    
    db_client = create_db_client(caller_info="flush_all_customers_reward_and_voucher_summary")
    
    with db_client.context():
        customers_list      = Customer.list_all()
        customers_count     = len(customers_list)
        logger.debug('customer count=%d', customers_count)
        for c in customers_list:
            __flush_customer_all_transaction(c) 
    
    return 'Flushed %d successfully' % customers_count, 200    

def __flush_customer_all_transaction(customer):
    @model_transactional(desc = "__flush_customer_all_transaction")
    def __start_transaction(customer):
        customer.reward_summary                     = {}
        customer.prepaid_summary                    = {}
        customer.entitled_voucher_summary           = {}
        customer.entitled_birthday_reward_summary   = {}
        customer.entitled_membership_reward_summary = {}
        
        customer.tags_list                          = []
        customer.memberships_list                   = []
        
        customer.tier_membership                    = None
        customer.previous_tier_membership           = None
        
        customer.last_transact_datetime             = None
        customer.previous_transact_datetime         = None
        customer.last_redeemed_datetime             = None
        
        customer.kpi_summary = {
                                'total_accumulated_point'   : 0,
                                'total_accumulated_prepaid' : 0,
                                'total_accumulated_stamp'   : 0,
                                'total_accumulated_topup'   : .0,
                                'total_transact_amount'     : .0
                                }
        
        
        customer.put() 
    
        customer_transactions_list =  CustomerTransaction.list_customer_transaction(customer, offset=0, limit=10000)
        
        for t in customer_transactions_list:
            t.delete()
        
        customer_redemptions_list =  CustomerRedemption.list_customer_redemption(customer, offset=0, limit=10000)
        
        for t in customer_redemptions_list:
            t.delete()
            
        customer_vouchers_list =  CustomerEntitledVoucher.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_vouchers_list:
            t.delete()
            
        customer_points_list =  CustomerPointReward.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_points_list:
            t.delete()
            
        customer_stamps_list =  CustomerStampReward.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_stamps_list:
            t.delete()
            
        customer_prepaids_list =  CustomerPrepaidReward.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_prepaids_list:
            t.delete()
            
        customer_membership_list =  CustomerMembership.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_membership_list:
            t.delete()
            
        
        customer_tier_membership_list =  CustomerTierMembership.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_tier_membership_list:
            t.delete()
            
        customer_tier_reward_summaries_list =  CustomerEntitledTierRewardSummary.list_all_by_customer(customer, offset=0, limit=10000)
        
        for t in customer_tier_reward_summaries_list:
            t.delete()             
            
    __start_transaction(customer)   
    

def _flush_merchant_all_customer(merchant_acct):
    
    customers_list = Customer.list_merchant_customer(merchant_acct, offset=0, limit=9999)
    
    for c in customers_list:
        registered_user = c.registered_user_acct
        registered_user.delete()
        c.delete()
    

@dev_tools_bp.route('/flush-customer-all-transaction', methods=['get'])
@request_values
def flush_customer_all_transaction(request_values):
    logger.debug('--- submit flush_customer_all_transaction ---')
    
    db_client = create_db_client(caller_info="flush_customer_all_transaction")
    
    customer_key = request_values.get('customer_key')
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        
        __flush_customer_all_transaction(customer)
        
    
    return 'Flushed %s successfully on %s' % (customer.name, datetime.now()), 200    

@dev_tools_bp.route('/flush-merchant-all-transaction', methods=['get'])
@request_values
def flush_merchant_all_transaction(request_values):
    logger.debug('--- submit flush_merchant_all_transaction ---')
    
    db_client = create_db_client(caller_info="flush_merchant_all_transaction")
    
    merchant_key = request_values.get('merchant_key')
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        customers_list = Customer.list_merchant_customer(merchant_acct)
        
        for c in customers_list:
            __flush_customer_all_transaction(c)
        
    
    return 'Flushed %s all transaction successfully on %s' % (merchant_acct.company_name, datetime.now()), 200  

@dev_tools_bp.route('/flush-merchant-all-customer', methods=['get'])
@request_values
def flush_merchant_all_customer(request_values):
    logger.debug('--- submit flush_merchant_all_customer ---')
    
    db_client = create_db_client(caller_info="flush_merchant_all_customer")
    
    merchant_key = request_values.get('merchant_key')
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        _flush_merchant_all_customer(merchant_acct)
        
    
    return 'Flushed %s all customer successfully on %s' % (merchant_acct.company_name, datetime.now()), 200    


@dev_tools_bp.route('/update-all-customers', methods=['get'])
def update_all_customers():
    logger.debug('--- submit update_all_customers ---')
    
    db_client = create_db_client(caller_info="update_all_customers")
    
    with db_client.context():
        customers_list      = Customer.list_all()
        customers_count     = len(customers_list)
        logger.debug('customer count=%d', customers_count)
        for c in customers_list:
            u = c.registered_user_acct
            if c.birth_date:
                birth_day_in_year   = to_day_of_year(c.birth_date)
                c.birth_day_in_year = birth_day_in_year
                u.birth_day_in_year = birth_day_in_year
            
            c.put() 
            u.put()
    
    return 'Flushed %d successfully' % customers_count, 200    


@dev_tools_bp.route('/show-merchant-acct-details', methods=['GET'])
@request_values
def show_merchant_acct_details(request_values): 
    merchant_acct_key       = request_values.get('merchant_acct_key')
    if is_empty(merchant_acct_key):
    
        logged_in_merchant_user = get_loggedin_merchant_user_account()
    
        db_client               = create_db_client(caller_info="show_merchant_acct_key")
        with db_client.context():
            merchant_acct           = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
            #merchant_acct           = logged_in_merchant_user.merchant_acct.to_dict()
    else:
        db_client               = create_db_client(caller_info="show_merchant_acct_key")
        with db_client.context():
            merchant_acct           = MerchantAcct.fetch(merchant_acct_key).to_dict()
    
    return jsonify(merchant_acct)

@dev_tools_bp.route('/show-user-details', methods=['GET'])
@request_values
def show_user_details(request_values): 
    merchant_user_key       = request_values.get('merchant_user_key')
    
    logger.debug('merchant_user_key=%s', merchant_user_key)
    
    if is_empty(merchant_user_key):
    
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        return jsonify(logged_in_merchant_user)
    else:
        db_client               = create_db_client(caller_info="show_user_details")
        with db_client.context():
            merchant_user           = MerchantUser.fetch(merchant_user_key)
        
        if merchant_user:    
            return jsonify(merchant_user.to_dict())
        else:
            return ('',400)

@dev_tools_bp.route('/update-published-program', methods=['GET'])
@request_values
def update_merchant_published_progam(request_values): 
    
    merchant_acct_key = request_values.get('merchant_acct_key')
    
    db_client               = create_db_client(caller_info="update_merchant_published_progam")
    
    if is_empty(merchant_acct_key):
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        with db_client.context():
            merchant_acct           = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
    
    else:
        with db_client.context():
            merchant_acct           = MerchantAcct.fetch(merchant_acct_key)
    
    
    with db_client.context():
        published_programs_list = []
        merchant_programs_list           = MerchantProgram.list_by_merchant_account(merchant_acct)
        for p in merchant_programs_list:
            if p.is_published and p.enabled:
                published_programs_list.append(p.to_program_configuration())
        
        merchant_acct.published_program_configuration = {
                                                        'programs'  : published_programs_list,
                                                        'count'     : len(published_programs_list)
                                                        }
        merchant_acct.put()
        
    return jsonify(merchant_acct.published_program_configuration)

@dev_tools_bp.route('/update-all-merchants-published-program', methods=['GET'])
def update_all_merchants_published_progam(): 
    
    db_client               = create_db_client(caller_info="update_all_merchants_published_progam")
    updated_merchant_programs_list = []
    with db_client.context():
        
        merchant_accts_list  = MerchantAcct.list(limit = conf.MAX_FETCH_RECORD)
        
        for merchant_acct in merchant_accts_list:
        
            published_programs_list = []
            merchant_programs_list           = MerchantProgram.list_by_merchant_account(merchant_acct)
            
            for p in merchant_programs_list:
                if p.is_published:
                    published_programs_list.append(p.to_program_configuration())
                
                if p.giveaway_method == 'auto':
                    p.giveaway_method = 'system'
                    p.put()
            
            updated_merchant_programs_list.append(published_programs_list)
                
            merchant_acct.published_program_configuration = {
                                                            'programs'  : published_programs_list,
                                                            'count'     : len(published_programs_list)
                                                            }
            
            merchant_acct.put()
        
    #return 'Update %d' % update_count, 200
    return jsonify(updated_merchant_programs_list)

@dev_tools_bp.route('/update-all-merchants-api-key', methods=['GET'])
def update_all_merchants_app_key(): 
    
    db_client               = create_db_client(caller_info="update_all_merchants_app_key")
    
    with db_client.context():
        
        merchant_accts_list  = MerchantAcct.list(limit = conf.MAX_FETCH_RECORD)
        
        update_count = len(merchant_accts_list)
        
        for merchant_acct in merchant_accts_list:
            merchant_acct.update_api_key()
        
    return 'Update %d' % update_count, 200

@dev_tools_bp.route('/update-all-customer-entitled-voucher-summary', methods=['GET'])
def update_all_customer_entitled_voucher_summary(): 
    
    db_client               = create_db_client(caller_info="update_all_customer_entitled_voucher_summary")
    
    with db_client.context():
        customer_list = Customer.list_all() 
        
        for customer in customer_list:
            customer_entitled_vouchers_list     = CustomerEntitledVoucher.list_by_customer(customer)
            customer_entitled_voucher_summary   = {}
            
            for customer_voucher in customer_entitled_vouchers_list:
                voucher_key         = customer_voucher.entitled_voucher_key
                voucher_details     = customer_voucher.entitled_voucher_entity
                voucher_image_url   = voucher_details.image_public_url
                voucher_label       = voucher_details.label 
                
                #summary_key     = '%s-%s-%s' % (voucher_key, customer_voucher.effective_date.strftime('%d-%m-%Y'), customer_voucher.expiry_date.strftime('%d-%m-%Y'))
                summary_key             = voucher_key
                found_summary_details   = customer_entitled_voucher_summary.get(summary_key)
                
                voucher_redeem_info = {
                                        'redeem_code'       : customer_voucher.redeem_code,
                                        'effective_date'    : customer_voucher.effective_date.strftime('%d-%m-%Y'),
                                        'expiry_date'       : customer_voucher.expiry_date.strftime('%d-%m-%Y')
                                         
                                    }
                
                if found_summary_details:
                    found_summary_details['redeem_info_list'].append(voucher_redeem_info)
                else:
                    found_summary_details = {
                                                'image_url'         : voucher_image_url,
                                                'label'             : voucher_label,
                                                'key'               : voucher_key,
                                                'redeem_info_list'  : [
                                                                            voucher_redeem_info
                                                                        ]
                                            }
                customer_entitled_voucher_summary[summary_key] = found_summary_details
             
            customer.entitled_voucher_summary = customer_entitled_voucher_summary
            customer.put()  
                
                
        update_count = len(customer_list)

    return 'Update %d' % update_count, 200

@dev_tools_bp.route('/flush-and-update-merchant-acct-membership-configuration', methods=['GET'])
def flush_and_update_merchant_membership_configuration(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    
    db_client               = create_db_client(caller_info="show_merchant_acct_key")
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
        memberships_list        = MerchantMembership.list_by_merchant_acct(merchant_acct)
        
        merchant_acct.flush_and_update_membership_configuration(memberships_list)
    
    return jsonify(merchant_acct.to_dict())

@dev_tools_bp.route('/flush-and-update-merchant-acct-tier-membership-configuration', methods=['GET'])
def flush_and_update_merchant_tier_membership_configuration(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    
    db_client               = create_db_client(caller_info="show_merchant_acct_key")
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
        memberships_list        = MerchantTierMembership.list_by_merchant_acct(merchant_acct)
        merchant_acct.flush_and_update_tier_membership_configuration(memberships_list)
    
    return jsonify(merchant_acct.to_dict())

@dev_tools_bp.route('/upstream/data-content')
@request_values
def read_upstream_data_content(request_values):
    
    upstream_data_key = request_values.get('upstream_data_key')
    
    logger.debug('upstream_data_key=%s', upstream_data_key)
    
    try:
        db_client = create_db_client(caller_info="read_upstream_data_content")
        with db_client.context():
            upstream_data = UpstreamData.fetch(upstream_data_key)
            
        if upstream_data:
            return jsonify(upstream_data.stream_content)
    except:
        logger.debug('Failed to fetch upstream data due to %s', get_tracelog())
    
    return 'Not found', 200

@dev_tools_bp.route('/model/data-content')
@request_values
def read_model_data_content(request_values):
    
    model_key = request_values.get('model_key')
    
    logger.debug('model_key=%s', model_key)
    
    try:
        db_client = create_db_client(caller_info="read_model_data_content")
        with db_client.context():
            model       = BaseNModel.fetch(model_key)
            classname   = model.__class__.__name__
            model_dict  = model.to_dict(deep_level=99)
            
        if model:
            return jsonify(
                {
                    'classname' : classname,
                    'datetime'  : datetime.now(),
                    'model_dict': model_dict
                    }
                )
    except:
        logger.debug('Failed to fetch model data due to %s', get_tracelog())
    
    return 'Not found', 200
