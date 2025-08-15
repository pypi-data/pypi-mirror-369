'''
Created on 6 May 2025

@author: jacklok
'''

from flask import Blueprint, render_template, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
#from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account,\
    get_preferred_language
from flask.json import jsonify
from trexmodel.models.datastore.partnership_models import PartnerLinked,\
    PartnershipSettings
from trexlib.libs.flask_wtf.request_wrapper import request_values, request_form,\
    request_args
from trexconf.program_conf import is_partnership_current_status_reach,\
    MERCHANT_PARTNERSHIP_STATUS_LINKED,\
    MERCHANT_PARTNERSHIP_STATUS_REQUESTED, MERCHANT_PARTNERSHIP_STATUS_REVIEWED,\
    MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED,\
    MERCHANT_PARTNERSHIP_STATUS_LIMIT_CONFIGURED
from trexadmin.forms.merchant.partnership.merchant_partnership_forms import MerchantPartnerDefineForm,\
    MerchantPartnerConfigurationForm, MerchantPartnerForm
from trexlib.utils.string_util import is_not_empty, is_empty
from trexadmin.controllers.system.system_route_helpers import get_merchant_partnership_status_type_json
from trexadmin.libs.jinja.program_filters import map_label_by_code
from trexmodel.models.datastore.redemption_catalogue_models import RedemptionCatalogue
from trexmail.email_helper import trigger_send_email
from trexconf import conf
from trexmodel.models.merchant_helpers import convert_points_between_merchants

merchant_manage_partnership_setup_bp = Blueprint('merchant_manage_partnership_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/partnership/setup')

#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')


'''
Blueprint settings here
'''


@merchant_manage_partnership_setup_bp.context_processor
def merchant_manage_partnership_setup_bp_inject_settings():
    
    return dict(
                MERCHANT_PARTNERSHIP_STATUS_LINKED              = MERCHANT_PARTNERSHIP_STATUS_LINKED,
                MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED   = MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED,
                MERCHANT_PARTNERSHIP_STATUS_LIMIT_CONFIGURED    = MERCHANT_PARTNERSHIP_STATUS_LIMIT_CONFIGURED,
                MERCHANT_PARTNERSHIP_STATUS_REVIEWED            = MERCHANT_PARTNERSHIP_STATUS_REVIEWED,
                MERCHANT_PARTNERSHIP_STATUS_REQUESTED           = MERCHANT_PARTNERSHIP_STATUS_REQUESTED,
                )

@merchant_manage_partnership_setup_bp.app_template_filter()
def partnership_setup_status_label(code):
    if code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_merchant_partnership_status_type_json(preferred_language)
        
        return map_label_by_code(code_label_json, code) or '-'
    else:
        return ''

@merchant_manage_partnership_setup_bp.route('/merchant-json', methods=['GET'])
@login_required
def merchant_partnership_merchant_in_json():
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="merchant_partnership_settings")
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        merchant_acct_json = merchant_acct.to_dict()
        #logger.debug('>>>>>>>>>>>>>>>>>read merchant details from DB')

    #return jsonify(merchant_acct_json)
    return create_rest_message(status_code=StatusCode.OK, **merchant_acct_json)

@merchant_manage_partnership_setup_bp.route('/search-merchant', methods=['POST'])
@login_required
@request_values
def search_merchant_partner_by_account_code(request_values):
    account_code    = request_values.get('account_code')
    db_client       = create_db_client(caller_info="merchant_partner_lookup_by_account_code")
    logger.debug('account_code=%s', account_code)
    with db_client.context():
        merchant_acct   = MerchantAcct.get_by_account_code(account_code)
        if merchant_acct:
            merchant_acct_json = {
                            'account_code'      : account_code,
                            'company_name'      : merchant_acct.company_name,
                            'merchant_acct_key' : merchant_acct.key_in_str,
                            }
    logger.debug('merchant_acct_json=%s', merchant_acct_json)
    if merchant_acct_json:
        return jsonify(merchant_acct_json)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        
    
@merchant_manage_partnership_setup_bp.route('/', methods=['GET'])
@login_required
def merchant_partnership_setup(): 
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    linked_partners_list    = []
    db_client = create_db_client(caller_info="merchant_partnership_settings")
    is_partnership_enabled = False
    with db_client.context():
        merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result                  = PartnerLinked.list_from_merchant_by_merchant_acct(merchant_acct)
        partnership_settings    = PartnershipSettings.get_by_merchant_acct(merchant_acct)
        if partnership_settings:
            is_partnership_enabled = partnership_settings.is_enabled
        
        for r in result:
            linked_partners_list.append(r.to_dict())
    
    return render_template('merchant/partnership/setup/merchant_manage_partnership.html',
                           page_title               = gettext('Manage Partnership'),
                           add_partner_url          = url_for('merchant_manage_partnership_setup_bp.create_partnership'),
                           linked_partners_list     = linked_partners_list,
                           is_partnership_enabled   = is_partnership_enabled,
                           
                           )
    
