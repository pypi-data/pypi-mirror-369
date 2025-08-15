'''
Created on 22 Jul 2021

@author: jacklok
'''

from flask import Blueprint, request, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexlib.utils.string_util import is_empty, is_not_empty, random_string
from flask.helpers import url_for
from trexconf import conf
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexadmin.libs.flask.pagination import CursorPager
from trexadmin.controllers.merchant.product.product_category_setup_routes import get_product_category_structure_code_label_json,\
    render_to_select_option_html
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexlib.utils.crypto_util import decrypt_json, encrypt_json
from trexadmin.forms.merchant.product_forms import ProductSearchForm,\
    UpdateProductForm,\
    ProductSettingOnPOSForm, CreateProductForm
from trexmodel.models.datastore.product_models import Product, ProductFile
from trexmodel.models.datastore.model_decorators import model_transactional
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexadmin.controllers.system.system_route_helpers import get_currency_config
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
import json
from trexweb.utils.common.http_response_util import create_cached_response,\
    MINE_TYPE_JSON
from trexlib.utils.common.cache_util import cache
from datetime import datetime
from flask.json import jsonify
import hashlib
from trexlib.libs.flask_wtf.request_wrapper import request_form, request_files,\
    request_values

product_setup_bp = Blueprint('product_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/product/item')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')



@product_setup_bp.route('/', methods=['get'])
def product_search():
    
    product_category_structure_option    = get_product_category_structure_code_label_json()
    product_category_select_option_html  = render_to_select_option_html(product_category_structure_option)
    
    logger.debug('product_category_select_option_html=%s', product_category_select_option_html)
    
    return render_template('merchant/product/item/product_search.html', 
                           page_title                           = gettext('Product Setup'),
                           product_search_url                   = url_for('product_setup_bp.search_product',
                                                                          limit     = conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE,
                                                                          #limit     = 1,
                                                                          page_no   = 1
                                                                          ),
                           product_category_select_option_html  = product_category_select_option_html,
                           )


@product_setup_bp.route('/details', methods=['get'])
def add_product():
    
    product_category_structure_option    = get_product_category_structure_code_label_json()
    product_category_select_option_html  = render_to_select_option_html(product_category_structure_option)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="add_product")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        currency_code   = merchant_acct.currency_code
    
    currency_details                    = get_currency_config(currency_code)
    
    logger.debug('product_category_select_option_html=%s', product_category_select_option_html)
    
    return render_template('merchant/product/item/product_details.html', 
                           page_title                           = gettext('Product Details'),
                           
                           update_product_url                   = url_for('product_setup_bp.add_product_post'),
                           product_image_video_url              = url_for('product_setup_bp.product_image_video'),
                           product_setting_on_pos_url           = url_for('product_setup_bp.product_setting_on_pos'),
                           
                           product_category_select_option_html  = product_category_select_option_html,
                           currency_details                     = currency_details,
                           tab_id                               = random_string(6),
                           )

