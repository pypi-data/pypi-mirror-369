'''
Created on 3 Oct 2023

@author: jacklok
'''
import logging
from flask import Blueprint, request
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.import_models import ConfirmedImportCustomerFile,\
    ImportFailedCustomerData
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexconf.conf import SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, SYSTEM_TASK_GCLOUD_PROJECT_ID, SYSTEM_TASK_GCLOUD_LOCATION, SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
from trexconf import conf as admin_conf
from trexlib.utils.google.cloud_tasks_util import create_task
from trexadmin.libs.http import StatusCode, create_rest_message
from _datetime import datetime
from trexadmin.helpers.import_customer_helper import create_import_customer
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.customer_models import Customer
from trexlib.utils.sms_util import send_sms
from trexlib.libs.flask_wtf.request_wrapper import request_args, request_json

import_customer_tasks_bp = Blueprint('import_customer_tasks_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/tasks/import/customer')

logger = logging.getLogger('task')

@import_customer_tasks_bp.route('/check-bucket-permission', methods=['GET'])
def check_bucket_permission():
    
    bucket              = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
    if bucket:
        return "Bucket is permitted path %s-%s" % (admin_conf.STORAGE_CREDENTIAL_PATH, datetime.now()), 200
    
    
    return "Bucket is not permitted path %s-%s" % (admin_conf.STORAGE_CREDENTIAL_PATH, datetime.now()), 200

@import_customer_tasks_bp.route('/check-credential-path', methods=['GET'])
def check_credential_path():
    return "credential path %s-%s" % (admin_conf.STORAGE_CREDENTIAL_PATH, datetime.now()), 200


@import_customer_tasks_bp.route('/from-file/<import_customer_file_key>/trigger', methods=['GET'])
def import_customer_from_file_trigger(request_args, import_customer_file_key):
    
    task_url        = '%s/tasks/import/customer/from-file/%s'% (admin_conf.IMPORT_BASE_URL, import_customer_file_key)
    queue_name      = 'default'
    payload         = {}
    
    create_task(task_url, queue_name, payload=payload, 
                            in_seconds      = 1, 
                            http_method     = 'GET',
                            credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                            project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                            location        = SYSTEM_TASK_GCLOUD_LOCATION,
                            service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                            ) 
    
    
    return "Triggered after %s" % datetime.now(), 200

@import_customer_tasks_bp.route('/from-file/<import_customer_file_key>/inform-message/via/<message_type>/trigger', methods=['GET'])
@request_args
def inform_customer_from_file_trigger(request_args, import_customer_file_key, message_type):
    task_url        = '%s/tasks/import/customer/from-file/%s/inform-message/via/%s'% (admin_conf.IMPORT_BASE_URL, import_customer_file_key, message_type)
    queue_name      = 'default'
    message         = request_args.get('message')
    payload         = {'message':message}
    
    
    create_task(task_url, queue_name, payload=payload, 
                            in_seconds      = 1, 
                            http_method     = 'POST',
                            credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                            project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                            location        = SYSTEM_TASK_GCLOUD_LOCATION,
                            service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                            ) 
    
    
    return "Triggered after %s, message_type=%s, message=%s" % (datetime.now(),message_type, message), 200

@import_customer_tasks_bp.route('/from-file-failed-checking/<import_customer_file_key>/trigger', methods=['GET','POST'])
def import_customer_from_file_failed_checking_trigger(import_customer_file_key):
    task_url        = '%s/tasks/import/customer/from-file-failed-checking/%s'% (admin_conf.IMPORT_BASE_URL, import_customer_file_key)
    queue_name      = 'default'
    payload         = {}
    
    create_task(task_url, queue_name, payload=payload, 
                            in_seconds      = 1, 
                            http_method     = 'GET',
                            credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                            project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                            location        = SYSTEM_TASK_GCLOUD_LOCATION,
                            service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                            ) 
    
    return "Triggered after %s" % datetime.now(), 200

