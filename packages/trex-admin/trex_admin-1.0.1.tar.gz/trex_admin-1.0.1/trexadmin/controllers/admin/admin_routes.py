'''
Created on 17 Sep 2020

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest, account_activated
from trexadmin.menu import admin_menu, superuser_menu
from trexadmin.libs.flask.utils.flask_helper import get_preferred_language, check_is_menu_accessable
from trexadmin.analytics_conf import ALL_CUSTOMER_GROWTH_CHART_DATA_URL
from flask_babel import gettext
from flask.helpers import url_for
import logging
import jinja2
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexadmin.controllers.system.system_route_helpers import get_admin_permission_list

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin')


logger = logging.getLogger('controller')

@jinja2.contextfilter
@admin_bp.app_template_filter()
def is_menu_accessable(context, menu_config):
    return check_is_menu_accessable(menu_config, 'admin_bp')


@admin_bp.route('/dashboard')
@account_activated
@login_required
def dashboard_page(): 
    return prepare_dashboard('admin/dashboard/admin_dashboard_index.html')
    
@admin_bp.route('/dashboard-content')
def dashboard_content(): 
    
    return prepare_dashboard('admin/dashboard/admin_dashboard.html')   
    
def prepare_dashboard(template_path):
    logger.debug('---prepare_dashboard---')   
    try:
        logged_in_user_id   = session.get('logged_in_user_id')
        is_super_user       = session.get('is_super_user')
        is_admin_user       = session.get('is_admin_user')
        
        logger.debug('dashboard_page: logged_in_user_id=%s', logged_in_user_id)
        
        
        if is_super_user:
            menu_config                     = superuser_menu.menu_items
        elif is_admin_user:
            menu_config                     = admin_menu.menu_items
        else:
            menu_config = []    
        
        return render_template(template_path, 
                               page_title                       = gettext('Dashboard'),
                               menu_config                      = menu_config,
                               page_url                         = url_for('admin_bp.dashboard_content'),
                               permission_list                  = get_admin_permission_list(get_preferred_language()),
                               application_logo_url             = url_for('static', filename='app/assets/img/shared/logo.png'),
                               customer_growth_chart_data_url   = ALL_CUSTOMER_GROWTH_CHART_DATA_URL,
                               year                             = datetime.now().year,
                               )
    except:
        logger.error('Failed due to %s', get_tracelog())              
    