@product_setup_bp.route('/product/search/page-size/<limit>/page/<page_no>', methods=['POST', 'GET'])
@login_required
def search_product(limit, page_no):
    logger.debug('---search_product---')
    encrypted_search_product_data  = request.args.get('encrypted_search_product_data') or {}
    
    logger.debug('encrypted_search_product_data=%s', encrypted_search_product_data)
    
    if encrypted_search_product_data:
        search_product_data            = decrypt_json(str.encode(encrypted_search_product_data))
        search_product_form            = ProductSearchForm(data=search_product_data)
        logger.debug('search_customer_data from search_product_data=%s', search_product_data)
        
    else:
        search_product_data             = request.form
        search_product_form             = ProductSearchForm(search_product_data)
        #encrypted_search_customer_data  = encrypt_json(search_customer_data).decode("utf-8")
        encrypted_search_product_data  = encrypt_json(search_product_data) 
    
        logger.debug('search_product_data from search form=%s', search_product_data)
        
        
        logger.debug('encrypted_search_product_data after encrypted=%s', encrypted_search_product_data)
    
    
    product_list                = []
    total_count                 = 0
    
    page_no_int                 = int(page_no)
    limit_int                   = int(limit)
    
    if search_product_form.validate():
        product_sku                 = search_product_form.product_sku.data
        product_name                = search_product_form.product_name.data
        product_category            = search_product_form.product_category.data
        
        cursor                          = request.args.get('cursor')
        previous_cursor                 = request.args.get('previous_cursor')
        
        logger.debug('product_sku=%s', product_sku)
        logger.debug('product_name=%s', product_name)
        logger.debug('product_category=%s', product_category)
        logger.debug('limit=%s', limit)
        
        logger.debug('cursor=%s', cursor)
        logger.debug('previous_cursor=%s', previous_cursor)
        
        
        db_client = create_db_client(caller_info="search_customer")
        
        if is_not_empty(product_name):
            product_name = product_name.strip()
        
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        try:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                (search_results, total_count, next_cursor)  = Product.search_merchant_product(merchant_acct, 
                                                                                                product_name            = product_name,
                                                                                                product_sku             = product_sku,
                                                                                                category_key            = product_category, 
                                                                                                limit                   = limit_int,
                                                                                                start_cursor            = cursor,
                                                                                                )
                
                for r in search_results:
                    product_list.append(r.to_dict())
                    
                
        except:
            logger.error('Fail to search product due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to search product'), status_code=StatusCode.BAD_REQUEST)
            
        
        
        logger.debug('total_count=%s', total_count)
        logger.debug('product_list=%s', product_list)
    else:
        logger.debug('search form invalid')
        error_message = search_product_form.create_rest_return_error_message()
                
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
        
            
    pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                     = next_cursor, 
                                previous_cursor                 = previous_cursor,
                                current_cursor                  = cursor,
                                encrypted_search_product_data  = encrypted_search_product_data,
                              ) 
    pages       = pager.get_pages()
    
    return render_template('merchant/product/item/product_listing_content.html', 
                               product_list                 = product_list,
                               end_point                    = 'product_setup_bp.search_product',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#product_search_list_div',
                               ) 

@product_setup_bp.route('/<product_key>', methods=['GET'])
def read_product(product_key):
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="read_product")
    
    try:
        with db_client.context():
            product = Product.fetch(product_key)
            product = product.to_dict()
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            currency_code   = merchant_acct.currency_code
        
        
        currency_details                        = get_currency_config(currency_code)
        product_category_structure_option       = get_product_category_structure_code_label_json()
        product_category_select_option_html     = render_to_select_option_html(product_category_structure_option, selected_category_code=product.get('category_code'))
        
        return render_template('merchant/product/item/product_details.html', 
                           page_title                           = gettext('Product Details'),
                           update_product_url         = url_for('product_setup_bp.update_product_post'),
                           product_image_video_url              = url_for('product_setup_bp.product_image_video'),
                           product_setting_on_pos_url           = url_for('product_setup_bp.product_setting_on_pos'),
                           product_category_select_option_html  = product_category_select_option_html,
                           product                              = product,
                           currency_details                     = currency_details,
                           product_key                          = product_key,
                           tab_id                               = random_string(6),
                           )
        
    except:
        logger.error('Fail to search customer due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search customer'), status_code=StatusCode.BAD_REQUEST)
    
@product_setup_bp.route('/product-file/<product_file_key>', methods=['GET'])
def read_product_file(product_file_key):
    
    
    db_client = create_db_client(caller_info="read_product_file")
    
    try:
        with db_client.context():
            product_file = ProductFile.fetch(product_file_key)
            product_file = product_file.to_dict()
        
        
        return render_template('merchant/product/item/product_file_content.html', 
                           product_file                         = product_file,
                           )
        
    except:
        logger.error('Fail to search customer due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search customer'), status_code=StatusCode.BAD_REQUEST)    
    
@product_setup_bp.route('/image-video', methods=['GET'])
def product_image_video():
    product_key = request.args.get('product_key')
    db_client = create_db_client(caller_info="product_image_video")
    
    product_file_dict_listing = []
    
    try:
        with db_client.context():
            product = Product.fetch(product_key)
            if product:
                product_file_listing = ProductFile.list_by_product(product)
                
                if product_file_listing:
                    for product_file in product_file_listing:
                        product_file_dict_listing.append(product_file.to_dict())
                    
        
        
        return render_template('merchant/product/item/product_upload_image_video_content.html', 
                           page_title                           = gettext('Product Image/Video'),
                           product_key                          = product_key,
                           product_file_listing                 = product_file_dict_listing,
                           upload_product_file_url              = url_for('product_setup_bp.upload_product_file_post'),
                           )
        
    except:
        logger.error('Fail to read product image/video due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to read product image/video'), status_code=StatusCode.BAD_REQUEST)    
    
    