@merchant_manage_partnership_setup_bp.route('/from-merchant', methods=['GET'])
@login_required
def merchant_partnership_from_merchant_listing(): 
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    linked_partners_list    = []
    db_client = create_db_client(caller_info="merchant_partnership_from_merchant_listing")

    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = PartnerLinked.list_from_merchant_by_merchant_acct(merchant_acct)
        
        for r in result:
            linked_partners_list.append(r.to_dict())
    
    return render_template('merchant/partnership/setup/merchant_partnership_from_merchant_listing_content.html',
                           linked_partners_list = linked_partners_list,
                           add_partner_url      = url_for('merchant_manage_partnership_setup_bp.create_partnership'),
                           ) 
    
@merchant_manage_partnership_setup_bp.route('/from-partner', methods=['GET'])
@login_required
def merchant_partnership_from_partner_listing():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    linked_partners_list    = []
    db_client = create_db_client(caller_info="merchant_partnership_from_partner_listing")

    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          =  PartnerLinked.list_from_partner_by_merchant_acct(merchant_acct)
        
        for r in result:
            linked_partners_list.append(r.to_dict())
    
    return render_template('merchant/partnership/setup/merchant_partnership_from_partner_listing_content.html',
                           linked_partners_list = linked_partners_list,
                           add_partner_url      = url_for('merchant_manage_partnership_setup_bp.create_partnership'),
                           )        

@merchant_manage_partnership_setup_bp.route('/create-partner', methods=['GET'])
@login_required
def create_partnership(): 
    
    return render_template('merchant/partnership/setup/create_merchant_partnership.html',
                           define_partner_url           = url_for('merchant_manage_partnership_setup_bp.define_partner_post'),
                           configure_partnership_url    = url_for('merchant_manage_partnership_setup_bp.configure_partnership_post'),
                           search_merchant_url          = url_for('merchant_manage_partnership_setup_bp.search_merchant_partner_by_account_code'),
                           show_partnership_review_url  = url_for('merchant_manage_partnership_setup_bp.load_partnership_review'),
                           is_view_mode                 = False,
                           )  

@merchant_manage_partnership_setup_bp.route('/edit-partnership/<partnership_key>', methods=['GET'])
@login_required
def edit_partnership(partnership_key): 
    db_client = create_db_client(caller_info="edit_partnership")
    configured_catalogue_with_label_list = []
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    with db_client.context():
        partnership     = PartnerLinked.fetch(partnership_key)
        status          = partnership.status
        
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        catalogue_list  = RedemptionCatalogue.list_published_partner_exclusive_by_merchant_account(merchant_acct)
        
        for r in partnership.redemption_catalogue_list:
            for c in catalogue_list:
                if c.key_in_str == r:
                    configured_catalogue_with_label_list.append(c.label)
        
        partnership     = partnership.to_dict()
        
        logger.debug('status=%s', status)
    
    DEFINE_PARTNER_COMPLETED_STATUS                 = is_partnership_current_status_reach(MERCHANT_PARTNERSHIP_STATUS_LINKED, status)
    REDEEM_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS   = is_partnership_current_status_reach(MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED, status)
    LIMIT_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS    = is_partnership_current_status_reach(MERCHANT_PARTNERSHIP_STATUS_LIMIT_CONFIGURED, status)
    REVIEW_PARTNERSHIP_COMPLETED_STATUS             = is_partnership_current_status_reach(MERCHANT_PARTNERSHIP_STATUS_REVIEWED, status)
    REQUEST_PARTNERSHIP_COMPLETED_STATUS            = is_partnership_current_status_reach(MERCHANT_PARTNERSHIP_STATUS_REQUESTED, status)
    
    logger.debug('DEFINE_PARTNER_COMPLETED_STATUS=%s', DEFINE_PARTNER_COMPLETED_STATUS)
    logger.debug('REDEEM_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS=%s', REDEEM_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS)
    logger.debug('LIMIT_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS=%s', LIMIT_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS)
    logger.debug('REVIEW_PARTNERSHIP_COMPLETED_STATUS=%s', REVIEW_PARTNERSHIP_COMPLETED_STATUS)
    logger.debug('REQUEST_PARTNERSHIP_COMPLETED_STATUS=%s', REQUEST_PARTNERSHIP_COMPLETED_STATUS)
    
    return render_template('merchant/partnership/setup/create_merchant_partnership.html',
                           define_partner_url                       = url_for('merchant_manage_partnership_setup_bp.define_partner_post'),
                           configure_partnership_url                = url_for('merchant_manage_partnership_setup_bp.configure_partnership_post'),
                           #show_partnership_redeem_limit_url        = url_for('merchant_manage_partnership_setup_bp.load_partnership_redeem_limit', partnership_key=partnership_key),
                           show_partnership_review_url              = url_for('merchant_manage_partnership_setup_bp.load_partnership_review'),
                           merchant_partnership_submit_request_url  = url_for('merchant_manage_partnership_setup_bp.submit_merchant_partnership_request_post', partnership_key=partnership_key),
                           partnership                              = partnership,
                           is_view_mode                             = False,
                           is_edit_mode                             = True,
                           completed_status                         = status, 
                           
                           configured_catalogue_list                = configured_catalogue_with_label_list,
                           
                           DEFINE_PARTNER_COMPLETED_STATUS                  = DEFINE_PARTNER_COMPLETED_STATUS,
                           REDEEM_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS    = REDEEM_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS,
                           LIMIT_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS     = LIMIT_CONFIGURE_PARTNERSHIP_COMPLETED_STATUS,
                           REVIEW_PARTNERSHIP_COMPLETED_STATUS              = REVIEW_PARTNERSHIP_COMPLETED_STATUS,
                           REQUEST_PARTNERSHIP_COMPLETED_STATUS             = REQUEST_PARTNERSHIP_COMPLETED_STATUS,
                           
                           
                           ) 


