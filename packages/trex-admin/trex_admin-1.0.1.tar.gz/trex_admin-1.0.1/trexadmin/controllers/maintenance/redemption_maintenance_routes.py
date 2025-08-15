'''
Created on 28 Nov 2024

@author: jacklok
'''

from flask import Blueprint, request
from trexmodel.utils.model.model_util import create_db_client
import logging
from flask_restful import Api
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexlib.utils.string_util import is_not_empty
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_redemption_upstream_for_merchant

redemption_maintenance_setup_bp = Blueprint('redemption_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/redemption')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

redemption_maintenance_setup_bp_api = Api(redemption_maintenance_setup_bp)

class TriggerUpdateRedeemedVoucher(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/redemption/init-update-redeemed-voucher'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        merchant_key        = request.args.get('merchant_key')
        date_range_start    = request.args.get('date_range_start')
        date_range_end      = request.args.get('date_range_end')
        return {
                'merchant_key'      : merchant_key,
                'date_range_start'  : date_range_start,
                'date_range_end'    : date_range_end,
            }    
    
class InitUpdateRedeemedVoucher(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitUpdateRedeemedVoucher")
    
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_key)
            count = CustomerRedemption.count_by_merchant_acct(merchant_acct)
        
        return count
    
    def get_task_batch_size(self):
        return 100
    
    def get_task_url(self):
        return '/maint/redemption/update-redeemed-voucher'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        date_range_start    = request.get_json().get('date_range_start')
        date_range_end      = request.get_json().get('date_range_end')
        return {
                'merchant_key'      : merchant_key,
                'date_range_start'  : date_range_start,
                'date_range_end'    : date_range_end,
            }
    
class ExecuteUpdateRedeemedVoucher(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteUpdateRedeemedVoucher")
    
        with db_client.context():
            merchant_acct               = MerchantAcct.fetch(merchant_key)
            (result, next_cursor)       = CustomerRedemption.list_by_merchant_acct(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor)
            
            if result:
                
                for customer_redemption in result:
                    reward_format = customer_redemption.reward_format
                    redeem_transaction_id   = customer_redemption.transaction_id
                    redeemed_by_outlet      = customer_redemption.redeemed_outlet
                    
                    if 'voucher' == reward_format:
                        redeemed_summary = customer_redemption.redeemed_summary
                        
                        redeemed_voucher_summary = redeemed_summary.get('voucher')
                        
                        redeemed_vouchers_dict = redeemed_voucher_summary.get('vouchers')
                        
                        for details in redeemed_vouchers_dict.values():
                            customer_entitled_vouchers = details.get('customer_entitled_vouchers')
                            logger.debug('customer_entitled_vouchers=%s', customer_entitled_vouchers)
                            if customer_entitled_vouchers:
                            
                                for customer_entitled_voucher_summary in customer_entitled_vouchers:
                                
                                    customer_entitled_voucher = CustomerEntitledVoucher.fetch(customer_entitled_voucher_summary.get('customer_entitled_voucher_key'))
                                    customer_entitled_voucher.redeemed_transaction_id   = redeem_transaction_id
                                    customer_entitled_voucher.redeemed_by_outlet        = redeemed_by_outlet
                                    
                                    customer_entitled_voucher.put()
                                
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/redemption/update-redeemed-voucher' 

    def get_data_payload(self):
        merchant_key        = request.get_json().get('merchant_key')
        date_range_start    = request.get_json().get('date_range_start')
        date_range_end      = request.get_json().get('date_range_end')
        return {
                'merchant_key'      : merchant_key,
                'date_range_start'  : date_range_start,
                'date_range_end'    : date_range_end,
            }   

class TriggerCreateRedemptionUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/redemption/init-create-redemption-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        return {
                
            }    
    
class InitCreateRedemptionUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        
        
        db_client = create_db_client(caller_info="InitCreateRedemptionUpstream")
    
        with db_client.context():
            count = CustomerRedemption.count()

        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/redemption/create-redemption-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
class ExecuteCreateRedemptionUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateRedemptionUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                #(result, next_cursor) = Customer.list(limit=20, start_cursor=start_cursor, return_with_cursor=True)
                if merchant_acct:
                    (result, next_cursor) = CustomerRedemption.list_merchant_transaction(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            else:
                (result, next_cursor) = CustomerRedemption.list_all(limit=20, start_cursor=start_cursor, return_with_cursor=True)
            
            logger.debug('=================>>>>>> ExecuteCreateTransactionUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            if result:
                for transaction in result:
                    create_merchant_customer_redemption_upstream_for_merchant(transaction)
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/redemption/create-redemption-upstream' 


redemption_maintenance_setup_bp_api.add_resource(TriggerUpdateRedeemedVoucher,   '/trigger-update-redeemed-voucher')
redemption_maintenance_setup_bp_api.add_resource(InitUpdateRedeemedVoucher,   '/init-update-redeemed-voucher')
redemption_maintenance_setup_bp_api.add_resource(ExecuteUpdateRedeemedVoucher,   '/update-redeemed-voucher')

redemption_maintenance_setup_bp_api.add_resource(TriggerCreateRedemptionUpstream,   '/trigger-create-redemption-upstream')
redemption_maintenance_setup_bp_api.add_resource(InitCreateRedemptionUpstream,   '/init-create-redemption-upstream')
redemption_maintenance_setup_bp_api.add_resource(ExecuteCreateRedemptionUpstream,   '/create-redemption-upstream')
