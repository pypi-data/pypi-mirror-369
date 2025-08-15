'''
Created on 18 Sep 2023

@author: jacklok
'''

from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.controllers.system.system_route_helpers import get_redemption_catalogue_status_json, map_label_by_code
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty, random_string
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account, get_preferred_language,\
    get_merchant_account_plan
import trexmodel.program_conf as program_conf
from trexadmin.libs.flask.decorator.common_decorators import limit_content_length
from trexlib.utils.google.gcloud_util import connect_to_bucket

import jinja2
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
from trexmodel.models.datastore.redemption_catalogue_models import RedemptionCatalogue
from trexadmin.forms.merchant.redemption_catalogue_forms import DefineRedemptionCatalogueForm,\
    RedemptionCatalogueExclusivityForm,\
    RedemptionCatalogueItemDetailsForm,\
    RedemptionCatalogueForm
from trexadmin.libs.jinja.program_filters import redeem_reward_format_label as redeem_reward_format_label_filer
    
from trexadmin.controllers.merchant.reward_program.reward_program_setup_routes import get_configured_tags_list
from trexconf import conf
from trexlib.libs.flask_wtf.request_wrapper import request_form, request_values, request_files

redemption_catalogue_bp = Blueprint('redemption_catalogue_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/redeem-program/redemption-catalogue/')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')
'''
def map_label_by_code(code_label_json, code):
    for rb in code_label_json:
        if rb.get('code')==code:
            return rb.get('label')
'''
@jinja2.contextfilter
@redemption_catalogue_bp.app_template_filter()
def redemption_catalogue_completed_status_label(context, redemption_catalogue_completed_status_code):
    if redemption_catalogue_completed_status_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_redemption_catalogue_status_json(preferred_language)
        return map_label_by_code(code_label_json, redemption_catalogue_completed_status_code)
    else:
        return ''

@jinja2.contextfilter
@redemption_catalogue_bp.app_template_filter()
def redeem_reward_format_label(context, code):
    return redeem_reward_format_label_filer(code)


'''
Blueprint settings here
'''
@redemption_catalogue_bp.context_processor
def redemption_catalogue_bp_inject_settings():
    
    return dict(
        
                REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE  = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE,
                REDEMPTION_CATALOGUE_STATUS_DEFINE_ITEM        = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINE_ITEM,
                REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL    = program_conf.REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL,
                REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY,
                REDEMPTION_CATALOGUE_STATUS_REVIEW             = program_conf.REDEMPTION_CATALOGUE_STATUS_REVIEW,
                REDEMPTION_CATALOGUE_STATUS_PUBLISH            = program_conf.REDEMPTION_CATALOGUE_STATUS_PUBLISH,
                
                LOYALTY_PACKAGE_LITE                           = program_conf.LOYALTY_PACKAGE_LITE,
                LOYALTY_PACKAGE_SCALE                          = program_conf.LOYALTY_PACKAGE_SCALE, 
                
                )
    

@redemption_catalogue_bp.route('/manage-redemption-catalogue', methods=['GET'])
@login_required
def manage_redemption_catalogue(): 
    logger.debug('---manage_redemption_catalogue---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="manage_redemption_catalogue")
    redemption_catalogues_list = []
    
    with db_client.context():
        merchant_acct               = MerchantUser.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result  = RedemptionCatalogue.list_by_merchant_account(merchant_acct)
        for r in result:
            redemption_catalogues_list.append(r.to_dict()) 
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/manage_redemption_catalogue.html',
                           page_title                                       = gettext('Redemption Catalogue Setup'),
                           archived_redemption_catalogue_listing_url        = url_for('redemption_catalogue_bp.archived_redemption_catalogue_listing'),
                           redemption_catalogue_listing_reload_url          = url_for('redemption_catalogue_bp.latest_redemption_catalogue_content'),
                           add_redemption_catalogue_item_post_url           = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_post'),
                           redemption_catalogues_list                       = redemption_catalogues_list,
                           )  

