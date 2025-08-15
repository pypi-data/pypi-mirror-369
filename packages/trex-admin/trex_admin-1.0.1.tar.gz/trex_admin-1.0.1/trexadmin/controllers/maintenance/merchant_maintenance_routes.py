from flask import Blueprint, request, render_template, jsonify
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
import logging, json
from flask.helpers import url_for
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser, Outlet
from trexmodel.models.datastore.prepaid_models import PrepaidSettings
from trexmodel.models.datastore.membership_models import MerchantMembership,\
    MerchantTierMembership
from datetime import datetime
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawProgram
from trexmodel.models.datastore.marketing_models import PushNotificationSetup
from trexmodel.models.datastore.program_models import MerchantProgram
from trexmodel.models.datastore.pos_models import POSSetting, DinningOption
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.product_models import ProductCatalogue
from trexadmin.controllers.merchant.product.product_category_setup_routes import get_product_category_structure_code_label_json_by_merchant_acct
from google.cloud import ndb
import pytz
from trexprogram.reward_program.reward_program_factory import RewardProgramFactory
from trexconf.config_util import DEFAULT_CURRENCY_JSON
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexapi.utils.push_notification_helper import create_prepaid_push_notification
from trexlib.libs.flask_wtf.request_wrapper import request_args, request_values
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexlib.utils.google.bigquery_util import create_bigquery_client,\
    create_table_from_template
from trexconf.conf import BIGQUERY_SERVICE_CREDENTIAL_PATH, MERCHANT_DATASET
from trexanalytics.bigquery_table_template_config import USER_VOUCHER_REMOVED_TEMPLATE,\
    TABLE_SCHEME_TEMPLATE, USER_VOUCHER_REDEEMED_TEMPLATE
from flask_restful import Api
from trexlib.utils.google.cloud_tasks_util import create_task


merchant_maintenance_setup_bp = Blueprint('merchant_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/merchant')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')


merchant_maintenance_setup_bp_api = Api(merchant_maintenance_setup_bp)


@merchant_maintenance_setup_bp.route('/membership/<membership_key>/expiry-date-calc', methods=['get'])
def calc_expiry_date_for_merchant_membership(membership_key):
    db_client = create_db_client(caller_info="read_merchant_acct")
    expiry_date = None
    start_date  = datetime.utcnow().date()
    with db_client.context():
        merchant_membership = MerchantMembership.fetch(membership_key)
        if merchant_membership:
            expiry_date = merchant_membership.calc_expiry_date(start_date=start_date)
    
    return jsonify({
            'start_date':start_date,
            'expiry_date': expiry_date,
            })    



@merchant_maintenance_setup_bp.route('/<merchant_key>/details', methods=['get'])
def read_merchant_acct(merchant_key):
    db_client = create_db_client(caller_info="read_merchant_acct")
    merchant_acct = {}
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        if merchant_acct:
            merchant_acct = merchant_acct.to_dict()
    
    
    
    return jsonify(merchant_acct) 

@merchant_maintenance_setup_bp.route('/<merchant_key>/dinning-option', methods=['get'])
def read_merchant_acct_dinning_option(merchant_key):
    db_client = create_db_client(caller_info="read_merchant_acct_dinning_option")
    dinning_option_json = []
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        if merchant_acct:
            dinning_option_list = DinningOption.list_by_merchant_acct(merchant_acct)
    
            if dinning_option_list:
                for d in dinning_option_list:
                    dinning_option_json.append({
                                                'option_key'                : d.key_in_str,
                                                'option_name'               : d.name,
                                                'option_prefix'             : d.prefix,
                                                'is_default'                : d.is_default,
                                                'is_dinning_input'          : d.is_dinning_input,
                                                'is_delivery_input'         : d.is_delivery_input,
                                                'is_takeaway_input'         : d.is_takeaway_input,
                                                'is_self_order_input'       : d.is_self_order_input,
                                                'is_self_payment_mandatory' : d.is_self_payment_mandatory,
                                                'dinning_table_is_required' : d.dinning_table_is_required,
                                                'assign_queue'              : d.assign_queue,
                                                })
    
    return jsonify(dinning_option_json) 



