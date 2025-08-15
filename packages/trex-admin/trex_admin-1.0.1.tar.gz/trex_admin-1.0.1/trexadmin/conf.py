'''
Created on 18 Sep 2020

@author: jacklok
'''
import logging, os, config_path 
from trexconf.conf import DEPLOYMENT_MODE, PRODUCTION_MODE, DEMO_MODE, LOCAL_MODE
from trexlib.utils.common.config_util import read_config

logger = logging.getLogger('debug')

CREDENTIAL_CONFIG                           = read_config('credential_config.txt')

APPLICATION_NAME                            = os.environ.get('APPLICATION_NAME')
APPLICATION_TITLE                           = os.environ.get('APPLICATION_TITLE')
APPLICATION_DESC                            = os.environ.get('APPLICATION_DESC')
APPLICATION_HREF                            = os.environ.get('APPLICATION_HREF')
APPLICATION_BASE_URL                        = os.environ.get('APPLICATION_BASE_URL')
WEBSITE_BASE_URL                            = os.environ.get('WEBSITE_BASE_URL')
IMAGE_BASE_URL                              = os.environ.get('IMAGE_BASE_URL')
IMPORT_BASE_URL                             = os.environ.get('IMPORT_BASE_URL')
IMAGE_PROD_BASE_URL                         = os.environ.get('IMAGE_PROD_BASE_URL')
REFER_BASE_URL                              = os.environ.get('REFER_BASE_URL')
MOBILE_APP_PLAY_STORE_URL                   = os.environ.get('PLAY_STORE_URL')
MOBILE_APP_ITUNES_STORE_URL                 = os.environ.get('APPLE_STORE_URL')
MOBILE_APP_HUAWEI_GALERY_URL                = os.environ.get('HUAWEI_STORE_URL')
MOBILE_APP_INSTALL_URL                      = os.environ.get('INSTALL_APP_URL')
DOWNLOAD_URL                                = os.environ.get('DOWNLOAD_URL')


EMAIL_EXPIRY_LENGTH_IN_MINUTE               = os.environ.get('EMAIL_EXPIRY_LENGTH_IN_MINUTE')
MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE        = os.environ.get('MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE')

INSTANT_REWARD_CUSTOM_URL                   = os.environ.get('INSTANT_REWARD_CUSTOM_URL')

REFER_A_FRIEND_CUSTOM_URL                   = os.environ.get('REFER_A_FRIEND_CUSTOM_URL')

#SIGNIN_URL                                  = 'http://localhost:8082/sec/signin'

TASK_BASE_URL                               = os.environ.get('TASK_BASE_URL')

DEBUG_MODE                                  = os.environ.get('DEBUG_MODE')

APPLICATION_SHOW_DASHBOARD_MESSAGE          = False
APPLICATION_SHOW_DASHBOARD_NOTIFICATION     = False


PAYMENT_GATEWAY_APP_KEY                     = ''
PAYMENT_GATEWAY_SECRET_KEY                  = ''

STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE     = os.environ.get('STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE')
STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE  = os.environ.get('STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE')

STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST     = os.environ.get('STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST')
STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST  = os.environ.get('STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST') 


CSRF_ENABLED                                        = True

CONTENT_WITH_JAVASCRIPT_LINK                        = True
 
APPLICATION_VERSION_NO                              = os.environ.get('APPLICATION_VERSION_NO')

DEFAULT_LANGUAGE                                    = 'en_us'

GCLOUD_PROJECT_ID                                   = os.environ.get('GCLOUD_PROJECT_ID')

SUPERUSER_ID                                        = CREDENTIAL_CONFIG.get('SUPERUSER_ID')
SUPERUSER_EMAIL                                     = CREDENTIAL_CONFIG.get('SUPERUSER_EMAIL')
SUPERUSER_HASHED_PASSWORD                           = CREDENTIAL_CONFIG.get('SUPERUSER_HASHED_PASSWORD')