@product_setup_bp.route('/profile-file/<product_file_key>', methods=['DELETE'])    
def delete_product_file_post(product_file_key):    
    if is_not_empty(product_file_key):
        db_client       = create_db_client( caller_info="upload_product_file_post")
        product_file    = None
        bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
        with db_client.context():
            product_file = ProductFile.fetch(product_file_key)
            ProductFile.remove_file(product_file, bucket)
        
        if product_file:
            return create_rest_message(status_code=StatusCode.ACCEPTED)
        else:
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@product_setup_bp.route('/product-file', methods=['POST'])    
@limit_content_length(1*1024*1024) # limit to 1mb
@request_form
@request_files
def upload_product_file_post(request_form, request_files):    
    product_key         = request_form.get('product_key')
    product_file_type   = request_form.get('product_file_type')
    uploaded_file       = request_files.get('file')
    
    logged_in_merchant_user       = get_loggedin_merchant_user_account()
    
    logger.debug('product_key=%s', product_key)
    logger.debug('product_file_type=%s', product_file_type)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))

    db_client = create_db_client( caller_info="upload_product_file_post")
        
    with db_client.context():
        product = Product.fetch(product_key)
        
        if product:
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
            product_file    = ProductFile.upload_file(uploaded_file, product, merchant_acct, bucket, product_file_type=product_file_type)
            
            if product_file:
                product_file = product_file.to_dict()
            
            logger.debug('After uploaded product file')
            
        else:
            logger.warn('Failed to fetch product data')
         
    if product_file:
        return render_template('merchant/product/item/product_file_content.html', 
                           product_file                         = product_file,
                           )
    else: 
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@product_setup_bp.route('/', methods=['POST'])
@request_form
def add_product_post(request_form):
    logger.debug('--- submit add_customer data ---')
    add_product_data = request_form
    
    logger.debug('add_product_data=%s', add_product_data)
    
    add_product_form = CreateProductForm(add_product_data)
    
    product_sku      = add_product_form.product_sku.data
    
    @model_transactional(desc='add_product_post')
    def __start_transaction(created_by):
        
        logger.debug('--add_product_post--')
        
        try:
            
            
            product_modifier    = add_product_form.product_modifier.data or ''
            if is_not_empty(product_modifier):
                product_modifier = product_modifier.split(',')
            else:
                product_modifier = []
                        
            
            logger.debug('product_modifier=%s', product_modifier)
            
            created_product = Product.create(
                                            product_sku,
                                            add_product_form.product_name.data,
                                            add_product_form.product_category.data,
                                            merchant_acct,           
                                            price                   = float(add_product_form.price.data),
                                            cost                    = float(add_product_form.cost.data), 
                                            barcode                 = add_product_form.barcode.data,
                                            product_desc            = add_product_form.product_desc.data,
                                            product_modifier        = product_modifier,
                                            created_by              = created_by
                                            )
            
        
            cache.delete_memoized(get_product_code_label_json)
            cache.delete_memoized(get_product_code_group_by_category_label_json)
            
            return created_product
            
        except:
            logger.error('Failed to create customer due to %s', get_tracelog())
    
    try:
        if add_product_form.validate():
            is_unique_sku = True
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            db_client = create_db_client(caller_info="add_product_post")
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                
                checking_unique_product = Product.get_by_product_sku(product_sku, merchant_acct)
                if checking_unique_product is None:
                    created_product = __start_transaction(merchant_user)
                else:
                    is_unique_sku = False
            
            if is_unique_sku:
                if created_product is None:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                else:
                    if created_product:
                        return create_rest_message(gettext('Product have been created'), 
                                               status_code  = StatusCode.OK, 
                                               created_product_key = created_product.key_in_str,
                                               )
                    else:
                        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                return create_rest_message(gettext('SKU have been taken'), status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = add_product_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to add product due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@product_setup_bp.route('/', methods=['PUT'])
@request_form
def update_product_post(request_form):
    logger.debug('--- submit update_product_post data ---')
    update_product_data = request_form
    
    logger.debug('update_product_data=%s', update_product_data)
    
    update_product_form = UpdateProductForm(update_product_data)
    
    product_sku      = update_product_form.product_sku.data
    
    @model_transactional(desc='update_product_post')
    def __start_transaction(updating_product, updated_by):
        
        logger.debug('--update_product_post--')
        
        
        product_modifier = update_product_form.product_modifier.data or ''
        if is_not_empty(product_modifier):
            product_modifier = product_modifier.split(',')
        else:
            product_modifier = []
        
        logger.debug('product_modifier=%s', product_modifier)
        
        updating_product.product_sku         = update_product_form.product_sku.data
        updating_product.category_key        = update_product_form.product_category.data
        updating_product.product_name        = update_product_form.product_name.data
        updating_product.barcode             = update_product_form.barcode.data
        updating_product.price               = float(update_product_form.price.data)
        updating_product.cost                = float(update_product_form.cost.data)
        updating_product.product_desc        = update_product_form.product_desc.data
        updating_product.product_modifier    = product_modifier
        
        Product.update(
                            updating_product,
                            updated_by              = updated_by
                            )
        
        
            
        
    
    try:
        if update_product_form.validate():
            is_unique_sku           = True
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            db_client               = create_db_client(caller_info="update_product_post")
            
            with db_client.context():
                updating_product        = Product.fetch(update_product_form.product_key.data)
                merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                checking_unique_product = Product.get_by_product_sku(product_sku, merchant_acct)
                if checking_unique_product is None or checking_unique_product.equal(updating_product):
                    __start_transaction(updating_product, merchant_user)
                else:
                    is_unique_sku = False
                
            
            cache.delete_memoized(get_product_code_label_json)
            cache.delete_memoized(get_product_code_group_by_category_label_json)
                
            if is_unique_sku:
            
                return create_rest_message(gettext('Product have been updated'), 
                                           status_code  = StatusCode.OK
                                           )
            else:
                return create_rest_message(gettext('SKU have been taken'), status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = update_product_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update product due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@product_setup_bp.route('/<product_key>', methods=['DELETE'])
def delete_product(product_key):
    try:
        if is_not_empty(product_key):
            
            db_client       = create_db_client(caller_info="delete_product")
            bucket          = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)
            with db_client.context():
                deleting_product = Product.fetch(product_key)
                if deleting_product:
                    Product.remove(deleting_product, bucket)
                    cache.delete_memoized(get_product_code_label_json)
                    cache.delete_memoized(get_product_code_group_by_category_label_json())
            
            if deleting_product:
                return create_rest_message(gettext('Product have been deleted'), 
                                           status_code  = StatusCode.OK
                                           )
            else:
                return create_rest_message(gettext('Invalid product data'), status_code=StatusCode.BAD_REQUEST)
                
        else:
            return create_rest_message(gettext('Invalid product data'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to delete product due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to delete the product'), status_code=StatusCode.BAD_REQUEST)
    
@product_setup_bp.route('/product-setting-on-pos', methods=['GET'])
@request_values
def product_setting_on_pos(request_values):
    logger.debug('---product_setting_on_pos---')
    product_key = request_values.get('product_key')
    
    logger.debug('product_key=%s', product_key)
    
    db_client = create_db_client(caller_info="product_setting_on_pos")
    product_image_dict_listing  = []
    pos_settings                = None
    default_image_url           = None
    
    try:
        with db_client.context():
            product = Product.fetch(product_key)
            if product:
                if product.pos_settings:
                    pos_settings = product.pos_settings
                    
                product_file_listing = ProductFile.list_by_product(product)
                
                if product_file_listing:
                    for product_file in product_file_listing:
                        logger.debug('product_file.product_file_type=%s', product_file.product_file_type)
                        if product_file.product_file_type.startswith('image'):
                            product_image_dict_listing.append(product_file.to_dict())
            
            if pos_settings is None:
                if product_image_dict_listing:
                    default_image_url = product_image_dict_listing[0].get('product_file_public_url')
                
                pos_settings        = {
                                    'representation_on_pos_option'  : 'image',
                                    #'represenation_sku'             : product.product_sku,
                                    #'represenation_name'            : product.product_name,
                                    'representation_settings'       : {
                                                                        'image_url': default_image_url,
                                                                        },
                                    }
             
        
        logger.debug('>>>>> pos_settings=%s', pos_settings)
        
        if is_empty(product_image_dict_listing):
            pos_settings['representation_on_pos_option'] = 'color'
        
        return render_template('merchant/product/item/product_setting_on_pos_content.html', 
                           page_title                                   = gettext('Representation on POS'),
                           product_key                                  = product_key,
                           product_name                                 = product.product_name,
                           product_sku                                  = product.product_sku,
                           product_image_dict_listing                   = product_image_dict_listing,
                           update_representation_on_pos_url             = url_for('product_setup_bp.product_setting_on_pos_post'),
                           pos_settings                                 = pos_settings,
                           )
        
    except:
        logger.error('Fail to show product represation on POS due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to show product represation on POS'), status_code=StatusCode.BAD_REQUEST)        

@product_setup_bp.route('/product-setting-on-pos', methods=['POST'])
@request_form
def product_setting_on_pos_post(request_form):
    logger.debug('--- submit product_setting_on_pos_post data ---')
    update_data = request_form
    
    logger.debug('update_data=%s', update_data)
    
    update_form = ProductSettingOnPOSForm(update_data)
    
    @model_transactional(desc='product_setting_on_pos_post')
    def __start_transaction(updating_product, updated_by):
        
        logger.debug('--product_representation_on_pos_post--')
        
        representation_on_pos_option    = update_form.representation_on_pos_option.data
        representation_settings         = None
        product_shortcut_key            = update_form.product_shortcut_key.data
        
        if representation_on_pos_option == 'image':
            representation_settings = {
                                        'image_url' : update_form.image_representation_url.data,
                                        }
        else:
            #representation_settings = json.loads(update_form.color_representation.data)
            representation_settings = update_form.color_representation.data
            
            if isinstance(representation_settings, str):
                representation_settings = json.loads(representation_settings)
            
            logger.debug('representation_settings=%s', representation_settings)
            logger.debug('representation_settings type=%s', type(representation_settings))
            
            if representation_settings.get('dark'):
                representation_settings['color'] = '#FFFFFF'
            else:
                representation_settings['color'] = '#000000'
            
        pos_settings = {
                        'representation_on_pos_option'  : representation_on_pos_option,
                        'represenation_sku'             : updating_product.product_sku,
                        'represenation_name'            : updating_product.product_name,
                        'representation_settings'       : representation_settings,
                        'product_shortcut_key'          : product_shortcut_key, 
                        }
        
        logger.debug('pos_settings=%s', pos_settings)
        
        updating_product.pos_settings = pos_settings
        
        Product.update(
                            updating_product,
                            updated_by              = updated_by
                            )
    
    try:
        if update_form.validate():
            
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            db_client = create_db_client(caller_info="product_representation_on_pos_post")
            with db_client.context():
                updating_product = Product.fetch(update_form.product_key.data)
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                __start_transaction(updating_product, merchant_user)
            
            
            return create_rest_message(gettext('Representation on POS have been updated'), 
                                           status_code  = StatusCode.OK
                                           )
            
                
        else:
            error_message = update_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update product due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

def get_product_listing(logged_in_merchant_user):
    
    product_listing = []
    
    merchant_acct           = logged_in_merchant_user.merchant_acct
    result                  = Product.list_by_merchant_acct(merchant_acct)
    
    for p in result:
        product_listing.append(p.to_dict())
    
    
    logger.debug('product_listing=%s', product_listing)
            
    return product_listing

def parse_product_to_option_json(product_listing):
    data_list = []
    
    
    for product in product_listing:
        pos_settings = product.get('pos_settings')
        logger.debug('pos_setting product name=%s', pos_settings)
        representation_settings = pos_settings.get('representation_settings')
        
        if representation_settings is not None:
            pos_representation = {
                                'option'            : pos_settings.get('representation_on_pos_option'),
                                'font_color'        : pos_settings.get('representation_settings').get('color'),
                                'background_color'  : pos_settings.get('representation_settings').get('value'),
                                'image_url'         : pos_settings.get('representation_settings').get('image_url'),
                                }
            data = {
                    'key'                   : product.get('key'),
                    'code'                  : product.get('product_sku'),
                    'label'                 : product.get('product_name'),
                    'pos_representation'    : pos_representation,
                }
           
        
            data_list.append(data)
            
        else:
            continue
        
        
        
    
    return data_list

def parse_product_group_by_category_to_option_json(product_listing):
    data_list = []
    
    
    for product in product_listing:
        pos_settings = product.get('pos_settings')
        logger.debug('pos_setting product name=%s', pos_settings)
        representation_settings = pos_settings.get('representation_settings')
        
        if representation_settings is not None:
            pos_representation = {
                                'option'            : pos_settings.get('representation_on_pos_option'),
                                'font_color'        : pos_settings.get('representation_settings').get('color'),
                                'background_color'  : pos_settings.get('representation_settings').get('value'),
                                'image_url'         : pos_settings.get('representation_settings').get('image_url'),
                                }
            data = {
                    'key'                   : product.get('key'),
                    'code'                  : product.get('product_sku'),
                    'label'                 : product.get('product_name'),
                    'group'                 : product.get('category_key'),
                    'pos_representation'    : pos_representation,
                }
           
        
            data_list.append(data)
            
        else:
            continue
        
        
        
    
    return data_list

def product_code_cache_key(f, *args, **kwargs):
    # Create a unique string based on function arguments
    key_data = { 'product_code'
        'args': args,
        'kwargs': kwargs
    }
    # Convert the key data to a JSON string
    key_string = json.dumps(key_data, sort_keys=True)
    # Generate an MD5 hash of the key string
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()

def product_code_group_by_category_cache_key(f, *args, **kwargs):
    # Create a unique string based on function arguments
    key_data = { 'product_code'
        'args': args,
        'kwargs': kwargs
    }
    # Convert the key data to a JSON string
    key_string = json.dumps(key_data, sort_keys=True)
    # Generate an MD5 hash of the key string
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()


@cache.memoize(timeout=300)
def get_product_code_label_json():
    logger.debug('reading product code from server')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="get_product_code_label_json")
    with db_client.context():
        merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        product_listing         = get_product_listing(merchant_user)
    
    return parse_product_to_option_json(product_listing)


#get_product_code_label_json.make_cache_key=product_code_cache_key


@cache.memoize(timeout=300)
def get_product_code_group_by_category_label_json():
    logger.debug('reading product code from server')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="get_product_code_label_json")
    with db_client.context():
        merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        product_listing         = get_product_listing(merchant_user)
    
    return parse_product_group_by_category_to_option_json(product_listing)


