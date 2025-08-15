'''
Created on 14 Apr 2020

@author: jacklok
'''
from flask import Blueprint, render_template, jsonify, url_for
from trexadmin.libs.flask.decorator.common_decorators import page_title
from trexadmin.libs.flask.decorator.security_decorators import login_required_rest
from trexlib.utils.log_util import get_tracelog
from trexadmin.libs.http import StatusCode
import logging
from trexconf import conf as lib_conf
from google.cloud import storage
from firebase_admin import firestore
from trexadmin.forms.test.test_forms import SendEmailForm, EncryptForm,\
    DecryptForm, AESEncryptForm, AESDecryptForm
from trexmail.email_helper import trigger_send_email
from trexweb.libs.http import create_rest_message
from trexlib.utils.google.cloud_tasks_util import create_task
from datetime import datetime
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexconf import conf as admin_conf
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexmodel.models.datastore.import_models import ImportCustomerFile
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.message_models import Message
from trexmodel.models.datastore.message_model_helper import create_transaction_message,\
    create_redemption_message
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexlib.utils.crypto_util import encrypt, decrypt, aes_encrypt, aes_decrypt,\
    generate_aes_256_keys, aes_encrypt_json, aes_decrypt_json
from trexlib.libs.flask_wtf.request_wrapper import request_headers, request_json,\
    request_form, request_args, session_value, request_values
from trexlib.libs.facebook.util.whatsapp_util import send_whatsapp_verification_message
from trexlib.utils.string_util import random_string, random_number
from trexapi.utils.push_notification_helper import create_prepaid_push_notification
from trexlib.utils.security_util import hash_password
from trexanalytics.controllers.importdata.import_upstream_data_routes import import_testing_upstream_data,\
    update_testing_upstream_data
from trexlib.utils.common.date_util import date_to_bigquery_qualified_datetime_str

test_bp = Blueprint('test_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/test'
                     )

logger = logging.getLogger('target_debug')






'''
Blueprint settings here
'''
@test_bp.context_processor
def test_bp_inject_settings():
    return dict(
                side_menu_group_name    = "test"
                )


@test_bp.route('/boostrap-divider', methods=['GET'])
@page_title('Bootstrap Divider')
def bootstrap_divider():
    return render_template("test/boostrap_divider.html", 
                           side_menu_item="bootstrap_divider",
                           page_title="Boostrap Divider",
                           page_url         = url_for('test_bp.bootstrap_divider'),
                           )

@test_bp.route('/bootstrap-breadcrumb', methods=['GET'])
@page_title('Bootstrap Breadcrumb')
def bootstrap_breadcrumb():
    return render_template("test/breadcrumb.html", 
                           side_menu_item="bootstrap_breadcrumb", 
                           page_title="Bootstrap Breadcrumb",
                           page_url         = url_for('test_bp.bootstrap_breadcrumb'),
                           )

@test_bp.route('/stripe-payment', methods=['GET'])
@page_title('Stripe Payment')
def stripe_payment():
    return render_template("test/stripe_payment.html", 
                           side_menu_item="stripe_payment",
                           page_title="Stripe Payment",
                           page_url         = url_for('test_bp.stripe_payment'),
                           )


@test_bp.route('/input-element', methods=['GET'])
def input_element():
    return render_template("test/input_element.html", 
                           side_menu_item="input_element",
                           page_title="Input Element",
                           page_url         = url_for('test_bp.input_element'),
                           )


@test_bp.route('/multi-tabs', methods=['GET'])
def multi_tabs():
    return render_template("test/multi_tabs.html", 
                           side_menu_item="multi_tabs",
                           page_title="Multi Tabs",
                           page_url         = url_for('test_bp.multi_tabs'),
                           )


@test_bp.route('/tab-profile', methods=['GET'])
def tab_profile():
    return render_template("test/test_profile_content.html", 
                           side_menu_item="multi_tabs")


@test_bp.route('/tab-contact', methods=['GET'])
def tab_contact():
    return render_template("test/test_contact_content.html", 
                           side_menu_item="multi_tabs")


@test_bp.route('/loading-content', methods=['GET'])
def loading_content():
    return render_template("test/loading_content.html", 
                           side_menu_item="loading_content",
                           page_title="Loading Content", 
                           LOADING_TEXT = "Please wait, your request are processing now",
                           LOADING_IMAGE_PATH=url_for('static', filename='app/assets/img/shared/loading.gif'),
                           page_url         = url_for('test_bp.loading_content'),
                           )
    
