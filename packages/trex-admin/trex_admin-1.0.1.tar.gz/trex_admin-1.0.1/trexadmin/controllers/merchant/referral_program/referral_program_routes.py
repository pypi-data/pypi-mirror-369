'''
Created on 17 Apr 2024

@author: jacklok
'''
from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
import logging


from trexconf import conf, program_conf
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.crypto_util import encrypt_json, aes_encrypt_json

referral_program_bp = Blueprint('referral_program_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/referral/program')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

@referral_program_bp.context_processor
def referral_program_setup_bp_inject_settings():
    
    return dict(
        )
    
@referral_program_bp.route('/merchant-acct-code/<merchant_acct_code>/referrer-code/<referrer_code>/join', methods=['GET'])
def show_referee_referral_program_reward_join_link(merchant_acct_code, referrer_code):
    try:
        db_client = create_db_client(caller_info="show_referee_referral_program_reward_join_link")
        
        logger.info('merchant_acct_code=%s, referrer_code=%s', merchant_acct_code, referrer_code)
        
        with db_client.context():
            merchant_acct = MerchantAcct.get_by_account_code(merchant_acct_code)
        
        page_link = '{base_url}/referral/program/merchant-acct-code/{merchant_acct_code}/referrer-code/{referrer_code}/join'.format(
                                base_url            = conf.REFER_BASE_URL,
                                merchant_acct_code  = merchant_acct_code,
                                referrer_code       = referrer_code,
                                ) 
        logger.info('page_link=%s', page_link)
        
        join_via_app_url = conf.REFER_A_FRIEND_DEEP_LINK;
        referrer_data = {
                        'merchant_acct_code': merchant_acct_code,
                        'referrer_code': referrer_code,
                        }
        encrypted_referrer_data = aes_encrypt_json(referrer_data)
        
        join_via_app_url = join_via_app_url.format(
                                        merchant_acct_code  = merchant_acct_code,
                                        referrer_code  = referrer_code,
                                        )
        logger.info('join_via_app_url=%s', join_via_app_url)
        join_via_web_url = conf.REFER_A_FRIEND_CUSTOM_URL;
        #join_via_web_url = conf.REFER_A_FRIEND_DEEP_LINK;
        '''
        join_via_web_url = join_via_web_url.format(
                                        merchant_acct_code  = merchant_acct_code,
                                        referrer_code       = referrer_code
                                        )
        '''
        
        join_via_web_url = join_via_web_url.format(
                                        referrer_data  = encrypted_referrer_data,
                                        )
        
        logger.info('join_via_app_url=%s', join_via_app_url)
        logger.info('join_via_web_url=%s', join_via_web_url)
        
        return render_template('merchant/loyalty/referral_program/referral_reward_page.html', 
                               page_title                       = merchant_acct.referee_promote_title,
                               promote_title                    = merchant_acct.referee_promote_title,
                               promote_desc                     = merchant_acct.referee_promote_desc,
                               promote_image                    = merchant_acct.referee_promote_image if is_not_empty(merchant_acct.referee_promote_image) else conf.REFERRAL_DEFAULT_PROMOTE_IMAGE,
                               page_link                        = page_link, 
                               join_via_app_url                 = join_via_app_url,
                               join_via_web_url                 = join_via_web_url,
                               show_full                        = True,
                               )
    except:
        logger.error('Failed due to %s', get_tracelog())
        
        return "Failed due to %%s" % get_tracelog(), 200
        
        
    
     
