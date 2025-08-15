'''
Created on 4 Dec 2024

@author: jacklok
'''

from flask import Blueprint, request
from trexmodel.utils.model.model_util import create_db_client
import logging
from flask_restful import Api
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexlib.utils.string_util import is_not_empty, remove_dash
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_prepaid_upstream_for_merchant,\
    create_merchant_customer_reward_upstream_for_merchant
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher,\
    VoucherRewardDetailsForUpstreamData

customer_reward_maintenance_setup_bp = Blueprint('customer_reward_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/reward')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

customer_reward_maintenance_setup_bp_api = Api(customer_reward_maintenance_setup_bp)

class TriggerImportCustomerPrepaidRewardUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/reward/init-import-customer-prepaid-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        merchant_key        = request.args.get('merchant_key')
        
        if is_not_empty(merchant_key):
            merchant_key = remove_dash(merchant_key)
        
        return {
                'merchant_key'      : merchant_key,
            }    
    
class InitImportCustomerPrepaidRewardUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitImportCustomerPrepaidRewardUpstream")
    
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                count = CustomerPrepaidReward.count_by_merchant_acct(merchant_acct)
            else:
                count = CustomerPrepaidReward.count()
        
        return count
    
    def get_task_batch_size(self):
        return 100
    
    def get_task_url(self):
        return '/maint/reward/import-customer-prepaid-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }
    
class ExecuteImportCustomerPrepaidRewardUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteImportCustomerPrepaidRewardUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                (result, next_cursor) = CustomerPrepaidReward.list_by_merchant_acct(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor)
            else:
                (result, next_cursor) = CustomerPrepaidReward.list_all(offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
                
            
            for prepaid_reward in result:
                transaction_id      = prepaid_reward.transaction_id
                transaction_details = CustomerTransaction.get_by_transaction_id(transaction_id)
                
                if transaction_details:
                    create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, prepaid_reward)
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, prepaid_reward)
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/reward/import-customer-prepaid-reward-upstream' 

    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }  
        
class TriggerImportCustomerPointRewardUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/reward/init-import-customer-point-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        merchant_key        = request.args.get('merchant_key')
        
        if is_not_empty(merchant_key):
            merchant_key = remove_dash(merchant_key)
        
        return {
                'merchant_key'      : merchant_key,
            }    
    
class InitImportCustomerPointRewardUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitImportCustomerPointRewardUpstream")
    
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                count = CustomerPointReward.count_by_merchant_acct(merchant_acct)
            else:
                count = CustomerPointReward.count()
        
        return count
    
    def get_task_batch_size(self):
        return 100
    
    def get_task_url(self):
        return '/maint/reward/import-customer-point-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }
    
class ExecuteImportCustomerPointRewardUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteImportCustomerPointRewardUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                (result, next_cursor) = CustomerPointReward.list_by_merchant_acct(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor)
            else:
                (result, next_cursor) = CustomerPointReward.list_all(offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
                
            
            for reward in result:
                transaction_id      = reward.transaction_id
                transaction_details = CustomerTransaction.get_by_transaction_id(transaction_id)
                
                if transaction_details:
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, reward)
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/reward/import-customer-point-reward-upstream' 

    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }   
        
class TriggerImportCustomerStampRewardUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/reward/init-import-customer-stamp-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        merchant_key        = request.args.get('merchant_key')
        
        if is_not_empty(merchant_key):
            merchant_key = remove_dash(merchant_key)
        
        return {
                'merchant_key'      : merchant_key,
            }    
    
class InitImportCustomerStampRewardUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitImportCustomerStampRewardUpstream")
    
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                count = CustomerStampReward.count_by_merchant_acct(merchant_acct)
            else:
                count = CustomerStampReward.count()
        
        return count
    
    def get_task_batch_size(self):
        return 100
    
    def get_task_url(self):
        return '/maint/reward/import-customer-stamp-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }
    
class ExecuteImportCustomerStampRewardUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteImportCustomerStampRewardUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                (result, next_cursor) = CustomerStampReward.list_by_merchant_acct(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor)
            else:
                (result, next_cursor) = CustomerStampReward.list_all(offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
                
            
            for reward in result:
                transaction_id      = reward.transaction_id
                transaction_details = CustomerTransaction.get_by_transaction_id(transaction_id)
                
                if transaction_details:
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, reward)
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/reward/import-customer-stamp-reward-upstream' 

    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }                   

class TriggerImportCustomerEntitledVoucherRewardUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/reward/init-import-customer-entitled-voucher-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        merchant_key        = request.args.get('merchant_key')
        
        if is_not_empty(merchant_key):
            merchant_key = remove_dash(merchant_key)
        
        return {
                'merchant_key'      : merchant_key,
            }    
    
class InitImportCustomerEntitledVoucherRewardUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitImportCustomerEntitledVoucherRewardUpstream")
    
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                count = CustomerEntitledVoucher.count_by_merchant_acct(merchant_acct)
            else:
                count = CustomerEntitledVoucher.count()
        
        return count
    
    def get_task_batch_size(self):
        return 100
    
    def get_task_url(self):
        return '/maint/reward/import-customer-entitled-voucher-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }
    
class ExecuteImportCustomerEntitledVoucherRewardUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteImportCustomerEntitledVoucherRewardUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                (result, next_cursor) = CustomerEntitledVoucher.list_by_merchant_acct(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor)
            else:
                (result, next_cursor) = CustomerEntitledVoucher.list_all(offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
                
            
            for reward in result:
                transaction_id      = reward.transaction_id
                transaction_details = CustomerTransaction.get_by_transaction_id(transaction_id)
                
                if transaction_details:
                    voucher_key             = reward.entitled_voucher_key
                    voucher_amount          = 1 
                    expiry_date             = reward.expiry_date
                    giveaway_datetime       = reward.rewarded_datetime
                    voucher_reward_brief    = VoucherRewardDetailsForUpstreamData(voucher_key, voucher_amount, expiry_date, giveaway_datetime)
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, voucher_reward_brief)
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/reward/import-customer-entitled-voucher-reward-upstream' 

    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }   

customer_reward_maintenance_setup_bp_api.add_resource(TriggerImportCustomerPrepaidRewardUpstream,   '/trigger-import-customer-prepaid-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(InitImportCustomerPrepaidRewardUpstream,   '/init-import-customer-prepaid-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(ExecuteImportCustomerPrepaidRewardUpstream,   '/import-customer-prepaid-reward-upstream')

customer_reward_maintenance_setup_bp_api.add_resource(TriggerImportCustomerPointRewardUpstream,   '/trigger-import-customer-point-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(InitImportCustomerPointRewardUpstream,   '/init-import-customer-point-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(ExecuteImportCustomerPointRewardUpstream,   '/import-customer-point-reward-upstream')

customer_reward_maintenance_setup_bp_api.add_resource(TriggerImportCustomerStampRewardUpstream,   '/trigger-import-customer-stamp-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(InitImportCustomerStampRewardUpstream,   '/init-import-customer-stamp-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(ExecuteImportCustomerStampRewardUpstream,   '/import-customer-stamp-reward-upstream')

customer_reward_maintenance_setup_bp_api.add_resource(TriggerImportCustomerEntitledVoucherRewardUpstream,   '/trigger-import-customer-entitled-voucher-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(InitImportCustomerEntitledVoucherRewardUpstream,   '/init-import-customer-entitled-voucher-reward-upstream')
customer_reward_maintenance_setup_bp_api.add_resource(ExecuteImportCustomerEntitledVoucherRewardUpstream,   '/import-customer-entitled-voucher-reward-upstream')


