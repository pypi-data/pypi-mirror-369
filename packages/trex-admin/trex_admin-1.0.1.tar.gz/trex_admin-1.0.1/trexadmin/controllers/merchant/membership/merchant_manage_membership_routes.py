'''
Created on 7 Apr 2021

@author: jacklok
'''

from flask import Blueprint, render_template, request, abort
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty, random_string
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.membership_models import MerchantMembership,\
    MerchantTierMembership
from trexadmin.forms.merchant.membership_forms import BasicMembershipForm
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
from trexweb.utils.common.http_response_util import MINE_TYPE_JSON,\
    create_cached_response
import json
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexconf import conf
from trexlib.utils.google.gcloud_util import connect_to_bucket


merchant_manage_basic_membership_bp = Blueprint('merchant_manage_basic_membership_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/manage-basic-membership')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@merchant_manage_basic_membership_bp.context_processor
def merchant_membership_settings_bp_inject_settings():
    
    return dict(
                
                )


@merchant_manage_basic_membership_bp.route('/', methods=['GET'])
@login_required
def basic_membership_overview(): 
    return show_membership_listing('merchant/loyalty/manage_membership/basic_membership/basic_membership_overview.html')

@merchant_manage_basic_membership_bp.route('/membership-listing', methods=['GET'])
@login_required
def membership_listing(): 
    return show_membership_listing('merchant/loyalty/manage_membership/basic_membership/latest_basic_membership_content.html', show_page_title=False)

@merchant_manage_basic_membership_bp.route('/archived-membership-listing', methods=['GET'])
@login_required
def archived_membership_listing(): 
    return show_archived_membership_listing('merchant/loyalty/manage_membership/basic_membership/archived_basic_membership.html')


