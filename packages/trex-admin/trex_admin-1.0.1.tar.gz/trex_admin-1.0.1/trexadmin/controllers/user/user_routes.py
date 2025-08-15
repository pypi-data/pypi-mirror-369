'''
Created on 5 Jul 2022

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
import logging
from trexadmin.forms.user.user_forms import ResetUserPasswordForm
from trexmodel.models.datastore.user_models import User
from datetime import datetime
from trexconf import conf

user_bp = Blueprint('user_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/user'
                     )

logger = logging.getLogger('debug')

'''
Blueprint settings here
'''
@user_bp.context_processor
def user_bp_inject_settings():
    return dict(
                side_menu_group_name    = "user"
                )


@user_bp.route('/reset-password-request/<reset_password_token>', methods=['GET'])
def reset_password(reset_password_token):
    logger.debug('--- get reset_password ---')
    
    user_acct               = None
    
    db_client = create_db_client(caller_info="reset_password")
    with db_client.context():
        user_acct = User.get_by_reset_password_token(reset_password_token)
    
    if user_acct :
        now = datetime.utcnow()
        logger.debug('reset_password: request_reset_password_expiry_datetime=%s', user_acct.request_reset_password_expiry_datetime)
        logger.debug('reset_password: now=%s', now)
        
        if user_acct.request_reset_password_expiry_datetime>now:
            return render_template("user/account/reset_password_request.html", 
                           reset_password_token = reset_password_token,
                           post_url = url_for('user_bp.reset_password_post'),
                           )
        else:
            return render_template("user/account/reset_password_reply.html", 
                                   message = "Request was expired",
                           )
    else:
        return render_template("user/account/reset_password_reply.html", 
                           message = "Invalid request",
                           )
        
@user_bp.route('/reset-password-success', methods=['GET'])
def reset_password_success():
    logger.debug('--- get reset_password_success ---')
    
    return render_template("user/account/reset_password_success.html", 
                           contact_us_url='%scontact-us'%conf.WEBSITE_BASE_URL,
                           )        
        
    
@user_bp.route('/reset-password-request', methods=['POST'])
def reset_password_post():
    logger.debug('--- submit reset_password_post data ---')
    reset_password_data = request.form
    
    logger.debug('reset_password_data=%s', reset_password_data)
    
    reset_password_form = ResetUserPasswordForm(reset_password_data)
    
    
    try:
        if reset_password_form.validate():
            
            db_client = create_db_client(caller_info="reset_password_post")
            
            reset_password_token    = reset_password_form.reset_password_token.data
            password                = reset_password_form.password.data
            
            logger.debug('reset_password_token=%s', reset_password_token)
            logger.debug('password=%s', password)
            
            user_acct               = None
            with db_client.context():
                user_acct = User.get_by_reset_password_token(reset_password_token) 
                
                if user_acct:
                    now = datetime.utcnow()
                    logger.debug('reset_password: request_reset_password_expiry_datetime=%s', user_acct.request_reset_password_expiry_datetime)
                    logger.debug('reset_password: now=%s', now)
                    if user_acct.request_reset_password_expiry_datetime>now:
                        user_acct.reset_password(password)
                    
            if user_acct:
                if user_acct.request_reset_password_expiry_datetime>now:
                    return create_rest_message('Password have been reset', status_code=StatusCode.OK)
                else:
                    return create_rest_message('Request has expired', status_code=StatusCode.BAD_REQUEST)
            else:
                return create_rest_message('Invalid request token', status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = reset_password_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to reset password due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    