@test_bp.route('/show-modal', methods=['GET'])
def show_modal():
    return render_template("test/show_modal.html", 
                           side_menu_item   = "show_modal",
                           page_title       = "Show Modal", 
                           page_url         = url_for('test_bp.show_modal'),
                           )
@test_bp.route('/show-jdpdfprint', methods=['GET'])    
def show_jspdfprint():
    return render_template("test/show_jspdfprint.html", 
                           side_menu_item   = "show_jspdfprint",
                           page_title       = "Show jdPDF Print", 
                           page_url         = url_for('test_bp.show_jspdfprint'),
                           )
    
@test_bp.route('/show-stepper-horizontal', methods=['GET'])    
def show_stepper_horizontal():
    return render_template("test/show_stepper_horizontal.html", 
                           page_title       = "Show Stepper horizontal", 
                           page_url         = url_for('test_bp.show_stepper_horizontal'),
                           )
    
@test_bp.route('/show-stepper-vertical', methods=['GET'])    
def show_stepper_vertical():
    return render_template("test/show_stepper_vertical.html", 
                           page_title       = "Show Stepper Vertical", 
                           page_url         = url_for('test_bp.show_stepper_vertical'),
                           )
    
            

    
@test_bp.route('/show-using-cookie', methods=['GET'])
def show_using_cookie():
    return render_template("test/show_using_cookie.html", 
                            
                           )        

@test_bp.route('/test-required-authoized-rest', methods=['GET'])
@login_required_rest
def test_required_authoized_rest():
    return jsonify({
                    'msg': 'success'
                    })     

def _item_to_value(iterator, item):
    return item

def list_directories(bucket_name, prefix='/'):
    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter='/')

    folders = []
    for blob in blobs:
        folders.append(blob.name)
    
    return {
            'path': blobs.path,
            'folders': folders,
            }

@test_bp.route('/test-list-bucket-folders', methods=['GET'])
@login_required_rest
def test_list_bucket_folders():
    
    bucket_name = 'penefit-storage'
    
    return jsonify({
                    'bucket_name': bucket_name,
                    'bucket_details': list_directories(bucket_name, prefix='merchant/')
                    })     

@test_bp.route('/test-list-bucket', methods=['GET'])
@login_required_rest
def test_list_bucket():
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    buckets_list = []
    for b in buckets:
        buckets_list.append({
                            'name': b.name,
                            'path': b.path,
                            })
    
    return jsonify({
                    
                    'buckets': buckets_list
                    })   
    
@test_bp.route('/sample-chartjs-1', methods=['GET'])    
def show_sample_chartjs_1_page():
    return render_template("test/sample_chartjs_1.html", 
                           )    
    
@test_bp.route('/dev-test', methods=['GET'])    
def show_dev_test_page():
    return render_template("test/show_dev_test.html", 
                           page_title       = "Development Test", 
                           page_url         = url_for('test_bp.show_dev_test_page'),
                           )

@test_bp.route('/treeview-menu-1', methods=['GET'])
def show_treeview_menu1():
    return render_template("test/show_treeview_menu1.html", 
                           page_title="Treeview Menu",
                           page_url         = url_for('test_bp.show_treeview_menu1'),
                           )    

@test_bp.route('/treeview-menu-2', methods=['GET'])
def show_treeview_menu2():
    return render_template("test/show_treeview_menu2.html", 
                           page_title="Treeview Menu",
                           page_url         = url_for('test_bp.show_treeview_menu2'),
                           )   
    
@test_bp.route('/show-firebase-counter', methods=['GET'])
def show_firebase_counter():
    firebase = firestore.client()        
    counter_ref = firebase.collection('test').document('counter')
    
    counter = counter_ref.get()
    counter_value = 0
    
    logger.debug('Found counter, counter=%s', counter)
    
    if counter is not None:
        
        counter_value = counter.get('value')
        
        logger.debug('Found counter, counter_value=%s', counter_value)
        if counter_value is None:
            counter_value = 0
            
            counter_ref.set({
                'value': counter_value
            })
        
    else:
        counter_ref.set({
            'value': 0
        })
        
    return render_template("test/update_counter.html", 
                            counter_value = counter_value,
                           )
    
@test_bp.route('/plus-firebase-counter', methods=['GET', 'POST'])
def plus_firebase_counter():
    firebase = firestore.client()       
    counter_ref = firebase.collection('test').document('counter')
    
    counter = counter_ref.get()
    
    if counter:
        
        counter_value = counter.get('value') + 1
        logger.debug('Found counter, counter_value=%d', counter_value)
        
        
        counter_ref.set({
            'value': counter_value
        })
    else:
        counter_ref.set({
            'value': 1
        })
        
    return jsonify({
                    
                    'counter_value': counter_value
                    })  
        
