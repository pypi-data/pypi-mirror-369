'''
Created on 19 Jul 2022

@author: jacklok
'''
import csv, os, json, logging
from trexlib.utils.common.common_util import sort_dict_list
from trexadmin.conf import DEFAULT_LANGUAGE
from trexweb.utils.common.http_response_util import MINE_TYPE_JSON,\
    create_cached_response
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_preferred_language
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import Outlet, MerchantAcct
from trexmodel.models.datastore.pos_models import DinningOption
from trexconf.conf import AGE_TIME_ONE_HOUR
from trexlib.utils.string_util import is_not_empty
from flask.globals import session
from trexmodel.program_conf import LOYALTY_PACKAGE_LITE
from pytz import country_timezones
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexconf import conf
from trexmodel.models.datastore.merchant_promotion_models import MerchantPromotionCode

COUNTRY_CODE_FILEPATH                       = os.path.abspath(os.path.dirname(__file__)) + '/data/countries.csv'

CURRENCY_CODE_FILEPATH                      = os.path.abspath(os.path.dirname(__file__)) + '/data/currency.csv' 

ADMIN_PERMISSION_CODE_FILEPATH              = os.path.abspath(os.path.dirname(__file__)) + '/data/admin_permission.csv'

MERCHANT_PERMISSION_CODE_FILEPATH           = os.path.abspath(os.path.dirname(__file__)) + '/data/merchant_permission.csv'

REWARD_BASE_CODE_FILEPATH                   = os.path.abspath(os.path.dirname(__file__)) + '/data/reward_base.csv'
REWARD_FORMAT_CODE_FILEPATH                 = os.path.abspath(os.path.dirname(__file__)) + '/data/reward_format.csv'
REWARD_BASE_AND_FORMAT_MAPPING_FILEPATH     = os.path.abspath(os.path.dirname(__file__)) + '/data/reward_base_and_reward_format_mapping.csv'
PROGRAM_STATUS_FILEPATH                     = os.path.abspath(os.path.dirname(__file__)) + '/data/program_status.csv'
MERCHANT_NEWS_STATUS_FILEPATH               = os.path.abspath(os.path.dirname(__file__)) + '/data/merchant_news_status.csv'

VOUCHER_STATUS_FILEPATH                     = os.path.abspath(os.path.dirname(__file__)) + '/data/voucher_status.csv'
VOUCHER_TYPE_FILEPATH                       = os.path.abspath(os.path.dirname(__file__)) + '/data/voucher_type.csv'

REDEMPTION_CATALOGUE_STATUS_FILEPATH        = os.path.abspath(os.path.dirname(__file__)) + '/data/redemption_catalogue_status.csv'

REDEEM_LIMIT_TYPE_FILEPATH                  = os.path.abspath(os.path.dirname(__file__)) + '/data/redeem_limit_type.csv'

REWARD_EFFECTIVE_TYPE_FILEPATH              = os.path.abspath(os.path.dirname(__file__)) + '/data/reward_effective_type.csv'
REWARD_EXPIRATION_TYPE_FILEPATH             = os.path.abspath(os.path.dirname(__file__)) + '/data/reward_expiration_type.csv'

REWARD_USE_CONDITION_FILEPATH               = os.path.abspath(os.path.dirname(__file__)) + '/data/reward_use_condition.csv'
WEEKDAY_FILEPATH                            = os.path.abspath(os.path.dirname(__file__)) + '/data/weekday.csv'

MEMBERSHIP_EXPIRATION_TYPE_FILEPATH         = os.path.abspath(os.path.dirname(__file__)) + '/data/membership_expiration_type.csv'

MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_FILEPATH      = os.path.abspath(os.path.dirname(__file__)) + '/data/membership_entitle_qualification_type.csv'  
MEMBERSHIP_UPGRADE_EXPIRY_TYPE_FILEPATH             = os.path.abspath(os.path.dirname(__file__)) + '/data/membership_upgrade_expiry_type.csv'

