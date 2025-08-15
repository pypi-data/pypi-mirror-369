'''
Created on 22 Jul 2021

@author: jacklok
'''
from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging, json
from trexlib.utils.string_util import is_not_empty, is_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexadmin.forms.merchant.product_forms import ProductCategorySetupForm,\
    ProductCategoryUpdateForm
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.product_models import ProductCategory
from trexlib.utils.common.common_util import sort_list
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON

from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct
from trexadmin.libs.decorators import elapsed_time_trace
from trexlib.utils.common.cache_util import cache
import hashlib
from trexlib.libs.flask_wtf.request_wrapper import request_values

product_category_setup_bp = Blueprint('product_category_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/product/category')


logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')


@product_category_setup_bp.route('/', methods=['get'])
@login_required
def product_category_setup():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="product_category_setup")
    with db_client.context():
        merchant_user = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        product_category_list            = get_product_category_structure(merchant_user)
        
    #logger.debug('product_category_list=%s', product_category_list)
    
    return render_template('merchant/product/category/product_category_setup.html', 
                           page_title                       = gettext('Category Setup'),
                           create_product_category_url      = url_for('product_category_setup_bp.create_product_category_post'),
                           update_product_category_url      = url_for('product_category_setup_bp.update_product_category_post'),
                           delete_product_category_url      = url_for('product_category_setup_bp.delete_product_category_post'),
                           product_category_list            = product_category_list,
                           )
    
def get_product_category_structure(logged_in_merchant_user):
    
    sorted_category_structure = []
    
    merchant_acct           = logged_in_merchant_user.merchant_acct
    category_structure      = ProductCategory.get_structure_by_merchant_acct(merchant_acct)
    category_structure      = sort_list(category_structure, sort_attr_name='category_label')
    
    #logger.debug('category_structure=%s', category_structure)
    
    for c in category_structure:
        sorted_category_structure.append(c.to_dict())
    
    
    logger.debug('sorted_category_structure=%s', sorted_category_structure)
            
    return sorted_category_structure

def get_product_category_structure_by_merchant_acct(merchant_acct):
    
    sorted_category_structure = []
    
    category_structure      = ProductCategory.get_structure_by_merchant_acct(merchant_acct)
    category_structure      = sort_list(category_structure, sort_attr_name='category_label')
    
    #logger.debug('category_structure=%s', category_structure)
    
    for c in category_structure:
        sorted_category_structure.append(c.to_dict())
    
    
    logger.debug('sorted_category_structure=%s', sorted_category_structure)
            
    return sorted_category_structure

def get_product_category_listing(logged_in_merchant_user):
    
    category_structure = []
    
    merchant_acct           = logged_in_merchant_user.merchant_acct
    category_listing        = ProductCategory.list_by_merchant_acct(merchant_acct)
    
    for c in category_listing:
        category_structure.append(c.to_dict())
    
    
    logger.debug('category_structure=%s', category_structure)
            
    return category_structure


@product_category_setup_bp.route('/delete', methods=['POST'])
@login_required
@request_values
def delete_product_category_post(request_values):
    category_key_list = request_values.getlist('category_key_list[]')
    
    logger.debug('category_key_list=%s', category_key_list)
    
    if is_not_empty(category_key_list):
        db_client = create_db_client(caller_info="delete_product_category_post")
        
        is_product_category_found = False
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        
        with db_client.context():
            merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            for category_key in category_key_list:
                product_category = ProductCategory.fetch(category_key)
                if product_category:
                    is_product_category_found = True
                    ProductCategory.remove(product_category, merchant_acct)
                    
                
            
            category_structure      = get_product_category_structure(merchant_user)
                
        if is_product_category_found:
            cache.delete_memoized(get_product_category_code_label_json)
            return create_rest_message(
                                        product_category_list  = category_structure,
                                        status_code=StatusCode.OK
                                        )
        else:
            return create_rest_message("Invalid category key", status_code=StatusCode.BAD_REQUEST)
    else:
        logger.error('Missing category key to delete')
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@product_category_setup_bp.route('/', methods=['POST'])
@login_required
@request_values
def create_product_category_post(request_values):
    
    product_category_setup_data      = request_values
    product_category_setup_form      = ProductCategorySetupForm(product_category_setup_data)
    
    logger.debug('product_category_setup_data=%s', product_category_setup_data)
    
    logger.debug('product_category_setup_form.category_group_key.data=%s', product_category_setup_form.category_group_key.data)
    logger.debug('product_category_setup_form.category_label.data=%s', product_category_setup_form.category_label.data)
    
    try:
        if product_category_setup_form.validate():
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            db_client = create_db_client(caller_info="create_product_category_post")
            with db_client.context():
                logger.debug('Going to create sub category')
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                product_modifier = product_category_setup_form.product_modifier.data or ''
                if is_not_empty(product_modifier):
                    product_modifier = product_modifier.split(',')
                else:
                    product_modifier = []
                
                logger.debug('product_modifier=%s', product_modifier)
                
                ProductCategory.create(
                                        product_category_setup_form.category_label.data, 
                                        parent_category_key     = product_category_setup_form.category_group_key.data,
                                        product_modifier        = product_modifier,
                                        merchant_acct           = merchant_acct, 
                                        created_by              = merchant_user
                                        )
                
                category_structure      = get_product_category_structure(merchant_user)
                    
                cache.delete_memoized(get_product_category_code_label_json)
                   
                return create_rest_message(
                                        product_category_list  = category_structure, 
                                        status_code=StatusCode.OK
                                        )
            
        else:
            error_message = product_category_setup_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Failed to create product category due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@product_category_setup_bp.route('/', methods=['PUT'])