@test_bp.route('/minus-firebase-counter', methods=['GET', 'POST'])
def minus_firebase_counter():
    firebase = firestore.client()
    counter_ref = firebase.collection('test').document('counter')
    
    counter = counter_ref.get()
    
    if counter:
        
        counter_value = counter.get('value')
        
        counter_value = counter_value-1 if counter_value>0 else 0
        
        logger.debug('Found counter, counter_value=%d', counter_value)
        
        
        counter_ref.set({
            'value': counter_value
        })
    else:
        counter_ref.set({
            'value': 0
        }) 
        
    return jsonify({
                    
                    'counter_value': counter_value
                    })   
    
@test_bp.route('/qr-code', methods=['GET'])
@request_args
def show_qr_code(request_args):
    qr_code = request_args.get('value')
    
    logger.debug('qr_code=%s', qr_code)
    
    return render_template("test/qr_code.html", 
                            qr_code = qr_code,
                           )
    
@test_bp.route('/send-email', methods=['get'])
def send_email():
    return render_template("test/send_email.html", 
                           page_title="Send Email",
                           page_url         = url_for('test_bp.send_email'),
                           post_url         = url_for('test_bp.send_email_post'),
                           )
        

@test_bp.route('/send-email', methods=['post'])
@request_form
def send_email_post(send_email_data):
    logger.info('--- submit send_email_post data ---')
    
    logger.info('send_email_data=%s', send_email_data)
    
    send_email_form = SendEmailForm(send_email_data)
    
    
    try:
        if send_email_form.validate():
            send_to       = send_email_form.send_to.data
            subject       = send_email_form.subject.data
            message       = send_email_form.message.data
            
            trigger_send_email(recipient_address = send_to, subject=subject, message=message)
                    
            return create_rest_message('Email have been sent', status_code=StatusCode.OK)
            #return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = send_email_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to send email due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
    
@test_bp.route('/create-program-task', methods=['get'])
def create_program_task():
    
    task_url    = '%s%s' % (lib_conf.SYSTEM_BASE_URL, '/program/task/tier-program/reward-consume')
    queue_name  = 'test'
    
    payload = {
                'program_key': 'value1',
                'customer_key': 'value2',
                'transaction_id': 'value3',
                'task_url': task_url,
                }
    
    create_task(task_url, queue_name, 
                in_seconds      = 1,
                http_method     = 'post', 
                payload         = payload,
                credential_path = lib_conf.SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                project_id      = lib_conf.SYSTEM_TASK_GCLOUD_PROJECT_ID,
                location        = lib_conf.SYSTEM_TASK_GCLOUD_LOCATION,
                service_email   = lib_conf.SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                )  
    
    return jsonify(payload) 


@test_bp.route('/read-credential-config', methods=['get'])
def get_credential_config():
    config = read_config('credential_config.txt')
    return create_rest_message(**config,
                               status_code=StatusCode.OK)

@test_bp.route('/show-local-datetime', methods=['get'])
def show_local_datetime():
    return jsonify({'now': datetime.now()})

@test_bp.route('/import/customer/merchant-acct/<merchant_key>', methods=['get'])
def read_merchant_import_customer_file(merchant_key):
    db_client = create_db_client(caller_info="read_merchant_import_customer_file")
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        
        bucket              = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)
        (file_size, rows)   = ImportCustomerFile.read_file(merchant_acct, bucket)
        
    return jsonify({
            'file_size' : file_size,
            'rows'      : rows,
            })
    
@test_bp.route('/show-transction-entitled-message-content/customer-transaction/<transction_key>', methods=['get'])
@session_value
def show_transaction_entitled_message_content(session_value, transction_key):
    db_client = create_db_client(caller_info="show_transaction_entitled_message_content")
    transaction_id = ''
    created_datetime = datetime.now()
    with db_client.context():
        customer_transaction = CustomerTransaction.fetch(transction_key)
        if customer_transaction:
            transaction_id = customer_transaction.transaction_id
            message_content = create_transaction_message(customer_transaction)    
            created_datetime = customer_transaction.created_datetime
        else:
            message_content='<html><body>Sorry, failed to construct message</body></html>'
        
        message_content_dict = message_content.to_dict()
    
    country_code          = session_value.get('country') or lib_conf.DEFAULT_COUNTRY_CODE
        
    #local_datetime = from_utc_datetime_to_local_datetime(created_datetime, country_code=country_code)    
        
    '''
    return jsonify({
            'transaction_id'    : transaction_id,
            'message_type'      : MESSAGE_CATEGORY_REWARD,
            'created_datetime'  : datetime.strftime(local_datetime, '%d %b %Y %H:%M'),
            'content_type'      :'html',
            'message_content'   : message_content,
            })  
    
    return render_template('test/test_message_content.html',
                           )
    '''
    
    return jsonify(message_content_dict)

