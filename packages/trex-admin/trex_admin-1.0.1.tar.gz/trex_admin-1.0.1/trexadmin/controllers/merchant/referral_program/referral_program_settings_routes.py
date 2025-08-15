'''
Created on 18 Apr 2024

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging


from trexconf import conf
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexadmin.forms.merchant.referral_program_forms import ReferralProgramPromoteTextForm
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct
from flask_babel import gettext
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.google.gcloud_util import connect_to_bucket
from flask.helpers import url_for

referral_program_settings_bp = Blueprint('referral_program_settings_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/referral-program/program-settings')


logger = logging.getLogger('controller')

@referral_program_settings_bp.context_processor
def referral_program_setup_bp_inject_settings():
    
    return dict(
        )


@referral_program_settings_bp.route('/program-referrer-promote-text', methods=['GET'])
@login_required
def show_program_referrer_promote_text(): 
    logger.debug('---show_program_referrer_promote_text---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="show_program_referrer_promote_text")
    try:
        
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            
    except:
        logger.error('Fail to get merchant program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/promote_text/referral_program_promote_text.html', 
                           page_title                   = gettext('Referrer Promote Text'),
                           promote_title                = merchant_acct.referrer_promote_title,
                           promote_desc                 = merchant_acct.referrer_promote_desc,
                           define_program_promote_text  = url_for('referral_program_settings_bp.define_referrer_promote_text_post'),
                           )
    
@referral_program_settings_bp.route('/program-referee-promote-text', methods=['GET'])
@login_required
def show_program_referee_promote_text(): 
    logger.debug('---show_program_referee_promote_text---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="show_program_referee_promote_text")
    try:
        
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            
    except:
        logger.error('Fail to get merchant program due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/promote_text/referral_program_promote_text.html', 
                           page_title                   = gettext('Referee Promote Text'),
                           promote_title                = merchant_acct.referee_promote_title,
                           promote_desc                 = merchant_acct.referee_promote_desc,
                           define_program_promote_text  = url_for('referral_program_settings_bp.define_referee_promote_text_post'),
                           )    

@referral_program_settings_bp.route('/define-referrer-promote-text', methods=['POST'])
@login_required
def define_referrer_promote_text_post(): 
    logger.debug('---define_referrer_promote_text_post---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    promote_text_data   = request.form
    promote_text_form   = ReferralProgramPromoteTextForm(promote_text_data)
    
    db_client               = create_db_client(caller_info="define_promote_text_post")
    
    if promote_text_form.validate():
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        try:
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                if merchant_acct: 
                    merchant_acct.update_referrer_program_promote_text(
                                                                promote_title      = promote_text_form.promote_title.data,
                                                                promote_desc       = promote_text_form.promote_desc.data,
                                                                modified_by        = merchant_user
                                                                  )
                        
                    return create_rest_message(status_code=StatusCode.OK)
                                            
        except:
            logger.error('Fail to define update program promote text due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update program promote text'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = promote_text_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
@referral_program_settings_bp.route('/define-referee-promote-text', methods=['POST'])
@login_required
def define_referee_promote_text_post(): 
    logger.debug('---define_referee_promote_text_post---')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    promote_text_data   = request.form
    promote_text_form   = ReferralProgramPromoteTextForm(promote_text_data)
    
    db_client               = create_db_client(caller_info="define_promote_text_post")
    
    if promote_text_form.validate():
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        try:
            with db_client.context():
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                if merchant_acct: 
                    merchant_acct.update_referee_program_promote_text(
                                                                promote_title      = promote_text_form.promote_title.data,
                                                                promote_desc       = promote_text_form.promote_desc.data,
                                                                modified_by        = merchant_user
                                                                  )
                        
                    return create_rest_message(status_code=StatusCode.OK)
                                            
        except:
            logger.error('Fail to define update program promote text due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update program promote text'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = promote_text_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)    

@referral_program_settings_bp.route('/program-referrer-promote-image', methods=['GET'])
@login_required
def show_program_referrer_promote_image(): 
    logger.debug('---show_program_referrer_promote_image---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="show_program_referrer_promote_image")
    try:
        
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/promote_image/referral_program_promote_image.html', 
                           page_title                   = gettext('Referrer Program Promote Image'),
                           upload_promote_image_post    = url_for('referral_program_settings_bp.upload_referrer_promote_image_post'),
                           uploaded_promote_image       = merchant_acct.referrer_promote_image if is_not_empty(merchant_acct.referrer_promote_image) else conf.REFERRAL_DEFAULT_PROMOTE_IMAGE, 
                           )

@referral_program_settings_bp.route('/program-referee-promote-image', methods=['GET'])
@login_required
def show_program_referee_promote_image(): 
    logger.debug('---show_program_referee_promote_image---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="show_program_referee_promote_image")
    try:
        
        with db_client.context():
            merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    return render_template('merchant/loyalty/referral_program/promote_image/referral_program_promote_image.html', 
                           page_title                   = gettext('Referee Program Promote Image'),
                           upload_promote_image_post    = url_for('referral_program_settings_bp.upload_referee_promote_image_post'),
                           uploaded_promote_image       = merchant_acct.referee_promote_image if is_not_empty(merchant_acct.referee_promote_image) else conf.REFERRAL_DEFAULT_PROMOTE_IMAGE, 
                           )
    
@referral_program_settings_bp.route('/upload-referrer-promote-image', methods=['POST'])    
@limit_content_length(1*1024*1024) # limit to 1mb
def upload_referrer_promote_image_post():    
    ticket_image_data               = request.form
    uploaded_file                   = request.files.get('file')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    logger.debug('promote_image_data=%s', ticket_image_data)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))
    
    db_client       = create_db_client( caller_info="upload_promote_image_post")
    
    with db_client.context():
        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        if merchant_acct:
            merchant_acct_key       = merchant_acct.key_in_str
            merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            bucket                  = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
            image_storage_filename  = 'merchant/'+merchant_acct_key+'/referral/referrer'+uploaded_file.filename
            blob                    = bucket.blob(image_storage_filename)
            
            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )
        
            uploaded_url        = blob.public_url
            
            if is_not_empty(merchant_acct.referrer_promote_image):
                old_logo_blob = bucket.get_blob(merchant_acct.referrer_promote_image) 
                if old_logo_blob:
                    old_logo_blob.delete()

            merchant_acct.upload_referrer_program_promote_image( 
                                                    image_public_url        = uploaded_url, 
                                                    image_storage_filename  = image_storage_filename, 
                                                    modified_by             = merchant_user
                                                    )
            
            logger.debug('After uploaded referral promote image url')
            
        else:
            logger.warn('Failed to fetch referral program data')
         
    if merchant_acct is None:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid merchant account'))    
            
    
    return create_rest_message(status_code=StatusCode.OK, uploaded_url=uploaded_url) 

@referral_program_settings_bp.route('/upload-referee-promote-image', methods=['POST'])    
@limit_content_length(1*1024*1024) # limit to 1mb
def upload_referee_promote_image_post():    
    ticket_image_data               = request.form
    uploaded_file                   = request.files.get('file')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    logger.debug('promote_image_data=%s', ticket_image_data)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))
    
    db_client       = create_db_client( caller_info="upload_promote_image_post")
    
    with db_client.context():
        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        if merchant_acct:
            merchant_acct_key       = merchant_acct.key_in_str
            merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            bucket                  = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
            image_storage_filename  = 'merchant/'+merchant_acct_key+'/referral/referee'+uploaded_file.filename
            blob                    = bucket.blob(image_storage_filename)
            
            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )
        
            uploaded_url        = blob.public_url
            
            if is_not_empty(merchant_acct.referee_promote_image):
                old_logo_blob = bucket.get_blob(merchant_acct.referee_promote_image) 
                if old_logo_blob:
                    old_logo_blob.delete()

            merchant_acct.upload_referee_program_promote_image( 
                                                    image_public_url        = uploaded_url, 
                                                    image_storage_filename  = image_storage_filename, 
                                                    modified_by             = merchant_user
                                                    )
            
            logger.debug('After uploaded referral promote image url')
            
        else:
            logger.warn('Failed to fetch referral program data')
         
    if merchant_acct is None:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid merchant account'))    
            
    
    return create_rest_message(status_code=StatusCode.OK, uploaded_url=uploaded_url)      

