'''
Created on 22 Dec 2020

@author: jacklok
'''
from flask import Blueprint, render_template, request, current_app
from trexadmin.forms.merchant.customer_forms import CustomerSearchForm, CustomerDetailsForm, CustomerRegistrationForm, ResetCustomerPasswordForm, \
    CustomerContactForm, CustomerBiodataForm, CustomerMemberKPIForm
from trexmodel.utils.model.model_util import create_db_client 
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership, CustomerTierMembership
from trexmodel.models.datastore.merchant_models import Outlet, MerchantTagging
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
from trexlib.utils.string_util import is_not_empty
from trexadmin.libs.jinja.common_filters import pretty_datetime_filter
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_merchant_configured_currency_details
from trexweb.utils.common.http_response_util import create_cached_response, MINE_TYPE_JSON
from trexanalytics.bigquery_upstream_data_config import create_registered_customer_upstream_for_system, create_merchant_registered_customer_upstream_for_merchant,\
    create_removed_customer_voucher_to_upstream_for_merchant,\
    create_merchant_customer_transaction_upstream_for_merchant
    
import json
from trexadmin.conf import PAGINATION_SIZE
#from google.cloud import ndb
from trexlib.utils.crypto_util import encrypt_json, decrypt_json
from trexadmin.controllers.system.system_route_helpers import get_reward_format_json
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.reward_models import CustomerEntitledTierRewardSummary,\
    CustomerEntitledVoucher
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from datetime import datetime
from trexmodel.models.datastore.helper.reward_transaction_helper import revert_transaction,\
    revert_redemption, check_user_joined_merchant_birthday_reward
from trexmodel.models.datastore.customer_model_helpers import update_customer_entiteld_voucher_summary_after_removed_voucher
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawTicket
from trexconf import conf
from trexlib.libs.flask_wtf.request_wrapper import request_form, request_values

merchant_manage_customer_bp = Blueprint('merchant_manage_customer_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/manage-customer')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@merchant_manage_customer_bp.context_processor
def manage_customer_bp_inject_settings():
    
    return dict(
                side_menu_group_name            = "merchant",
                customer_details_url            = url_for('merchant_manage_customer_bp.customer_details'),
               customer_contact_url             = url_for('merchant_manage_customer_bp.customer_contact'),
               customer_biodata_url             = url_for('merchant_manage_customer_bp.customer_biodata'),
               customer_member_kpi_url          = url_for('merchant_manage_customer_bp.customer_member_kpi'),
               customer_member_reward_url       = url_for('merchant_manage_customer_bp.customer_member_reward'),
               customer_transaction_history_url = url_for('merchant_manage_customer_bp.list_customer_transaction_history', 
                                                          limit=conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE, 
                                                          page_no=1),
               customer_redemption_history_url = url_for('merchant_manage_customer_bp.list_customer_redemption_history', 
                                                          limit=conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE, 
                                                          page_no=1),
                
                )

@merchant_manage_customer_bp.route('/', methods=['GET'])
@login_required
def manage_customer(): 
    logger.debug('---manage_customer---')
    
    
    return render_template('merchant/crm/manage_customer/manage_customer_index.html', 
                           page_title           = gettext('Manage Customer'),
                           page_url             = url_for('merchant_manage_customer_bp.manage_customer'),
                           pagination_limit     = PAGINATION_SIZE,
                           search_customer_url  = url_for('merchant_manage_customer_bp.search_customer', 
                                                          limit     = conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE,
                                                          #limit     = 2,
                                                          page_no   = 1
                                                          )
                           )

@merchant_manage_customer_bp.route('/add', methods=['GET'])
@login_required
def add_customer(): 
    
    return render_template('merchant/crm/manage_customer/manage_customer_details.html',
                           customer                     = None,
                           show_password_input          = True,
                           
                           #customer_details_url         = url_for('merchant_manage_customer_bp.customer_details'),
                           #customer_contact_url         = url_for('merchant_manage_customer_bp.customer_contact'),
                           #customer_biodata_url         = url_for('merchant_manage_customer_bp.customer_biodata'),
                           #customer_member_kpi_url      = url_for('merchant_manage_customer_bp.customer_member_kpi'),
                           #customer_member_reward_url   = url_for('merchant_manage_customer_bp.customer_member_reward'),
                           post_url                     = url_for('merchant_manage_customer_bp.add_customer_post'),
                           )


