'''
Created on 24 Mar 2023

@author: jacklok
'''

from flask import Blueprint, jsonify, Response
from trexmodel.utils.model.model_util import create_db_client 
import logging
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from flask_restful import Api
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexadmin.controllers.report.merchant import customer
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexanalytics.bigquery_upstream_data_config import create_merchant_registered_customer_upstream_for_merchant,\
    create_registered_customer_upstream_for_system,\
    create_merchant_customer_transaction_upstream_for_merchant,\
    create_customer_membership_upstream_for_merchant,\
    create_partnership_transaction_upstream_for_merchant
from trexanalytics.helper.bigquery_upstream_helpers import create_transction_reward_upstream,\
    create_redemption_upstream
from flask_restful import Resource
from trexlib.utils.google.bigquery_util import create_bigquery_client
from trexconf import conf
import re
from google.cloud import bigquery
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexlib.utils.google.cloud_tasks_util import create_task
from trexmodel.models.datastore.partnership_models import PartnershipRewardTransaction
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.log_util import get_tracelog
from trexanalytics.bigquery_table_template_config import TABLE_SCHEME_TEMPLATE
import json

upstream_maintenance_bp = Blueprint('upstream_maintenance_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/upstream')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

upstream_maintenance_setup_bp_api = Api(upstream_maintenance_bp)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)  # Convert set to list
        return super().default(obj)

@upstream_maintenance_bp.route('/ping', methods=['get'])
def ping():
    return "pong", 200

def matches_table_pattern(s, prefix):
    pattern = rf"^{prefix}\d{{8}}$"
    return bool(re.match(pattern, s))

@upstream_maintenance_bp.route('/table-scheme/<table_scheme>/scheme-field-list', methods=['get'])
def show_table_scheme_field_list(table_scheme):
    table_scheme_list = TABLE_SCHEME_TEMPLATE.get(table_scheme)
    
    expected_fields = set(field.name for field in table_scheme_list)
    
    
    return jsonify({'fields':json.dumps(expected_fields, cls=SetEncoder)})
    
    

@upstream_maintenance_bp.route('/dataset/<dataset_name>/table-name-prefix/<table_name_prefix>/list-dataset-table', methods=['get'])
def list_dataset_table_partition(dataset_name, table_name_prefix):
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID)
    dataset_ref     = bg_client.dataset(dataset_name)
    tables          = bg_client.list_tables(dataset_ref)
    tables_list     = []
    final_table_prefix = '%s_' % (table_name_prefix)
    for table in tables:
        if table.table_id.startswith(final_table_prefix):
            if matches_table_pattern(table.table_id, final_table_prefix):
                tables_list.append(table.table_id)
            
    return jsonify(tables_list)

@upstream_maintenance_bp.route('/merchant-dataset/merchant-account-code/<merchant_account_code>/table-name-prefix/<table_name_prefix>/list-dataset-table', methods=['get'])
def list_merchant_dataset_table_partition(merchant_account_code, table_name_prefix):
    bg_client           = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID)
    merchant_dataset    = 'merchant_%s' % merchant_account_code
    dataset_ref         = bg_client.dataset(merchant_dataset)
    tables              = bg_client.list_tables(dataset_ref)
    tables_list         = []
    final_table_prefix  = '%s_' % (table_name_prefix)
    for table in tables:
        if table.table_id.startswith(final_table_prefix):
            if matches_table_pattern(table.table_id, final_table_prefix):
                tables_list.append(table.table_id)
            
    return jsonify(tables_list)

@upstream_maintenance_bp.route('/dataset/<dataset_name>/table-name/<table_name>/merchant-account-code/<merchant_account_code>/list-dataset-table', methods=['get'])
def list_dataset_table_partition_by_merchant_code(dataset_name, table_name, merchant_account_code):
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    final_dataset_name = '%s_%s' % (dataset_name, merchant_account_code.replace('-',''))
    
    dataset_ref     = bg_client.dataset(final_dataset_name)
    tables          = bg_client.list_tables(dataset_ref)
    tables_list     = []
    
    
    for table in tables:
        #logger.debug('table.table_id=%s', table.table_id)
        if table.table_id==table_name:
            tables_list.append(table.table_id)
            logger.debug('table.table_id=%s', table.table_id)
            
    return jsonify(tables_list)

