'''
Created on 5 Oct 2023

@author: jacklok
'''
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.customer_models import CustomerMembership,\
    CustomerTierMembership
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher,\
    CustomerPointReward, CustomerStampReward
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
import logging
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawTicket
from trexmodel.models.datastore.analytic_models import UpstreamData

logger = logging.getLogger('helper')

@model_transactional(desc='delete_customer')
def delete_customer(customer):
    
    __delete_customer_membership(customer)
    __delete_customer_tier_membership(customer)
    
    __delete_customer_entitled_voucher(customer)
    __delete_customer_point_reward(customer)
    __delete_customer_stamp_reward(customer)
    __delete_customer_prepaid_reward(customer)
    
    __delete_customer_transaction(customer)
    __delete_customer_lucky_draw_ticket(customer)
    __delete_customer_upstream(customer)
    
    customer.delete()
    
    

def __delete_customer_membership(customer):
    CustomerMembership.delete_all_by_customer(customer)
    
def __delete_customer_tier_membership(customer):
    CustomerTierMembership.delete_all_by_customer(customer)
    
def __delete_customer_entitled_voucher(customer):
    CustomerEntitledVoucher.delete_all_by_customer(customer)
    
def __delete_customer_point_reward(customer):
    CustomerPointReward.delete_all_by_customer(customer)
    
def __delete_customer_stamp_reward(customer):
    CustomerStampReward.delete_all_by_customer(customer)

def __delete_customer_prepaid_reward(customer):
    CustomerPrepaidReward.delete_all_by_customer(customer)                    

def __delete_customer_transaction(customer):
    CustomerTransaction.delete_all_by_customer(customer)  

def __delete_customer_lucky_draw_ticket(customer):
    LuckyDrawTicket.delete_all_by_customer(customer)
    
def __delete_customer_upstream(customer):
    customer_key = customer.key_in_str
    result = UpstreamData.list_not_send()
    
    logger.debug('found unsend upstream data=%d', len(result))
    
    for r in result:
        stream_content_customer_key = r.stream_content[0].get('CustomerKey')
        logger.debug('stream_content_customer_key=%s', stream_content_customer_key)
        if stream_content_customer_key == customer_key:
            r.delete()
        
    
        
