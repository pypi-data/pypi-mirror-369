'''
Created on 25 Jan 2022

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexlib.utils.string_util import is_not_empty
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.pos_models import POSCatalogue,\
    DinningTableSetup, DinningOption
from trexadmin.forms.merchant.pos_forms import POSCatalogueForm,\
    DinningTableSetupForm
from trexadmin.controllers.system.system_route_helpers import get_merchant_outlet_code
from trexadmin.conf import DINNING_ORDER_APP_URL

dining_table_setup_bp = Blueprint('dining_table_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/dinning-table-setup')

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@dining_table_setup_bp.context_processor
def dining_table_source_setup_bp_setup_settings_bp_inject_settings():
    
    return dict(
                
                )


@dining_table_setup_bp.route('/', methods=['GET'])
@login_required
def dinning_table_setup_listing(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="dinning_table_setup_listing")
    dinning_table_setup_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = DinningTableSetup.list_by_merchant_acct(merchant_acct)
        for r in result:
            dinning_table_setup_list.append(r.to_dict())
    
    return render_template('merchant/pos/dinning_table/dinning_table_setup_listing.html',
                           page_title               = gettext('Dinning Table Setup'),
                           add_url                  = url_for('dining_table_setup_bp.add_dinning_table_setup'),
                           reload_url               = url_for('dining_table_setup_bp.dinning_table_setup_listing_content'),
                           dinning_table_setup_list = dinning_table_setup_list,
                           )
    
@dining_table_setup_bp.route('/listing-content', methods=['GET'])
@login_required
def dinning_table_setup_listing_content(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="dinning_table_setup_listing_content")
    dinning_table_setup_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = DinningTableSetup.list_by_merchant_acct(merchant_acct)
        for r in result:
            dinning_table_setup_list.append(r.to_dict())
    
    return render_template('merchant/pos/dinning_table/dinning_table_setup_listing_content.html',
                           dinning_table_setup_list = dinning_table_setup_list,
                           )
    
    
@dining_table_setup_bp.route('/add', methods=['GET'])
@login_required
def add_dinning_table_setup(): 
    
    outlet_list = get_merchant_outlet_code()
    
    return render_template('merchant/pos/dinning_table/dinning_table_setup.html',
                           page_title                       = gettext('Dinning Table Setup'),
                           submit_dinning_table_setup_url   = url_for('dining_table_setup_bp.add_dinning_table_setup_post'),
                           outlet_list                      = outlet_list,
                           ) 
    
@dining_table_setup_bp.route('/add', methods=['POST'])
@login_required
def add_dinning_table_setup_post():
    submit_dinning_table_data       = request.form
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    logger.debug('submit_dinning_table_data=%s', submit_dinning_table_data)
    
    dinning_table_setup_form        = DinningTableSetupForm(submit_dinning_table_data)
    if dinning_table_setup_form.validate():
        dinning_table_setup_key = dinning_table_setup_form.dinning_table_setup_key.data
        name                    = dinning_table_setup_form.name.data
        table_list              = dinning_table_setup_form.table_list.data
        assign_outlet           = dinning_table_setup_form.assign_outlet.data
        show_occupied           = dinning_table_setup_form.show_occupied.data
        
        if is_not_empty(assign_outlet):
            assign_outlet = assign_outlet.split(',')
        
        db_client       = create_db_client(caller_info="add_dinning_table_setup_post")
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if is_not_empty(dinning_table_setup_key):
                dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
                if dinning_table_setup:
                    DinningTableSetup.update(dinning_table_setup, name, table_list, assign_outlet, show_occupied=show_occupied)
            else:
                dinning_table_setup = DinningTableSetup.create(name, table_list, assign_outlet, merchant_acct, show_occupied=show_occupied)
            
        if dinning_table_setup:
            return create_rest_message(gettext('Dinning table setup have been created'), 
                                                dinning_table_setup_key = dinning_table_setup.key_in_str,
                                                status_code             = StatusCode.OK,
                                                )
            
    else:
        error_message = dinning_table_setup_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
    
@dining_table_setup_bp.route('/<dinning_table_setup_key>', methods=['GET'])
@login_required
def read_dinning_table_setup(dinning_table_setup_key):    
    
    
    outlet_list = get_merchant_outlet_code()
    
    db_client       = create_db_client(caller_info="read_dinning_table_setup")
    
    with db_client.context():
        dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
        if dinning_table_setup:
            dinning_table_setup = dinning_table_setup.to_dict()
        
    return render_template('merchant/pos/dinning_table/dinning_table_setup.html',
                       page_title                       = gettext('Dinning Table Setup'),
                       submit_dinning_table_setup_url   = url_for('dining_table_setup_bp.add_dinning_table_setup_post'),
                       dinning_table_setup              = dinning_table_setup,
                       outlet_list                      = outlet_list,
                       )
    
@dining_table_setup_bp.route('/<dinning_table_setup_key>', methods=['DELETE'])
@login_required
def delete_dinning_table_setup_post(dinning_table_setup_key):
    db_client       = create_db_client(caller_info="delete_dinning_table_setup_post")
    with db_client.context():
        dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
        if dinning_table_setup:
            DinningTableSetup.remove(dinning_table_setup)
    
    return create_rest_message(gettext('Dinning table setup have been removed'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )
    
@dining_table_setup_bp.route('/<dinning_table_setup_key>/publish', methods=['POST'])
@login_required
def publish_dinning_table_setup_post(dinning_table_setup_key):
    db_client       = create_db_client(caller_info="publish_dinning_table_setup_post")
    with db_client.context():
        dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
        if dinning_table_setup:
            dinning_table_setup.publish()
    
    return create_rest_message(gettext('Dinning table setup have been published'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )  
    
@dining_table_setup_bp.route('/<dinning_table_setup_key>/unpublish', methods=['POST'])
@login_required
def unpublish_dinning_table_setup_post(dinning_table_setup_key):
    db_client       = create_db_client(caller_info="unpublish_dinning_table_setup_post")
    with db_client.context():
        dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
        if dinning_table_setup:
            dinning_table_setup.unpublish()
    
    return create_rest_message(gettext('Dinning table setup have been published'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )
    
@dining_table_setup_bp.route('/<dinning_table_setup_key>/generate-order-qr-code', methods=['get'])
@login_required
def generate_dinning_table_order_qr_code(dinning_table_setup_key):
    outlet_list                 = get_merchant_outlet_code()
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="generate_dinning_table_order_qr_code")
    dinning_option_list         = []
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
        dinning_table_setup = dinning_table_setup.to_dict()
        
        _dinning_option_list = DinningOption.list_by_merchant_acct(merchant_acct)
        if _dinning_option_list:
            for d in _dinning_option_list:
                if d.is_self_order_input:
                    dinning_option_list.append(d.to_dict())
            
    return render_template('merchant/pos/dinning_table/dinning_table_order_qr_code_generation.html',
                       dinning_table_setup              = dinning_table_setup,
                       outlet_list                      = outlet_list,
                       dinning_option_list              = dinning_option_list,
                       )
    
@dining_table_setup_bp.route('/<dinning_table_setup_key>/dinning-option/<dinning_option_key>/generate-order-qr-code/<outlet_key>', methods=['get'])
@login_required
def dinning_table_order_qr_code_listing(dinning_table_setup_key, dinning_option_key, outlet_key):
    db_client       = create_db_client(caller_info="dinning_table_order_qr_code_listing")
    
    with db_client.context():
        dinning_table_setup = DinningTableSetup.fetch(dinning_table_setup_key)
        weblink_details_listing = dinning_table_setup.generate_weblink_details_list(outlet_key, dinning_option_key, DINNING_ORDER_APP_URL)
            
    return render_template('merchant/pos/dinning_table/dinning_table_order_qr_code_listing.html',
                       weblink_details_listing      = weblink_details_listing,
                       show_full                    = True,
                       
                       )    
                

