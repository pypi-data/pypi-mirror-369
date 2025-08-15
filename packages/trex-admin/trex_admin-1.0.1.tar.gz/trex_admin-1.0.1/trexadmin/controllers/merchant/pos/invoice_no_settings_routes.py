'''
Created on 16 Feb 2022

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.pos_models import DinningOption,\
    InvoiceNoGeneration
from trexadmin.forms.merchant.pos_forms import DinningOptionForm

invoice_no_settings_bp = Blueprint('invoice_no_settings_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/invoice-no-settings')

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@invoice_no_settings_bp.context_processor
def invoice_no_settings_inject_settings():
    
    return dict(
                
                )


@invoice_no_settings_bp.route('/', methods=['GET'])
@login_required
def invoice_no_settings():
    return __invoice_no_generator_content('merchant/pos/invoice_no_settings/manage_invoice_no_settings.html')
        
    
@invoice_no_settings_bp.route('/list-content', methods=['GET'])    
@login_required
def invoice_no_generator_listing_content():
    return __invoice_no_generator_content('merchant/pos/invoice_no_settings/invoice_no_generator_listing_content.html')

def __invoice_no_generator_content(target_template): 
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    db_client                       = create_db_client(caller_info="__invoice_no_generator_content")
    invoice_no_generator_list       = []
    
    with db_client.context():
        merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        invoice_no_generation   = InvoiceNoGeneration.getByMerchantAcct(merchant_acct)
        if invoice_no_generation:
            invoice_no_generator_list = invoice_no_generation.generators_list
            #pass
            
        
    logger.debug('invoice_no_generator_list=%s', invoice_no_generator_list)
    
    return render_template(target_template,
                           page_title                                       = gettext('Invoice No Setup'),
                           invoice_no_generator_list                        = invoice_no_generator_list,
                           invoice_no_generator_listing_content_reload_url  = url_for('invoice_no_settings_bp.invoice_no_generator_listing_content'),
                           update_invoice_no_generator_url                  = url_for('invoice_no_settings_bp.update_invoice_no_generator_post'),
                           )
    
@invoice_no_settings_bp.route('/add', methods=['POST'])
@login_required
def update_invoice_no_generator_post():
    invoice_no_generation_data          = request.form
    logged_in_merchant_user             = get_loggedin_merchant_user_account()
    generators_list                     = invoice_no_generation_data.getlist('generators_list[]')
    db_client                           = create_db_client(caller_info="add_invoice_no_generator_post")
    
    logger.debug('invoice_no_generation_data=%s', invoice_no_generation_data);
    logger.debug('generators_list=%s', generators_list);
    
    with db_client.context():
        merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        invoice_no_generation   = InvoiceNoGeneration.create(generators_list, merchant_acct)
            
    if invoice_no_generation:
        return create_rest_message(gettext('Invoice No generator have been updated'), 
                                            status_code                 = StatusCode.OK,
                                            )
    else:
        return create_rest_message(gettext('Failed to update invoice no generator'), status_code=StatusCode.BAD_REQUEST)
    
    
    
    