@login_required
@request_values
def update_product_category_post(request_values):
    
    product_category_update_data      = request_values
    product_category_update_form      = ProductCategoryUpdateForm(product_category_update_data)
    
    logger.debug('product_category_update_data=%s', product_category_update_data)
    
    logger.debug('product_category_update_form.category_key.data=%s', product_category_update_form.category_key.data)
    logger.debug('product_category_update_form.category_label.data=%s', product_category_update_form.category_label.data)
    
    try:
        if product_category_update_form.validate():
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            logger.debug('Going to update sub category')
            found_category_to_update = False
            db_client = create_db_client(caller_info="update_product_category_post")
            with db_client.context():
                
                product_modifier = product_category_update_form.product_modifier.data or ''
                product_modifier = product_modifier.split(',')
                
                logger.debug('product_modifier=%s', product_modifier)
                
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                
                product_category = ProductCategory.fetch(product_category_update_form.category_key.data)
                
                if product_category:
                    found_category_to_update = True
                    
                    ProductCategory.update(
                                        product_category,    
                                        product_category_update_form.category_label.data, 
                                        product_modifier    = product_modifier,
                                        modified_by         = merchant_user
                                        )
                    category_structure      = get_product_category_structure(merchant_user)
                    
                    
                else:
                    return create_rest_message(gettext('Invalid Product Category data'), status_code=StatusCode.BAD_REQUEST)
            
            
            
            if found_category_to_update:
                cache.delete_memoized(get_product_category_code_label_json)
                return create_rest_message(
                                        product_category_list  = category_structure, 
                                        status_code=StatusCode.OK
                                        )
                
            else:
                return create_rest_message(gettext('Invalid Product Category data'), status_code=StatusCode.BAD_REQUEST)
            
        else:
            error_message = product_category_update_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Failed to create product category due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to update product category'), status_code=StatusCode.BAD_REQUEST)    

@elapsed_time_trace(trace_key="construct_category_tree_structure")
def construct_category_tree_structure(category_tree_structure, category_list):
    for category in category_list:
        if is_empty(category.get('parent_category_key')):
            #top most category
            category_tree_structure.append(category)
            __find_child_category(category, category_list)
                
    
def __find_child_category(category, category_list):
    if is_not_empty(category.get('child_category_keys')):
        childs                      = []
        parent_product_modifier     = category.get('product_modifier') or []
        
        for child_category_key in category.get('child_category_keys'):
            child = __lookup_category_from_category_list(child_category_key, category_list)
            
            logger.debug('category product_modifier of %s =%s', category.get('key'), parent_product_modifier)
            if child:
                child_product_modifier      = child.get('product_modifier') or []
                child_product_modifier      = list(set(parent_product_modifier) | set(child_product_modifier) )
                child['product_modifier']   = child_product_modifier
                
                logger.debug('child_product_modifier of %s =%s', category.get('key'), child_product_modifier)
                
                if is_not_empty(child.get('child_category_keys')):
                    __find_child_category(child, category_list)
                childs.append(child)
        
        category['childs'] = childs
        
def __lookup_category_from_category_list(category_code, category_list):
    for category in category_list:
        if category.get('key') == category_code:
            return category  