GIVEAWAY_METHOD_FILEPATH                            = os.path.abspath(os.path.dirname(__file__)) + '/data/giveaway_method.csv'
GIVEAWAY_SYSTEM_CONDITION_FILEPATH                  = os.path.abspath(os.path.dirname(__file__)) + '/data/giveaway_system_condition.csv'

BARCODE_TYPE_FILEPATH                               = os.path.abspath(os.path.dirname(__file__)) + '/data/barcode_type.csv'

BIRTHDAY_REWARD_GIVEAWAY_TYPE_FILEPATH              = os.path.abspath(os.path.dirname(__file__)) + '/data/birthday_reward_giveaway_type.csv'

ENTITLE_REWARD_CONDITION_FILEPATH                   = os.path.abspath(os.path.dirname(__file__)) + '/data/entitle_reward_condition.csv'

RUNNING_NO_GENERATOR_FILEPATH                       = os.path.abspath(os.path.dirname(__file__)) + '/data/invoice_no_generator.csv'

RECEIPT_HEADER_DATA_TYPE_FILEPATH                   = os.path.abspath(os.path.dirname(__file__)) + '/data/receipt_header_data_type.csv'

RECEIPT_FOOTER_DATA_TYPE_FILEPATH                   = os.path.abspath(os.path.dirname(__file__)) + '/data/receipt_footer_data_type.csv'

PRODUCT_PACKAGE_FILEPATH                            = os.path.abspath(os.path.dirname(__file__)) + '/data/product_package.csv'

LOYALTY_PACKAGE_FILEPATH                            = os.path.abspath(os.path.dirname(__file__)) + '/data/loyalty_package.csv'

POS_PACKAGE_FILEPATH                                = os.path.abspath(os.path.dirname(__file__)) + '/data/pos_package.csv'

LOYALTY_PACKAGE_FEATURE_FILEPATH                    = os.path.abspath(os.path.dirname(__file__)) + '/data/loyalty_package_feature.csv'

REDEEM_REWARD_FORMAT_CODE_FILEPATH                  = os.path.abspath(os.path.dirname(__file__)) + '/data/redeem_reward_format.csv'

PUSH_NOTIFICATION_CONTENT_TYPE_CODE_FILEPATH        = os.path.abspath(os.path.dirname(__file__)) + '/data/push_notification_content_type.csv'


INDUSTRY_TYPE_FILEPATH                              = os.path.abspath(os.path.dirname(__file__)) + '/data/industry.csv'

MERCHANT_PARTNERSHIP_STATUS_FILEPATH                = os.path.abspath(os.path.dirname(__file__)) + '/data/merchant_partnership_status.csv'

MERCHANT_PARTNERSHIP_LIMIT_REDEEM_TYPE_FILEPATH     = os.path.abspath(os.path.dirname(__file__)) + '/data/partnership_limit_redeem_type.csv'

BUSINESS_TYPE_FILEPATH                              = os.path.abspath(os.path.dirname(__file__)) + '/data/business_type.csv'

RESTAURANT_RATING_TYPE_FILEPATH                     = os.path.abspath(os.path.dirname(__file__)) + '/data/restaurant_rating_type.csv'
RETAIL_RATING_TYPE_FILEPATH                         = os.path.abspath(os.path.dirname(__file__)) + '/data/retail_rating_type.csv'

logger = logging.getLogger('helper')


def map_label_by_code(code_label_json, code):
    for rb in code_label_json:
        if rb.get('code')==code:
            return rb.get('label')

def get_country_json():
    countries_list = []
    
    with open(COUNTRY_CODE_FILEPATH) as csv_file:
        logging.debug('Found country data file')
        data        = csv.reader(csv_file, delimiter=',')
        first_line  = True
        
        for column in data:
            if not first_line:
                try:
                    countries_list.append({
                    "code": column[0],
                    "label": column[1],
                    'timezone': ",".join(country_timezones(column[0])),
                    })
                except:
                    logger.error('Failed to get timezones for %s', column[1])
            else:
                first_line = False
    
    return sort_dict_list(countries_list, sort_attr_name='label')

def get_country_timezone_list_json(country_code):
    timezone_list = []
    for tz in country_timezones(country_code):
        timezone_list.append({
                        'code': tz,
                        'label': tz,
            })
    return timezone_list;
    
