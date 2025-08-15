from flask import Blueprint, render_template, request, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexadmin import conf
from trexmodel.models.datastore.marketing_models import MarketingImage
from trexlib.libs.flask_wtf.request_wrapper import request_form, request_files


merchant_upload_marketing_image_bp = Blueprint('merchant_upload_marketing_image_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/marketing/image')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@merchant_upload_marketing_image_bp.context_processor
def merchant_marketing_upload_image_bp_inject_settings():
    
    return dict(
                
                )


@merchant_upload_marketing_image_bp.route('/', methods=['GET'])
@login_required
def manage_marketing_image(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_marketing_image")
    image_file_list = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        result_listing = MarketingImage.list_by_merchant_acct(merchant_acct)
        logger.debug('result_listing=%s', result_listing)
                
        if result_listing:
            for image_file in result_listing:
                image_file_list.append(image_file.to_dict())
                
    return render_template('merchant/marketing/upload_image/merchant_manage_marketing_image.html',
                           page_title                   = gettext('Upload Marketing Image'),
                           page_url                     = url_for('merchant_upload_marketing_image_bp.manage_marketing_image'),
                           add_image_url                = url_for('merchant_upload_marketing_image_bp.upload_image_file'),
                           reload_image_listing_url     = url_for('merchant_upload_marketing_image_bp.manage_image_listing_content'),
                           acct_id                      = merchant_acct.key_in_str,
                           image_file_list              = image_file_list

                           )
    
@merchant_upload_marketing_image_bp.route('/image-listing-content', methods=['GET'])
@login_required
def manage_image_listing_content(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_image_listing_content")
    image_file_list = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        result_listing = MarketingImage.list_by_merchant_acct(merchant_acct)
                
        if result_listing:
            for image_file in result_listing:
                image_file_list.append(image_file.to_dict())
    
    #sorted_banner_file_list = sort_dict_list(image_file_list, sort_attr_name='sequence')
        
    return render_template('merchant/marketing/upload_image/image_listing_content.html',
                           image_file_list     = image_file_list

                           )    
    

@merchant_upload_marketing_image_bp.route('/upload-image-file', methods=['GET'])
@login_required
def upload_image_file():
    
    try:
        return render_template('merchant/marketing/upload_image/upload_image_form.html', 
                           page_title               = gettext('Upload Image'),
                           upload_image_file_url    = url_for('merchant_upload_marketing_image_bp.upload_image_file_post'),
                           )
        
    except:
        logger.error('Fail to read image file due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to read image/video'), status_code=StatusCode.BAD_REQUEST)   

@merchant_upload_marketing_image_bp.route('/upload-image-file', methods=['POST'])   
@limit_content_length(1*1024*1024) # limit to 1mb
@login_required
@request_form
@request_files
def upload_image_file_post(request_form, request_files):    
    image_label         = request_form.get('image_label')
    image_file_type     = request_form.get('image_file_type')
    uploaded_file       = request_files.get('file')
    
    logger.info('image_label=%s', image_label)
    logger.info('image_file_type=%s', image_file_type)
    logger.info('uploaded_file=%s', uploaded_file)
    
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="upload_image_file_post")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
        image_file      = MarketingImage.upload_file(uploaded_file, image_label, merchant_acct, bucket, image_file_type=image_file_type)
            
        if image_file:
            image_file = image_file.to_dict()
        
            logger.debug('After uploaded image file')
            
        else:
            logger.warn('Failed to upload image data')
         
    if image_file:
        return create_rest_message(status_code=StatusCode.OK)
    else: 
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@merchant_upload_marketing_image_bp.route('/<image_file_key>', methods=['DELETE'])    
@login_required
def delete_image_file_post(image_file_key):    
    if is_not_empty(image_file_key):
        db_client       = create_db_client( caller_info="image_file_key")
        image_file      = None
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
        with db_client.context():
            image_file = MarketingImage.fetch(image_file_key)
            MarketingImage.remove_file(image_file, bucket)
        
        if image_file:
            return create_rest_message(status_code=StatusCode.ACCEPTED)
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    

     
           