@merchant_maintenance_setup_bp.route('/<merchant_key>/pos-catalogue', methods=['get'])
def read_merchant_acct_pos_catalogue(merchant_key):
    db_client = create_db_client(caller_info="read_merchant_acct_pos_catalogue")
    result = []
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        if merchant_acct:
            pos_setting_list = POSSetting.list_by_merchant_account(merchant_acct)
            for pos_setting in pos_setting_list:
                if pos_setting:
                    
                    assigned_outlet = pos_setting.assigned_outlet_entity
                    
                    logger.info('assigned_outlet name=%s', assigned_outlet.name)
                    
                    catalogue_key   = assigned_outlet.assigned_catalogue_key
                    
                    logger.debug('catalogue_key=%s', catalogue_key);
                    
                    if is_not_empty(catalogue_key):
                        product_catalogue   = ProductCatalogue.fetch(catalogue_key)
                        category_tree_structure_in_json  = get_product_category_structure_code_label_json_by_merchant_acct(merchant_acct)
                        
                        if product_catalogue:
                            last_updated_datetime = product_catalogue.modified_datetime
                            if assigned_outlet.modified_datetime is not None and assigned_outlet.modified_datetime>last_updated_datetime:
                                last_updated_datetime = assigned_outlet.modified_datetime
                            
                            catalogue_json =  {
                                                    'key'                       : catalogue_key,    
                                                    'category_list'             : category_tree_structure_in_json,
                                                    'product_by_category_map'   : product_catalogue.published_menu_settings,
                                                    'last_updated_datetime'     : last_updated_datetime.strftime('%d-%m-%Y %H:%M:%S')
                                                } 
                            result.append(catalogue_json) 
    
    return jsonify(result)

@merchant_maintenance_setup_bp.route('/merchant-acct-key/<merchant_key>/update-outlet-count', methods=['get'])
def update_merchant_acct_outlet_count(merchant_key):
    db_client = create_db_client(caller_info="update_merchant_acct_outlet_count")
    merchant_acct = {}
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        if merchant_acct:
            
            count = Outlet.count_by_merchant_account(merchant_acct)
            merchant_acct.outlet_count = count
            merchant_acct.put()
            merchant_acct = merchant_acct.to_dict()
    
    
    
    return jsonify(merchant_acct) 

@merchant_maintenance_setup_bp.route('/<merchant_key>/update-outlet-count', methods=['get'])
def update_merchant_acct_published_voucher(merchant_key):
    db_client = create_db_client(caller_info="update_merchant_acct_published_voucher")
    merchant_acct = {}
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        if merchant_acct:
            
            count = Outlet.count_by_merchant_account(merchant_acct)
            merchant_acct.outlet_count = count
            merchant_acct.put()
            merchant_acct = merchant_acct.to_dict()
    
    
    
    return jsonify(merchant_acct) 

@merchant_maintenance_setup_bp.route('/<merchant_key>/prepaid-program/update', methods=['get'])
def update_prepaid_program(merchant_key):
    db_client = create_db_client(caller_info="update_prepaid_program")
    prepaid_program_configuration = {}
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        prepaid_programs_list = PrepaidSettings.list_by_merchant_acct(merchant_acct)
        
        latest_prepaid_programs_list = []
        
        for p in prepaid_programs_list:
            if p.enabled:
                #p.update_merchant_account_prepaid_configuration()
                latest_prepaid_programs_list.append(p.to_configuration())
        
        prepaid_program_configuration['programs'] = latest_prepaid_programs_list
        prepaid_program_configuration['count'] = len(prepaid_program_configuration)
        
        merchant_acct.prepaid_configuration = prepaid_program_configuration
        merchant_acct.put()
        
    return jsonify(prepaid_program_configuration)  

@merchant_maintenance_setup_bp.route('/<merchant_key>/reward-program/update', methods=['get'])
def update_reward_program(merchant_key):
    db_client = create_db_client(caller_info="update_reward_program")
    published_program_configuration = {}
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        programs_list = MerchantProgram.list_by_merchant_account(merchant_acct)
        
        latest_programs_list = []
        
        for p in programs_list:
            if p.enabled:
                #p.update_merchant_account_prepaid_configuration()
                latest_programs_list.append(p.to_configuration())
        
        published_program_configuration['programs'] = latest_programs_list
        published_program_configuration['count'] = len(latest_programs_list)
        
        merchant_acct.published_program_configuration = published_program_configuration
        merchant_acct.put()
        
    return jsonify(published_program_configuration)  

@merchant_maintenance_setup_bp.route('/<merchant_key>/lucky-draw-program/update', methods=['get'])
def update_lucky_draw_program(merchant_key):
    db_client = create_db_client(caller_info="update_prepaid_program")
    lucky_draw_configuration = {}
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        programs_list = LuckyDrawProgram.list_by_merchant_acct(merchant_acct)
        
        latest_lucky_draw_programs_list = []
        
        for p in programs_list:
            logger.debug('program name=%s', p.label)
            if p.enabled and p.is_expired==False:
                #p.image_public_url = 'https://backofficedev.augmigo.com/static/app/assets/img/program/lucky_draw_ticket_default-min.png'
                p.put()
                #p.update_merchant_account_prepaid_configuration()
                latest_lucky_draw_programs_list.append(p.to_configuration())
        
        lucky_draw_configuration['programs'] = latest_lucky_draw_programs_list
        lucky_draw_configuration['count'] = len(latest_lucky_draw_programs_list)
        
        merchant_acct.lucky_draw_configuration = lucky_draw_configuration
        merchant_acct.put()
        
    return jsonify(lucky_draw_configuration)  

