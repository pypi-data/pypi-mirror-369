'''
Created on 13 Mar 2023

@author: jacklok
'''

from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client 
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership
from trexmodel.models.datastore.merchant_models import Outlet
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantUser
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.model_decorators import model_transactional
from trexlib.utils.string_util import is_not_empty
from trexadmin.forms.merchant.customer_forms import CustomerMembershipForm
from trexmodel.models.datastore.membership_models import MerchantMembership
from trexmodel.models.datastore.helper.reward_transaction_helper import check_giveaway_reward_for_membership_purchase_transaction
from trexanalytics.bigquery_upstream_data_config import create_customer_membership_upstream_for_merchant


manage_customer_membership_bp = Blueprint('manage_customer_membership_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/customer-membership')


logger = logging.getLogger('debug')

'''
Blueprint settings here
'''
@manage_customer_membership_bp.context_processor
def manage_customer_membership_bp_inject_settings():
    
    return dict(
                )
    
@manage_customer_membership_bp.route('/customer/<customer_key>/assign', methods=['GET'])
@login_required
def assign_customer_membership(customer_key): 
    logger.debug('---assign_customer_membership---')
    
    db_client = create_db_client(caller_info="assign_customer_membership")
    merchant_membership_keys_list = []
    with db_client.context():
        customer            = Customer.fetch(customer_key)
        result              = CustomerMembership.list_active_by_customer(customer)
        
        if is_not_empty(result):
            for r in result:
                merchant_membership_keys_list.append(r.merchant_membership_key)
        
        customer_details= customer.to_dict()
    
    logger.debug('merchant_membership_keys_list=%s', merchant_membership_keys_list)
    return render_template('merchant/crm/customer_membership/assign_customer_membership.html', 
                           page_title                       = gettext('Assign Customer Membership'),
                           customer                         = customer_details,
                           merchant_membership_keys_list    = merchant_membership_keys_list,
                           post_url                         = url_for('manage_customer_membership_bp.assign_customer_membership_post', customer_key=customer_key),
                           ) 
    
@manage_customer_membership_bp.route('/customer/<customer_key>/assign', methods=['POST'])
@login_required
def assign_customer_membership_post(customer_key): 
    logger.debug('---assign_customer_membership_post---')
    
    customer_membership_data = request.form
    
    logger.debug('customer_membership_data=%s', customer_membership_data)
    
    customer_membership_form = CustomerMembershipForm(customer_membership_data)
    
    logger.debug('customer_key=%s', customer_key)
    
    try:
        if is_not_empty(customer_key):
            if customer_membership_form.validate():
                db_client = create_db_client(caller_info="assign_customer_membership_post")
                
                logged_in_merchant_user = get_loggedin_merchant_user_account()
                membership_key = customer_membership_form.membership_key.data
                
                logger.debug('membership_key=%s', membership_key)
                
                with db_client.context():   
                    customer_acct   = Customer.fetch(customer_key)
                    logger.debug('customer_acct=%s', customer_acct)
                    
                    
                    
                    
                    
                    if customer_acct:
                        merchant_membership = MerchantMembership.fetch(membership_key)
                        
                        customer_membership = CustomerMembership.get_by_customer_and_merchant_membership(customer_acct, merchant_membership)
                
                
                        
                if customer_membership:
                    logger.debug('customer membership have been assigned already')
                    return create_rest_message(gettext('Customer membership already have been assigned'), status_code=StatusCode.OK)
                
                else:
                    with db_client.context():    
                        assigned_by         = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                        assigned_outlet     = Outlet.fetch(customer_membership_form.assigned_outlet.data)
                        
                        __assign_membership(customer_acct, merchant_membership, assigned_by, assigned_outlet)
                        
                        logger.debug('customer membership assigned successfully')
                
                    return create_rest_message(gettext('Customer membership have been assigned successfully'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = customer_membership_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete customer data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to assign membership due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)          


@model_transactional(desc="assign customer membership")
def __assign_membership(customer, merchant_membership, assigned_by, assigned_outlet):
    customer_membership = CustomerMembership.create(customer, merchant_membership, assigned_by=assigned_by, assigned_outlet=assigned_outlet)
    
    customer_transaction = CustomerTransaction.create_membership_purchase_transaction(
                                customer, customer_membership, 
                                system_remarks= "Joined Membership", 
                                transact_outlet=assigned_outlet, 
                                transact_by=assigned_by, 
                                )
    check_giveaway_reward_for_membership_purchase_transaction(customer, customer_transaction)
    create_customer_membership_upstream_for_merchant(customer_membership)
    
    