@upstream_maintenance_bp.route('/dataset/<dataset_name>/table-name/<table_name>/merchant-account-code/<merchant_account_code>/delete-dataset-table', methods=['get','post'])
def delete_dataset_table_partition(dataset_name, table_name, merchant_account_code):
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID)
    final_dataset_name = '%s_%s' % (dataset_name, merchant_account_code.replace('-',''))
    is_deleted = False
    try:
        table_ref = bg_client.dataset(final_dataset_name).table(table_name)
        bg_client.delete_table(table_ref)
        is_deleted = True
    except:
        logger.error('failed due to %s', get_tracelog())
    
    if is_deleted:
        return "deleted", 200
    else:
        return "Failed to delete", 200


class ModuleIndexResource(Resource):
    
    def output_html(self, content, code=200, headers=None):
        resp = Response(content, mimetype='text/html', headers=headers)
        resp.status_code = code
        return resp
    
    def post(self):
        return self.get()
    
    def get(self):
        return self.output_html("Upstream maintenance module")

class TriggerDeleteMerchantDatasetTable(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-delete-merchant-dataset-table'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values  
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        table_name=request_values.get('table_name')
        logger.debug('merchant_key=%s', merchant_key)
        logger.debug('table_name=%s', table_name)
        return {
                'merchant_key'  : merchant_key,
                'table_name'    : table_name,
            }    
        
class InitDeleteMerchantDatasetTable(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key = kwargs.get('merchant_key')
        logger.debug('merchant_key=%s', merchant_key)
        
        if is_not_empty(merchant_key):
            return 1
        else:
            db_client = create_db_client(caller_info="InitDeleteMerchantDatasetTable")
        
            with db_client.context():
                count = MerchantAcct.count()
            
            return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/delete-merchant-dataset-table'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        table_name=request_values.get('table_name')
        return {
                'merchant_key'  : merchant_key,
                'table_name'    : table_name,
            }
    
class ExecuteDeleteMerchantDatasetTable(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        table_name      = kwargs.get('table_name')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteDeleteMerchantDatasetTable")
    
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
                merchant_account_code = merchant_acct.account_code.replace('-','')
                merchant_dataset = 'merchant'
                delete_table_url = 'maint/upstream/dataset/{dataset}/table-name/{table_name}/merchant-account-code/{merchant_account_code}/delete-dataset-table'.format(dataset=merchant_dataset, table_name=table_name, merchant_account_code=merchant_account_code)
                logger.debug('delete_table_url=%s', delete_table_url)
                _trigger_upstream_task(merchant_acct, delete_table_url)
                
            else:
                
                (result, next_cursor) = MerchantAcct.list(start_cursor=start_cursor, return_with_cursor=True)
                
                for merchant_acct in result:
                    merchant_account_code = merchant_acct.account_code.replace('-','')
                    merchant_dataset = 'merchant'
                    delete_table_url = 'maint/upstream/dataset/{dataset}/table-name/{table_name}/merchant-account-code/{merchant_account_code}/delete-dataset-table'.format(dataset=merchant_dataset, table_name=table_name, merchant_account_code=merchant_account_code)
                    logger.debug('delete_table_url=%s', delete_table_url)
                    _trigger_upstream_task(merchant_acct, delete_table_url)
                     
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/delete-merchant-dataset-table'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        table_name=request_values.get('table_name')
        return {
                'merchant_key'  : merchant_key,
                'table_name'    : table_name,
            }    

class TriggerCreateAllMerchantUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-create-all-merchant-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        return {
            }    
        
class InitCreateAllMerchantUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        
        
        db_client = create_db_client(caller_info="InitCreateAllMerchantUpstream")
    
        with db_client.context():
            count = MerchantAcct.count()
            logger.debug('merchant count=%d', count)
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/create-all-merchant-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        return {
        
            }


def _trigger_upstream_task(merchant_acct, upstream_url):
    task_url    = '%s/%s' % (conf.SYSTEM_BASE_URL, upstream_url)
    queue_name  = 'upstream-maint'
    
    create_task(task_url, queue_name, 
                in_seconds      = 1,
                http_method     = 'get', 
                payload         = {'merchant_key': merchant_acct.key_in_str},
                credential_path = conf.SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                project_id      = conf.SYSTEM_TASK_GCLOUD_PROJECT_ID,
                location        = conf.SYSTEM_TASK_GCLOUD_LOCATION,
                service_email   = conf.SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                )
    
def _trigger_create_merchant_registered_upstream_task(merchant_acct):
    _trigger_upstream_task(merchant_acct, 'maint/upstream/trigger-merchant-registered-customer-upstream')

def _trigger_create_merchant_customer_membership_upstream_task(merchant_acct):
    _trigger_upstream_task(merchant_acct, 'maint/upstream/trigger-customer-membership-upstream')

def _trigger_create_merchant_sales_upstream_task(merchant_acct):
    _trigger_upstream_task(merchant_acct, 'maint/upstream/trigger-merchant-sales-upstream')

def _trigger_create_merchant_customer_reward_upstream_task(merchant_acct):
    _trigger_upstream_task(merchant_acct, 'maint/upstream/trigger-merchant-customer-reward-upstream')
    
def _trigger_create_merchant_customer_redemption_upstream_task(merchant_acct):
    _trigger_upstream_task(merchant_acct, 'maint/upstream/trigger-merchant-customer-redemption-upstream')
    
class ExecuteCreateAllMerchantUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        start_cursor    = kwargs.get('start_cursor')
        
        db_client = create_db_client(caller_info="ExecuteCreateAllMerchantUpstream")
    
        with db_client.context():
            (result, next_cursor) = MerchantAcct.list(start_cursor=start_cursor, limit=50, return_with_cursor=True)
            logger.debug('=================>>>>>> ExecuteCreateAllMerchantUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
            
            for merchant_acct in result:
                logger.debug('going to trigger upstream for merchant(%s)', merchant_acct.brand_name)
                #_trigger_create_merchant_registered_upstream_task(merchant_acct)
                #_trigger_create_merchant_customer_membership_upstream_task(merchant_acct)
                #_trigger_create_merchant_sales_upstream_task(merchant_acct)
                _trigger_create_merchant_customer_reward_upstream_task(merchant_acct)
                #_trigger_create_merchant_customer_redemption_upstream_task(merchant_acct)
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/create-all-merchant-upstream'
    
    @request_values
    def get_data_payload(self, request_values):
        
        return {
                
            } 

class TriggerCreateMerchantRegisteredCustomerUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-merchant-registered-customer-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        logger.debug('merchant_key=%s', merchant_key)
        
        return {
                'merchant_key': merchant_key,
            }    
        
class InitCreateMerchantRegisteredCustomerUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key = kwargs.get('merchant_key')
        
        
        db_client = create_db_client(caller_info="InitCreateMerchantRegisteredCustomerUpstrea")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
        
            count = Customer.count_merchant_customer(merchant_acct)
            
            logger.debug('customer count=%d', count)
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/merchant-registered-customer-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteCreateMerchantRegisteredCustomerUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateMerchantRegisteredCustomer")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
            if merchant_acct:
                
                (result, next_cursor) = Customer.list_merchant_customer(merchant_acct, start_cursor, limit=50, return_with_cursor=True) 
                                                                                            
                logger.debug('=================>>>>>> ExecuteCreateMerchantRegisteredCustomerUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    for customer in result:
                        logger.debug('going to create upstream for customer name=%s', customer.name)
                        
                        create_merchant_registered_customer_upstream_for_merchant(customer)
                        create_registered_customer_upstream_for_system(customer)
                    
                    
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/merchant-registered-customer-upstream'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            } 
        
class TriggerCreateCustomerMembershipUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-customer-membership-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
        
class InitCreateCustomerMembershipUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        
        merchant_key = kwargs.get('merchant_key')
        
        
        db_client = create_db_client(caller_info="InitCreateMerchantRegisteredCustomerUpstrea")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
        
            count = CustomerMembership.count_merchant_customer_membership(merchant_acct)
            logger.debug('customer membership count=%d', count)
            
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/customer-membership-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteCreateCustomerMembershipUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateMerchantRegisteredCustomer")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
            if merchant_acct:
                
                (result, next_cursor) = CustomerMembership.list_merchant_customer_membership(merchant_acct, limit=50, start_cursor=start_cursor, return_with_cursor=True) 
                                                                                            
                logger.debug('=================>>>>>> ExecuteCreateMerchantRegisteredCustomerUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    for customer_membership in result:
                        customer = customer_membership.customer
                        if customer:
                            logger.debug('going to create upstream for customer name=%s', customer.name)
                        
                        create_customer_membership_upstream_for_merchant(customer_membership)
                    
                    
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/customer-membership-upstream'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }         
    
class TriggerCreateCustomerRewardUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-merchant-customer-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
        
class InitCreateCustomerRewardUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key = kwargs.get('merchant_key')
        
        
        db_client = create_db_client(caller_info="InitCreateCustomerRewardUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
        
            count = CustomerTransaction.count_merchant_transaction(merchant_acct)
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/merchant-customer-reward-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteCreateCustomerRewardUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateCustomerRewardUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
            if merchant_acct:
                
                (result, next_cursor) = CustomerTransaction.list_merchant_transaction(merchant_acct, start_cursor, limit=50, return_with_cursor=True) 
                                                                                            
                logger.debug('=================>>>>>> ExecuteCreateCustomerRewardUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    for transaction_details in result:
                        create_transction_reward_upstream(transaction_details)
                        
                    
                    
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/merchant-customer-reward-upstream'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
        
class TriggerCreateMerchantSalesUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-merchant-sales-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values  
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
        
class InitCreateMerchantSalesUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key = kwargs.get('merchant_key')
        
        
        db_client = create_db_client(caller_info="InitCreateMerchantSalesUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
        
            count = CustomerTransaction.count_merchant_transaction(merchant_acct)
            
            logger.debug('customer transaction count=%d', count)
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/merchant-sales-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteCreateMerchantSalesUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateMerchantSalesUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
            if merchant_acct:
                
                (result, next_cursor) = CustomerTransaction.list_merchant_transaction(merchant_acct, start_cursor, limit=50, return_with_cursor=True) 
                                                                                            
                logger.debug('=================>>>>>> ExecuteCreateMerchantSalesUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    for transaction_details in result:
                        create_merchant_customer_transaction_upstream_for_merchant(transaction_details, )
                        
                    
                    
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/merchant-sales-upstream'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }        
    
class TriggerCreateCustomerRedemptionUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-merchant-customer-redemption-upstream'
    
    def get_task_queue(self):
        return 'test'
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
        
class InitCreateCustomerRedemptionUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key = kwargs.get('merchant_key')
        
        logger.debug('InitCreateCustomerRedemptionUpstream debug: merchant_key=%s', merchant_key)
        
        db_client = create_db_client(caller_info="InitCreateCustomerRedemptionUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
        
            count = CustomerRedemption.count_merchant_redemption(merchant_acct)
        
        logger.debug('InitCreateCustomerRedemptionUpstream debug: count=%d', count)
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/merchant-customer-redemption-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        
        logger.debug('InitCreateCustomerRedemptionUpstream debug: get_data_payload merchant_key=%s', merchant_key)
        
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteCreateCustomerRedemptionUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('ExecuteCreateCustomerRedemptionUpstream debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateCustomerRedemptionUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
            if merchant_acct:
                
                (result, next_cursor) = CustomerRedemption.list_merchant_transaction(merchant_acct, start_cursor, limit=50, return_with_cursor=True) 
                                                                                            
                logger.debug('=================>>>>>> ExecuteCreateCustomerRedemptionUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    for redemption_details in result:
                        
                        create_redemption_upstream(redemption_details)    
                        
                    
                    
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/merchant-customer-redemption-upstream'    
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }

class TriggerUpdateMerchantUpstreamTable(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/update-merchant-upstream-table'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    @request_values
    def get_data_payload(self,  request_json):
        
        merchant_account_code   = request_json.get('merchant_account_code')
        table_name_prefix       = request_json.get('table_name_prefix')
        column_name             = request_json.get('column_name')
        column_data_type        = request_json.get('column_data_type')
        
        logger.debug('merchant_account_code=%s', merchant_account_code)
        logger.debug('table_name_prefix=%s', table_name_prefix)
        logger.debug('column_name=%s', column_name)
        logger.debug('column_data_type=%s', column_data_type)
        
        return {
            'merchant_account_code' : merchant_account_code,
            'table_name_prefix'     : table_name_prefix,
            'column_name'           : column_name,
            'column_data_type'      : column_data_type,
            }  

 
    
class ExecuteUpdateMerchantUpstreamTable(Resource):
    def post(self):
        return self.get()
    
    @request_values
    def get(self, request_values):
        merchant_account_code   = request_values.get('merchant_account_code')
        table_name_prefix       = request_values.get('table_name_prefix')
        column_name             = request_values.get('column_name')
        column_data_type        = request_values.get('column_data_type')
        
        logger.debug('merchant_account_code=%s', merchant_account_code)
        logger.debug('table_name_prefix=%s', table_name_prefix)
        logger.debug('column_name=%s', column_name)
        logger.debug('column_data_type=%s', column_data_type)
        
        
        merchant_dataset    = 'merchant_%s' % merchant_account_code
        tables_list         = []
        final_table_prefix  = '%s_' % (table_name_prefix)
        
        logger.debug('merchant_dataset=%s', merchant_dataset)
        logger.debug('final_table_prefix=%s', final_table_prefix)
        
        
        bg_client           = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID)
        dataset_ref         = bg_client.dataset(merchant_dataset)
        tables              = bg_client.list_tables(dataset_ref)
        
        for table in tables:
            if table.table_id.startswith(final_table_prefix):
                if matches_table_pattern(table.table_id, final_table_prefix):
                    tables_list.append(table.table_id)
                    
                    full_qualified_table_id='{project_id}.{dataset}.{table_id}'.format(project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset=merchant_dataset, table_id=table.table_id)
                    
                    logger.debug('full_qualified_table_id=%s', full_qualified_table_id)
                    
                    table_to_update = bg_client.get_table(full_qualified_table_id)
                    new_schema      = table_to_update.schema[:]
                    new_schema.append(bigquery.SchemaField(column_name, column_data_type))
                    
                    table.schema = new_schema
                    
                    bg_client.update_table(table_to_update, ["schema"])
                    logger.debug('after updated %s', full_qualified_table_id)

    
                
        return jsonify(tables_list)
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/update-merchant-upstream-table'    
    
    def get_data_payload(self):
        
        return {
        
            }

class TriggerCreateMerchantPartnershipRewardTransactionUpstream(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/upstream/init-merchant-partnership-reward-transaction-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values  
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        logger.debug('merchant_key=%s', merchant_key)
        return {
                'merchant_key': merchant_key,
            }    
        
class InitCreateMerchantPartnershipRewardTransactionUpstream(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key = kwargs.get('merchant_key')
        logger.debug('merchant_key=%s', merchant_key)
        
        db_client = create_db_client(caller_info="InitCreateMerchantPartnershipRewardTransactionUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
        
            count = PartnershipRewardTransaction.count_merchant_partnership_reward_transaction(merchant_acct)
            
            logger.debug('merchant partnership reward transaction count=%d', count)
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/upstream/merchant-partnership-reward-transaction-upstream'
    
    def get_task_queue(self):
        return 'upstream-maint'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteCreateMerchantPartnershipRewardTransactionUpstream(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        next_cursor     = None
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteCreateMerchantPartnershipRewardTransactionUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.get_or_read_from_cache(merchant_key)
            
            if merchant_acct:
                
                (result, next_cursor) = PartnershipRewardTransaction.list_merchant_partnership_reward_transaction(merchant_acct, start_cursor, limit=50, return_with_cursor=True) 
                                                                                            
                logger.debug('=================>>>>>> ExecuteCreateMerchantPartnershipRewardTransactionUpstream debug: result count=%s, next_cursor=%s', len(result), next_cursor)
                if result:
                    for transaction_details in result:
                        create_partnership_transaction_upstream_for_merchant(transaction_details)
                        
                    
                    
                
        return next_cursor
        
    def get_task_queue(self):
        return 'upstream-maint'   
    
    def get_task_url(self):
        return '/maint/upstream/merchant-partnership-reward-transaction-upstream'
    
    @request_values
    def get_data_payload(self, request_values):
        merchant_key=request_values.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
    
upstream_maintenance_setup_bp_api.add_resource(ModuleIndexResource,   '/index')

upstream_maintenance_setup_bp_api.add_resource(TriggerDeleteMerchantDatasetTable,   '/trigger-delete-merchant-dataset-table')
upstream_maintenance_setup_bp_api.add_resource(InitDeleteMerchantDatasetTable,   '/init-delete-merchant-dataset-table')
upstream_maintenance_setup_bp_api.add_resource(ExecuteDeleteMerchantDatasetTable,   '/delete-merchant-dataset-table')


upstream_maintenance_setup_bp_api.add_resource(TriggerCreateMerchantRegisteredCustomerUpstream,   '/trigger-merchant-registered-customer-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateMerchantRegisteredCustomerUpstream,   '/init-merchant-registered-customer-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateMerchantRegisteredCustomerUpstream,   '/merchant-registered-customer-upstream')

upstream_maintenance_setup_bp_api.add_resource(TriggerCreateCustomerMembershipUpstream,   '/trigger-customer-membership-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateCustomerMembershipUpstream,   '/init-customer-membership-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateCustomerMembershipUpstream,   '/customer-membership-upstream')
          
upstream_maintenance_setup_bp_api.add_resource(TriggerCreateMerchantSalesUpstream,   '/trigger-merchant-sales-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateMerchantSalesUpstream,   '/init-merchant-sales-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateMerchantSalesUpstream,   '/merchant-sales-upstream')

upstream_maintenance_setup_bp_api.add_resource(TriggerCreateCustomerRewardUpstream,   '/trigger-merchant-customer-reward-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateCustomerRewardUpstream,   '/init-merchant-customer-reward-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateCustomerRewardUpstream,   '/merchant-customer-reward-upstream')

upstream_maintenance_setup_bp_api.add_resource(TriggerCreateCustomerRedemptionUpstream,   '/trigger-merchant-customer-redemption-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateCustomerRedemptionUpstream,   '/init-merchant-customer-redemption-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateCustomerRedemptionUpstream,   '/merchant-customer-redemption-upstream')


upstream_maintenance_setup_bp_api.add_resource(TriggerCreateAllMerchantUpstream,   '/trigger-create-all-merchant-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateAllMerchantUpstream,   '/init-create-all-merchant-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateAllMerchantUpstream,   '/create-all-merchant-upstream')


upstream_maintenance_setup_bp_api.add_resource(TriggerCreateMerchantPartnershipRewardTransactionUpstream,   '/trigger-merchant-partnership-reward-transaction-upstream')
upstream_maintenance_setup_bp_api.add_resource(InitCreateMerchantPartnershipRewardTransactionUpstream,   '/init-merchant-partnership-reward-transaction-upstream')
upstream_maintenance_setup_bp_api.add_resource(ExecuteCreateMerchantPartnershipRewardTransactionUpstream,   '/merchant-partnership-reward-transaction-upstream')


upstream_maintenance_setup_bp_api.add_resource(TriggerUpdateMerchantUpstreamTable,   '/trigger-update-merchant-upstream-table')
upstream_maintenance_setup_bp_api.add_resource(ExecuteUpdateMerchantUpstreamTable,   '/update-merchant-upstream-table')


