
'''
Created on 26 Dec 2020

@author: jacklok
'''
from flask import Blueprint, render_template, request
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
import jinja2
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexconf import conf as admin_conf, conf
from trexmodel.utils.model.model_util import create_db_client
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexadmin.forms.merchant.merchant_forms import AddMerchantForm
from trexadmin.libs.jinja.merchant_filters import loyalty_package_filter,\
    product_package_filter
from trexadmin.controllers.system.system_route_helpers import get_country_timezone_list_json
from trexlib.libs.flask_wtf.request_wrapper import request_debug, request_files,\
    request_form

merchant_manage_account_bp = Blueprint('merchant_manage_account_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/manage-account')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

'''
Blueprint settings here
'''
@merchant_manage_account_bp.context_processor
def merchant_account_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@jinja2.contextfilter
@merchant_manage_account_bp.app_template_filter()
def product_package_label(context, product_package):
    return product_package_filter(product_package)

@jinja2.contextfilter
@merchant_manage_account_bp.app_template_filter()
def loyalty_package_label(context, account_package):
    return loyalty_package_filter(account_package)

@merchant_manage_account_bp.route('/details', methods=['GET'])
@request_debug
@login_required
def merchant_account_details(): 
    logger.debug('---merchant_account_details---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_acct_key = logged_in_merchant_user.get('merchant_acct_key')
    db_client = create_db_client( caller_info="merchant_account_details")
    
    
    with db_client.context():
        merchant_acct   = MerchantAcct.fetch(merchant_acct_key)
        timezone_list = get_country_timezone_list_json(merchant_acct.country)
    
    return render_template('merchant/settings/manage_account/manage_account_details.html', 
                           page_title           = gettext('Account Details'),
                           page_url             = url_for('merchant_manage_account_bp.merchant_account_details'),
                           post_url             = url_for('merchant_manage_account_bp.merchant_account_details_post'),
                           merchant             = merchant_acct.to_dict(),
                           merchant_acct_key    = merchant_acct_key,
                           timezone_list        = timezone_list,
                           #currency_list        = get_currency_list(),
                           )

@merchant_manage_account_bp.route('/details', methods=['POST'])
@request_debug
@login_required
def merchant_account_details_post():
    logger.debug('---merchant_account_details_post---')
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    merchant_account_details_data   = request.form
    merchant_details_form           = AddMerchantForm(merchant_account_details_data)
    
    logger.debug('merchant_account_details_data=%s', merchant_account_details_data)
    
    if merchant_details_form.validate():
        db_client = create_db_client( caller_info="merchant_account_details")
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            logger.debug('website=%s', merchant_details_form.website.data)
            
            MerchantAcct.update_details(merchant_acct,
                                        company_name    = merchant_details_form.company_name.data,
                                        brand_name      = merchant_details_form.brand_name.data,
                                        business_reg_no = merchant_details_form.business_reg_no.data,
                                        contact_name    = merchant_details_form.contact_name.data,
                                        email           = merchant_details_form.email.data,
                                        mobile_phone    = merchant_details_form.mobile_phone.data,
                                        office_phone    = merchant_details_form.office_phone.data,
                                        currency_code   = merchant_details_form.currency_code.data,
                                        country         = merchant_details_form.country.data,
                                        website         = merchant_details_form.website.data,
                                        timezone        = merchant_details_form.timezone.data,
                                        industry        = merchant_details_form.industry.data,
                                        )
            
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            logger.debug('website after updated=%s', merchant_acct.website)
            
        return create_rest_message(gettext('Merchant account have been updated'), status_code=StatusCode.OK)
    
    else:
        error_message = merchant_details_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)    
        
        
    
        
@merchant_manage_account_bp.route('/upload-logo', methods=['GET'])
def upload_logo():
    logger.debug('---upload_logo---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client( caller_info="upload_logo")
        
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
    
    return render_template("merchant/settings/manage_account/upload_brand_logo.html", 
                           page_title           = gettext('Upload Brand Logo'),
                           page_url           = url_for('merchant_manage_account_bp.upload_logo'),
                           upload_url           = url_for('merchant_manage_account_bp.upload_logo_post'),
                           logo_public_url      = merchant_acct.logo_public_url,
                           )
    
@merchant_manage_account_bp.route('/upload-logo', methods=['POST'])    
@limit_content_length(1000*1024) # limit to 1000mb of logo upload
@request_form
@request_files
def upload_logo_post(request_form, request_files):    
    uploaded_file           = request_files.get('file')
    image_file_type         = request_form.get('image_file_type')
    mimeType                = uploaded_file.content_type
    
    if not mimeType.startswith('image'):
        return create_rest_message(gettext('The uploading file is not image format type'), status_code=StatusCode.BAD_REQUEST)
    else:
    
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        
        logger.debug('uploaded_file=%s', uploaded_file)
        logger.debug('mimeType=%s', mimeType)
        
        if not uploaded_file:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))
    
        db_client = create_db_client( caller_info="upload_logo_post")
            
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            if merchant_acct:
                #merchant_acct_key       = merchant_acct.key_in_str
                bucket                  = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
                merchant_acct.upload_logo(uploaded_file, bucket, logo_file_type=image_file_type)
                uploaded_url = merchant_acct.logo_public_url
                '''
                bucket                  = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)    
                #logo_storage_filename   = 'merchant/'+merchant_acct_key+'/logo/'+uploaded_file.filename
                logo_storage_filename   = 'merchant/'+merchant_acct_key+'/logo/brand-logo.png'
                blob                    = bucket.blob(logo_storage_filename)
                
                blob.upload_from_string(
                    uploaded_file.read(),
                    content_type=uploaded_file.content_type
                )
            
                uploaded_url        = blob.public_url
                
                if is_not_empty(merchant_acct.logo_storage_filename):
                    old_logo_blob = bucket.get_blob(merchant_acct.logo_storage_filename) 
                    if old_logo_blob:
                        old_logo_blob.delete()
    
                merchant_acct.logo_public_url       = uploaded_url
                merchant_acct.logo_storage_filename = logo_storage_filename
                merchant_acct.put()
                logger.debug('After update merchant uploaded logo url')
                '''
            else:
                logger.warn('Failed to fetch merchant account data')
             
        if merchant_acct is None:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid data'))    
                
        
        return create_rest_message(status_code=StatusCode.OK, uploaded_url=uploaded_url) 
    
             
