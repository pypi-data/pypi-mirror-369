'''
Created on 8 Sep 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexadmin.forms.merchant.merchant_forms import ProgramSettingsForm

manage_program_settings_bp = Blueprint('manage_program_settings_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/reward-program/settings/')


logger = logging.getLogger('debug')

'''
Blueprint settings here
'''
@manage_program_settings_bp.context_processor
def program_settings_bp_inject_settings():
            
    return dict(
                
                )
    
@manage_program_settings_bp.route('/', methods=['GET'])
@login_required
def manage_program_settings():
    
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    
    db_client           = create_db_client(caller_info="program_settings_bp_inject_settings")
        
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        if merchant_acct:
            program_settings = merchant_acct.program_settings
            
            #logger.debug('>>>>> before program_settings.rating_review= %s', merchant_acct.program_settings.get('rating_review'))
            
            if program_settings is None:
                merchant_acct.program_settings = MerchantAcct.default_program_settings()
                merchant_acct.put()
            #else:
                #merchant_acct.program_settings.update(MerchantAcct.default_program_settings())
                #logger.debug('read default setting first, %s', merchant_acct.program_settings)
            
            #logger.debug('>>>>> after merchant_acct.program_settings.rating_review= %s', merchant_acct.program_settings.get('rating_review'))
                    
    return render_template('merchant/settings/manage_program/manage_program_settings.html', 
                           page_title                   = gettext('Manage Other Settings'),
                           page_url                     = url_for('manage_program_settings_bp.manage_program_settings'),
                           post_url                     = url_for('manage_program_settings_bp.manage_program_settings_post'),
                           **merchant_acct.program_settings
                           
                           #days_of_return_policy        = days_of_return_policy,
                           )

@manage_program_settings_bp.route('/', methods=['POST'])
@login_required
def manage_program_settings_post():
    
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    
    db_client                   = create_db_client(caller_info="program_settings_bp_inject_settings")
        
    program_settings_data           = request.form
    program_settings_form           = ProgramSettingsForm(program_settings_data)    
    
    logger.debug('program_settings_data=%s', program_settings_data)
    
    if program_settings_form.validate():
        days_of_return_policy               = program_settings_form.days_of_return_policy.data        
        days_of_repeat_purchase_measurement = program_settings_form.days_of_repeat_purchase_measurement.data
        membership_renew_advance_day        = program_settings_form.membership_renew_advance_day.data
        membership_renew_late_day           = program_settings_form.membership_renew_late_day.data
        rating_review                       = program_settings_form.rating_review.data
        
        logger.debug('days_of_return_policy=%s', days_of_return_policy)
        logger.debug('days_of_repeat_purchase_measurement=%s', days_of_repeat_purchase_measurement)
        logger.debug('membership_renew_advance_day=%s', membership_renew_advance_day)
        logger.debug('membership_renew_late_day=%s', membership_renew_late_day)
        logger.debug('rating_review=%s', rating_review)
        
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if merchant_acct.program_settings is None:
                merchant_acct.program_settings = {}
                
            merchant_acct.program_settings['days_of_return_policy']                 = days_of_return_policy
            merchant_acct.program_settings['days_of_repeat_purchase_measurement']   = days_of_repeat_purchase_measurement
            merchant_acct.program_settings['membership_renew_advance_day']          = membership_renew_advance_day
            merchant_acct.program_settings['membership_renew_late_day']             = membership_renew_late_day
            merchant_acct.program_settings['rating_review']                         = rating_review
            
            merchant_acct.put()
        
        return create_rest_message(gettext('Program settingst have been updated'), status_code=StatusCode.OK)
            
    else:
        error_message = program_settings_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)        