#get_product_code_group_by_category_label_json.make_cache_key=product_code_group_by_category_cache_key


@product_setup_bp.route('/time', methods=['GET'])
@cache.cached(timeout=300, )
def get_time():
    logger.debug('reading from server')
    
    return jsonify({
                    'time': datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S'),
                    'data': get_product_code_label_json()
                    })

@product_setup_bp.route('/list-code', methods=['GET'])
def list_product_code_label():
    logger.debug('---list_product_code_label--- ')
    
    product_in_json  = json.dumps(get_product_code_label_json(), sort_keys = True, separators = (',', ': '))
    resp = create_cached_response(product_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return resp

@product_setup_bp.route('/list-code-group-by-category', methods=['GET'])
def list_product_code_group_by_category_label():
    logger.debug('---list_product_code_group_by_category_label--- ')
    
    product_in_json  = json.dumps(get_product_code_group_by_category_label_json(), sort_keys = True, separators = (',', ': '))
    resp = create_cached_response(product_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return resp


@product_setup_bp.route('/setting-details-on-pos/<product_key>', methods=['GET'])
#@cache.cached(timeout=50)
def product_setting_details_on_pos(product_key):
    logger.debug('---product_setting_details_on_pos--- ')
    
    db_client = create_db_client(caller_info="product_setting_details_on_pos")
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    with db_client.context():
        product         = Product.fetch(product_key)
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        setting_details_for_pos_in_json  = json.dumps(product.setting_details_for_pos(merchant_acct), sort_keys = True, separators = (',', ': '))
    
    
    json_resp = create_cached_response(setting_details_for_pos_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return json_resp    
    