@merchant_manage_customer_bp.route('/add', methods=['post'])
@login_required
@request_form
def add_customer_post(request_form):
    logger.debug('--- submit add_customer data ---')
    add_customer_data       = request_form
    #logged_in_merchant_user = get_loggedin_merchant_user_account()
    logger.debug('add_customer_data=%s', add_customer_data)
    
    add_customer_form = CustomerRegistrationForm(add_customer_data)

    @model_transactional(desc='add customer transaction')
    def __start_transaction():
        
        logger.debug('--__start_transaction--')
        
        try:
            
            registered_outlet   = Outlet.fetch(add_customer_form.registered_outlet.data)
            created_customer    = Customer.create(
                                            outlet                  = registered_outlet,
                                            name                    = add_customer_form.name.data,
                                            mobile_phone            = add_customer_form.mobile_phone.data,
                                            email                   = add_customer_form.email.data,
                                            password                = add_customer_form.password.data,
                                            merchant_reference_code = add_customer_form.merchant_reference_code.data,
                                            )
            
        
            
            create_merchant_registered_customer_upstream_for_merchant(created_customer)
            create_registered_customer_upstream_for_system(created_customer)
            
            return created_customer
            
        except:
            logger.error('Failed to create customer due to %s', get_tracelog())
            
    
    
    try:
        if add_customer_form.validate():
            
            db_client = create_db_client(caller_info="add_customer_post")
            with db_client.context():
                created_customer = __start_transaction()
            
            
            if created_customer is None:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                if created_customer:
                    return create_rest_message(gettext('Customer have been created'), 
                                           status_code          = StatusCode.OK, 
                                           created_customer_key = created_customer.key_in_str,
                                           post_url             = url_for('merchant_manage_customer_bp.update_customer_post'))
                else:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = add_customer_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@merchant_manage_customer_bp.route('/update', methods=['post'])
@request_form
def update_customer_post(request_form):
    logger.debug('--- submit update_customer_post data ---')
    customer_details_data = request_form
    
    logger.debug('customer_details_data=%s', customer_details_data)
    
    customer_details_form = CustomerDetailsForm(customer_details_data)
    customer_key = customer_details_form.customer_key.data
    
    logger.debug('customer_key=%s', customer_key)
    
    try:
        if is_not_empty(customer_key):
            if customer_details_form.validate():
                
                    
                db_client = create_db_client(caller_info="update_customer_post")
                with db_client.context():   
                    customer            = Customer.fetch(customer_key)
                    registered_outlet   = Outlet.fetch(customer_details_form.registered_outlet.data)
                    logger.debug('customer=%s', customer)
                    
                    Customer.update(customer                = customer, 
                                    outlet                  = registered_outlet,
                                    name                    = customer_details_form.name.data,
                                    email                   = customer_details_form.email.data,
                                    mobile_phone            = customer_details_form.mobile_phone.data,
                                    merchant_reference_code = customer_details_form.merchant_reference_code.data,
                                    )
                    
                    
                    #create_merchant_registered_customer_upstream_for_merchant(customer)
                    #create_registered_customer_upstream_for_system(customer)
                
                
                return create_rest_message(gettext('Customer details have been updated'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = customer_details_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete customer data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to update customer details due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@merchant_manage_customer_bp.route('/customer-details/<customer_key>', methods=['GET'])
@login_required
def read_customer(customer_key): 
    logger.debug('---read_customer---')
    
    db_client = create_db_client(caller_info="read_customer")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        customer_details = customer.to_dict()
    
    return render_template('merchant/crm/manage_customer/manage_customer_details.html', 
                           page_title                       = gettext('Customer Details'),
                           customer                         = customer_details,
                           
                           post_url                         = url_for('merchant_manage_customer_bp.update_customer_post'),
                           customer_key                     = customer_key,
                           
                           ) 
    
@merchant_manage_customer_bp.route('/customer-details', methods=['GET'])
@login_required
@request_values
def customer_details(request_values): 
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="customer_details")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        customer_details = customer.to_dict()
        
    
    return render_template('merchant/crm/manage_customer/customer_details_content.html', 
                           page_title           = gettext('Customer Details'),
                           customer             = customer_details,
                           post_url             = url_for('merchant_manage_customer_bp.update_customer_post'),
                           ) 
    
@merchant_manage_customer_bp.route('/customer-contact', methods=['GET'])
@login_required
@request_values
def customer_contact(request_values): 
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="customer_contact")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        registered_user_acct = customer.registered_user_acct
        
    
    return render_template('merchant/crm/manage_customer/customer_contact.html', 
                           page_title           = gettext('Customer Contact'),
                           user_acct            = registered_user_acct.to_dict(),
                           post_url             = url_for('merchant_manage_customer_bp.customer_contact_post'),
                           )         

