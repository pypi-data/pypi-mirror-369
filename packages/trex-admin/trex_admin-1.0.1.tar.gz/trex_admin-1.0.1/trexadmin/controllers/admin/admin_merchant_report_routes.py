'''
Created on 16 Dec 2020

@author: jacklok
'''

from flask import Blueprint, render_template
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from flask.helpers import url_for
from flask_babel import gettext
import jinja2

admin_merchant_report_bp = Blueprint('admin_merchant_report_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/report')


logger = logging.getLogger()

'''
Blueprint settings here
'''
@admin_merchant_report_bp.context_processor
def admin_report_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "admin",
                
                )
'''
@jinja2.contextfilter
@admin_merchant_report_bp.app_template_filter()
def pretty_datetime(context, datetime_str):
    return pretty_datetime_filter(context, datetime_str)
'''

@admin_merchant_report_bp.route('/joined-merchant', methods=['GET'])
@login_required
def joined_merchant_report(): 
    logger.debug('---joined_merchant_report---')
    
    
    return render_template('admin/report/merchant/report_joined_merchant.html', 
                           page_title       = gettext('Joined Merchant Report'),
                           page_url         = url_for('admin_merchant_report_bp.joined_merchant_report')
                           
                           )
    
@admin_merchant_report_bp.route('/merchant-transaction', methods=['GET'])
@login_required
def merchant_transaction_report(): 
    logger.debug('---merchant_transaction_report---')
    
    
    return render_template('admin/report/merchant/report_merchant_transaction.html', 
                           page_title       = gettext('Merchant Transaction Report'),
                           page_url         = url_for('admin_merchant_report_bp.merchant_transaction_report')
                           
                           )    