'''
Created on 11 Dec 2020

@author: jacklok
'''

from flask import Blueprint, render_template, request, abort
from trexadmin.forms.merchant.merchant_forms import AddMerchantUserForm, UpdateMerchantUserForm, ResetMerchantUserPasswordForm, MerchantUserPermissionForm,\
    SearchMerchantUserForm
from trexmodel.models.datastore.merchant_models import Outlet
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager, CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.log_util import get_tracelog
import logging
from trexconf import conf as lib_conf
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser

from trexlib.utils.string_util import is_not_empty, random_string
from trexadmin.controllers.system.system_route_helpers import get_merchant_permission_list
from trexadmin.libs.jinja.common_filters import pretty_datetime_filter
from flask.helpers import url_for
from flask_babel import gettext
from trexlib.utils.security_util import hash_password
from trexadmin.libs.flask.utils.flask_helper import get_preferred_language, get_loggedin_merchant_user_account
import jinja2
from trexadmin.conf import PAGINATION_SIZE

merchant_manage_user_bp = Blueprint('merchant_manage_user_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/manage-user')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@merchant_manage_user_bp.context_processor
def manage_user_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

#@jinja2.contextfilter
#@merchant_manage_user_bp.app_template_filter()
#def pretty_datetime(context, datetime_str):
#    return pretty_datetime_filter(context, datetime_str)

@merchant_manage_user_bp.route('/', methods=['GET'])
@login_required
def manage_user(): 
    logger.debug('---manage_user---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    outlet_list = []
    
    db_client = create_db_client(caller_info="manage_user")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        __outlet_list           = Outlet.list_by_merchant_acct(merchant_acct)
    
        if __outlet_list:
            for m in __outlet_list:
                outlet_list.append(m.to_dict())
    
    return render_template('merchant/staff/manage_user/manage_user_index.html', 
                           page_title           = gettext('Manage Staff'),
                           page_url             = url_for('merchant_manage_user_bp.manage_user'),
                           list_all_user_url    = url_for('merchant_manage_user_bp.list_user_by_page', limit=PAGINATION_SIZE, page_no=1),
                           add_user_url         = url_for('merchant_manage_user_bp.add_user'),
                           search_user_url      = url_for('merchant_manage_user_bp.search_user', limit=PAGINATION_SIZE, page_no=1),
                           outlet_list          = outlet_list,
                           )

@merchant_manage_user_bp.route('/add-user', methods=['GET'])
@login_required
def add_user():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    return render_template('merchant/staff/manage_user/manage_user_details.html',
                           show_password_input  = True,
                           merchant_acct_key    = logged_in_merchant_user.get('merchant_acct_key'),
                           post_url             = url_for('merchant_manage_user_bp.add_user_post'),
                           user_permission_url  = url_for('merchant_manage_user_bp.user_permission'),
                           tab_id               = random_string(6), 
                           )

@merchant_manage_user_bp.route('/add', methods=['POST'])
@login_required_rest
def add_user_post():
    logger.debug('--- submit add_user_post ---')
    add_user_data = request.form
    
    logger.debug('add_user_data=%s', add_user_data)
    
    add_user_form       = AddMerchantUserForm(add_user_data)
    merchant_acct_key   = add_user_form.merchant_acct_key.data
    
    post_url            = url_for('merchant_manage_user_bp.update_user_post')
    
    return add_user_post_function(merchant_acct_key, post_url)
    
def add_user_post_function(merchant_acct_key, post_url):     
    add_user_data = request.form
    add_user_form = AddMerchantUserForm(add_user_data)
    
    try:
        if add_user_form.validate():
            
            logger.debug('merchant_acct_key=%s', merchant_acct_key)
            
            db_client = create_db_client(caller_info="add_user_post_function")
            error_message = None
            with db_client.context():
                try:
                    
                    merchant_acct       = MerchantAcct.fetch(merchant_acct_key)
                    if merchant_acct:
                        
                        merchant_user = MerchantUser.create(
                                            merchant_acct       = merchant_acct,
                                            name                = add_user_form.name.data,
                                            username            = add_user_form.username.data,
                                            password            = add_user_form.password.data,
                                            )
                        
                        hashed_signin_password = hash_password(merchant_user.user_id, add_user_form.password.data)
                        
                        merchant_user.password = hashed_signin_password
                        merchant_user.put()
                        
                except:
                    logger.error('Failed to create contact due to %s', get_tracelog())
                    error_message = gettext('Failed to create/update staff account')
                    
                
            if error_message:
                return create_rest_message(message = error_message, status_code=StatusCode.BAD_REQUEST)
            else:
                if merchant_acct is None:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid staff account data'))
                else:
                    return create_rest_message(gettext('Staff account have been created'), 
                                                   status_code=StatusCode.OK, 
                                                   created_merchant_user_key = merchant_user.key_in_str,
                                                   post_url = post_url)
                
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            
            error_message = add_user_form.create_rest_return_error_message()
            logger.warn('Failed due to form validation where %s', error_message)
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register staff account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@merchant_manage_user_bp.route('/search/page-size/<limit>/page/<page_no>', methods=['POST'])
@login_required_rest
def search_user(limit, page_no):
 
    logger.debug('---search_user---')
    search_user_data = request.form
    
    logger.debug('search_user_data=%s', search_user_data)
    
    search_user_form = SearchMerchantUserForm(search_user_data)
    
    
    page_no_int = int(page_no, 10)
    
    template_path = 'merchant/staff/manage_user/merchant_user_listing.html'
    
    
    limit_int       = int(limit, 10)
    
    cursor                          = request.args.get('cursor')
    previous_cursor                 = request.args.get('previous_cursor')
    merchant_user_list              = []
    
    
    logger.debug('limit_int=%s', limit_int)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    try:
        if search_user_form.validate():
            db_client = create_db_client(caller_info="search_user")
            with db_client.context():
                merchant_acct   = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
                
                (result, total_count, next_cursor) = MerchantUser.search_by_merchant_account(
                                                            merchant_acct,
                                                            name            = search_user_form.name.data,
                                                            username        = search_user_form.username.data,
                                                            assigned_outlet = search_user_form.assigned_outlet.data,
                                                            limit           = limit_int
                                                            )
                
                logger.debug('total_count=%s', total_count)
                
                if result:
                    for m in result:
                        merchant_user_list.append(m.to_dict())
            
            pager       = CursorPager(page_no_int, total_count, limit_int, 
                                        next_cursor                     = next_cursor, 
                                        previous_cursor                 = previous_cursor,
                                        current_cursor                  = cursor,
                                      )
            
            pages       = pager.get_pages()
            
            return list_user_function(logged_in_merchant_user.get('merchant_acct_key'), template_path, merchant_user_list,
                              pager     = pager,
                              pages     = pages,
                              end_point = 'merchant_manage_user_bp.list_user_by_page',
                              
                              )
            
        else:
            error_message = search_user_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
    except:
        logger.error('Fail to search user due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search staff'), status_code=StatusCode.BAD_REQUEST)
        
    
