'''
Created on 28 May 2021

@author: jacklok
'''

from flask import Blueprint, request, render_template
from trexmodel.utils.model.model_util import create_db_client 
from trexadmin.libs.http import StatusCode, create_rest_message
import logging
from trexlib.utils.string_util import is_not_empty
from flask.json import jsonify
from trexmodel.models.datastore.customer_models import Customer
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from flask.helpers import url_for
from trexmodel.models.datastore.merchant_models import Outlet, MerchantUser
from datetime import datetime, timedelta
from trexconf import conf
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher
from trexadmin.forms.merchant.redeeming_forms import RedeemRewardForm
from trexmodel import program_conf
from flask_babel import gettext
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.helper.reward_transaction_helper import redeem_reward_transaction
from trexmodel.models.datastore.helper.reward_model_helpers import check_redeem_voucher_is_valid

redeeming_bp = Blueprint('redeeming_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/redeeming')


#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')


@redeeming_bp.context_processor
def redeeming_bp_inject_settings():
    
    return dict(
                )


@redeeming_bp.route('/', methods=['get'])
def redeeming_index():
    return 'Redeeming module', 200

@redeeming_bp.route('/enter-redeem/<customer_key>', methods=['get'])
def enter_redeem(customer_key):
    logger.debug('--- submit enter_redeem ---')
    
    db_client = create_db_client(caller_info="check_entitle_reward_get_post")
    
    with db_client.context():
        customer            = Customer.fetch(customer_key)
        customer_details    = customer.to_dict()
        
    
    return render_template('merchant/loyalty/redeeming/enter_redeem.html', 
                           customer                 = customer_details,
                           voucher_group_dict       = __list_customer_entitled_voucher(customer_key),
                           post_url                 = url_for('redeeming_bp.enter_redeem_post'),
                           )

@redeeming_bp.route('/enter-redeem', methods=['post'])
def enter_redeem_post():
    logger.debug('--- submit enter_redeem_post ---')
    redeem_reward_data      = request.form
    redeem_form             = RedeemRewardForm(redeem_reward_data)
    
    logger.debug('redeem_reward_data=%s', redeem_reward_data)
    
    logger.debug('redeem_form.reward_format.data=%s', redeem_form.reward_format.data)
    logger.debug('redeem_form.redeem_voucher.data=%s', redeem_form.redeem_voucher.data)
    
    if redeem_form.validate():
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        
        db_client = create_db_client(caller_info="enter_redeem_post")
        
        redeemed_datetime_in_gmt    = redeem_form.redeemed_datetime.data
        
        logger.debug('redeemed_datetime_in_gmt =%s', redeemed_datetime_in_gmt)
        
        
        with db_client.context():   
            customer        = Customer.fetch(redeem_form.customer_key.data)
            if customer:
                merchant_acct = customer.registered_merchant_acct
        
        redeemed_datetime = None
        now               = datetime.utcnow()
            
        if redeemed_datetime_in_gmt:
            redeemed_datetime    =  redeemed_datetime_in_gmt - timedelta(hours=merchant_acct.gmt_hour)
            
            logger.debug('redeemed_datetime after=%s', redeemed_datetime)
            
            if redeemed_datetime > now:
                return create_rest_message(gettext('Redeem datetime cannot be future'), status_code=StatusCode.BAD_REQUEST)
        else:
            redeemed_datetime   = now
        
        reward_format               = redeem_form.reward_format.data
        redeem_amount               = redeem_form.redeem_amount.data
        redeemed_voucher_keys_list  = redeem_form.redeem_voucher.data
        invoice_id                  = redeem_form.invoice_id.data
        remarks                     = redeem_form.remarks.data
        
        if is_not_empty(redeemed_voucher_keys_list):
            redeemed_voucher_keys_list = redeemed_voucher_keys_list.split(',')
        
        
        
        if reward_format in (program_conf.REWARD_FORMAT_POINT,program_conf.REWARD_FORMAT_STAMP) :
            reward_summary              = customer.reward_summary
            
            logger.debug('********************************')
            logger.debug('reward_summary=%s', reward_summary)
            logger.debug('********************************')
            
            if reward_summary.get(reward_format).get('amount') < redeem_amount:
                return create_rest_message(gettext('Not sufficient reward amount to redeem'), status_code=StatusCode.BAD_REQUEST)
            
        elif reward_format == program_conf.REWARD_FORMAT_VOUCHER:
            
            logger.debug('********************************')
            logger.debug('redeemed_voucher_keys_list=%s', redeemed_voucher_keys_list)
            logger.debug('********************************')
            
            customer_vouchers_list = []
            
            for voucher_key in redeemed_voucher_keys_list:
                
                logger.debug('voucher_key=%s', voucher_key)
                
                with db_client.context():
                    customer_voucher        = CustomerEntitledVoucher.fetch(voucher_key)
                    
                
                customer_vouchers_list.append(customer_voucher)
                        
            try:
                with db_client.context():
                    check_redeem_voucher_is_valid(customer, customer_vouchers_list, redeem_datetime=redeemed_datetime)
            except Exception as error:
                return create_rest_message(str(error), status_code=StatusCode.BAD_REQUEST)
                
            
        elif reward_format == program_conf.REWARD_FORMAT_PREPAID:
            prepaid_summary              = customer.prepaid_summary
            
            logger.debug('********************************')
            logger.debug('prepaid_summary=%s', prepaid_summary)
            logger.debug('********************************')
            
            if prepaid_summary.get('amount') < redeem_amount:
                return create_rest_message(gettext('Not sufficient prepaid amount to redeem'), status_code=StatusCode.BAD_REQUEST)
            
            
        #is_redeem_success = True
        redemption_details = None
        
        with db_client.context():
            try:   
                merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                redeemed_outlet     = Outlet.fetch(redeem_form.redeemed_outlet.data)
                
                redemption_details  = redeem_reward_transaction(customer, 
                                                                redeem_outlet               = redeemed_outlet,
                                                                reward_format               = reward_format,
                                                                reward_amount               = redeem_amount,
                                                                invoice_id                  = invoice_id,
                                                                remarks                     = remarks,
                                                                redeemed_by                 = merchant_user, 
                                                                redeemed_datetime           = redeemed_datetime, 
                                                                redeemed_voucher_keys_list  = redeemed_voucher_keys_list
                                                                )
                
                updated_customer  = Customer.fetch(redeem_form.customer_key.data)
                
            except:
                logger.error('Failed to redeem due to %s', get_tracelog())
                
        
            logger.debug('redemption_details=%s', redemption_details)
        
        if redemption_details:
            #require reward summary to update form validation
            return create_rest_message(status_code=StatusCode.OK, reward_summary = updated_customer.reward_summary)
        else:
            return create_rest_message(gettext('Failed to redeem'), status_code=StatusCode.BAD_REQUEST)
            
        
    else:
        error_message = redeem_form.create_rest_return_error_message()
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    


