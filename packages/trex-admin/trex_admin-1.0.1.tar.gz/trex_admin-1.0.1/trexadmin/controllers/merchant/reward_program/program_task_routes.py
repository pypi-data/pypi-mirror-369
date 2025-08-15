'''
Created on 9 Apr 2023

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect, url_for, current_app
import logging, json, uuid
from trexlib.utils.log_util import get_tracelog
from flask_restful import Api
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from flask.globals import request
from flask.json import jsonify
from trexmodel.models.datastore.model_decorators import model_transactional
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_redemption_upstream_for_merchant
from trexmodel.models.datastore.message_model_helper import create_redemption_message


program_task_bp = Blueprint('program_task_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/program/task')

logger = logging.getLogger('debug')

@program_task_bp.route('/tier-program/reward-consume', methods=['post'])
def tier_program_reward_consume_for_transaction():
    requet_json                 = request.get_json()
    customer_key                = requet_json.get('customer_key')
    transaction_id              = requet_json.get('transaction_id')
    redeem_reward_details       = requet_json.get('redeem_reward_details')
    
    redeem_reward_details = json.loads(redeem_reward_details)
    
    
    logger.debug('redeem_reward_details=%s', redeem_reward_details)
    logger.debug('customer_key=%s', customer_key)
    logger.debug('transaction_id=%s', transaction_id)
    
    
    @model_transactional(desc='tier_program_reward_consume_for_transaction')
    def __start_transaction(customer_acct, customer_transaction, redeem_reward_details):
        transact_outlet = customer_transaction.transact_outlet_entity
        
        for reward_format, reward_amount_to_redeem in redeem_reward_details.items():
            logger.debug('to redeem: reward_format=%s, reward_amount_to_redeem=%s', reward_format, reward_amount_to_redeem)
            customer_redemption = CustomerRedemption.create(customer_acct, reward_format, 
                                                                              redeemed_outlet               = transact_outlet,
                                                                              redeemed_amount               = reward_amount_to_redeem,            
                                                                              invoice_id                    = customer_transaction.invoice_id, 
                                                                              redeemed_by                   = customer_transaction.transact_by_user, 
                                                                              redeemed_datetime             = customer_transaction.transact_datetime,
                                                                              is_tier_program_redemption    = True,
                                                                              tier_program_transaction_id   = customer_transaction.transaction_id,
                                                                              )
                    
        if customer_redemption:
            #create_redemption_message(customer_redemption)
            create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, )
    
    
    db_client = create_db_client(caller_info="tier_program_reward_consume")
    
    with db_client.context():
        customer                = Customer.fetch(customer_key)
        customer_transaction    = CustomerTransaction.get_by_transaction_id(transaction_id)
        
        __start_transaction(customer, customer_transaction, redeem_reward_details)
    
    return jsonify(request.get_json())    
        
