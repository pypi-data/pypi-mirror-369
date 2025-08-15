'''
Created on 27 Mar 2023

@author: jacklok
'''
from flask import Blueprint, request, render_template, jsonify
import logging
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.transaction_models import CustomerTransaction,\
    SalesTransaction
from trexanalytics.helper.bigquery_upstream_helpers import list_transction_reward,\
    create_transction_reward_upstream
from flask.json import jsonify
from trexmodel.models.datastore.message_model_helper import create_transaction_message
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexanalytics.bigquery_upstream_data_config import create_merchant_sales_transaction_upstream_for_merchant,\
    create_merchant_customer_transaction_upstream_for_merchant,\
    upstream_schema_config, create_upstream_data
from flask_restful import Api
from trexanalytics.bigquery_table_template_config import CUSTOMER_TRANSACTION_TEMPLATE,\
    SALES_TRANSACTION_TEMPLATE

transaction_maintenance_setup_bp = Blueprint('transaction_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/transaction')


transaction_maintenance_setup_bp_api = Api(transaction_maintenance_setup_bp)

#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')


@transaction_maintenance_setup_bp.route('/transaciton-id/<transaction_id>/create-sales-transaction-upstream', methods=['get'])
def create_sales_transaction_upstream_by_transaction_id(transaction_id):
    db_client = create_db_client(caller_info="create_sales_transaction_upstream_by_transaction_id")
    
    with db_client.context():
        sales_transaction = SalesTransaction.get_by_transaction_id(transaction_id)
        if sales_transaction:
            create_merchant_sales_transaction_upstream_for_merchant(sales_transaction)
            sales_transaction = sales_transaction.to_dict()
        
    return jsonify({'sales_transaction': sales_transaction})


@transaction_maintenance_setup_bp.route('/count-sales-transaction', methods=['get'])
def count_sales_transaction():
    db_client = create_db_client(caller_info="count_sales_transaction")
    
    with db_client.context():
        count = SalesTransaction.count()
        logger.debug('count=%s', count)
        
        
    return jsonify({'count': count})

@transaction_maintenance_setup_bp.route('/count-customer-transaction', methods=['get'])
def count_customer_transaction():
    db_client = create_db_client(caller_info="count_customer_transaction")
    
    with db_client.context():
        count = CustomerTransaction.count()
        logger.debug('count=%s', count)
        
        
    return jsonify({'count': count})

@transaction_maintenance_setup_bp.route('/merchant-acct/<merchant_acct_key>/count-merchant-sales-transaction', methods=['get'])
def count_merchant_sales_transaction(merchant_acct_key):
    db_client = create_db_client(caller_info="count_merchant_sales_transaction")
    
    with db_client.context():
        merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_acct_key)
        count = SalesTransaction.count_by_merchant(merchant_acct)
        logger.debug('count=%s', count)
        
        
    return jsonify({'count': count})

@transaction_maintenance_setup_bp.route('/transaction-id/<transaction_id>/create-customer-transaction-upstream-data', methods=['get'])
def show_customer_transaction_upstream_data(transaction_id):
    db_client = create_db_client(caller_info="show_customer_transaction_upstream_data")
    
    with db_client.context():
        customer_transaction =  CustomerTransaction.get_by_transaction_id(transaction_id)
        if customer_transaction:
            schema = upstream_schema_config.get(CUSTOMER_TRANSACTION_TEMPLATE)
            upstream_data = create_upstream_data(customer_transaction, schema, maint=True)
            
            
        else:
            upstream_data = {}
        
    return jsonify(upstream_data)

@transaction_maintenance_setup_bp.route('/transaction-id/<transaction_id>/create-sales-transaction-upstream-data', methods=['get'])
def show_sales_transaction_upstream_data(transaction_id):
    db_client = create_db_client(caller_info="show_customer_transaction_upstream_data")
    
    with db_client.context():
        customer_transaction =  SalesTransaction.get_by_transaction_id(transaction_id)
        if customer_transaction:
            schema = upstream_schema_config.get(SALES_TRANSACTION_TEMPLATE)
            upstream_data = create_upstream_data(customer_transaction, schema, maint=True)
            
            
        else:
            upstream_data = {}
        
    return jsonify(upstream_data)


