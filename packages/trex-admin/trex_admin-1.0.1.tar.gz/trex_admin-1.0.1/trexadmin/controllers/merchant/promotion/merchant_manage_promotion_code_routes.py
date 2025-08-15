'''
Created on 2 Mar 2025

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_promotion_models import MerchantPromotionCode
from trexadmin.forms.merchant.merchant_forms import AddMerchantPromotionCodeForm,\
    UpdateMerchantPromotionCodeForm
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct

merchant_manage_promotion_code_bp = Blueprint('merchant_manage_promotion_code_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/promotion/code')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''


@merchant_manage_promotion_code_bp.context_processor
def merchant_manage_promotion_code_bp_inject_settings():
    
    return dict(
                
                )


@merchant_manage_promotion_code_bp.route('/list', methods=['GET'])
@login_required
def merchant_promotion_code(): 
    return list_merchant_promotion_code_function('merchant/promotion/code/manage_promotion_code_listing.html')
    

@merchant_manage_promotion_code_bp.route('/list-content', methods=['GET'])
@login_required
def merchant_promotion_code_listing_content(): 
    return list_merchant_promotion_code_function('merchant/promotion/code/manage_promotion_code_listing_content.html')

    
def list_merchant_promotion_code_function(template_name):
    merchant_promotion_code_list = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="list_merchant_promotion_code_function")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        __merchant_promotion_code_list = MerchantPromotionCode.list_by_merchant_account(merchant_acct)
    
    for l in __merchant_promotion_code_list:
        merchant_promotion_code_list.append(l.to_dict())
        
    return render_template(template_name,
                           page_title                       = gettext('Manage Promotion Code'),
                           page_url                         = url_for('merchant_manage_promotion_code_bp.merchant_promotion_code'),
                           add_promotion_code_url           = url_for('merchant_manage_promotion_code_bp.add_promotion_code'),
                           reload_list_promotion_code_url   = url_for('merchant_manage_promotion_code_bp.merchant_promotion_code_listing_content'),
                           delete_promotion_code_url        = url_for('merchant_manage_promotion_code_bp.delete_promotion_code'),
                           promotion_code_list              = merchant_promotion_code_list,
                           show_tips                        = True,
                           )

    
@merchant_manage_promotion_code_bp.route('/add', methods=['GET'])
@login_required
def add_promotion_code():
    return render_template('merchant/promotion/code/promotion_code_details.html',
                           page_title=gettext('Add Promotion Code'),
                           post_url=url_for('merchant_manage_promotion_code_bp.add_promotion_code_post'),
                           )    


@merchant_manage_promotion_code_bp.route('/add', methods=['POST'])
@login_required_rest
def add_promotion_code_post():
    promotion_code_data = request.form
    promotion_code_form = AddMerchantPromotionCodeForm(promotion_code_data)
    
    logger.debug('promotion_code_data=%s', promotion_code_data)
    
    return add_or_update_promotion_code_function(promotion_code_form, is_creating_new_promotion_code=True)


@merchant_manage_promotion_code_bp.route('/update', methods=['POST'])
@login_required_rest
def update_promotion_code_post():
    promotion_code_form = UpdateMerchantPromotionCodeForm(request.form)
    return add_or_update_promotion_code_function(promotion_code_form, is_creating_new_code=False)       

    
def add_or_update_promotion_code_function(validate_form, is_creating_new_promotion_code=False):
    
    logger.debug('---add_or_update_promotion_code_function---, is_creating_new_promotion_code=%s', is_creating_new_promotion_code)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    if validate_form.validate():
        try:
            db_client = create_db_client(caller_info="add_or_update_promotion_code_function")
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                same_label_promotion_code = MerchantPromotionCode.get_by_merchant_label(merchant_acct, validate_form.label.data)
                
                if is_creating_new_promotion_code:
                    if same_label_promotion_code:
                        return create_rest_message(gettext('Same label have been used'), status_code=StatusCode.BAD_REQUEST)
                    else:
                        created_promotion_code = MerchantPromotionCode.create(merchant_acct, label=validate_form.label.data, desc=validate_form.desc.data)
                        
                        logger.debug('created_promotion_code=%s', created_promotion_code.to_dict())
                    
                else:
                    promotion_code_key = validate_form.promotion_code_key.data
                    
                    if same_label_promotion_code:
                        if same_label_promotion_code.key_in_str != promotion_code_key:
                            return create_rest_message(gettext('Same label have been used'), status_code=StatusCode.BAD_REQUEST)
                    
                    created_promotion_code = MerchantPromotionCode.fetch(promotion_code_key)
                    
                    created_promotion_code.update(label=validate_form.label.data, desc=validate_form.desc.data)
                
            return create_rest_message(gettext('Promotion code have been updated'),
                                                           status_code=StatusCode.OK,
                                                           created_promotion_code_key=created_promotion_code.key_in_str,
                                                           post_url=url_for('merchant_manage_promotion_code_bp.update_promotion_code_post'))
        except:
            error_message = gettext('Failed to update promotion code')
            logger.warn('Failed due to %s', get_tracelog())
        
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    else:
        error_message = validate_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)

    
@merchant_manage_promotion_code_bp.route('', methods=['delete'])
@login_required_rest
def delete_promotion_code():
    promotion_code_key = request.args.get('promotion_code_key')
    logger.debug('--- submit delete_promotion_code data ---')
    logger.debug('promotion_code_key=%s', promotion_code_key)
    try:
        if is_not_empty(promotion_code_key):
            db_client = create_db_client(caller_info="delete_promotion_code")
            try:
                with db_client.context():   
                    merchant_promotion_code = MerchantPromotionCode.fetch(promotion_code_key)
                    if merchant_promotion_code:
                        merchant_promotion_code.delete()
                
                return create_rest_message(gettext('Promotion code have been deleted'), status_code=StatusCode.OK)
            except:
                return create_rest_message(gettext("Failed to delete promotion code"), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete promotion code data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to delete promotion code due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)       
    