@merchant_manage_partnership_setup_bp.route('/view-requested-partnership/<partnership_key>', methods=['GET'])
@login_required
def view_requested_partnership(partnership_key): 
    db_client = create_db_client(caller_info="view_requested_partnership")
    configured_catalogue_list = []
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    with db_client.context():
        partnership     = PartnerLinked.fetch(partnership_key)
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        
        merchant_partnership_settings               = PartnershipSettings.get_by_merchant_acct(merchant_acct)
        requested_merchant_acct                     = partnership.requested_from_merchant_entity
        requested_merchant_partnership_settings     = PartnershipSettings.get_by_merchant_acct(requested_merchant_acct)
        
        catalogue_list  = RedemptionCatalogue.list_published_partner_exclusive_by_merchant_account(requested_merchant_acct)
        
        merchant_point_worth_value_in_currency              = merchant_partnership_settings.point_worth_value_in_currency
        requested_merchant_point_worth_value_in_currency    = requested_merchant_partnership_settings.point_worth_value_in_currency
        
        for r in partnership.redemption_catalogue_list:
            for c in catalogue_list:
                if c.key_in_str == r:
                    
                    catalogue_dict = c.to_dict()
                    
                    for catalogue_item_dict in catalogue_dict.get('catalogue_items'):
                        redeem_reward_amount = catalogue_item_dict.get('redeem_reward_amount')
                        merchant_redeem_reward_amount = convert_points_between_merchants(redeem_reward_amount, requested_merchant_point_worth_value_in_currency, merchant_point_worth_value_in_currency)
                        catalogue_item_dict['merchant_redeem_reward_amount'] = merchant_redeem_reward_amount
                        
                    configured_catalogue_list.append(catalogue_dict)
        
        partnership     = partnership.to_dict()
        
    
    return render_template('merchant/partnership/setup/view_requested_partnership.html',
                           partnership                  = partnership,
                           configured_catalogue_list    = configured_catalogue_list,
                           requested_merchant_acct_key  = requested_merchant_acct.key_in_str,
                           
                           approve_partnership_url      = url_for('merchant_manage_partnership_setup_bp.approve_merchant_partnership_request_post'),
                           
                           merchant_point_worth_value_in_currency           = merchant_point_worth_value_in_currency,
                           requested_merchant_point_worth_value_in_currency = requested_merchant_point_worth_value_in_currency,
                           )     
    