@merchant_maintenance_setup_bp.route('/<merchant_key>/membership/update', methods=['get'])
def update_membership(merchant_key):
    db_client = create_db_client(caller_info="update_prepaid_program")
    membership_configuration_list = []
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        
        merchant_memberships_list = MerchantMembership.list_by_merchant_acct(merchant_acct)
        
        for p in merchant_memberships_list:
            membership_configuration_list.append(p.to_configuration())
    
        merchant_acct.membership_configuration = {
                                                'memberships'  :membership_configuration_list,
                                                'count'     : len(membership_configuration_list),
                                                }
        merchant_acct.put()
    return jsonify(membership_configuration_list)

@merchant_maintenance_setup_bp.route('/<merchant_key>/tier-membership/update', methods=['get'])
def update_tier_membership(merchant_key):
    db_client = create_db_client(caller_info="update_prepaid_program")
    membership_configuration_list = []
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        
        merchant_tier_memberships_list = MerchantTierMembership.list_by_merchant_acct(merchant_acct)
        
        for p in merchant_tier_memberships_list:
            membership_configuration_list.add(p.to_configuration())
    
        merchant_acct.tier_membership_configuration = {
                                                'memberships'   : membership_configuration_list,
                                                'count'         : len(membership_configuration_list),
                                                }
        merchant_acct.put()
    return jsonify(membership_configuration_list)  

@merchant_maintenance_setup_bp.route('/update-merchant-user', methods=['get'])
def update_merchant_user():
    db_client = create_db_client(caller_info="update_merchant_user")
    
    with db_client.context():
        
        merchant_user_list = MerchantUser.list_all()
        
        logger.debug('merchant_user_list count=%d', len(merchant_user_list))
        
        for merchant_user in merchant_user_list:
            if merchant_user.permission:
                granted_outlets_list =  merchant_user.permission.get('granted_outlet')
            else:
                granted_outlets_list = []
        
            merchant_user.granted_outlets_search_list = " ".join(granted_outlets_list)
            merchant_user.put()
            
        
    return jsonify({
            "count"             : len(merchant_user_list),
            "updated_datetime"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })   
    
@merchant_maintenance_setup_bp.route('/<merchant_key>/push-notification/schedule-date/<schedule_date>/unsend', methods=['get'])
def list_unsend_push_notification(merchant_key, schedule_date):
    db_client = create_db_client(caller_info="list_unsend_push_notification")
    push_notification_setup_list = [] 
    with db_client.context():
        #merchant_acct = MerchantAcct.fetch(merchant_key)
        schedule_datetime = datetime.strptime(schedule_date, '%d-%m-%Y')
        result = PushNotificationSetup.list(schedule_datetime)
        for r in result:
            push_notification_setup_list.append(r.to_dict())
        
    return jsonify({
            "count"                 : len(result),
            "schedule_datetime"     : schedule_datetime.strftime("%d-%m-%Y %H:%M:%S"),
            'result'                : push_notification_setup_list,
            })
    
@merchant_maintenance_setup_bp.route('/<merchant_key>/gmt-hour', methods=['get'])
def get_merchant_gmt_hour(merchant_key):
    db_client = create_db_client(caller_info="get_merchant_gmt_hour")
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        #gmt_hour = merchant_acct.gmt_hour
        now             = datetime.utcnow()
        timezone        = pytz.timezone(merchant_acct.timezone)
        #timezone_time   = now.astimezone(self.timezone)
        gmt_hour = timezone.utcoffset(now).total_seconds() / 3600
        
        
    return jsonify({
            "gmt_hour"                 : gmt_hour
            })
    
@merchant_maintenance_setup_bp.route('/<merchant_key>/currency-config', methods=['get'])
def get_merchant_currency_config_from_reward_program_factory(merchant_key):
    db_client = create_db_client(caller_info="get_merchant_currency_config_from_reward_program_factory")
    #currency_config = DEFAULT_CURRENCY_JSON
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
        #gmt_hour = merchant_acct.gmt_hour
        reward_program_factory = RewardProgramFactory(merchant_acct)
        programs_list = reward_program_factory.create_program_list()
        if is_not_empty(programs_list):
            logger.debug('programs_list count =%d', len(programs_list))
            for program in programs_list:
                logger.debug('program=%s', program)
    
            currency_config = programs_list[0].currency_config
        
    return jsonify({
            "currency"                 : currency_config
            })  
    