@redemption_catalogue_bp.route('/create-redemption-catalogue', methods=['GET'])
@login_required
def create_redemption_catalogue(): 
    logger.debug('---create_redemption_catalogue---')
    
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    db_client       = create_db_client( caller_info="define_redemption_catalogue_post")
    
    with db_client.context():
        merchant_acct       = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/create_redemption_catalogue.html',
                           is_edit_redemption_catalogue                             = True,
                           is_partnership_enabled                                   = __is_loyalty_package_scale_enabled(),
                           define_redemption_catalogue_url                          = url_for('redemption_catalogue_bp.define_redemption_catalogue_post'),
                           
                           show_redemption_catalogue_review_url                     = url_for('redemption_catalogue_bp.show_redemption_catalogue_review'),
                           
                           upload_redemption_catalogue_image_post_url               = url_for('redemption_catalogue_bp.upload_redemption_catalogue_image_post'),
                           update_redemption_catalogue_image_uploaded_url           = url_for('redemption_catalogue_bp.define_complete_redemption_catalogue_image_post'),
                           
                           redemption_catalogue_default_image_url                   = conf.REDEMPTION_CATALOGUE_DEFAULT_IMAGE,
                           add_redemption_catalogue_item_listing_url                = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_listing'),
                           add_redemption_catalogue_item_post_url                   = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_post'),
                           add_redemption_catalogue_item_complete_url               = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_completed_post'),
                           update_redemption_catalogue_exclusivity_post_url         = url_for('redemption_catalogue_bp.update_redemption_catalogue_exclusivity_post'),
                           publish_redemption_catalogue_url                         = url_for('redemption_catalogue_bp.publish_redemption_catalogue_post'),
                           
                           REDEMPTION_CATALOGUE_STATUS_DEFINE_CATALOGUE_COMPLETED   = False,
                           REDEMPTION_CATALOGUE_DEFINE_ITEM_COMPLETED               = False,
                           REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL_COMPLETED    = False,
                           REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY_COMPLETED = False,
                           REDEMPTION_CATALOGUE_STATUS_REVIEW_COMPLETED             = False,
                           
                           loyalty_package                                          = merchant_acct.loyalty_package,
                           
                           configured_tag_list              = get_configured_tags_list(),
                           )  

@redemption_catalogue_bp.route('/define-redemption-catalogue', methods=['POST'])
@login_required
@request_form
def define_redemption_catalogue_post(request_form): 
    logger.debug('---define_redemption_catalogue_post---')
    
    db_client       = create_db_client( caller_info="define_redemption_catalogue_post")
    
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    define_redemption_catalogue_form          = DefineRedemptionCatalogueForm(request_form)
    
    
    
    try:
        with db_client.context():
            merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            merchant_acct       = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
            
            redemption_catalogue_key = define_redemption_catalogue_form.redemption_catalogue_key.data
            
            if is_not_empty(redemption_catalogue_key):
                redemption_catalogue = RedemptionCatalogue.fetch(redemption_catalogue_key)
                
                RedemptionCatalogue.update(redemption_catalogue, 
                                             label                  = define_redemption_catalogue_form.label.data,
                                             desc                   = define_redemption_catalogue_form.desc.data, 
                                             start_date             = define_redemption_catalogue_form.start_date.data,
                                             end_date               = define_redemption_catalogue_form.end_date.data,
                                             redeem_reward_format   = define_redemption_catalogue_form.redeem_reward_format.data, 
                                             modified_by            = merchant_user,
                                             loyalty_package        = merchant_acct.loyalty_package,
                                        )
            else:
                redemption_catalogue = RedemptionCatalogue.create(merchant_acct, 
                                                             label                  = define_redemption_catalogue_form.label.data,
                                                             desc                   = define_redemption_catalogue_form.desc.data, 
                                                             start_date             = define_redemption_catalogue_form.start_date.data,
                                                             end_date               = define_redemption_catalogue_form.end_date.data,
                                                             redeem_reward_format   = define_redemption_catalogue_form.redeem_reward_format.data, 
                                                             created_by             = merchant_user,
                                                             loyalty_package        = merchant_acct.loyalty_package,
                                                               )
            
        redemption_catalogue_key = redemption_catalogue.key_in_str
        return create_rest_message(
                                status_code=StatusCode.OK, 
                                redemption_catalogue_key            = redemption_catalogue_key,
                                add_redemption_catalogue_item_url   = url_for('redemption_catalogue_bp.add_redemption_catalogue_item',redemption_catalogue_key=redemption_catalogue_key,),
                                
                                )
    except:
        logger.error('Failed to define redemption catalogue due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to define redemption catalogue'), status_code=StatusCode.BAD_REQUEST)
    

