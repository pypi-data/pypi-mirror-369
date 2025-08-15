'''
Created on 1 Jul 2020

@author: jacklok
'''
from flask import Blueprint, render_template, request, current_app
from trexadmin.forms.merchant.merchant_forms import AddMerchantUserForm
from trexadmin.controllers.merchant.settings.merchant_manage_user_routes import read_user_function, \
    update_user_post_function, user_permission_post_function, delete_user_function, \
    reset_user_password_post_function, user_permission_function, reset_user_password_function, \
    list_user_function, add_user_post_function

from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
from flask.helpers import url_for
from flask_babel import gettext

admin_manage_user_bp = Blueprint('admin_manage_user_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/manage-user')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@admin_manage_user_bp.context_processor
def manage_user_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "admin",
                
                )
'''
@jinja2.contextfilter
@admin_manage_user_bp.app_template_filter()
def pretty_datetime(context, datetime_str):
    return pretty_datetime_filter(context, datetime_str)
'''

@admin_manage_user_bp.route('/add/merchant-acct/<merchant_acct_key>', methods=['GET'])
@login_required
def add_user(merchant_acct_key): 
    return render_template('merchant/staff/manage_user/manage_user_details.html',
                           show_password_input  = True,
                           page_title           = gettext('Add User Account'),
                           merchant_acct_key    = merchant_acct_key,
                           post_url             = url_for('admin_manage_user_bp.add_user_post'),
                           user_permission_url  = url_for('admin_manage_user_bp.user_permission'), 
                           )
    
@admin_manage_user_bp.route('/add', methods=['POST'])
@login_required_rest
def add_user_post():
    logger.debug('--- submit add_user_post ---')
    add_user_data = request.form
    
    current_app.logger.debug('add_user_data=%s', add_user_data)
    
    add_user_form       = AddMerchantUserForm(add_user_data)
    merchant_acct_key   = add_user_form.merchant_acct_key.data
    
    post_url = url_for('admin_manage_user_bp.update_user_post')
    
    return add_user_post_function(merchant_acct_key, post_url)    

@admin_manage_user_bp.route('/user-permission', methods=['GET'])
@login_required
def user_permission():
    post_url  = url_for('admin_manage_user_bp.user_permission_post')
    return user_permission_function(post_url)
    
@admin_manage_user_bp.route('/user-permission', methods=['POST'])
@login_required
def user_permission_post(): 
    return user_permission_post_function()
 
@admin_manage_user_bp.route('/user-details', methods=['GET'])
@login_required
def read_user(): 
    post_url             = url_for('admin_manage_user_bp.update_user_post')
    user_permission_url  = url_for('admin_manage_user_bp.user_permission')
    return read_user_function(post_url, user_permission_url)

@admin_manage_user_bp.route('/update', methods=['post'])
def update_user_post():
    return update_user_post_function()
    
@admin_manage_user_bp.route('/user', methods=['delete'])
@login_required
def delete_user():
    return delete_user_function() 


@admin_manage_user_bp.route('/reset-user-password', methods=['get'])
@login_required
def reset_user_password(): 
    post_url = url_for('admin_manage_user_bp.reset_user_password_post')
    return reset_user_password_function(post_url)
    
@admin_manage_user_bp.route('/reset-user-password', methods=['post'])
@login_required
def reset_user_password_post():
    return reset_user_password_post_function()    

@admin_manage_user_bp.route('/list-user', methods=['GET'])
@login_required
def list_all_user(): 
    
    merchant_acct_key                   = request.args.get('merchant_acct_key')
    
    page_url                            = None
    add_merchant_user_url               = url_for('admin_manage_user_bp.add_user', merchant_acct_key=merchant_acct_key)
    edit_merchant_user_url              = url_for('admin_manage_user_bp.read_user')
    delete_merchant_user_url            = url_for('admin_manage_user_bp.delete_user')
    reset_merchant_user_password_url    = url_for('admin_manage_user_bp.reset_user_password')
    
    template_path                       = 'admin/manage_merchant/merchant_user_listing.html'
    
    merchant_user_list               = []
    
    db_client = create_db_client(caller_info="list_all_user")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.fetch(merchant_acct_key)
        
        __merchant_user_list    = MerchantUser.list_by_merchant_account(merchant_acct)
        
        if __merchant_user_list:
            for m in __merchant_user_list:
                merchant_user_list.append(m.to_dict())
    
    return list_user_function(merchant_acct_key, template_path, merchant_user_list, 
                              add_merchant_user_url             = add_merchant_user_url, 
                              edit_merchant_user_url            = edit_merchant_user_url, 
                              delete_merchant_user_url          = delete_merchant_user_url, 
                              reset_merchant_user_password_url  = reset_merchant_user_password_url
                              )
    

    
