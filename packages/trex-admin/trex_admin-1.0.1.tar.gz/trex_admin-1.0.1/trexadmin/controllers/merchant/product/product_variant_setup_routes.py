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
from trexmodel.models.datastore.product_models import ProductCategory
from trexlib.utils.common.common_util import sort_list
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON, MINE_TYPE_JAVASCRIPT

from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct

product_variant_setup_bp = Blueprint('product_variant_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/product/variant')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')