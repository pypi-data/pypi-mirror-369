'''
Created on 20 Apr 2020

@author: jacklok
'''
import csv, os, json 
from flask import Blueprint, render_template, request, current_app, session, jsonify, abort
from trexlib.utils.log_util import get_tracelog
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON, MINE_TYPE_JAVASCRIPT
from trexmodel.utils.model.model_util import create_db_client
from trexweb.libs.http import StatusCode, create_rest_message
from trexmodel.models.datastore.system_models import ContactUs, Feedback
from trexweb.forms.system_forms import ContactUsForm, FeedbackForm
from trexweb.conf import SIGNIN_URL
from trexmail.flask_mail import send_email
from trexmail.conf import DEFAULT_SENDER, DEFAULT_RECIPIENT_EMAIL
from trexconf import conf
import logging
from flask.helpers import url_for
from flask_babel import gettext
#from trexmodel import program_conf
from trexconf import program_conf
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantTagging,\
    Outlet
from datetime import datetime
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from werkzeug.utils import redirect
from trexmail.email_helper import is_valid_email
from trexadmin.controllers.system.system_route_helpers import get_country_json,\
    list_csv_code_label_json, get_currency_json, get_merchant_permission_json,\
    get_reward_base_json, get_program_status_json, get_reward_format_json,\
    get_reward_effective_type_json, get_reward_expiration_type_json,\
    get_reward_base_and_reward_format_mapping, get_reward_use_condition_json,\
    get_weekday_json, get_membership_expiration_type_json,\
    get_membership_entitle_qualification_type_json,get_voucher_type_json,\
    get_membership_upgrade_expiry_type_json, get_giveaway_method_json,\
    get_giveaway_system_condition_json, get_barcode_type_json,\
    get_running_no_generator_json, get_receipt_header_data_type_json,\
    get_receipt_footer_data_type_json,\
    get_birthday_reward_giveaway_type_form_list,\
    get_entitle_reward_condition_list, get_currency_config,\
    get_merchant_dinning_option_code, get_merchant_outlet_code,\
    get_redeem_limit_type_json, get_loyalty_package_feature_by_group_value_json,\
    get_loyalty_package_json, get_product_package_json,\
    get_redeem_reward_format_json, get_push_notification_content_type_json,\
    get_loyalty_device_activation_code, get_pos_package_json,\
    get_merchant_promotion_code, get_industry_type_json,\
    get_merchant_partnership_status_type_json,\
    get_merchant_partnership_limit_redeem_type_json,\
    get_merchant_business_type_json
from trexlib.utils.string_util import is_not_empty, truncate_if_max_length
from trexconf.conf import AGE_TIME_FIVE_MINUTE, AGE_TIME_ONE_HOUR
from trexmodel.models.datastore.marketing_models import MarketingImage
from trexlib.utils.common.cache_util import cache
from trexmodel.models.datastore.redemption_catalogue_models import RedemptionCatalogue
from trexlib.libs.flask_wtf.request_wrapper import request_language

system_bp = Blueprint('system_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/system'
                     )

#from main import csrf


LANGUAGES = 'LANGUAGES'

#logger = logging.getLogger('system-controller')
logger = logging.getLogger('target-debug')

