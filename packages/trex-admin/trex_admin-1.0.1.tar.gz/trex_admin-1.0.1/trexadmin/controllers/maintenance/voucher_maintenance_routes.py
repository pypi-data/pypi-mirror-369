'''
Created on 26 Nov 2024

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
from trexanalytics.bigquery_upstream_data_config import create_revert_redeemed_customer_voucher_to_upstream_for_merchant,\
    create_redeemed_customer_voucher_to_upstream_for_merchant,\
    create_removed_customer_voucher_to_upstream_for_merchant,\
    create_revert_entitled_customer_voucher_upstream_for_merchant,\
    create_entitled_customer_voucher_upstream_for_merchant
from trexlib.libs.flask_wtf.request_wrapper import request_values
from datetime import datetime
from trexconf import conf
from flask.json import jsonify
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.string_util import is_not_empty, remove_dash
from trexapi.decorators.api_decorators import merchant_key_required
from trexmodel.models.datastore.voucher_models import MerchantVoucher

voucher_maintenance_setup_bp = Blueprint('voucher_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/voucher')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

voucher_maintenance_setup_bp_api = Api(voucher_maintenance_setup_bp)

@voucher_maintenance_setup_bp.route('/merchant-voucher-key/<merchant_voucher_key>/list-customer-entitled-voucher', methods=['get','post'])
@request_values
def list_customer_entitled_voucher_by_merchant_voucher_key_and_date_ranage(request_values, merchant_voucher_key):
    start_date  = request_values.get('start_date')
    end_date    = request_values.get('end_date')
    
    voucher_list = []
    if is_not_empty(start_date) and is_not_empty(end_date):
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
    
    logger.debug('start_date=%s', start_date)
    logger.debug('end_date=%s', end_date)
    
    db_client = create_db_client(caller_info="list_customer_entitled_voucher_by_merchant_voucher_key")
    with db_client.context():
        merchant_voucher = MerchantVoucher.get_or_read_from_cache(merchant_voucher_key)
        logger.debug('merchant_voucher=%s', merchant_voucher)
        if merchant_voucher:
            
            result = CustomerEntitledVoucher.list_by_merchant_voucher(merchant_voucher, entitled_datetime_start=start_date, entitled_datetime_end=end_date)
        
            for r in result:
                voucher_list.append(r.to_dict())

    return jsonify({'vouchers': voucher_list})

@voucher_maintenance_setup_bp.route('/merchant-voucher-key/<merchant_voucher_key>/count-customer-entitled-voucher', methods=['get','post'])
@request_values
def count_customer_entitled_voucher_by_merchant_voucher_key_and_date_ranage(request_values, merchant_voucher_key):
    start_date  = request_values.get('start_date')
    end_date    = request_values.get('end_date')
    
    if is_not_empty(start_date) and is_not_empty(end_date):
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
    
    logger.debug('start_date=%s', start_date)
    logger.debug('end_date=%s', end_date)
    
    db_client = create_db_client(caller_info="count_customer_entitled_voucher_by_merchant_voucher_key_and_date_ranage")
    with db_client.context():
        merchant_voucher = MerchantVoucher.fetch(merchant_voucher_key)
        logger.debug('merchant_voucher=%s', merchant_voucher)
        if merchant_voucher:
            
            count = CustomerEntitledVoucher.count_merchant_voucher(merchant_voucher)
            
    return jsonify({'count': count})

@voucher_maintenance_setup_bp.route('/<merchant_voucher_key>/rebuild-configuration', methods=['get','post'])
def rebuild_merchant_voucher_configuration(merchant_voucher_key):
    db_client = create_db_client(caller_info="rebuild_merchant_voucher_configuration")
    with db_client.context():
        merchant_voucher = MerchantVoucher.fetch(merchant_voucher_key)
        
        if merchant_voucher:
            merchant_voucher.configuration =  merchant_voucher.rebuild_configuration
            merchant_voucher.put()

            return jsonify(merchant_voucher.configuration)
        
    return "Invalid merchant voucher", 400

@voucher_maintenance_setup_bp.route('/<merchant_key>/show-voucher-statistic-by-date-range', methods=['get','post'])
@request_values
def show_merchant_voucher_statistic_by_date_range(request_values, merchant_key):
    date_range_start    = request_values.get('date_range_start')
    date_range_end      = request_values.get('date_range_end')
    
    logger.debug('date_range_start=%s', date_range_start)
    logger.debug('date_range_end=%s', date_range_end)
    logger.debug('merchant_key=%s', merchant_key)
    
    if date_range_start and date_range_end:
        start_date                  = datetime.strptime(date_range_start, '%d/%m/%Y')
        end_date                    = datetime.strptime(date_range_end, '%d/%m/%Y')
    else:
        start_date  = None
        end_date    = None
    
    
    db_client = create_db_client(caller_info="show_merchant_voucher_statistic")
    
    removed_count   = 0
    redeemed_count  = 0
    reverted_count  = 0
    
    try:
        with db_client.context():
            merchant_acct               = MerchantAcct.fetch(merchant_key)
            total_count = CustomerEntitledVoucher.count_by_merchant_acct(merchant_acct, start_date, end_date)
            
            customer_vouchers_list = CustomerEntitledVoucher.list_by_merchant_acct(merchant_acct, start_date, end_date, limit=conf.MAX_FETCH_RECORD)
            for customer_voucher in customer_vouchers_list:
                is_redeemed = customer_voucher.is_redeemed
                is_removed  = customer_voucher.is_removed
                is_reverted = customer_voucher.is_reverted
                
                logger.debug('status=%s', customer_voucher.status)
                
                if is_redeemed:
                    redeemed_count+=1
                elif is_removed:
                    removed_count+=1
                elif is_reverted:
                    reverted_count+=1
    except:
        logger.error('Failed due to %s', get_tracelog())
    
    return jsonify({
            'total'     : total_count,
            'removed'   : removed_count,
            'redeemed'  : redeemed_count,
            'reverted'  : reverted_count,
            })
        


class TriggerImportVoucherUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/voucher/init-import-voucher-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key        = request_values.get('merchant_key')
        
        if is_not_empty(merchant_key):
            merchant_key = remove_dash(merchant_key)
        
        return {
                'merchant_key'      : merchant_key,
                
            }    
    
class InitImportVoucherUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitImportVoucherUpstream")
    
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
        return '/maint/voucher/import-voucher-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key        = request_values.get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }
    
class ExecuteImportVoucherUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteImportVoucherUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct               = MerchantAcct.fetch(merchant_key)
                (result, next_cursor)       = CustomerEntitledVoucher.list_by_merchant_acct(
                                                                            merchant_acct, 
                                                                            offset=offset, 
                                                                            limit=limit, 
                                                                            start_cursor=start_cursor,
                                                                            return_with_cursor=True
                                                                            )
            else:
                (result, next_cursor)       = CustomerEntitledVoucher.list_all(
                                                                            offset=offset, 
                                                                            limit=limit, 
                                                                            start_cursor=start_cursor,
                                                                            return_with_cursor=True
                                                                            )
            
            if result:
                
                for customer_voucher in result:
                    is_redeemed = customer_voucher.is_redeemed
                    is_removed  = customer_voucher.is_removed
                    is_reverted = customer_voucher.is_reverted
                    
                    if is_reverted:
                        
                        create_revert_entitled_customer_voucher_upstream_for_merchant(customer_voucher)
                        logger.debug('going to create upstream for reverted voucher')    
                    elif is_removed:
                        create_removed_customer_voucher_to_upstream_for_merchant(customer_voucher)
                        logger.debug('going to create upstream for removed voucher')
                        
                    elif is_redeemed:
                        create_redeemed_customer_voucher_to_upstream_for_merchant(customer_voucher)
                        logger.debug('going to create upstream for redeemed voucher')
                    
                    create_entitled_customer_voucher_upstream_for_merchant(customer_voucher)
                    logger.debug('going to create upstream for entitled voucher')
                        
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/voucher/import-voucher-upstream' 
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key        = request_values.get('merchant_key')
        return {
                'merchant_key'      : merchant_key,
            }   


voucher_maintenance_setup_bp_api.add_resource(TriggerImportVoucherUpstream,   '/trigger-import-voucher-upstream')
voucher_maintenance_setup_bp_api.add_resource(InitImportVoucherUpstream,   '/init-import-voucher-upstream')
voucher_maintenance_setup_bp_api.add_resource(ExecuteImportVoucherUpstream,   '/import-voucher-upstream')