@transaction_maintenance_setup_bp.route('/transaction-key/<transaction_key>/list-reward', methods=['get'])
def list_transaction_reward(transaction_key):
    db_client = create_db_client(caller_info="list_transaction_reward")
    rewards_list = []
    with db_client.context():
        customer_transaction = CustomerTransaction.fetch(transaction_key)
        logger.debug('customer_transaction=%s', customer_transaction)
        if customer_transaction:
            rewards_list = list_transction_reward(customer_transaction)
        
        
    return jsonify(rewards_list)

@transaction_maintenance_setup_bp.route('/transaction-id/<transaction_id>/list-reward', methods=['get'])
def list_transaction_reward_by_transaction_id(transaction_id):
    db_client = create_db_client(caller_info="list_transaction_reward_by_transaction_id")
    rewards_list = []
    with db_client.context():
        customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
        logger.debug('customer_transaction=%s', customer_transaction)
        if customer_transaction:
            _rewards_list = list_transction_reward(customer_transaction)
            if _rewards_list:
                for r in _rewards_list:
                    rewards_list.append(r.to_dict())
        
    return jsonify(rewards_list)

@transaction_maintenance_setup_bp.route('/transaction-id/<transaction_id>/create-reward-upstream', methods=['get'])
def create_tansaction_reward_upstream_by_transaction_id(transaction_id):
    db_client = create_db_client(caller_info="list_transaction_reward_by_transaction_id")
    rewards_list = []
    with db_client.context():
        customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
        logger.debug('customer_transaction=%s', customer_transaction)
        if customer_transaction:
            _rewards_list = list_transction_reward(customer_transaction)
            if _rewards_list:
                for r in _rewards_list:
                    rewards_list.append(r.to_dict())
            
            create_transction_reward_upstream(customer_transaction)
        
    return jsonify(rewards_list)

@transaction_maintenance_setup_bp.route('/transaction-id/<transaction_id>/create-transaction-message', methods=['get'])
def create_tansaction_message(transaction_id):
    db_client = create_db_client(caller_info="create_tansaction_message")
    rewards_list = []
    with db_client.context():
        customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
        logger.debug('customer_transaction=%s', customer_transaction)
        if customer_transaction:
            create_transaction_message(customer_transaction)
        
    return jsonify(rewards_list)

class TriggerCreateTransactionUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/transaction/init-create-transaction-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        return {
                
            }    
    
class InitCreateTransactionUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        
        
        db_client = create_db_client(caller_info="InitCreateTransactionUpstream")
    
        with db_client.context():
            count = CustomerTransaction.count()

        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/transaction/create-transaction-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
class ExecuteCreateTransactionUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateTransactionUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                #(result, next_cursor) = Customer.list(limit=20, start_cursor=start_cursor, return_with_cursor=True)
                if merchant_acct:
                    (result, next_cursor) = CustomerTransaction.list_merchant_transaction(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            else:
                (result, next_cursor) = CustomerTransaction.list(limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            
            logger.debug('=================>>>>>> ExecuteCreateTransactionUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            if result:
                for transaction in result:
                    logger.debug('transaction key=%s', transaction.key_in_str)
                    create_merchant_customer_transaction_upstream_for_merchant(transaction)
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/transaction/create-transaction-upstream' 

class TriggerCreateSalesTransactionUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/transaction/init-create-sales-transaction-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        return {
                
            }    
    
class InitCreateSalesTransactionUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        
        
        db_client = create_db_client(caller_info="InitCreateSalesTransactionUpstream")
    
        with db_client.context():
            count = SalesTransaction.count()

        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/transaction/create-sales-transaction-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
class ExecuteCreateSalesTransactionUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateSalesTransactionUpstream")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                #(result, next_cursor) = Customer.list(limit=20, start_cursor=start_cursor, return_with_cursor=True)
                if merchant_acct: 
                    (result, next_cursor) = SalesTransaction.list_merchant_transaction(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            else:
                (result, next_cursor) = SalesTransaction.list(limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            
            logger.debug('=================>>>>>> ExecuteCreateTransactionUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            if result:
                for transaction in result:
                    logger.debug('transaction key=%s', transaction.key_in_str)
                    create_merchant_sales_transaction_upstream_for_merchant(transaction)
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/transaction/create-sales-transaction-upstream' 
    
class TriggerCheckFromCustomerTransactionToCreateSalesTransaction(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/transaction/init-check-from-customer-transaction-to-create-sales-transaction'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        return {
                
            }    
    
class InitCheckFromCustomerTransactionToCreateSalesTransaction(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        
        
        db_client = create_db_client(caller_info="InitCheckFromCustomerTransactionToCreateSalesTransaction")
    
        with db_client.context():
            count = CustomerTransaction.count()

        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/transaction/check-from-customer-transaction-to-create-sales-transaction'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    
class ExecuteCheckFromCustomerTransactionToCreateSalesTransaction(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCheckFromCustomerTransactionToCreateSalesTransaction")
        
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                if merchant_acct: 
                    (result, next_cursor) = CustomerTransaction.list_merchant_transaction(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            else:
                (result, next_cursor) = CustomerTransaction.list(limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            
            logger.debug('=================>>>>>> ExecuteCheckFromCustomerTransactionToCreateSalesTransaction debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            total_created       = self.recorded_payload.get('total_created',0)
            total_found         = self.recorded_payload.get('total_created',0)
            total_count         = self.recorded_payload.get('total_count',0)
            total_new_created   = 0
            total_found_created = 0
            
            logger.debug('=================>>>>>> b4 total_created=%d, total_found=%d', total_created, total_found)
            if result:
                total_count+=len(result)
                for transaction in result:
                    
                    if transaction.is_sales_transaction:
                        transaction_id = transaction.transaction_id
                        sales_transaction =  SalesTransaction.get_by_transaction_id(transaction_id)
                        if sales_transaction is None:
                            sales_transaction = SalesTransaction.create(
                                                   transact_outlet      = transaction.transact_outlet_details,
                                                   
                                                   transact_amount      = transaction.transact_amount, 
                                                   tax_amount           = transaction.tax_amount,
                                                   
                                                   invoice_id           = transaction.invoice_id, 
                                                   transaction_id       = transaction_id,
                                                   
                                                   remarks              = transaction.remarks,
                                                   system_remarks       = transaction.system_remarks,
                                                   
                                                   is_revert            = transaction.is_revert,
                                                   reverted_datetime    = transaction.reverted_datetime,
                                                   reverted_by          = transaction.reverted_by,
                                                   reverted_by_username = transaction.reverted_by_username,
                                                   
                                                   transact_datetime    = transaction.transact_datetime,
                                                   
                                                   allow_to_revert      = transaction.allow_to_revert,
                                                   sales_channel        = transaction.sales_channel,
                                                   
                                                   created_datetime     = transaction.created_datetime,
                                                   transact_by          = transaction.transact_by,
                                                   
                                                   
                                                   )
                            total_new_created +=1
                        else:
                            total_found_created +=1
            
            total_created+=total_new_created
            total_found+=total_found_created
            
            self.recorded_payload['total_created']  = total_created
            self.recorded_payload['total_found']    = total_found
            self.recorded_payload['total_count']    = total_count
            
            logger.debug('=================>>>>>> after total_created=%d, total_found=%d', total_created, total_found)
            
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/transaction/check-from-customer-transaction-to-create-sales-transaction'     


transaction_maintenance_setup_bp_api.add_resource(TriggerCreateTransactionUpstream,   '/trigger-create-transaction-upstream')
transaction_maintenance_setup_bp_api.add_resource(InitCreateTransactionUpstream,   '/init-create-transaction-upstream')
transaction_maintenance_setup_bp_api.add_resource(ExecuteCreateTransactionUpstream,   '/create-transaction-upstream')

transaction_maintenance_setup_bp_api.add_resource(TriggerCheckFromCustomerTransactionToCreateSalesTransaction,   '/trigger-check-from-customer-transaction-to-create-sales-transaction')
transaction_maintenance_setup_bp_api.add_resource(InitCheckFromCustomerTransactionToCreateSalesTransaction,   '/init-check-from-customer-transaction-to-create-sales-transaction')
transaction_maintenance_setup_bp_api.add_resource(ExecuteCheckFromCustomerTransactionToCreateSalesTransaction,   '/check-from-customer-transaction-to-create-sales-transaction')
    
transaction_maintenance_setup_bp_api.add_resource(TriggerCreateSalesTransactionUpstream,   '/trigger-create-sales-transaction-upstream')
transaction_maintenance_setup_bp_api.add_resource(InitCreateSalesTransactionUpstream,   '/init-create-sales-transaction-upstream')
transaction_maintenance_setup_bp_api.add_resource(ExecuteCreateSalesTransactionUpstream,   '/create-sales-transaction-upstream')