def show_membership_listing(template_name, show_page_title=True): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    memberships_list        = []
    
    db_client = create_db_client(caller_info="show_membership_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                __memberships_list            = MerchantMembership.list_by_merchant_acct(merchant_acct)
                if __memberships_list:
                    for m in __memberships_list:
                        memberships_list.append(m.to_dict())
                        
            
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
           
    
    logger.debug('memberships_list count=%d', len(memberships_list))
            
    return render_template(template_name,
                           page_title                       = gettext('Membership Setup') if show_page_title else None,
                           page_url                         = url_for('merchant_manage_basic_membership_bp.basic_membership_overview') if show_page_title else None,
                           add_membership_url               = url_for('merchant_manage_basic_membership_bp.add_membership'),
                           reload_memberships_listing_url   = url_for('merchant_manage_basic_membership_bp.membership_listing'),
                           archived_membership_listing_url  = url_for('merchant_manage_basic_membership_bp.archived_membership_listing'),
                           memberships_list                 = memberships_list,
                           show_tips                        = show_page_title,
                           )
    
def show_archived_membership_listing(template_name): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    memberships_list        = []
    
    db_client = create_db_client(caller_info="show_membership_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                __memberships_list            = MerchantMembership.list_by_merchant_acct(merchant_acct, is_archived=True)
                if __memberships_list:
                    for m in __memberships_list:
                        memberships_list.append(m.to_dict())
                        
            
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
           
    
    logger.debug('memberships_list count=%d', len(memberships_list))
            
    return render_template(template_name,
                           memberships_list                 = memberships_list,
                           )    

@merchant_manage_basic_membership_bp.route('/add', methods=['GET'])
@login_required
def add_membership():
    return render_template('merchant/loyalty/manage_membership/basic_membership/basic_membership_details.html',
                           post_url                         = url_for('merchant_manage_basic_membership_bp.add_membership_post'),
                           upload_membership_card_image_url = url_for('merchant_manage_basic_membership_bp.upload_membership_card_image'),
                           )
    
@merchant_manage_basic_membership_bp.route('/membership-card-image', methods=['GET'])
@login_required
def upload_membership_card_image():
    membership_key       = request.args.get('membership_key')
    
    if is_not_empty(membership_key):
        db_client = create_db_client(caller_info="upload_membership_card_image")
        
        with db_client.context():
            membership            = MerchantMembership.fetch(membership_key)
            
    return render_template('merchant/loyalty/manage_membership/membership_card_image_content.html',
                           upload_url       = url_for('merchant_manage_basic_membership_bp.upload_membership_card_image_post'),
                           membership_key   = membership_key,
                           image_public_url = membership.image_public_url,
                           membership       = membership.to_dict(),
                           )    

@merchant_manage_basic_membership_bp.route('/membership-card-image', methods=['POST'])   
@limit_content_length(1*1024*1024) # limit to 1mb
def upload_membership_card_image_post():    
    membership_key      = request.form.get('membership_key')
    uploaded_file       = request.files.get('file')
    
    logger.debug('membership_key=%s', membership_key)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="upload_membership_card_image_post")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
        membership      = MerchantMembership.fetch(membership_key)
        MerchantMembership.upload_membership_card_image(membership, uploaded_file, merchant_acct, bucket, modified_by=merchant_user)
            
        
         
    return create_rest_message(status_code=StatusCode.OK, image_public_url=membership.image_public_url)
    
    
@merchant_manage_basic_membership_bp.route('/edit/<membership_key>', methods=['GET'])
@login_required
def edit_membership(membership_key):
    
    return read_membership(membership_key, is_view_mode=False)

@merchant_manage_basic_membership_bp.route('/view/<membership_key>', methods=['GET'])
@login_required
def view_membership(membership_key):
    
    return read_membership(membership_key, is_view_mode=True) 
    
def read_membership(membership_key, is_view_mode=True):
    
    db_client = create_db_client(caller_info="show_membership_listing")
    try:
        with db_client.context():
            membership            = MerchantMembership.fetch(membership_key)
                
                        
            
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
    
    return render_template('merchant/loyalty/manage_membership/basic_membership/basic_membership_details.html',
                           
                           membership                       = membership.to_dict(),
                           membership_key                   = membership_key,
                           post_url                         = url_for('merchant_manage_basic_membership_bp.edit_membership_post'),
                           upload_membership_card_image_url = url_for('merchant_manage_basic_membership_bp.upload_membership_card_image'),
                           is_view_mode                     = is_view_mode,
                           
                           )          
    
@merchant_manage_basic_membership_bp.route('/add', methods=['POST'])
@login_required
def add_membership_post():
    
    membership_data = request.form
    membership_form = BasicMembershipForm(membership_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if membership_form.validate():
        try:
            db_client = create_db_client(caller_info="add_membership_post")
            
            membership_key = membership_form.membership_key.data
            
            logger.debug('membership_key=%s', membership_key)
            
            if is_empty(membership_key):
                logger.debug('new membership')
                with db_client.context():
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                    membership      = MerchantMembership.create(merchant_acct, 
                                                             label                  = membership_form.label.data,
                                                             desc                   = membership_form.desc.data,
                                                             expiration_type        = membership_form.expiration_type.data,
                                                             expiration_value       = membership_form.expiration_value.data,
                                                             created_by             = merchant_user,
                                                             discount_rate          = membership_form.discount_rate.data,
                                                             terms_and_conditions   = membership_form.terms_and_conditions.data,
                                                             )
                    
                    membership_key      = membership.key_in_str
                
                if membership is None:
                    return create_rest_message(gettext('Invalid membership'), status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message(status_code=StatusCode.OK, 
                                        created_membership_key = membership_key,
                                        )
            else:
                logger.debug('update membership')
                with db_client.context():
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                                                         
                    membership      = MerchantMembership.fetch(membership_key)
                    MerchantMembership.update(membership, 
                                             label                      = membership_form.label.data,
                                             desc                       = membership_form.desc.data,
                                             expiration_type            = membership_form.expiration_type.data,
                                             expiration_value           = membership_form.expiration_value.data,
                                             modified_by                = merchant_user,
                                             discount_rate              = membership_form.discount_rate.data,
                                             terms_and_conditions       = membership_form.terms_and_conditions.data,
                                             )
                    
                    return create_rest_message(status_code=StatusCode.OK)
            
        except:
            logger.error('Fail to create membership due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to save membership'), status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = membership_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
      
    
@merchant_manage_basic_membership_bp.route('/edit', methods=['POST'])
@login_required
def edit_membership_post():
    
    logger.debug('---edit_membership_post---')
    
    membership_data = request.form
    membership_form = BasicMembershipForm(membership_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if membership_form.validate():
        try:
            db_client = create_db_client(caller_info="add_membership_post")
            
            membership_key = membership_form.membership_key.data
            logger.debug('membership_form=%s', membership_form)
            
            if is_not_empty(membership_key):
            
                with db_client.context():
                    membership          = MerchantMembership.fetch(membership_key)
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    
                    if membership:
                        MerchantMembership.update(membership, 
                                             label                      = membership_form.label.data,
                                             desc                       = membership_form.desc.data,
                                             expiration_type            = membership_form.expiration_type.data,
                                             expiration_value           = membership_form.expiration_value.data,
                                             modified_by                = merchant_user,
                                             discount_rate              = membership_form.discount_rate.data,
                                             terms_and_conditions       = membership_form.terms_and_conditions.data,
                                             )
                    
                        membership_key      = membership.key_in_str
                if membership:
                    return create_rest_message(status_code=StatusCode.OK
                                        )
                else:
                    logger.error('Fail to update membership due to %s', get_tracelog())
                    return create_rest_message(gettext('Invalid membership data'), status_code=StatusCode.BAD_REQUEST)
                                        
            else:
                logger.error('Fail to update membership due to %s', get_tracelog())
                return create_rest_message(gettext('Invalid membership data'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to create membership due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to save membership'), status_code=StatusCode.BAD_REQUEST)
    
    else:
        error_message = membership_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
@merchant_manage_basic_membership_bp.route('/archive-membership', methods=['POST','GET'])
@login_required
def archive_membership_post(): 
    
    logger.debug('---archive_membership_post---')
    
    membership_key = request.args.get('membership_key')
    
    logger.debug('membership_key=%s', membership_key)
    
    db_client               = create_db_client(caller_info="archive_membership_post")
    try:
        with db_client.context():
            if is_empty(membership_key):
                return create_rest_message(gettext('Invaid membership data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                membership = MerchantMembership.fetch(membership_key)
                if membership:
                    MerchantMembership.archive_membership(membership)
                    
        if membership is None:
            return create_rest_message(gettext('Invalid merchant membership'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to archive merchant membership due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive merchant membership'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK)

@merchant_manage_basic_membership_bp.route('/list-basic-membership-code', methods=['GET'])
def list_basic_membership_code():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client               = create_db_client(caller_info="list_membership_code")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        memberships_list        = MerchantMembership.list_by_merchant_acct(merchant_acct)
        
        for m in memberships_list:
            data_list.append({
                                        'code'  : m.key_in_str,
                                        'label' : m.label,
                                        })
                
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    json_resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return json_resp  

@merchant_manage_basic_membership_bp.route('/list-tier-membership-code', methods=['GET'])
def list_tier_membership_code():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client               = create_db_client(caller_info="list_tier_membership_code")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        memberships_list        = MerchantTierMembership.list_by_merchant_acct(merchant_acct)
        
        for m in memberships_list:
            data_list.append({
                                        'code'  : m.key_in_str,
                                        'label' : m.label,
                                        })
                
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    json_resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return json_resp   
