'''
Created on 19 Jul 2023

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
import logging
from trexadmin import conf
from trexlib.utils.crypto_util import decrypt, encrypt
from trexmodel.models.datastore.transaction_models import SalesTransaction
from trexadmin.libs import http
from werkzeug.utils import redirect
from trexlib.utils.string_util import is_not_empty
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexlib.utils.log_util import get_tracelog


mobile_app_bp = Blueprint('mobile_app_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/mobile-app'
                     )

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

'''
Blueprint settings here
'''
@mobile_app_bp.context_processor
def mobile_app_bp_inject_settings():
    return dict(
                
                )

@mobile_app_bp.route('/instant-reward/<instant_reward_code>/encrypt', methods=['GET'])
def encrypt_instant_reward_code(instant_reward_code):
    return encrypt(instant_reward_code), 200

@mobile_app_bp.route('/instant-reward/earn', methods=['GET'])
@request_values
def earn_instant_reward(request_values):
    instant_reward_code = request_values.get('code')
    transaction_id      = None
    target_url          = None
    is_valid            = False
    is_used             = False
    install_url         = conf.MOBILE_APP_INSTALL_URL
    db_client = create_db_client(caller_info="earn_instant_reward")
    
    logger.info('instant_reward_code=%s', instant_reward_code) 
    
    try:
        transaction_id      = decrypt(instant_reward_code)
        target_url          = conf.INSTANT_REWARD_CUSTOM_URL % instant_reward_code
        logger.info('transaction_id=%s', transaction_id)
        
        with db_client.context():
            sales_transaction = SalesTransaction.get_by_transaction_id(transaction_id)
            logger.info('sales_transaction.used=%s', sales_transaction.used)
            
            if sales_transaction.used==False:
                is_valid = True
            else:
                is_used = True
    except:
        logger.error('Invalid instant reward code, due to %s', get_tracelog())
    
    
    
    logger.debug('install_url=%s', install_url)
    logger.debug('target_url=%s', target_url)  
    logger.debug('is_used=%s', is_used)
    logger.debug('is_valid=%s', is_valid)    
    
    template_name = 'mobile_app/earn_instant_reward.html'
    if is_used:
        template_name = 'mobile_app/instant_reward_have_been_used.html'
    else:
        if is_valid==False:
            template_name = 'mobile_app/invalid_instant_reward_code.html'
        
    return render_template(template_name, 
                           transaction_id   = transaction_id,
                           is_valid         = is_valid,
                           target_url       = target_url,
                           install_url      = install_url,
                           )
    
@mobile_app_bp.route('/install-app', methods=['GET'])
def install_app():
    
    redirect_url = None
    if http.is_huawei(request):
        redirect_url = conf.MOBILE_APP_HUAWEI_GALERY_URL
    elif http.is_android(request):
        redirect_url = conf.MOBILE_APP_PLAY_STORE_URL
    elif http.is_ios(request):
        redirect_url = conf.MOBILE_APP_ITUNES_STORE_URL
    else:
        redirect_url = conf.DOWNLOAD_URL

    return redirect(redirect_url)
    
@mobile_app_bp.route('/google-play-store', methods=['GET'])
def google_play_store():
    return render_template("mobile_app/install_store.html", 
                           store_name = 'Google Play Store',
                           browser_user_agent=http.browser_user_agent(request),
                           )
    
@mobile_app_bp.route('/apple-store', methods=['GET'])
def apple_store():
    return render_template("mobile_app/install_store.html", 
                           store_name = 'Apple Store',
                           browser_user_agent=http.browser_user_agent(request),
                           )
    
@mobile_app_bp.route('/huawei-gallery', methods=['GET'])
def huawei_gallary():
    return render_template("mobile_app/install_store.html", 
                           store_name = 'Huawei Gallery',
                           browser_user_agent=http.browser_user_agent(request),
                           )
    
@mobile_app_bp.route('/download', methods=['GET'])
def download():
    redirect_url = None
    if http.is_huawei(request):
        redirect_url = conf.MOBILE_APP_HUAWEI_GALERY_URL
    elif http.is_android(request):
        redirect_url = conf.MOBILE_APP_PLAY_STORE_URL
    elif http.is_ios(request):
        redirect_url = conf.MOBILE_APP_ITUNES_STORE_URL
    if is_not_empty(redirect_url):
        logger.debug('redirect_url=%s', redirect_url)
        return redirect(redirect_url)
    else:
        logger.debug('redirect_url is empty')
        return render_template("mobile_app/download_app.html", 
                           browser_user_agent   = http.browser_user_agent(request),
                           play_store_url       = conf.MOBILE_APP_PLAY_STORE_URL,
                           huawei_store_url     = conf.MOBILE_APP_HUAWEI_GALERY_URL,
                           apple_store_url      = conf.MOBILE_APP_ITUNES_STORE_URL,
                           )            
          
