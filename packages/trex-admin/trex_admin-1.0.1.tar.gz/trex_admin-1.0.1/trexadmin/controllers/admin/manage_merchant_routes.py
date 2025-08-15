'''
Created on 15 May 2020

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for, current_app
from trexadmin.forms.merchant.merchant_forms import AddMerchantForm, MerchantSearchForm
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.utils.model.model_util import create_db_client
from trexlib.utils.string_util import is_not_empty, is_empty
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexlib.utils.log_util import get_tracelog
from trexadmin.libs.flask.pagination import Pager, CursorPager
import logging
from datetime import datetime
from trexconf import conf as admin_conf  
from flask_babel import gettext
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexadmin.conf import PAGINATION_SIZE
from trexlib.utils.crypto_util import encrypt_json, decrypt_json
from trexadmin.controllers.system.system_route_helpers import get_country_timezone_list_json
from trexlib.utils.google.cloud_tasks_util import create_task
from trexconf.conf import SYSTEM_TASK_SERVICE_CREDENTIAL_PATH,\
    SYSTEM_TASK_GCLOUD_PROJECT_ID, SYSTEM_TASK_GCLOUD_LOCATION,\
    SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL, BIGQUERY_SERVICE_CREDENTIAL_PATH,\
    MERCHANT_DATASET
from trexanalytics.controllers.main_routes import create_bigquery_client
from trexanalytics.bigquery_table_template_config import USER_VOUCHER_REMOVED_TEMPLATE,\
    TABLE_SCHEME_TEMPLATE, USER_VOUCHER_REDEEMED_TEMPLATE
from trexlib.utils.google.bigquery_util import create_table_from_template


admin_manage_merchant_bp = Blueprint('admin_manage_merchant_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/manage-merchant')


logger = logging.getLogger('debug')

credential_config = {}


@admin_manage_merchant_bp.route('/index', methods=['GET'])
@login_required
def manage_merchant(): 
    logger.debug('---manage_merchant---')
    return render_template('admin/manage_merchant/manage_merchant_index.html', 
                           page_title       = gettext('Manage Merchant'), 
                           #merchant_list    = merchant_list,
                           pagination_limit = PAGINATION_SIZE,
                           page_url         = url_for('admin_manage_merchant_bp.manage_merchant'),
                           #total_count      = total_count
                           )

@admin_manage_merchant_bp.route('/add', methods=['GET'])
@login_required
def add_merchant(): 
    
    return render_template('admin/manage_merchant/manage_merchant_details.html',
                           page_title       = gettext('Add Merchant Account'),
                           merchant         = None,
                           post_url         = url_for('admin_manage_merchant_bp.add_merchant_post'),
                           #page_url         = url_for('admin_manage_merchant_bp.add_merchant'),
                           )
    


@admin_manage_merchant_bp.route('/add', methods=['POST'])
@login_required_rest
def add_merchant_post(): 
    logger.debug('--- submit add_merchant data ---')
    add_merchant_data = request.form
    
    logger.debug('add_merchant_data=%s', add_merchant_data)
    
    add_merchant_form = AddMerchantForm(add_merchant_data)
    
    
    try:
        if add_merchant_form.validate():
            
            db_client = create_db_client(caller_info="add_merchant_post")
            
            with db_client.context():
                try:
                    merchant_acct = MerchantAcct.create(
                                                    company_name        = add_merchant_form.company_name.data,
                                                    brand_name          = add_merchant_form.brand_name.data,
                                                    contact_name        = add_merchant_form.contact_name.data,
                                                    email               = add_merchant_form.email.data,
                                                    mobile_phone        = add_merchant_form.mobile_phone.data,
                                                    office_phone        = add_merchant_form.office_phone.data,
                                                    plan_start_date     = add_merchant_form.plan_start_date.data,
                                                    plan_end_date       = add_merchant_form.plan_end_date.data,
                                                    country             = add_merchant_form.country.data,
                                                    timezone            = add_merchant_form.timezone.data,
                                                    currency_code       = add_merchant_form.currency_code.data,
                                                    product_package     = add_merchant_form.product_package.data,
                                                    loyalty_package     = add_merchant_form.loyalty_package.data,
                                                    pos_package         = add_merchant_form.pos_package.data,
                                                    outlet_limit        = add_merchant_form.outlet_limit.data,
                                                    )
                    
                    account_code = merchant_acct.account_code
                    bq_client    = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)
                    
                    account_code    = account_code.replace('-','')
                    now = datetime.utcnow()
                    year_month_day = datetime.strftime(now, '%Y%m%d')
                    
                    table_name = USER_VOUCHER_REMOVED_TEMPLATE
                    final_table_name        = '{}_{}_{}'.format(table_name, account_code, year_month_day)
                    
                    created_table   = create_table_from_template(
                                        MERCHANT_DATASET, 
                                        final_table_name, 
                                        TABLE_SCHEME_TEMPLATE.get(USER_VOUCHER_REMOVED_TEMPLATE), 
                                        bigquery_client=bq_client)
                    logger.info('create_merchant_required_analytics_table: created table(%s)=%s', final_table_name, created_table)
                    
                    table_name = USER_VOUCHER_REDEEMED_TEMPLATE
                    final_table_name        = '{}_{}_{}'.format(table_name, account_code, year_month_day)
                    
                    created_table   = create_table_from_template(
                                        MERCHANT_DATASET, 
                                        final_table_name, 
                                        TABLE_SCHEME_TEMPLATE.get(USER_VOUCHER_REDEEMED_TEMPLATE), 
                                        bigquery_client=bq_client)
                    logger.info('create_merchant_required_analytics_table: created table(%s)=%s', final_table_name, created_table)
                    merchant_key = merchant_acct.key_in_str
                    
                    '''
                    
                    
                    task_url = '/merchant/task/merchant-key/{merchant_key}/create-required-analytics-table'.format(merchant_key=merchant_key)
                    
                    logger.debug('Going to trigger task to create merchant analytics required tables')
                    
                    create_task(task_url, 'default', 
                        in_seconds      = 1,
                        http_method     = 'GET', 
                        payload         = {},
                        credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                        project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                        location        = SYSTEM_TASK_GCLOUD_LOCATION,
                        service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL,
                        )
                    '''
                    return create_rest_message('Merchant Account have been created', 
                                               status_code=StatusCode.OK, 
                                               created_merchant_key = merchant_key,
                                               post_url = url_for('admin_manage_merchant_bp.update_merchant_post'),
                                               next_url = url_for('admin_manage_merchant_bp.read_merchant', merchant_key=merchant_key)
                                               )
                
                except:
                    logger.error('Failed to create contact due to %s', get_tracelog())
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            
            error_message = add_merchant_form.create_rest_return_error_message()
            logger.warn('Failed due to form validation where %s', error_message)
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register merchant account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@admin_manage_merchant_bp.route('/update', methods=['post'])
@login_required_rest
def update_merchant_post():
    logger.debug('--- submit admin_manage_merchant_bp data ---')
    merchant_details_data = request.form
    
    logger.debug('merchant_details_data=%s', merchant_details_data)
    
    merchant_details_form = AddMerchantForm(merchant_details_data)
    merchant_key = merchant_details_form.key.data
    
    logger.debug('merchant_key=%s', merchant_key)
    
    try:
        if is_not_empty(merchant_key):
            if merchant_details_form.validate():
                
                logger.debug('product package=%s', merchant_details_form.product_package.data)
                logger.debug('loyalty package=%s', merchant_details_form.loyalty_package.data)
                                
                db_client = create_db_client(caller_info="update_merchant_post")
                
                with db_client.context():   
                    merchant_acct = MerchantAcct.fetch(merchant_key)
                    logger.debug('superuser=%s', merchant_acct)
                    
                    if merchant_acct:
                        MerchantAcct.update(
                                        merchant_acct,
                                        company_name      = merchant_details_form.company_name.data,
                                        brand_name        = merchant_details_form.brand_name.data,
                                        contact_name      = merchant_details_form.contact_name.data,
                                        email             = merchant_details_form.email.data,
                                        mobile_phone      = merchant_details_form.mobile_phone.data,
                                        office_phone      = merchant_details_form.office_phone.data,
                                        plan_start_date   = merchant_details_form.plan_start_date.data,
                                        plan_end_date     = merchant_details_form.plan_end_date.data,
                                        currency_code     = merchant_details_form.currency_code.data,
                                        country           = merchant_details_form.country.data,
                                        timezone          = merchant_details_form.timezone.data,
                                        product_package   = merchant_details_form.product_package.data,
                                        loyalty_package   = merchant_details_form.loyalty_package.data,
                                        pos_package       = merchant_details_form.pos_package.data,
                                        outlet_limit      = merchant_details_form.outlet_limit.data,
                                        
                                        
                            )
                
                if merchant_acct:
                    return create_rest_message(gettext('Merchant account have been updated'), status_code=StatusCode.OK)
                else:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = merchant_details_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete merchant account data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to register merchant account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@admin_manage_merchant_bp.route('/merchant-details/<merchant_key>', methods=['GET'])
@login_required
def read_merchant(merchant_key): 
    logger.debug('---read_merchant---')
    
    logger.debug('merchant_key=%s', merchant_key)
    
    if is_not_empty(merchant_key):
        try:
            
            merchant_acct = None    
                
            db_client = create_db_client(caller_info="read_merchant")
            
            with db_client.context():
                merchant_acct = MerchantAcct.fetch(merchant_key)
                timezone_list = get_country_timezone_list_json(merchant_acct.country)
            merchant_acct_dict = merchant_acct.to_dict()
            
            logger.debug('merchant_acct_dict=%s', merchant_acct_dict)
            
            return render_template('admin/manage_merchant/manage_merchant_details.html', 
                                   page_title           = 'Merchant Account Details',
                                   post_url             = url_for('admin_manage_merchant_bp.update_merchant_post'), 
                                   merchant             = merchant_acct_dict,
                                   merchant_acct_key    = merchant_key,
                                   timezone_list        = timezone_list,
                                   #page_url             = url_for('admin_manage_merchant_bp.read_merchant', merchant_key=merchant_key),
                                   ) 
                
        except:
            logger.error('Fail to read merchant account details due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
   
@admin_manage_merchant_bp.route('/merchant-details/<merchant_key>', methods=['delete'])
@login_required_rest
def delete_merchant(merchant_key):
    logger.debug('--- submit delete_merchant data ---')
    try:
        if is_not_empty(merchant_key):
            db_client = create_db_client(caller_info="delete_merchant")
            with db_client.context():   
                merchant_acct = MerchantAcct.fetch(merchant_key)
                logger.debug('merchant_acct=%s', merchant_acct)
                if merchant_acct:
                    merchant_acct.delete_and_related() 
            
            return create_rest_message(gettext('Merchant account have been deleted'), status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext("Incomplete merchant account data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to delete merchant account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 

@admin_manage_merchant_bp.route('/merchant-details/search/page-size/<limit>/page/<page_no>', methods=['POST', 'GET'])
#@admin_manage_merchant_bp.route('/merchant-details/search', methods=['POST'])
@login_required
def search_merchant(limit, page_no): 
    logger.debug('---search_merchant---')
    encrypted_search_merchant_data  = request.args.get('encrypted_search_merchant_data') or {}
    
    logger.debug('encrypted_search_merchant_data=%s', encrypted_search_merchant_data)
    
    if encrypted_search_merchant_data:
        search_merchant_data            = decrypt_json(str.encode(encrypted_search_merchant_data))
        search_merchant_form            = MerchantSearchForm(data=search_merchant_data)
        logger.debug('search_merchant_data from encrypted_search_merchant_data=%s', search_merchant_data)
        
    else:
        search_merchant_data            = request.form
        search_merchant_form            = MerchantSearchForm(search_merchant_data)
        
        logger.debug('search_merchant_data from search form=%s', search_merchant_data)
        
        encrypted_search_merchant_data  = encrypt_json(search_merchant_data)
        
        logger.debug('encrypted_search_merchant_data after encrypted=%s', encrypted_search_merchant_data)
        
        
    
    
    merchant_list               = []
    total_count                 = 0
    
    offset                      = get_offset_by_page_no(page_no, limit=limit)
    page_no_int                 = int(page_no)
    limit_int                   = int(limit)
    
    if search_merchant_form.validate():
        company_name            = search_merchant_form.company_name.data
        account_code            = search_merchant_form.account_code.data
        
        if is_not_empty(account_code):
            account_code = MerchantAcct.format_account_code(account_code)
        
        cursor                          = request.args.get('cursor')
        previous_cursor                 = request.args.get('previous_cursor')
        
        logger.debug('company_name=%s', company_name)
        logger.debug('account_code=%s', account_code)
        
        logger.debug('limit=%s', limit)
        
        logger.debug('cursor=%s', cursor)
        logger.debug('previous_cursor=%s', previous_cursor)
        
        
        db_client = create_db_client(caller_info="search_customer")
        
        
        
        
        try:
            with db_client.context():
                (search_results, total_count, next_cursor)  = MerchantAcct.search_merchant_account( 
                                                                                                company_name            = company_name, 
                                                                                                account_code            = account_code, 
                                                                                                offset                  = offset,
                                                                                                limit                   = limit_int,
                                                                                                start_cursor            = cursor,
                                                                                                
                                                                                                )
        except:
            logger.error('Fail to search customer due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to search customer'), status_code=StatusCode.BAD_REQUEST)
            
        for r in search_results:
            merchant_list.append(r.to_dict())
        
        logger.debug('total_count=%s', total_count)
        logger.debug('merchant_list=%s', merchant_list)
    else:
        logger.debug('search form invalid')
        error_message = search_merchant_form.create_rest_return_error_message()
                
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
        
            
    pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                     = next_cursor, 
                                previous_cursor                 = previous_cursor,
                                current_cursor                  = cursor,
                                encrypted_search_merchant_data  = encrypted_search_merchant_data,
                              )
    
    pages       = pager.get_pages()
    
    return render_template('admin/manage_merchant/merchant_listing_content.html', 
                               merchant_list                = merchant_list,
                               end_point                    = 'admin_manage_merchant_bp.search_merchant',
                               cursor_pager                 = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#merchant_list_div',
                               )  
    
    
@admin_manage_merchant_bp.route('/merchant-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
def list_merchant(limit, page_no): 
    logger.debug('---list_merchant---')
    
    logger.debug('page_no=%s', page_no)
    
    page_no_int = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    merchant_list   = []
    limit_int       = int(limit, 10)
    
    try:
        db_client = create_db_client(caller_info="list_merchant")
        
        with db_client.context():
            total_count             = MerchantAcct.count()
            result                  = MerchantAcct.list_all(limit=limit_int, offset=offset)
        
        #logger.debug('list_merchant: result=%s', result)
        
        for m in result:
            merchant_list.append(m.to_dict())
        
           
        pager       = Pager(page_no_int, total_count, limit_int, show_only_next_and_previous=False)
        pages       = pager.get_pages()
        
        
        return render_template('admin/manage_merchant/merchant_listing_content.html', 
                               merchant_list                = merchant_list,
                               end_point                    = 'admin_manage_merchant_bp.list_merchant',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#merchant_list_div',
                               )
    
    except:
        logger.error('Fail to list merchant account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    
@admin_manage_merchant_bp.route('/upload-logo', methods=['GET'])
def upload_logo():
    merchant_acct_key   = request.args.get('merchant_acct_key')
    db_client = create_db_client(caller_info="upload_logo")
        
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_acct_key)
    
    return render_template("admin/manage_merchant/upload_merchant_logo.html", 
                           page_title           = "Upload Logo",
                           upload_url           = url_for('admin_manage_merchant_bp.upload_logo_post'),
                           merchant_acct_key    = merchant_acct_key,
                           logo_public_url      = merchant_acct.logo_public_url,
                           )
@admin_manage_merchant_bp.route('/upload-logo', methods=['POST'])    
@limit_content_length(1024*1024) # limit to 1mb of logo upload
def upload_logo_post():    
    uploaded_file       = request.files.get('file')
    #merchant_acct_key   = request.args.get('merchant_acct_key')
    
    upload_logo_data    = request.form
    merchant_acct_key   = upload_logo_data.get('merchant_acct_key')
    
    logger.debug('merchant_acct_key=%s', merchant_acct_key)
    logger.debug('uploaded_file=%s', uploaded_file)
    logger.debug('credential_config=%s', current_app.config['credential_config'])
    
    if is_empty(merchant_acct_key):
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Missing required data'))
    
    elif not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    bucket                  = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)    
    #logo_storage_filename   = 'merchant/'+merchant_acct_key+'/logo/'+uploaded_file.filename
    logo_storage_filename   = 'merchant/'+merchant_acct_key+'/logo/brand-logo.png'
    try:
        blob                    = bucket.blob(logo_storage_filename)
        
        logger.debug('bucket=%s', bucket)
        logger.debug('logo_storage_filename=%s', logo_storage_filename)
        
        blob.upload_from_string(
            uploaded_file.read(),
            content_type=uploaded_file.content_type
        )
    
        # The public URL can be used to directly access the uploaded file via HTTP.
        uploaded_url        = blob.public_url
        
        logger.debug('uploaded_url=%s', uploaded_url)
    except:
        logger.error('failed to upload logo to storage due to %s', get_tracelog())
    
    db_client = create_db_client(caller_info="upload_logo_post")
        
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_acct_key)
        if merchant_acct:
            if is_not_empty(merchant_acct.logo_storage_filename):
                old_logo_blob = bucket.get_blob(merchant_acct.logo_storage_filename) 
                if old_logo_blob:
                    old_logo_blob.delete()
            merchant_acct.logo_public_url       = uploaded_url
            merchant_acct.logo_storage_filename = logo_storage_filename
            merchant_acct.put()
            logger.debug('After update merchant uploaded logo url')
        else:
            logger.warn('Failed to fetch merchant account data')
         
    if merchant_acct is None:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid data'))    
            
    
    return create_rest_message(status_code=StatusCode.OK, uploaded_url=uploaded_url)
    
@admin_manage_merchant_bp.route('/import-cusstomer', methods=['GET'])
@login_required
def import_customer(): 
    
    return render_template('admin/import/customer/import_customer.html',
                           page_title       = gettext('Import Customer'),
                           merchant         = None,
                           post_url         = url_for('import_customer_bp.import_customer'),
                           #page_url         = url_for('admin_manage_merchant_bp.add_merchant'),
                           )   
                   