@redemption_catalogue_bp.route('/<redemption_catalogue_key>/add-redemption-catalogue-item', methods=['GET'])
@login_required
def add_redemption_catalogue_item(redemption_catalogue_key): 
    logger.debug('---add_redemption_catalogue_item---')
    
    db_client       = create_db_client( caller_info="add_redemption_catalogue_item")
    
    with db_client.context():
        redemption_catalogue  = RedemptionCatalogue.fetch(redemption_catalogue_key)
        if redemption_catalogue:
            redemption_catalogue = redemption_catalogue.to_dict()
            
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/setup/add_redemption_catalogue_item_content.html',
                           is_edit_redemption_catalogue                 = True,
                           
                           add_redemption_catalogue_item_url            = url_for('redemption_catalogue_bp.add_redemption_catalogue_item',redemption_catalogue_key=redemption_catalogue_key,),
                           add_redemption_catalogue_item_post_url       = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_post'),
                           #add_redemption_catalogue_item_listing_url    = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_listing',redemption_catalogue_key=redemption_catalogue_key),
                           add_redemption_catalogue_item_listing_url    = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_listing'),
                           
                           )
    
@redemption_catalogue_bp.route('/redemption-catalogue-item-listing', methods=['GET'])
@login_required
@request_values
def add_redemption_catalogue_item_listing(request_values): 
    logger.debug('---reload_redemption_catalogue_item_listing---')
    redemption_catalogue_key = request_values.get('redemption_catalogue_key')
     
    db_client       = create_db_client( caller_info="add_redemption_catalogue_item_listing")
    
    with db_client.context():
        redemption_catalogue  = RedemptionCatalogue.fetch(redemption_catalogue_key)
        if redemption_catalogue:
            redemption_catalogue_items_list = redemption_catalogue.catalogue_settings.get('items')
            redemption_catalogue = redemption_catalogue.to_dict()
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/setup/add_redemption_catalogue_item_listing_content.html',
                           redemption_catalogue             = redemption_catalogue,
                           redemption_catalogue_items_list  = redemption_catalogue_items_list,
                           is_edit_redemption_catalogue     = True,
                           )      
    
@redemption_catalogue_bp.route('/add-redemption-catalogue-item', methods=['POST'])
@login_required
@request_form
def add_redemption_catalogue_item_post(request_form): 
    logger.debug('---add_redemption_catalogue_item_post---')
    
    db_client       = create_db_client( caller_info="add_redemption_catalogue_item_post")
    
    redemption_catalogue_item_form          = RedemptionCatalogueItemDetailsForm(request_form)
    
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    if redemption_catalogue_item_form.validate():
        
        effective_date = redemption_catalogue_item_form.effective_date.data
        if is_not_empty(effective_date):
            effective_date = effective_date.strftime('%d-%m-%Y')
            
        redemption_catalogue_item_settings = {
                                'voucher_index'         : random_string(10),
                                'voucher_key'           : redemption_catalogue_item_form.voucher_key.data,
                                'voucher_amount'        : redemption_catalogue_item_form.voucher_amount.data,
                                'redeem_reward_amount'  : redemption_catalogue_item_form.redeem_reward_amount.data,
                                
                                'use_online'            : redemption_catalogue_item_form.use_online.data,
                                'use_in_store'          : redemption_catalogue_item_form.use_in_store.data,
                                
                                'effective_type'        : redemption_catalogue_item_form.effective_type.data,
                                'effective_date'        : effective_date,
                                'effective_value'       : redemption_catalogue_item_form.effective_value.data,
                                
                                'expiration_type'       : redemption_catalogue_item_form.expiration_type.data,
                                'expiration_date'       : redemption_catalogue_item_form.expiration_date.data,
                                'expiration_value'      : redemption_catalogue_item_form.expiration_value.data,    
                            }    
      
        try:
            with db_client.context():
                merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                redemption_catalogue    = RedemptionCatalogue.fetch(redemption_catalogue_item_form.redemption_catalogue_key.data)
                
                logger.debug('redemption_catalogue_item_settings=%s', redemption_catalogue_item_settings)
                
                redemption_catalogue.add_redemption_catalogue_item(redemption_catalogue_item_settings, modified_by=merchant_user)
                
                
            return create_rest_message(status_code=StatusCode.OK)
        except:
            logger.error('Failed to add redemption catalogue item due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to add redemption catalogue item'), status_code=StatusCode.BAD_REQUEST)
    
    else:
        error_message = redemption_catalogue_item_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)       
    
