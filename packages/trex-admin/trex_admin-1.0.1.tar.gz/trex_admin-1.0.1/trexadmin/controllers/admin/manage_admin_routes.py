'''
Created on 8 May 2020

@author: jacklok
'''
from flask import Blueprint, render_template, request, current_app, abort
from trexadmin.forms.admin.admin_forms import AdminDetailsForm, AdminDetailsAddForm, AdminUserPermissionForm
from trexlib.forms.common.common_forms import ResetPasswordForm
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexadmin.libs.flask.utils.flask_helper import get_preferred_language,\
    convert_list_to_string
from trexadmin.controllers.system.system_route_helpers import get_admin_permission_list
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.log_util import get_tracelog
from trexconf import conf as lib_conf
import logging
from trexmodel.models.datastore.admin_models import AdminUser
from trexlib.utils.string_util import is_not_empty
from trexadmin.libs.jinja.common_filters import pretty_datetime_filter
from flask.helpers import url_for
from flask_babel import gettext
from trexlib.utils.security_util import hash_password
from trexadmin.conf import PAGINATION_SIZE
import jinja2

manage_admin_bp = Blueprint('manage_admin_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/manage-admin')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@manage_admin_bp.context_processor
def admin_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "admin",
                
                )
'''
@jinja2.contextfilter
@manage_admin_bp.app_template_filter()
def pretty_datetime(context, datetime_str):
    return pretty_datetime_filter(context, datetime_str)
'''
    
    
    
@manage_admin_bp.route('/index', methods=['GET'])
@login_required
def manage_administrator(): 
    logger.debug('---manage_administrator---')
    
    
    #return create_rest_message('Test error message', status_code=StatusCode.BAD_REQUEST)
    
    return render_template('admin/manage_admin/manage_admin_index.html', 
                           page_title       = gettext('Manage Administrator Account'),
                           pagination_limit = PAGINATION_SIZE, 
                           page_url         = url_for('manage_admin_bp.manage_administrator')
                           #superuser_list=superuser_list
                           )
    

@manage_admin_bp.route('/add', methods=['GET'])
@login_required
def add_admin(): 
    
    return render_template('admin/manage_admin/manage_admin_details.html',
                           show_password_input  = True,
                           post_url             = url_for('manage_admin_bp.add_admin_post'),
                           admin_permission_url = url_for('manage_admin_bp.admin_permission'),
                           )


@manage_admin_bp.route('/add', methods=['post'])
def add_admin_post():
    logger.debug('--- submit add_admin data ---')
    add_admin_data = request.form
    
    logger.debug('add_admin_data=%s', add_admin_data)
    
    add_admin_form = AdminDetailsAddForm(add_admin_data)
    
    
    try:
        if add_admin_form.validate():
            
            is_failed = False
            db_client = create_db_client(caller_info="add_admin_post")
            with db_client.context():
                try:
                    created_admin = AdminUser.create(
                                                    name        = add_admin_form.name.data,
                                                    email       = add_admin_form.email.data,
                                                    password    = add_admin_form.password.data,
                                                    active      = True,
                                                    )
                    
                
                
                except:
                    logger.error('Failed to create contact due to %s', get_tracelog())
                    is_failed = True
                
            
            
            if is_failed:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                if created_admin:
                    return create_rest_message(gettext('Administrator have been created'), 
                                           status_code=StatusCode.OK, 
                                           created_admin_key=created_admin.key_in_str,
                                           post_url = url_for('manage_admin_bp.update_admin_post'))
                else:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = add_admin_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)


