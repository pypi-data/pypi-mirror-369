'''
Created on 26 Sep 2023

@author: jacklok
'''

from flask import Blueprint, render_template, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask_babel import gettext
import jinja2
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexmodel.models.datastore.import_models import ImportCustomerFile
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
    
from trexconf.conf import SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, SYSTEM_TASK_GCLOUD_PROJECT_ID, SYSTEM_TASK_GCLOUD_LOCATION, SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
from trexconf import conf as admin_conf, conf
from trexlib.utils.google.cloud_tasks_util import create_task
from flask.globals import request


import_customer_bp = Blueprint('import_customer_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/import/customer')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@import_customer_bp.context_processor
def import_customer_bp_inject_settings():
    
    return dict(
                
                )


@import_customer_bp.route('/merchant/<merchant_key>', methods=['GET'])
@login_required
def import_customer(merchant_key): 
    
    db_client = create_db_client(caller_info="import_customer")
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(merchant_key)
        
        outlets_list            = Outlet.list_by_merchant_acct(merchant_acct)
        
        prepaid_programs_list   = merchant_acct.list_data_import_giveaway_prepaid_programs()
        point_programs_list     = merchant_acct.list_data_import_giveaway_point_programs()
        stamp_programs_list     = merchant_acct.list_data_import_giveaway_stamp_programs()
        
        
    
    return render_template('admin/import/customer/import_customer.html', 
                       page_title                                   = gettext('Import Customer'),
                       merchant_key                                 = merchant_key,
                       
                       upload_customer_file_url                     = url_for('import_customer_bp.upload_customer_file_post'),
                       uploaded_file_content_url                    = url_for('import_customer_bp.show_uploaded_customer_file', merchant_key=merchant_key),
                       define_customer_account_settings_url         = url_for('import_customer_bp.define_customer_account_settings'),
                       define_import_customer_reward_settings_url   = url_for('import_customer_bp.define_reward_program_settings'),
                       import_review_content_url                    = url_for('import_customer_bp.import_review', merchant_key=merchant_key),
                       import_customer_confirm_status_url           = url_for('import_customer_bp.confirm_status'),
                       
                       outlets_list                                 = outlets_list,
                       prepaid_programs_list                        = prepaid_programs_list,
                       point_programs_list                          = point_programs_list,
                       stamp_programs_list                          = stamp_programs_list,
                       )
        
@import_customer_bp.route('/upload-customer-file', methods=['POST'])
@login_required
def upload_customer_file_post():
    merchant_key            = request.form.get('merchant_key')
    uploaded_file           = request.files.get('file')
    
    logger.debug('merchant_key=%s', merchant_key)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    
    db_client = create_db_client(caller_info="upload_customer_file_post")
    with db_client.context():
        merchant_acct   = MerchantAcct.fetch(merchant_key)
        bucket          = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
        customer_file   = ImportCustomerFile.upload_file(merchant_acct, uploaded_file, bucket)
            
        if customer_file:
            customer_file = customer_file.to_dict()
        
            logger.debug('After uploaded import customer file')
            
        else:
            logger.warn('Failed to fetch import  customer data')
         
    if customer_file:
        return create_rest_message(status_code=StatusCode.OK)
    else: 
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@import_customer_bp.route('/merchant/<merchant_key>/uploaded-customer-file-content', methods=['GET'])
@login_required
def show_uploaded_customer_file(merchant_key): 
    db_client = create_db_client(caller_info="upload_customer_file_post")
    total_count     = 0
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(merchant_key)
            
            bucket              = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
            rows                = ImportCustomerFile.read_file(merchant_acct, bucket)
            total_count         = len(rows)
        
        logger.debug('rows=%s', rows)
        logger.debug('total_count=%s', total_count)
    except:
        logger.error('Failed due to %s', get_tracelog())
            
    return render_template('admin/import/customer/uploaded_customer_file_content.html', 
                       merchant_key     = merchant_key,
                       total_count      = total_count,
                       data_info        = _import_data_study(rows),
                       )  
    
@import_customer_bp.route('/merchant/<merchant_key>/import-review', methods=['GET'])
@login_required
def import_review(merchant_key): 
    db_client   = create_db_client(caller_info="import_review")
    data_info   = {}
    total_count = 0
    try:
        with db_client.context():
            merchant_acct           = MerchantAcct.fetch(merchant_key)
            import_customer_file    = ImportCustomerFile.get(merchant_acct) 
            bucket                  = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
            rows                    = ImportCustomerFile.read_file(merchant_acct, bucket, import_customer_file=import_customer_file)
            data_info               = _import_data_study(rows)
            total_count             = len(rows)
        
        logger.debug('rows=%s', rows)
        if import_customer_file:
            reward_program_settings = import_customer_file.import_settings.get('reward_program_settings')
            logger.debug('reward_program_settings=%s', reward_program_settings)
            data_info.update(reward_program_settings)
            
            logger.debug('data_info=%s', data_info)
            '''
            if is_not_empty(reward_program_settings.get('prepaid_cash_program')):
                data_info['prepaid_cash_program'] = reward_program_settings.get('prepaid_cash_program')
                
            if is_not_empty(reward_program_settings.get('point_program')):
                data_info['point_program'] = reward_program_settings.get('point_program')
                
            if is_not_empty(reward_program_settings.get('stamp_program')):
                data_info['stamp_program'] = reward_program_settings.get('stamp_program')    
            '''
    except:
        logger.error('Failed due to %s', get_tracelog())
            
    return render_template('admin/import/customer/import_customer_review_content.html', 
                       merchant_key     = merchant_key,
                       data_info        = data_info,
                       total_count      = total_count,
                       )      