@system_bp.context_processor
def inject_settings():
    return dict(
                REWARD_EFFECTIVE_TYPE_IMMEDIATE         = program_conf.REWARD_EFFECTIVE_TYPE_IMMEDIATE,
                REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE     = program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE,
                REWARD_EFFECTIVE_TYPE_AFTER_MONTH       = program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH,
                REWARD_EFFECTIVE_TYPE_AFTER_WEEK        = program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK,
                REWARD_EFFECTIVE_TYPE_AFTER_DAY         = program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY,
                
                REWARD_EXPIRATION_TYPE_SPECIFIC_DATE    = program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE,
                REWARD_EXPIRATION_TYPE_AFTER_YEAR       = program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR,
                REWARD_EXPIRATION_TYPE_AFTER_MONTH      = program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH,
                REWARD_EXPIRATION_TYPE_AFTER_WEEK       = program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK,
                REWARD_EXPIRATION_TYPE_AFTER_DAY        = program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY,
                
                ADVANCE_IN_DAY                          = program_conf.ADVANCE_IN_DAY,
                REWARD_LIMIT_TYPE_NO_LIMIT              = program_conf.REWARD_LIMIT_TYPE_NO_LIMIT,
                REWARD_LIMIT_TYPE_BY_TRANSACTION        = program_conf.REWARD_LIMIT_TYPE_BY_TRANSACTION,
                REWARD_LIMIT_TYPE_BY_MONTH              = program_conf.REWARD_LIMIT_TYPE_BY_MONTH,
                REWARD_LIMIT_TYPE_BY_WEEK               = program_conf.REWARD_LIMIT_TYPE_BY_WEEK, 
                REWARD_LIMIT_TYPE_BY_DAY                = program_conf.REWARD_LIMIT_TYPE_BY_DAY,
                )

@system_bp.after_request
def set_system_response_headers(response):
    request_url = request.url
    logging.debug('request_url=%s', request_url)
    
    if request_url.endswith('.js'):
        response.headers['Content-Type'] = MINE_TYPE_JAVASCRIPT
    
    response.charset= 'utf-8'    
    logging.debug('---set_system_response_headers---')
    
    return response

@system_bp.route('/contact-us', methods=['GET'])
def contact_us():
    return render_template("system/contact_us_from_dashboard.html", 
                           page_title       = gettext("Drop Us a Message"),
                           page_url         = url_for('system_bp.contact_us')
                           )
    
@system_bp.route('/contact-us-page', methods=['GET'])
def contact_us_page():
    return render_template("system/contact_us.html"
                           )        

@system_bp.route('/thank-you-for-contact-us-page', methods=['GET'])
def thank_you_for_contact_us_page():
    return render_template("system/thank_you_for_contact_us_page.html")

@system_bp.route('/thank-you-for-contact-us', methods=['GET'])
def thank_you_for_contact_us():
    return render_template("system/thank_you_for_contact_us.html")




