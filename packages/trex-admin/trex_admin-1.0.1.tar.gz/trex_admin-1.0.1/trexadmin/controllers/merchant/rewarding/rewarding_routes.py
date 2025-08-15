'''
Created on 23 Apr 2021

@author: jacklok
'''


from flask import Blueprint, request, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.helper.reward_transaction_helper import check_giveaway_reward_for_transaction
from trexmodel.models.datastore.reward_models import CustomerPointReward, CustomerStampReward
from flask.json import jsonify
from trexmodel.models.datastore.customer_models import Customer
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
import gettext
from flask.helpers import url_for
from trexmodel.models.datastore.merchant_models import Outlet, MerchantUser
from trexadmin.forms.merchant.rewarding_forms import GiveawayRewardForm
from trexmodel.models.datastore.program_models import MerchantProgram
from trexmodel.models.datastore.model_decorators import model_transactional
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_transaction_upstream_for_merchant
from datetime import datetime, timedelta
from trexmodel.models.datastore.message_model_helper import create_transaction_message

rewarding_bp = Blueprint('rewarding_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/rewarding')


logger = logging.getLogger('controller')


@rewarding_bp.route('/', methods=['get'])
def rewarding_index():
    return 'Rewarding module', 200

@rewarding_bp.route('/transaction-summary', methods=['get'])
def show_transaction_reward_summary():
    logger.debug('--- submit show_transaction_reward_summary ---')
    
    transaction_id = request.args.get('transaction_id')
    
    db_client = create_db_client(caller_info="check_entitle_reward_get_post")
    
    with db_client.context():
        customer_transaction            = CustomerTransaction.get_by_transaction_id(transaction_id)
        
        transaction_details = customer_transaction.to_dict()
    
    return jsonify(transaction_details)

@rewarding_bp.route('/list-customer-reward/<customer_key>', methods=['get'])
def list_customer_entitled_reward(customer_key):
    logger.debug('--- list_customer_entitled_reward ---')
    
    db_client = create_db_client(caller_info="list_customer_entitled_reward")
    
    reward_list = []
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        
        point_reward_list = CustomerPointReward.list_by_customer(customer)
        stamp_reward_list = CustomerStampReward.list_by_customer(customer)
        
        for p in point_reward_list:
            reward_list.append(p.to_reward_summary())
            
        for p in stamp_reward_list:
            reward_list.append(p.to_reward_summary())    
        
    
    return jsonify(reward_list) 

@rewarding_bp.route('/list-customer-reward-by-transaction-id/<transaction_id>', methods=['get'])
def list_customer_entitled_reward_by_transaction_id(transaction_id):
    logger.debug('--- list_customer_entitled_reward_by_transaction_id ---')
    
    db_client = create_db_client(caller_info="list_customer_entitled_reward_by_transaction_id")
    
    reward_list = []
    
    with db_client.context():
        point_reward_list = CustomerPointReward.list_by_transaction_id(transaction_id)
        stamp_reward_list =CustomerStampReward.list_by_transaction_id(transaction_id)
        
        for p in point_reward_list:
            reward_list.append(p.to_reward_summary())
            
        for p in stamp_reward_list:
            reward_list.append(p.to_reward_summary())    
        
    
    return jsonify(reward_list) 




@rewarding_bp.route('/giveaway-reward/<customer_key>', methods=['GET'])
@login_required
def giveaway_reward(customer_key): 
    logger.debug('---giveaway_reward---')
    
    db_client = create_db_client(caller_info="giveaway_reward")
    
    with db_client.context():
        customer                        = Customer.fetch(customer_key)
        customer_details                = customer.to_dict()
    
    #currency_details    = get_currency_config(currency_code)    
    
    return render_template('merchant/loyalty/rewarding/giveaway_reward.html', 
                           customer                 = customer_details,
                           post_url                 = url_for('rewarding_bp.giveaway_reward_post'),
                           ) 
    rewarding_bp

@rewarding_bp.route('/giveaway-reward', methods=['post'])
def giveaway_reward_post():
    logger.debug('--- submit giveaway_reward_post ---')   
    
    giveaway_reward_data = request.form
    
    logger.debug('giveaway_reward_data=%s', giveaway_reward_data)
    
    giveaway_reward_form = GiveawayRewardForm(giveaway_reward_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    if giveaway_reward_form.validate():
        
        
        db_client = create_db_client(caller_info="giveaway_reward_post")
    
        @model_transactional(desc='giveaway_reward_post')
        def __start_for_manual_giveaway_reward_transaction(customer, transact_outlet, customer_transaction_details_form, merchant_user, 
                                                           transact_datetime, program_configuration):
            customer_transaction = CustomerTransaction.create_manual_transaction(
                                           customer, 
                                           transact_outlet      = transact_outlet,
                                           
                                           remarks              = customer_transaction_details_form.remarks.data,
                                           
                                           transact_by          = merchant_user,
                                           
                                           transact_datetime    = transact_datetime,
                                           )
            
            program_configuration_list  = [program_configuration]    
            reward_set                  = customer_transaction_details_form.reward_set_count.data
            
            logger.debug('reward_set=%d', reward_set)
            
            give_reward_status          = check_giveaway_reward_for_transaction(customer, 
                                                                                customer_transaction, 
                                                                                program_configuration_list, 
                                                                                reward_set=reward_set)
            
            logger.debug('give_reward_status=%s', give_reward_status)
            
            if give_reward_status:
                logger.debug('Going to create upstream')
                create_transaction_message(customer_transaction)
                create_merchant_customer_transaction_upstream_for_merchant(customer_transaction, )
            
        
        transact_datetime_in_gmt    = giveaway_reward_form.giveaway_reward_datetime.data
        
        logger.debug('transact_datetime_in_gmt b4=%s', transact_datetime_in_gmt)
        
        with db_client.context():   
            customer        = Customer.fetch(giveaway_reward_form.customer_key.data)
            merchant_acct   = customer.registered_merchant_acct
            if customer:
                transact_outlet = Outlet.fetch(giveaway_reward_form.giveaway_outlet.data)
            
            logger.debug('customer=%s', customer)
        
        if customer is None:
            return create_rest_message(gettext('Invalid customer data'), status_code=StatusCode.BAD_REQUEST)
        
        transact_datetime = None
            
        if transact_datetime_in_gmt:
            transact_datetime    =  transact_datetime_in_gmt - timedelta(hours=merchant_acct.gmt_hour)
            
            logger.debug('transact_datetime_in_gmt after=%s', transact_datetime_in_gmt)
            
            now                         = datetime.now()
            if transact_datetime > now:
                return create_rest_message(gettext('Transact datetime cannot future'), status_code=StatusCode.BAD_REQUEST)
        
        with db_client.context():
            merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            giveaway_reward_program_key = giveaway_reward_form.giveaway_reward_program.data
            giveaway_reward_program     = MerchantProgram.fetch(giveaway_reward_program_key)
            program_configuration       = giveaway_reward_program.to_configuration()
            
            __start_for_manual_giveaway_reward_transaction(customer, 
                                                           transact_outlet, 
                                                           giveaway_reward_form, 
                                                           merchant_user, 
                                                           transact_datetime, 
                                                           program_configuration)
                
        
        return create_rest_message('Giveaway reward to customer successfully', status_code=StatusCode.OK)
    else:
        error_message = giveaway_reward_form.create_rest_return_error_message()
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
    
     
    