@merchant_maintenance_setup_bp.route('program/<activation_code>/send-push-notification', methods=['get'])
@request_values
def send_merchant_program_device_push_notification(request_values, activation_code):
    db_client = create_db_client(caller_info="send_merchant_program_device_push_notification")
    device_token_list = []
    with db_client.context():
        program_device = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        if program_device:
            title   = request_values.get('title')
            message = request_values.get('message')
            for device_token in program_device.device_tokens_list:
                try:
                    device_token_list.append(device_token)
                    '''
                    create_prepaid_push_notification(
                        title_data=title, 
                        message_data = message,
                        speech = message,
                        device_token = device_token
                        
                    )
                    '''
                except:
                    logger.error('Failed to send push notification due to %s', get_tracelog())
        
        
    return jsonify({
            "device_tokens_list"                 : device_token_list
            })            
    
@merchant_maintenance_setup_bp.route('/<merchant_key>/url-safe-key', methods=['get'])
def convert_to_urlsafe_key(merchant_key):
    urlsafe_key = ndb.Key(urlsafe=merchant_key).urlsafe()
        
    return jsonify({
            "urlsafe_key"          : '%s'% urlsafe_key.decode('utf-8'),
            })        
    
    
class TriggerUpdateMerchantAcct(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/merchant/init-update-merchant-acct'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        merchant_key=request.args.get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }    
    
class InitUpdateMerchantAcct(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitUpdateMerchantAcct")
    
        with db_client.context():
            if is_not_empty(merchant_key):
                merchant_acct = MerchantAcct.fetch(merchant_key)
                if merchant_acct:
                    count = 1
            else:
                count = MerchantAcct.count()
        
        return count
    
    def get_task_batch_size(self):
        return 10
    
    def get_task_url(self):
        return '/maint/merchant/update-merchant-acct'
    
    def get_task_queue(self):
        return 'test'
    
    
    def get_data_payload(self):
        merchant_key=request.get_json().get('merchant_key')
        return {
                'merchant_key': merchant_key,
            }
    
class ExecuteUpdateMerchantAcct(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteUpdateMerchantAcct")
    
        with db_client.context():
            if merchant_key:
                merchant_acct   = MerchantAcct.fetch(merchant_key)
                result          = [merchant_acct]
                next_cursor     = None
            else:
                (result, next_cursor)       = MerchantAcct.list(offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=True)
            
            if result:
                
                for merchant_acct in result:
                    self._update_merchant_acct(merchant_acct)
                    
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/merchant/update-merchant-acct' 

    def get_data_payload(self):
        merchant_key=request.get_json().get('merchant_key')
        return {
                'merchant_key': merchant_key,
            } 
        
    def _update_merchant_acct(self, merchant_acct):
        self._create_analytic_required_table(merchant_acct)
    
    def _create_analytic_required_table(self, merchant_acct):
        year_month_day = datetime.strftime(merchant_acct.registered_datetime, '%Y%m%d')
        account_code = merchant_acct.account_code
        bq_client    = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)
        
        account_code    = account_code.replace('-','')
        
        table_name = USER_VOUCHER_REMOVED_TEMPLATE
        final_table_name        = '{}_{}'.format(table_name, year_month_day)
        
        merchant_dataset = '%s_%s' % (MERCHANT_DATASET, account_code)
        
        created_table   = create_table_from_template(
                            merchant_dataset, 
                            final_table_name, 
                            TABLE_SCHEME_TEMPLATE.get(USER_VOUCHER_REMOVED_TEMPLATE), 
                            bigquery_client=bq_client)
        logger.info('create_merchant_required_analytics_table: created table(%s)=%s', final_table_name, created_table)
        
        table_name = USER_VOUCHER_REDEEMED_TEMPLATE
        final_table_name        = '{}_{}'.format(table_name, year_month_day)
        
        created_table   = create_table_from_template(
                            merchant_dataset, 
                            final_table_name, 
                            TABLE_SCHEME_TEMPLATE.get(USER_VOUCHER_REDEEMED_TEMPLATE), 
                            bigquery_client=bq_client)
        logger.info('create_merchant_required_analytics_table: created table(%s)=%s', final_table_name, created_table)
    
         
        
merchant_maintenance_setup_bp_api.add_resource(TriggerUpdateMerchantAcct,   '/trigger-update-merchant-acct')
merchant_maintenance_setup_bp_api.add_resource(InitUpdateMerchantAcct,   '/init-update-merchant-acct')
merchant_maintenance_setup_bp_api.add_resource(ExecuteUpdateMerchantAcct,   '/update-merchant-acct')

              