WHATSAPP_TOKEN                                      = os.environ.get('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID                            = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_VERIFY_TOKEN                               = os.environ.get('WHATSAPP_VERIFY_TOKEN')
FACEBOOK_API_VERSION                                = os.environ.get('FACEBOOK_API_VERSION')

STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH                = os.environ['CLOUD_STORAGE_SERVICE_ACCOUNT_KEY']
STORAGE_CREDENTIAL_PATH                             = os.path.abspath(os.path.dirname(__file__)) + '/json/' + STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH
CLOUD_STORAGE_BUCKET                                = os.environ.get('CLOUD_STORAGE_BUCKET')

DEFAULT_GRAVATAR_URL                                = 'http://www.gravatar.com/avatar'
CSRF_PROTECT                                        = True
MAX_CONTENT_FILE_LENGTH                             = 20 * 1024 * 1024 #limit all request size to 20 mb

IS_PRODUCTION                                       = DEPLOYMENT_MODE==PRODUCTION_MODE
IS_LOCAL                                            = DEPLOYMENT_MODE==LOCAL_MODE
#DEBUG_MODE = False

if DEPLOYMENT_MODE==PRODUCTION_MODE:
    #DEBUG_MODE       = False
    #DEBUG_MODE       = True

    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.WARN
    #LOGGING_LEVEL    = logging.INFO
    #LOGGING_LEVEL    = logging.ERROR
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE
    
    CSRF_PROTECT                            = False
    
    
elif DEPLOYMENT_MODE==DEMO_MODE:
    #DEBUG_MODE       = True
    #DEBUG_MODE       = False
    
    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.INFO
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST
    
    CSRF_PROTECT                            = False
    

elif DEPLOYMENT_MODE==LOCAL_MODE:
    #DEBUG_MODE       = True

    #LOGGING_LEVEL    = logging.DEBUG
    LOGGING_LEVEL    = logging.INFO
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST
    CSRF_PROTECT                            = False


SUPPORT_LANGUAGES                               = ['en','zh']

DEFAULT_COUNTRY_PHONE_PREFIX                    = '+60'
DEFAULT_COUNTRY_CODE                            = 'my'
DEFAULT_CURRENCY_CODE                           = 'MYR'
SECRET_KEY                                      = os.environ['SECRET_KEY']
PAGINATION_SIZE                                 = 10
VISIBLE_PAGE_COUNT                              = 10
SUPPORT_LANGUAGES                               = ['en','zh']

VOUCHER_DEFAULT_IMAGE                           = '%s/static/app/assets/img/voucher/voucher-sample-image.png' % IMAGE_PROD_BASE_URL
LUCKY_DRAW_TICKET_DEFAULT_IMAGE                 = '%s/static/app/assets/img/program/lucky_draw_ticket_default-min.png' % IMAGE_PROD_BASE_URL
REDEMPTION_CATALOGUE_DEFAULT_IMAGE              = '%s/static/app/assets/img/program/redemption-catalogue-default-min.png' % IMAGE_PROD_BASE_URL
REFERRAL_DEFAULT_PROMOTE_IMAGE                  = '%s/static/app/assets/img/program/referral-default-promote.png' % IMAGE_PROD_BASE_URL


ROUNDING_TYPE_ROUND_UP                          = 'roundup'
ROUNDING_TYPE_ROUND_DOWN                        = 'rounddown'

DEFAULT_CURRENCY                                = {
                                                    'code'                  : 'myr',
                                                    'currency_display'      : 'Malaysia Ringgit',
                                                    'currency_label'        : 'RM',
                                                    'floating_point'        : '2',
                                                    'decimal_separator'     : '.',
                                                    'thousand_separator'    : ',',
                                                }



DINNING_ORDER_APP_URL                            = os.environ.get('DINNING_ORDER_APP_URL')



CHECK_ENTITLE_REWARD_THRU_TASKQUEUE              = False

SHOW_DASHBOARD_ANALYTICS_DATA                    = os.environ.get('SHOW_DASHBOARD_ANALYTICS_DATA')

DOCS_URL                                         = os.environ.get('DOCS_URL')

SERVICE_HEADER_AUTHENTICATED_PARAM               = 'x-service-auth-token'
SERVICE_HEADER_AUTHENTICATED_TOKEN               = os.environ.get('SERVICE_HEADER_AUTHENTICATED_TOKEN')

SECRET_HEADER_AUTHENTICATED_PARAM                = 'x-secret-token'
SECRET_HEADER_AUTHENTICATED_TOKEN                = os.environ.get('SECRET_HEADER_AUTHENTICATED_TOKEN')

DEFAULT_TIMEZONE                                 = 'Asia/Kuala_Lumpur'

FIREBASE_SERVICE_ACCOUNT_KEY_PATH                = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')

#-----------------------------------------------------------------
# Web Beacon settings
#-----------------------------------------------------------------
WEB_BEACON_TRACK_EMAIL_OPEN   = 'eo'




