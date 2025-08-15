'''
Created on 11 Dec 2020

@author: jacklok
'''
from flask import Blueprint, render_template, session, redirect
from trexadmin.libs.flask.decorator.security_decorators import secret_token_authenticated
from flask.helpers import url_for
import logging, json
from flask.globals import current_app
from json import JSONEncoder
from datetime import datetime, date
from trexconf import conf

main_bp = Blueprint('main_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/')

logger = logging.getLogger('root')

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()

@main_bp.route('/')
@main_bp.route('/signin')
def home_page(): 
    
    was_once_logged_in  = session.get('was_once_logged_in')
        
    logger.debug('was_once_logged_in=%s', was_once_logged_in)
    
    if was_once_logged_in:
        user_type = session.get('user_type')
        
        logger.debug('user_type=%s', user_type)
        
        if user_type == 'merchant':
            return redirect(url_for('merchant_bp.dashboard_page'))
    else:
        return redirect(url_for('security_bp.merchant_signin_page'))
        
    
    return render_template('index.html',
                               admin_signin_url     = url_for('security_bp.admin_signin_page'),
                               merchant_signin_url  = url_for('security_bp.merchant_signin_page'),
                               )
    

@main_bp.route('/admin')
@main_bp.route('/admin/signin')
def admin_home_page(): 
    
    was_once_logged_in  = session.get('was_once_logged_in')
        
    logger.debug('was_once_logged_in=%s', was_once_logged_in)
    
    if was_once_logged_in:
        user_type = session.get('user_type')
        
        logger.debug('user_type=%s', user_type)
        
        if user_type == 'admin':
            return redirect(url_for('admin_bp.dashboard_page'))
        
    else:
        return redirect(url_for('security_bp.admin_signin_page'))
    
    return render_template('index.html',
                               admin_signin_url     = url_for('security_bp.admin_signin_page'),
                               merchant_signin_url  = url_for('security_bp.merchant_signin_page'),
                               )
    
@main_bp.route('/config')
@secret_token_authenticated
def app_config():     
    return json.dumps(current_app.config, indent=4, cls=DateTimeEncoder)


@main_bp.route('/version')
def app_version():     
    return conf.APPLICATION_VERSION_NO

@main_bp.route('/test')
def test_page(): 
    
    return render_template('test.html',
                               current_datetime = datetime.now(),
                               )

@main_bp.route('/manifest.json')
def manifest_son():     
    return {
            "manifest_version": "1.0",
            "version": "1.0",
            "name": "Augmigo BackOffice",
            "default_locale": "en",
            "description": "Augmigo is a platform to let merchant enroll membership program",
        }    
    
    