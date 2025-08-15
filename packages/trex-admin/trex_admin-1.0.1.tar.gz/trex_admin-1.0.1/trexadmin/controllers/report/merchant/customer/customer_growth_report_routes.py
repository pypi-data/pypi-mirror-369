'''
Created on 7 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template, request, current_app
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from flask.helpers import url_for
from flask_babel import gettext
import jinja2

merchant_customer_growth_report_bp = Blueprint('merchant_customer_growth_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/report/customer/')


logger = logging.getLogger('report')

'''
Blueprint settings here
'''
@merchant_customer_growth_report_bp.context_processor
def merchant_customer_growth_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_customer_growth_report_bp.route('/', methods=['GET'])
@login_required
def merchant_customer_growth(): 
    current_app.logger.debug('---merchant_customer_growth---')
    
    
    return render_template('report/merchant/customer/merchant_customer_growth_report.html', 
                           page_title           = gettext('Customer Growth Report'),
                           page_url             = url_for('merchant_customer_growth_report_bp.merchant_customer_growth'),
                           
                           )