@redemption_catalogue_bp.route('/<redemption_catalogue_key>/remove-redemption-catalogue-item/<voucher_index>', methods=['DELETE'])
@login_required
def remove_redemption_catalogue_item_delete(redemption_catalogue_key, voucher_index): 
    logger.debug('---remove_redemption_catalogue_item_delete---')
    
    db_client       = create_db_client( caller_info="remove_redemption_catalogue_item_delete")
    
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    logger.debug('redemption_catalogue_key=%s', redemption_catalogue_key)
    logger.debug('voucher_index=%s', voucher_index)
    
    if is_not_empty(redemption_catalogue_key) and is_not_empty(voucher_index):
        
        try:
            with db_client.context():
                merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                redemption_catalogue    = RedemptionCatalogue.fetch(redemption_catalogue_key)
                
                redemption_catalogue.remove_redemption_catalogue_item(voucher_index, modified_by=merchant_user)
                
                
            return create_rest_message(status_code=StatusCode.OK)
        except:
            logger.error('Failed to remove redemption catalogue item due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to remove redemption catalogue item'), status_code=StatusCode.BAD_REQUEST)
    
    else:
        logger.warn('Failed due to missing redemption catalogue key or voucher index')
            
        return create_rest_message(gettext('Missing redemption catalogue item data to proceed'), status_code=StatusCode.BAD_REQUEST)       

@redemption_catalogue_bp.route('/completed-adding-redemption-catalogue-item', methods=['POST'])
@login_required
@request_form
def add_redemption_catalogue_item_completed_post(request_form): 
    logger.debug('---add_redemption_catalogue_item_completed_post---')   
    db_client       = create_db_client( caller_info="add_redemption_catalogue_item_post")
    
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    redemption_catalogue_form          = RedemptionCatalogueForm(request_form)
    
    
    try:
        with db_client.context():
            merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            redemption_catalogue    = RedemptionCatalogue.fetch(redemption_catalogue_form.redemption_catalogue_key.data)
            
            redemption_catalogue.complete_adding_redemption_catalogue_item(modified_by=merchant_user)
            
            
        return create_rest_message(status_code=StatusCode.OK)
    except:
        logger.error('Failed to complete adding redemption catalogue item due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to complete adding redemption catalogue item'), status_code=StatusCode.BAD_REQUEST)
    
