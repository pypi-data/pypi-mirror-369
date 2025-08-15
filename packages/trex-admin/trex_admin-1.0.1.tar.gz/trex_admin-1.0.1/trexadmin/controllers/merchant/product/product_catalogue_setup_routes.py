'''
Created on 13 Dec 2021

@author: jacklok
'''

from flask import Blueprint, request, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
import logging
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexadmin.controllers.merchant.product.product_category_setup_routes import get_product_category_structure_code_label_json,\
    render_to_select_option_html
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexadmin.forms.merchant.product_forms import ProductCatalogueDetailsForm
from trexmodel.models.datastore.product_models import ProductCatalogue
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
import json
from trexweb.utils.common.http_response_util import create_cached_response,\
    MINE_TYPE_JSON

product_catalogue_setup_bp = Blueprint('product_catalogue_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/product/catalogue')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@product_catalogue_setup_bp.route('/', methods=['get'])
def product_catalogue_listing():
    product_catalogues_list = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="product_catalogue_listing")
    
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result              = ProductCatalogue.list_by_merchant_acct(merchant_acct)
        
        if result:
            for c in result:
                product_catalogues_list.append(c.to_dict())
                
        
    
    return render_template('merchant/product/catalogue/product_catalogue_listing.html', 
                           page_title                           = gettext('Catalogue Listing'),
                           add_product_catalogue_url            = url_for('product_catalogue_setup_bp.create_product_catalogue'),
                           reload_list_product_catalogue_url    = url_for('product_catalogue_setup_bp.product_catalogue_listing_content'),
                           product_catalogues_list              = product_catalogues_list,
                           product_catalogue                    = None,
                           )
    
@product_catalogue_setup_bp.route('/details', methods=['get'])
def create_product_catalogue():
    
    product_category_structure_option    = get_product_category_structure_code_label_json()
    product_category_select_option_html  = render_to_select_option_html(product_category_structure_option, show_product_item_in_data=True)
    
    logger.debug('product_category_structure_option=%s', product_category_structure_option)
    
    return render_template('merchant/product/catalogue/product_catalogue_details.html', 
                           page_title                           = gettext('Catalogue Details'),
                           post_url                             = url_for('product_catalogue_setup_bp.product_catalogue_post'),
                           product_catalogue_desc               = '',
                           product_category_select_option_html  = product_category_select_option_html,
                           )
    

@product_catalogue_setup_bp.route('/details/<catalogue_key>', methods=['get'])
def edit_product_catalogue(catalogue_key):
    
    db_client = create_db_client(caller_info="edit_product_catalogue")
    
    with db_client.context():
        product_catalogue = ProductCatalogue.fetch(catalogue_key)
        if product_catalogue:
            product_catalogue = product_catalogue.to_dict()
    
    product_category_structure_option    = get_product_category_structure_code_label_json()
    product_category_select_option_html  = render_to_select_option_html(product_category_structure_option, show_product_item_in_data=True, selected_category_code=product_catalogue.get('category_code'))
    
    return render_template('merchant/product/catalogue/product_catalogue_details.html', 
                           page_title                           = gettext('Catalogue Details'),
                           post_url                             = url_for('product_catalogue_setup_bp.product_catalogue_post'),
                           product_catalogue                    = product_catalogue,
                           product_catalogue_desc               = product_catalogue.get('desc'),
                           product_category_select_option_html  = product_category_select_option_html,
                           )

@product_catalogue_setup_bp.route('/view/<catalogue_key>', methods=['get'])
def view_product_catalogue(catalogue_key):
    db_client = create_db_client(caller_info="edit_product_catalogue")
    
    with db_client.context():
        product_catalogue = ProductCatalogue.fetch(catalogue_key)
        if product_catalogue:
            product_catalogue = product_catalogue.to_dict()
    
    product_category_structure_option    = get_product_category_structure_code_label_json()
    product_category_select_option_html  = render_to_select_option_html(product_category_structure_option, 
                                                                        show_item_count=False, 
                                                                        show_product_item_in_data=True,
                                                                        menu_settings=product_catalogue.get('menu_settings')
                                                                        )
    
    return render_template('merchant/product/catalogue/product_catalogue_preview.html', 
                           product_catalogue                    = product_catalogue,
                           product_category_select_option_html  = product_category_select_option_html,
                           )

