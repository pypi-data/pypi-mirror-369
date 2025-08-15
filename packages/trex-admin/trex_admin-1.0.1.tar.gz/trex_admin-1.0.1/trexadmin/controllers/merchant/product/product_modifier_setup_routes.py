'''
Created on 23 Nov 2021

@author: jacklok
'''
from flask import Blueprint, request, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging, json
from trexlib.utils.string_util import is_not_empty, is_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexadmin.forms.merchant.product_forms import ProductModifierDetailsForm
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexmodel.models.datastore.product_models import ProductModifier
from trexlib.utils.common.common_util import sort_list
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON, MINE_TYPE_JAVASCRIPT

from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct
import hashlib

product_modifier_setup_bp = Blueprint('product_modifier_setup_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/product/modifier')



#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@product_modifier_setup_bp.route('/list', methods=['GET'])
@login_required
def product_modifier_listing(): 
    product_modifiers_list = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="product_option_listing")
    with db_client.context():
        merchant_acct               = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        __product_modifiers_list    = ProductModifier.list_by_merchant_account(merchant_acct)
    
    for l in __product_modifiers_list:
        product_modifiers_list.append(l.to_dict())
        
    return render_template('merchant/product/modifier/product_modifier_listing.html',
                           page_title                       = gettext('Product Modifier Setup'),
                           page_url                         = url_for('product_modifier_setup_bp.product_modifier_listing'),
                           product_modifiers_list           = product_modifiers_list,
                           add_product_modifier_url         = url_for('product_modifier_setup_bp.add_product_modifier'),
                           reload_list_product_modifier_url = url_for('product_modifier_setup_bp.modifier_listing_content'),
                           #edit_product_modifier_url        = url_for('product_modifier_setup_bp.edit_product_modifier'),
                           show_tips                        = True,
                           )