@test_bp.route('/show-message-content/message/<message_key>', methods=['get'])
def show_message_content(message_key):
    db_client = create_db_client(caller_info="show_message_content")

    with db_client.context():
        message = Message.fetch(message_key)
        customer_transaction = message.customer_transaction_entity
    
    if message and customer_transaction:
        message_content = message.message_content.get('content')
        #message_content_in_json = create_entiled_message(customer_transaction)
        #message_content = message_content_in_json.get('content')
    else:
        message_content='<html><body>Sorry, failed to construct message</body></html>'
    
        
    return message_content

@test_bp.route('/show-redemption-message-content/customer-redemption/<customer_redemption_key>', methods=['get'])
def show_redemption_message_content(customer_redemption_key):
    db_client = create_db_client(caller_info="show_redemption_message_content")
    
    with db_client.context():
        customer_redemption  = CustomerRedemption.fetch(customer_redemption_key)
        message = create_redemption_message(customer_redemption)
        message = message.to_dict()
    
    return jsonify(message)

@test_bp.route('/fernet-encrypt', methods=['post'])
@request_form
def test_fernet_encrypt(encrypt_data):
    logger.debug('--- submit test_fernet_encrypt data ---')
    
    logger.info('encrypt_data=%s', encrypt_data)
    
    encrypt_form = EncryptForm(encrypt_data)
    
    plain_text = encrypt_form.plain.data
    fernet_key = encrypt_form.fernet_key.data
    
    logger.debug('plain text=%s', plain_text)
    logger.debug('fernet key=%s', fernet_key)
    
    encrypted_text = encrypt(plain_text, fernet_key=fernet_key)
    
    return jsonify({
            'encrypted': encrypted_text
            })
    
@test_bp.route('/aes-encrypt', methods=['post'])
@request_form
def test_aes_encrypt(request_form):
    logger.debug('--- submit test_aes_encrypt data ---')
    
    logger.info('request_form=%s', request_form)
    
    encrypt_form = AESEncryptForm(request_form)
    
    aes_key = encrypt_form.aes_key.data
    
    logger.debug('plain text=%s', plain_text)
    logger.debug('aes_key=%s', aes_key)
    
    encrypted_text = aes_encrypt(plain_text, key=aes_key)
    
    return jsonify({
            'encrypted': encrypted_text
            }) 
    
@test_bp.route('/aes-encrypt-json', methods=['post'])
@request_json
def test_aes_json_encrypt(request_json):
    logger.debug('--- submit test_aes_json_encrypt data ---')
    
    logger.info('request_json=%s', request_json)
    
    json_data = request_json.get('json_data')
    aes_key = request_json.get('aes_key')
    
    
    logger.debug('json_data text=%s', json_data)
    logger.debug('aes_key=%s', aes_key)
    
    encrypted_text = aes_encrypt_json(json_data, key=aes_key)
    
    return jsonify({
            'encrypted': encrypted_text
            })        

@test_bp.route('/generate-aes-32b-key', methods=['get'])
def test_generate_aes_key():
    keys = generate_aes_256_keys(num_keys=1, bytes_count=32)
    
    return jsonify({
            'keys': keys
            })


from collections import defaultdict
def to_multidict(single_dict):
    multi_dict = defaultdict(list)
    for key, value in single_dict.items():
        multi_dict[key].append(value)

@test_bp.route('/fernet-decrypt', methods=['post'])
@request_form
def test_fernet_decrypt(decrypt_data):
    logger.debug('--- submit test_fernet_decrypt data ---')
    #decrypt_data = request.form
    
    logger.info('decrypt_data=%s', decrypt_data)
    
    decrypt_form = DecryptForm(decrypt_data)
    
    encrypted = decrypt_form.encrypted.data
    fernet_key = decrypt_form.fernet_key.data
    
    logger.debug('encrypted=%s', encrypted)
    logger.debug('fernet key=%s', fernet_key)
    
    plain_text = decrypt(encrypted, fernet_key=fernet_key)
    
    return jsonify({
            'decrypted': plain_text
            })

