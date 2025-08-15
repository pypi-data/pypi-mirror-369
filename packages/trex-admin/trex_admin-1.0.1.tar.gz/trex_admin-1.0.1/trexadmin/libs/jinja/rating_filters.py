'''
Created on 22 Jul 2025

@author: jacklok
'''

from trexadmin.libs.flask.utils.flask_helper import get_preferred_language
from trexadmin.controllers.system.system_route_helpers import get_restaurant_rating_type_json,\
    get_retail_rating_type_json
import logging
from trexadmin.libs.jinja.program_filters import map_label_by_code

#logger = logging.getLogger('debug')
logger = logging.getLogger('target_debug')


def restaurant_rating_type_label_filter(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_restaurant_rating_type_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''
    
def retail_rating_type_label_filter(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_retail_rating_type_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''    