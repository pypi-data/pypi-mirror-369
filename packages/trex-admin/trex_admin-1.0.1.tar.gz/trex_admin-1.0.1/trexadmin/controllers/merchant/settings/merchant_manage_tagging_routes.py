'''
Created on 8 Feb 2021

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantTagging
from trexadmin.forms.merchant.merchant_forms import AddMerchantTaggingForm, UpdateMerchantTaggingForm
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account

merchant_settings_tagging_bp = Blueprint('merchant_settings_tagging_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/settings/tagging')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@merchant_settings_tagging_bp.context_processor
def merchant_settings_tagging_bp_inject_settings():
    
    return dict(
                
                )


@merchant_settings_tagging_bp.route('/list', methods=['GET'])
@login_required
def merchant_settings_tagging(): 
    return list_merchant_tagging_function('merchant/crm/tagging/manage_tagging_listing.html')
    

@merchant_settings_tagging_bp.route('/list-content', methods=['GET'])
@login_required
def merchant_settings_tagging_listing_content(): 
    return list_merchant_tagging_function('merchant/crm/tagging/manage_tagging_listing_content.html')

    
def list_merchant_tagging_function(template_name):
    merchant_tag_list = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="merchant_settings_tagging_listing")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        __merchant_tag_list = MerchantTagging.list_by_merchant_account(merchant_acct)
    
    for l in __merchant_tag_list:
        merchant_tag_list.append(l.to_dict())
        
    return render_template(template_name,
                           page_title           = gettext('Manage Tag'),
                           page_url             = url_for('merchant_settings_tagging_bp.merchant_settings_tagging'),
                           add_tag_url          = url_for('merchant_settings_tagging_bp.add_tagging'),
                           reload_list_tag_url  = url_for('merchant_settings_tagging_bp.merchant_settings_tagging_listing_content'),
                           delete_tagging_url   = url_for('merchant_settings_tagging_bp.delete_tagging'),
                           tag_list             = merchant_tag_list,
                           show_tips            = True,
                           )

    
@merchant_settings_tagging_bp.route('/add', methods=['GET'])
@login_required
def add_tagging():
    return render_template('merchant/crm/tagging/tagging_details.html',
                           page_title=gettext('Add Tag'),
                           post_url=url_for('merchant_settings_tagging_bp.add_tagging_post'),
                           )    


@merchant_settings_tagging_bp.route('/add', methods=['POST'])
@login_required_rest
def add_tagging_post():
    tagging_data = request.form
    tagging_form = AddMerchantTaggingForm(tagging_data)
    
    logger.debug('tagging_data=%s', tagging_data)
    
    return add_or_update_tag_function(tagging_form, is_creating_new_tag=True)


@merchant_settings_tagging_bp.route('/update', methods=['POST'])
@login_required_rest
def update_tagging_post():
    tagging_form = UpdateMerchantTaggingForm(request.form)
    return add_or_update_tag_function(tagging_form, is_creating_new_tag=False)       

    
def add_or_update_tag_function(validate_form, is_creating_new_tag=False):
    
    logger.debug('---add_or_update_tag_function---, is_creating_new_tag=%s', is_creating_new_tag)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    if validate_form.validate():
        try:
            db_client = create_db_client(caller_info="add_or_update_tag_function")
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                same_label_tagging = MerchantTagging.get_by_merchant_label(merchant_acct, validate_form.label.data)
                
                if is_creating_new_tag:
                    if same_label_tagging:
                        return create_rest_message(gettext('Same label have been used'), status_code=StatusCode.BAD_REQUEST)
                    else:
                        created_tag = MerchantTagging.create(merchant_acct, label=validate_form.label.data, desc=validate_form.desc.data)
                        
                        logger.debug('created_tag=%s', created_tag.to_dict())
                    
                else:
                    tag_key = validate_form.tag_key.data
                    
                    if same_label_tagging:
                        if same_label_tagging.key_in_str != tag_key:
                            return create_rest_message(gettext('Same label have been used'), status_code=StatusCode.BAD_REQUEST)
                    
                    created_tag = MerchantTagging.fetch(tag_key)
                    
                    created_tag.update(label=validate_form.label.data, desc=validate_form.desc.data)
                
            return create_rest_message(gettext('Tag have been updated'),
                                                           status_code=StatusCode.OK,
                                                           created_tag_key=created_tag.key_in_str,
                                                           post_url=url_for('merchant_settings_tagging_bp.update_tagging_post'))
        except:
            error_message = gettext('Failed to update tag')
            logger.warn('Failed due to %s', get_tracelog())
        
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = validate_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)

    
@merchant_settings_tagging_bp.route('', methods=['delete'])
@login_required_rest
def delete_tagging():
    tagging_key = request.args.get('tagging_key')
    logger.debug('--- submit delete_tagging data ---')
    try:
        if is_not_empty(tagging_key):
            db_client = create_db_client(caller_info="delete_tagging")
            try:
                with db_client.context():   
                    merchant_tagging = MerchantTagging.fetch(tagging_key)
                    if merchant_tagging:
                        merchant_tagging.delete()
                
                return create_rest_message(gettext('Tag have been deleted'), status_code=StatusCode.OK)
            except:
                return create_rest_message(gettext("Failed to delete tag"), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete tag data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to delete outlet due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)       
    