def get_currency_json():
    data_list = []
    
    with open(CURRENCY_CODE_FILEPATH) as csv_file:
        logging.debug('Found currency data file')
        data        = csv.reader(csv_file, delimiter=',')
        first_line  = True
        
        
        
        for column in data:
            if not first_line:
                data_list.append({
                    "code": column[0],
                    "label": column[1],
                    "currency_label": column[2],
                    "floating_point": column[3],
                    "decimal_separator": column[4],
                    "thousand_separator": column[5],
                    })
            else:
                first_line = False
    
    return sort_dict_list(data_list, sort_attr_name='label')


def get_reward_format_label(reward_format, locale):
    reward_format_list = get_reward_format_json(locale)
    for rf in reward_format_list:
        if reward_format==rf.get('code'):
            return rf.get('label')
        
def get_product_code_label(product_code, locale):
    product_package_json = get_product_package_json(locale)
    
    for p in product_package_json:
        if p.get('code') == product_code:
            return p.get('label')
    
    
        
def get_loyalty_package_label(account_package, locale):
    loyalty_package_list = get_loyalty_package_json(locale)
    for rf in loyalty_package_list:
        if account_package==rf.get('code'):
            return rf.get('label')
        
def get_pos_package_label(account_package, locale):
    pos_package_list = get_pos_package_json(locale)
    for rf in pos_package_list:
        if account_package==rf.get('code'):
            return rf.get('label')                        

def get_csv_code_label_in_json(csv_file, locale, extract_all_by_header=False, group_value=None):
    
    logger.debug('get_csv_json: locale=%s', locale)
    
    data_list = []
    
    if locale is None:
        locale = DEFAULT_LANGUAGE
    
    header_list         = ['code', 'label', 'locale', 'group']
    locale_column_index = 2
    group_column_index  = 3
    
    logger.debug('group_value=%s', group_value)
    
    with open(csv_file) as csv_file:
        data        = csv.reader(csv_file, delimiter=',')
        
        first_line  = True
        
        for column in data:
            logger.debug('column=%s', column)
            
            if not first_line:
                
                if locale==column[locale_column_index].strip():
                    if not column[0].startswith('-'):
                        
                        if extract_all_by_header:
                            data_dict = {}
                            
                            if is_not_empty(group_value):
                                
                                if column[group_column_index] == group_value:
                                    
                                    for i in range(len(header_list)):
                                        data_dict[header_list[i]] = column[i]
                                    data_list.append(data_dict)
                                
                            else:
                                for i in range(len(header_list)):
                                    data_dict[header_list[i]] = column[i]
                                data_list.append(data_dict)
                        
                        else:
                            
                            if is_not_empty(group_value):
                                if column[group_column_index] == group_value:
                                    data_list.append({
                                            header_list[0]: column[0],
                                            header_list[1]: column[1],
                                            })
                            else:
                                data_list.append({
                                            header_list[0]: column[0],
                                            header_list[1]: column[1],
                                            })
                                
            else:
                if extract_all_by_header:
                    header_list = column
                
                column_index = 0
                for column in header_list:
                    if column == 'locale':
                        locale_column_index = column_index
                        
                    if column == 'group':
                        group_column_index = column_index    
                    
                    column_index+=1    
                
                logger.debug('locale_column_index=%d', locale_column_index)
                logger.debug('group_column_index=%d', group_column_index)
                
                first_line = False
    
    
    logger.debug('data_list=%s', data_list)
    
    return sort_dict_list(data_list, sort_attr_name='code')

