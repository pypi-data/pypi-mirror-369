'''
Created on 25 Oct 2023

@author: jacklok
'''
from trexlib.utils.string_util import is_not_empty

def is_product_allow(account_plan, product_code):
    product_package = account_plan.get('product_package')
    if is_not_empty(product_package):
        if product_code in product_package:
            return True
    
    return False

def is_feature_allow(account_plan, product_code, feature_group, feature_code):
    product_package = account_plan.get('product_package')
    if is_not_empty(product_package):
        if product_code in product_package:
            product_feature_map = account_plan.get('%s_package_feature'%product_code)
            if is_not_empty(product_feature_map):
                feature_codes_list = product_feature_map.get(feature_group)
                if feature_code in feature_codes_list:
                    return True 
    
    return False
    