def __list_customer_entitled_voucher(customer_key):
    logger.debug('--- __list_customer_entitled_voucher ---')
    
    db_client = create_db_client(caller_info="__list_customer_entitled_voucher")
    
    voucher_group_dict = {} 
    
    today_date = datetime.today().date()
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        
        customer_voucher_list = CustomerEntitledVoucher.list_by_customer(customer)
        
        logger.debug('customer_voucher_list count=%s', len(customer_voucher_list))
        
        for cv in customer_voucher_list:
            
            voucher_group_key       = cv.entitled_voucher_key
            entitled_voucher        = cv.entitled_voucher_entity
            voucher_effective_date  = cv.effective_date
            voucher_expiry_date     = cv.expiry_date
            is_effective            = voucher_effective_date <= today_date
            is_expired              = voucher_expiry_date < today_date
            
            voucher_group           = voucher_group_dict.get(voucher_group_key)
            
            if voucher_group:
                group_list = voucher_group.get('vouchers')
            else:
                voucher_group_dict[voucher_group_key] = {
                                                        'label' : entitled_voucher.label,
                                                        }
                group_list = []
            
            if not is_expired and is_effective:
            
                group_list.append({
                                    
                                    'voucher_key'       : cv.key_in_str,
                                    'redeem_code'       : cv.redeem_code,
                                    'effective_date'    : voucher_effective_date.strftime('%d %b %Y'),
                                    'expiry_date'       : voucher_expiry_date.strftime('%d %b %Y'), 
                                    'is_effective'      : is_effective,
                                    'is_expired'        : is_expired,
                                    })
            voucher_group_dict[voucher_group_key]['vouchers'] = group_list
        
        filtered_voucher_group_dict = {}
            
        for voucher_key, voucher_details in voucher_group_dict.items():
            if len(voucher_details.get('vouchers'))>0:
                filtered_voucher_group_dict[voucher_key] = voucher_details
    
    
            
    return filtered_voucher_group_dict

@redeeming_bp.route('/list-customer-entitled-voucher/<customer_key>', methods=['get'])
def list_customer_entitled_voucher(customer_key):
    logger.debug('--- list_customer_entitled_voucher ---')
    
    voucher_group_dict = __list_customer_entitled_voucher(customer_key)
    
    return jsonify(voucher_group_dict) 