@redemption_catalogue_bp.route('/update-redemption-catalogue-exclusivity', methods=['POST'])
@login_required
@request_form
def update_redemption_catalogue_exclusivity_post(request_form): 
    logger.debug('---update_redemption_catalogue_exclusivity_post---')   
    db_client       = create_db_client( caller_info="update_redemption_catalogue_exclusivity_post")
    
    logged_in_merchant_user             = get_loggedin_merchant_user_account()
    
    exclusivity_form                    = RedemptionCatalogueExclusivityForm(request_form)
    
    if exclusivity_form.validate():
    
        try:
            with db_client.context():
                merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                redemption_catalogue    = RedemptionCatalogue.fetch(exclusivity_form.redemption_catalogue_key.data)
                partner_exclusive       = exclusivity_form.partner_exclusive.data
                
                logger.debug('partner_exclusive=%s', partner_exclusive)
                if partner_exclusive:
                    exclusivity_configuration = {
                                                'tags'              : [],
                                                'memberships'       : [],
                                                'tier_memberships'  : [],
                                                'partner_exclusive' : partner_exclusive,
                                                }
                else:
                    tags_list = exclusivity_form.tags_list.data
                    if is_not_empty(tags_list):
                        tags_list = tags_list.split(',')
                        
                        tags_list = [x for x in tags_list if x]
                    
                    membership_key_list = exclusivity_form.membership_key.data
                    if is_not_empty(membership_key_list):
                        membership_key_list = membership_key_list.split(',')
                        
                        membership_key_list = [x for x in membership_key_list if x]
                        
                    tier_membership_key_list = exclusivity_form.tier_membership_key.data
                    if is_not_empty(tier_membership_key_list):
                        tier_membership_key_list = tier_membership_key_list.split(',')       
                        
                        tier_membership_key_list = [x for x in tier_membership_key_list if x]
                    
                    exclusivity_configuration = {
                                                'tags'              : tags_list,
                                                'memberships'       : membership_key_list,
                                                'tier_memberships'  : tier_membership_key_list,
                                                'partner_exclusive' : partner_exclusive,
                                                }
                
                logger.debug('exclusivity_configuration=%s', exclusivity_configuration)
                
                redemption_catalogue.update_redemption_catalogue_exclusivity(exclusivity_configuration, modified_by=merchant_user)
                
                
            return create_rest_message(status_code=StatusCode.OK)
        except:
            logger.error('Failed to update redemption catalogue exclusivity due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to complete adding redemption catalogue item'), status_code=StatusCode.BAD_REQUEST)                     
    else:
        error_message = exclusivity_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
@redemption_catalogue_bp.route('/latest-redemption-catalogue', methods=['GET'])
@login_required
def latest_redemption_catalogue_content(): 
    logger.debug('---latest_redemption_catalogue_content---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    
    db_client = create_db_client(caller_info="latest_redemption_catalogue_content")
    redemption_catalogues_list = []
    
    with db_client.context():
        merchant_acct               = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result  = RedemptionCatalogue.list_by_merchant_account(merchant_acct)
        for r in result:
            redemption_catalogues_list.append(r.to_dict()) 
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/latest_redemption_catalogue_listing_content.html',
                           redemption_catalogues_list = redemption_catalogues_list,
                           archived_redemption_catalogue_listing_url = url_for('redemption_catalogue_bp.archived_redemption_catalogue_listing'),
                           redemption_catalogue_listing_reload_url   = url_for('redemption_catalogue_bp.latest_redemption_catalogue_content'),
                           
                           )  
    