@merchant_manage_partnership_setup_bp.route('/redeem-limit/<partnership_key>', methods=['GET'])
@login_required
def load_partnership_redeem_limit(partnership_key): 
    db_client = create_db_client(caller_info="load_partnership_redeem_limit_content")

    with db_client.context():
        partnership     = PartnerLinked.fetch(partnership_key)
        status          = partnership.status
        partnership     = partnership.to_dict()
        
        logger.debug('status=%s', status)
    
    
    return render_template('merchant/partnership/setup/merchant_partnership_limit_redeem_configuration_content.html',
                           define_partnership_redeem_limit_url      = url_for('merchant_manage_partnership_setup_bp.define_partner_post'),
                           partnership                              = partnership,
                           is_view_mode                             = False,
                           is_edit_mode                             = True,
                           completed_status                         = status, 
                           ) 
    
@merchant_manage_partnership_setup_bp.route('/review', methods=['GET'])
@login_required
@request_args
def load_partnership_review(request_args): 
    partnership_key = request_args.get('partnership_key')
    db_client = create_db_client(caller_info="load_partnership_review")
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    configured_catalogue_with_label_list = []
    with db_client.context():
        partnership     = PartnerLinked.fetch(partnership_key)
        status          = partnership.status
        
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        catalogue_list  = RedemptionCatalogue.list_published_partner_exclusive_by_merchant_account(merchant_acct)
        
        for r in partnership.redemption_catalogue_list:
            for c in catalogue_list:
                if c.key_in_str == r:
                    configured_catalogue_with_label_list.append(c.label)
            
        partnership     = partnership.to_dict()
        
        logger.debug('status=%s', status)
    
    
    return render_template('merchant/partnership/setup/merchant_partnership_review_content.html',
                           merchant_partnership_submit_request_url  = url_for('merchant_manage_partnership_setup_bp.submit_merchant_partnership_request_post', partnership_key=partnership_key),
                           partnership                              = partnership,
                           is_view_mode                             = False,
                           is_edit_mode                             = True,
                           completed_status                         = status, 
                           configured_catalogue_list                = configured_catalogue_with_label_list,
                           )       


    
@merchant_manage_partnership_setup_bp.route('/view-partner/<partnership_key>', methods=['GET'])
@login_required
def view_partnership(partnership_key): 
    db_client = create_db_client(caller_info="view_partnership")
    configured_catalogue_with_label_list = []
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    with db_client.context():
        partnership     = PartnerLinked.fetch(partnership_key)
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        catalogue_list  = RedemptionCatalogue.list_published_partner_exclusive_by_merchant_account(merchant_acct)
        
        for r in partnership.redemption_catalogue_list:
            for c in catalogue_list:
                if c.key_in_str == r:
                    configured_catalogue_with_label_list.append(c.label)
        
        partnership     = partnership.to_dict()
        
    return render_template('merchant/partnership/setup/create_merchant_partnership.html',
                           partnership                              = partnership,
                           is_view_mode                             = True,
                           
                           configured_catalogue_list                = configured_catalogue_with_label_list,

                           DEFINE_PARTNER_COMPLETED_STATUS          = True,
                           CONFIGURE_PARTNERSHIP_COMPLETED_STATUS   = True,
                           REVIEW_PARTNERSHIP_COMPLETED_STATUS      = True,
                           REQUEST_PARTNERSHIP_COMPLETED_STATUS     = True,
                           )         