@product_catalogue_setup_bp.route('/details', methods=['POST','PUT'])
def product_catalogue_post():
    
    product_catalogue_data           = request.form
    product_catalogue_form           = ProductCatalogueDetailsForm(product_catalogue_data)
    
    logger.debug('product_catalogue_data=%s', product_catalogue_data)
    
    try:
        if product_catalogue_form.validate():
            
            is_new_setup            = False
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            
            catalogue_key           = product_catalogue_form.catalogue_key.data
            catalogue_name          = product_catalogue_form.catalogue_name.data
            desc                    = product_catalogue_form.desc.data
            menu_settings           = product_catalogue_form.menu_settings.data
            
            
            
            
            db_client = create_db_client(caller_info="product_catalogue_post")
            
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                
                if is_not_empty(catalogue_key):
                    logger.debug('going to update product catalogue')
                    
                    product_catalogue    = ProductCatalogue.fetch(catalogue_key)
                    
                    if product_catalogue:
                    
                        ProductCatalogue.update(product_catalogue, 
                                                catalogue_name,
                                                menu_settings       = menu_settings,
                                                desc                = desc,
                                                modified_by         = merchant_user,
                                               )
                    
                    
                else:
                    logger.debug('going to create catalogue')
                    
                    product_catalogue    = ProductCatalogue.create( 
                                                                    catalogue_name,
                                                                    menu_settings       = menu_settings,
                                                                    merchant_acct       = merchant_acct,
                                                                    desc                = desc,
                                                                    created_by          = merchant_user,
                                                                   )
                
                    is_new_setup = True
            
            logger.debug('is_new_setup=%s', is_new_setup)
            
            if product_catalogue is None:
                logger.debug('product_catalogue is None')
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                if is_new_setup:
                    
                    return create_rest_message(status_code  = StatusCode.OK, 
                                           catalogue_key = product_catalogue.key_in_str,
                                           )
                else:
                    return create_rest_message(status_code=StatusCode.OK)
            
                    
        else:
            error_message = product_catalogue_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to setup catalogue due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
    
@product_catalogue_setup_bp.route('/listing-content', methods=['get'])
def product_catalogue_listing_content():
    
    product_catalogues_list = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="catalogue_listing")
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result              = ProductCatalogue.list_by_merchant_acct(merchant_acct)
        
        if result:
            for c in result:
                product_catalogues_list.append(c.to_dict())
    
    return render_template('merchant/product/catalogue/product_catalogue_listing_content.html', 
                           add_product_catalogue_url            = url_for('product_catalogue_setup_bp.create_product_catalogue'),
                           reload_list_product_catalogue_url    = url_for('product_catalogue_setup_bp.product_catalogue_listing_content'),
                           product_catalogues_list              = product_catalogues_list,
                           )        


@product_catalogue_setup_bp.route('/publish/<catalogue_key>', methods=['POST'])
def publish_product_catalogue_post(catalogue_key):
    
    if is_not_empty(catalogue_key):
        db_client = create_db_client(caller_info="publish_product_catalogue_post")
        
        with db_client.context():
            product_catalogue = ProductCatalogue.fetch(catalogue_key)
            product_catalogue.publish()
            
        
        return create_rest_message(gettext('Catalogue have been published'), status_code=StatusCode.ACCEPTED)
    else:
        return create_rest_message(gettext('Invalid catalogue data'), status_code=StatusCode.BAD_REQUEST)   
    
@product_catalogue_setup_bp.route('/unpublish/<catalogue_key>', methods=['POST'])
def unpublish_product_catalogue_post(catalogue_key):
    
    if is_not_empty(catalogue_key):
        db_client = create_db_client(caller_info="unpublish_product_catalogue_post")
        
        with db_client.context():
            product_catalogue = ProductCatalogue.fetch(catalogue_key)
            product_catalogue.unpublish()
            
        
        return create_rest_message(gettext('Catalogue have been unpublished'), status_code=StatusCode.ACCEPTED)
    else:
        return create_rest_message(gettext('Invalid catalogue data'), status_code=StatusCode.BAD_REQUEST)    


@product_catalogue_setup_bp.route('/<catalogue_key>', methods=['get'])
def product_catalogue_setting_details_on_pos(catalogue_key):
    db_client                   = create_db_client(caller_info="get_product_catalogue")
    product_catalogue_in_json   = {}
    with db_client.context():
        product_catalogue = ProductCatalogue.fetch(catalogue_key)
        if product_catalogue:
            product_catalogue_in_json  = json.dumps(product_catalogue.setting_details_for_pos, sort_keys = True, separators = (',', ': '))
    
    json_resp = create_cached_response(product_catalogue_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return json_resp

def get_published_product_catalogue_listing(merchant_acct):
    
    catalogue_listing = []
    
    result          = ProductCatalogue.list_published_by_merchant_acct(merchant_acct) 
    
    for c in result:
        catalogue_listing.append(c.to_dict())
    
    
    return catalogue_listing

def parse_to_option_json(catalogue_listing):
    data_list = []
    
    for catalogue in catalogue_listing:
        data = {
                    'code'                  : catalogue.get('key'),
                    'label'                 : catalogue.get('catalogue_name'),
                    
                }
        data_list.append(data)
    
    return data_list

def get_product_catalogue_code_label_json():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client               = create_db_client(caller_info="get_product_catalogue_code_label_json")
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        category_list       = get_published_product_catalogue_listing(merchant_acct)
    
    return parse_to_option_json(category_list)


@product_catalogue_setup_bp.route('/list-catalogue-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_catalogue_code_label_in_structure():
    logger.debug('---list_catalogue_code_label_in_structure--- ')
    
    category_tree_structure_in_json  = json.dumps(get_product_catalogue_code_label_json(), sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(category_tree_structure_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  )
    
    return resp
    