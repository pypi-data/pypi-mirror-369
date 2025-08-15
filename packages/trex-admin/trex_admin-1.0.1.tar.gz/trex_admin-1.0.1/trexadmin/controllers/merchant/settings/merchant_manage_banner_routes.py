from flask import Blueprint, render_template, request, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct, BannerFile
#from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexconf import conf
from trexlib.utils.common.common_util import sort_dict_list

merchant_manage_banner_bp = Blueprint('merchant_manage_banner_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/settings/banner')

logger = logging.getLogger('debug')

'''
Blueprint settings here
'''


@merchant_manage_banner_bp.context_processor
def merchant_manage_banner_bp_inject_settings():
    
    return dict(
                
                )


@merchant_manage_banner_bp.route('/', methods=['GET'])
@login_required
def manage_banner_index(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_banner_index")
    banner_file_list = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        result_listing = BannerFile.list_by_merchant_acct(merchant_acct)
        logger.debug('result_listing=%s', result_listing)
                
        if result_listing:
            for banner_file in result_listing:
                banner_file_list.append(banner_file.to_dict())
                
    sorted_banner_file_list = sort_dict_list(banner_file_list, sort_attr_name='sequence')
        
    return render_template('merchant/settings/manage_banner/merchant_manage_banner.html',
                           page_title                   = gettext('Manage Banner'),
                           page_url                     = url_for('merchant_manage_banner_bp.manage_banner_index'),
                           add_banner_url               = url_for('merchant_manage_banner_bp.upload_banner_file'),
                           reload_banner_listing_url    = url_for('merchant_manage_banner_bp.manage_banner_listing_content'),
                           update_banner_sequence_url   = url_for('merchant_manage_banner_bp.update_banner_sequence'),
                           acct_id                      = merchant_acct.key_in_str,
                           banner_file_list             = sorted_banner_file_list

                           )
    
@merchant_manage_banner_bp.route('/banner-listing-content', methods=['GET'])
@login_required
def manage_banner_listing_content(): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_banner_index")
    banner_file_list = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        result_listing = BannerFile.list_by_merchant_acct(merchant_acct)
                
        if result_listing:
            for banner_file in result_listing:
                banner_file_list.append(banner_file.to_dict())
    
    sorted_banner_file_list = sort_dict_list(banner_file_list, sort_attr_name='sequence')
        
    return render_template('merchant/settings/manage_banner/banner_listing_content.html',
                           banner_file_list     = sorted_banner_file_list

                           )    
    

@merchant_manage_banner_bp.route('/upload-banner-file', methods=['GET'])
@login_required
def upload_banner_file():
    
    try:
        return render_template('merchant/settings/manage_banner/upload_banner_form.html', 
                           page_title                           = gettext('Upload Banner'),
                           upload_banner_file_url               = url_for('merchant_manage_banner_bp.upload_banner_file_post'),
                           )
        
    except:
        logger.error('Fail to read product image/video due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to read product image/video'), status_code=StatusCode.BAD_REQUEST)   

@merchant_manage_banner_bp.route('/upload-banner-file', methods=['POST'])   
@limit_content_length(conf.MAX_CONTENT_FILE_LENGTH)
@login_required
def upload_banner_file_post():    
    banner_file_type   = request.form.get('banner_file_type')
    uploaded_file       = request.files.get('file')
    
    logger.debug('banner_file_type=%s', banner_file_type)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="upload_banner_file_post")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
        banner_file    = BannerFile.upload_file(uploaded_file, merchant_acct, bucket, banner_file_type=banner_file_type)
            
        if banner_file:
            banner_file = banner_file.to_dict()
        
            logger.debug('After uploaded banner file')
            
        else:
            logger.warn('Failed to fetch banner data')
         
    if banner_file:
        return create_rest_message(status_code=StatusCode.OK)
    else: 
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@merchant_manage_banner_bp.route('/<banner_file_key>', methods=['DELETE'])    
@login_required
def delete_banner_file_post(banner_file_key):    
    if is_not_empty(banner_file_key):
        db_client       = create_db_client( caller_info="delete_banner_file_post")
        banner_file    = None
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
        with db_client.context():
            banner_file = BannerFile.fetch(banner_file_key)
            BannerFile.remove_file(banner_file, bucket)
        
        if banner_file:
            return create_rest_message(status_code=StatusCode.ACCEPTED)
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@merchant_manage_banner_bp.route('/update-banner-sequence', methods=['POST'])
@login_required
def update_banner_sequence():
    banner_data                         = request.form
    logged_in_merchant_user             = get_loggedin_merchant_user_account()
    banner_data_list                    = banner_data.getlist('banner_data_list[]')
    db_client                           = create_db_client(caller_info="update_banner_sequence")
    
    logger.debug('banner_data_list=%s', banner_data_list);
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result_listing = BannerFile.list_by_merchant_acct(merchant_acct)
        for index, banner_file_key in enumerate(banner_data_list, start=1):
            for banner_file in result_listing:
                if banner_file.key_in_str == banner_file_key:
                    banner_file.sequence = index
                    banner_file.put()
                    break
                    
                    
    return create_rest_message(gettext('Banner sequence have been updated'), status_code=StatusCode.OK)
     
           