@manage_admin_bp.route('/search', methods=['POST'])
@login_required_rest
def search_admin(): 
    logger.debug('---search_admin---')
    search_admin_data = request.form
    
    logger.debug('search_admin_data=%s', search_admin_data)
    
    search_admin_form = AdminDetailsForm(search_admin_data)
    
    logger.debug('email=%s', search_admin_form.email.data)
    
    headers = request.headers
    
    
    try:
        
        db_client = create_db_client(caller_info="search_admin")
        with db_client.context():
            admin_user = AdminUser.get_by_email(search_admin_form.email.data)
        
        if admin_user:
            result_key = admin_user.key_in_str 
            
            logger.debug('result_key=%s', result_key)
            
            result_url = url_for('manage_admin_bp.list_search_admin', admin_key=result_key)
            
            logger.debug('result_url=%s', result_url)
            
            return create_rest_message(status_code=StatusCode.OK, result_key=result_key, result_url=result_url) 
        else:
            result_url = url_for('manage_admin_bp.list_search_admin', admin_key='None')
            #return create_rest_message("Administrator account is not found", status_code=StatusCode.BAD_REQUEST)
            return create_rest_message(status_code=StatusCode.OK, result_key='', result_url=result_url)
        
    except:
        logger.error('Fail to search admin due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@manage_admin_bp.route('/admin-listing/<admin_key>', methods=['GET'])
@login_required
def list_search_admin(admin_key): 
    logger.debug('---list_search_admin---')
    
    logger.debug('list_search_admin: admin_key=%s', admin_key)
    
    if is_not_empty(admin_key):
        try:
            
            admin_user_list = []    
                
            db_client = create_db_client(caller_info="list_search_admin")
            with db_client.context():
                admin_user = AdminUser.fetch(admin_key)
                if admin_user:
                    admin_user_list.append(admin_user.to_dict(gmt=lib_conf.DEFAULT_GMT))
            
            pager       = Pager(1, len(admin_user_list), len(admin_user_list))
            pages       = pager.get_pages()
            
            permission_list = get_admin_permission_list(get_preferred_language())
            
            return render_template('admin/manage_admin/admin_listing_content.html', 
                                   admin_user_list              = admin_user_list,
                                   end_point                    = 'manage_admin_bp.list_admin',
                                   pager                        = pager,
                                   pages                        = pages,
                                   pagination_target_selector   = '#admin_search_list_div',
                                   permission_list              = permission_list,
                                   ) 
                
        except:
            logger.error('Fail to list admin due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        #return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        return render_template('admin/manage_admin/admin_listing_content.html', superuser_list=[])
 
@manage_admin_bp.route('/admin-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
def list_admin(limit, page_no): 
    logger.debug('---list_admin---')
    
    logger.debug('page_no=%s', page_no)
    
    page_no_int = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    admin_user_list = []
    result          = []
    try:
        db_client = create_db_client(caller_info="list_admin")
        with db_client.context():
            total_count             = AdminUser.count()
            result                  = AdminUser.list_all(limit=int(limit), offset=offset)
        
        logger.debug('total_count=%s', total_count)
        
        for m in result:
            admin_user_list.append(m.to_dict())
        
           
        pager       = Pager(page_no_int, total_count, limit_int)
        pages       = pager.get_pages()
        
        permission_list = get_admin_permission_list(get_preferred_language())
        
        return render_template('admin/manage_admin/admin_listing_content.html', 
                               admin_user_list              = admin_user_list,
                               end_point                    = 'manage_admin_bp.list_admin',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#admin_search_list_div',
                               permission_list              = permission_list,
                               )
    
    except:
        logger.error('Fail to list merchant account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
@manage_admin_bp.route('/admin-details/<admin_key>', methods=['GET'])
@login_required
def read_admin(admin_key): 
    logger.debug('#####################################---read_admin---')
    
    logger.debug('admin_key=%s', admin_key)
    
    if is_not_empty(admin_key):
        try:
            
            db_client = create_db_client(caller_info="read_admin")
            with db_client.context():
                admin_user = AdminUser.fetch(admin_key)
            
            admin_user_dict = admin_user.to_dict()
            
            logger.debug('admin_user_dict=%s', admin_user_dict)
            
            return render_template('admin/manage_admin/manage_admin_details.html', 
                                   page_title           = gettext('Administrator Account Details'),
                                   post_url             = url_for('manage_admin_bp.update_admin_post'), 
                                   admin_user           = admin_user_dict,
                                   admin_permission_url = url_for('manage_admin_bp.admin_permission'),
                                   admin_user_key       = admin_key,
                                   ) 
                
        except:
            logger.error('Fail to read admin details due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@manage_admin_bp.route('/update', methods=['post'])
def update_admin_post():
    logger.debug('--- submit update_admin_post data ---')
    admin_details_data = request.form
    
    current_app.logger.debug('admin_details_data=%s', admin_details_data)
    
    admin_details_form = AdminDetailsForm(admin_details_data)
    super_user_key = admin_details_form.admin_user_key.data
    
    logger.debug('super_user_key=%s', super_user_key)
    
    try:
        if is_not_empty(super_user_key):
            if admin_details_form.validate():
                
                    
                db_client = create_db_client(caller_info="update_admin_post")
                with db_client.context():   
                    admin_user = AdminUser.fetch(super_user_key)
                    logger.debug('admin_user=%s', admin_user)
                    if admin_user:
                        admin_user.name  = admin_details_form.name.data
                        admin_user.email = admin_details_form.email.data
                        
                        admin_user.put()
                
                
                return create_rest_message(gettext('Administrator have been updated'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = admin_details_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete administrator data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        current_app.logger.error('Fail to register account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@manage_admin_bp.route('/admin-details/<admin_key>', methods=['delete'])
def delete_admin(admin_key):
    logger.debug('--- submit delete_admin_post data ---')
    try:
        if is_not_empty(admin_key):
            db_client = create_db_client(caller_info="delete_admin")
            with db_client.context():   
                admin_user = AdminUser.fetch(admin_key)
                logger.debug('admin_user=%s', admin_user)
                if admin_user:
                    admin_user.key.delete()
            
            return create_rest_message(gettext('Administrator account have been deleted'), status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext('Incomplete administrator account data'), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to delete admin account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    


@manage_admin_bp.route('/admin-permission', methods=['GET'])
@login_required
def admin_permission():
    
    admin_user_key = request.args.get('admin_user_key')
    current_app.logger.debug('admin_user_key=%s', admin_user_key)
    
    if is_not_empty(admin_user_key):
        db_client = create_db_client(caller_info="admin_permission")
        with db_client.context():
            admin_user = AdminUser.fetch(admin_user_key)
            current_app.logger.debug('admin_user=%s', admin_user)
            
        permission_list = get_admin_permission_list(get_preferred_language())
        
        current_app.logger.debug('permission_list=%s', permission_list)
        
        if admin_user:
            
            return render_template('admin/manage_admin/admin_permission.html',
                       page_title               = gettext('Add Admin Permission'),
                       post_url                 = url_for('manage_admin_bp.admin_permission_post'),
                       admin_user               = admin_user.to_dict(),
                       permission_list          = permission_list,
                       )
        else:
            abort(404)
    else:
        abort(404)
    
@manage_admin_bp.route('/admin-permission', methods=['POST'])
@login_required
def admin_permission_post(): 
    current_app.logger.debug('--- submit post_user_permission ---')
    user_permission_data = request.form
    
    current_app.logger.debug('user_permission_data=%s', user_permission_data)
    
    user_permission_form = AdminUserPermissionForm(user_permission_data)
    
    
    logger.debug('permission='+convert_list_to_string(user_permission_form.permission.data))
    
    try:
        if user_permission_form.validate():
            admin_user_key            = user_permission_form.admin_user_key.data
            
            current_app.logger.debug('admin_user_key=%s', admin_user_key)
            
            if is_not_empty(admin_user_key):
                db_client = create_db_client(caller_info="admin_permission_post")
                with db_client.context():
                    admin_user = AdminUser.fetch(admin_user_key)
                    
                
                if admin_user:
                    
                    error_message = None
                    
                    with db_client.context():
                        try:
                            admin_user.update_permission(admin_user, user_permission_form.permission.data, is_superuser = user_permission_form.is_superuser.data)
                        except:
                            error_message = gettext('Failed to update permission')
                            current_app.logger.error('Failed to update permission due to %s', get_tracelog())
                    
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
            current_app.logger.warn('Failed due to form validation where %s', error_message)
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        current_app.logger.error('Fail to add permission to admin user due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    
    return create_rest_message(status_code=StatusCode.OK)

@manage_admin_bp.route('/reset-admin-password/<user_key>', methods=['get'])
@login_required
def reset_admin_password(user_key): 
    return render_template('shared/reset_password.html',
                           page_title       = 'Reset Password',
                           post_url         = url_for('manage_admin_bp.reset_admin_password_post'),
                           key              = user_key,
                           )
    
@manage_admin_bp.route('/reset-admin-password', methods=['post'])
def reset_admin_password_post():
    current_app.logger.debug('--- reset_admin_password_post ---')
    try:
        user_details_data = request.form
    
        current_app.logger.debug('user_details_data=%s', user_details_data)
        user_details_form   = ResetPasswordForm(user_details_data)
        user_key            = user_details_form.key.data
        password            = user_details_form.password.data
        confirm_password    = user_details_form.confirm_password.data
        
        if is_not_empty(user_key):
            
            
            
            if is_not_empty(password) and password==confirm_password:
                user = None
                db_client = create_db_client(caller_info="reset_admin_password_post")
                with db_client.context():   
                    user = AdminUser.fetch(user_key)
                
                if user:
                    user.password = hash_password(user.user_id, password)
                    
                    with db_client.context():
                        user.put()
                        
                    return create_rest_message(gettext('Merchant user password have been reset'), status_code=StatusCode.OK)
            else:
                return create_rest_message(gettext("Password and confirm password must be matched or not empty"), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete merchant user data"), status_code=StatusCode.BAD_REQUEST)        
        
            
    except:
        current_app.logger.error('Fail to reset merchant user password due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  