@import_customer_tasks_bp.route('/from-file/<import_customer_file_key>/inform-message/via/<message_type>', methods=['GET','POST'])
@request_json
def inform_customer_from_file(request_json, import_customer_file_key, message_type):
    
    db_client           = create_db_client(caller_info="inform_customer_from_file")
    
    bucket              = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
    rows                = []
    
    sms_message         = request_json.get('message')
    
    with db_client.context():
        import_customer_file    = ConfirmedImportCustomerFile.fetch(import_customer_file_key)
        if import_customer_file:
            if import_customer_file.is_ready:
                rows = import_customer_file.read_customer_data_rows(bucket)
            
        if rows:
            for row in rows:
                payload = row
                logger.info('payload=%s', payload)
                
                email           = payload.get('email')
                mobile_phone    = payload.get('mobile_phone')
                
                if message_type=='email':
                    if email is not None:
                        logger.info('inform via email')
                
                elif message_type=='sms':
                    if mobile_phone is not None:
                        logger.info('inform via sms')
                        send_sms(to_number=mobile_phone, body=sms_message)
                        
                elif message_type=='email_or_sms':
                    if email is not None:
                        logger.info('inform via email')
                        
                
               
                
    return "Triggered after %s" % datetime.now(), 200

@import_customer_tasks_bp.route('/from-file-failed-checking/<import_customer_file_key>', methods=['GET','POST'])
def import_customer_from_file_failed_checking(import_customer_file_key):
    db_client           = create_db_client(caller_info="import_customer_from_file")
    
    bucket              = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
    rows                = []
    
    
    
    with db_client.context():
        import_customer_file    = ConfirmedImportCustomerFile.fetch(import_customer_file_key)
        merchant_acct           = import_customer_file.merchant_acct_entity
        if import_customer_file:
            if import_customer_file.is_ready:
                rows = import_customer_file.read_customer_data_rows(bucket)
            
        if rows:
            for row in rows:
                payload = row
                logger.info('payload=%s', payload)
                
                email           = payload.get('email')
                mobile_phone    = payload.get('mobile_phone')
                
                if email is not None:
                    created_customer = Customer.get_by_email(email, merchant_acct=merchant_acct)
                elif mobile_phone is not None:
                    created_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
                        
                if created_customer is None:
                    ImportFailedCustomerData.create(merchant_acct, payload)
                
                
                
    return "Triggered after %s" % datetime.now(), 200

@import_customer_tasks_bp.route('/from-file/<import_customer_file_key>', methods=['GET'])
def import_customer_from_file(import_customer_file_key):
    db_client           = create_db_client(caller_info="import_customer_from_file")
    
    bucket              = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
    rows                = []
    
    
    
    merchant_acct_key   = None
    with db_client.context():
        import_customer_file   = ConfirmedImportCustomerFile.fetch(import_customer_file_key)
        merchant_acct = MerchantAcct.fetch(merchant_acct_key)
        if import_customer_file:
            merchant_acct_key = import_customer_file.merchant_acct_key
            if import_customer_file.is_ready:
                rows = import_customer_file.read_customer_data_rows(bucket)
            
        if rows:
            task_url        = '%s/tasks/import/customer/create'% admin_conf.IMPORT_BASE_URL
            queue_name      = 'import'
            
            
            logger.debug('rows=%s', rows)
            
            for row in rows:
                payload = row
                payload['merchant_acct_key']    = merchant_acct_key
                payload['default_password']     = import_customer_file.import_settings.get('default_password')
                payload['registered_outlet']    = import_customer_file.import_settings.get('registered_outlet')
                
                payload.update(import_customer_file.import_settings.get('reward_program_settings'))
                
                logger.info('payload=%s', payload)
                
                create_import_customer(payload, merchant_acct)
                '''
                create_task(task_url, queue_name, payload=payload, 
                            in_seconds      = 1, 
                            http_method     = 'POST',
                            credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                            project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                            location        = SYSTEM_TASK_GCLOUD_LOCATION,
                            service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                            ) 
                '''
    return "Triggered after %s" % datetime.now(), 200

@import_customer_tasks_bp.route('/create', methods=['POST'])
def create_import_customer_post():
    customer_data       = request.get_json()
    merchant_acct_key   = customer_data.get('merchant_acct_key')
    logger.info('merchant_acct_key=%s', merchant_acct_key)
    logger.info('customer_data=%s', customer_data)
    
    
    db_client = create_db_client(caller_info="import_customer_from_file")
    with db_client.context():
        try:
            merchant_acct = MerchantAcct.fetch(merchant_acct_key)
            if merchant_acct:
                logger.info('Going to import to %s', merchant_acct.brand_name)
                create_import_customer(customer_data, merchant_acct)
            else:
                logger.info('Merchant account not found')
        except:
            logger.error('Failed to import customer due to %s', get_tracelog())
    
    return create_rest_message(status_code=StatusCode.OK)