@merchant_manage_partnership_setup_bp.route('/define-partner', methods=['POST'])
@login_required
@request_form
def define_partner_post(request_form):
    logger.debug('request_form=%s', request_form)
    partner_define_form =  MerchantPartnerDefineForm(request_form)
    
    try:
        if partner_define_form.validate():
            db_client = create_db_client(caller_info="define_partner_post")
            logged_in_merchant_user = get_loggedin_merchant_user_account()
            
            with db_client.context():
                merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                partnership_key         = partner_define_form.partnership_key.data
                partner_merchant_key    = partner_define_form.partner_merchant_key.data
                desc                    = partner_define_form.desc.data
                start_date              = partner_define_form.start_date.data
                end_date                = partner_define_form.end_date.data
                
                logger.debug('partnership_key=%s', partnership_key)
                logger.debug('partner_merchant_key=%s', partner_merchant_key)
                logger.debug('desc=%s', desc)
                logger.debug('start_date=%s', start_date)
                logger.debug('end_date=%s', end_date)
                
                if is_not_empty(partnership_key):
                    partnership = PartnerLinked.fetch(partnership_key)
                    
                    partner_merchant = MerchantAcct.get_or_read_from_cache(partner_merchant_key)
                    if partner_merchant:
                        if partnership: 
                            PartnerLinked.update(partnership, partner_merchant, start_date, end_date, desc=desc, modified_by=merchant_user)
                        else:
                            partnership = PartnerLinked.create(merchant_acct, partner_merchant, start_date, end_date, desc=desc, created_by=merchant_user)
                        
                        return create_rest_message(status_code=StatusCode.OK, partnership_key=partnership.key_in_str)
                    
                    else:
                        return create_rest_message(gettext('Invalid merchant partner'), status_code=StatusCode.BAD_REQUEST)
                else:
                    partner_merchant = MerchantAcct.get_or_read_from_cache(partner_merchant_key)
                    
                    partnership = PartnerLinked.create(merchant_acct, partner_merchant, start_date, end_date, desc=desc, created_by=merchant_user)

                    return create_rest_message(status_code=StatusCode.OK, partnership_key=partnership.key_in_str)
        else:
            return create_rest_message(gettext('Failed to link merchant partner'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Failed to link merchant partner due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to link merchant partner'), status_code=StatusCode.BAD_REQUEST)
            

@merchant_manage_partnership_setup_bp.route('/define-partner-configuration', methods=['POST'])
@login_required
@request_form
def configure_partnership_post(request_form):
    logger.debug('request_form=%s', request_form)
    configure_partnership_form =  MerchantPartnerConfigurationForm(request_form)
    
    try:
        if configure_partnership_form.validate():
            db_client = create_db_client(caller_info="configure_partnership_post")
            
            with db_client.context():
                partnership_key                 = configure_partnership_form.partnership_key.data
                redemption_catalogue_list       = configure_partnership_form.redemption_catalogue_list.data
                limit_redeem                    = configure_partnership_form.limit_redeem.data
                
                redemption_catalogue_list = redemption_catalogue_list.split(',')
                
                logger.debug('partnership_key=%s', partnership_key)
                logger.debug('redemption_catalogue_list=%s', redemption_catalogue_list)
                logger.debug('limit_redeem=%s', limit_redeem)
                
                if is_not_empty(partnership_key):
                    partnership = PartnerLinked.fetch(partnership_key)
                    
                    if partnership:
                        partnership.update_configuration(redemption_catalogue_list, limit_redeem)
                        return create_rest_message(status_code=StatusCode.OK, )
                    
                    else:
                        return create_rest_message(gettext('Invalid merchant partner'), status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message(gettext('Invalid merchant partnership'), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext('Failed to configure merchant partnership'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Failed to configure merchant partnership due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to configure merchant partnership'), status_code=StatusCode.BAD_REQUEST)
    
@merchant_manage_partnership_setup_bp.route('/submit-partnership-request', methods=['POST'])
@login_required
@request_form
def submit_merchant_partnership_request_post(request_form):
    logger.debug('request_form=%s', request_form)
    partnership_form =  MerchantPartnerForm(request_form)
    
    try:
        if partnership_form.validate():
            db_client = create_db_client(caller_info="submit_merchant_partnership_request_post")
            is_request_ready_to_send    = False
            is_valid_partner_merchant   = True
            is_valid_partnership        = True
            logged_in_merchant_user     = get_loggedin_merchant_user_account()
            with db_client.context():
                partnership_key                 = partnership_form.partnership_key.data
                logger.debug('partnership_key=%s', partnership_key)
                
                if is_not_empty(partnership_key):
                    partnership     = PartnerLinked.fetch(partnership_key)
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    if partnership:
                        PartnerLinked.submit_request(partnership, requested_by=merchant_user)
                        partner_merchant = partnership.partner_merchant_entity
                        if partner_merchant:
                            email               = partner_merchant.email
                            contact_name        = partner_merchant.contact_name
                            from_merchant       = partnership.merchant_entity
                            from_merchant_name  = from_merchant.company_name
                            application_name    = conf.APPLICATION_NAME

                            is_request_ready_to_send = True
                    else:
                        is_valid_partner_merchant = False
                else:
                    is_valid_partner_merchant = False
            
            if is_valid_partnership:
                if is_valid_partner_merchant:
                    if is_request_ready_to_send:
                        __send_request_email(email, contact_name, from_merchant_name, application_name)
                        return create_rest_message(status_code=StatusCode.OK, )
                    else:
                        return create_rest_message(gettext('Failed to send partnership request'), status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message(gettext('Invalid partner merchant account'), status_code=StatusCode.BAD_REQUEST)
            else:
                return create_rest_message(gettext('Invalid merchant partnership'), status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message(gettext('Failed to send merchant partnership request'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Failed to configure merchant partnership due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to send merchant partnership request'), status_code=StatusCode.BAD_REQUEST)    


def __send_request_email(email, contact_name, from_merchant_name, application_name, ):
    subject = gettext('Partnership Request from {from_merchant_name}').format(from_merchant_name=from_merchant_name)
    message = gettext('Dear {contact_name},\n\n\tYou have received partnership request from {from_merchant_name}. Please check the request in Partnership module. \n\nThis is auto generated email, please do not reply the email.\n\nFrom {application_name}').format(contact_name=contact_name, from_merchant_name=from_merchant_name, application_name=application_name)
    trigger_send_email(
                recipient_address = email, 
                subject=subject, 
                message=message
                )

@merchant_manage_partnership_setup_bp.route('/approve-partnership-request', methods=['POST'])
@login_required
@request_form
def approve_merchant_partnership_request_post(request_form):
    logger.debug('request_form=%s', request_form)
    partnership_form =  MerchantPartnerForm(request_form)
    
    try:
        if partnership_form.validate():
            db_client = create_db_client(caller_info="approve_merchant_partnership_request_post")
            is_approved                 = False
            is_valid_partner_merchant   = True
            is_valid_partnership        = True
            logged_in_merchant_user     = get_loggedin_merchant_user_account()
            with db_client.context():
                partnership_key                 = partnership_form.partnership_key.data
                logger.debug('partnership_key=%s', partnership_key)
                
                if is_not_empty(partnership_key):
                    partnership     = PartnerLinked.fetch(partnership_key)
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    
                    if partnership:
                        PartnerLinked.approve_request(partnership, approved_by=merchant_user)
                        is_approved = True
                    else:
                        is_valid_partner_merchant = False
                else:
                    is_valid_partner_merchant = False
            
            logger.debug('is_approved=%s', is_approved)
            logger.debug('is_valid_partner_merchant=%s', is_valid_partner_merchant)
            logger.debug('is_valid_partner_merchant=%s', is_valid_partner_merchant)
            
            if is_valid_partnership:
                if is_valid_partner_merchant:
                    if is_approved:
                        return create_rest_message(status_code=StatusCode.OK, )
                    else:
                        return create_rest_message(gettext('Failed to approve partnership request'), status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message(gettext('Invalid partner merchant account'), status_code=StatusCode.BAD_REQUEST)
            else:
                return create_rest_message(gettext('Invalid merchant partnership'), status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_rest_message(gettext('Failed to approve merchant partnership'), status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Failed to configure merchant partnership due to %s', get_tracelog())
        
        return create_rest_message(gettext('Failed to configure merchant partnership'), status_code=StatusCode.BAD_REQUEST)

@merchant_manage_partnership_setup_bp.route('/from-merchant/disable/<partnership_key>', methods=['POST'])
@login_required
def disable_merchant_partnership_from_merchant_post(partnership_key): 
    
    logger.debug('---disable_merchant_partnership_from_merchant_post---')
    
    logger.debug('partnership_key=%s', partnership_key)
    
    db_client               = create_db_client(caller_info="disable_merchant_partnership_from_merchant_post")
    try:
        with db_client.context():
            if is_empty(partnership_key):
                return create_rest_message(gettext('Invaid merchant partnership data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                partnership = PartnerLinked.fetch(partnership_key)
                if partnership:
                    logger.info('going to disable merchant partnership')
                    PartnerLinked.disable(partnership)
                    
        if partnership is None:
            return create_rest_message(gettext('Invalid merchant partnership'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to disable merchant partnership due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to disable merchant partnership'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,) 

@merchant_manage_partnership_setup_bp.route('/from-merchant/enable/<partnership_key>', methods=['POST','GET'])
@login_required
def enable_merchant_partnership_from_merchant_post(partnership_key): 
    
    logger.debug('---enable_merchant_partnership_from_merchant_post---')
    
    logger.debug('partnership_key=%s', partnership_key)
    
    db_client               = create_db_client(caller_info="enable_merchant_partnership_from_merchant_post")
    try:
        with db_client.context():
            if is_empty(partnership_key):
                return create_rest_message(gettext('Invaid merchant partnership data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                partnership = PartnerLinked.fetch(partnership_key)
                if partnership:
                    logger.info('going to enable merchant partnership')
                    PartnerLinked.enable(partnership)
                    
        if partnership is None:
            return create_rest_message(gettext('Invalid merchant partnership'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to enable merchant partnership due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to enable merchant partnership'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)  
    