@product_modifier_setup_bp.route('/modifier-listing-content', methods=['GET'])
@login_required
def modifier_listing_content(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    currency_details            = get_merchant_configured_currency_details()
    product_modifiers_list      = []
    db_client = create_db_client(caller_info="modifier_listing_content")
    try:
        with db_client.context():
            merchant_acct               = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
            __modifier_list             = ProductModifier.list_by_merchant_account(merchant_acct)
            if __modifier_list:
                for modifier in __modifier_list:
                    product_modifiers_list.append(modifier.to_dict())
                        
            
    except:
        logger.error('Fail to list membership due to %s', get_tracelog())
           
    
    return render_template('merchant/product/modifier/product_modifier_listing_content.html',
                           product_modifiers_list           = product_modifiers_list,
                           currency_details                 = currency_details,
                           )

@product_modifier_setup_bp.route('/add', methods=['GET'])
@login_required
def add_product_modifier(): 
    currency_details            = get_merchant_configured_currency_details()
    
    return render_template('merchant/product/modifier/product_modifier_details.html',
                           currency_details = currency_details,
                           post_url = url_for('product_modifier_setup_bp.product_modifier_post'),
                           )
    
@product_modifier_setup_bp.route('/<product_modifier_key>', methods=['GET'])
@login_required
def edit_product_modifier(product_modifier_key): 
    
    logger.debug('---edit_product_modifier---')
    
    #product_modifier_key        = request.args.get('product_modifier_key')
    currency_details            = get_merchant_configured_currency_details()
    
    logger.debug('product_modifier_key=%s', product_modifier_key)
    
    db_client = create_db_client(caller_info="edit_product_modifier")
            
    with db_client.context():
        product_modifier    = ProductModifier.fetch(product_modifier_key)
        if product_modifier:
            product_modifier = product_modifier.to_dict()
    
    return render_template('merchant/product/modifier/product_modifier_details.html',
                           currency_details = currency_details,
                           post_url         = url_for('product_modifier_setup_bp.product_modifier_post'),
                           product_modifier = product_modifier,
                           )    
    
@product_modifier_setup_bp.route('/', methods=['POST','PUT'])
@login_required
def product_modifier_post():
    
    product_modifier_data           = request.form
    product_modifier_form           = ProductModifierDetailsForm(product_modifier_data)
    
    logger.debug('product_modifier_data=%s', product_modifier_data)
    
    try:
        if product_modifier_form.validate():
            
            is_new_setup            = False
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            
            modifier_key            = product_modifier_form.modifier_key.data
            modifier_name           = product_modifier_form.modifier_name.data
            modifier_label          = product_modifier_form.modifier_label.data
            modifier_options        = product_modifier_form.modifier_options.data
            allow_multiple_option   = product_modifier_form.allow_multiple_option.data
            option_is_mandatory     = product_modifier_form.option_is_mandatory.data
            have_default_option     = False
            
            if modifier_options: 
                for modifier_option in modifier_options.values():
                    if modifier_option.get('is_default'):
                        have_default_option = True
                        break
            
            logger.debug('allow_multiple_option=%s', allow_multiple_option)
            logger.debug('modifier_options=%s', modifier_options)    
            
            db_client = create_db_client(caller_info="product_modifier_post")
            
            if allow_multiple_option==False:
                #check how many default option
                default_option_count = 0
                for option_details in modifier_options.values():
                    logger.debug('option_details=%s', option_details);
                    
                    if option_details.get('is_default'):
                        default_option_count+=1
                     
                logger.debug('default_option_count=%s', default_option_count)
                if default_option_count>1:
                    return create_rest_message(gettext('More than one default option is not allow. Please turn on allow multiple option otherwise please remain 1 default option'), status_code=StatusCode.BAD_REQUEST)
                    
            
            with db_client.context():
                merchant_acct = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                if is_not_empty(modifier_key):
                    logger.debug('going to update product modifier')
                    
                    product_modifier    = ProductModifier.fetch(modifier_key)
                    
                    if product_modifier:
                    
                        ProductModifier.update(product_modifier, 
                                                modifier_name,
                                                modifier_label          = modifier_label,    
                                                modifier_options        = modifier_options,
                                                have_default_option     = have_default_option,
                                                allow_multiple_option   = allow_multiple_option,
                                                option_is_mandatory     = option_is_mandatory,
                                               )
                    
                    
                else:
                    logger.debug('going to create prepaid settings')
                    
                    product_modifier    = ProductModifier.create(merchant_acct, 
                                                                    modifier_name,
                                                                    modifier_label          = modifier_label,
                                                                    modifier_options        = modifier_options,
                                                                    have_default_option     = have_default_option,
                                                                    allow_multiple_option   = allow_multiple_option,
                                                                    option_is_mandatory     = option_is_mandatory,
                                                                   )
                
                    is_new_setup = True
            
            logger.debug('is_new_setup=%s', is_new_setup)
            
            if product_modifier is None:
                logger.debug('product_modifier is None')
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                if is_new_setup:
                    
                    return create_rest_message(status_code  = StatusCode.OK, 
                                           modifier_key = product_modifier.key_in_str,
                                           )
                else:
                    return create_rest_message(status_code=StatusCode.OK)
            
                    
        else:
            error_message = product_modifier_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to setup modifier due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@product_modifier_setup_bp.route('/enable/<product_modifier_key>', methods=['POST','GET'])
@login_required
def enable_product_modifier(product_modifier_key): 
    return enable_or_disable_product_modifier(product_modifier_key, True)

@product_modifier_setup_bp.route('/disable/<product_modifier_key>', methods=['POST','GET'])
@login_required
def disable_product_modifier(product_modifier_key): 
    return enable_or_disable_product_modifier(product_modifier_key, False)
    
def enable_or_disable_product_modifier(product_modifier_key, to_enable): 
    
    db_client               = create_db_client(caller_info="enable_or_disable_product_modifier")
    
    try:
        with db_client.context():
            if is_empty(product_modifier_key):
                return create_rest_message(gettext('Invaid modifier data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                product_modifier = ProductModifier.fetch(product_modifier_key)
                if product_modifier:
                    if to_enable:
                        ProductModifier.enable(product_modifier) 
                        logger.debug('Modifier have been enabled')
                    else:
                        ProductModifier.disable(product_modifier)
                        logger.debug('Modifier program have been disabled')
                    
        if ProductModifier is None:
            return create_rest_message(gettext('Invalid modifier'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update modifier due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update modifier'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)   

@product_modifier_setup_bp.route('/archive/<product_modifier_key>', methods=['POST','GET'])
@login_required
def archive_product_modifier(product_modifier_key): 
    
    logger.debug('---archive_product_modifier---')
    
    db_client   = create_db_client(caller_info="archive_product_modifier")
    
    try:
        with db_client.context():
            if is_empty(product_modifier_key):
                return create_rest_message(gettext('Invaid modifier data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                product_modifier = ProductModifier.fetch(product_modifier_key)
                if product_modifier:
                    product_modifier.archive(product_modifier) 
                    logger.debug('Modifier have been archived')
                    
        if product_modifier is None:
            return create_rest_message(gettext('Invalid modifier'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update modifier due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive modifier'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,) 

def parse_to_option_json(modifier_options_list):
    data_list = []
    
    for option in modifier_options_list:
        data = {
                    'code'  : option.key_in_str,
                    'label' : option.modifier_name,
                    
                }
        data_list.append(data)
    
    return data_list

def get_product_modifier_code_label_json():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="get_product_modifier_code_label_json")
    with db_client.context():
        merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        merchant_acct       = merchant_user.merchant_acct
        modifiers_list      = ProductModifier.list_by_merchant_account(merchant_acct)
    
    return parse_to_option_json(modifiers_list)


@product_modifier_setup_bp.route('/list-product-modifier-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_product_modifier_code_label():
    logger.debug('---list_product_modifier_code_label--- ')
    
    product_modifier_in_json  = json.dumps(get_product_modifier_code_label_json(), sort_keys = True, separators = (',', ': '))
    
    resp    = create_cached_response(product_modifier_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return resp
    
    