@system_bp.route('/list-country-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_country_code_json():
    logger.debug('---list_country_code_json--- ')
    
    data_list = get_country_json()
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-currency-code', methods=['GET'])
#@cache.cached(timeout=50)
def list_currency_code_json():
    logger.debug('---list_currency_code_json--- ')
    data_list = get_currency_json()
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-merchant-permission-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_merchant_permission_code_json(request_language):
    logging.debug('---list_merchant_permission_code_json--- ')
    data_list = get_merchant_permission_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-reward-base-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_reward_base_code_json(request_language):
    logging.debug('---list_reward_base_code_json--- ')
    data_list = get_reward_base_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-program-status', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_program_status_code_json(request_language):
    logging.debug('---list_program_status_code_json--- ')
    data_list = get_program_status_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-reward-format-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_reward_format_code_json(request_language):
    logging.debug('---list_reward_format_code_json--- ')
    data_list = get_reward_format_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-redeem-reward-format-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_redeem_reward_format_code_json(request_language):
    logging.debug('---list_redeem_reward_format_code_json--- ')
    data_list = get_redeem_reward_format_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-push-notification-content-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_push_notification_content_type_json(request_language):
    logging.debug('---list_push_notification_content_type_json--- ')
    data_list = get_push_notification_content_type_json(request_language)
    
    return list_csv_code_label_json(data_list)



@system_bp.route('/list-reward-effective-type', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_reward_effective_type_code_json(request_language):
    logging.debug('---list_reward_effective_type_code_json--- ')
    data_list = get_reward_effective_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-reward-expiration-type', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_reward_expiration_type_code_json(request_language):
    logging.debug('---list_reward_expiration_type_code_json--- ')
    data_list = get_reward_expiration_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-reward-base-and-reward-format-mapping', methods=['GET'])
@cache.cached(timeout=600)
def list_reward_base_and_reward_format_json():
    logger.debug('---list_reward_base_and_reward_format_json--- ')
    data_list = get_reward_base_and_reward_format_mapping()
    
    #data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    return list_csv_code_label_json(data_list)


@system_bp.route('/list-reward-use-condition-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_reward_use_condition_code_json(request_language):
    logger.debug('---list_reward_use_condition_code_json--- ')
    
    data_list = get_reward_use_condition_json(request_language)()
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-weekday-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_weekday_code_json(request_language):
    logger.debug('---list_weekday_code_json--- ')
    
    data_list = get_weekday_json(request_language)()
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-membership-expiration-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_membership_expiration_type_code_json(request_language):
    logger.debug('---list_membership_expiration_type_code_json--- ')
    
    data_list = get_membership_expiration_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-membership-entitle-qualification-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_membership_entitle_qualification_type_code_json(request_language):
    logger.debug('---list_membership_entitle_qualification_type_code_json--- ')
    
    data_list = get_membership_entitle_qualification_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-membership-upgrade-expiry-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_membership_upgrade_expiry_type_code_json(request_language):
    logger.debug('---list_membership_entitle_qualification_type_code_json--- ')
    
    data_list = get_membership_upgrade_expiry_type_json(request_language)
    
    return list_csv_code_label_json(data_list)


@system_bp.route('/list-giveaway-method-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_giveaway_method_code_json(request_language):
    logger.debug('---list_giveaway_method_code_json--- ')
    
    data_list = get_giveaway_method_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-giveaway-system-condition-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_giveaway_system_condition_code_json(request_language):
    logger.debug('---list_giveaway_system_condition_code_json--- ')

    data_list = get_giveaway_system_condition_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-barcode-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_barcode_type_code_json(request_language):
    logger.debug('---list_barcode_type_code_json--- ')
    
    data_list = get_barcode_type_json(request_language)
    
    return list_csv_code_label_json(data_list)


@system_bp.route('/list-running-no-generator-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_running_no_generator_code_json(request_language):
    logger.debug('---list_running_no_generator_code_json--- ')
    
    data_list = get_running_no_generator_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-receipt-header-data-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_receipt_header_data_type_code_json(request_language):
    logger.debug('---list_receipt_header_data_type_code_json--- ')
    
    data_list = get_receipt_header_data_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-receipt-footer-data-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_receipt_footer_data_type_code_json(request_language):
    logger.debug('---list_receipt_footer_data_type_code_json--- ')
    
    data_list = get_receipt_footer_data_type_json(request_language)
    
    return list_csv_code_label_json(data_list)



@system_bp.route('/list-birthday-reward-giveaway-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_birthday_reward_giveaway_type_code_json(request_language):
    logger.debug('---list_birthday_reward_giveaway_type_code_json--- ')
    
    data_list = get_birthday_reward_giveaway_type_form_list(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-entitle-reward-condition-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_entitle_reward_condition_code_json(request_language):
    logger.debug('---list_entitle_reward_condition_code_json--- ')
    
    data_list = get_entitle_reward_condition_list(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-voucher-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_voucher_type_json(request_language):
    logger.debug('---list_voucher_type_json--- ')
    
    data_list = get_voucher_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-redeem-limit-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_redeem_limit_type_json(request_language):
    logger.debug('---list_redeem_limit_type_json--- ')
    
    data_list = get_redeem_limit_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-industry-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_industry_type_json(request_language):
    logger.debug('---list_industry_type_json--- ')
    
    data_list = get_industry_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-merchant-partnership-status-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_merchant_partnership_status_json(request_language):
    logger.debug('---list_merchant_partnership_status_json--- ')
    
    data_list = get_merchant_partnership_status_type_json(request_language)
    
    return list_csv_code_label_json(data_list)



@system_bp.route('/list-merchant-voucher-code', methods=['GET'])
def list_publish_voucher_json():
    logging.debug('---list_publish_voucher_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    db_client = create_db_client(caller_info="list_publish_voucher_json")
    try:
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            voucher_list            = MerchantVoucher.list_by_merchant_account(merchant_acct) 
            '''
            published_vouchers_list = merchant_acct.published_voucher_configuration.get('vouchers') or []
            for voucher in published_vouchers_list:
                data_list.append({
                                "code"      : voucher.get('voucher_key'),
                                "label"     : voucher.get('label'),
                                'image_url' : voucher.get('image_url'),
                                })
            '''
            for voucher in voucher_list:
                data_list.append({
                                "code"      : voucher.key_in_str,
                                "label"     : voucher.label,
                                'image_url' : voucher.image_public_url,
                                })
            
    except:
        logger.error('Fail to list published voucher due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_FIVE_MINUTE,
                                  )
    
    return resp 

@system_bp.route('/list-merchant-voucher-code/<merchant_acct_key>', methods=['GET'])
def list_publish_merchant_voucher_json(merchant_acct_key):
    logging.debug('---list_publish_merchant_voucher_json--- ')
    data_list = []
    
    db_client = create_db_client(caller_info="list_publish_merchant_voucher_json")
    try:
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(merchant_acct_key)
            voucher_list            = MerchantVoucher.list_by_merchant_account(merchant_acct) 
            for voucher in voucher_list:
                data_list.append({
                                "code"      : voucher.key_in_str,
                                "label"     : voucher.label,
                                'image_url' : voucher.image_public_url,
                                })
            
    except:
        logger.error('Fail to list published merchant voucher due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_FIVE_MINUTE,
                                  )
    
    return resp  

@system_bp.route('/list-merchant-partner-exclusive-redemption-catalogue', methods=['GET'])
def list_merchant_partner_exclusive_redemption_catalogue_json():
    logging.debug('---list_merchant_partner_exclusive_redemption_catalogue_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    db_client = create_db_client(caller_info="list_merchant_partner_exclusive_redemption_catalogue_json")
    try:
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            catalogue_list          = RedemptionCatalogue.list_published_partner_exclusive_by_merchant_account(merchant_acct) 
            for catalogue in catalogue_list:
                if catalogue.is_archived==False and catalogue.is_expired==False and catalogue.is_effectived==True:
                    data_list.append({
                                "code"      : catalogue.key_in_str,
                                "label"     : catalogue.label,
                                'image_url' : catalogue.image_public_url,
                                })
            
    except:
        logger.error('Fail to list published voucher due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_FIVE_MINUTE,
                                  )
    
    return resp 

@system_bp.route('/list-merchant-partner-merchant-acct', methods=['GET'])
def list_merchant_partner_merchant_acct_json():
    logging.debug('---list_merchant_partner_merchant_acct_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    db_client = create_db_client(caller_info="list_merchant_partner_merchant_acct_json")
    
    try:
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            
            
            if merchant_acct.partner_merchant_history_configuration and merchant_acct.partner_merchant_history_configuration.get('partners'):
                for partner_merchant in merchant_acct.partner_merchant_history_configuration.get('partners').values():
                    data_list.append({
                            "code"              : partner_merchant.get('merchant_acct_key'),
                            "label"             : partner_merchant.get('brand_name'),
                            'logo_image_url'    : partner_merchant.get('logo_image_url'),
                        })
            
    except:
        logger.error('Fail to list published voucher due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_FIVE_MINUTE,
                                  )
    
    return resp 

@system_bp.route('/list-partnership-limit-redeem-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_partnership_limit_redeem_type_json(request_language):
    logger.debug('---list_partnership_limit_redeem_type_json--- ')
    
    data_list = get_merchant_partnership_limit_redeem_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-merchant-marketing-image-code', methods=['GET'])
def list_marketing_images_json():
    logging.debug('---list_marketing_images_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list = []
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    logger.debug('logged_in_merchant_user=%s', logged_in_merchant_user)
    
    db_client = create_db_client(caller_info="list_marketing_images_json")
    
    try:
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            images_list = MarketingImage.list_by_merchant_acct(merchant_acct)
            
            for image in images_list:
                data_list.append({
                                "code"      : image.image_file_public_url,
                                "label"     : image.image_label,
                                'image_url' : image.image_file_public_url,
                                })
            
    except:
        logger.error('Fail to list marketing image due to %s', get_tracelog())
    
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_FIVE_MINUTE,
                                  )
    
    return resp  

@system_bp.route('/list-product-package', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_product_package_code_json(request_language):
    logging.debug('---list_product_package_code_json--- ')
    data_list = get_product_package_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-loyalty-package', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_loyalty_package_code_json(request_language):
    logging.debug('---list_loyalty_package_code_json--- ')
    data_list = get_loyalty_package_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-pos-package', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_pos_package_code_json(request_language):
    logging.debug('---list_pos_package_code_json--- ')
    data_list = get_pos_package_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/list-loyalty-package-feature/package/<package_code>', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_loyalty_package_feature_code_json(request_language, package_code):
    logging.debug('---list_package_feature_code_json--- ')
    
    data_list = get_loyalty_package_feature_by_group_value_json(request_language, package_code)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/config.js', methods=['GET'])
#@cache.cached(timeout=60)
def config():
    logger.debug('############################### config ############################### ')
    
    logger.debug('g = %s ', current_app.config['version_no'])
    
    logged_in_merchant_user           = get_loggedin_merchant_user_account()
    is_merchant_user        = session.get('is_merchant_user') if session else False
    currency_code           = conf.DEFAULT_CURRENCY_CODE
    
    logger.debug('is_merchant_user=%s', is_merchant_user)
    
    if is_merchant_user:
        logger.debug('going to get currency code from merchant user')
        db_client                   = create_db_client(caller_info="config")
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            currency_code   = merchant_acct.currency_code
    else:
        logger.debug('not merchant user')
        
    logger.debug('default currency_code=%s', currency_code)
                
    currency_details    = get_currency_config(currency_code)
    
    
    logger.debug('currency_details=%s', currency_details)
    
    config_dict = {
                    "DASHBOARD_URL"             : url_for('admin_bp.dashboard_page'),
                    "SIGNIN_URL"                : SIGNIN_URL,
                    "LOADING_TEXT"              : gettext('Please wait, your request are processing now'), 
                    "currency"                  : currency_details,
                    
                    
                    }
    
    
    return render_template("system/config.js", **config_dict)



@system_bp.route('/js-i18n.js', methods=['GET'])
def javascript_i18n_message():
    logging.debug('---javascript_i18n_message--- ')
    return render_template("i18n/js_message.js")

@system_bp.route('/contact-us', methods=['post'])
def contact_us_post():
    logging.debug('--- submit contact_us data ---')
    contact_us_data = request.form
    
    logging.debug('contact_us_data=%s', contact_us_data)
    
    contact_us_form = ContactUsForm(contact_us_data)
    to_send_email = False
    
    
    try:
        if contact_us_form.validate():
            was_once_logged_in  = session.get('was_once_logged_in')
            logged_in_user = session.get('logged_in_user')
            
            logger.debug('logged_in_user=%s', logged_in_user)
            
            db_client = create_db_client(caller_info="contact_us_post")
            
            try:
                name    = contact_us_form.name.data
                email   = contact_us_form.email.data
                
                if was_once_logged_in:
                    name    = logged_in_user.get('name')
                    email   = logged_in_user.get('email')
                    
                    
                if is_not_empty(email) and is_valid_email(email):    
                    to_send_email = True
                    with db_client.context():
                        ContactUs.create(
                                    contact_name        = name,
                                    contact_email       = email,
                                    contact_subject     = contact_us_form.subject.data,
                                    contact_message     = contact_us_form.message.data
                                    )
                
                    contact_us_subject = 'Contact-Us Subject: %s' % contact_us_form.subject.data
            
            except:
                logging.error('Failed to create contact due to %s', get_tracelog())
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)

            if to_send_email:
                send_email(sender           = DEFAULT_SENDER, 
                               to_address   = [DEFAULT_RECIPIENT_EMAIL], 
                               subject      = contact_us_subject, 
                               body         = contact_us_form.message.data,
                               cc_address   = [contact_us_form.email.data],
                               app          = current_app
                               )
                    
            return create_rest_message('Thank you, we will contact you shortly', status_code=StatusCode.OK)
            #return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = contact_us_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to contact us due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@system_bp.route('/send-email', methods=['post'])
#@csrf.exempt
def send_email_post():
    logger.info('--- submit send_email_post data ---')
    send_email_data = request.get_json() 
    
    logger.info('send_email_data=%s', send_email_data)
    
    #send_email_form = SendEmailForm(send_email_data)
    sender_address      = send_email_data.get('sender_address')
    recipient_address   = send_email_data.get('recipient_address')
    subject             = send_email_data.get('subject')
    message             = send_email_data.get('message')
    cc_address          = send_email_data.get('cc_address')
    
    try:
        if is_not_empty(sender_address) and is_not_empty(recipient_address) and is_not_empty(subject) and is_not_empty(message):
            cc_address_list = []
            if is_not_empty(cc_address):
                cc_address_list [cc_address]
                
            send_email(sender       = sender_address, 
                       to_address   = [recipient_address], 
                       subject      = subject, 
                       body         = message,
                       cc_address   = cc_address_list,
                       app          = current_app
                       )
                    
            return create_rest_message('Email have been sent', status_code=StatusCode.OK)
            #return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            #error_message = send_email_form.create_rest_return_error_message()
            error_message = 'Invalid email data'
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to send email due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    

@system_bp.route('/feedback', methods=['GET'])
def feedback_form():
    logging.debug('---feedback_form--- ')
    return render_template("system/feedback_form_content.html")

@system_bp.route('/full-modal-example', methods=['GET'])
def full_modal_example():
    return render_template("test/full_modal_example_content.html")
    
@system_bp.route('/feedback', methods=['post'])
def feedback_form_post():
    logging.debug('--- submit feedback_post data ---')
    feedback_data = request.form
    
    logging.debug('feedback_data=%s', feedback_data)
    
    feedback_form = FeedbackForm(feedback_data)
    
    try:
        if feedback_form.validate():
            
            
            db_client = create_db_client(caller_info="feedback_post")
            with db_client.context():
                try:
                    Feedback.create(
                                    name            = feedback_form.name.data,
                                    email           = feedback_form.email.data,
                                    rating          = feedback_form.rating.data,
                                    message         = feedback_form.message.data
                                    )
                    
                    return create_rest_message('Thank you for you feedback', status_code=StatusCode.OK)
                
                except:
                    logging.error('Failed to create contact due to %s', get_tracelog())
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = feedback_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to submit feedback due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    



@system_bp.route('/list-support-currency', methods=['GET'])
def list_currency_details():
    logging.debug('---list_currency_details--- ')
    currency_json_list      = get_currency_json()
    return jsonify(currency_json_list)


@system_bp.route('/currency-details/<currency_code>', methods=['GET'])
def get_target_currency_details(currency_code):
    logging.debug('---get_target_currency_details--- ')
    currency_json_list      = get_currency_json()
    target_currency_json    = {}
    if currency_code:
        for currency_json in currency_json_list:
            if currency_json.get('code') == currency_code:
                target_currency_json = currency_json
                break
    else:
        target_currency_json = currency_json_list
    return jsonify(target_currency_json)

@system_bp.route('/list-merchant-tagging', methods=['GET'])
#@cache.cached(timeout=50)
def list_merchant_tagging():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="list_merchant_tagging")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        __merchant_tag_list     = MerchantTagging.list_by_merchant_account(merchant_acct)
        
        if __merchant_tag_list:
            for mt in __merchant_tag_list:
                data_list.append({
                        "code"  : mt.label,
                        "label" : mt.label,
                        })
                
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp 

@system_bp.route('/list-granted-outlet', methods=['GET'])
def list_granted_outlet():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="list_granted_outlet")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        __outlet_list   = Outlet.list_by_merchant_acct(merchant_acct)
        is_admin_user   = logged_in_merchant_user.get('is_admin')
        granted_outlet  = logged_in_merchant_user.get('granted_outlet')
        
        if __outlet_list:
            for m in __outlet_list:
                if is_admin_user:
                    data_list.append({
                                        'code'  : m.key_in_str,
                                        'label' : m.name,
                                        })
                else:
                    if m.key_in_str in granted_outlet:
                        data_list.append({
                                        'code'  : m.key_in_str,
                                        'label' : m.name,
                                        })
                
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp




    

@system_bp.route('/list-outlet-code', methods=['GET'])
def list_merchant_outlet_code():
    data_list_in_json  = json.dumps(get_merchant_outlet_code(), sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp

@system_bp.route('/list-promotion-code', methods=['GET'])
def list_merchant_promotion_code():
    data_list_in_json  = json.dumps(get_merchant_promotion_code(), sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp

@system_bp.route('/list-loyalty-device-activation-code', methods=['GET'])
def list_merchant_loyalty_device_activation_code():
    data_list_in_json  = json.dumps(get_loyalty_device_activation_code(), sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp

@system_bp.route('/list-dinning-option-code', methods=['GET'])
def list_merchant_dinning_option_code():
    data_list_in_json  = json.dumps(get_merchant_dinning_option_code(), sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp

@system_bp.route('/list-giveaway-program', methods=['GET'])
def list_giveaway_program():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="list_merchant_tagging")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        giveaway_program_list   = merchant_acct.manual_giveaway_reward_program_list
        
        for program in giveaway_program_list:
            
            data_list.append({
                                        'code'  : program.get('program_key'),
                                        'label' : program.get('desc'),
                                        })
                
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  
                                  )
    
    return resp

@system_bp.route('/list-valid-giveaway-program', methods=['GET'])
def list_valid_giveaway_program():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="list_valid_giveaway_program")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        giveaway_program_list   = merchant_acct.manual_giveaway_reward_program_list
        today = datetime.today().date()
        for program in giveaway_program_list:
            program_start_date_str      = program.get('start_date')
            program_end_date_str        = program.get('end_date')
            program_start_date          = datetime.strptime(program_start_date_str, '%d-%m-%Y').date()
            program_end_date            = datetime.strptime(program_end_date_str, '%d-%m-%Y').date()
            if today<=program_end_date and program_start_date<=today:
                data_list.append({
                                        'code'      : program.get('program_key'),
                                        'label'     : program.get('label') or truncate_if_max_length(program.get('desc'), 100),
                                        'start_date': program.get('start_date'),
                                        'end_date'  : program.get('end_date'),
                                        })
                
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  
                                  )
    
    return resp  

@system_bp.route('/list-merchant-joined-year-code', methods=['GET'])
def list_merchant_joined_year_code_json():
    logging.debug('---list_merchant_joined_year_code_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="list_merchant_tagging")
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        start_joined_year   = merchant_acct.plan_start_date.year
    
    today       = datetime.today()
    this_year   = today.year
    data_list   = []
    for year in range(start_joined_year, this_year):
        data_list.append({
                                        'code'  : year,
                                        'label' : year,
                                        })
    data_list_in_json  = json.dumps(data_list, sort_keys = True, separators = (',', ': '))
                
    resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  
                                  )
    
    return resp        

@system_bp.route('/list-business-type-code', methods=['GET'])
@cache.cached(timeout=600)
@request_language
def list_business_type_json(request_language):
    logging.debug('---list_business_type_json--- ')
    data_list = get_merchant_business_type_json(request_language)
    
    return list_csv_code_label_json(data_list)

@system_bp.route('/merchant-logo-url/<merchant_act_key>', methods=['GET'])
def merchant_logo_image_url(merchant_act_key):
    db_client = create_db_client(caller_info="list_merchant_tagging")
    with db_client.context():
        merchant_acct       = MerchantAcct.fetch(merchant_act_key)
        
        logo_image_url = merchant_acct.logo_public_url
        
    return redirect(logo_image_url)
  