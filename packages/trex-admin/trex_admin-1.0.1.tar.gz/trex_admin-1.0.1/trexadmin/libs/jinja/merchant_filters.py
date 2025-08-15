'''
Created on 25 Oct 2023

@author: jacklok
'''
from trexadmin.libs.flask.utils.flask_helper import get_preferred_language
from trexadmin.controllers.system.system_route_helpers import get_loyalty_package_label,\
    get_product_code_label, get_merchant_news_status_json, map_label_by_code
from trexlib.utils.string_util import is_not_empty
from flask_babel import gettext
import logging

logger = logging.getLogger('debug')


def product_package_filter(product_package):
    product_label_list = []
    
    logger.debug('product_package_filter debug: product_package=%s', product_package)
    
    if is_not_empty(product_package):
        preferred_language  = get_preferred_language()
        
        for p in product_package:
            logger.debug('product_package_filter debug: p=%s', p)
            product_label = get_product_code_label(p, preferred_language)
            
            if product_label:
                product_label_list.append(product_label)
        
    return ", ".join(product_label_list)

def loyalty_package_filter(account_package):
    if is_not_empty(account_package):
        preferred_language  = get_preferred_language()
        loyalty_package_label = get_loyalty_package_label(account_package, preferred_language)
        
        return loyalty_package_label
            
             
    
    return gettext('Unknown')

def merchant_news_completed_status_label(completed_status_code):
    if completed_status_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_merchant_news_status_json(preferred_language)
        return map_label_by_code(code_label_json, completed_status_code)
    else:
        return ''    