@merchant_manage_user_bp.route('/user-listing/<user_key>', methods=['GET'])
@login_required
def list_search_user(user_key): 
    logger.debug('---list_search_user---')
    
    logger.debug('list_search_user: user_key=%s', user_key)
    
    if is_not_empty(user_key):
        try:
            
            user_list = []    
                
            db_client = create_db_client(caller_info="list_search_user")
            with db_client.context():
                user = MerchantUser.fetch(user_key)
                if user:
                    user_list.append(user.to_dict(gmt=lib_conf.DEFAULT_GMT))
            
            pager       = Pager(1, len(user_list), len(user_list))
            pages       = pager.get_pages()
            
            
            return render_template('merchant/staff/manage_user/user_listing_content.html', 
                                   superuser_list               = user_list,
                                   end_point                    = 'merchant_manage_user_bp.list_user',
                                   pager                        = pager,
                                   pages                        = pages,
                                   pagination_target_selector   = '#user_search_list_div'
                                   ) 
                
        except:
            logger.error('Fail to list user due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        #return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        return render_template('merchant/staff/manage_user/user_listing_content.html', user_list=[])

@merchant_manage_user_bp.route('/list-all-user', methods=['GET'])
@login_required
def list_all_user():
    logged_in_merchant_user          = get_loggedin_merchant_user_account()
    merchant_user_list               = []
    
    db_client = create_db_client(caller_info="list_user")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        __merchant_user_list    = MerchantUser.list_by_merchant_account(merchant_acct)
        
        if __merchant_user_list:
            for m in __merchant_user_list:
                merchant_user_list.append(m.to_dict())
    
    template_path = 'merchant/staff/manage_user/merchant_user_listing.html'
    
    return list_user_function(logged_in_merchant_user.get('merchant_acct_key'), template_path, merchant_user_list)

def list_user_function(merchant_acct_key, template_path, merchant_user_list,
                           add_merchant_user_url            = None,
                           edit_merchant_user_url           = None,
                           delete_merchant_user_url         = None,
                           reset_merchant_user_password_url = None,         
                           pager                            = None,
                           pages                            = None,
                           end_point                        = None,
                           pagination_target_selector       = '#user_list_div',
                           ):    
    
    if add_merchant_user_url is None:
        add_merchant_user_url            = url_for('merchant_manage_user_bp.add_user')
    
    if edit_merchant_user_url is None:
        edit_merchant_user_url           = url_for('merchant_manage_user_bp.read_user')
    
    if delete_merchant_user_url is None:
        delete_merchant_user_url         = url_for('merchant_manage_user_bp.delete_user')
    
    if reset_merchant_user_password_url is None:
        reset_merchant_user_password_url = url_for('merchant_manage_user_bp.reset_user_password')
    
    outlet_list         = []
    permission_list     = get_merchant_permission_list(get_preferred_language())
    
    
    db_client = create_db_client(caller_info="list_all_user_function")
    
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(merchant_acct_key)
        __outlet_list           = Outlet.list_by_merchant_acct(merchant_acct)
    
        if __outlet_list:
            for m in __outlet_list:
                outlet_list.append(m.to_dict())        
    
    return render_template(template_path,
                           page_title                       = gettext('Manage User'),
                           merchant_acct_key                = merchant_acct_key,
                           merchant_user_list               = merchant_user_list or [],
                           add_merchant_user_url            = add_merchant_user_url,
                           edit_merchant_user_url           = edit_merchant_user_url,
                           delete_merchant_user_url         = delete_merchant_user_url,
                           reset_merchant_user_password_url = reset_merchant_user_password_url,
                           permission_list                  = permission_list,
                           outlet_list                      = outlet_list or [],
                           pager                            = pager,
                           pages                            = pages,
                           end_point                        = end_point,
                           pagination_target_selector       = pagination_target_selector,
                           logged_in_merchant_user          = get_loggedin_merchant_user_account(),
                           )
    
    
@merchant_manage_user_bp.route('/list-user/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_user_by_page(limit, page_no): 
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    merchant_user_list = []
    
    logger.debug('page_no=%s', page_no)
    
    page_no_int = int(page_no, 10)
    
    template_path = 'merchant/staff/manage_user/merchant_user_listing.html'
    
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    limit_int       = int(limit, 10)
    
    db_client = create_db_client(caller_info="list_user_by_page")
    
    cursor                          = request.args.get('cursor')
    previous_cursor                 = request.args.get('previous_cursor')
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        total_count             = MerchantUser.count_by_merchant_account(merchant_acct)
        (result, next_cursor)   = MerchantUser.list_all_by_merchant_account(merchant_acct, 
                                                                        offset              = offset,
                                                                        limit               = limit_int,
                                                                        start_cursor        = cursor, 
                                                                        return_with_cursor  = True,
                                                                        )
        
        
        if result:
            for m in result:
                merchant_user_list.append(m.to_dict())
    
    pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                     = next_cursor, 
                                previous_cursor                 = previous_cursor,
                                current_cursor                  = cursor,
                              )
    
    pages       = pager.get_pages()
    
    
    
    return list_user_function(logged_in_merchant_user.get('merchant_acct_key'), template_path, merchant_user_list,
                              pager     = pager,
                              pages     = pages,
                              end_point = 'merchant_manage_user_bp.list_user_by_page',
                              )
    
    
    
 
@merchant_manage_user_bp.route('/user-details', methods=['GET'])
@login_required
def read_user():
    post_url             = url_for('merchant_manage_user_bp.update_user_post')
    user_permission_url  = url_for('merchant_manage_user_bp.user_permission')
    return read_user_function(post_url, user_permission_url)
    
def read_user_function(post_url, user_permission_url): 
    logger.debug('---read_user---')
    
    user_key            = request.args.get('user_key')
    merchant_acct_key   = None
    logger.debug('user_key=%s', user_key)
    
    if is_not_empty(user_key):
        try:
            
            user = None    
                
            db_client = create_db_client(caller_info="read_user")
            with db_client.context():
                user = MerchantUser.fetch(user_key)
                merchant_acct_key = user.merchant_acct_key
                user_dict = user.to_dict()
            
            logger.debug('user_dict=%s', user_dict)
            
            return render_template('merchant/staff/manage_user/manage_user_details.html', 
                                   page_title           = gettext('Staff Account Details'),
                                   post_url             = post_url, 
                                   merchant_user        = user_dict,
                                   user_permission_url  = user_permission_url,
                                   user_key             = user_key,
                                   merchant_acct_key    = merchant_acct_key,
                                   tab_id               = random_string(6),
                                   ) 
                
        except:
            logger.error('Fail to read user details due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
    
@merchant_manage_user_bp.route('/update', methods=['post'])
def update_user_post():
    return update_user_post_function()

def update_user_post_function():    
    logger.debug('--- submit update_user_post data ---')
    user_details_data = request.form
    
    logger.debug('user_details_data=%s', user_details_data)
    
    user_details_form   = UpdateMerchantUserForm(user_details_data)
    merchant_user_key   = user_details_form.merchant_user_key.data
    
    logger.debug('merchant_user_key=%s', merchant_user_key)
    
    try:
        if is_not_empty(merchant_user_key):
            if user_details_form.validate():
                
                    
                db_client = create_db_client(
                                             caller_info="update_user_post")
                with db_client.context():   
                    user = MerchantUser.fetch(merchant_user_key)
                    logger.debug('user=%s', user)
                    
                    is_username_duplicated = False
                    if user:
                        new_username    = user_details_form.username.data
                        
                        check_unique_merchant_user = MerchantUser.get_by_username(new_username)
                        
                        logger.debug('check_unique_merchant_user=%s', check_unique_merchant_user)
                        
                        if check_unique_merchant_user is not None:
                            logger.debug('check_unique_merchant_user.key_in_str=%s', check_unique_merchant_user.key_in_str)
                        
                        if check_unique_merchant_user is None or (check_unique_merchant_user.key_in_str ==merchant_user_key):
                        
                            user.name       = user_details_form.name.data
                            user.username   = new_username
                            user.put()
                        else:
                            is_username_duplicated = True
                                
                
                if is_username_duplicated:
                    return create_rest_message(gettext('Merchant user username have been taken'), 
                                               status_code=StatusCode.BAD_REQUEST)
                
                else:
                    
                    return create_rest_message(gettext('Merchant user account have been updated'), 
                                               status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = user_details_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete staff data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to register account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@merchant_manage_user_bp.route('/user-permission', methods=['GET'])
@login_required
def user_permission():
    post_url  = url_for('admin_manage_user_bp.user_permission_post')
    return user_permission_function(post_url)
    
def user_permission_function(post_url):    
    merchant_user_key       = request.args.get('merchant_user_key')
    
    logger.debug('merchant_user_key=%s', merchant_user_key)
    
    if is_not_empty(merchant_user_key):
        db_client = create_db_client(caller_info="user_permission")
        outlet_list = []
        with db_client.context():
            merchant_user   = MerchantUser.fetch(merchant_user_key)
            merchant_acct   = merchant_user.merchant_acct
            logger.debug('merchant_user=%s', merchant_user)
            __outlet_list = Outlet.list_by_merchant_acct(merchant_acct)
            
        permission_list = get_merchant_permission_list(get_preferred_language())
        
        if __outlet_list:
            for o in __outlet_list:
                outlet_list.append(o.to_dict())
        
        logger.debug('permission_list=%s', permission_list)
        logger.debug('outlet_list=%s', outlet_list)
        
        if merchant_user:
            
            return render_template('merchant/staff/manage_user/user_permission.html',
                       page_title               = gettext('Add Staff Permission'),
                       post_url                 = post_url,
                       merchant_user            = merchant_user.to_dict(),
                       permission_list          = permission_list,
                       outlet_list              = outlet_list,
                       )
        else:
            abort(404)
    else:
        abort(404)    

@merchant_manage_user_bp.route('/user-permission', methods=['POST'])
@login_required
def user_permission_post():
    return user_permission_post_function()
    
def user_permission_post_function(): 
    logger.debug('--- submit post_user_permission ---')
    user_permission_data = request.form
    
    logger.debug('user_permission_data=%s', user_permission_data)
    
    user_permission_form = MerchantUserPermissionForm(user_permission_data)
    
    
    try:
        if user_permission_form.validate():
            merchant_user_key            = user_permission_form.merchant_user_key.data
            
            logger.debug('merchant_user_key=%s', merchant_user_key)
            
            if is_not_empty(merchant_user_key):
                db_client = create_db_client(
                                             caller_info="user_permission_post")
                with db_client.context():
                    merchant_user = MerchantUser.fetch(merchant_user_key)
                    merchant_acct = merchant_user.merchant_acct
                
                if merchant_user and merchant_acct:
                    
                    error_message = None
                    
                    with db_client.context():
                        try:
                            MerchantUser.update_permission(merchant_user, 
                                                           user_permission_form.access_permission.data,
                                                           user_permission_form.outlet_permission.data, 
                                                           is_admin = user_permission_form.is_admin.data
                                                           )
                        except:
                            error_message = gettext('Failed to update permission')
                            logger.error('Failed to update permission due to %s', get_tracelog())
                    
                else:
                    error_message = gettext('Invalid data')
                    
                if error_message:
                    return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message(gettext('Permission have been updated'), 
                                                   status_code=StatusCode.OK)
            
            else:
                return create_rest_message(gettext('Missing user data'), status_code=StatusCode.BAD_REQUEST)        
        else:
            
            error_message = user_permission_form.create_rest_return_error_message()
            logger.warn('Failed due to form validation where %s', error_message)
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to add permission to staff due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    
    return create_rest_message(status_code=StatusCode.OK)
    
@merchant_manage_user_bp.route('/delete', methods=['delete'])
@login_required
def delete_user():
    return delete_user_function()

def delete_user_function():    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    user_key = request.args.get('user_key')
    logger.debug('--- submit delete_user data ---, user_key=%s', user_key)
    try:
        if is_not_empty(user_key):
            logger.debug('delete_user: user_key=%s', user_key)
            logger.debug('delete_user: logged_in_merchant_user.key=%s', logged_in_merchant_user.get('key'))
            
            
            if user_key == logged_in_merchant_user.get('key'):
                return create_rest_message(message=gettext('Cannot delete own account'), 
                                           status_code=StatusCode.BAD_REQUEST)
            else:
                db_client = create_db_client(caller_info="delete_user")
                with db_client.context():   
                    user = MerchantUser.fetch(user_key)
                    logger.debug('user=%s', user)
                    if user:
                        user.key.delete()
                        #pass
            
            return create_rest_message(gettext('Staff account have been deleted'), 
                                       status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext("Incomplete staff data"), 
                                       status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to delete merchant user account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)       

@merchant_manage_user_bp.route('/reset-user-password', methods=['get'])
@login_required
def reset_user_password():
    post_url  = url_for('merchant_manage_user_bp.reset_user_password_post')
    return reset_user_password_function(post_url)
    
def reset_user_password_function(post_url):     
    user_key = request.args.get('user_key')
    return render_template('shared/reset_password.html',
                           page_title       = gettext('Reset Password'),
                           post_url         = post_url,
                           key              = user_key,
                           )

@merchant_manage_user_bp.route('/reset-user-password', methods=['post'])
@login_required
def reset_user_password_post():
    return reset_user_password_post_function()

def reset_user_password_post_function():    
    logger.debug('--- reset_user_password ---')
    try:
        user_details_data = request.form
    
        logger.debug('user_details_data=%s', user_details_data)
        user_details_form   = ResetMerchantUserPasswordForm(user_details_data)
        user_key            = user_details_form.key.data
        password            = user_details_form.password.data
        confirm_password    = user_details_form.confirm_password.data
        
        if is_not_empty(user_key):
            
            
            
            if is_not_empty(password) and password==confirm_password:
                user = None
                db_client = create_db_client(caller_info="reset_user_password_post")
                with db_client.context():   
                    user = MerchantUser.fetch(user_key)
                
                if user:
                    user.password = hash_password(user.user_id, password)
                    
                    with db_client.context():
                        user.put()
                        
                    return create_rest_message(gettext('Staff password have been reset'), 
                                               status_code=StatusCode.OK)
            else:
                return create_rest_message(gettext("Password and confirm password must be matched or not empty"), 
                                           status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete merchant user data"), 
                                       status_code=StatusCode.BAD_REQUEST)        
        
            
    except:
        logger.error('Fail to reset merchant user password due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
           