def render_to_select_option_html(product_category_structure_option, show_item_count=True, show_product_item_in_data=False, 
                                 selected_category_code=None, menu_settings=None):
    
    html_string = ''
    if is_not_empty(product_category_structure_option):
        for pc in product_category_structure_option:
            #logger.debug('pc=%s', pc)
            
            if show_item_count:
                label = pc.get('label_with_item_count')
            else:
                label = pc.get('label')
            
            product_modifier = pc.get('product_modifier')
            if product_modifier:
                product_modifier = ','.join(pc.get('product_modifier'))
            else:
                product_modifier = ''
            
            if pc.get('group'):
                child_option_html = render_to_select_option_html(pc.get('childs'), 
                                                                 show_item_count            = show_item_count, 
                                                                 menu_settings              = menu_settings, 
                                                                 show_product_item_in_data  = show_product_item_in_data, 
                                                                 selected_category_code     = selected_category_code)
                
                html_string += '<optgroup label="{label}">{child_option}</optgroup>'.format(label=label, child_option=child_option_html, product_modifier=product_modifier)
            else:
                to_show_option  = True
                category_code   = pc.get('code')
                product_items   = ','.join(pc.get('product_items') or [])
                product_items_count = 0
                if pc.get('product_items'):
                    product_items_count = len(pc.get('product_items'))
                    
                if menu_settings:
                    to_show_option = False
                    for __category_code, product_items_list in menu_settings.items():
                        if category_code == __category_code:
                            to_show_option = True
                            product_items       = ','.join(product_items_list or [])
                            product_items_count = len(product_items_list)
                            break
                
                if to_show_option:
                    _html_format = '<option value="{value}" {selected} data-product-modifier="{product_modifier}" data-product-items="{product_items}" data-product-items-count="{product_items_count}">{label}</option>'
                    
                    if selected_category_code:
                        if selected_category_code == category_code:
                            if show_product_item_in_data:
                                
                                html_content = _html_format.format(value=category_code, label=label, product_modifier=product_modifier, product_items=product_items, product_items_count=product_items_count, selected='selected')
                                
                            else:
                                html_content = _html_format.format(value=category_code, label=label, product_modifier=product_modifier, product_items='', product_items_count=product_items_count, selected='selected')
                                
                        else:
                            if show_product_item_in_data:
                                
                                html_content = _html_format.format(value=category_code, label=label, product_modifier=product_modifier, product_items=product_items, product_items_count=product_items_count, selected='')
                                
                            else:
                                html_content = _html_format.format(value=category_code, label=label, product_modifier=product_modifier, product_items='', product_items_count=product_items_count, selected='')
        
                    else:
                        if show_product_item_in_data:
                            html_content = _html_format.format(value=category_code, label=label, product_modifier=product_modifier, product_items=product_items, product_items_count=product_items_count, selected='')
                            
                        else:
                            html_content = _html_format.format(value=category_code, label=label, product_modifier=product_modifier, product_items='', product_items_count=product_items_count, selected='')
                            
                    
                    html_string+=html_content
            
            
    return html_string
            
def parse_to_option_json(category_tree_structure):
    data_list = []
    
    for category in category_tree_structure:
        data = {
                    'code'                  : category.get('key'),
                    'label'                 : category.get('category_label'),
                    'label_with_item_count' : category.get('category_label_and_other_details'),
                    'group'                 : category.get('has_child'),
                    'product_modifier'      : category.get('product_modifier'),
                    'product_items'         : category.get('product_items'),
                }
        if category.get('childs'):
            child_data_list = parse_to_option_json(category.get('childs'))
            if child_data_list:
                data['childs'] = child_data_list   
        
        data_list.append(data)
    
    return data_list

def get_product_category_structure_code_label_json():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="get_product_category_structure_code_label_json")
    with db_client.context():
        merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        category_list       = get_product_category_structure(merchant_user)
    
    category_tree_structure = []
    
    construct_category_tree_structure(category_tree_structure, category_list)
    
    return parse_to_option_json(category_tree_structure)

def get_product_category_structure_code_label_json_by_merchant_acct(merchant_acct):
    category_list       = get_product_category_structure_by_merchant_acct(merchant_acct)
    
    category_tree_structure = []
    
    construct_category_tree_structure(category_tree_structure, category_list)
    
    return parse_to_option_json(category_tree_structure)

def product_category_cache_key(f, *args, **kwargs):
    # Create a unique string based on function arguments
    key_data = { 'product_category'
        'args': args,
        'kwargs': kwargs
    }
    # Convert the key data to a JSON string
    key_string = json.dumps(key_data, sort_keys=True)
    # Generate an MD5 hash of the key string
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()

@cache.memoize(timeout=300)
def get_product_category_code_label_json():
    logger.debug('reading product category from server')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="get_product_category_code_label_json")
    with db_client.context():
        merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        category_list       = get_product_category_listing(merchant_user)
    
    return parse_to_option_json(category_list)

get_product_category_code_label_json.make_cache_key=product_category_cache_key

@product_category_setup_bp.route('/list-category-code-structure', methods=['GET'])
#@cache.cached(timeout=50)
def list_category_code_label_in_structure():
    logger.debug('---list_category_code_label_in_structure--- ')
    
    category_tree_structure_in_json  = json.dumps(get_product_category_code_label_json(), sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(category_tree_structure_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  )
    
    return resp

@product_category_setup_bp.route('/list-structured-category-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_structured_category_code_label():
    logger.debug('---list_structured_category_code_label--- ')
    category_tree_structure_in_json  = json.dumps(get_product_category_structure_code_label_json(), sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(category_tree_structure_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  )
    
    return resp

@product_category_setup_bp.route('/list-category-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_category_code_label():
    logger.debug('---list_category_code_label_in_structure--- ')
    
    category_tree_structure_in_json  = json.dumps(get_product_category_code_label_json(), sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(category_tree_structure_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  )
    
    return resp