def get_admin_permission_json(locale):
    
    logger.debug('get_admin_permission_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(ADMIN_PERMISSION_CODE_FILEPATH, locale)

def get_merchant_permission_json(locale):
    
    logger.debug('get_merchant_permission_list: locale=%s', locale)
    
    return get_csv_code_label_in_json(MERCHANT_PERMISSION_CODE_FILEPATH, locale)

def get_reward_base_json(locale, group_value=None):
    
    logger.debug('get_reward_base_json: locale=%s', locale)
    
    if group_value is None:
        group_value = get_loyalty_package_value()
    
    return get_csv_code_label_in_json(REWARD_BASE_CODE_FILEPATH, locale, group_value=group_value)

def get_reward_format_json(locale, group_value=None):
    
    logger.debug('get_reward_format_json: locale=%s', locale)
    
    if group_value is None:
        group_value = get_loyalty_package_value()
    
    return get_csv_code_label_in_json(REWARD_FORMAT_CODE_FILEPATH, locale, group_value=group_value)

def get_program_status_json(locale):
    
    logger.debug('get_program_status_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(PROGRAM_STATUS_FILEPATH, locale)

def get_merchant_news_status_json(locale):
    
    logger.debug('get_merchant_news_status_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(MERCHANT_NEWS_STATUS_FILEPATH, locale)

def get_redemption_catalogue_status_json(locale):
    
    logger.debug('get_redemption_catalogue_status_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REDEMPTION_CATALOGUE_STATUS_FILEPATH, locale)

def get_voucher_status_json(locale):
    
    logger.debug('get_voucher_status_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(VOUCHER_STATUS_FILEPATH, locale)

def get_voucher_type_json(locale):
    
    logger.debug('get_voucher_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(VOUCHER_TYPE_FILEPATH, locale)

def get_redeem_limit_type_json(locale):
    
    logger.debug('get_redeem_limit_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REDEEM_LIMIT_TYPE_FILEPATH, locale)


def get_reward_effective_type_json(locale):
    
    logger.debug('get_reward_effective_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REWARD_EFFECTIVE_TYPE_FILEPATH, locale)

def get_reward_expiration_type_json(locale):
    
    logger.debug('get_reward_expiration_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REWARD_EXPIRATION_TYPE_FILEPATH, locale)

def get_membership_expiration_type_json(locale):
    
    logger.debug('get_membership_expiration_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(MEMBERSHIP_EXPIRATION_TYPE_FILEPATH, locale)

def get_membership_entitle_qualification_type_json(locale):
    
    logger.debug('get_membership_entitle_qualification_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_FILEPATH, locale)

def get_membership_upgrade_expiry_type_json(locale):
    
    logger.debug('get_membership_upgrade_expiry_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(MEMBERSHIP_UPGRADE_EXPIRY_TYPE_FILEPATH, locale)


def get_reward_use_condition_json(locale):
    
    logger.debug('get_reward_use_condition_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REWARD_BASE_CODE_FILEPATH, locale)

def get_weekday_json(locale):
    
    logger.debug('get_weekday_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REWARD_BASE_CODE_FILEPATH, locale)

def get_giveaway_method_json(locale):
    
    logger.debug('get_giveaway_method_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(GIVEAWAY_METHOD_FILEPATH, locale)

def get_giveaway_system_condition_json(locale):
    
    logger.debug('get_giveaway_system_condition_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(GIVEAWAY_SYSTEM_CONDITION_FILEPATH, locale)

def get_industry_type_json(locale):
    
    logger.debug('get_industry_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(INDUSTRY_TYPE_FILEPATH, locale)

def get_merchant_partnership_status_type_json(locale):
    
    logger.debug('get_merchant_partnership_status_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(MERCHANT_PARTNERSHIP_STATUS_FILEPATH, locale)

def get_merchant_partnership_limit_redeem_type_json(locale):
    
    logger.debug('get_merchant_partnership_status_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(MERCHANT_PARTNERSHIP_LIMIT_REDEEM_TYPE_FILEPATH, locale)


def get_merchant_business_type_json(locale):
    
    logger.debug('get_merchant_business_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(BUSINESS_TYPE_FILEPATH, locale)

def get_restaurant_rating_type_json(locale):
    
    logger.debug('get_restaurant_rating_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(RESTAURANT_RATING_TYPE_FILEPATH, locale)

def get_retail_rating_type_json(locale):
    
    logger.debug('get_retail_rating_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(RETAIL_RATING_TYPE_FILEPATH, locale)



def get_csv_code_label_in_list(csv_file, locale):
    
    logger.debug('get_csv_code_label_in_list: locale=%s', locale)
    
    data_list = []
    
    if locale is None:
        locale = DEFAULT_LANGUAGE
    
    with open(csv_file) as csv_file:
        logger.debug('Found csv data file')
        data        = csv.reader(csv_file, delimiter=',')
        first_line  = True
        
        for column in data:
            
            if not first_line:
                logger.debug('%d - %s', len(column), column)
                if not column[0].startswith('-'):
                    data_list.append((column[0],column[1]))
            else:
                first_line = False
    
    
    logger.debug('data_list=%s', data_list)
    
    return data_list

def get_admin_permission_list(locale):
    
    logger.debug('get_admin_permission_list: locale=%s', locale)
    
    return get_csv_code_label_in_list(ADMIN_PERMISSION_CODE_FILEPATH, locale)
    
def get_merchant_permission_list(locale):
    
    logger.debug('get_merchant_permission_list: locale=%s', locale)
    
    return get_csv_code_label_in_list(MERCHANT_PERMISSION_CODE_FILEPATH, locale)

def get_reward_base_list(locale):
    
    logger.debug('get_reward_base_list: locale=%s', locale)
    
    return get_csv_code_label_in_list(REWARD_BASE_CODE_FILEPATH, locale)

def get_reward_form_list(locale):
    
    logger.debug('get_reward_form_list: locale=%s', locale)
    
    return get_csv_code_label_in_list(REWARD_BASE_CODE_FILEPATH, locale)

def get_currency_list():
    
    currency_list = []
    
    with open(CURRENCY_CODE_FILEPATH) as csv_file:
        logging.debug('Found currency data file')
        data        = csv.reader(csv_file, delimiter=',')
        first_line  = True
        
        for column in data:
            if not first_line:
                currency_list.append((column[0],column[1]))
            else:
                first_line = False
    
    
    logger.debug('currency_list=%s', currency_list)
    
    return currency_list

def get_currency_config(currency_code):
    currency_json_list = get_currency_json()
    
    logger.debug('currency_json_list=%s', currency_json_list)
    for currency_json in currency_json_list:
        if currency_json.get('code') == currency_code:
            return currency_json
        
def get_reward_base_and_reward_format_mapping():
    data_list = []
    
    with open(REWARD_BASE_AND_FORMAT_MAPPING_FILEPATH) as csv_file:
        logging.debug('Found reward base and reward format mapping data file')
        data        = csv.reader(csv_file, delimiter=',')
        first_line  = True
        
        
        
        for column in data:
            if not first_line:
                if not column[0].startswith('-'):
                    data_list.append({
                        "reward_base": column[0],
                        "reward_format": column[1],
                        })
            else:
                first_line = False
    
    return data_list        

def get_barcode_type_json(locale):
    
    logger.debug('get_barcode_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(BARCODE_TYPE_FILEPATH, locale)

def get_running_no_generator_json(locale):
    
    logger.debug('get_running_no_generator_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(RUNNING_NO_GENERATOR_FILEPATH, locale)

def get_receipt_header_data_type_json(locale):
    
    logger.debug('get_receipt_header_data_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(RECEIPT_HEADER_DATA_TYPE_FILEPATH, locale)

def get_receipt_footer_data_type_json(locale):
    
    logger.debug('get_receipt_footer_data_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(RECEIPT_FOOTER_DATA_TYPE_FILEPATH, locale, extract_all_by_header=True)


def get_birthday_reward_giveaway_type_form_list(locale):
    
    logger.debug('get_birthday_reward_giveaway_type_form_list: locale=%s', locale)
    
    return get_csv_code_label_in_json(BIRTHDAY_REWARD_GIVEAWAY_TYPE_FILEPATH, locale)

def get_entitle_reward_condition_list(locale):
    
    logger.debug('get_entitle_reward_condition_list: locale=%s', locale)
    
    return get_csv_code_label_in_json(ENTITLE_REWARD_CONDITION_FILEPATH, locale)

def get_redeem_reward_format_json(locale):
    
    logger.debug('get_redeem_reward_format_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(REDEEM_REWARD_FORMAT_CODE_FILEPATH, locale)

def get_push_notification_content_type_json(locale):
    
    logger.debug('get_push_notification_content_type_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(PUSH_NOTIFICATION_CONTENT_TYPE_CODE_FILEPATH, locale)

def get_push_notification_content_type_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_push_notification_content_type_json(preferred_language)
        
        return map_label_by_code(code_label_json, code)
    else:
        return ''


def list_csv_code_label_json(code_label_json):
    logger.debug('---list_csv_code_label_json--- ')
    
    
    filtered_data_json_list = []
    
    for d in code_label_json:
        if d.get('code').startswith('-'):
            continue
        else:
            filtered_data_json_list.append(d)
    
    filtered_data_json_list          = json.dumps(filtered_data_json_list, sort_keys = True, separators = (',', ': '))
    
    resp = create_cached_response(filtered_data_json_list, 
                                  mime_type             = MINE_TYPE_JSON, 
                                  max_age_in_seconds    = AGE_TIME_ONE_HOUR
                                  )
    
    return resp

def get_product_package_json(locale):
    
    logger.debug('get_product_package_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(PRODUCT_PACKAGE_FILEPATH, locale)

def get_loyalty_package_json(locale):
    
    logger.debug('get_loyalty_package_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(LOYALTY_PACKAGE_FILEPATH, locale)

def get_pos_package_json(locale):
    
    logger.debug('get_pos_package_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(POS_PACKAGE_FILEPATH, locale)


def get_loyalty_package_feature_json(locale):
    
    logger.debug('get_loyalty_package_feature_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(LOYALTY_PACKAGE_FEATURE_FILEPATH, locale)

def get_loyalty_package_feature_by_group_value_json(locale, group_value):
    
    logger.debug('get_loyalty_package_feature_by_group_value_json: locale=%s', locale)
    
    return get_csv_code_label_in_json(LOYALTY_PACKAGE_FEATURE_FILEPATH, locale, group_value=group_value)


def get_merchant_outlet_code():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="get_merchant_outlet_code")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        __outlet_list   = Outlet.list_by_merchant_acct(merchant_acct)
        
        if __outlet_list:
            for m in __outlet_list:
                data_list.append({
                                        'code'  : m.key_in_str,
                                        'label' : m.name,
                                        })
                
    return data_list

def get_merchant_promotion_code():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="get_merchant_promotion_code")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        __promotion_codes_list   = MerchantPromotionCode.list_by_merchant_account(merchant_acct)
        
        if __promotion_codes_list:
            for m in __promotion_codes_list:
                data_list.append({
                                        'code'  : m.label,
                                        'label' : m.label,
                                        })
                
    return data_list

def get_merchant_dinning_option_code():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="get_merchant_dinning_option_code")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        __data_list   = DinningOption.list_by_merchant_acct(merchant_acct)
        
        if __data_list:
            for m in __data_list:
                data_list.append({
                                        'code'  : m.key_in_str,
                                        'label' : m.name,
                                        })
                
    return data_list

def get_loyalty_package_value():
    group_value = LOYALTY_PACKAGE_LITE
    merchant_acct_details = session.get('merchant_acct_details')
    
    logger.debug('merchant_acct_details=%s', merchant_acct_details)
    
    if merchant_acct_details:
        account_plan    = merchant_acct_details.get('account_plan')
        if account_plan:
            loyalty_package = account_plan.get('loyalty_package')
            if loyalty_package:
                group_value = loyalty_package
                
    return group_value

def get_loyalty_device_activation_code():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    data_list               = []
    
    db_client = create_db_client(caller_info="get_loyalty_device_activation_code")
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        __loyalty_activation_list   = LoyaltyDeviceSetting.list_by_merchant_account(merchant_acct, limit=conf.MAX_FETCH_RECORD)
        
        if __loyalty_activation_list:
            for m in __loyalty_activation_list:
                data_list.append({
                                        'code'  : m.activation_code,
                                        'label' : m.device_name,
                                        #'group' : m.assigned_outlet_key,
                                        })
                
    return data_list