@test_bp.route('/aes-decrypt', methods=['post'])
@request_form
def test_aes_decrypt(decrypt_data):
    logger.debug('--- submit test_aes_decrypt data ---')
    #decrypt_data = request.form
    
    logger.info('decrypt_data=%s', decrypt_data)
    
    decrypt_form = AESDecryptForm(decrypt_data)
    
    encrypted = decrypt_form.encrypted.data
    aes_key = decrypt_form.aes_key.data
    
    logger.debug('encrypted=%s', encrypted)
    logger.debug('aes_key=%s', aes_key)
    
    plain_text = aes_decrypt(encrypted, key=aes_key)
    
    return jsonify({
            'decrypted': plain_text
            })
    
@test_bp.route('/aes-decrypt-json', methods=['post'])
@request_form
def test_aes_decrypt_json(decrypt_data):
    logger.debug('--- submit test_aes_decrypt_json data ---')
    #decrypt_data = request.form
    
    logger.info('decrypt_data=%s', decrypt_data)
    
    decrypt_form = AESDecryptForm(decrypt_data)
    
    encrypted = decrypt_form.encrypted.data
    aes_key = decrypt_form.aes_key.data
    
    logger.debug('encrypted=%s', encrypted)
    logger.debug('aes_key=%s', aes_key)
    
    decrypted_json = aes_decrypt_json(encrypted, key=aes_key)
    
    return decrypted_json   

@test_bp.route('/test-decorator', methods=['GET','POST'])
@request_headers
@request_json
@request_args
def app_test(headers, json_data, request_values):
    return jsonify({
            'headers': headers,
            'json_data': json_data,
            'request_values':request_values,
            }) 


@test_bp.route('/test-send-whatsapp-verification-code', methods=['GET','POST'])
@request_args
def test_send_whatsapp_verification_code(request_args):
    mobile_phone        = request_args.get('mobile_phone')
    request_id          = request_args.get('request_id')
    
    logger.debug('mobile_phone=%s', mobile_phone)
    logger.debug('request_id=%s', request_id)
    
    request_id = random_string(4, is_human_mistake_safe=True)
    verification_code = random_number(6)
    
    send_whatsapp_verification_message(mobile_phone, verification_code, request_id=request_id)
    
    return jsonify({
            'mobile_phone':mobile_phone,
            'request_id':request_id,
            'verification_code':verification_code,
            })     



@test_bp.route('/generate-hashed-password', methods=['get'])
@request_args
def generate_hashed_password(request_args):
    unique_id           = request_args.get('unique_id','')
    password            = request_args.get('password')
    
    logger.debug('unique_id=%s', unique_id)
    logger.debug('password=%s', password)
    
    hashed_password = hash_password(unique_id, password)
    
    return create_rest_message(status_code=StatusCode.OK, hashed_password=hashed_password) 
 
@test_bp.route('/send-prepaid-push-notification', methods=['get'])
@request_args
def send_device_prepaid_push_notification(request_args):
    title            = request_args.get('title')
    message          = request_args.get('message')
    device_token     = request_args.get('device_token')
    language_code    = request_args.get('language_code')
    
    create_prepaid_push_notification(
                        title_data=title, 
                        message_data = message,
                        speech = message,
                        device_token = device_token,
                        language_code = language_code,
                        
                    )
        
    return create_rest_message(status_code=StatusCode.OK) 

@test_bp.route('/import-testing-upstream', methods=['get'])
@request_values
def import_testing_upstream(request_values):
    test_key    = request_values.get('test_key')
    test_value  = request_values.get('test_value')
    
    logger.debug('test_key=%s', test_key)
    logger.debug('test_value=%s', test_value)
    
    testing_json = {
            'test_key'  : test_key,
            'test_value': test_value,
            'updated_datetime'  : date_to_bigquery_qualified_datetime_str(datetime.utcnow())
            }
    
    import_testing_upstream_data(testing_json)
    
    return create_rest_message(status_code=StatusCode.OK, testing_json=testing_json)

@test_bp.route('/update-testing-upstream', methods=['get'])
@request_values
def update_testing_upstream(request_values):
    test_key    = request_values.get('test_key')
    test_value  = request_values.get('test_value')
    
    logger.debug('test_key=%s', test_key)
    logger.debug('test_value=%s', test_value)
    
    update_testing_data_json = {
        'updated_fields':{
                'test_value': test_value,
                },
        'condition_fields':{
                'test_key': test_key,
                },
        }
    
    update_testing_upstream_data(update_testing_data_json)
    
    return create_rest_message(status_code=StatusCode.OK, update_testing_data_json=update_testing_data_json)
    
    
    
    