def _import_data_study(import_data_rows):
    email_only_count                    = 0
    mobile_phone_only_count             = 0
    email_and_mobile_phone_only_count   = 0
    no_email_and_mobile_phone_count     = 0
    customer_data_count                 = len(import_data_rows)
    import_count                        = 0
    
    
    for customer_data in import_data_rows:
        if is_not_empty(customer_data.get('email')):
            if is_not_empty(customer_data.get('mobile_phone')):
                email_and_mobile_phone_only_count+=1
                import_count+=1
            else:
                email_only_count+=1
                import_count+=1
        else:
            if is_not_empty(customer_data.get('mobile_phone')):
                mobile_phone_only_count+=1
                import_count+=1
            else:
                no_email_and_mobile_phone_count+=1
    
    return {
            'email_only_count'                  : email_only_count,
            'mobile_phone_only_count'           : mobile_phone_only_count,
            'email_and_mobile_phone_only_count' : email_and_mobile_phone_only_count,
            'no_email_and_mobile_phone_count'   : no_email_and_mobile_phone_count,
            'import_count'                      : import_count,
            'customer_data_count'               : customer_data_count,
        }
            
@import_customer_bp.route('/define-customer-account-settings', methods=['POST'])
@login_required
def define_customer_account_settings():
    merchant_key                = request.form.get('merchant_key')
    registered_outlet           = request.form.get('registered_outlet')
    default_password            = request.form.get('default_password')
    
    logger.debug('registered_outlet=%s', registered_outlet)
    logger.debug('default_password=%s', default_password)
    
    db_client = create_db_client(caller_info="define_customer_account_settings")
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(merchant_key)
            ImportCustomerFile.define_account_settings(merchant_acct, 
                                                        registered_outlet=registered_outlet, 
                                                        default_password=default_password)
        
        return create_rest_message(status_code=StatusCode.OK)
    except:
        logger.error('Failed due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to define customer account settings'), status_code=StatusCode.BAD_REQUEST)

@import_customer_bp.route('/define-reward-program-settings', methods=['POST'])
@login_required
def define_reward_program_settings():
    merchant_key            = request.form.get('merchant_key')
    prepaid_cash_program    = request.form.get('prepaid_cash_program')
    point_program           = request.form.get('point_program')
    stamp_program           = request.form.get('stamp_program')
    
    logger.debug('prepaid_cash_program=%s', prepaid_cash_program)
    logger.debug('point_program=%s', point_program)
    logger.debug('stamp_program=%s', stamp_program)
    
    db_client = create_db_client(caller_info="update_reward_program_settings")
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(merchant_key)
            reward_program_settings = {}
            
            if is_not_empty(prepaid_cash_program):
                reward_program_settings['prepaid_cash_program'] = prepaid_cash_program
                
            if is_not_empty(point_program):
                reward_program_settings['point_program'] = point_program
                
            if is_not_empty(stamp_program):
                reward_program_settings['stamp_program'] = stamp_program
                        
            ImportCustomerFile.update_reward_program_settings(merchant_acct, reward_program_settings)
        
        return create_rest_message(status_code=StatusCode.OK)
    except:
        return create_rest_message(gettext('Failed to define reward program settings'), status_code=StatusCode.BAD_REQUEST)
    
@import_customer_bp.route('/confirm', methods=['POST'])
@login_required
def confirm_status():
    merchant_key            = request.form.get('merchant_key')
    
    db_client = create_db_client(caller_info="confirm_status")
    try:
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(merchant_key)
            
            import_customer_file = ImportCustomerFile.confirm_status(merchant_acct)
            
        task_url        = '%s/tasks/import/customer/from-file/%s' % (conf.IMPORT_BASE_URL ,import_customer_file.key_in_str)
        queue_name      = 'dispatch'
        
        logger.debug('task_url=%s', task_url)
        
        create_task(task_url, queue_name, 
                    in_seconds      = 1, 
                    http_method     = 'GET',
                    credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                    project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                    location        = SYSTEM_TASK_GCLOUD_LOCATION,
                    service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                    )    
        
        return create_rest_message(status_code=StatusCode.OK)
    except:
        logger.error('Failed to confirm status due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to confirm customer import'), status_code=StatusCode.BAD_REQUEST)    
