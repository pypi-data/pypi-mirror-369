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
from trexadmin.forms.merchant.product_forms import ProductCategorySetupForm,\
    ProductCategoryUpdateForm
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.product_models import ProductCategory, Product
from trexlib.utils.common.common_util import sort_list
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON, MINE_TYPE_JAVASCRIPT
from datetime import datetime
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct

product_maintenance_setup_bp = Blueprint('product_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/product')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')


@product_maintenance_setup_bp.route('/update-product-pos-setting/<merchant_acct_key>', methods=['get'])
def update_product_pos_setting(merchant_acct_key):
    db_client = create_db_client(caller_info="update_product_pos_setting")
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_acct_key)
        product_list = Product.list_by_merchant_acct(merchant_acct)
        for p in product_list:
            pos_settings = p.pos_settings
            new_pos_settings = {
                                    'representation_on_pos_option'  : pos_settings.get('representation_on_pos_option'),
                                    'representation_settings'       : pos_settings.get('representation_settings'),
                                    'product_shortcut_key'          : pos_settings.get('product_shortcut_key'),
                                    }
            p.pos_settings = new_pos_settings
            p.put()
            
    return 'Done on %s' % datetime.now(), 200        

@product_maintenance_setup_bp.route('/update-product-category-hierarchy/<merchant_acct_key>', methods=['get'])
def update_product_category_hierarchy(merchant_acct_key):
    db_client = create_db_client(caller_info="update_product_category_hierarchy")
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_acct_key)
        product_categories_list = ProductCategory.list_by_merchant_acct(merchant_acct)
        
        for pc in product_categories_list:
            logger.debug('checking %s and pc.parent_category_key=%s', pc.category_label, pc.parent_category_key)
            if is_not_empty(pc.parent_category_key):
                parent_category = None
                for p in product_categories_list:
                    if pc.parent_category_key == p.key_in_str:
                        parent_category = p
                        break
                
                if parent_category:
                    logger.debug('Found parent category, and going to update')
                    parent_category.add_child_category(pc)
                    
    
    return 'Done', 200

@product_maintenance_setup_bp.route('/update-product-category-product-items-reference/<merchant_acct_key>', methods=['get'])
def update_product_category_product_items_reference(merchant_acct_key):
    db_client = create_db_client(caller_info="update_product_category_product_items_reference")
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_acct_key)
        products_list = Product.list_by_merchant_acct(merchant_acct)
        
        if products_list:
            product_item_keys_by_category_key_dict = {}
            
            logger.debug('Total product count=%d', len(products_list))
            
            for product in products_list:
                category_key   = product.category_key 
                product_key     = product.key_in_str 
                if product_item_keys_by_category_key_dict.get(category_key):
                    product_item_keys_by_category_key_dict[category_key].append(product_key)
                else:
                    product_item_keys_by_category_key_dict[category_key] = [product_key]
            
            logger.debug('product_item_keys_by_category_key_dict=%s', product_item_keys_by_category_key_dict)
            
            #flush all product category product items reference first
            product_categories_list = ProductCategory.list_by_merchant_acct(merchant_acct)
            for pc in product_categories_list:
                pc.product_items            = []
                pc.child_category_keys      = []
                pc.put()
            
            for category_key, product_items_list in product_item_keys_by_category_key_dict.items():
                product_category = ProductCategory.fetch(category_key)
                product_category.product_items          = product_items_list
                
                product_category.put()
                
                if is_not_empty(product_category.parent_category_key):
                    logger.debug('product_category.parent_category_key=%s', product_category.parent_category_key)
                    parent_product_category = ProductCategory.fetch(product_category.parent_category_key)
                    
                    product_category.update_parent_category_with_product_items_reference(parent_product_category, product_category.product_items, merchant_acct)
                    
                    if parent_product_category is not None:
                        parent_product_category.add_child_category(product_category)
                        logger.debug('parent_product_category.child_category_keys=%s', parent_product_category.child_category_keys)
                    
                    
                    
    
    return create_rest_message('Updated', status_code=StatusCode.OK)
                        
        
        