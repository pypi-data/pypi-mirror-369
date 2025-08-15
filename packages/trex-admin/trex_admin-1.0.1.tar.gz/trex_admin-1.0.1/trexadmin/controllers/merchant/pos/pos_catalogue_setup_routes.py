'''
Created on 29 Dec 2021

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
from trexmodel.models.datastore.pos_models import POSCatalogue
from trexadmin.forms.merchant.pos_forms import POSCatalogueForm
from trexadmin.controllers.system.system_route_helpers import get_merchant_outlet_code

pos_catalogue_setup_bp = Blueprint('pos_catalogue_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/catalogue-setup')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

'''
Blueprint settings here
'''


@pos_catalogue_setup_bp.context_processor
def pos_catalogue_setup_settings_bp_inject_settings():
    
    return dict(
                
                )


@pos_catalogue_setup_bp.route('/', methods=['GET'])
@login_required
def pos_catalogue_listing(): 
    pos_catalogue_list           = []
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    db_client       = create_db_client(caller_info="pos_catalogue_listing")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result = POSCatalogue.list_by_merchant_acct(merchant_acct)
        
        for r in result:
            pos_catalogue_list.append(r.to_dict())
    
    return render_template('merchant/pos/pos_catalogue/pos_catalogue_listing.html',
                           page_title                       = gettext('POS Catalogue Setup'),
                           pos_catalogue_list               = pos_catalogue_list,
                           add_pos_catalogue_url            = url_for('pos_catalogue_setup_bp.add_pos_catalogue_details'),
                           reload_list_pos_catalogue_url    = url_for('pos_catalogue_setup_bp.pos_catalogue_listing_content'),
                           )
    
@pos_catalogue_setup_bp.route('/list-content', methods=['GET'])
@login_required
def pos_catalogue_listing_content(): 
    pos_catalogue_list           = []
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    db_client       = create_db_client(caller_info="pos_catalogue_listing")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result = POSCatalogue.list_by_merchant_acct(merchant_acct)
        
        for r in result:
            pos_catalogue_list.append(r.to_dict())
    
    return render_template('merchant/pos/pos_catalogue/pos_catalogue_listing_content.html',
                           page_title                   = gettext('POS Catalogue Setup'),
                           pos_catalogue_list           = pos_catalogue_list,
                           add_pos_catalogue_url        = url_for('pos_catalogue_setup_bp.add_pos_catalogue_details'),
                           )    
    
@pos_catalogue_setup_bp.route('/details', methods=['GET'])
@login_required
def add_pos_catalogue_details(): 
    
    outlet_list = get_merchant_outlet_code()
    
    return render_template('merchant/pos/pos_catalogue/pos_catalogue_details.html',
                           page_title                       = gettext('POS Catalogue Details'),
                           submit_pos_catalogue_url         = url_for('pos_catalogue_setup_bp.submit_pos_catalogue_details_post'),
                           
                           outlet_list                      = outlet_list,
                           pos_catalogue                    = None,
                           ) 
    
@pos_catalogue_setup_bp.route('/details/<pos_catalogue_key>', methods=['GET'])
@login_required
def edit_pos_catalogue_details(pos_catalogue_key): 
    
    outlet_list = get_merchant_outlet_code()
    
    db_client       = create_db_client(caller_info="edit_pos_catalogue_details")
    with db_client.context():
        pos_catalogue = POSCatalogue.fetch(pos_catalogue_key)
        
        if pos_catalogue:
            pos_catalogue = pos_catalogue.to_dict()
    
    return render_template('merchant/pos/pos_catalogue/pos_catalogue_details.html',
                           page_title                       = gettext('POS Catalogue Details'),
                           submit_pos_catalogue_url         = url_for('pos_catalogue_setup_bp.submit_pos_catalogue_details_post'),
                           outlet_list                      = outlet_list,
                           pos_catalogue                    = pos_catalogue,
                           )     
    
@pos_catalogue_setup_bp.route('/details', methods=['POST', 'PUT'])
@login_required
def submit_pos_catalogue_details_post(): 
    
    submit_pos_catalogue_data      = request.form
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    
    logger.debug('submit_pos_catalogue_data=%s', submit_pos_catalogue_data)
    
    pos_catalogue_form = POSCatalogueForm(submit_pos_catalogue_data)
    
    if pos_catalogue_form.validate():
        db_client       = create_db_client(caller_info="pos_catalogue_details_post")
        with db_client.context():
            
            pos_catalogue_key   = pos_catalogue_form.pos_catalogue_key.data
            catalogue_key       = pos_catalogue_form.catalogue_key.data
            assign_outlet       = pos_catalogue_form.assign_outlet.data
            
            logger.debug('pos_catalogue_key=%s', pos_catalogue_key)
            logger.debug('catalogue_key=%s', catalogue_key)
            logger.debug('assign_outlet=%s', assign_outlet)
            
            if is_not_empty(assign_outlet):
                assign_outlet = assign_outlet.split(',')
            
            if is_not_empty(pos_catalogue_key):
                POSCatalogue.update(pos_catalogue_key, catalogue_key, assigned_outlet_key_list=assign_outlet) 
                
                return create_rest_message(gettext('POS catalogue have been updated'), 
                                                status_code         = StatusCode.OK,
                                                )
            else:
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key')) 
                outlet_catalogue = POSCatalogue.create(catalogue_key, merchant_acct, assigned_outlet_key_list=assign_outlet)
                
                return create_rest_message(gettext('POS catalogue have been created'), 
                                                pos_catalogue_key   = outlet_catalogue.key_in_str,
                                                status_code         = StatusCode.OK,
                                                )
                
    else:
        error_message = pos_catalogue_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    

def publish_or_unpublish_pos_catalogue(pos_catalogue_key, to_publish):
    db_client       = create_db_client(caller_info="publish_or_unpublish_pos_catalogue")
    with db_client.context():
        pos_catalogue = POSCatalogue.fetch(pos_catalogue_key)
        if pos_catalogue:
            if to_publish:
                pos_catalogue.publish()
            else:
                pos_catalogue.unpublish()
     
@pos_catalogue_setup_bp.route('/publish/<pos_catalogue_key>', methods=['POST'])
@login_required
def publish_pos_catalogue_post(pos_catalogue_key):
    publish_or_unpublish_pos_catalogue(pos_catalogue_key, True)
    
    return create_rest_message(status_code         = StatusCode.ACCEPTED)
    

@pos_catalogue_setup_bp.route('/unpublish/<pos_catalogue_key>', methods=['POST'])
@login_required
def unpublish_pos_catalogue_post(pos_catalogue_key):
    publish_or_unpublish_pos_catalogue(pos_catalogue_key, False)     
    
    return create_rest_message(status_code         = StatusCode.ACCEPTED)                                          
    