@redemption_catalogue_bp.route('/publish-catalogue', methods=['POST','GET'])
@login_required
@request_values
def publish_redemption_catalogue_post(request_values): 
    redemption_catalogue_key = request_values.get('redemption_catalogue_key')

    logger.debug('redemption_catalogue_key=%s', redemption_catalogue_key)
    
    db_client               = create_db_client(caller_info="publish_redemption_catalogue_post")
    try:
        with db_client.context():
            if is_empty(redemption_catalogue_key):
                return create_rest_message(gettext('Invaid redemption catalogue data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                redemption_catalogue = RedemptionCatalogue.fetch(redemption_catalogue_key)
                if redemption_catalogue:
                    redemption_catalogue.publish_redemption_catalogue()
                    
        if redemption_catalogue is None:
            return create_rest_message(gettext('Invalid redemption catalogue'), status_code=StatusCode.BAD_REQUEST)
        
    except:
        logger.error('Fail to publish redemption catalogue due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to publish redemption catalogue'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)     
    
@redemption_catalogue_bp.route('/archived-redemption-catalogue', methods=['GET'])
@login_required
def archived_redemption_catalogue_listing(): 
    logger.debug('---archived_redemption_catalogue_listing---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="archived_redemption_catalogue_listing")
    redemption_catalogues_list = []
    
    with db_client.context():
        merchant_acct               = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result  = RedemptionCatalogue.list_archived_by_merchant_account(merchant_acct)
        for r in result:
            redemption_catalogues_list.append(r.to_dict())
    
    
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/archived_redemption_catalogue.html',
                           redemption_catalogues_list = redemption_catalogues_list,
                           )   
    
@redemption_catalogue_bp.route('/<redemption_catalogue_key>/edit-redemption-catalogue', methods=['GET'])
@login_required
def edit_redemption_catalogue(redemption_catalogue_key):
    return __edit_redemption_catalogue(redemption_catalogue_key)

@redemption_catalogue_bp.route('/<redemption_catalogue_key>/clone-redemption-catalogue', methods=['GET'])
@login_required
def clone_redemption_catalogue(redemption_catalogue_key):
    return __edit_redemption_catalogue(redemption_catalogue_key, is_clone=True)

def __is_loyalty_package_scale_enabled():
    account_plan = get_merchant_account_plan()
    if is_not_empty(account_plan.get(program_conf.LOYALTY_PACKAGE_SCALE)):
        return True
    else:
        return False


def __edit_redemption_catalogue(redemption_catalogue_key, is_clone = False): 
    logger.debug('---edit_redemption_catalogue---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="edit_redemption_catalogue")
    
    with db_client.context():
        merchant_acct         = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        redemption_catalogue  = RedemptionCatalogue.fetch(redemption_catalogue_key)
        if redemption_catalogue:
            redemption_catalogue_items_list = redemption_catalogue.catalogue_settings.get('items')
            redemption_catalogue = redemption_catalogue.to_dict()
            
            

    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/create_redemption_catalogue.html',
                           is_clone                                                 = is_clone,
                           is_partnership_enabled                                   = __is_loyalty_package_scale_enabled(),
                           redemption_catalogue                                     = redemption_catalogue,
                           redemption_catalogue_items_list                          = redemption_catalogue_items_list,
                           
                           redemption_catalogue_completed_status                    = redemption_catalogue.get('completed_status'),
                           define_redemption_catalogue_url                          = url_for('redemption_catalogue_bp.define_redemption_catalogue_post'),
                           
                           add_redemption_catalogue_item_post_url                   = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_post'),
                           add_redemption_catalogue_item_url                        = url_for('redemption_catalogue_bp.add_redemption_catalogue_item', redemption_catalogue_key=redemption_catalogue_key,),
                           #add_redemption_catalogue_item_listing_url                = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_listing', redemption_catalogue_key=redemption_catalogue_key),
                           add_redemption_catalogue_item_listing_url                = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_listing'),
                           add_redemption_catalogue_item_complete_url               = url_for('redemption_catalogue_bp.add_redemption_catalogue_item_completed_post'),
                           show_redemption_catalogue_review_url                     = url_for('redemption_catalogue_bp.show_redemption_catalogue_review'),
                           
                           upload_redemption_catalogue_image_post_url               = url_for('redemption_catalogue_bp.upload_redemption_catalogue_image_post'),
                           update_redemption_catalogue_image_uploaded_url           = url_for('redemption_catalogue_bp.define_complete_redemption_catalogue_image_post'),
                           
                           redemption_catalogue_default_image_url                   = conf.REDEMPTION_CATALOGUE_DEFAULT_IMAGE,
                           
                           update_redemption_catalogue_exclusivity_post_url         = url_for('redemption_catalogue_bp.update_redemption_catalogue_exclusivity_post'),
                           
                           publish_redemption_catalogue_url                         = url_for('redemption_catalogue_bp.publish_redemption_catalogue_post'),
                           
                           REDEMPTION_CATALOGUE_STATUS_DEFINE_CATALOGUE_COMPLETED   = False,
                           REDEMPTION_CATALOGUE_DEFINE_ITEM_COMPLETED               = False,
                           REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL_COMPLETED    = False,
                           REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY_COMPLETED = False,
                           REDEMPTION_CATALOGUE_STATUS_REVIEW_COMPLETED             = False,
                           
                           loyalty_package                                          = merchant_acct.loyalty_package,
                           
                           configured_tag_list                  = get_configured_tags_list(),
                           
                           is_edit_redemption_catalogue         = True,
                           )
    
@redemption_catalogue_bp.route('/<redemption_catalogue_key>/clone-redemption-catalogue', methods=['POST'])
@login_required
def clone_redemption_catalogue_post(redemption_catalogue_key): 
    logger.debug('---clone_redemption_catalogue---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client = create_db_client(caller_info="clone_redemption_catalogue")
    
    with db_client.context():
        redemption_catalogue  = RedemptionCatalogue.fetch(redemption_catalogue_key)
        if redemption_catalogue:
            merchant_user                   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            cloned_redemption_catalogue     = redemption_catalogue.clone(created_by=merchant_user)
            
            cloned_redemption_catalogue.put()
            
    if cloned_redemption_catalogue:
        return create_rest_message(status_code=StatusCode.OK, edit_new_cloned_url=url_for('redemption_catalogue_bp.clone_redemption_catalogue',redemption_catalogue_key=cloned_redemption_catalogue.key_in_str,))
            
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Failed to clone'))
    
      
    
@redemption_catalogue_bp.route('/<redemption_catalogue_key>/view-redemption-catalogue', methods=['GET'])
@login_required
def view_redemption_catalogue(redemption_catalogue_key): 
    logger.debug('---view_redemption_catalogue---') 
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client = create_db_client(caller_info="view_redemption_catalogue")
    
    with db_client.context():
        merchant_acct         = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        redemption_catalogue  = RedemptionCatalogue.fetch(redemption_catalogue_key)
        if redemption_catalogue:
            redemption_catalogue_items_list = redemption_catalogue.catalogue_settings.get('items')
            redemption_catalogue = redemption_catalogue.to_dict()
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/view_redemption_catalogue.html',
                           is_edit_redemption_catalogue                             = False,
                           is_partnership_enabled                                   = __is_loyalty_package_scale_enabled(),
                           redemption_catalogue                                     = redemption_catalogue,
                           redemption_catalogue_items_list                          = redemption_catalogue_items_list,
                           
                           REDEMPTION_CATALOGUE_STATUS_DEFINE_CATALOGUE_COMPLETED   = False,
                           REDEMPTION_CATALOGUE_DEFINE_ITEM_COMPLETED               = False,
                           REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL_COMPLETED    = False,
                           REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY_COMPLETED = False,
                           REDEMPTION_CATALOGUE_STATUS_REVIEW_COMPLETED             = False,
                           
                           loyalty_package                                          = merchant_acct.loyalty_package,
                           
                           configured_tag_list                  = get_configured_tags_list(),
                           )


@redemption_catalogue_bp.route('/upload-redemption-catalogue-image', methods=['POST'])    
@limit_content_length(1*1024*1024) 
@request_values
@request_files
def upload_redemption_catalogue_image_post(request_values, request_files):    
    redemption_catalogue_key                    = request_values.get('redemption_catalogue_key')
    uploaded_file                               = request_files.get('file')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    logger.debug('redemption_catalogue_key=%s', redemption_catalogue_key)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))
    
    if is_empty(redemption_catalogue_key):
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid redemption catalogue data'))
    
    db_client       = create_db_client( caller_info="upload_redemption_catalogue_image_post")
    
    with db_client.context():
        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        if merchant_acct:
            merchant_acct_key       = merchant_acct.key_in_str
            merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            redemption_catalogue    = RedemptionCatalogue.fetch(redemption_catalogue_key)
            bucket                  = connect_to_bucket(credential_filepath=conf.STORAGE_CREDENTIAL_PATH)    
            image_storage_filename  = 'merchant/'+merchant_acct_key+'/redemption-catalogue/'+uploaded_file.filename
            blob                    = bucket.blob(image_storage_filename)
            
            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )
        
            uploaded_url        = blob.public_url
            
            if is_not_empty(redemption_catalogue.image_public_url):
                old_logo_blob = bucket.get_blob(redemption_catalogue.image_public_url) 
                if old_logo_blob:
                    old_logo_blob.delete()

            redemption_catalogue.update_redemption_catalogue_image( 
                                                    image_public_url        = uploaded_url, 
                                                    image_storage_filename  = image_storage_filename, 
                                                    modified_by             = merchant_user
                                                    )
            
            logger.debug('After uploaded redemption catalogue image url')
            
        else:
            logger.warn('Failed to fetch redemption catalogue data')
         
    if merchant_acct is None or redemption_catalogue is None:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid redemption catalogue data'))    
            
    
    return create_rest_message(status_code=StatusCode.OK, uploaded_url=uploaded_url)  