@merchant_manage_customer_bp.route('/customer-contact', methods=['post'])
@request_form
def customer_contact_post(request_form):
    logger.debug('--- submit customer_contact_post data ---')
    customer_contact_data = request_form
    
    logger.debug('customer_contact_data=%s', customer_contact_data)
    
    customer_contact_form = CustomerContactForm(customer_contact_data)
    user_key = customer_contact_form.user_key.data
    
    logger.debug('user_key=%s', user_key)
    
    try:
        if is_not_empty(user_key):
            if customer_contact_form.validate():
                db_client = create_db_client(caller_info="customer_contact_post")
                with db_client.context():   
                    user_acct = User.fetch(user_key)
                    logger.debug('user_acct=%s', user_acct)
                    if user_acct:
                        User.update_contact(user_acct, 
                                                address=customer_contact_form.address.data,
                                                city=customer_contact_form.city.data,
                                                state=customer_contact_form.state.data,
                                                postcode=customer_contact_form.postcode.data,
                                                country=customer_contact_form.country.data
                                                )
                        update_customer_data(user_acct, update_upstream=False)
                        
                
                return create_rest_message(gettext('Customer contact have been updated'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = customer_contact_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete customer data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to update customer details due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@merchant_manage_customer_bp.route('/customer-biodata', methods=['GET'])
@login_required
@request_values
def customer_biodata(request_values): 
    customer_key = request_values.get('customer_key')
    logger.debug('customer_biodata debug: customer_key=%s', customer_key)
    db_client = create_db_client(caller_info="customer_biodata")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        registered_user_acct = customer.registered_user_acct
        
    
    return render_template('merchant/crm/manage_customer/customer_biodata.html', 
                           page_title           = gettext('Customer Biodata'),
                           user_acct            = registered_user_acct.to_dict(),
                           post_url             = url_for('merchant_manage_customer_bp.customer_biodata_post'),
                           )     

@merchant_manage_customer_bp.route('/customer-biodata', methods=['post'])
@request_form
def customer_biodata_post(request_form):
    logger.debug('--- submit customer_biodata_post data ---')
    customer_biodata_data = request_form
    
    logger.debug('customer_biodata_data=%s', customer_biodata_data)
    
    customer_biodata_form = CustomerBiodataForm(customer_biodata_data)
    user_key = customer_biodata_form.user_key.data
    
    logger.debug('user_key=%s', user_key)
    
    try:
        if is_not_empty(user_key):
            if customer_biodata_form.validate():
                db_client = create_db_client(caller_info="customer_biodata_post")
                with db_client.context():   
                    user_acct = User.fetch(user_key)
                    logger.debug('user_acct=%s', user_acct)
                    if user_acct:
                        birth_date              = customer_biodata_form.birth_date.data
                        gender                  = customer_biodata_form.gender.data    
                        
                        is_dob_changed          = user_acct.birth_date!=birth_date
                        is_gender_changed       = user_acct.gender!=gender
                        
                        logger.debug('changed birth_date=%s', birth_date)
                        logger.debug('original birth_date=%s', user_acct.birth_date)
                        
                        logger.debug('changed gender=%s', gender)
                        logger.debug('original gender=%s', user_acct.gender)
                        
                        logger.debug('is_dob_changed=%s', is_dob_changed)
                        logger.debug('is_gender_changed=%s', is_gender_changed)
                        
                        
                        if is_dob_changed or is_gender_changed:
                            User.update_biodata(user_acct, 
                                                gender      = customer_biodata_form.gender.data,
                                                birth_date  = customer_biodata_form.birth_date.data,
                                                )
                            update_customer_data(user_acct)
                                                
                            logger.debug('going to check user birthday reward')
                            check_user_joined_merchant_birthday_reward(user_acct)
                
                return create_rest_message(gettext('Customer biodata have been updated'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = customer_biodata_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete customer data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to update customer details due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  

@merchant_manage_customer_bp.route('/customer-member-kpi', methods=['GET'])
@login_required
@request_values
def customer_member_kpi(request_values): 
    customer_key = request_values.get('customer_key')
    
    db_client = create_db_client(caller_info="customer_member_kpi")
    configured_tag_list                     = []
    merchant_membership_keys_list           = []
    customer_membership_details_list        = []
    customer_tier_membership_details_list   = []
    with db_client.context():
        customer            = Customer.fetch(customer_key)
        customer_details    = customer.to_dict()
        merchant_acct       = customer.registered_merchant_acct
        merchant_tag_list   = MerchantTagging.list_by_merchant_account(merchant_acct)
        member_tags_list    = customer.tags_list or []
        
        result              = CustomerMembership.list_by_customer(customer)
        if is_not_empty(result):
            for r in result:
                merchant_membership_keys_list.append(r.merchant_membership_key)
                customer_membership_details_list.append(r.to_dict())
        
        result = CustomerTierMembership.list_by_customer(customer)
        if is_not_empty(result):
            for r in result:
                customer_tier_membership_details_list.append(r.to_dict())
    
    for t in merchant_tag_list:
        configured_tag_list.append(t.label)
    
    logger.debug('customer_membership_details_list=%s', customer_membership_details_list)
    
    return render_template('merchant/crm/manage_customer/customer_member_kpi.html', 
                           page_title                               = gettext('Member KPI'),
                           customer                                 = customer_details,
                           configured_tag_list                      = configured_tag_list,
                           merchant_membership_keys_list            = merchant_membership_keys_list,
                           customer_membership_details_list         = customer_membership_details_list,
                           customer_tier_membership_details_list    = customer_tier_membership_details_list,
                           member_tags_list                         = member_tags_list,
                           post_url                                 = url_for('merchant_manage_customer_bp.customer_member_kpi_post'),
                           )

@merchant_manage_customer_bp.route('/customer-member-kpi', methods=['post'])
@request_form
def customer_member_kpi_post(request_form):
    logger.debug('--- submit customer_member_kpi_post data ---')
    customer_kpi_data = request_form
    
    logger.debug('customer_kpi_data=%s', customer_kpi_data)
    
    customer_member_kpi_form = CustomerMemberKPIForm(customer_kpi_data)
    customer_key = customer_member_kpi_form.customer_key.data
    
    logger.debug('customer_key=%s', customer_key)
    
    try:
        if is_not_empty(customer_key):
            if customer_member_kpi_form.validate():
                db_client = create_db_client(caller_info="customer_member_kpi_post")
                with db_client.context():   
                    customer_acct   = Customer.fetch(customer_key)
                    logger.debug('customer_acct=%s', customer_acct)
                    tags_list = customer_member_kpi_form.tags_list.data
                    
                    '''
                    membership_key_list = customer_member_kpi_form.membership_key.data
                    if is_not_empty(membership_key_list):
                        membership_key_list = membership_key_list.split(',')
                        
                        membership_key_list = [x for x in membership_key_list if x]
                        
                    tier_membership_key = customer_member_kpi_form.tier_membership_key.data
                    '''
                    
                    if customer_acct:
                        Customer.update_KPI(customer_acct, tags_list=tags_list)
                        
                
                return create_rest_message(gettext('Customer member KPI have been updated'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = customer_member_kpi_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete customer data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to update customer member KPI due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
     

@merchant_manage_customer_bp.route('/customer-member-reward', methods=['GET'])
@login_required
@request_values
def customer_member_reward(request_values): 
    customer_key = request_values.get('customer_key')
    
    selected_language   = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    currency_details    = get_merchant_configured_currency_details()
    prepaid_amount      = .0
    db_client           = create_db_client(caller_info="customer_member_reward")
    
    customer_program_tier_status_summary_list = []
    
    with db_client.context():
        customer                = Customer.fetch(customer_key)
        
        if customer.prepaid_summary:
            prepaid_amount = customer.prepaid_summary.get('amount')
        
        customer_details        = customer.to_dict()
        
        customer_tier_reward_program_summary_list = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
        
        logger.debug('customer_tier_reward_program_summary_list=%s', customer_tier_reward_program_summary_list)
        
        if customer_tier_reward_program_summary_list:
            for ctrps in customer_tier_reward_program_summary_list:
                customer_program_tier_status_summary_list.append(ctrps.to_program_tier_status_summary())
        
        
    reward_format_json_list     = get_reward_format_json(selected_language)
    reward_format_dict          = {}
    for j in reward_format_json_list:
        reward_format_dict[j.get('code')] = j.get('label')
    
    
    
    return render_template('merchant/crm/manage_customer/customer_member_reward.html', 
                           page_title                                   = gettext('Member Reward'),
                           customer                                     = customer_details,
                           reward_format_dict                           = reward_format_dict,
                           currency_details                             = currency_details,
                           prepaid_amount                               = prepaid_amount,
                           customer_program_tier_status_summary_list    = customer_program_tier_status_summary_list,
                           )
    
def update_customer_data(user_acct, update_upstream=True):
    
    customer_acct_list = Customer.list_by_user_account(user_acct)
    if customer_acct_list:
        for c in customer_acct_list:
            c.update_from_user_acct(user_acct)
            
            if update_upstream:
                create_merchant_registered_customer_upstream_for_merchant(c)
                create_registered_customer_upstream_for_system(c)
    
@merchant_manage_customer_bp.route('/customer/<customer_key>', methods=['DELETE'])
@login_required
def delete_customer(customer_key): 
    logger.debug('---read_customer---')
    
    db_client = create_db_client(caller_info="add_customer_post")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            customer.key.delete()
            
    return create_rest_message(gettext('Merchant account have been deleted'), status_code=StatusCode.OK)


@merchant_manage_customer_bp.route('/redeem-code/<redeem_code>', methods=['DELETE'])
@login_required
def delete_customer_entitled_voucher(redeem_code): 
    logger.debug('---delete_customer_entitled_voucher---')
    
    @model_transactional(desc='delete_customer_entitled_voucher customer transaction')
    def __start_transaction():
        customer_entitled_voucher = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
        customer = customer_entitled_voucher.entitled_customer_entity
        logger.debug('customer_entitled_voucher=%s', customer_entitled_voucher)
        if customer_entitled_voucher:
            customer_entitled_voucher.remove()
            
            update_customer_entiteld_voucher_summary_after_removed_voucher(customer.entitled_voucher_summary, customer_entitled_voucher)
            customer.put()
            
            create_removed_customer_voucher_to_upstream_for_merchant(customer_entitled_voucher)
    
    db_client = create_db_client(caller_info="delete_customer_entitled_voucher")
    with db_client.context():
        __start_transaction()
            
            
    return create_rest_message(gettext('Voucher have been deleted'), status_code=StatusCode.OK)

@merchant_manage_customer_bp.route('/ticket-key/<ticket_key>', methods=['DELETE'])
@login_required
def delete_customer_entitled_lucky_draw_ticket(ticket_key): 
    logger.debug('---delete_customer_entitled_lucky_draw_ticket---, ticket_key=%s', ticket_key)
    
    @model_transactional(desc='delete_customer_entitled_lucky_draw_ticket')
    def __start_transaction():
        lucky_draw_ticket = LuckyDrawTicket.get_by_ticket_key(ticket_key)
        #customer = lucky_draw_ticket.customer_acct_entity
        
        if lucky_draw_ticket:
            #lucky_draw_ticket.remove(customer_acct=customer)
            lucky_draw_ticket.remove()
        else:
            logger.warn('ticket is not found')
            
    
    db_client = create_db_client(caller_info="delete_customer_entitled_lucky_draw_ticket")
    with db_client.context():
        __start_transaction()
            
            
    return create_rest_message(gettext('Ticket have been deleted'), status_code=StatusCode.OK)

    
@merchant_manage_customer_bp.route('/reset-customer-password', methods=['get'])
@login_required
@request_values
def reset_customer_password(request_values):
    post_url  = url_for('merchant_manage_customer_bp.reset_customer_password_post')
    customer_key = request_values.get('customer_key')
    return reset_customer_password_function(customer_key, post_url)
    
def reset_customer_password_function(customer_key, post_url):     
    
    return render_template('shared/reset_password.html',
                           page_title               = gettext('Reset Password'),
                           post_url                 = post_url,
                           key                      = customer_key,
                           reset_customer_password  = True,
                           )
    
@merchant_manage_customer_bp.route('/reset-customer-password', methods=['post'])
@login_required
@request_form
def reset_customer_password_post(request_form):
    return reset_customer_password_post_function(request_form)

def reset_customer_password_post_function(request_form):    
    logger.debug('--- reset_customer_password_post_function ---')
    try:
        customer_details_data = request_form
    
        logger.debug('user_details_data=%s', customer_details_data)
        customer_details_form   = ResetCustomerPasswordForm(customer_details_data)
        customer_key            = customer_details_form.key.data
        password                = customer_details_form.password.data
        confirm_password        = customer_details_form.confirm_password.data
        
        if is_not_empty(customer_key):
            if is_not_empty(password) and password==confirm_password:
                db_client = create_db_client(
                                             caller_info="reset_customer_password_post_function")
                with db_client.context():   
                    customer = Customer.fetch(customer_key)
                    user_acct = customer.registered_user_acct
                    if user_acct:
                        user_acct.reset_password(password)
                    
                if user_acct:
                    
                    return create_rest_message(gettext('Customer password have been reset'), 
                                               status_code=StatusCode.OK)
            else:
                return create_rest_message(gettext("Password and confirm password must be matched or not empty"), 
                                           status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete customer data"), 
                                       status_code=StatusCode.BAD_REQUEST)        
        
            
    except:
        logger.error('Fail to reset customer password due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST) 
    
@merchant_manage_customer_bp.route('/customer/search/page-size/<limit>/page/<page_no>', methods=['POST', 'GET'])
@login_required
@request_values
@request_form
def search_customer(request_values, request_form, limit, page_no): 
    logger.debug('---search_customer---')
    #encrypted_search_customer_data  = request.args.get('encrypted_search_customer_data') or {}
    encrypted_search_customer_data  = request_values.get('encrypted_search_customer_data') or {}
    
    logger.debug('encrypted_search_customer_data=%s', encrypted_search_customer_data)
    
    if encrypted_search_customer_data:
        search_customer_data            = decrypt_json(encrypted_search_customer_data)
        search_customer_form            = CustomerSearchForm(data=search_customer_data)
        logger.debug('search_customer_data from encrypted_search_customer_data=%s', search_customer_data)
        
    else:
        search_customer_data            = request_form
        search_customer_form            = CustomerSearchForm(search_customer_data)
        #encrypted_search_customer_data  = encrypt_json(search_customer_data).decode("utf-8")
        encrypted_search_customer_data  = encrypt_json(search_customer_data) 
    
        logger.debug('search_customer_data from search form=%s', search_customer_data)
        
        
        logger.debug('encrypted_search_customer_data after encrypted=%s', encrypted_search_customer_data)
    
    
    customer_list               = []
    total_count                 = 0
    
    page_no_int                 = int(page_no)
    limit_int                   = int(limit)
    
    if search_customer_form.validate():
        name                        = search_customer_form.name.data
        mobile_phone                = search_customer_form.mobile_phone.data
        email                       = search_customer_form.email.data
        reference_code              = search_customer_form.reference_code.data
        merchant_reference_code     = search_customer_form.merchant_reference_code.data
        merchant_tagging            = search_customer_form.merchant_tagging.data
        registered_date_start       = search_customer_form.registered_date_start.data
        registered_date_end         = search_customer_form.registered_date_end.data
        
        
        cursor                          = request_values.get('cursor')
        previous_cursor                 = request_values.get('previous_cursor')
        
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")
            
        if reference_code:
            reference_code = reference_code.replace(" ", "")
            
        if merchant_reference_code:
            merchant_reference_code = merchant_reference_code.replace(" ", "")        
        
        logger.debug('name=%s', name)
        logger.debug('mobile_phone=%s', mobile_phone)
        logger.debug('email=%s', email)
        logger.debug('reference_code=%s', reference_code)
        logger.debug('merchant_reference_code=%s', merchant_reference_code)
        logger.debug('registered_date_start=%s', registered_date_start)
        logger.debug('registered_date_end=%s', registered_date_end)
        logger.debug('merchant_tagging=%s', merchant_tagging)
        
        logger.debug('limit=%s', limit)
        
        logger.debug('cursor=%s', cursor)
        logger.debug('previous_cursor=%s', previous_cursor)
        
        
        db_client = create_db_client(caller_info="search_customer")
        
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        try:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                (search_results, total_count, next_cursor)  = Customer.search_merchant_customer(merchant_acct, 
                                                                                                name                    = name, 
                                                                                                email                   = email, 
                                                                                                mobile_phone            = mobile_phone, 
                                                                                                reference_code          = reference_code,
                                                                                                merchant_reference_code = merchant_reference_code,
                                                                                                registered_date_start   = registered_date_start,
                                                                                                registered_date_end     = registered_date_end,
                                                                                                merchant_tagging        = merchant_tagging,
                                                                                                limit                   = limit_int,
                                                                                                start_cursor            = cursor,
                                                                                                )
                
                for r in search_results:
                    customer_list.append(r.to_dict())
        except:
            logger.error('Fail to search customer due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to search customer'), status_code=StatusCode.BAD_REQUEST)
        
        prepaid_program_available = False    
        if merchant_acct.prepaid_configuration:
            prepaid_program_available = True
        
        logger.debug('total_count=%s', total_count)
        logger.debug('customer_list=%s', customer_list)
    else:
        logger.debug('search form invalid')
        error_message = search_customer_form.create_rest_return_error_message()
                
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
        
            
    pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                     = next_cursor, 
                                previous_cursor                 = previous_cursor,
                                current_cursor                  = cursor,
                                encrypted_search_customer_data  = encrypted_search_customer_data,
                              ) 
    pages       = pager.get_pages()
    
    return render_template('merchant/crm/manage_customer/customer_listing_content.html', 
                               customer_list                = customer_list,
                               end_point                    = 'merchant_manage_customer_bp.search_customer',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#customer_search_list_div',
                               prepaid_program_available    = prepaid_program_available,
                               )           


@merchant_manage_customer_bp.route('/customer-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_customer(request_values, limit, page_no): 
    logger.debug('---list_customer---')
    
    logger.debug('page_no=%s', page_no)
    
    cursor                          = request_values.get('cursor')
    previous_cursor                 = request_values.get('previous_cursor')
    
    page_no_int     = int(page_no, 10)
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    total_count     = 0
    limit_int       = int(limit, 10)
    customer_list   = []
    result          = []
    
    logger.debug('list_customer: limit_int=%d', limit_int)
    
    try:
        logged_in_merchant_user = get_loggedin_merchant_user_account()
    
        db_client = create_db_client(caller_info="list_customer")
        try:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                result,next_cursor  = Customer.list_merchant_customer(merchant_acct, offset=offset, limit=limit_int, start_cursor=cursor, return_with_cursor=True)
                total_count         = Customer.count_merchant_customer(merchant_acct)
                
                for r in result:
                    customer_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_customer: total_count=%d', total_count)
        
        prepaid_program_available = False    
        if merchant_acct.prepaid_configuration:
            prepaid_program_available = True
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                next_cursor                   = next_cursor, 
                                previous_cursor               = previous_cursor, 
                                current_cursor                = cursor,
                              )
        pages       = pager.get_pages()
        
        return render_template('merchant/crm/manage_customer/customer_listing_content.html', 
                               customer_list                = customer_list,
                               end_point                    = 'merchant_manage_customer_bp.list_customer',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#customer_search_list_div',
                               prepaid_program_available    = prepaid_program_available,
                               )
    
    except:
        logger.error('Fail to list customer due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   
    
@merchant_manage_customer_bp.route('/list-granted-outlet', methods=['GET'])
#@cache.cached(timeout=50)
def list_granted_outlet_json():
    logging.debug('---list_granted_outlet_code_json--- ')
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    granted_outlet_list     = []
    
    if logged_in_merchant_user.get('is_admin'):
        db_client = create_db_client(caller_info="list_granted_outlet_json")
            
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            merchant_outlet_list    = Outlet.list_by_merchant_acct(merchant_acct)
            
            for o in merchant_outlet_list:
                
                granted_outlet_list.append({
                                                'code'  : o.key_in_str,
                                                'label' : o.name,
                                                })
    else:
        
        granted_outlet          = logged_in_merchant_user.get('granted_outlet')
        
        db_client = create_db_client(caller_info="list_granted_outlet_json")
            
        with db_client.context():
            merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            merchant_outlet_list    = Outlet.list_by_merchant_acct(merchant_acct)
            
            for outlet in merchant_outlet_list:
                outlet_key = outlet.key_in_str
                if outlet_key in granted_outlet:
                    granted_outlet_list.append({
                                                'code'  : outlet_key,
                                                'label' : outlet.name,
                                                })
                
    
    data_list_in_json  = json.dumps(granted_outlet_list, sort_keys = True, separators = (',', ': '))
    
    json_resp = create_cached_response(data_list_in_json, 
                                  mime_type             = MINE_TYPE_JSON,
                                  )
    
    return json_resp
     
  
@merchant_manage_customer_bp.route('/customer-transaction-history/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_customer_transaction_history(request_values, limit, page_no): 
    logger.debug('---list_customer_transaction_history---')
    
    logger.debug('page_no=%s', page_no)
    
    customer_key                = request_values.get('customer_key')
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    customer_transaction_list   = []
    next_cursor                 = None
    
    logger.debug('list_customer_transaction: customer_key=%s', customer_key)
    logger.debug('list_customer_transaction: cursor=%s', cursor)
    logger.debug('list_customer_transaction: limit_int=%d', limit_int)
    
    try:
        db_client = create_db_client(caller_info="list_customer_transaction")
        try:
            with db_client.context():
                customer                    = Customer.fetch(customer_key)
                merchant_acct               = customer.registered_merchant_acct
                (result, next_cursor)       = CustomerTransaction.list_customer_transaction(customer, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                total_count                 = CustomerTransaction.count_customer_transaction(customer)
                
                for r in result:
                    customer_transaction_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_customer_transaction: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  customer_key                  = customer_key
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('merchant/crm/customer_transaction/customer_transaction_listing.html', 
                               customer_transaction_list    = customer_transaction_list,
                               end_point                    = 'merchant_manage_customer_bp.list_customer_transaction_history',
                               pager                        = pager,
                               pages                        = pages,
                               customer_key                 = customer_key,
                               pagination_target_selector   = '#customer_transaction_listing_div',
                               merchant_acct                = merchant_acct,
                               )
    
    except:
        logger.error('Fail to list customer due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
  
@merchant_manage_customer_bp.route('/customer-redemption-history/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_values
def list_customer_redemption_history(request_values, limit, page_no): 
    logger.debug('---list_customer_redemption_history---')
    
    logger.debug('page_no=%s', page_no)
    
    customer_key                = request_values.get('customer_key')
    cursor                      = request_values.get('cursor')
    previous_cursor             = request_values.get('previous_cursor')
    page_no_int                 = int(page_no, 10)
    
    total_count                 = 0
    limit_int                   = int(limit, 10)
    #limit_int                   = 2
    customer_redemption_list   = []
    next_cursor                 = None
    
    logger.debug('list_customer_redemption: customer_key=%s', customer_key)
    logger.debug('list_customer_redemption: cursor=%s', cursor)
    logger.debug('list_customer_redemption: limit_int=%d', limit_int)
    
    try:
        db_client = create_db_client(caller_info="list_customer_redemption_history")
        try:
            with db_client.context():
                customer                    = Customer.fetch(customer_key)
                merchant_acct               = customer.registered_merchant_acct
                (result, next_cursor)       = CustomerRedemption.list_customer_redemption(customer, limit=limit_int, return_with_cursor=True, start_cursor=cursor)
                total_count                 = CustomerRedemption.count_customer_redemption(customer)
                
                for r in result:
                    customer_redemption_list.append(r.to_dict())
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        logger.debug('list_customer_redemption: total_count=%d', total_count)
        
        pager       = CursorPager(page_no_int, total_count, limit_int, 
                                  next_cursor                   = next_cursor, 
                                  previous_cursor               = previous_cursor, 
                                  current_cursor                = cursor,
                                  customer_key                  = customer_key,
                                  
                                  )
        pages       = pager.get_pages()
        
        
        
        return render_template('merchant/crm/customer_redemption/customer_redemption_listing.html', 
                               customer_redemption_list     = customer_redemption_list,
                               end_point                    = 'merchant_manage_customer_bp.list_customer_redemption_history',
                               pager                        = pager,
                               pages                        = pages,
                               customer_key                 = customer_key,
                               pagination_target_selector   = '#customer_redemption_listing_div',
                               merchant_acct                 = merchant_acct,
                               )
    
    except:
        logger.error('Fail to list customer due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)   

@merchant_manage_customer_bp.route('/revert-transaction/<transaction_key>', methods=['post'])
def revert_transaction_post(transaction_key):
    logger.debug('--- submit revert_transaction_post ---')
    
    logger.debug('transaction_key=%s', transaction_key)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    try:
        db_client               = create_db_client(caller_info="revert_transaction_post")
        revert_status           = False
        reverted_datetime_utc   = datetime.utcnow()
        reverted_datetime       = datetime.now()
            
        logger.debug('revert_redemption_post: reverted_datetime_utc=%s', reverted_datetime_utc)
        logger.debug('revert_redemption_post: reverted_datetime=%s', reverted_datetime)
        logger.debug('revert_redemption_post: transaction_key=%s', transaction_key)
        with db_client.context():   
            customer_transction = CustomerTransaction.fetch(transaction_key)
            customer_transction.reverted_datetime = reverted_datetime_utc
            
            logger.debug('revert_transaction_post: reverted_datetime=%s', reverted_datetime)
            
            if customer_transction:
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                revert_status = __revert_customer_transaction(customer_transction, merchant_user, reverted_datetime_utc)
                
                logger.debug('revert_status=%s', revert_status)
            
            create_merchant_customer_transaction_upstream_for_merchant(customer_transction, Reverted=True)
                
        if revert_status:
            return create_rest_message(gettext('Customer transaction have been reverted'),
                                                reverted_datetime_text = pretty_datetime_filter(None, reverted_datetime), 
                                                status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext('Failed to revert transaction'), status_code=StatusCode.BAD_REQUEST)
        
        if customer_transction is None:
            return create_rest_message(gettext('Invalid transaction key'), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext('Customer transaction have been reverted successfully'), status_code=StatusCode.OK)
            
    except:
        logger.error('Fail to revert customer transaction due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to revert customer transaction'), status_code=StatusCode.BAD_REQUEST)    
    
@model_transactional(desc="__revert_customer_transaction")
def __revert_customer_transaction(customer_transction, reverted_by, reverted_datetime):     
    return revert_transaction(customer_transction, reverted_by, reverted_datetime=reverted_datetime)    

    
@merchant_manage_customer_bp.route('/revert-redemption/<redemption_key>', methods=['post'])
def revert_redemption_post(redemption_key):
    logger.debug('--- submit revert_redemption_post ---')   
    
    db_client       = create_db_client(caller_info="revert_redemption_post")
    
    try:
        reverted_datetime_utc   = datetime.utcnow()
        reverted_datetime       = datetime.now()
            
        logger.debug('revert_redemption_post: reverted_datetime_utc=%s', reverted_datetime_utc)
        logger.debug('revert_redemption_post: reverted_datetime=%s', reverted_datetime)
        
        with db_client.context():
            customer_redemption = CustomerRedemption.fetch(redemption_key)
        
            if customer_redemption:
                logged_in_merchant_user = get_loggedin_merchant_user_account()
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                
                __revert_customer_redemption(customer_redemption, merchant_user, reverted_datetime=reverted_datetime_utc)
                
            
        
        return create_rest_message(gettext('Customer redemption have been reverted'),
                                                    reverted_datetime_text = pretty_datetime_filter(None, reverted_datetime),
                                                    status_code=StatusCode.OK
                                                    )
    except:
        logger.error('Fail to revert customer redemption due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to revert customer redemption'), status_code=StatusCode.BAD_REQUEST)
    
@model_transactional(desc="__revert_customer_redemption")
def __revert_customer_redemption(customer_redemption, reverted_by, reverted_datetime):     
       
    return revert_redemption(customer_redemption, reverted_by, reverted_datetime=reverted_datetime)
     

@merchant_manage_customer_bp.route('/reference-code/qrcode/<reference_code>', methods=['get'])
def view_customer_reference_code_qr(reference_code):
    return render_template("test/qr_code.html", 
                            qr_code = reference_code,
                           )
    
@merchant_manage_customer_bp.route('/voucher/redeem-code/qrcode/<redeem_code>', methods=['get'])
def view_voucher_redeem_code_qr(redeem_code):
    return render_template("test/qr_code.html", 
                            qr_code = redeem_code,
                           )    

        