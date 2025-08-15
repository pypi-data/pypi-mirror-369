'''
Created on 8 Mar 2022

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
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    ServiceTaxSetup
from trexadmin.controllers.system.system_route_helpers import get_merchant_outlet_code
from trexadmin.forms.merchant.merchant_forms import ServiceTaxSetupForm

service_tax_setup_bp = Blueprint('service_tax_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/service-tax-setup')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

@service_tax_setup_bp.context_processor
def service_tax_setup_bp_inject_settings():
    
    return dict(
                
                )


@service_tax_setup_bp.route('/', methods=['GET'])
@login_required
def service_tax_setup_listing(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="service_tax_setup_listing")
    service_tax_setup_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = ServiceTaxSetup.list_by_merchant_acct(merchant_acct)
        for r in result:
            service_tax_setup_list.append(r.to_dict())
    
    return render_template('merchant/settings/service_tax_setup/service_tax_setup_listing.html',
                           page_title               = gettext('Taxes Setup'),
                           add_url                  = url_for('service_tax_setup_bp.add_service_tax_setup'),
                           reload_url               = url_for('service_tax_setup_bp.service_tax_setup_listing_content'),
                           service_tax_setup_list = service_tax_setup_list,
                           )
    
@service_tax_setup_bp.route('/listing-content', methods=['GET'])
@login_required
def service_tax_setup_listing_content(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="service_tax_setup_listing_content")
    service_tax_setup_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = ServiceTaxSetup.list_by_merchant_acct(merchant_acct)
        for r in result:
            service_tax_setup_list.append(r.to_dict())
    
    return render_template('merchant/settings/service_tax_setup/service_tax_setup_listing_content.html',
                           service_tax_setup_list = service_tax_setup_list,
                           )
    
    
@service_tax_setup_bp.route('/add', methods=['GET'])
@login_required
def add_service_tax_setup(): 
    
    outlet_list = get_merchant_outlet_code()
    
    return render_template('merchant/settings/service_tax_setup/service_tax_setup.html',
                           page_title                       = gettext('Taxes Setup'),
                           submit_service_tax_setup_url   = url_for('service_tax_setup_bp.add_service_tax_setup_post'),
                           outlet_list                      = outlet_list,
                           ) 
    
@service_tax_setup_bp.route('/add', methods=['POST'])
@login_required
def add_service_tax_setup_post():
    submit_service_tax_data       = request.form
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    logger.debug('submit_service_tax_data=%s', submit_service_tax_data)
    
    service_tax_setup_form        = ServiceTaxSetupForm(submit_service_tax_data)
    if service_tax_setup_form.validate():
        service_tax_setup_key   = service_tax_setup_form.service_tax_setup_key.data
        tax_reg_id              = service_tax_setup_form.tax_reg_id.data
        tax_name                = service_tax_setup_form.tax_name.data
        tax_label               = service_tax_setup_form.tax_label.data
        tax_apply_type          = service_tax_setup_form.tax_apply_type.data
        tax_pct_amount          = service_tax_setup_form.tax_pct_amount.data
        assign_outlet           = service_tax_setup_form.assign_outlet.data
        
        if is_not_empty(assign_outlet):
            assign_outlet = assign_outlet.split(',')
        
        db_client       = create_db_client(caller_info="add_service_tax_setup_post")
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if is_not_empty(service_tax_setup_key):
                service_tax_setup = ServiceTaxSetup.fetch(service_tax_setup_key)
                if service_tax_setup:
                    ServiceTaxSetup.update(service_tax_setup, tax_reg_id, tax_name, tax_label, tax_apply_type, tax_pct_amount, assign_outlet)
            else:
                service_tax_setup = ServiceTaxSetup.create(tax_reg_id, tax_name, tax_label, tax_apply_type, tax_pct_amount, assign_outlet, merchant_acct)
            
        if service_tax_setup:
            return create_rest_message(gettext('Tax setup have been created'), 
                                                service_tax_setup_key   = service_tax_setup.key_in_str,
                                                status_code             = StatusCode.OK,
                                                )
            
    else:
        error_message = service_tax_setup_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
    
@service_tax_setup_bp.route('/<service_tax_setup_key>', methods=['GET'])
@login_required
def read_service_tax_setup(service_tax_setup_key):    
    
    
    outlet_list = get_merchant_outlet_code()
    
    db_client       = create_db_client(caller_info="read_service_tax_setup")
    
    with db_client.context():
        service_tax_setup = ServiceTaxSetup.fetch(service_tax_setup_key)
        if service_tax_setup:
            service_tax_setup = service_tax_setup.to_dict()
        
    return render_template('merchant/settings/service_tax_setup/service_tax_setup.html',
                       page_title                       = gettext('Tax Setup'),
                       submit_service_tax_setup_url   = url_for('service_tax_setup_bp.add_service_tax_setup_post'),
                       service_tax_setup              = service_tax_setup,
                       outlet_list                      = outlet_list,
                       )
    
@service_tax_setup_bp.route('/<service_tax_setup_key>', methods=['DELETE'])
@login_required
def delete_service_tax_setup_post(service_tax_setup_key):
    db_client       = create_db_client(caller_info="delete_service_tax_setup_post")
    with db_client.context():
        service_tax_setup = ServiceTaxSetup.fetch(service_tax_setup_key)
        if service_tax_setup:
            ServiceTaxSetup.remove(service_tax_setup)
    
    return create_rest_message(gettext('Tax setup have been removed'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )
    
@service_tax_setup_bp.route('/<service_tax_setup_key>/publish', methods=['POST'])
@login_required
def publish_service_tax_setup_post(service_tax_setup_key):
    db_client       = create_db_client(caller_info="publish_service_tax_setup_post")
    with db_client.context():
        service_tax_setup = ServiceTaxSetup.fetch(service_tax_setup_key)
        if service_tax_setup:
            service_tax_setup.publish()
    
    return create_rest_message(gettext('Tax setup have been published'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )  
    
@service_tax_setup_bp.route('/<service_tax_setup_key>/unpublish', methods=['POST'])
@login_required
def unpublish_service_tax_setup_post(service_tax_setup_key):
    db_client       = create_db_client(caller_info="unpublish_service_tax_setup_post")
    with db_client.context():
        service_tax_setup = ServiceTaxSetup.fetch(service_tax_setup_key)
        if service_tax_setup:
            service_tax_setup.unpublish()
    
    return create_rest_message(gettext('Tax setup have been published'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                ) 