@redemption_catalogue_bp.route('/define-complete-redemption-catalogue-image', methods=['POST'])    
@request_values
def define_complete_redemption_catalogue_image_post(request_values):
    redemption_catalogue_key = request_values.get('redemption_catalogue_key')
    
    db_client       = create_db_client(caller_info="define_complete_program_ticket_image_post")
    try:
        logged_in_merchant_user = get_loggedin_merchant_user_account()
        with db_client.context():
            merchant_user           = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
            redemption_catalogue    = RedemptionCatalogue.fetch(redemption_catalogue_key)
            
            redemption_catalogue.completed_redemption_catalogue_image_status(modified_by=merchant_user, default_redemption_catalogue_image=conf.REDEMPTION_CATALOGUE_DEFAULT_IMAGE)
            
    except:
        logger.error('Fail to update complete program ticket image status to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update complete program ticket image status'), status_code=StatusCode.BAD_REQUEST)
    
    return create_rest_message(status_code=StatusCode.OK)
    
@redemption_catalogue_bp.route('/show-redemption-catalogue-review', methods=['GET'])
@login_required
@request_values
def show_redemption_catalogue_review(request_values): 
    logger.debug('---show_redemption_catalogue_review---')
    
    redemption_catalogue_key = request_values.get('redemption_catalogue_key')
    
    db_client = create_db_client(caller_info="show_redemption_catalogue_review")
    try:
        
        with db_client.context():
            redemption_catalogue        = RedemptionCatalogue.fetch(redemption_catalogue_key)
            redemption_catalogue_dict   = redemption_catalogue.to_dict()
            
            
    except:
        logger.error('Fail to get redemption catalogue due to %s', get_tracelog())
           
    
    
    
    return render_template('merchant/loyalty/redeem_program/redemption_catalogue/setup/redemption_catalogue_review_content.html', 
                           redemption_catalogue   = redemption_catalogue_dict,
                           )

