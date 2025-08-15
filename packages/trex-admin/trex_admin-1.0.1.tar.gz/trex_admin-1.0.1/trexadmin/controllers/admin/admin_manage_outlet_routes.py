'''
Created on 8 Dec 2020

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for, current_app
from trexadmin.forms.merchant.merchant_forms import AddMerchantOutletForm
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexlib.utils.log_util import get_tracelog
from trexadmin.controllers.merchant.settings.merchant_manage_outlet_routes import add_outlet_post_function, update_outlet_post_function, delete_outlet_function
import logging
from flask_babel import gettext
from trexlib.utils.string_util import is_not_empty

admin_manage_outlet_bp = Blueprint('admin_manage_outlet_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/manage-merchant-outlet')


logger = logging.getLogger('application:manage_outlet_bp')

database_config = {}


@admin_manage_outlet_bp.route('/list-outlet', methods=['GET'])
@login_required
def list_outlet(): 
    merchant_acct_key = request.args.get('merchant_acct_key')
    db_client = create_db_client(caller_info="list_outlet")
    with db_client.context():
        merchant_acct   = MerchantAcct.fetch(merchant_acct_key)
        __outlet_list     = Outlet.list_by_merchant_acct(merchant_acct)
    
    outlet_list = []
    if __outlet_list:
        for o in __outlet_list:
            outlet_list.append(o.to_dict())
    
    return render_template('admin/manage_merchant/merchant_outlet_listing.html',
                           page_title                       = gettext('Outlet Listing'),
                           merchant_acct_key                = merchant_acct_key,
                           outlet_list                      = outlet_list or [],
                           add_outlet_url                   = url_for('admin_manage_outlet_bp.add_outlet', merchant_acct_key=merchant_acct_key),
                           edit_merchant_outlet_url_path    = 'admin_manage_outlet_bp.read_outlet',
                           delete_merchant_outlet_url_path  = 'admin_manage_outlet_bp.delete_outlet',
                           )
    
@admin_manage_outlet_bp.route('/add-outlet/<merchant_acct_key>', methods=['GET'])
@login_required
def add_outlet(merchant_acct_key): 
    
    return render_template('merchant/settings/manage_outlet/manage_outlet_details.html',
                           page_title           = 'Outlet Details',
                           merchant_acct_key    = merchant_acct_key,
                           merchant_outlet      = None,
                           post_url             = url_for('admin_manage_outlet_bp.add_outlet_post', merchant_acct_key=merchant_acct_key),
                           )

@admin_manage_outlet_bp.route('/add-outlet/<merchant_acct_key>', methods=['POST'])
@login_required_rest
def add_outlet_post(merchant_acct_key): 
    current_app.logger.debug('--- submit add_outlet_post ---')
    add_outlet_data = request.form
    
    current_app.logger.debug('add_outlet_data=%s', add_outlet_data)
    
    add_outlet_form = AddMerchantOutletForm(add_outlet_data)
    
    merchant_acct_key   = add_outlet_form.merchant_acct_key.data
    
    return add_outlet_post_function(merchant_acct_key, post_url=url_for('admin_manage_outlet_bp.update_outlet_post')) 
    
@admin_manage_outlet_bp.route('/outlet/<outlet_key>', methods=['GET'])
@login_required
def read_outlet(outlet_key): 
    logger.debug('---read_outlet---')
    
    logger.debug('outlet_key=%s', outlet_key)
    
    if is_not_empty(outlet_key):
        try:
            
            outlet = None    
                
            db_client = create_db_client(caller_info="read_outlet")
            
            with db_client.context():
                outlet = Outlet.fetch(outlet_key)
            
            outlet_dict = outlet.to_dict()
            
            logger.debug('outlet_dict=%s', outlet_dict)
            
            return render_template('merchant/settings/manage_outlet/manage_outlet_details.html', 
                                   page_title       = gettext('Outlet Details'),
                                   post_url         = url_for('admin_manage_outlet_bp.update_outlet_post'), 
                                   merchant_outlet  = outlet_dict,
                                   ) 
                
        except:
            logger.error('Fail to read merchant account details due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
   
@admin_manage_outlet_bp.route('/outlet/<outlet_key>', methods=['delete'])
@login_required_rest
def delete_outlet(outlet_key):
    return delete_outlet_function(outlet_key)  


@admin_manage_outlet_bp.route('/update', methods=['post'])
@login_required_rest
def update_outlet_post():
    return update_outlet_post_function()
