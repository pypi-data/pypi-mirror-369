'''
Created on 21 Mar 2022

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
from trexmodel.models.datastore.pos_models import ServiceChargeSetup,\
    DinningOption
from trexadmin.forms.merchant.pos_forms import ServiceChargeSetupForm
from trexadmin.controllers.system.system_route_helpers import get_merchant_outlet_code

service_charge_setup_bp = Blueprint('service_charge_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/service-charge-setup')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

@service_charge_setup_bp.context_processor
def service_charge_setup_bp_inject_settings():
    
    return dict(
                
                )


@service_charge_setup_bp.route('/', methods=['GET'])
@login_required
def service_charge_setup_listing(): 
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    db_client                       = create_db_client(caller_info="service_charge_setup_listing")
    service_charge_setup_list       = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = ServiceChargeSetup.list_by_merchant_acct(merchant_acct)
        for r in result:
            service_charge_setup_list.append(r.to_dict())
    
    return render_template('merchant/pos/service_charge/service_charge_setup_listing.html',
                           page_title                   = gettext('Additional Charge Setup'),
                           add_url                      = url_for('service_charge_setup_bp.add_service_charge_setup'),
                           reload_url                   = url_for('service_charge_setup_bp.service_charge_setup_listing_content'),
                           service_charge_setup_list    = service_charge_setup_list,
                           )
    
@service_charge_setup_bp.route('/listing-content', methods=['GET'])
@login_required
def service_charge_setup_listing_content(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="service_charge_setup_listing_content")
    service_charge_setup_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = ServiceChargeSetup.list_by_merchant_acct(merchant_acct)
        for r in result:
            service_charge_setup_list.append(r.to_dict())
    
    return render_template('merchant/pos/service_charge/service_charge_setup_listing_content.html',
                           service_charge_setup_list = service_charge_setup_list,
                           )
    
    
@service_charge_setup_bp.route('/add', methods=['GET'])
@login_required
def add_service_charge_setup(): 
    
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="add_service_charge_setup")
    dinning_option_list         = []
    outlet_list                 = get_merchant_outlet_code()
    with db_client.context():
        merchant_acct       = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
        _dinning_option_list = DinningOption.list_by_merchant_acct(merchant_acct)
        if _dinning_option_list:
            for d in _dinning_option_list:
                dinning_option_list.append(d.to_dict())
    
    return render_template('merchant/pos/service_charge/service_charge_setup.html',
                           page_title                           = gettext('Service Charge Setup'),
                           submit_service_charge_setup_url      = url_for('service_charge_setup_bp.add_service_charge_setup_post'),
                           dinning_option_list                  = dinning_option_list,
                           outlet_list                          = outlet_list,
                           ) 
    
@service_charge_setup_bp.route('/add', methods=['POST'])
@login_required
def add_service_charge_setup_post():
    submit_service_charge_data       = request.form
    logged_in_merchant_user          = get_loggedin_merchant_user_account()
    
    logger.debug('submit_service_charge_data=%s', submit_service_charge_data)
    
    service_charge_setup_form        = ServiceChargeSetupForm(submit_service_charge_data)
    if service_charge_setup_form.validate():
        service_charge_setup_key        = service_charge_setup_form.service_charge_setup_key.data
        charge_name                     = service_charge_setup_form.charge_name.data
        charge_label                    = service_charge_setup_form.charge_label.data
        charge_pct_amount               = service_charge_setup_form.charge_pct_amount.data
        applyed_dinning_option          = service_charge_setup_form.applyed_dinning_option.data
        assign_outlet                   = service_charge_setup_form.assign_outlet.data
        
        if is_not_empty(assign_outlet):
            assign_outlet = assign_outlet.split(',')
            
        if is_not_empty(applyed_dinning_option):
            applyed_dinning_option = applyed_dinning_option.split(',')    
        
        db_client       = create_db_client(caller_info="add_service_charge_setup_post")
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if is_not_empty(service_charge_setup_key):
                service_charge_setup = ServiceChargeSetup.fetch(service_charge_setup_key)
                if service_charge_setup:
                    ServiceChargeSetup.update(service_charge_setup, charge_name, charge_label, charge_pct_amount, applyed_dinning_option, assign_outlet)
            else:
                service_charge_setup = ServiceChargeSetup.create(charge_name, charge_label, charge_pct_amount, applyed_dinning_option, assign_outlet, merchant_acct)
            
        if service_charge_setup:
            return create_rest_message(gettext('Service Charge setup have been created'), 
                                                service_charge_setup_key    = service_charge_setup.key_in_str,
                                                status_code                 = StatusCode.OK,
                                                )
            
    else:
        error_message = service_charge_setup_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
    
@service_charge_setup_bp.route('/<service_charge_setup_key>', methods=['GET'])
@login_required
def read_service_charge_setup(service_charge_setup_key):    
    
    
    outlet_list             = get_merchant_outlet_code()
    dinning_option_list     = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client               = create_db_client(caller_info="read_service_charge_setup")
    
    with db_client.context():
        merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        service_charge_setup    = ServiceChargeSetup.fetch(service_charge_setup_key)
        if service_charge_setup:
            service_charge_setup = service_charge_setup.to_dict()
            
        _dinning_option_list = DinningOption.list_by_merchant_acct(merchant_acct)
        if _dinning_option_list:
            for d in _dinning_option_list:
                dinning_option_list.append(d.to_dict())
        
    return render_template('merchant/pos/service_charge/service_charge_setup.html',
                       page_title                           = gettext('Service Charge Setup'),
                       submit_service_charge_setup_url      = url_for('service_charge_setup_bp.add_service_charge_setup_post'),
                       service_charge_setup                 = service_charge_setup,
                       outlet_list                          = outlet_list,
                       dinning_option_list                  = dinning_option_list,    
                       )
    
@service_charge_setup_bp.route('/<service_charge_setup_key>', methods=['DELETE'])
@login_required
def delete_service_charge_setup_post(service_charge_setup_key):
    db_client       = create_db_client(caller_info="delete_service_charge_setup_post")
    with db_client.context():
        service_charge_setup = ServiceChargeSetup.fetch(service_charge_setup_key)
        if service_charge_setup:
            ServiceTaxSetup.remove(service_charge_setup)
    
    return create_rest_message(gettext('Service Charge setup have been removed'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )
    
@service_charge_setup_bp.route('/<service_charge_setup_key>/publish', methods=['POST'])
@login_required
def publish_service_charge_setup_post(service_charge_setup_key):
    db_client       = create_db_client(caller_info="publish_service_charge_setup_post")
    with db_client.context():
        service_charge_setup = ServiceChargeSetup.fetch(service_charge_setup_key)
        if service_charge_setup:
            service_charge_setup.publish()
    
    return create_rest_message(gettext('Service Charge setup have been published'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )  
    
@service_charge_setup_bp.route('/<service_charge_setup_key>/unpublish', methods=['POST'])
@login_required
def unpublish_service_charge_setup_post(service_charge_setup_key):
    db_client       = create_db_client(caller_info="unpublish_service_charge_setup_post")
    with db_client.context():
        service_charge_setup = ServiceChargeSetup.fetch(service_charge_setup_key)
        if service_charge_setup:
            service_charge_setup.unpublish()
    
    return create_rest_message(gettext('Service Charge setup have been published'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                ) 