@redemption_catalogue_bp.route('/<redemption_catalogue_key>/archive-redemption-catalogue', methods=['POST'])
@login_required
def archive_redemption_catalogue_post(redemption_catalogue_key): 
    logger.debug('---archive_redemption_catalogue_post---')
    
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="archive_redemption_catalogue_post")
    
    try:
        with db_client.context():
            if is_empty(redemption_catalogue_key):
                return create_rest_message(gettext('Invaid redemption catalogue data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                redemption_catalogue = RedemptionCatalogue.fetch(redemption_catalogue_key)
                if redemption_catalogue:
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    redemption_catalogue.archive(modified_by=merchant_user)
    except:
        logger.error('Fail to update redemption catalogue due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive redemption catalogue'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

@redemption_catalogue_bp.route('/enable-redemption-catalogue/<redemption_catalogue_key>', methods=['POST','GET'])
@login_required
def enable_redemption_catalogue(redemption_catalogue_key): 
    return enable_or_disable_redemption_catalogue(redemption_catalogue_key, True)

@redemption_catalogue_bp.route('/disable-redemption-catalogue/<redemption_catalogue_key>', methods=['POST','GET'])
@login_required
def disable_redemption_catalogue(redemption_catalogue_key): 
    return enable_or_disable_redemption_catalogue(redemption_catalogue_key, False)
    
def enable_or_disable_redemption_catalogue(redemption_catalogue_key, to_enable): 
    
    logger.debug('redemption_catalogue_key=%s', redemption_catalogue_key)
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    db_client               = create_db_client(caller_info="enable_or_disable_redemption_catalogue")
    
    try:
        with db_client.context():
            if is_empty(redemption_catalogue_key):
                return create_rest_message(gettext('Invaid redemption catalogue data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                redemption_catalogue = RedemptionCatalogue.fetch(redemption_catalogue_key)
                if redemption_catalogue:
                    merchant_user       = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    if to_enable:
                        redemption_catalogue.enable(modified_by=merchant_user)
                        logger.debug('Redemption catalogue have been enabled')
                    else:
                        redemption_catalogue.disable(modified_by=merchant_user)
                        logger.debug('Redemption catalogue have been disabled')
                else:
                    logger.warn('program is not found')
                    
        if redemption_catalogue is None:
            return create_rest_message(gettext('Invalid redemption catalogue'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to update redemption catalogue due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to update redemption catalogue'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)

